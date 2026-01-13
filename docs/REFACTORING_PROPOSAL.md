# Server.py Refactoring Proposal

## Current State

- **server.py**: 1287 lines (monolithic)
- **Issues addressed**: ✅ Removed unused imports, dead code, extracted duplicate logic
- **Remaining**: Modular refactoring needed for maintainability

## Proposed Structure

```
comfyui-mcp-server/
├── server.py                    # Main entry point (~200 lines)
├── models/
│   ├── __init__.py
│   ├── asset.py                 # AssetRecord dataclass
│   └── workflow.py              # WorkflowParameter, WorkflowToolDefinition
├── managers/
│   ├── __init__.py
│   ├── asset_registry.py        # AssetRegistry class (~90 lines)
│   ├── defaults_manager.py      # DefaultsManager class (~175 lines)
│   └── workflow_manager.py      # WorkflowManager class (~365 lines)
└── tools/
    ├── __init__.py
    ├── helpers.py               # Shared helper functions (~80 lines)
    ├── configuration.py         # list_models, get_defaults, set_defaults (~85 lines)
    ├── workflow.py              # list_workflows, run_workflow (~100 lines)
    ├── asset.py                 # view_asset tool (~100 lines)
    └── generation.py            # _register_workflow_tool (~170 lines)
```

## Benefits

1. **Separation of Concerns**: Each module has a single responsibility
2. **Testability**: Easier to unit test individual components
3. **Maintainability**: Smaller files are easier to navigate and modify
4. **Reduced Merge Conflicts**: Multiple developers can work on different modules
5. **Clear Dependencies**: Import structure shows module relationships

## Migration Strategy

### Phase 1: Extract Data Models (Low Risk)
1. Create `models/` directory
2. Move `AssetRecord` to `models/asset.py`
3. Move `WorkflowParameter` and `WorkflowToolDefinition` to `models/workflow.py`
4. Update imports in `server.py`

### Phase 2: Extract Managers (Medium Risk)
1. Create `managers/` directory
2. Move `AssetRegistry` to `managers/asset_registry.py`
3. Move `DefaultsManager` to `managers/defaults_manager.py`
4. Move `WorkflowManager` to `managers/workflow_manager.py`
5. Update imports throughout

### Phase 3: Extract Tools (Medium Risk)
1. Create `tools/` directory
2. Move `_register_and_build_response` to `tools/helpers.py`
3. Move configuration tools to `tools/configuration.py`
4. Move workflow tools to `tools/workflow.py`
5. Move asset tools to `tools/asset.py`
6. Move generation tools to `tools/generation.py`

### Phase 4: Refactor server.py (Low Risk)
1. Keep only initialization, FastMCP setup, and tool registration
2. Import all modules from new structure
3. Verify all functionality works

## Implementation Notes

### Circular Dependencies
- **Risk**: Managers might need to import from models
- **Solution**: Models should have no dependencies on managers
- **Order**: Models → Managers → Tools → Server

### Global State
- **Current**: Global instances (comfyui_client, workflow_manager, etc.)
- **Approach**: Keep globals in server.py, pass to tools as needed
- **Alternative**: Use dependency injection (future enhancement)

### Backward Compatibility
- **Goal**: No breaking changes to API
- **Testing**: Run client.py test after each phase
- **Verification**: All MCP tools should work identically

## File Size Targets

After refactoring:
- `server.py`: ~200 lines (down from 1287)
- `models/asset.py`: ~20 lines
- `models/workflow.py`: ~30 lines
- `managers/asset_registry.py`: ~90 lines
- `managers/defaults_manager.py`: ~175 lines
- `managers/workflow_manager.py`: ~365 lines
- `tools/helpers.py`: ~80 lines
- `tools/configuration.py`: ~85 lines
- `tools/workflow.py`: ~100 lines
- `tools/asset.py`: ~100 lines
- `tools/generation.py`: ~170 lines

**Total**: ~1415 lines (slight increase due to imports/boilerplate, but much better organized)

## Testing Plan

After each phase:
1. ✅ Run `python server.py` - should start without errors
2. ✅ Run `python client.py` - should connect and list tools
3. ✅ Test `generate_image` tool
4. ✅ Test `list_workflows` tool
5. ✅ Test `view_asset` tool
6. ✅ Verify all imports work

## Rollback Plan

- Keep original `server.py` in git history
- Each phase is a separate commit
- Can revert individual phases if issues arise
- Full rollback: `git revert` to pre-refactoring state

## Recommendation

**Start with Phase 1** (extract models) - lowest risk, immediate benefit. If successful, proceed with Phase 2, etc.

**Alternative**: If you prefer to keep the monolith for now, the code is already cleaner after removing dead code and extracting duplicate logic. Refactoring can be done incrementally as needed.
