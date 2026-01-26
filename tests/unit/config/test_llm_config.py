"""Tests for LLM Configuration - Subsection 5.2.1.

Subsection tests for Phase 5.2.1: Environment Variables
These tests verify:
1. LLMConfig loads provider from LLM_PROVIDER environment variable
2. LLMConfig loads model from LLM_MODEL environment variable
3. LLMConfig loads API keys from provider-specific environment variables
4. LLMConfig supports .env file for local development
5. LLMConfig configuration hierarchy: env vars > .env file > defaults
6. LLMConfig validates API key format
7. LLMConfig validates provider value
8. LLMConfig validates model value per provider
9. LLMConfig runtime provider switching
10. LLMConfig returns error when required API key missing for selected provider
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from src.config.llm_config import LLMConfig, get_llm_config


class TestLLMConfigEnvironmentVariables:
    """Test LLM configuration loading from environment variables."""

    def test_subsection_5_2_1_1_loads_provider_from_env_var(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 1: LLMConfig loads provider from LLM_PROVIDER environment variable."""
        monkeypatch.setenv("LLM_PROVIDER", "openai")

        config = LLMConfig()
        config_data = config.get_config()

        assert config_data.provider == "openai"

    def test_subsection_5_2_1_2_loads_model_from_env_var(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 2: LLMConfig loads model from LLM_MODEL environment variable."""
        monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")

        config = LLMConfig()
        config_data = config.get_config()

        assert config_data.model == "gpt-4o-mini"

    def test_subsection_5_2_1_3_loads_api_keys_from_provider_specific_env_vars(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 3: LLMConfig loads API keys from provider-specific environment variables."""
        # Test OpenAI API key
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key-12345")

        config = LLMConfig()
        config_data = config.get_config()

        assert config_data.api_key == "sk-test-openai-key-12345"

        # Test Anthropic API key
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-anthropic-key-12345")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        config2 = LLMConfig()
        config_data2 = config2.get_config()

        assert config_data2.api_key == "sk-ant-test-anthropic-key-12345"

        # Test Google API key
        monkeypatch.setenv("LLM_PROVIDER", "gemini")
        monkeypatch.setenv("GOOGLE_API_KEY", "google-test-api-key-12345")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        config3 = LLMConfig()
        config_data3 = config3.get_config()

        assert config_data3.api_key == "google-test-api-key-12345"

    def test_subsection_5_2_1_4_supports_dotenv_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 4: LLMConfig supports .env file for local development."""
        # Clear any existing env vars first
        for key in ["LLM_PROVIDER", "LLM_MODEL", "OPENAI_API_KEY"]:
            monkeypatch.delenv(key, raising=False)

        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text(
            "LLM_PROVIDER=openai\n" "LLM_MODEL=gpt-4o\n" "OPENAI_API_KEY=sk-dotenv-test-key-12345\n"
        )

        # Mock _find_env_file to return our temp env file
        with patch("src.utils.env_loader._find_env_file", return_value=env_file):
            # Reload env to pick up the .env file
            from src.utils.env_loader import reload_env

            reload_env()

            config = LLMConfig()
            config_data = config.get_config()

            # Verify values loaded from .env file
            assert config_data.provider == "openai"
            assert config_data.model == "gpt-4o"
            assert config_data.api_key == "sk-dotenv-test-key-12345"

    def test_subsection_5_2_1_5_configuration_hierarchy(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 5: LLMConfig configuration hierarchy: env vars > .env file > defaults."""
        # Create .env file with defaults
        env_file = tmp_path / ".env"
        env_file.write_text("LLM_PROVIDER=anthropic\n" "LLM_MODEL=claude-3-5-sonnet-latest\n")

        with patch("src.utils.env_loader._find_env_file", return_value=env_file):
            from src.utils.env_loader import reload_env

            reload_env()

            # Set environment variable to override .env file
            monkeypatch.setenv("LLM_PROVIDER", "openai")
            # LLM_MODEL should still come from .env file

            config = LLMConfig()
            config_data = config.get_config()

            # Environment variable takes precedence
            assert config_data.provider == "openai"
            # .env file value used when env var not set
            assert config_data.model == "claude-3-5-sonnet-latest"

        # Test defaults when neither env var nor .env file set
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.delenv("LLM_MODEL", raising=False)

        # Mock no .env file found
        with patch("src.utils.env_loader._find_env_file", return_value=None):
            reload_env()

            config2 = LLMConfig()
            config_data2 = config2.get_config()

            # Defaults: provider and model are None
            assert config_data2.provider is None
            assert config_data2.model is None
            assert config_data2.enabled is False  # Default is disabled

    def test_subsection_5_2_1_6_validates_api_key_format(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 6: LLMConfig validates API key format (basic validation, not actual API check)."""
        # Clear any model env var from previous tests
        monkeypatch.delenv("LLM_MODEL", raising=False)

        # Valid OpenAI key format
        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-valid-openai-key-12345")

        config = LLMConfig()
        is_valid, error = config.validate_config()

        assert is_valid is True
        assert error is None

        # Invalid OpenAI key format (missing 'sk-' prefix)
        monkeypatch.setenv("OPENAI_API_KEY", "invalid-key-format")

        config2 = LLMConfig()
        is_valid2, error2 = config2.validate_config()

        assert is_valid2 is False
        assert "Invalid API key format" in error2  # type: ignore

        # Valid Anthropic key format
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-valid-anthropic-key-12345")

        config3 = LLMConfig()
        is_valid3, error3 = config3.validate_config()

        assert is_valid3 is True
        assert error3 is None

        # Invalid Anthropic key format
        monkeypatch.setenv("ANTHROPIC_API_KEY", "invalid-key")

        config4 = LLMConfig()
        is_valid4, error4 = config4.validate_config()

        assert is_valid4 is False
        assert "Invalid API key format" in error4  # type: ignore

        # Too short key
        monkeypatch.setenv("OPENAI_API_KEY", "sk-short")

        config5 = LLMConfig()
        is_valid5, error5 = config5.validate_config()

        assert is_valid5 is False
        assert "Invalid API key format" in error5  # type: ignore

    def test_subsection_5_2_1_7_validates_provider_value(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 7: LLMConfig validates provider value (must be openai, anthropic, or gemini)."""
        # Clear any model env var from previous tests
        monkeypatch.delenv("LLM_MODEL", raising=False)

        # Valid provider
        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-valid-key-12345678")

        config = LLMConfig()
        is_valid, error = config.validate_config()

        assert is_valid is True

        # Invalid provider
        monkeypatch.setenv("LLM_PROVIDER", "invalid_provider")

        config2 = LLMConfig()
        config_data = config2.get_config()

        # Invalid provider is not loaded (returns None)
        assert config_data.provider is None

        # Validation fails when enabled but no provider
        is_valid2, error2 = config2.validate_config()
        assert is_valid2 is False
        assert "provider not set" in error2  # type: ignore

        # Test set_provider with invalid value
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        config3 = LLMConfig()
        success, error3 = config3.set_provider("invalid_provider")

        assert success is False
        assert "Invalid provider" in error3  # type: ignore
        # Check all valid providers are mentioned (order may vary)
        assert "anthropic" in error3.lower()  # type: ignore
        assert "gemini" in error3.lower()  # type: ignore
        assert "openai" in error3.lower()  # type: ignore

    def test_subsection_5_2_1_8_validates_model_value_per_provider(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 8: LLMConfig validates model value per provider."""
        # Create a config.json with supported models
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {
                        "models": [
                            "gpt-4o",
                            "gpt-4o-mini",
                            "gpt-3.5-turbo",
                        ]
                    },
                    "anthropic": {
                        "models": [
                            "claude-3-5-sonnet-latest",
                            "claude-3-5-haiku-latest",
                        ]
                    },
                    "gemini": {"models": ["gemini-2.0-flash-exp", "gemini-1.5-pro"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-valid-key-12345678")

        # Valid model for OpenAI
        monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")

        config = LLMConfig(config_path=config_file)
        is_valid, error = config.validate_config()

        assert is_valid is True
        assert error is None

        # Invalid model for OpenAI
        monkeypatch.setenv("LLM_MODEL", "invalid-model")

        config2 = LLMConfig(config_path=config_file)
        is_valid2, error2 = config2.validate_config()

        assert is_valid2 is False
        assert "not supported by provider" in error2  # type: ignore

        # Valid model for Anthropic
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_MODEL", "claude-3-5-sonnet-latest")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-valid-key-12345678")

        config3 = LLMConfig(config_path=config_file)
        is_valid3, error3 = config3.validate_config()

        assert is_valid3 is True

    def test_subsection_5_2_1_9_runtime_provider_switching(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 9: LLMConfig runtime provider switching (updates provider/model without restart)."""
        # Create config file
        config_file = tmp_path / "config.json"
        config_data: dict[str, Any] = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-4o-mini"]},
                    "anthropic": {"models": ["claude-3-5-sonnet-latest"]},
                    "gemini": {"models": ["gemini-2.0-flash-exp"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        # Set up initial provider
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-key-12345678")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-anthropic-key-12345678")

        config = LLMConfig(config_path=config_file)
        initial_config = config.get_config()

        assert initial_config.provider == "openai"

        # Switch to Anthropic at runtime
        success, error = config.set_provider("anthropic", "claude-3-5-sonnet-latest")

        assert success is True
        assert error is None

        # Verify provider switched
        updated_config = config.get_config()
        assert updated_config.provider == "anthropic"
        assert updated_config.model == "claude-3-5-sonnet-latest"

        # Try switching to provider without API key
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        success2, error2 = config.set_provider("gemini")

        assert success2 is False
        assert "API key missing" in error2  # type: ignore

    def test_subsection_5_2_1_10_returns_error_when_api_key_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 10: LLMConfig returns error when required API key missing for selected provider."""
        # Clear any model env var from previous tests
        monkeypatch.delenv("LLM_MODEL", raising=False)

        # Enable LLM and set provider but no API key
        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        config = LLMConfig()
        is_valid, error = config.validate_config()

        assert is_valid is False
        assert "API key missing" in error  # type: ignore
        assert "OPENAI_API_KEY" in error  # type: ignore

        # Test with Anthropic
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        config2 = LLMConfig()
        is_valid2, error2 = config2.validate_config()

        assert is_valid2 is False
        assert "API key missing" in error2  # type: ignore
        assert "ANTHROPIC_API_KEY" in error2  # type: ignore

        # Test with Gemini
        monkeypatch.setenv("LLM_PROVIDER", "gemini")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        config3 = LLMConfig()
        is_valid3, error3 = config3.validate_config()

        assert is_valid3 is False
        assert "API key missing" in error3  # type: ignore
        assert "GOOGLE_API_KEY" in error3  # type: ignore


class TestLLMConfigDefaults:
    """Test LLM configuration defaults and disabled state."""

    def test_llm_disabled_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When LLM_ENABLED not set, LLM should be disabled by default."""
        monkeypatch.delenv("LLM_ENABLED", raising=False)

        config = LLMConfig()
        config_data = config.get_config()

        assert config_data.enabled is False

    def test_llm_enabled_with_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When LLM_ENABLED=true, LLM should be enabled."""
        monkeypatch.setenv("LLM_ENABLED", "true")

        config = LLMConfig()
        config_data = config.get_config()

        assert config_data.enabled is True

        # Test various truthy values
        for value in ["1", "yes", "True", "TRUE"]:
            monkeypatch.setenv("LLM_ENABLED", value)
            config = LLMConfig()
            assert config.get_config().enabled is True

    def test_disabled_llm_always_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When LLM is disabled, validation should always pass."""
        monkeypatch.setenv("LLM_ENABLED", "false")
        # No provider or API key set

        config = LLMConfig()
        is_valid, error = config.validate_config()

        # Should be valid even without provider/API key when disabled
        assert is_valid is True
        assert error is None


class TestLLMConfigReload:
    """Test LLM configuration reload functionality."""

    def test_reload_picks_up_new_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that reload() picks up new environment variables."""
        monkeypatch.setenv("LLM_PROVIDER", "openai")

        config = LLMConfig()
        initial_config = config.get_config()

        assert initial_config.provider == "openai"

        # Change environment
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("LLM_MODEL", "claude-3-5-sonnet-latest")

        # Reload config
        config.reload()
        reloaded_config = config.get_config()

        assert reloaded_config.provider == "anthropic"
        assert reloaded_config.model == "claude-3-5-sonnet-latest"


class TestLLMConfigGlobalInstance:
    """Test global LLM config instance."""

    def test_get_llm_config_returns_singleton(self) -> None:
        """Test that get_llm_config() returns a singleton instance."""
        config1 = get_llm_config()
        config2 = get_llm_config()

        assert config1 is config2


class TestLLMConfigPerAgentConfiguration:
    """Test per-agent LLM configuration (SCOUT_PROVIDER, STRATEGIST_PROVIDER)."""

    def test_get_agent_config_loads_agent_specific_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_agent_config() loads agent-specific provider from env vars."""
        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("SCOUT_PROVIDER", "openai")
        monkeypatch.setenv("STRATEGIST_PROVIDER", "anthropic")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-key-12345678")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-anthropic-key-12345678")

        config = LLMConfig()

        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        assert scout_config.provider == "openai"
        assert strategist_config.provider == "anthropic"

    def test_get_agent_config_loads_default_model_from_config_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_agent_config() loads default model (first model) from config.json."""
        # Create config.json with models
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2", "gpt-4o"]},
                    "anthropic": {
                        "models": ["claude-haiku-4-5-20251001", "claude-haiku-4-5"]
                    },
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("SCOUT_PROVIDER", "openai")
        monkeypatch.setenv("STRATEGIST_PROVIDER", "anthropic")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-key-12345678")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-anthropic-key-12345678")

        config = LLMConfig(config_path=config_file)

        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        # Should get first model from list for each provider
        assert scout_config.model == "gpt-5.2"
        assert strategist_config.model == "claude-haiku-4-5-20251001"

    def test_get_agent_config_includes_api_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_agent_config() includes the API key for the agent's provider."""
        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("SCOUT_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-scout-openai-key")

        config = LLMConfig()
        scout_config = config.get_agent_config("scout")

        assert scout_config.api_key == "sk-scout-openai-key"

    def test_validate_agent_config_validates_agent_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that validate_agent_config() validates agent-specific provider configuration."""
        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("SCOUT_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-valid-key-12345678")

        config = LLMConfig()
        is_valid, error = config.validate_agent_config("scout")

        assert is_valid is True
        assert error is None

    def test_validate_agent_config_fails_when_provider_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that validate_agent_config() fails when agent provider not set."""
        monkeypatch.setenv("LLM_ENABLED", "true")
        # No SCOUT_PROVIDER set

        config = LLMConfig()
        is_valid, error = config.validate_agent_config("scout")

        assert is_valid is False
        assert "SCOUT_PROVIDER" in error  # type: ignore

    def test_validate_agent_config_fails_when_api_key_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that validate_agent_config() fails when API key missing for agent's provider."""
        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("STRATEGIST_PROVIDER", "anthropic")
        # No ANTHROPIC_API_KEY set
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        config = LLMConfig()
        is_valid, error = config.validate_agent_config("strategist")

        assert is_valid is False
        assert "API key missing" in error  # type: ignore
        assert "ANTHROPIC_API_KEY" in error  # type: ignore

    def test_different_providers_per_agent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test using different providers for Scout and Strategist."""
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2"]},
                    "gemini": {"models": ["gemini-2.5-flash"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("SCOUT_PROVIDER", "openai")
        monkeypatch.setenv("STRATEGIST_PROVIDER", "gemini")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-key-12345678")
        monkeypatch.setenv("GOOGLE_API_KEY", "google-api-key-12345678")

        config = LLMConfig(config_path=config_file)

        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        # Scout uses OpenAI
        assert scout_config.provider == "openai"
        assert scout_config.model == "gpt-5.2"
        assert scout_config.api_key == "sk-openai-key-12345678"

        # Strategist uses Gemini
        assert strategist_config.provider == "gemini"
        assert strategist_config.model == "gemini-2.5-flash"
        assert strategist_config.api_key == "google-api-key-12345678"

        # Validate both agents
        assert config.validate_agent_config("scout")[0] is True
        assert config.validate_agent_config("strategist")[0] is True

    def test_same_provider_for_both_agents(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test using same provider for both Scout and Strategist."""
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        monkeypatch.setenv("LLM_ENABLED", "true")
        monkeypatch.setenv("SCOUT_PROVIDER", "openai")
        monkeypatch.setenv("STRATEGIST_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-key-12345678")

        config = LLMConfig(config_path=config_file)

        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        # Both use OpenAI
        assert scout_config.provider == "openai"
        assert strategist_config.provider == "openai"
        assert scout_config.model == "gpt-5.2"
        assert strategist_config.model == "gpt-5.2"
