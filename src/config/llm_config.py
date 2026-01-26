"""LLM configuration management with environment variable support.

Subsection 5.2.1: Environment Variables
Loads LLM provider and model configuration from environment variables with hierarchy:
1. Environment variables (highest priority)
2. .env file
3. Defaults (lowest priority)

Supports:
- LLM_ENABLED: Enable/disable LLM integration (default: false)
- LLM_PROVIDER: Provider name (openai, anthropic, gemini)
- LLM_MODEL: Model name for the provider
- OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY: Provider-specific API keys
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.utils.config import get_config_path
from src.utils.env_loader import get_api_key


@dataclass
class LLMConfigData:
    """LLM configuration data.

    Attributes:
        enabled: Whether LLM integration is enabled
        provider: LLM provider name (openai, anthropic, gemini)
        model: Model name for the provider
        api_key: API key for the selected provider (None if missing)
    """

    enabled: bool
    provider: str | None
    model: str | None
    api_key: str | None


class LLMConfig:
    """LLM configuration loader with environment variable support.

    Configuration hierarchy (highest to lowest priority):
    1. Environment variables (LLM_ENABLED, LLM_PROVIDER, LLM_MODEL)
    2. .env file (loaded via env_loader)
    3. Defaults (enabled=false, provider=None, model=None)

    Validates:
    - Provider must be one of: openai, anthropic, gemini
    - Model must be supported by the provider (from config.json)
    - API key must be present for the selected provider
    """

    # Valid providers
    VALID_PROVIDERS = {"openai", "anthropic", "gemini"}

    # API key environment variable names
    API_KEY_ENV_VARS = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
    }

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize LLM configuration.

        Args:
            config_path: Path to config file. If None, uses default config.json.
        """
        self._config_path = config_path or get_config_path()
        self._file_config: dict[str, Any] = {}
        self._load_file_config()

        # Current runtime configuration
        self._enabled: bool = self._load_enabled()
        self._provider: str | None = self._load_provider()
        self._model: str | None = self._load_model()

    def _load_file_config(self) -> None:
        """Load configuration from config.json file."""
        if not self._config_path.exists():
            # Use defaults if config file doesn't exist
            self._file_config = self._get_default_config()
            return

        try:
            with open(self._config_path) as f:
                self._file_config = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ValueError(f"Failed to load config from {self._config_path}: {e}") from e

        # Validate config structure
        if "llm" not in self._file_config:
            self._file_config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration.

        Note: This is a fallback when config.json doesn't exist.
        All model names should be defined in config/config.json (single source of truth).
        """
        return {
            "llm": {
                "providers": {
                    "openai": {"models": []},
                    "anthropic": {"models": []},
                    "gemini": {"models": []},
                },
            },
        }

    def _load_enabled(self) -> bool:
        """Load LLM_ENABLED from environment.

        Returns:
            True if LLM_ENABLED=true, False otherwise (default: False)
        """
        enabled_str = os.getenv("LLM_ENABLED", "false").lower()
        return enabled_str in ("true", "1", "yes")

    def _load_provider(self) -> str | None:
        """Load LLM_PROVIDER from environment.

        Returns:
            Provider name if set and valid, None otherwise
        """
        provider = os.getenv("LLM_PROVIDER")
        if provider and provider.lower() in self.VALID_PROVIDERS:
            return provider.lower()
        return None

    def _load_model(self) -> str | None:
        """Load LLM_MODEL from environment.

        Returns:
            Model name if set, None otherwise
        """
        return os.getenv("LLM_MODEL")

    def get_config(self) -> LLMConfigData:
        """Get current LLM configuration.

        Returns:
            LLMConfigData with current configuration including API key
        """
        api_key = None
        if self._provider:
            api_key = self._get_api_key(self._provider)

        return LLMConfigData(
            enabled=self._enabled,
            provider=self._provider,
            model=self._model,
            api_key=api_key,
        )

    def get_agent_config(self, agent_name: str) -> LLMConfigData:
        """Get LLM configuration for a specific agent.

        Per-agent configuration uses {AGENT}_PROVIDER environment variables:
        - SCOUT_PROVIDER for Scout agent
        - STRATEGIST_PROVIDER for Strategist agent

        The model is automatically selected from config.json as the first model
        for the configured provider.

        Args:
            agent_name: Agent name (scout, strategist)

        Returns:
            LLMConfigData with agent-specific configuration
        """
        # Load agent-specific provider from environment
        provider = self._load_agent_provider(agent_name)

        # Get default model for this provider from config.json
        model = None
        if provider:
            model = self._get_default_model_for_provider(provider)

        # Get API key for provider
        api_key = None
        if provider:
            api_key = self._get_api_key(provider)

        return LLMConfigData(
            enabled=self._enabled,
            provider=provider,
            model=model,
            api_key=api_key,
        )

    def _load_agent_provider(self, agent_name: str) -> str | None:
        """Load provider for a specific agent from environment.

        Reads {AGENT}_PROVIDER environment variable (e.g., SCOUT_PROVIDER).

        Args:
            agent_name: Agent name (scout, strategist)

        Returns:
            Provider name if set and valid, None otherwise
        """
        env_var = f"{agent_name.upper()}_PROVIDER"
        provider = os.getenv(env_var)
        if provider and provider.lower() in self.VALID_PROVIDERS:
            return provider.lower()
        return None

    def _get_default_model_for_provider(self, provider: str) -> str | None:
        """Get default model for a provider from config.json.

        Returns the first model in the provider's model list (preserves order from config.json).

        Args:
            provider: Provider name

        Returns:
            Default model name, or None if no models configured
        """
        try:
            provider_lower = provider.lower()
            providers = self._file_config.get("llm", {}).get("providers", {})
            if provider_lower not in providers:
                return None
            models = providers[provider_lower].get("models", [])
            if models and isinstance(models[0], str):
                return str(models[0])
        except (KeyError, IndexError):
            pass
        return None

    def _get_api_key(self, provider: str) -> str | None:
        """Get API key for provider.

        Args:
            provider: Provider name

        Returns:
            API key from environment, or None if not found
        """
        env_var = self.API_KEY_ENV_VARS.get(provider)
        if not env_var:
            return None
        return get_api_key(env_var)

    def validate_config(self) -> tuple[bool, str | None]:
        """Validate current configuration.

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        # If LLM is disabled, always valid
        if not self._enabled:
            return True, None

        # If enabled, provider must be set and valid
        if not self._provider:
            return False, "LLM enabled but provider not set (LLM_PROVIDER)"

        if self._provider not in self.VALID_PROVIDERS:
            return (
                False,
                f"Invalid provider '{self._provider}', must be one of: {', '.join(sorted(self.VALID_PROVIDERS))}",
            )

        # Validate API key first (more critical than model)
        api_key = self._get_api_key(self._provider)
        if not api_key:
            env_var = self.API_KEY_ENV_VARS[self._provider]
            return False, f"API key missing for provider '{self._provider}' (set {env_var})"

        # Validate model if set
        if self._model:
            supported_models = self.get_supported_models(self._provider)
            if supported_models and self._model not in supported_models:
                return False, f"Model '{self._model}' not supported by provider '{self._provider}'"

        # Basic API key format validation
        if not self._validate_api_key_format(api_key, self._provider):
            return False, f"Invalid API key format for provider '{self._provider}'"

        return True, None

    def validate_agent_config(self, agent_name: str) -> tuple[bool, str | None]:
        """Validate configuration for a specific agent.

        Args:
            agent_name: Agent name (scout, strategist)

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
        """
        # If LLM is disabled, always valid
        if not self._enabled:
            return True, None

        # Get agent-specific config
        config = self.get_agent_config(agent_name)

        # If enabled, provider must be set
        if not config.provider:
            env_var = f"{agent_name.upper()}_PROVIDER"
            return False, f"LLM enabled but provider not set for {agent_name} (set {env_var})"

        # Validate provider is valid
        if config.provider not in self.VALID_PROVIDERS:
            return (
                False,
                f"Invalid provider '{config.provider}' for {agent_name}, must be one of: {', '.join(sorted(self.VALID_PROVIDERS))}",
            )

        # Validate API key exists
        if not config.api_key:
            env_var = self.API_KEY_ENV_VARS[config.provider]
            return (
                False,
                f"API key missing for {agent_name} provider '{config.provider}' (set {env_var})",
            )

        # Validate API key format
        if not self._validate_api_key_format(config.api_key, config.provider):
            return False, f"Invalid API key format for {agent_name} provider '{config.provider}'"

        return True, None

    def _validate_api_key_format(self, api_key: str, provider: str) -> bool:
        """Basic API key format validation (not actual API check).

        Args:
            api_key: API key to validate
            provider: Provider name

        Returns:
            True if format appears valid, False otherwise
        """
        # Basic validation: non-empty, reasonable length
        if not api_key or len(api_key) < 10:
            return False

        # Provider-specific prefix checks
        if provider == "openai" and not api_key.startswith("sk-"):
            return False
        if provider == "anthropic" and not api_key.startswith("sk-ant-"):
            return False

        return True

    def set_provider(self, provider: str, model: str | None = None) -> tuple[bool, str | None]:
        """Runtime provider switching.

        Updates provider and model without restart.

        Args:
            provider: Provider name (openai, anthropic, gemini)
            model: Model name (optional)

        Returns:
            Tuple of (success, error_message)
        """
        provider_lower = provider.lower()

        # Validate provider
        if provider_lower not in self.VALID_PROVIDERS:
            return (
                False,
                f"Invalid provider '{provider}', must be one of: {', '.join(sorted(self.VALID_PROVIDERS))}",
            )

        # Validate model if provided
        if model:
            supported_models = self.get_supported_models(provider_lower)
            if supported_models and model not in supported_models:
                return False, f"Model '{model}' not supported by provider '{provider_lower}'"

        # Validate API key exists
        api_key = self._get_api_key(provider_lower)
        if not api_key:
            env_var = self.API_KEY_ENV_VARS[provider_lower]
            return False, f"API key missing for provider '{provider_lower}' (set {env_var})"

        # Update runtime config
        self._provider = provider_lower
        self._model = model

        return True, None

    def get_supported_models(self, provider: str) -> set[str]:
        """Get supported models for a provider from config.json.

        Args:
            provider: Provider name (openai, anthropic, gemini).

        Returns:
            Set of supported model names.

        Raises:
            ValueError: If provider not found in config.
        """
        provider_lower = provider.lower()
        providers = self._file_config.get("llm", {}).get("providers", {})

        if provider_lower not in providers:
            raise ValueError(f"Provider '{provider}' not found in config")

        models = providers[provider_lower].get("models", [])
        return set(models)

    def reload(self) -> None:
        """Reload configuration from environment and file."""
        self._load_file_config()
        self._enabled = self._load_enabled()
        self._provider = self._load_provider()
        self._model = self._load_model()


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
