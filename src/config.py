"""Configuration management for team balancing system."""

import json
import sys
from typing import Dict, Any


# Global configuration variable
CONFIG: Dict[str, Any] = {}


def load_config(config_path: str) -> None:
    """Load configuration from JSON file."""
    global CONFIG
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            CONFIG = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse config file '{config_path}': {e}")
        sys.exit(1)


def get_config(key: str, default: Any = None) -> Any:
    """Safely get a value from the global configuration."""
    return CONFIG.get(key, default)
