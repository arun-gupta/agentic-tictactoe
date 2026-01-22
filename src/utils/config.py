"""Configuration management utilities."""

from pathlib import Path


def get_config_path() -> Path:
    """Get path to config file.

    Looks for config.json in:
    1. Current working directory
    2. Project root (where pyproject.toml is)
    3. config/ directory in project root

    Returns:
        Path to config.json file.
    """
    # Try current directory first
    current_dir = Path.cwd()
    config_path = current_dir / "config.json"
    if config_path.exists():
        return config_path

    # Try config/ directory in current directory
    config_path = current_dir / "config" / "config.json"
    if config_path.exists():
        return config_path

    # Try project root (look for pyproject.toml)
    project_root = _find_project_root()
    if project_root:
        config_path = project_root / "config" / "config.json"
        if config_path.exists():
            return config_path

        config_path = project_root / "config.json"
        if config_path.exists():
            return config_path

    # Default to config/config.json in project root
    project_root = project_root or current_dir
    return project_root / "config" / "config.json"


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
