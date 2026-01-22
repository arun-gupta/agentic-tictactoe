"""Tests for LLM configuration management."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config.llm_config import LLMConfig, get_llm_config


class TestLLMConfigInitialization:
    """Test LLMConfig initialization."""

    def test_initialization_with_default_config_path(self, tmp_path: Path) -> None:
        """Test that LLMConfig uses default config path when not provided."""
        with patch("src.config.llm_config.get_config_path", return_value=tmp_path / "config.json"):
            # Config file doesn't exist, should use defaults
            config = LLMConfig()
            assert config._config_path == tmp_path / "config.json"
            assert "llm" in config._config

    def test_initialization_with_custom_config_path(self, tmp_path: Path) -> None:
        """Test that LLMConfig uses custom config path when provided."""
        custom_path = tmp_path / "custom.json"
        config = LLMConfig(config_path=custom_path)
        assert config._config_path == custom_path

    def test_initialization_loads_config_from_file(self, tmp_path: Path) -> None:
        """Test that LLMConfig loads config from existing file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2", "gpt-4o"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = LLMConfig(config_path=config_file)
        assert config._config == config_data

    def test_initialization_uses_defaults_when_file_not_exists(self, tmp_path: Path) -> None:
        """Test that LLMConfig uses default config when file doesn't exist."""
        config_file = tmp_path / "nonexistent.json"
        config = LLMConfig(config_path=config_file)
        # Should use default config
        assert "llm" in config._config
        assert "providers" in config._config["llm"]
        assert "openai" in config._config["llm"]["providers"]

    def test_initialization_handles_json_decode_error(self, tmp_path: Path) -> None:
        """Test that LLMConfig handles JSON decode errors."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("invalid json content {")

        with pytest.raises(ValueError, match="Failed to load config"):
            LLMConfig(config_path=config_file)

    def test_initialization_handles_file_read_error(self, tmp_path: Path) -> None:
        """Test that LLMConfig handles file read errors."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"llm": {"providers": {}}}')  # Create file first

        # Make file unreadable by mocking open to raise OSError on read
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(ValueError, match="Failed to load config"):
                LLMConfig(config_path=config_file)

    def test_initialization_uses_defaults_when_llm_key_missing(self, tmp_path: Path) -> None:
        """Test that LLMConfig uses defaults when 'llm' key is missing."""
        config_file = tmp_path / "config.json"
        config_data = {"other": "data"}
        config_file.write_text(json.dumps(config_data))

        config = LLMConfig(config_path=config_file)
        # Should use default config when 'llm' key missing
        assert "llm" in config._config
        assert "providers" in config._config["llm"]


class TestLLMConfigGetSupportedModels:
    """Test get_supported_models() method."""

    def test_get_supported_models_returns_models_for_provider(self, tmp_path: Path) -> None:
        """Test that get_supported_models returns models for specified provider."""
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2", "gpt-4o"]},
                    "anthropic": {"models": ["claude-haiku-4-5-20251001"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = LLMConfig(config_path=config_file)
        models = config.get_supported_models("openai")

        assert models == {"gpt-5.2", "gpt-4o"}

    def test_get_supported_models_is_case_insensitive(self, tmp_path: Path) -> None:
        """Test that get_supported_models is case insensitive for provider name."""
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = LLMConfig(config_path=config_file)
        models_upper = config.get_supported_models("OPENAI")
        models_lower = config.get_supported_models("openai")

        assert models_upper == models_lower

    def test_get_supported_models_raises_error_for_unknown_provider(self, tmp_path: Path) -> None:
        """Test that get_supported_models raises ValueError for unknown provider."""
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2"]},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = LLMConfig(config_path=config_file)
        with pytest.raises(ValueError, match="Provider 'unknown' not found"):
            config.get_supported_models("unknown")

    def test_get_supported_models_returns_empty_set_when_no_models(self, tmp_path: Path) -> None:
        """Test that get_supported_models returns empty set when provider has no models."""
        config_file = tmp_path / "config.json"
        config_data = {
            "llm": {
                "providers": {
                    "openai": {},
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = LLMConfig(config_path=config_file)
        models = config.get_supported_models("openai")

        assert models == set()


class TestLLMConfigReload:
    """Test reload() method."""

    def test_reload_updates_config_from_file(self, tmp_path: Path) -> None:
        """Test that reload() updates config from file."""
        config_file = tmp_path / "config.json"
        initial_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2"]},
                }
            }
        }
        config_file.write_text(json.dumps(initial_data))

        config = LLMConfig(config_path=config_file)
        assert config.get_supported_models("openai") == {"gpt-5.2"}

        # Update config file
        updated_data = {
            "llm": {
                "providers": {
                    "openai": {"models": ["gpt-5.2", "gpt-4o"]},
                }
            }
        }
        config_file.write_text(json.dumps(updated_data))

        # Reload config
        config.reload()
        assert config.get_supported_models("openai") == {"gpt-5.2", "gpt-4o"}


class TestGetLLMConfig:
    """Test get_llm_config() function."""

    def test_get_llm_config_returns_singleton(self) -> None:
        """Test that get_llm_config returns the same instance."""
        # Reset global instance
        import src.config.llm_config

        src.config.llm_config._llm_config = None

        config1 = get_llm_config()
        config2 = get_llm_config()

        assert config1 is config2
