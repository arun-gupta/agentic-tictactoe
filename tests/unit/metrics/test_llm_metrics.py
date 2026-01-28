"""Unit tests for LLM metrics tracking.

Tests cover Phase 5.3 subsection requirements:
- Track LLM calls with all metadata fields
- Retrieve calls filtered by agent
- Generate aggregated game session metadata
- Store and export metrics for post-game analysis

Spec Reference: Section 12.1 - LLM Provider Metadata and Experimentation Tracking
"""

import re
from datetime import datetime

import pytest

from src.metrics.llm_metrics import GameSessionMetadata, LLMCall, LLMMetrics


class TestLLMMetricsTrackCall:
    """Test LLMMetrics.track_call() method - records LLM calls with metadata."""

    def test_track_call_records_all_metadata_fields(self) -> None:
        """LLMMetrics.track_call() records LLM call with all required metadata fields.

        Given: An LLMMetrics instance
        When: track_call() is called with complete metadata
        Then: A new LLMCall is recorded with all fields (agent_name, prompt, response,
              tokens_used, latency_ms, model, provider, timestamp)
        """
        metrics = LLMMetrics()

        metrics.track_call(
            agent_name="Scout",
            prompt="Analyze this board",
            response="Board shows opening phase",
            tokens_used=150,
            latency_ms=1200.5,
            model="gpt-4o-mini",
            provider="openai",
        )

        session = metrics.get_game_session_metadata()
        assert len(session.calls) == 1
        call = session.calls[0]
        assert call.agent_name == "Scout"
        assert call.prompt == "Analyze this board"
        assert call.response == "Board shows opening phase"
        assert call.tokens_used == 150
        assert call.latency_ms == 1200.5
        assert call.model == "gpt-4o-mini"
        assert call.provider == "openai"
        # Verify timestamp is ISO 8601 format with timezone
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+\d{2}:\d{2}", call.timestamp)

    def test_track_call_accepts_strategist_agent(self) -> None:
        """LLMMetrics.track_call() accepts Strategist as agent_name.

        Given: An LLMMetrics instance
        When: track_call() is called with agent_name="Strategist"
        Then: The call is recorded with agent_name="Strategist"
        """
        metrics = LLMMetrics()

        metrics.track_call(
            agent_name="Strategist",
            prompt="Plan next move",
            response="Take center position",
            tokens_used=200,
            latency_ms=1500.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )

        strategist_calls = metrics.get_agent_calls("Strategist")
        assert len(strategist_calls) == 1
        assert strategist_calls[0].agent_name == "Strategist"

    def test_track_call_maintains_chronological_order(self) -> None:
        """LLMMetrics.track_call() maintains chronological order of calls.

        Given: An LLMMetrics instance
        When: Multiple calls are tracked in sequence
        Then: Calls are stored in chronological order (timestamp increases)
        """
        metrics = LLMMetrics()

        # Track three calls with small delays
        metrics.track_call(
            agent_name="Scout",
            prompt="First call",
            response="Response 1",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Second call",
            response="Response 2",
            tokens_used=200,
            latency_ms=1100.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )
        metrics.track_call(
            agent_name="Scout",
            prompt="Third call",
            response="Response 3",
            tokens_used=150,
            latency_ms=1050.0,
            model="gemini-3-flash-preview",
            provider="gemini",
        )

        session = metrics.get_game_session_metadata()
        assert len(session.calls) == 3

        # Verify chronological order by parsing timestamps
        timestamps = [datetime.fromisoformat(call.timestamp) for call in session.calls]
        assert timestamps[0] <= timestamps[1] <= timestamps[2]


class TestLLMMetricsGetAgentCalls:
    """Test LLMMetrics.get_agent_calls() method - retrieve calls by agent."""

    def test_get_agent_calls_returns_scout_calls_only(self) -> None:
        """LLMMetrics.get_agent_calls('Scout') returns only Scout agent calls.

        Given: LLMMetrics with calls from both Scout and Strategist
        When: get_agent_calls('Scout') is called
        Then: Only Scout calls are returned
        """
        metrics = LLMMetrics()
        metrics.track_call(
            agent_name="Scout",
            prompt="Scout call 1",
            response="Response 1",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Strategist call",
            response="Response 2",
            tokens_used=200,
            latency_ms=1500.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )
        metrics.track_call(
            agent_name="Scout",
            prompt="Scout call 2",
            response="Response 3",
            tokens_used=150,
            latency_ms=1200.0,
            model="gpt-4o-mini",
            provider="openai",
        )

        scout_calls = metrics.get_agent_calls("Scout")
        assert len(scout_calls) == 2
        assert all(call.agent_name == "Scout" for call in scout_calls)
        assert scout_calls[0].prompt == "Scout call 1"
        assert scout_calls[1].prompt == "Scout call 2"

    def test_get_agent_calls_returns_strategist_calls_only(self) -> None:
        """LLMMetrics.get_agent_calls('Strategist') returns only Strategist agent calls.

        Given: LLMMetrics with calls from both Scout and Strategist
        When: get_agent_calls('Strategist') is called
        Then: Only Strategist calls are returned
        """
        metrics = LLMMetrics()
        metrics.track_call(
            agent_name="Scout",
            prompt="Scout call",
            response="Response 1",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Strategist call 1",
            response="Response 2",
            tokens_used=200,
            latency_ms=1500.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Strategist call 2",
            response="Response 3",
            tokens_used=250,
            latency_ms=1600.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )

        strategist_calls = metrics.get_agent_calls("Strategist")
        assert len(strategist_calls) == 2
        assert all(call.agent_name == "Strategist" for call in strategist_calls)
        assert strategist_calls[0].prompt == "Strategist call 1"
        assert strategist_calls[1].prompt == "Strategist call 2"

    def test_get_agent_calls_returns_empty_list_when_no_calls(self) -> None:
        """LLMMetrics.get_agent_calls() returns empty list when no calls exist.

        Given: An empty LLMMetrics instance
        When: get_agent_calls() is called
        Then: An empty list is returned
        """
        metrics = LLMMetrics()
        scout_calls = metrics.get_agent_calls("Scout")
        assert scout_calls == []
        strategist_calls = metrics.get_agent_calls("Strategist")
        assert strategist_calls == []


