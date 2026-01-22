"""LLM provider abstraction layer.

This module provides an abstraction layer for LLM providers, allowing
the system to work with multiple LLM providers (OpenAI, Anthropic, Google Gemini)
through a unified interface.

The implementation uses Pydantic AI under the hood for type-safe agent definitions
and structured outputs, but provides a provider abstraction for flexibility.
"""

from src.llm.openai_provider import OpenAIProvider
from src.llm.provider import LLMProvider, LLMResponse

__all__ = ["LLMProvider", "LLMResponse", "OpenAIProvider"]
