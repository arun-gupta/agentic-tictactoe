"""Tests for Scout Agent LLM Enhancement - Subsection 5.1.1.

Subsection tests for Phase 5.1.1: Scout LLM Enhancement (Pydantic AI)
These tests verify:
1. ScoutAgent.analyze() calls Pydantic AI Agent when LLM enabled
2. ScoutAgent.analyze() prompts LLM with board state and game context
3. ScoutAgent.analyze() receives BoardAnalysis from Pydantic AI structured output
4. ScoutAgent.analyze() falls back to rule-based analysis on LLM timeout (>5s)
5. ScoutAgent.analyze() falls back to rule-based analysis on LLM parse error
6. ScoutAgent.analyze() falls back to rule-based analysis on LLM authentication error
7. ScoutAgent.analyze() retries LLM call on timeout (3 retries with exponential backoff)
8. ScoutAgent.analyze() logs LLM call metadata (prompt, response, tokens, latency, model)
"""

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.run import AgentRunResult

from src.agents.scout import ScoutAgent
from src.domain.agent_models import BoardAnalysis
from src.domain.models import Board, GameState


class TestScoutLLMIntegration:
    """Test Scout agent LLM integration with Pydantic AI."""

    def test_subsection_5_1_1_1_calls_pydantic_ai_when_llm_enabled(self) -> None:
        """Subsection test 1: ScoutAgent.analyze() calls Pydantic AI Agent when LLM enabled."""
        # Create mock LLM agent
        mock_llm_agent = MagicMock()
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        # Patch the create_scout_agent to return our mock
        with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True)

            board = Board()
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

            result = scout.analyze(game_state)

            # Verify LLM agent was called
            assert mock_llm_agent.run.called
            assert result.success
            assert result.data is not None

    def test_subsection_5_1_1_2_prompts_llm_with_board_state_and_context(self) -> None:
        """Subsection test 2: ScoutAgent.analyze() prompts LLM with board state and game context."""
        # Create mock LLM agent
        mock_llm_agent = MagicMock()
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True)

            board = Board(
                cells=[
                    ["X", "O", "EMPTY"],
                    ["EMPTY", "EMPTY", "EMPTY"],
                    ["EMPTY", "EMPTY", "EMPTY"],
                ]
            )
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

            result = scout.analyze(game_state)

            # Verify LLM was called with a prompt
            assert mock_llm_agent.run.called
            call_args = mock_llm_agent.run.call_args[0]
            prompt = call_args[0]

            # Verify prompt contains board state and context
            assert "X O ." in prompt or "X O" in prompt  # Board state
            assert "AI Symbol: O" in prompt  # AI symbol
            assert "Opponent Symbol: X" in prompt  # Opponent symbol
            assert "Move Count: 2" in prompt  # Move count
            assert result.success

    def test_subsection_5_1_1_3_receives_board_analysis_from_pydantic_ai(self) -> None:
        """Subsection test 3: ScoutAgent.analyze() receives BoardAnalysis from Pydantic AI structured output."""
        # Create mock LLM agent with structured BoardAnalysis response
        mock_llm_agent = MagicMock()
        expected_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.5,
        )
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = expected_analysis
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True)

            board = Board()
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=4)

            result = scout.analyze(game_state)

            # Verify we got the BoardAnalysis from Pydantic AI
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, BoardAnalysis)
            assert result.data.game_phase == "midgame"
            assert result.data.board_evaluation_score == 0.5

    def test_subsection_5_1_1_4_fallback_on_timeout(self) -> None:
        """Subsection test 4: ScoutAgent.analyze() falls back to rule-based analysis on LLM timeout (>5s)."""
        # Create mock LLM agent that times out
        mock_llm_agent = MagicMock()
        mock_llm_agent.run = AsyncMock(side_effect=TimeoutError())

        with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True, timeout_seconds=0.1, max_retries=1)

            board = Board()
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

            result = scout.analyze(game_state)

            # Should fall back to rule-based and still succeed
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, BoardAnalysis)
            # Verify it's rule-based result by checking for strategic moves on empty board
            assert len(result.data.strategic_moves) == 9  # Rule-based returns all positions

    def test_subsection_5_1_1_5_fallback_on_parse_error(self) -> None:
        """Subsection test 5: ScoutAgent.analyze() falls back to rule-based analysis on LLM parse error."""
        # Create mock LLM agent that raises parse error
        mock_llm_agent = MagicMock()
        mock_llm_agent.run = AsyncMock(side_effect=UnexpectedModelBehavior("Parse error"))

        with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True)

            board = Board()
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

            result = scout.analyze(game_state)

            # Should fall back to rule-based and still succeed
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, BoardAnalysis)
            # Verify it's rule-based result
            assert len(result.data.strategic_moves) == 9

    def test_subsection_5_1_1_6_fallback_on_authentication_error(self) -> None:
        """Subsection test 6: ScoutAgent.analyze() falls back to rule-based analysis on LLM authentication error."""
        # Create mock LLM agent that raises authentication error
        mock_llm_agent = MagicMock()
        mock_llm_agent.run = AsyncMock(side_effect=Exception("Authentication failed"))

        with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True)

            board = Board()
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

            result = scout.analyze(game_state)

            # Should fall back to rule-based and still succeed
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, BoardAnalysis)
            # Verify it's rule-based result
            assert len(result.data.strategic_moves) == 9

    def test_subsection_5_1_1_7_retries_on_timeout_with_exponential_backoff(self) -> None:
        """Subsection test 7: ScoutAgent.analyze() retries LLM call on timeout (3 retries with exponential backoff)."""
        # Create mock LLM agent that times out multiple times
        mock_llm_agent = MagicMock()
        call_count = 0

        async def mock_run_with_retries(*args: Any, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError()
            # Success on 3rd retry
            mock_result = MagicMock(spec=AgentRunResult)
            mock_result.data = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="opening",
                board_evaluation_score=0.0,
            )
            return mock_result

        mock_llm_agent.run = AsyncMock(side_effect=mock_run_with_retries)

        with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True, timeout_seconds=0.1, max_retries=3)

            board = Board()
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

            start_time = time.time()
            result = scout.analyze(game_state)
            elapsed_time = time.time() - start_time

            # Verify retries happened (should have called run 3 times)
            assert mock_llm_agent.run.call_count == 3
            assert result.success
            # Verify exponential backoff happened (at least 3 seconds: 1s + 2s)
            assert elapsed_time >= 3.0

    def test_subsection_5_1_1_8_logs_llm_call_metadata(self, caplog: Any) -> None:
        """Subsection test 8: ScoutAgent.analyze() logs LLM call metadata (prompt, response, tokens, latency, model)."""
        # Create mock LLM agent
        mock_llm_agent = MagicMock()
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        with caplog.at_level("INFO"):
            with patch("src.agents.scout.create_scout_agent", return_value=mock_llm_agent):
                scout = ScoutAgent(ai_symbol="O", llm_enabled=True)

                board = Board()
                game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

                result = scout.analyze(game_state)

            # Verify logging happened
            assert result.success
            # Check for log messages containing metadata
            log_messages = [record.message for record in caplog.records]
            # Should have metadata log (most important for this test)
            assert any("Scout LLM call metadata" in msg for msg in log_messages)
            # Should have completion log
            assert any("Scout LLM analysis completed" in msg for msg in log_messages)
            # Verify metadata contains expected fields
            metadata_msgs = [msg for msg in log_messages if "Scout LLM call metadata" in msg]
            assert len(metadata_msgs) > 0
            # Check that metadata log contains attempt, latency, and prompt_length
            assert any("attempt=" in msg for msg in metadata_msgs)
            assert any("latency=" in msg for msg in metadata_msgs)
            assert any("prompt_length=" in msg for msg in metadata_msgs)


