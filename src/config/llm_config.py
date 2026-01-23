"""LLM configuration management.

Loads LLM provider and model configuration from config file.
"""

import json
from pathlib import Path
from typing import Any

from src.utils.config import get_config_path


class LLMConfig:
    """LLM configuration loader.

    Loads supported models for each provider from config file.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize LLM configuration.

        Args:
            config_path: Path to config file. If None, uses default config.json.
        """
        self._config_path = config_path or get_config_path()
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self._config_path.exists():
            # Use defaults if config file doesn't exist
            self._config = self._get_default_config()
            return

        try:
            with open(self._config_path) as f:
                self._config = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ValueError(f"Failed to load config from {self._config_path}: {e}") from e

        # Validate config structure
        if "llm" not in self._config:
            self._config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration.

        Note: This is a fallback when config.json doesn't exist.
        All model names should be defined in config/config.json (single source of truth).
        """
        # Return empty config structure - config.json must exist for models
        # This ensures config.json is the single source of truth
        return {
            "llm": {
                "providers": {
                    "openai": {"models": []},
                    "anthropic": {"models": []},
                    "gemini": {"models": []},
                },
            },
        }

    def get_supported_models(self, provider: str) -> set[str]:
        """Get supported models for a provider.

        Args:
            provider: Provider name (openai, anthropic, gemini).

        Returns:
            Set of supported model names.

        Raises:
            ValueError: If provider not found in config.
        """
        provider_lower = provider.lower()
        providers = self._config.get("llm", {}).get("providers", {})

        if provider_lower not in providers:
            raise ValueError(f"Provider '{provider}' not found in config")

        models = providers[provider_lower].get("models", [])
        return set(models)

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


# Global config instance
_llm_config: LLMConfig | None = None


def get_llm_config() -> LLMConfig:
    """Get global LLM config instance.

    Returns:
        LLMConfig instance.
    """
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config
