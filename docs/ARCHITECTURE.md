# Architecture

High-level architecture and design decisions for ComfyUI MCP Server.

## Overview

The server bridges MCP (Model Context Protocol) and ComfyUI, providing a standardized interface for AI agents to generate media through ComfyUI workflows.

## Core Components

### WorkflowManager

**Purpose**: Discovers, loads, and processes ComfyUI workflow JSON files.

**Responsibilities:**
- Scan `workflows/` directory for JSON files
- Extract parameters from `PARAM_*` placeholders
- Build `WorkflowToolDefinition` objects
- Render workflows with provided parameters
- Apply constrained overrides (for `run_workflow`)

**Key Methods:**
- `_load_workflows()`: Discovery and loading
- `_extract_parameters()`: Placeholder parsing
- `render_workflow()`: Parameter substitution
- `apply_workflow_overrides()`: Constrained parameter updates

### DefaultsManager

**Purpose**: Manages default values with configurable precedence.

**Precedence Order:**
1. Per-call values (explicit parameters)
2. Runtime defaults (`set_defaults` tool)
3. Config file (`~/.config/comfy-mcp/config.json`)
4. Environment variables
5. Hardcoded defaults

**Key Methods:**
- `get_default()`: Resolve value with precedence
- `set_defaults()`: Set runtime defaults
- `persist_defaults()`: Write to config file

### AssetRegistry

**Purpose**: Track generated assets for viewing and management.

**Features:**
- UUID-based asset IDs
- TTL-based expiration (default 24 hours)
- URL-based deduplication (optional)
- Automatic cleanup of expired assets

**Key Methods:**
- `register_asset()`: Register new asset, return `AssetRecord`
- `get_asset()`: Retrieve by ID (checks expiration)
- `cleanup_expired()`: Remove expired assets

### ComfyUIClient

**Purpose**: Interface with ComfyUI API.

**Responsibilities:**
- Queue workflows via `/prompt` endpoint
- Poll for completion via `/history/{prompt_id}`
- Extract asset URLs from outputs
- Fetch asset metadata (size, dimensions, mime type)

**Key Methods:**
- `run_custom_workflow()`: Execute workflow and wait for completion
- `_queue_workflow()`: Submit workflow to ComfyUI
- `_wait_for_prompt()`: Poll until completion
- `_extract_first_asset_url()`: Find asset in outputs

## Workflow System

### Discovery

1. `WorkflowManager` scans `workflows/` directory
2. Loads JSON files (skips `.meta.json` files)
3. Extracts `PARAM_*` placeholders
4. Builds parameter definitions with types and bindings
5. Creates `WorkflowToolDefinition` objects

### Parameter Extraction

**Placeholder Format**: `PARAM_<TYPE?>_<NAME>`

**Examples:**
- `PARAM_PROMPT` → `prompt: str` (required)
- `PARAM_INT_STEPS` → `steps: int` (optional)
- `PARAM_FLOAT_CFG` → `cfg: float` (optional)

**Binding**: Maps to `[node_id, input_name]` in workflow JSON

### Tool Registration

1. `register_workflow_generation_tools()` iterates over definitions
2. Creates dynamic tool functions with proper signatures
3. Handles type coercion (JSON-RPC strings → Python types)
4. Registers with FastMCP via `@mcp.tool()` decorator

### Execution Flow

1. Tool called with parameters
2. `render_workflow()` substitutes placeholders with values
3. Defaults applied for missing optional parameters
4. Workflow queued to ComfyUI
5. Server polls for completion
6. Asset URL extracted from outputs
7. Asset registered in `AssetRegistry`
8. Response returned with `asset_id` and `asset_url`

## Asset Lifecycle

### Generation

1. Workflow executes in ComfyUI
2. Asset saved to ComfyUI output directory
3. ComfyUI returns output metadata

### Registration

1. `AssetRegistry.register_asset()` called
2. UUID generated for `asset_id`
3. Expiration time calculated (now + TTL)
4. `AssetRecord` created and stored
5. URL-to-ID mapping created (for deduplication)

### Viewing

1. `view_image` called with `asset_id`
2. `AssetRegistry.get_asset()` retrieves record
3. Expiration checked (returns None if expired)
4. Asset bytes fetched from ComfyUI `/view` endpoint
5. Image processed (downscale, re-encode as WebP)
6. Base64-encoded thumbnail returned

### Expiration

