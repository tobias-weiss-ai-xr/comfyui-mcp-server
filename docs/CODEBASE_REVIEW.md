# Codebase Review & Refactoring Plan

## Executive Summary

After a major rewrite, the codebase has grown to ~1287 lines in `server.py`. This review identifies cleanup opportunities and proposes a modular refactoring to improve maintainability.

## Issues Found

### 1. Unused Imports
- **`hashlib`** in `server.py:7` - imported but never used
- **Fix**: Remove unused import

### 2. Dead Code
- **`archive/comfyui_workflow_test.py`** - Old test file using deprecated `urllib.request`, superseded by `client.py`
- **`process_image_for_inline()`** in `asset_processor.py:379` - Marked as deprecated, replaced by `encode_preview_for_mcp()`
- **Fix**: Remove archive file, remove or update deprecated function

### 3. Code Duplication
- **Asset registration logic** duplicated in:
  - `run_workflow()` (lines 1040-1051)
  - `_register_workflow_tool()` (lines 1151-1162)
- **Response building logic** also duplicated (lines 1053-1093 vs 1164-1199)
- **Fix**: Extract shared helper function `_register_and_build_response()`

### 4. Monolithic `server.py` (1287 lines)

**Current Structure:**
- Lines 1-60: Constants and configuration
- Lines 71-85: Data classes (AssetRecord)
- Lines 88-177: AssetRegistry class
- Lines 180-355: DefaultsManager class
- Lines 357-365: WorkflowParameter dataclass
- Lines 367-375: WorkflowToolDefinition dataclass
- Lines 377-743: WorkflowManager class
- Lines 744-749: Global initialization
- Lines 752-777: AppContext and lifespan
- Lines 780-996: MCP tool functions
- Lines 1099-1264: Tool registration logic
- Lines 1266-1287: Module-level execution

**Proposed Refactoring:**

```
server.py (main entry point, ~200 lines)
├── models/
│   ├── __init__.py
│   ├── asset.py          # AssetRecord dataclass
│   └── workflow.py       # WorkflowParameter, WorkflowToolDefinition
├── managers/
│   ├── __init__.py
│   ├── asset_registry.py # AssetRegistry class
│   ├── defaults_manager.py # DefaultsManager class
│   └── workflow_manager.py # WorkflowManager class
├── tools/
│   ├── __init__.py
│   ├── generation.py     # generate_image, generate_song tools
│   ├── configuration.py  # list_models, get_defaults, set_defaults
│   ├── workflow.py       # list_workflows, run_workflow
│   └── asset.py          # view_asset tool
└── server.py             # FastMCP setup, tool registration, main entry
```

**Benefits:**
- Clear separation of concerns
- Easier to test individual components
- Better code navigation
- Reduced merge conflicts
- Follows Python package best practices

## Recommended Action Plan

### Phase 1: Quick Wins (Low Risk)
1. ✅ Remove unused `hashlib` import
2. ✅ Remove `archive/comfyui_workflow_test.py`
3. ✅ Remove deprecated `process_image_for_inline()` function
4. ✅ Extract duplicate asset registration logic

### Phase 2: Refactoring (Medium Risk)
1. Create `models/` package for data classes
2. Create `managers/` package for business logic classes
3. Create `tools/` package for MCP tool functions
4. Update imports throughout codebase
5. Test that all functionality still works

### Phase 3: Testing (High Priority)
1. Add unit tests for extracted modules
2. Add integration tests for tool functions
3. Verify backward compatibility

## Detailed Refactoring Plan

### Step 1: Extract Data Models

**Create `models/asset.py`:**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class AssetRecord:
    """Record of a generated asset for tracking and viewing"""
    asset_id: str
    asset_url: str
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    bytes_size: int
    sha256: Optional[str]
    created_at: datetime
    workflow_id: str
    prompt_id: str
    expires_at: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Create `models/workflow.py`:**
```python
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

@dataclass
class WorkflowParameter:
    name: str
    placeholder: str
    annotation: type
    description: str
    bindings: list[Tuple[str, str]] = field(default_factory=list)
    required: bool = True

@dataclass
class WorkflowToolDefinition:
    workflow_id: str
    tool_name: str
    description: str
    template: Dict[str, Any]
    parameters: "OrderedDict[str, WorkflowParameter]"
    output_preferences: Sequence[str]
```

### Step 2: Extract Managers

**Create `managers/asset_registry.py`:**
- Move `AssetRegistry` class (lines 88-177)
- Import `AssetRecord` from `models.asset`

**Create `managers/defaults_manager.py`:**
- Move `DefaultsManager` class (lines 180-355)
- Keep dependencies on `ComfyUIClient` and config paths

**Create `managers/workflow_manager.py`:**
- Move `WorkflowManager` class (lines 377-743)
- Import data models from `models.workflow`

### Step 3: Extract Tools

**Create `tools/helpers.py`:**
- Shared helper: `_register_and_build_response()` to eliminate duplication

**Create `tools/configuration.py`:**
- `list_models()`
- `get_defaults()`
- `set_defaults()`

**Create `tools/workflow.py`:**
- `list_workflows()`
- `run_workflow()`

**Create `tools/asset.py`:**
- `view_asset()`

**Create `tools/generation.py`:**
- `_register_workflow_tool()` function
- Auto-registered workflow tools (generate_image, generate_song, etc.)

### Step 4: Update server.py

**New `server.py` structure:**
```python
# Imports
from mcp.server.fastmcp import FastMCP
from managers.asset_registry import AssetRegistry
from managers.defaults_manager import DefaultsManager
from managers.workflow_manager import WorkflowManager
from tools.configuration import register_configuration_tools
from tools.workflow import register_workflow_tools
from tools.asset import register_asset_tools
from tools.generation import register_workflow_generation_tools

# Configuration
# Global initialization
# AppContext and lifespan
# FastMCP setup
# Tool registration
# Main entry point
```

## Migration Strategy

1. **Create new structure** alongside existing code
2. **Move code incrementally** (one module at a time)
3. **Update imports** as modules are moved
4. **Test after each move** to ensure nothing breaks
5. **Remove old code** once new structure is verified

## Risk Assessment

- **Low Risk**: Removing unused imports and dead code
- **Medium Risk**: Extracting duplicate logic (requires careful testing)
- **Medium-High Risk**: Full refactoring (requires comprehensive testing)

## Testing Checklist

After refactoring, verify:
- [ ] All MCP tools still work
- [ ] Workflow generation still works
- [ ] Asset viewing still works
- [ ] Defaults management still works
- [ ] Configuration persistence still works
- [ ] Client.py test client still works
- [ ] No import errors
- [ ] No circular dependencies
