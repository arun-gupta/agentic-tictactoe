"""pytest fixtures and configuration.

This file centralizes test-suite behavior that should apply consistently across
unit, integration, and contract tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.utils.env_loader import reload_env


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest and load .env for tests.

    Ensures local developer keys in `.env` are available when tests need them,
    while still allowing tests to override env vars via `patch.dict`.
    """
    reload_env()

    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests (deselect with '-m \"not unit\"')",
    )
    config.addinivalue_line(
        "markers",
        "live_llm: marks tests that make real LLM API calls (opt-in; may incur cost)",
    )
    config.addinivalue_line(
        "markers",
        "llm_integration: marks tests that validate LLM provider integrations",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark tests based on their directory."""
    for item in items:
        path = Path(str(item.fspath))
        path_str = str(path.as_posix())
        if "/tests/integration/" in path_str:
            item.add_marker(pytest.mark.integration)
            if "/tests/integration/llm/" in path_str or "/tests/integration/agents/" in path_str:
                item.add_marker(pytest.mark.llm_integration)
        elif "/tests/unit/" in path_str:
            item.add_marker(pytest.mark.unit)
