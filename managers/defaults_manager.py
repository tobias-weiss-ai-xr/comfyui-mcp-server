"""Defaults management for workflow parameters"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from comfyui_client import ComfyUIClient

logger = logging.getLogger("MCP_Server")

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "comfy-mcp"
CONFIG_FILE = CONFIG_DIR / "config.json"


class DefaultsManager:
    """Manages default values with precedence: per-call > runtime > config > env > hardcoded"""
    
    def __init__(self, comfyui_client: ComfyUIClient):
        self.comfyui_client = comfyui_client
        self._runtime_defaults: Dict[str, Dict[str, Any]] = {
            "image": {},
            "audio": {},
            "video": {}
        }
        self._config_defaults = self._load_config_defaults()
        self._hardcoded_defaults = {
            "image": {
                "width": 512,
                "height": 512,
                "steps": 20,
                "cfg": 8.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": "v1-5-pruned-emaonly.ckpt",
                "negative_prompt": "text, watermark",
            },
            "audio": {
                "steps": 50,
                "cfg": 5.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "seconds": 60,
                "lyrics_strength": 0.99,
                "model": "ace_step_v1_3.5b.safetensors",
            },
            "video": {
                "width": 1280,
                "height": 720,
                "steps": 20,
                "cfg": 8.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": "wan2.2_vae.safetensors",
                "negative_prompt": "text, watermark",
                "duration": 5,
                "fps": 16,
            }
        }
    
    def _load_config_defaults(self) -> Dict[str, Dict[str, Any]]:
        """Load defaults from config file"""
        defaults = {"image": {}, "audio": {}, "video": {}}
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    defaults["image"] = config.get("defaults", {}).get("image", {})
                    defaults["audio"] = config.get("defaults", {}).get("audio", {})
                    defaults["video"] = config.get("defaults", {}).get("video", {})
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load config file {CONFIG_FILE}: {e}")
        return defaults
    
    def _get_env_defaults(self) -> Dict[str, Dict[str, Any]]:
        """Load defaults from environment variables"""
        defaults = {"image": {}, "audio": {}, "video": {}}
        image_model = os.getenv("COMFY_MCP_DEFAULT_IMAGE_MODEL")
        audio_model = os.getenv("COMFY_MCP_DEFAULT_AUDIO_MODEL")
        video_model = os.getenv("COMFY_MCP_DEFAULT_VIDEO_MODEL")
        if image_model:
            defaults["image"]["model"] = image_model
        if audio_model:
            defaults["audio"]["model"] = audio_model
        if video_model:
            defaults["video"]["model"] = video_model
        return defaults
    
    def get_default(self, namespace: str, key: str, provided_value: Any = None) -> Any:
        """Get default value with precedence: provided > runtime > config > env > hardcoded"""
        if provided_value is not None:
            return provided_value
        
        # Check runtime defaults (highest priority after provided)
        if key in self._runtime_defaults.get(namespace, {}):
            return self._runtime_defaults[namespace][key]
        
        # Check config file defaults
        if key in self._config_defaults.get(namespace, {}):
            return self._config_defaults[namespace][key]
        
        # Check environment variables
        env_defaults = self._get_env_defaults()
        if key in env_defaults.get(namespace, {}):
            return env_defaults[namespace][key]
        
        # Check hardcoded defaults (lowest priority)
        if key in self._hardcoded_defaults.get(namespace, {}):
            return self._hardcoded_defaults[namespace][key]
        
        return None
    
    def get_all_defaults(self) -> Dict[str, Dict[str, Any]]:
        """Get all effective defaults (merged from all sources)"""
        env_defaults = self._get_env_defaults()
        result = {
            "image": {},
            "audio": {},
            "video": {}
        }
        
        for namespace in ["image", "audio", "video"]:
            # Start with hardcoded
            result[namespace] = self._hardcoded_defaults[namespace].copy()
            # Override with env
            result[namespace].update(env_defaults.get(namespace, {}))
            # Override with config
            result[namespace].update(self._config_defaults.get(namespace, {}))
            # Override with runtime (highest)
            result[namespace].update(self._runtime_defaults.get(namespace, {}))
        
        return result
    
    def set_defaults(self, namespace: str, defaults: Dict[str, Any], validate_models: bool = True) -> Dict[str, Any]:
        """Set runtime defaults for a namespace. Returns validation errors if any."""
        errors = []
        
        if namespace not in ["image", "audio", "video"]:
            return {"error": f"Invalid namespace: {namespace}. Must be 'image', 'audio', or 'video'"}
        
        # Validate model names if provided
        if validate_models and "model" in defaults:
            model_name = defaults["model"]
            available_models = self.comfyui_client.available_models
            if available_models and model_name not in available_models:
                errors.append(f"Model '{model_name}' not found. Available models: {available_models[:5]}...")
        
        if errors:
            return {"errors": errors}
        
        # Update runtime defaults
        if namespace not in self._runtime_defaults:
            self._runtime_defaults[namespace] = {}
        self._runtime_defaults[namespace].update(defaults)
        
        return {"success": True, "updated": defaults}
    
    def persist_defaults(self, namespace: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Persist defaults to config file"""
        # Ensure config directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load existing config
        config = {}
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                config = {}
        
        # Update defaults
        if "defaults" not in config:
            config["defaults"] = {}
        if namespace not in config["defaults"]:
            config["defaults"][namespace] = {}
        config["defaults"][namespace].update(defaults)
        
        # Save config
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            # Reload config defaults
            self._config_defaults = self._load_config_defaults()
            return {"success": True, "persisted": defaults}
        except IOError as e:
            return {"error": f"Failed to write config file: {e}"}
