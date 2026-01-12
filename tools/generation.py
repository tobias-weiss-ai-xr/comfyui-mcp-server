"""Workflow generation tools (auto-registered from workflow files)"""

import inspect
import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from models.workflow import WorkflowToolDefinition
from tools.helpers import register_and_build_response

logger = logging.getLogger("MCP_Server")


def register_workflow_generation_tools(
    mcp: FastMCP,
    workflow_manager,
    comfyui_client,
    defaults_manager,
    asset_registry
):
    """Register workflow-backed generation tools (e.g., generate_image, generate_song)"""
    
    def _register_workflow_tool(definition: WorkflowToolDefinition):
        def _tool_impl(*args, **kwargs):
            # Extract return_inline_preview if present (not a workflow parameter)
            return_inline_preview = kwargs.pop("return_inline_preview", False)
            
            # Coerce parameter types before signature binding
            # MCP/JSON-RPC may pass numbers as strings, so we need to convert them
            coerced_kwargs = {}
            param_dict = {p.name: p for p in definition.parameters.values()}
            
            for key, value in kwargs.items():
                if key in param_dict:
                    param = param_dict[key]
                    # Coerce to correct type if needed
                    if value is not None:
                        try:
                            # Handle string representations of numbers
                            if param.annotation is int:
                                if isinstance(value, str) and value.strip().isdigit():
                                    coerced_kwargs[key] = int(value)
                                elif isinstance(value, (int, float)):
                                    coerced_kwargs[key] = int(value)
                                else:
                                    coerced_kwargs[key] = value
                            elif param.annotation is float:
                                if isinstance(value, str):
                                    coerced_kwargs[key] = float(value)
                                elif isinstance(value, (int, float)):
                                    coerced_kwargs[key] = float(value)
                                else:
                                    coerced_kwargs[key] = value
                            else:
                                coerced_kwargs[key] = value
                        except (ValueError, TypeError) as e:
                            # If coercion fails, use original value and let validation handle it
                            logger.warning(f"Failed to coerce {key}={value!r} to {param.annotation.__name__}: {e}")
                            coerced_kwargs[key] = value
                    else:
                        coerced_kwargs[key] = None
                else:
                    # Unknown parameter, pass through
                    coerced_kwargs[key] = value
            
            bound = _tool_impl.__signature__.bind(*args, **coerced_kwargs)
            bound.apply_defaults()
            try:
                workflow = workflow_manager.render_workflow(definition, dict(bound.arguments), defaults_manager)
                result = comfyui_client.run_custom_workflow(
                    workflow,
                    preferred_output_keys=definition.output_preferences,
                )
                
                # Register asset and build response
                return register_and_build_response(
                    result,
                    definition.workflow_id,
                    asset_registry,
                    tool_name=definition.tool_name,
                    return_inline_preview=return_inline_preview
                )
                
            except Exception as exc:
                logger.exception("Workflow '%s' failed", definition.workflow_id)
                return {"error": str(exc)}

        # Separate required and optional parameters to ensure correct ordering
        required_params = []
        optional_params = []
        annotations: Dict[str, Any] = {}
        
        for param in definition.parameters.values():
            # For numeric types, use Any to allow string coercion from JSON-RPC
            # FastMCP/Pydantic validation is strict, so we accept Any and validate/coerce ourselves
            if param.annotation in (int, float):
                # Use Any to bypass strict type checking, we'll coerce in the function
                annotation_type = Any
            else:
                annotation_type = param.annotation
            
            if param.required:
                parameter = inspect.Parameter(
                    name=param.name,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=annotation_type,
                )
                required_params.append(parameter)
            else:
                # Optional parameter with default value
                # For numeric types, use Any directly (not Optional[Any]) to allow string coercion
                if param.annotation in (int, float):
                    final_annotation = Any
                else:
                    final_annotation = Optional[annotation_type]
                parameter = inspect.Parameter(
                    name=param.name,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=final_annotation,
                    default=None,
                )
                optional_params.append(parameter)
            annotations[param.name] = param.annotation
        
        # Add return_inline_preview as optional parameter
        optional_params.append(inspect.Parameter(
            name="return_inline_preview",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=bool,
            default=False,
        ))
        annotations["return_inline_preview"] = bool
        
        # Combine: required parameters first, then optional
        parameters = required_params + optional_params
        annotations["return"] = dict
        _tool_impl.__signature__ = inspect.Signature(parameters, return_annotation=dict)
        _tool_impl.__annotations__ = annotations
        _tool_impl.__name__ = f"tool_{definition.tool_name}"
        _tool_impl.__doc__ = definition.description
        mcp.tool(name=definition.tool_name, description=definition.description)(_tool_impl)
        logger.info(
            "Registered MCP tool '%s' for workflow '%s'",
            definition.tool_name,
            definition.workflow_id,
        )
    
    # Register all workflow-backed tools
    if workflow_manager.tool_definitions:
        for tool_definition in workflow_manager.tool_definitions:
            _register_workflow_tool(tool_definition)
    else:
        logger.info(
            "No workflow placeholders found in %s; add %s markers to enable auto tools",
            workflow_manager.workflows_dir,
            "PARAM_",
        )
