"""Google Gemini LLM provider implementation.

This module implements the Gemini provider using the Google Generative AI SDK directly.
Supports models: gemini-3-flash-preview (Gemini 3 Flash - most balanced model)
Reference: https://ai.google.dev/gemini-api/docs/models
"""

import os
import time

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from google.generativeai.types import GenerateContentResponse

from src.llm.provider import LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation.

    Uses the Google Generative AI SDK to make API calls. Supports retry logic and
    error handling for timeouts, rate limits, and authentication errors.
    """

    # Supported Gemini models (Gemini 3 Flash - most balanced model)
    # See https://ai.google.dev/gemini-api/docs/models
    SUPPORTED_MODELS = {
        "gemini-3-flash-preview",  # Most balanced model built for speed, scale, and frontier intelligence
        # Aliases
        "gemini-3-flash",
    }

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize Gemini provider.

        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
        """
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")

        genai.configure(api_key=api_key)  # type: ignore[attr-defined]
        self.api_key = api_key

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text using Google Gemini API.

        Args:
            prompt: The input prompt to send to the LLM
            model: The model name (must be one of SUPPORTED_MODELS)
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            LLMResponse containing the generated text, token usage, and latency

        Raises:
            ValueError: If model is not supported or parameters are invalid
            RuntimeError: If the API call fails after retries
        """
        # Validate model
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. Supported models: {', '.join(self.SUPPORTED_MODELS)}"
            )

        # Validate parameters
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")

        start_time = time.time()

        try:
            # Make API call with retry logic
            response = self._call_with_retry(
                prompt=prompt,
                model=model,
                max_output_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract response data
            text = response.text if hasattr(response, "text") else ""

            # Get token usage from response
            tokens_used = 0
            if hasattr(response, "usage_metadata"):
                usage = response.usage_metadata
                tokens_used = (usage.prompt_token_count or 0) + (usage.candidates_token_count or 0)
            elif hasattr(response, "usage"):
                # Fallback for different response formats
                usage = response.usage
                tokens_used = (getattr(usage, "prompt_token_count", 0) or 0) + (
                    getattr(usage, "candidates_token_count", 0) or 0
                )

            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                text=text,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
            )

        except google_exceptions.GoogleAPIError as e:
            latency_ms = (time.time() - start_time) * 1000
            raise RuntimeError(f"Google Gemini API error: {e}") from e
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise RuntimeError(f"Unexpected error calling Google Gemini API: {e}") from e

    def _call_with_retry(
        self,
        prompt: str,
        model: str,
        max_output_tokens: int,
        temperature: float,
        max_retries: int = 3,
    ) -> GenerateContentResponse:
        """Call Google Gemini API with exponential backoff retry logic.

        Args:
            prompt: The input prompt
            model: The model name
            max_output_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            max_retries: Maximum number of retry attempts

        Returns:
            Google Gemini API response object

        Raises:
            google_exceptions.GoogleAPIError: If API call fails after all retries
        """
        last_exception: Exception | None = None

        for attempt in range(max_retries):
            try:
                # Create model instance
                gemini_model = genai.GenerativeModel(model)  # type: ignore[attr-defined]

                # Generate content
                response = gemini_model.generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": max_output_tokens,
                        "temperature": temperature,
                    },
                )
                return response

            except google_exceptions.ResourceExhausted as e:
                # Rate limit error (429) - check for Retry-After header
                retry_after = None
                if hasattr(e, "response") and e.response:
                    headers = getattr(e.response, "headers", {})
                    retry_after = headers.get("Retry-After") if headers else None

                if retry_after:
                    wait_time = float(retry_after)
                else:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2**attempt

                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                raise

            except (
                google_exceptions.DeadlineExceeded,
                google_exceptions.ServiceUnavailable,
            ) as e:
                # Timeout or service unavailable - retry with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 1s, 2s, 4s
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                raise

            except (
                google_exceptions.Unauthenticated,
                google_exceptions.PermissionDenied,
            ):
                # Authentication errors - don't retry
                raise

            except google_exceptions.GoogleAPIError as e:
                # Other API errors - retry with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                raise

        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        raise RuntimeError("Failed to call Google Gemini API after retries")
