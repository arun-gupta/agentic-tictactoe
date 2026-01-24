"""Non-live LLM integration tests.

Validates that provider classes correctly wire to shared configuration (e.g.
supported models from `config/config.json`) without making network calls.
"""

from __future__ import annotations

from src.llm.anthropic_provider import AnthropicProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.openai_provider import OpenAIProvider


def test_openai_supported_models_loaded_from_config() -> None:
    provider = OpenAIProvider(api_key="test-key")
    assert "gpt-5.2" in provider.SUPPORTED_MODELS


def test_anthropic_supported_models_loaded_from_config() -> None:
    provider = AnthropicProvider(api_key="test-key")
    assert "claude-haiku-4-5" in provider.SUPPORTED_MODELS


def test_gemini_supported_models_loaded_from_config() -> None:
    provider = GeminiProvider(api_key="test-key")
    assert "gemini-3-flash-preview" in provider.SUPPORTED_MODELS
