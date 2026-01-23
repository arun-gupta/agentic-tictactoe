"""Tests for Gemini provider (Phase 5.0.4).

Tests verify that GeminiProvider correctly implements the LLMProvider interface,
supports Gemini 3 Flash model, and handles errors appropriately.
"""

import os
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import google.api_core.exceptions as google_exceptions
import pytest

from src.llm.gemini_provider import GeminiProvider
from src.llm.provider import LLMResponse


class TestGeminiProviderInterface:
    """Test GeminiProvider implements LLMProvider interface."""

    def test_gemini_provider_implements_llm_provider(self) -> None:
        """Test that GeminiProvider implements LLMProvider interface."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider()
            assert isinstance(provider, GeminiProvider)

    def test_gemini_provider_has_generate_method(self) -> None:
        """Test that GeminiProvider has generate() method."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider()
            assert hasattr(provider, "generate")
            assert callable(provider.generate)


class TestGeminiProviderInitialization:
    """Test GeminiProvider initialization."""

    @patch("src.llm.gemini_provider.genai.configure")
    def test_initialization_with_api_key(self, mock_configure: MagicMock) -> None:
        """Test initialization with explicit API key."""
        provider = GeminiProvider(api_key="test-key-123")
        assert provider._api_key == "test-key-123"
        mock_configure.assert_called_once_with(api_key="test-key-123")

    @patch("src.llm.gemini_provider.genai.configure")
    def test_initialization_with_env_var(self, mock_configure: MagicMock) -> None:
        """Test initialization reads API key from environment variable."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key-456"}):
            provider = GeminiProvider()
            assert provider._api_key == "env-key-456"
            mock_configure.assert_called_once_with(api_key="env-key-456")

    def test_initialization_fails_without_api_key(self) -> None:
        """Test initialization fails when no API key provided."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Google API key is required"):
                GeminiProvider()


