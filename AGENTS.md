# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-26
**Commit:** [pending git info]
**Branch:** [pending]

## OVERVIEW
ComfyUI MCP Server - Lightweight Model Context Protocol server that bridges AI agents to local ComfyUI for image/audio/video generation and iterative refinement.

## STRUCTURE
```
comfyui-mcp-server/
├── server.py              # Main entry point (if __name__ == "__main__")
├── comfyui_client.py      # ComfyUI API client (HTTP requests to localhost:8188)
├── asset_processor.py     # Image processing (Pillow, base64 encoding)
├── managers/              # Core business logic layer
├── tools/                 # MCP tool implementations
├── models/                # Data models
├── workflows/             # ComfyUI workflow JSON files
├── tests/                 # Pytest test suite
└── docs/                  # Comprehensive documentation
```

## WHERE TO LOOK
| Domain | Location | Reference |
|--------|----------|----------|
| Server entry | server.py line 206 | AGENTS.md |
| MCP tools | tools/ | tools_AGENTS.md |
| Managers | managers/ | managers_AGENTS.md |
| Testing | tests/ | tests_AGENTS.md |
| Documentation | docs/ | See REFERENCE.md, ARCHITECTURE.md |

## CONVENTIONS

### Code Style
- PEP 8 (from CONTRIBUTING.md)
- Type hints required
- Docstrings required
- Small, focused functions

### Default Resolution
Priority: per-call → runtime → config file → env vars → hardcoded

### Asset Identity
Identified by (filename, subfolder, type) tuple (not URL). Session-scoped (lost on restart).

## ANTI-PATTERNS

### Architecture Limitations
- Ephemeral asset registry: asset_id references valid only while server running + 24hr TTL
- Session-scoped design: list_assets() supports session filtering

## COMMANDS
```bash
# Run server (default: streamable-http on port 9000)
python server.py

# Run server (stdio transport)
python server.py --stdio

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html
```

## NOTES

### Entry Point
- Primary: server.py line 206
- Two modes: HTTP transport (default) or stdio transport

### Workflow History
- Stored in AssetRegistry as comfy_history dict
- Used by regenerate() to replay with parameter overrides

### Testing Gaps
- No CI/CD workflows
- No automated linting/formatting in repository
