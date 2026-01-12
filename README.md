# ComfyUI MCP Server

A lightweight Python-based MCP (Model Context Protocol) server that interfaces with a local [ComfyUI](https://github.com/comfyanonymous/ComfyUI) instance to generate images, audio, and video programmatically via AI agent requests.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start ComfyUI** (if not already running):
   ```bash
   cd <ComfyUI_dir>
   python main.py --port 8188
   ```

3. **Run the MCP server:**
   ```bash
   python server.py
   ```
   Server starts at `http://127.0.0.1:9000/mcp`

4. **Test it:**
   ```bash
   python test_client.py
   ```

## Features

- **Image Generation**: Generate images using Stable Diffusion workflows
- **Audio Generation**: Generate songs using AceStep workflows  
- **Inline Image Viewing**: View generated images directly in chat with `view_image`
- **Flexible Workflows**: Add custom workflows by placing JSON files in `workflows/`
- **Smart Defaults**: Automatic parameter defaults with configurable precedence
- **Asset Management**: Automatic asset tracking with expiration

## Basic Usage

### Generate an Image

```python
# Simple call with defaults
result = generate_image(prompt="a beautiful sunset")

# Custom parameters
result = generate_image(
    prompt="a cyberpunk cityscape at night",
    width=1024,
    height=768,
    model="sd_xl_base_1.0.safetensors",
    steps=30
)

# Access the result
asset_id = result["asset_id"]        # For viewing with view_image
asset_url = result["asset_url"]      # Direct URL to the image
```

### View an Image Inline

```python
# Generate an image
result = generate_image(prompt="a cat")

# View it inline in chat
view_image(asset_id=result["asset_id"], mode="thumb")
```

### Generate Audio

```python
result = generate_song(
    tags="electronic, ambient",
    lyrics="In the quiet of the night, stars shine bright...",
    seconds=30
)
```

## Available Tools

### Generation Tools

- **`generate_image`**: Generate images (requires `prompt`)
- **`generate_song`**: Generate audio (requires `tags` and `lyrics`)

### Viewing Tools

- **`view_image`**: View generated images inline (images only, not audio/video)

### Configuration Tools

- **`list_models`**: List available ComfyUI models
- **`get_defaults`**: Get current default values
- **`set_defaults`**: Set default values (with optional persistence)

### Workflow Tools

- **`list_workflows`**: List all available workflows
- **`run_workflow`**: Run any workflow with custom parameters

## Parameters

### generate_image

**Required:**
- `prompt` (string): Text description of the image

**Optional (with defaults):**
- `width`, `height` (int): Image dimensions (default: 512)
- `model` (string): Checkpoint model name (default: "v1-5-pruned-emaonly.ckpt")
- `steps` (int): Sampling steps (default: 20)
- `cfg` (float): Guidance scale (default: 8.0)
- `sampler_name` (string): Sampling method (default: "euler")
- `scheduler` (string): Scheduler type (default: "normal")
- `denoise` (float): Denoising strength 0.0-1.0 (default: 1.0)
- `negative_prompt` (string): Negative prompt (default: "text, watermark")
- `seed` (int): Random seed (auto-generated if not provided)

### generate_song

**Required:**
- `tags` (string): Comma-separated style tags
- `lyrics` (string): Full lyric text

**Optional (with defaults):**
- `seconds` (int): Duration in seconds (default: 60)
- `steps` (int): Sampling steps (default: 50)
- `cfg` (float): Guidance scale (default: 5.0)
- `lyrics_strength` (float): Lyrics influence 0.0-1.0 (default: 0.99)
- `seed` (int): Random seed (auto-generated if not provided)

## Configuration

### Default Values

Defaults are resolved in this order (highest to lowest priority):

1. **Per-call values** - Explicitly provided in tool calls
2. **Runtime defaults** - Set via `set_defaults` (ephemeral)
3. **Config file** - `~/.config/comfy-mcp/config.json` (persistent)
4. **Environment variables** - `COMFY_MCP_DEFAULT_IMAGE_MODEL`, etc.
5. **Hardcoded defaults** - Built-in sensible values

### Environment Variables

- `COMFYUI_URL`: ComfyUI server URL (default: `http://localhost:8188`)
- `COMFY_MCP_DEFAULT_IMAGE_MODEL`: Default image model
- `COMFY_MCP_DEFAULT_AUDIO_MODEL`: Default audio model
- `COMFY_MCP_WORKFLOW_DIR`: Workflow directory (default: `./workflows`)
- `COMFY_MCP_ASSET_TTL_HOURS`: Asset expiration time (default: 24)

### Config File Example

Create `~/.config/comfy-mcp/config.json`:

```json
{
  "defaults": {
    "image": {
      "model": "sd_xl_base_1.0.safetensors",
      "width": 1024,
      "height": 1024,
      "steps": 30
    },
    "audio": {
      "seconds": 30,
      "steps": 60
    }
  }
}
```

## Custom Workflows

Add custom workflows by placing JSON files in the `workflows/` directory. Workflows are automatically discovered and exposed as MCP tools.

### Workflow Placeholders

Use `PARAM_*` placeholders in workflow JSON to expose parameters:

- `PARAM_PROMPT` → `prompt: str` (required)
- `PARAM_INT_STEPS` → `steps: int` (optional)
- `PARAM_FLOAT_CFG` → `cfg: float` (optional)

**Example:**
```json
{
  "3": {
    "inputs": {
      "text": "PARAM_PROMPT",
      "steps": "PARAM_INT_STEPS"
    }
  }
}
```

The tool name is derived from the filename (e.g., `my_workflow.json` → `my_workflow` tool).

### Advanced: Workflow Metadata

For advanced control, create a `.meta.json` file alongside your workflow:

```json
{
  "name": "My Custom Workflow",
  "description": "Does something cool",
  "defaults": {
    "steps": 30
  },
  "constraints": {
    "width": {"min": 64, "max": 2048, "step": 64}
  }
}
```

## Project Structure

```
comfyui-mcp-server/
├── server.py              # Main entry point
├── comfyui_client.py      # ComfyUI API client
├── asset_processor.py     # Image processing utilities
├── test_client.py         # Test client
├── managers/              # Core managers
│   ├── workflow_manager.py
│   ├── defaults_manager.py
│   └── asset_registry.py
├── tools/                 # MCP tool implementations
│   ├── generation.py
│   ├── asset.py
│   ├── configuration.py
│   └── workflow.py
├── models/                # Data models
│   ├── workflow.py
│   └── asset.py
└── workflows/             # Workflow JSON files
    ├── generate_image.json
    └── generate_song.json
```

## Notes

- Ensure your models exist in `<ComfyUI_dir>/models/checkpoints/`
- Server uses **streamable-http** transport (HTTP-based, not WebSocket)
- Workflows are auto-discovered - no code changes needed
- Assets expire after 24 hours (configurable)
- `view_image` only supports images (PNG, JPEG, WebP, GIF)

## Documentation

- [API Reference](docs/REFERENCE.md) - Complete tool reference and parameters
- [Architecture](docs/ARCHITECTURE.md) - Design decisions and system overview

## Contributing

Issues and pull requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Acknowledgements

- [@venetanji](https://github.com/venetanji) - streamable-http rewrite foundation & PARAM_* system

## Maintainer
[@joenorton](https://github.com/joenorton)

## License

Apache License 2.0
