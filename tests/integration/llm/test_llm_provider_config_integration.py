"""Non-live LLM integration tests.

Validates that provider classes correctly wire to shared configuration (e.g.
supported models from `config/config.json`) without making network calls.
"""

from __future__ import annotations

from src.config.llm_config import get_llm_config
from src.llm.anthropic_provider import AnthropicProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.openai_provider import OpenAIProvider


def test_openai_supported_models_loaded_from_config() -> None:
    """Test that OpenAI provider loads models from config.json."""
    provider = OpenAIProvider(api_key="test-key")
    config = get_llm_config()
    expected_models = config.get_supported_models("openai")

    # Provider should have loaded models from config
    assert len(provider.SUPPORTED_MODELS) > 0, "OpenAI provider should have models"
    assert provider.SUPPORTED_MODELS == expected_models, "Models should match config.json"


def test_anthropic_supported_models_loaded_from_config() -> None:
    """Test that Anthropic provider loads models from config.json."""
    provider = AnthropicProvider(api_key="test-key")
    config = get_llm_config()
    expected_models = config.get_supported_models("anthropic")

    # Provider should have loaded models from config
    assert len(provider.SUPPORTED_MODELS) > 0, "Anthropic provider should have models"
    assert provider.SUPPORTED_MODELS == expected_models, "Models should match config.json"


def test_gemini_supported_models_loaded_from_config() -> None:
    """Test that Gemini provider loads models from config.json."""
    provider = GeminiProvider(api_key="test-key")
    config = get_llm_config()
    expected_models = config.get_supported_models("gemini")

    # Provider should have loaded models from config
    assert len(provider.SUPPORTED_MODELS) > 0, "Gemini provider should have models"
    assert provider.SUPPORTED_MODELS == expected_models, "Models should match config.json"
