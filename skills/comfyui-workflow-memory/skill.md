# ComfyUI Workflow Memory Skill

## Overview

This superpower skill preserves and recalls knowledge about ComfyUI workflows, enabling persistent memory of:
- Generation parameters and settings
- Workflow configurations
- Prompt templates and styles
- Asset history and metadata
- Custom node configurations

## Features

### 1. **Workflow State Capture**
Captures the complete state of a generation request including:
- Model/sampler settings
- Prompt engineering patterns
- Resolution and aspect ratios
- Style parameters

### 2. **Prompt Library**
Stores and retrieves effective prompts:
- Categorized by style (architecture, portrait, landscape, abstract)
- Tagged with effectiveness ratings
- Searchable by keywords

### 3. **Generation History**
Maintains a searchable history of all generations:
- Timestamps and parameters
- Success/failure tracking
- Performance metrics

### 4. **Workflow Templates**
Pre-configured workflow setups for common use cases:
- **dub_techno_architecture**: Dark industrial minimal with bass visualization
- **cinematic_wide**: 1920x1080 cinematic compositions
- **portrait_square**: 1024x1024 portrait styles
- **abstract_art**: Experimental generative art

## Stored Knowledge Schema

```json
{
  "workflow_memory": {
    "current_session": {
      "active_workflow": "zai_small",
      "default_resolution": { "width": 1920, "height": 1080 },
      "last_prompt": "...",
      "generation_count": 0
    },
    "prompt_library": {
      "architecture_dub_techno": [
        {
          "prompt": "brutalist concrete tower...",
          "tags": ["architecture", "dub-techno", "industrial"],
          "rating": 5,
          "last_used": "2024-01-01T00:00:00Z"
        }
      ]
    },
    "generation_history": [
      {
        "id": "uuid",
        "timestamp": "ISO-8601",
        "workflow": "zai_small",
        "prompt": "...",
        "resolution": { "width": 1920, "height": 1080 },
        "asset_id": "uuid",
        "success": true
      }
    ],
    "workflow_configs": {
      "zai_small": {
        "description": "Fast SDXL generation workflow",
        "default_params": {
          "width": 1024,
          "height": 576,
          "return_inline_preview": true
        },
        "optimal_settings": {
          "cinematic": { "width": 1920, "height": 1080 },
          "square": { "width": 1024, "height": 1024 },
          "portrait": { "width": 896, "height": 1152 }
        }
      }
    },
    "learned_patterns": {
      "effective_keywords_combos": [
        ["dub techno", "concrete", "bass visualization"],
        ["architecture", "sculpture", "minimal"]
      ],
      "style_modifiers": {
        "dark_moody": ["cold", "dark", "minimal", "industrial"],
        "cinematic": ["cinematic", "dramatic lighting", "atmospheric"]
      }
    }
  }
}
```

## Usage Examples

### Capture Current Workflow State
```
User: "Remember this configuration"
Skill: Saves current width, height, prompt pattern, and style settings
```

### Recall Effective Prompts
```
User: "What prompts work well for architecture?"
Skill: Returns top-rated architecture prompts with tags and ratings
```

### Apply Workflow Template
```
User: "Use dub techno architecture style"
Skill: Loads pre-configured settings for dark industrial minimal aesthetic
```

### View Generation History
```
User: "Show my recent generations"
Skill: Lists last N generations with parameters and asset IDs
```

## Implementation Notes

- Memory persists across sessions via JSON file storage
- Automatic capture of successful generations
- Prompt effectiveness learned from user feedback
- Workflow configs synced with ComfyUI server capabilities