class TestLLMMetricsGameSessionMetadata:
    """Test LLMMetrics.get_game_session_metadata() - aggregated metrics."""

    def test_get_game_session_metadata_returns_aggregated_metrics(self) -> None:
        """LLMMetrics.get_game_session_metadata() returns aggregated metrics for session.

        Given: LLMMetrics with multiple tracked calls
        When: get_game_session_metadata() is called
        Then: Returns GameSessionMetadata with correct aggregated values:
              - total_tokens (sum)
              - total_latency_ms (sum)
              - total_calls (count)
              - scout_calls (count)
              - strategist_calls (count)
        """
        metrics = LLMMetrics()
        metrics.track_call(
            agent_name="Scout",
            prompt="Call 1",
            response="Response 1",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Call 2",
            response="Response 2",
            tokens_used=200,
            latency_ms=1500.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )
        metrics.track_call(
            agent_name="Scout",
            prompt="Call 3",
            response="Response 3",
            tokens_used=150,
            latency_ms=1200.0,
            model="gemini-3-flash-preview",
            provider="gemini",
        )

        session = metrics.get_game_session_metadata()
        assert isinstance(session, GameSessionMetadata)
        assert session.total_tokens == 450  # 100 + 200 + 150
        assert session.total_latency_ms == 3700.0  # 1000 + 1500 + 1200
        assert session.total_calls == 3
        assert session.scout_calls == 2
        assert session.strategist_calls == 1

    def test_get_game_session_metadata_includes_all_calls(self) -> None:
        """LLMMetrics.get_game_session_metadata() includes all LLMCall records.

        Given: LLMMetrics with tracked calls
        When: get_game_session_metadata() is called
        Then: The returned metadata includes all LLMCall records in the 'calls' field
        """
        metrics = LLMMetrics()
        metrics.track_call(
            agent_name="Scout",
            prompt="Call 1",
            response="Response 1",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Call 2",
            response="Response 2",
            tokens_used=200,
            latency_ms=1500.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )

        session = metrics.get_game_session_metadata()
        assert len(session.calls) == 2
        assert all(isinstance(call, LLMCall) for call in session.calls)


class TestLLMMetricsExportFormat:
    """Test LLMMetrics export format - all required fields present."""

    def test_llm_call_export_format_includes_all_required_fields(self) -> None:
        """LLMMetrics export format includes all required fields per spec.

        Given: An LLMCall instance
        When: The call is exported (via model_dump())
        Then: All required fields are present:
              - timestamp
              - agent_name
              - prompt
              - response
              - tokens_used
              - latency_ms
              - model
              - provider
        """
        metrics = LLMMetrics()
        metrics.track_call(
            agent_name="Scout",
            prompt="Test prompt",
            response="Test response",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )

        session = metrics.get_game_session_metadata()
        call_dict = session.calls[0].model_dump()

        # Verify all required fields are present
        required_fields = [
            "timestamp",
            "agent_name",
            "prompt",
            "response",
            "tokens_used",
            "latency_ms",
            "model",
            "provider",
        ]
        for field in required_fields:
            assert field in call_dict, f"Missing required field: {field}"

    def test_game_session_metadata_export_format(self) -> None:
        """GameSessionMetadata export format includes all aggregated metrics.

        Given: A GameSessionMetadata instance with tracked calls
        When: The metadata is exported (via model_dump())
        Then: All aggregated fields are present:
              - total_tokens
              - total_latency_ms
              - total_calls
              - scout_calls
              - strategist_calls
              - calls (list of LLMCall objects)
        """
        metrics = LLMMetrics()
        metrics.track_call(
            agent_name="Scout",
            prompt="Test",
            response="Response",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )

        session = metrics.get_game_session_metadata()
        session_dict = session.model_dump()

        # Verify all aggregated fields are present
        required_fields = [
            "total_tokens",
            "total_latency_ms",
            "total_calls",
            "scout_calls",
            "strategist_calls",
            "calls",
        ]
        for field in required_fields:
            assert field in session_dict, f"Missing required field: {field}"


