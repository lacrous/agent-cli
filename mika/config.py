"""Configuration management for mika CLI."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


APP_NAME = "mika"


def get_config_dir() -> Path:
    """Return the platform-appropriate configuration directory."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif os.name == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    config_dir = base / APP_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Return the path to the main config JSON file."""
    return get_config_dir() / "config.json"


def get_history_dir() -> Path:
    """Return the directory used to store conversation history."""
    history_dir = get_config_dir() / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir


def get_logs_dir() -> Path:
    """Return the directory used for log files."""
    logs_dir = get_config_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_completion_dir() -> Path:
    """Return the directory used for shell completion scripts."""
    completion_dir = get_config_dir() / "completion"
    completion_dir.mkdir(parents=True, exist_ok=True)
    return completion_dir


def default_config() -> Dict[str, Any]:
    """Return the default configuration structure."""
    return {
        "provider": None,
        "model": None,
        "system_prompt": "You are a helpful coding and general-purpose assistant.",
        "api_keys": {},
        "theme": "default",
    }


def load_config() -> Dict[str, Any]:
    """Load the configuration from disk or return defaults."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = default_config()
            cfg.update(data)
            return cfg
        except (json.JSONDecodeError, OSError):
            pass
    return default_config()


def save_config(config: Dict[str, Any]) -> None:
    """Persist the configuration to disk."""
    config_path = get_config_path()
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_api_key(provider: str) -> Optional[str]:
    """Return the stored API key for a provider, or None."""
    cfg = load_config()
    key = cfg.get("api_keys", {}).get(provider)
    if key:
        return key
    env_var = f"{provider.upper().replace('-', '_')}_API_KEY"
    return os.environ.get(env_var)


def set_api_key(provider: str, api_key: str) -> None:
    """Store an API key for a provider."""
    cfg = load_config()
    cfg.setdefault("api_keys", {})[provider] = api_key
    save_config(cfg)


def set_provider(provider: str, model: Optional[str] = None) -> None:
    """Set the active provider and optional default model."""
    cfg = load_config()
    cfg["provider"] = provider
    if model is not None:
        cfg["model"] = model
    save_config(cfg)


def set_model(model: str) -> None:
    """Set the default model for the active provider."""
    cfg = load_config()
    cfg["model"] = model
    save_config(cfg)


def set_system_prompt(prompt: str) -> None:
    """Update the system prompt."""
    cfg = load_config()
    cfg["system_prompt"] = prompt
    save_config(cfg)


def get_active_provider() -> Optional[str]:
    """Return the currently configured provider, if any."""
    return load_config().get("provider")


def get_active_model() -> Optional[str]:
    """Return the currently configured model, if any."""
    return load_config().get("model")


def get_system_prompt() -> str:
    """Return the configured system prompt."""
    return load_config().get("system_prompt", default_config()["system_prompt"])