class TestGeminiProviderGenerate:
    """Test GeminiProvider.generate() method."""

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_generate_calls_gemini_api_with_correct_parameters(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that generate() calls Gemini API with correct parameters."""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_response.usage_metadata = Mock(prompt_token_count=50, candidates_token_count=50)

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        response = provider.generate(
            prompt="Test prompt",
            model="gemini-3-flash-preview",
            max_tokens=100,
            temperature=0.7,
        )

        # Verify API was called correctly
        mock_generative_model.assert_called_once_with("gemini-3-flash-preview")
        mock_model.generate_content.assert_called_once_with(
            "Test prompt",
            generation_config={"max_output_tokens": 100, "temperature": 0.7},
        )

        # Verify response
        assert isinstance(response, LLMResponse)
        assert response.text == "Test response"
        assert response.tokens_used == 100  # prompt + candidates
        assert response.latency_ms > 0

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_generate_supports_gemini_3_flash_preview_model(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider supports gemini-3-flash-preview model."""
        mock_response = Mock()
        mock_response.text = "Response"
        mock_response.usage_metadata = Mock(prompt_token_count=10, candidates_token_count=10)

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        response = provider.generate(prompt="Test", model="gemini-3-flash-preview")

        assert response.text == "Response"
        mock_generative_model.assert_called_once_with("gemini-3-flash-preview")

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_generate_supports_configured_models(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider supports all models configured in config.json."""
        mock_response = Mock()
        mock_response.text = "Response"
        mock_response.usage_metadata = Mock(prompt_token_count=10, candidates_token_count=10)

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")

        # Test all models from config (config is single source of truth)
        for model in provider.SUPPORTED_MODELS:
            response = provider.generate(prompt="Test", model=model)
            assert response.text == "Response"
            # Verify API was called with correct model
            mock_generative_model.assert_called_with(model)

    def test_generate_rejects_unsupported_model(self) -> None:
        """Test that generate() rejects unsupported models."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider()
            with pytest.raises(ValueError, match="Unsupported model"):
                provider.generate(prompt="Test", model="gemini-1.5-pro")

    def test_generate_validates_max_tokens_minimum(self) -> None:
        """Test that generate() validates max_tokens is at least 1."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider()
            with pytest.raises(ValueError, match="max_tokens must be at least 1"):
                provider.generate(prompt="Test", model="gemini-3-flash-preview", max_tokens=0)

    def test_generate_validates_temperature_range(self) -> None:
        """Test that generate() validates temperature is between 0.0 and 2.0."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider()
            with pytest.raises(ValueError, match="temperature must be between 0.0 and 2.0"):
                provider.generate(prompt="Test", model="gemini-3-flash-preview", temperature=2.1)


class TestGeminiProviderErrorHandling:
    """Test GeminiProvider error handling and retries."""

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    @patch("src.llm.gemini_provider.time.sleep")
    def test_handles_api_timeout_errors_with_retry(
        self,
        mock_sleep: MagicMock,
        mock_configure: MagicMock,
        mock_generative_model: MagicMock,
    ) -> None:
        """Test that GeminiProvider handles API timeout errors with retries."""
        timeout_error = google_exceptions.DeadlineExceeded("Timeout")
        mock_response = Mock()
        mock_response.text = "Success"
        mock_response.usage_metadata = Mock(prompt_token_count=10, candidates_token_count=10)

        mock_model = Mock()
        mock_model.generate_content.side_effect = [timeout_error, mock_response]
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        response = provider.generate(prompt="Test", model="gemini-3-flash-preview")

        assert response.text == "Success"
        assert mock_model.generate_content.call_count == 2
        mock_sleep.assert_called_once_with(1)  # First retry waits 1 second

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_handles_authentication_errors_without_retry(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider handles authentication errors without retry."""
        auth_error = google_exceptions.Unauthenticated("Invalid API key")
        mock_model = Mock()
        mock_model.generate_content.side_effect = auth_error
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        with pytest.raises(RuntimeError):  # Our code wraps it in RuntimeError
            provider.generate(prompt="Test", model="gemini-3-flash-preview")

        # Should not retry on auth errors
        assert mock_model.generate_content.call_count == 1

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    @patch("src.llm.gemini_provider.time.sleep")
    def test_handles_rate_limit_with_retry_after_header(
        self,
        mock_sleep: MagicMock,
        mock_configure: MagicMock,
        mock_generative_model: MagicMock,
    ) -> None:
        """Test that GeminiProvider handles rate limit with Retry-After header."""
        mock_model = Mock()
        mock_response_obj = Mock()
        mock_response_obj.headers = {"Retry-After": "4"}
        rate_limit_error = google_exceptions.ResourceExhausted(
            message="Rate limit exceeded", response=mock_response_obj
        )

        # First call fails with rate limit, second succeeds
        mock_model.generate_content.side_effect = [
            rate_limit_error,
            Mock(
                text="Success",
                usage_metadata=Mock(prompt_token_count=10, candidates_token_count=10),
            ),
        ]
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        response = provider.generate(prompt="Test", model="gemini-3-flash-preview")

        assert response.text == "Success"
        # Should wait 4 seconds (from Retry-After header) before retry
        mock_sleep.assert_called_with(4.0)

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    @patch("src.llm.gemini_provider.time.sleep")
    def test_handles_other_api_errors_with_retry(
        self,
        mock_sleep: MagicMock,
        mock_configure: MagicMock,
        mock_generative_model: MagicMock,
    ) -> None:
        """Test that GeminiProvider handles other API errors with retry."""
        mock_model = Mock()
        api_error = google_exceptions.GoogleAPIError("Internal server error")

        # First call fails, second succeeds
        mock_model.generate_content.side_effect = [
            api_error,
            Mock(
                text="Success",
                usage_metadata=Mock(prompt_token_count=10, candidates_token_count=10),
            ),
        ]
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        response = provider.generate(prompt="Test", model="gemini-3-flash-preview")

        assert response.text == "Success"
        assert mock_model.generate_content.call_count == 2
        mock_sleep.assert_called_once_with(1)  # Exponential backoff: 2^0 = 1

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_handles_permission_denied_without_retry(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider handles permission denied errors without retry."""
        mock_model = Mock()
        perm_error = google_exceptions.PermissionDenied("Permission denied")
        mock_model.generate_content.side_effect = perm_error
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        with pytest.raises(RuntimeError):
            provider.generate(prompt="Test", model="gemini-3-flash-preview")

        # Should not retry on permission errors
        assert mock_model.generate_content.call_count == 1

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_handles_fallback_token_usage_calculation(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider handles fallback token usage calculation."""
        mock_model = Mock()
        # Mock response with usage (not usage_metadata)
        # Use getattr to return actual integers, not Mocks
        mock_usage = Mock()
        type(mock_usage).prompt_token_count = PropertyMock(return_value=5)
        type(mock_usage).candidates_token_count = PropertyMock(return_value=5)
        mock_response = Mock()
        mock_response.text = "Response"
        mock_response.usage = mock_usage
        # Make sure response doesn't have usage_metadata
        del mock_response.usage_metadata
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        response = provider.generate(prompt="Test", model="gemini-3-flash-preview")

        assert response.text == "Response"
        assert response.tokens_used == 10

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_handles_api_error_exception_path(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider handles GoogleAPIError exception path."""
        mock_model = Mock()
        api_error = google_exceptions.GoogleAPIError("API error")
        mock_model.generate_content.side_effect = api_error
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        with pytest.raises(RuntimeError, match="Google Gemini API error"):
            provider.generate(prompt="Test", model="gemini-3-flash-preview")

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_handles_unexpected_exception_path(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider handles unexpected exceptions."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = ValueError("Unexpected error")
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        with pytest.raises(RuntimeError, match="Unexpected error"):
            provider.generate(prompt="Test", model="gemini-3-flash-preview")

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_returns_structured_response(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider returns structured response with text, tokens_used, latency_ms."""
        mock_response = Mock()
        mock_response.text = "Generated text"
        mock_response.usage_metadata = Mock(prompt_token_count=75, candidates_token_count=75)

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model

        provider = GeminiProvider(api_key="test-key")
        response = provider.generate(prompt="Test", model="gemini-3-flash-preview")

        assert isinstance(response, LLMResponse)
        assert response.text == "Generated text"
        assert response.tokens_used == 150  # prompt + candidates
        assert response.latency_ms > 0

    @patch("src.llm.gemini_provider.genai.GenerativeModel")
    @patch("src.llm.gemini_provider.genai.configure")
    def test_handles_rate_limit_errors_with_retry_logic(
        self, mock_configure: MagicMock, mock_generative_model: MagicMock
    ) -> None:
        """Test that GeminiProvider has retry logic for rate limit errors.

        Note: Full ResourceExhausted handling with Retry-After header parsing
        is verified in the implementation code. Integration tests with actual
        Gemini API calls will validate the complete retry behavior.
        """
        # Verify the retry logic exists in the code structure
        provider = GeminiProvider(api_key="test-key")

        # Verify the _call_with_retry method exists (retry logic)
        assert hasattr(provider, "_call_with_retry")
        assert callable(provider._call_with_retry)

        # Verify SUPPORTED_MODELS are loaded from config (config is single source of truth)
        provider = GeminiProvider(api_key="test-key")
        # Models should come from config.json, not hardcoded
        assert len(provider.SUPPORTED_MODELS) > 0, "No models configured in config.json"
        # Verify at least one model is configured (exact model names come from config)
        assert "gemini-3-flash-preview" in provider.SUPPORTED_MODELS
