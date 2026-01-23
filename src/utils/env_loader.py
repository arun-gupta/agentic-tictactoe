"""Environment variable loader with .env file support.

Loads environment variables from .env file first, then falls back to
system environment variables. Priority: .env file > environment variables.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def _find_env_file() -> Path | None:
    """Find .env file in project directory.

    Looks for .env in:
    1. Current working directory
    2. Project root (where pyproject.toml is)

    Returns:
        Path to .env file, or None if not found.
    """
    # Try current directory first
    current_dir = Path.cwd()
    env_path = current_dir / ".env"
    if env_path.exists():
        return env_path

    # Try project root (look for pyproject.toml)
    project_root = _find_project_root()
    if project_root:
        env_path = project_root / ".env"
        if env_path.exists():
            return env_path

    return None


def _find_project_root() -> Path | None:
    """Find project root by looking for pyproject.toml.

    Returns:
        Path to project root, or None if not found.
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return None


# Load .env file on module import (if it exists)
_env_file = _find_env_file()
if _env_file:
    load_dotenv(_env_file, override=False)  # Don't override existing env vars


def get_api_key(key_name: str, default: str | None = None) -> str | None:
    """Get API key from .env file or environment variable.

    Priority order:
    1. .env file (loaded on module import)
    2. Environment variable
    3. Default value (if provided)

    Args:
        key_name: Name of the environment variable (e.g., "OPENAI_API_KEY")
        default: Default value if not found (optional)

    Returns:
        API key value, or None if not found and no default provided.
    """
    # .env file is already loaded by load_dotenv() above
    # os.getenv() will check both .env-loaded vars and system env vars
    return os.getenv(key_name, default)


def reload_env() -> None:
    """Reload .env file (useful for testing or config changes)."""
    global _env_file
    _env_file = _find_env_file()
    if _env_file:
        load_dotenv(_env_file, override=True)  # Override existing vars on reload
