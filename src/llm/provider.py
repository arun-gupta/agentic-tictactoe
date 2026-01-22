"""Abstract LLM provider interface.

This module defines the abstract base class for all LLM providers,
ensuring a consistent interface regardless of the underlying provider
(OpenAI, Anthropic, Google Gemini).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.utils.env_loader import get_api_key


@dataclass
class LLMResponse:
    """Structured response from LLM provider.

    Attributes:
        text: The generated text response from the LLM
        tokens_used: Total tokens used (input + output)
        latency_ms: Response latency in milliseconds
    """

    text: str
    tokens_used: int
    latency_ms: float


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    All LLM providers must implement the generate() method to provide
    a consistent interface for LLM calls across different providers.
    """

    def _load_api_key(self, api_key: str | None, env_key_name: str, provider_name: str) -> str:
        """Load API key with priority: explicit > .env file > environment variable.

        Args:
            api_key: Explicitly provided API key (optional)
            env_key_name: Name of the environment variable (e.g., "OPENAI_API_KEY")
            provider_name: Name of the provider (e.g., "OpenAI") for error messages

        Returns:
            API key string

        Raises:
            ValueError: If API key is not found in any source
        """
        loaded_key = api_key or get_api_key(env_key_name)
        if not loaded_key:
            raise ValueError(
                f"{provider_name} API key is required. Set {env_key_name} in .env file, "
                "environment variable, or pass api_key parameter."
            )
        return loaded_key

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text using the LLM provider.

        Args:
            prompt: The input prompt to send to the LLM
            model: The model name to use (e.g., 'gpt-4o', 'claude-3-5-sonnet')
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            LLMResponse containing the generated text, token usage, and latency

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If the LLM call fails (timeout, API error, etc.)
        """
        pass
