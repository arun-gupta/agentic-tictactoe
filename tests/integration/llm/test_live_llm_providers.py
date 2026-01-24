"""Live LLM integration tests across providers.

These tests make real network calls and may incur cost. They are opt-in and
skipped unless explicitly enabled.
"""

from __future__ import annotations

import os
from collections.abc import Callable

import pytest

from src.config.llm_config import get_llm_config
from src.llm.anthropic_provider import AnthropicProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.openai_provider import OpenAIProvider
from src.llm.provider import LLMProvider


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip() in {"1", "true", "yes", "on", "TRUE", "YES"}


def _live_tests_enabled() -> bool:
    return _truthy_env("RUN_LIVE_LLM_TESTS")


def _selected_providers() -> set[str] | None:
    raw = os.getenv("LIVE_LLM_PROVIDERS", "").strip()
    if not raw:
        return None
    return {p.strip().lower() for p in raw.split(",") if p.strip()}


def _get_default_model(provider: str) -> str:
    """Get default model from config.json (single source of truth)."""
    config = get_llm_config()
    models = config.get_supported_models(provider)
    if not models:
        raise ValueError(f"No models configured for provider: {provider}")
    return sorted(models)[0]  # Use first model alphabetically as default


ProviderCase = tuple[str, str, str, Callable[[], LLMProvider]]


CASES: list[ProviderCase] = [
    ("openai", "OPENAI_API_KEY", "LIVE_LLM_OPENAI_MODEL", OpenAIProvider),
    ("anthropic", "ANTHROPIC_API_KEY", "LIVE_LLM_ANTHROPIC_MODEL", AnthropicProvider),
    ("gemini", "GOOGLE_API_KEY", "LIVE_LLM_GEMINI_MODEL", GeminiProvider),
]


@pytest.mark.live_llm
@pytest.mark.parametrize(
    ("provider_name", "api_key_env", "model_env", "provider_factory"),
    CASES,
)
def test_live_llm_generate_smoke(
    provider_name: str,
    api_key_env: str,
    model_env: str,
    provider_factory: Callable[[], LLMProvider],
) -> None:
    if not _live_tests_enabled():
        pytest.skip("Set RUN_LIVE_LLM_TESTS=1 to enable live LLM tests.")

    selected = _selected_providers()
    if selected is not None and provider_name not in selected:
        pytest.skip(f"{provider_name} not selected via LIVE_LLM_PROVIDERS.")

    if not os.getenv(api_key_env):
        pytest.skip(f"{api_key_env} not set; configure it in .env or environment.")

    # Get default model from config.json (single source of truth)
    default_model = _get_default_model(provider_name)
    model = os.getenv(model_env, default_model)

    provider = provider_factory()
    response = provider.generate(
        prompt="Reply with exactly: pong",
        model=model,
        max_tokens=16,
        temperature=0.0,
    )

    assert "pong" in response.text.strip().lower()
    assert response.tokens_used > 0
    assert response.latency_ms > 0