1. Assets expire after TTL (default 24 hours)
2. `cleanup_expired()` removes expired records
3. Called periodically during `view_image` operations

## Image Processing Pipeline

### Purpose

Convert large images to small, context-friendly thumbnails for inline display in chat.

### Constraints

- **Size limit**: 100KB base64 payload (configurable)
- **Dimension limit**: 512px max dimension (configurable)
- **Format**: WebP (efficient compression)

### Process

1. **Fetch**: Download image bytes from ComfyUI
2. **Load**: Open with Pillow, apply EXIF orientation
3. **Downscale**: Resize to fit within `max_dim` (maintain aspect ratio)
4. **Optimize**: Quality ladder (70 → 55 → 40) to fit budget
5. **Encode**: Save as WebP, base64 encode
6. **Validate**: Check total payload size (base64 + data URI prefix)
7. **Cache**: Store result (LRU cache, max 100 entries)

### Why WebP?

- Better compression than PNG/JPEG
- Supports transparency
- Widely supported in modern clients
- Good quality/size tradeoff

### Why Thumbnails Only?

- Context window limits in AI chat interfaces
- Base64 encoding adds ~33% overhead
- Large images cause context bloat and crashes
- Thumbnails provide visual feedback without cost

## Default Value System

### Why Multiple Sources?

Different use cases need different defaults:
- **Hardcoded**: Sensible defaults for new users
- **Config file**: Persistent preferences
- **Runtime**: Session-specific overrides
- **Environment**: Deployment-specific settings

### Resolution Algorithm

```python
def get_default(namespace, key, provided_value):
    if provided_value is not None:
        return provided_value  # Explicit wins
    
    # Check in order of precedence
    if key in runtime_defaults[namespace]:
        return runtime_defaults[namespace][key]
    if key in config_defaults[namespace]:
        return config_defaults[namespace][key]
    if key in env_defaults[namespace]:
        return env_defaults[namespace][key]
    if key in hardcoded_defaults[namespace]:
        return hardcoded_defaults[namespace][key]
    
    return None  # No default found
```

## Security Considerations

### Path Traversal Protection

Workflow IDs are sanitized before file access:

```python
safe_id = workflow_id.replace("/", "_").replace("\\", "_").replace("..", "_")
safe_id = "".join(c for c in safe_id if c.isalnum() or c in ("_", "-"))
```

Resolved paths are validated to be within `workflows/` directory.

### Asset Access Control

- Only assets generated by this server can be viewed
- `asset_id` must exist in registry
- Expired assets are automatically removed
- No direct file system access from tools

### Parameter Validation

- Overrides constrained to declared parameters
- Type coercion with validation
- Constraints enforced (min/max/enum) if metadata provided

## Performance Considerations

### Caching

- **Workflows**: Cached after first load (in-memory)
- **Image previews**: LRU cache (max 100 entries)
- **Model list**: Cached in `ComfyUIClient` (refreshed on init)

### Polling Strategy

- 1-second intervals
- Maximum 30 attempts (30 seconds)
- Exponential backoff considered but not implemented

### Memory Management

- Asset registry: In-memory dict (consider persistence for production)
- Image cache: Limited to 100 entries
- Expired assets cleaned up automatically

## Design Decisions

### Why Streamable-HTTP?

- Better scalability than WebSocket
- Cloud-ready (works behind load balancers)
- Standard HTTP tooling
- Stateless (easier to scale horizontally)

### Why UUID Asset IDs?

- Globally unique
- No collisions
- Opaque (doesn't leak internal structure)
- Standard format

### Why TTL Instead of Manual Deletion?

- Automatic cleanup reduces memory usage
- No manual management needed
- Predictable behavior
- Configurable per deployment

### Why Separate view_image Tool?

- Lazy loading: Only fetch/process when needed
- Size control: Enforce limits at viewing time
- Format conversion: Optimize for display
- Separation of concerns: Generation vs. viewing

## Future Considerations

### Potential Improvements

- **Persistent asset registry**: Database backend for production
- **Rate limiting**: Prevent abuse
- **Health checks**: ComfyUI connectivity monitoring
- **Metrics**: Generation time, success rates
- **Batch operations**: Generate multiple assets
- **Streaming**: Real-time progress updates

### Scalability

Current design is single-instance. For scale:
- Add database backend for asset registry
- Implement distributed locking for workflow execution
- Add queue system for high-volume scenarios
- Consider caching layer for ComfyUI responses