class TestLLMMetricsPostGameAnalysis:
    """Test LLMMetrics enables post-game analysis."""

    def test_metrics_enable_post_game_analysis(self) -> None:
        """LLMMetrics enables post-game analysis (data available after game ends).

        Given: A completed game session with tracked LLM calls
        When: get_game_session_metadata() is called after game ends
        Then: All metrics are available for post-game analysis:
              - Individual call details (prompts, responses, tokens, latency)
              - Aggregated session metrics (totals, per-agent counts)
              - Data can be exported for further analysis
        """
        metrics = LLMMetrics()

        # Simulate a game session with multiple agent calls
        metrics.track_call(
            agent_name="Scout",
            prompt="Analyze opening board",
            response="Center is available",
            tokens_used=120,
            latency_ms=1100.0,
            model="gpt-4o-mini",
            provider="openai",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Plan first move",
            response="Take center for control",
            tokens_used=180,
            latency_ms=1400.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )
        metrics.track_call(
            agent_name="Scout",
            prompt="Analyze midgame",
            response="Opponent threatens row 0",
            tokens_used=150,
            latency_ms=1250.0,
            model="gpt-4o-mini",
            provider="openai",
        )
        metrics.track_call(
            agent_name="Strategist",
            prompt="Plan defensive move",
            response="Block opponent threat",
            tokens_used=160,
            latency_ms=1300.0,
            model="claude-haiku-4-5",
            provider="anthropic",
        )

        # Get session metadata for post-game analysis
        session = metrics.get_game_session_metadata()

        # Verify all data is available
        assert session.total_tokens == 610
        assert session.total_latency_ms == 5050.0
        assert session.total_calls == 4
        assert session.scout_calls == 2
        assert session.strategist_calls == 2
        assert len(session.calls) == 4

        # Verify individual call details are preserved for analysis
        assert session.calls[0].prompt == "Analyze opening board"
        assert session.calls[1].prompt == "Plan first move"
        assert session.calls[2].prompt == "Analyze midgame"
        assert session.calls[3].prompt == "Plan defensive move"

        # Verify data can be exported (converted to dict for JSON serialization)
        session_dict = session.model_dump()
        assert isinstance(session_dict, dict)
        assert "total_tokens" in session_dict
        assert "calls" in session_dict
        assert isinstance(session_dict["calls"], list)

    def test_metrics_reset_clears_session_data(self) -> None:
        """LLMMetrics.reset() clears all session data for new game.

        Given: LLMMetrics with tracked calls from previous game
        When: reset() is called
        Then: All metrics are cleared and ready for a new game session
        """
        metrics = LLMMetrics()

        # Track calls for first game
        metrics.track_call(
            agent_name="Scout",
            prompt="Game 1 call",
            response="Response",
            tokens_used=100,
            latency_ms=1000.0,
            model="gpt-4o-mini",
            provider="openai",
        )

        # Reset for new game
        metrics.reset()

        # Verify all metrics are cleared
        session = metrics.get_game_session_metadata()
        assert session.total_tokens == 0
        assert session.total_latency_ms == 0.0
        assert session.total_calls == 0
        assert session.scout_calls == 0
        assert session.strategist_calls == 0
        assert len(session.calls) == 0


class TestLLMMetricsValidation:
    """Test LLMMetrics validation and error handling."""

    def test_llm_call_validates_negative_tokens(self) -> None:
        """LLMCall validates tokens_used >= 0.

        Given: An attempt to create LLMCall with negative tokens
        When: LLMCall is instantiated
        Then: Validation error is raised
        """
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            LLMCall(
                timestamp="2025-01-28T10:00:00+00:00",
                agent_name="Scout",
                prompt="Test",
                response="Response",
                tokens_used=-10,
                latency_ms=1000.0,
                model="gpt-4o-mini",
                provider="openai",
            )

    def test_llm_call_validates_negative_latency(self) -> None:
        """LLMCall validates latency_ms >= 0.0.

        Given: An attempt to create LLMCall with negative latency
        When: LLMCall is instantiated
        Then: Validation error is raised
        """
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            LLMCall(
                timestamp="2025-01-28T10:00:00+00:00",
                agent_name="Scout",
                prompt="Test",
                response="Response",
                tokens_used=100,
                latency_ms=-500.0,
                model="gpt-4o-mini",
                provider="openai",
            )

    def test_game_session_metadata_validates_negative_values(self) -> None:
        """GameSessionMetadata validates all numeric fields >= 0.

        Given: An attempt to create GameSessionMetadata with negative values
        When: GameSessionMetadata is instantiated
        Then: Validation error is raised
        """
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            GameSessionMetadata(
                total_tokens=-100,
                total_latency_ms=1000.0,
                total_calls=1,
                scout_calls=1,
                strategist_calls=0,
            )
