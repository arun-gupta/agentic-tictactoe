"""Tests for Strategist Agent LLM Enhancement - Subsection 5.1.2.

Subsection tests for Phase 5.1.2: Strategist LLM Enhancement (Pydantic AI)
These tests verify:
1. StrategistAgent.plan() calls Pydantic AI Agent when LLM enabled
2. StrategistAgent.plan() prompts LLM with BoardAnalysis and game context
3. StrategistAgent.plan() receives Strategy from Pydantic AI structured output
4. StrategistAgent.plan() falls back to priority-based selection on LLM timeout (>5s)
5. StrategistAgent.plan() falls back to priority-based selection on LLM parse error
6. StrategistAgent.plan() falls back to priority-based selection on LLM authentication error
7. StrategistAgent.plan() retries LLM call on timeout (3 retries with exponential backoff)
8. StrategistAgent.plan() logs LLM call metadata (prompt, response, tokens, latency, model)
"""

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.run import AgentRunResult

from src.agents.strategist import StrategistAgent
from src.domain.agent_models import BoardAnalysis, MovePriority, MoveRecommendation, Strategy
from src.domain.models import Position


class TestStrategistLLMIntegration:
    """Test Strategist agent LLM integration with Pydantic AI."""

    def test_subsection_5_1_2_1_calls_pydantic_ai_when_llm_enabled(self) -> None:
        """Subsection test 1: StrategistAgent.plan() calls Pydantic AI Agent when LLM enabled."""
        # Create mock LLM agent
        mock_llm_agent = MagicMock()
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = Strategy(
            primary_move=MoveRecommendation(
                position=Position(row=1, col=1),
                priority=MovePriority.CENTER_CONTROL,
                confidence=0.7,
                reasoning="Control center",
            ),
            alternatives=[],
            game_plan="Control center for strategic advantage",
            risk_assessment="low",
        )
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        # Patch the create_strategist_agent to return our mock
        with patch("src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent):
            strategist = StrategistAgent(ai_symbol="O", llm_enabled=True)

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="opening",
                board_evaluation_score=0.0,
            )

            result = strategist.plan(analysis)

            # Verify LLM agent was called
            assert mock_llm_agent.run.called
            assert result.success
            assert result.data is not None

    def test_subsection_5_1_2_2_prompts_llm_with_board_analysis_and_context(self) -> None:
        """Subsection test 2: StrategistAgent.plan() prompts LLM with BoardAnalysis and game context."""
        # Create mock LLM agent
        mock_llm_agent = MagicMock()
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = Strategy(
            primary_move=MoveRecommendation(
                position=Position(row=0, col=2),
                priority=MovePriority.BLOCK_THREAT,
                confidence=0.95,
                reasoning="Block threat",
            ),
            alternatives=[],
            game_plan="Block opponent threat",
            risk_assessment="high",
        )
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent):
            strategist = StrategistAgent(ai_symbol="O", llm_enabled=True)

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="midgame",
                board_evaluation_score=-0.3,
            )

            result = strategist.plan(analysis)

            # Verify LLM was called with a prompt
            assert mock_llm_agent.run.called
            call_args = mock_llm_agent.run.call_args[0]
            prompt = call_args[0]

            # Verify prompt contains board analysis and context
            assert "midgame" in prompt  # Game phase
            assert "-0.3" in prompt  # Board evaluation
            assert "AI Symbol: O" in prompt  # AI symbol
            assert result.success

    def test_subsection_5_1_2_3_receives_strategy_from_pydantic_ai(self) -> None:
        """Subsection test 3: StrategistAgent.plan() receives Strategy from Pydantic AI structured output."""
        # Create mock LLM agent with structured Strategy response
        mock_llm_agent = MagicMock()
        expected_strategy = Strategy(
            primary_move=MoveRecommendation(
                position=Position(row=1, col=1),
                priority=MovePriority.CENTER_CONTROL,
                confidence=0.7,
                reasoning="Control center",
            ),
            alternatives=[
                MoveRecommendation(
                    position=Position(row=0, col=0),
                    priority=MovePriority.CORNER_CONTROL,
                    confidence=0.6,
                    reasoning="Alternative corner",
                )
            ],
            game_plan="Control center position to maximize future opportunities",
            risk_assessment="medium",
        )
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = expected_strategy
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent):
            strategist = StrategistAgent(ai_symbol="O", llm_enabled=True)

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="midgame",
                board_evaluation_score=0.2,
            )

            result = strategist.plan(analysis)

            # Verify we got the Strategy from Pydantic AI
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, Strategy)
            assert result.data.primary_move.position == Position(row=1, col=1)
            assert result.data.risk_assessment == "medium"
            assert len(result.data.alternatives) == 1

    def test_subsection_5_1_2_4_fallback_on_timeout(self) -> None:
        """Subsection test 4: StrategistAgent.plan() falls back to priority-based selection on LLM timeout (>5s)."""
        # Create mock LLM agent that times out
        mock_llm_agent = MagicMock()
        mock_llm_agent.run = AsyncMock(side_effect=TimeoutError())

        with patch("src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent):
            strategist = StrategistAgent(
                ai_symbol="O", llm_enabled=True, timeout_seconds=0.1, max_retries=1
            )

            from src.domain.agent_models import StrategicMove

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[
                    StrategicMove(
                        position=Position(row=1, col=1),
                        move_type="center",
                        priority=10,
                        reasoning="Center position",
                    )
                ],
                game_phase="opening",
                board_evaluation_score=0.0,
            )

            result = strategist.plan(analysis)

            # Should fall back to priority-based and still succeed
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, Strategy)
            # Priority-based will select center for opening
            assert result.data.primary_move.priority == MovePriority.CENTER_CONTROL

    def test_subsection_5_1_2_5_fallback_on_parse_error(self) -> None:
        """Subsection test 5: StrategistAgent.plan() falls back to priority-based selection on LLM parse error."""
        # Create mock LLM agent that raises parse error
        mock_llm_agent = MagicMock()
        mock_llm_agent.run = AsyncMock(side_effect=UnexpectedModelBehavior("Parse error"))

        with patch("src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent):
            strategist = StrategistAgent(ai_symbol="O", llm_enabled=True)

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="opening",
                board_evaluation_score=0.0,
            )

            result = strategist.plan(analysis)

            # Should fall back to priority-based and still succeed
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, Strategy)

    def test_subsection_5_1_2_6_fallback_on_authentication_error(self) -> None:
        """Subsection test 6: StrategistAgent.plan() falls back to priority-based selection on LLM authentication error."""
        # Create mock LLM agent that raises authentication error
        mock_llm_agent = MagicMock()
        mock_llm_agent.run = AsyncMock(side_effect=Exception("Authentication failed"))

        with patch("src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent):
            strategist = StrategistAgent(ai_symbol="O", llm_enabled=True)

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="opening",
                board_evaluation_score=0.0,
            )

            result = strategist.plan(analysis)

            # Should fall back to priority-based and still succeed
            assert result.success
            assert result.data is not None
            assert isinstance(result.data, Strategy)

    def test_subsection_5_1_2_7_retries_on_timeout_with_exponential_backoff(self) -> None:
        """Subsection test 7: StrategistAgent.plan() retries LLM call on timeout (3 retries with exponential backoff)."""
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
            mock_result.data = Strategy(
                primary_move=MoveRecommendation(
                    position=Position(row=1, col=1),
                    priority=MovePriority.CENTER_CONTROL,
                    confidence=0.7,
                    reasoning="Control center",
                ),
                alternatives=[],
                game_plan="Control center",
                risk_assessment="low",
            )
            return mock_result

        mock_llm_agent.run = AsyncMock(side_effect=mock_run_with_retries)

        with patch("src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent):
            strategist = StrategistAgent(
                ai_symbol="O", llm_enabled=True, timeout_seconds=0.1, max_retries=3
            )

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="opening",
                board_evaluation_score=0.0,
            )

            start_time = time.time()
            result = strategist.plan(analysis)
            elapsed_time = time.time() - start_time

            # Verify retries happened (should have called run 3 times)
            assert mock_llm_agent.run.call_count == 3
            assert result.success
            # Verify exponential backoff happened (at least 3 seconds: 1s + 2s)
            assert elapsed_time >= 3.0

    def test_subsection_5_1_2_8_logs_llm_call_metadata(self, caplog: Any) -> None:
        """Subsection test 8: StrategistAgent.plan() logs LLM call metadata (prompt, response, tokens, latency, model)."""
        # Create mock LLM agent
        mock_llm_agent = MagicMock()
        mock_result = MagicMock(spec=AgentRunResult)
        mock_result.data = Strategy(
            primary_move=MoveRecommendation(
                position=Position(row=1, col=1),
                priority=MovePriority.CENTER_CONTROL,
                confidence=0.7,
                reasoning="Control center",
            ),
            alternatives=[],
            game_plan="Control center",
            risk_assessment="low",
        )
        mock_llm_agent.run = AsyncMock(return_value=mock_result)

        with caplog.at_level("INFO"):
            with patch(
                "src.agents.strategist.create_strategist_agent", return_value=mock_llm_agent
            ):
                strategist = StrategistAgent(ai_symbol="O", llm_enabled=True)

                analysis = BoardAnalysis(
                    threats=[],
                    opportunities=[],
                    strategic_moves=[],
                    game_phase="opening",
                    board_evaluation_score=0.0,
                )

                result = strategist.plan(analysis)

            # Verify logging happened
            assert result.success
            # Check for log messages containing metadata
            log_messages = [record.message for record in caplog.records]
            # Should have metadata log (most important for this test)
            assert any("Strategist LLM call metadata" in msg for msg in log_messages)
            # Should have completion log
            assert any("Strategist LLM planning completed" in msg for msg in log_messages)
            # Verify metadata contains expected fields
            metadata_msgs = [msg for msg in log_messages if "Strategist LLM call metadata" in msg]
            assert len(metadata_msgs) > 0
            # Check that metadata log contains attempt, latency, and prompt_length
            assert any("attempt=" in msg for msg in metadata_msgs)
            assert any("latency=" in msg for msg in metadata_msgs)
            assert any("prompt_length=" in msg for msg in metadata_msgs)


