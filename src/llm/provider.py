"""Abstract LLM provider interface.

This module defines the abstract base class for all LLM providers,
ensuring a consistent interface regardless of the underlying provider
(OpenAI, Anthropic, Google Gemini).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


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
