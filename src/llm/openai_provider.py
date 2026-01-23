"""OpenAI LLM provider implementation.

This module implements the OpenAI provider using the OpenAI SDK directly.
Supported models are loaded from config file.
"""

import time
from typing import Any

import openai
from openai import OpenAI

from src.config.llm_config import get_llm_config
from src.llm.provider import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation.

    Uses the OpenAI SDK to make API calls. Supports retry logic and
    error handling for timeouts, rate limits, and authentication errors.

    Supported models are loaded from config file (config/config.json).
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key. If None, reads from .env file or OPENAI_API_KEY env var.
                    Priority: explicit api_key > .env file > environment variable.
        """
        self._api_key = self._load_api_key(api_key, "OPENAI_API_KEY", "OpenAI")

        self._client = OpenAI(api_key=self._api_key)
        self._config = get_llm_config()

    @property
    def SUPPORTED_MODELS(self) -> set[str]:
        """Get supported models from config."""
        return self._config.get_supported_models("openai")

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text using OpenAI API.

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
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract response data
            text = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                text=text,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
            )

        except openai.APIError as e:
            latency_ms = (time.time() - start_time) * 1000
            raise RuntimeError(f"OpenAI API error: {e}") from e
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            raise RuntimeError(f"Unexpected error calling OpenAI API: {e}") from e

    def _call_with_retry(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        max_retries: int = 3,
    ) -> Any:
        """Call OpenAI API with exponential backoff retry logic.

        Args:
            prompt: The input prompt
            model: The model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            max_retries: Maximum number of retry attempts

        Returns:
            OpenAI API response object

        Raises:
            openai.APIError: If API call fails after all retries
        """
        last_exception: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return response

            except openai.RateLimitError as e:
                # Rate limit error - check for Retry-After header
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

            except (openai.APITimeoutError, openai.APIConnectionError) as e:
                # Timeout or connection error - retry with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 1s, 2s, 4s
                    time.sleep(wait_time)
                    last_exception = e
                    continue
                raise

            except (openai.AuthenticationError, openai.PermissionDeniedError):
                # Authentication errors - don't retry
                raise

            except openai.APIError as e:
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
        raise RuntimeError("Failed to call OpenAI API after retries")
