"""Pydantic AI agent definitions for type-safe agent workflows.

This module creates Pydantic AI Agent instances for Scout and Strategist
agents with structured output validation using domain models.
"""

import os
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIModel

from src.config.llm_config import get_llm_config
from src.domain.agent_models import BoardAnalysis, Strategy
from src.utils.env_loader import get_api_key


def _get_pydantic_ai_model(provider: str, model: str) -> Any:
    """Get Pydantic AI model instance for a provider.

    Pydantic AI models read API keys from environment variables, so we ensure
    the appropriate environment variable is set before creating the model.

    Args:
        provider: Provider name (openai, anthropic, gemini)
        model: Model name (must be one of the models configured in config/config.json)

    Returns:
        Pydantic AI model instance

    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    provider_lower = provider.lower()

    if provider_lower == "openai":
        api_key = get_api_key("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file or environment variables")
        # Pydantic AI reads from environment, so ensure it's set
        if os.environ.get("OPENAI_API_KEY") != api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        return OpenAIModel(model)

    if provider_lower == "anthropic":
        api_key = get_api_key("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file or environment variables")
        # Pydantic AI reads from environment, so ensure it's set
        if os.environ.get("ANTHROPIC_API_KEY") != api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        return AnthropicModel(model)

    if provider_lower == "gemini":
        api_key = get_api_key("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables")
        # Pydantic AI reads from environment, so ensure it's set
        if os.environ.get("GOOGLE_API_KEY") != api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        return GoogleModel(model)

    raise ValueError(f"Unsupported provider: {provider}")


def create_scout_agent(
    provider: str | None = None, model: str | None = None
) -> Agent[None, BoardAnalysis]:
    """Create Pydantic AI Agent for Scout with BoardAnalysis response model.

    Args:
        provider: LLM provider name (openai, anthropic, gemini). If None, uses first available.
        model: Model name. If None, uses first model from config for the provider.

    Returns:
        Pydantic AI Agent configured for Scout with BoardAnalysis response model

    Raises:
        ValueError: If provider/model not found or API key missing
    """
    config = get_llm_config()

    # Determine provider
    if not provider:
        # Try providers in order: openai, anthropic, gemini
        for p in ["openai", "anthropic", "gemini"]:
            try:
                models = config.get_supported_models(p)
                if models:
                    provider = p
                    break
            except ValueError:
                continue

        if not provider:
            raise ValueError("No LLM provider configured. Check config/config.json")

    # Determine model
    if not model:
        models = config.get_supported_models(provider)
        if not models:
            raise ValueError(f"No models configured for provider: {provider}")
        # Get first model from set
        model_list = list(models)
        if not model_list:
            raise ValueError(f"No models configured for provider: {provider}")
        model = model_list[0]

    # Get Pydantic AI model instance
    pydantic_model = _get_pydantic_ai_model(provider, model)

    # Create agent with BoardAnalysis as output type
    agent = Agent(
        model=pydantic_model,
        output_type=BoardAnalysis,
        system_prompt=(
            "You are a Tic-Tac-Toe board analysis agent. Analyze the game board state "
            "and identify threats (opponent two-in-a-row), opportunities (AI two-in-a-row), "
            "strategic positions (center, corners, edges), game phase (opening, midgame, endgame), "
            "and provide a board evaluation score (-1.0 to 1.0). Return a structured BoardAnalysis."
        ),
    )

    return agent


def create_strategist_agent(
    provider: str | None = None, model: str | None = None
) -> Agent[None, Strategy]:
    """Create Pydantic AI Agent for Strategist with Strategy response model.

    Args:
        provider: LLM provider name (openai, anthropic, gemini). If None, uses first available.
        model: Model name. If None, uses first model from config for the provider.

    Returns:
        Pydantic AI Agent configured for Strategist with Strategy response model

    Raises:
        ValueError: If provider/model not found or API key missing
    """
    config = get_llm_config()

    # Determine provider
    if not provider:
        # Try providers in order: openai, anthropic, gemini
        for p in ["openai", "anthropic", "gemini"]:
            try:
                models = config.get_supported_models(p)
                if models:
                    provider = p
                    break
            except ValueError:
                continue

        if not provider:
            raise ValueError("No LLM provider configured. Check config/config.json")

    # Determine model
    if not model:
        models = config.get_supported_models(provider)
        if not models:
            raise ValueError(f"No models configured for provider: {provider}")
        # Get first model from set
        model_list = list(models)
        if not model_list:
            raise ValueError(f"No models configured for provider: {provider}")
        model = model_list[0]

    # Get Pydantic AI model instance
    pydantic_model = _get_pydantic_ai_model(provider, model)

    # Create agent with Strategy as output type
    agent = Agent(
        model=pydantic_model,
        output_type=Strategy,
        system_prompt=(
            "You are a Tic-Tac-Toe strategy agent. Given a board analysis, "
            "recommend the best move with a primary move (highest priority), "
            "alternative moves sorted by priority, a game plan, and risk assessment. "
            "Return a structured Strategy with MoveRecommendation objects."
        ),
    )

    return agent
