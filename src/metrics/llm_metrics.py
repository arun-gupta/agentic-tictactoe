"""LLM metrics tracking module.

This module provides functionality to track LLM API calls, including prompts,
responses, token usage, latency, and provider metadata. Metrics are stored
per agent and aggregated per game session for post-game analysis.

Spec Reference: Section 12.1 - LLM Provider Metadata and Experimentation Tracking
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

AgentName = Literal["Scout", "Strategist"]


class LLMCall(BaseModel):
    """Represents a single LLM API call with metadata.

    Attributes:
        timestamp: ISO 8601 timestamp of when the call was made
        agent_name: Name of the agent making the call ('Scout' or 'Strategist')
        prompt: The input prompt sent to the LLM
        response: The text response from the LLM
        tokens_used: Total tokens used (input + output)
        latency_ms: Response latency in milliseconds
        model: The model name used (e.g., 'gpt-4o-mini', 'claude-haiku-4-5')
        provider: The provider name ('openai', 'anthropic', or 'gemini')
    """

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    agent_name: AgentName = Field(..., description="Agent making the call")
    prompt: str = Field(..., description="Input prompt")
    response: str = Field(..., description="LLM response text")
    tokens_used: int = Field(..., ge=0, description="Total tokens (input + output)")
    latency_ms: float = Field(..., ge=0.0, description="Response latency in milliseconds")
    model: str = Field(..., description="Model name")
    provider: str = Field(..., description="Provider name (openai, anthropic, gemini)")


class GameSessionMetadata(BaseModel):
    """Aggregated metrics for a game session.

    Attributes:
        total_tokens: Sum of tokens across all LLM calls in the session
        total_latency_ms: Sum of latency across all LLM calls in the session
        total_calls: Total number of LLM calls made in the session
        scout_calls: Number of calls made by Scout agent
        strategist_calls: Number of calls made by Strategist agent
        calls: List of all LLMCall records in chronological order
    """

    total_tokens: int = Field(default=0, ge=0, description="Total tokens used")
    total_latency_ms: float = Field(default=0.0, ge=0.0, description="Total latency")
    total_calls: int = Field(default=0, ge=0, description="Total number of calls")
    scout_calls: int = Field(default=0, ge=0, description="Scout agent call count")
    strategist_calls: int = Field(default=0, ge=0, description="Strategist agent call count")
    calls: list[LLMCall] = Field(default_factory=list, description="All LLM calls")


class LLMMetrics:
    """Tracks LLM API calls and provides aggregated metrics for game sessions.

    This class maintains a collection of LLM calls and provides methods to:
    - Track new LLM calls with full metadata
    - Retrieve calls filtered by agent name
    - Get aggregated metrics for the current game session
    - Export data for post-game analysis

    Usage:
        metrics = LLMMetrics()
        metrics.track_call(
            agent_name="Scout",
            prompt="Analyze this board...",
            response="The board shows...",
            tokens_used=150,
            latency_ms=1200,
            model="gpt-4o-mini",
            provider="openai"
        )
        session_data = metrics.get_game_session_metadata()
    """

    def __init__(self) -> None:
        """Initialize an empty metrics tracker."""
        self._calls: list[LLMCall] = []

    def track_call(
        self,
        agent_name: AgentName,
        prompt: str,
        response: str,
        tokens_used: int,
        latency_ms: float,
        model: str,
        provider: str,
    ) -> None:
        """Record a new LLM API call with metadata.

        Args:
            agent_name: Name of the agent making the call ('Scout' or 'Strategist')
            prompt: The input prompt sent to the LLM
            response: The text response from the LLM
            tokens_used: Total tokens used (input + output)
            latency_ms: Response latency in milliseconds
            model: The model name (e.g., 'gpt-4o-mini', 'claude-haiku-4-5')
            provider: The provider name ('openai', 'anthropic', or 'gemini')
        """
        timestamp = datetime.now(UTC).isoformat()
        call = LLMCall(
            timestamp=timestamp,
            agent_name=agent_name,
            prompt=prompt,
            response=response,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            model=model,
            provider=provider,
        )
        self._calls.append(call)

    def get_agent_calls(self, agent_name: AgentName) -> list[LLMCall]:
        """Get all LLM calls for a specific agent.

        Args:
            agent_name: Name of the agent ('Scout' or 'Strategist')

        Returns:
            List of LLMCall objects for the specified agent, in chronological order
        """
        return [call for call in self._calls if call.agent_name == agent_name]

    def get_game_session_metadata(self) -> GameSessionMetadata:
        """Get aggregated metrics for the current game session.

        Returns:
            GameSessionMetadata containing:
            - total_tokens: Sum of tokens across all calls
            - total_latency_ms: Sum of latency across all calls
            - total_calls: Total number of LLM calls
            - scout_calls: Number of Scout agent calls
            - strategist_calls: Number of Strategist agent calls
            - calls: List of all LLMCall records
        """
        total_tokens = sum(call.tokens_used for call in self._calls)
        total_latency_ms = sum(call.latency_ms for call in self._calls)
        total_calls = len(self._calls)
        scout_calls = len([c for c in self._calls if c.agent_name == "Scout"])
        strategist_calls = len([c for c in self._calls if c.agent_name == "Strategist"])

        return GameSessionMetadata(
            total_tokens=total_tokens,
            total_latency_ms=total_latency_ms,
            total_calls=total_calls,
            scout_calls=scout_calls,
            strategist_calls=strategist_calls,
            calls=self._calls.copy(),  # Return a copy to prevent external modification
        )

    def reset(self) -> None:
        """Reset all metrics (clear all tracked calls).

        This should be called at the start of a new game session.
        """
        self._calls.clear()