class TestScoutLLMDisabled:
    """Test Scout agent with LLM disabled (backward compatibility)."""

    def test_llm_disabled_uses_rule_based(self) -> None:
        """When LLM is disabled, should use rule-based analysis."""
        scout = ScoutAgent(ai_symbol="O", llm_enabled=False)

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = scout.analyze(game_state)

        # Should succeed with rule-based
        assert result.success
        assert result.data is not None
        assert isinstance(result.data, BoardAnalysis)
        # Rule-based on empty board returns all 9 strategic positions
        assert len(result.data.strategic_moves) == 9

    def test_default_llm_disabled(self) -> None:
        """By default, LLM should be disabled for backward compatibility."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = scout.analyze(game_state)

        # Should succeed with rule-based (default behavior)
        assert result.success
        assert result.data is not None
        assert len(result.data.strategic_moves) == 9


class TestScoutLLMInitializationFailure:
    """Test Scout agent LLM initialization failure handling."""

    def test_initialization_failure_falls_back_to_rule_based(self) -> None:
        """When LLM initialization fails, should fall back to rule-based."""
        # Mock create_scout_agent to raise an error
        with patch("src.agents.scout.create_scout_agent", side_effect=ValueError("No API key")):
            scout = ScoutAgent(ai_symbol="O", llm_enabled=True)

            # Should have fallen back to disabled mode
            assert not scout.llm_enabled
            assert scout._llm_agent is None

            board = Board()
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

            result = scout.analyze(game_state)

            # Should still work with rule-based
            assert result.success
            assert result.data is not None
