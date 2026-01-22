"""Tests for LLM provider interface (Phase 5.0.1).

Tests verify that the abstract LLMProvider interface is correctly defined
and cannot be instantiated directly.
"""

import pytest

from src.llm.provider import LLMProvider, LLMResponse


class TestLLMProviderInterface:
    """Test LLMProvider abstract interface."""

    def test_llm_provider_is_abstract(self) -> None:
        """Test that LLMProvider cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            LLMProvider()  # type: ignore[abstract]

    def test_llm_provider_has_generate_method(self) -> None:
        """Test that LLMProvider interface defines generate() method signature."""
        # Check that generate is an abstract method
        assert hasattr(LLMProvider, "generate")
        assert getattr(LLMProvider.generate, "__isabstractmethod__", False)


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_llm_response_creation(self) -> None:
        """Test creating LLMResponse with all fields."""
        response = LLMResponse(
            text="Test response",
            tokens_used=100,
            latency_ms=250.5,
        )
        assert response.text == "Test response"
        assert response.tokens_used == 100
        assert response.latency_ms == 250.5

    def test_llm_response_fields(self) -> None:
        """Test that LLMResponse has required fields."""
        response = LLMResponse(
            text="Test",
            tokens_used=50,
            latency_ms=100.0,
        )
        # Verify all fields are accessible
        assert hasattr(response, "text")
        assert hasattr(response, "tokens_used")
        assert hasattr(response, "latency_ms")