class TestStrategistLLMDisabled:
    """Test Strategist agent with LLM disabled (backward compatibility)."""

    def test_llm_disabled_uses_priority_based(self) -> None:
        """When LLM is disabled, should use priority-based strategy."""
        strategist = StrategistAgent(ai_symbol="O", llm_enabled=False)

        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )

        result = strategist.plan(analysis)

        # Should succeed with priority-based
        assert result.success
        assert result.data is not None
        assert isinstance(result.data, Strategy)

    def test_default_llm_disabled(self) -> None:
        """By default, LLM should be disabled for backward compatibility."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )

        result = strategist.plan(analysis)

        # Should succeed with priority-based (default behavior)
        assert result.success
        assert result.data is not None


class TestStrategistLLMInitializationFailure:
    """Test Strategist agent LLM initialization failure handling."""

    def test_initialization_failure_falls_back_to_priority_based(self) -> None:
        """When LLM initialization fails, should fall back to priority-based."""
        # Mock create_strategist_agent to raise an error
        with patch(
            "src.agents.strategist.create_strategist_agent", side_effect=ValueError("No API key")
        ):
            strategist = StrategistAgent(ai_symbol="O", llm_enabled=True)

            # Should have fallen back to disabled mode
            assert not strategist.llm_enabled
            assert strategist._llm_agent is None

            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="opening",
                board_evaluation_score=0.0,
            )

            result = strategist.plan(analysis)

            # Should still work with priority-based
            assert result.success
            assert result.data is not None
