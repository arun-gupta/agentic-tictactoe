"""Integration tests for Agent Pipeline Orchestration.

Tests the complete pipeline flow: Scout → Strategist → Executor
"""

import time

from src.agents.executor import ExecutorAgent
from src.agents.pipeline import AgentPipeline
from src.agents.scout import ScoutAgent
from src.agents.strategist import StrategistAgent
from src.domain.errors import E_LLM_TIMEOUT
from src.domain.models import Board, GameState, Position


# ==============================================================================
# SUBSECTION 3.3.1: Pipeline Coordinator
# ==============================================================================
class TestPipelineCoordinator:
    """Development tests for pipeline coordinator logic."""

    def test_subsection_3_3_1_orchestrates_agents_in_correct_order(self) -> None:
        """Subsection 3.3.1: Orchestrates Scout → Strategist → Executor in correct order."""
        pipeline = AgentPipeline(ai_symbol="O")

        # Create game state where it's AI's turn
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Execute pipeline
        result = pipeline.execute_pipeline(game_state)

        # Should succeed and return MoveExecution
        assert result.success
        assert result.data is not None
        assert result.data.position is not None
        assert result.data.success

    def test_subsection_3_3_1_passes_board_analysis_to_strategist(self) -> None:
        """Subsection 3.3.1: Passes BoardAnalysis from Scout to Strategist."""
        pipeline = AgentPipeline(ai_symbol="O")

        # Create game state with a threat (X has two in a row)
        # This should be detected by Scout and passed to Strategist
        # Need odd move_count for AI's turn
        board = Board(
            cells=[
                ["X", "X", "EMPTY"],  # Threat - X can win
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        # Execute pipeline
        result = pipeline.execute_pipeline(game_state)

        # Should succeed and block the threat
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.success
        # Should block at position (0,2)
        assert execution.position == Position(row=0, col=2)

    def test_subsection_3_3_1_passes_strategy_to_executor(self) -> None:
        """Subsection 3.3.1: Passes Strategy from Strategist to Executor."""
        pipeline = AgentPipeline(ai_symbol="O")

        # Create game state with an opportunity (O has two in a row)
        # Strategist should prioritize the win, Executor should execute it
        board = Board(
            cells=[
                ["O", "O", "EMPTY"],  # Opportunity - O can win
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        # Execute pipeline
        result = pipeline.execute_pipeline(game_state)

        # Should succeed and take the winning move
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.success
        # Should win at position (0,2)
        assert execution.position == Position(row=0, col=2)
        assert execution.actual_priority_used is not None

    def test_subsection_3_3_1_returns_move_execution_result(self) -> None:
        """Subsection 3.3.1: Returns final MoveExecution result."""
        pipeline = AgentPipeline(ai_symbol="O")

        # Create game state where it's AI's turn (odd move_count)
        # Player (X) has made first move
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Execute pipeline
        result = pipeline.execute_pipeline(game_state)

        # Should return AgentResult with MoveExecution
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.position is not None
        assert execution.execution_time_ms >= 0.0
        assert execution.reasoning is not None
        assert len(execution.reasoning) > 0

    def test_subsection_3_3_1_handles_agent_failures(self) -> None:
        """Subsection 3.3.1: Handles agent failures and returns error result."""
        pipeline = AgentPipeline(ai_symbol="O")

        # Create invalid game state that might cause issues
        # Use a game state that's already over - Scout should still work,
        # but Executor should fail validation, and fallback should detect game over
        board = Board(
            cells=[
                ["X", "X", "X"],  # X has won
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        # Execute pipeline - should detect game is over via fallback
        result = pipeline.execute_pipeline(game_state)

        # Should return result with fallback, but MoveExecution.success=False because game is over
        assert result.success  # Pipeline succeeded
        assert result.data is not None
        assert not result.data.success  # But MoveExecution indicates failure (game over)
        assert "game is already over" in result.data.reasoning.lower()


# ==============================================================================
# SUBSECTION 3.3.2: Timeout Configuration
# ==============================================================================
class TestTimeoutConfiguration:
    """Development tests for timeout configuration."""

    def test_subsection_3_3_2_enforces_scout_timeout(self) -> None:
        """Subsection 3.3.2: Enforces Scout timeout at 5 seconds."""

        # Create a slow Scout agent that sleeps for longer than timeout
        class SlowScoutAgent(ScoutAgent):
            def analyze(self, game_state):
                time.sleep(6)  # Sleep longer than 5s timeout
                return super().analyze(game_state)

        pipeline = AgentPipeline(ai_symbol="O", scout_timeout=0.5)  # Short timeout for testing
        # Replace scout with slow version
        pipeline.scout = SlowScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = pipeline.execute_pipeline(game_state)

        # With fallback implemented, Scout timeout triggers Fallback Rule Set 1
        # Pipeline should succeed with fallback, but metadata indicates timeout/fallback
        assert result.success  # Fallback allows pipeline to succeed
        assert result.data is not None
        assert result.data.success
        # Metadata should indicate fallback was used (due to timeout)
        assert result.metadata is not None
        assert "fallback_used" in result.metadata

    def test_subsection_3_3_2_enforces_strategist_timeout(self) -> None:
        """Subsection 3.3.2: Enforces Strategist timeout at 3 seconds."""

        # Create a slow Strategist agent that sleeps for longer than timeout
        class SlowStrategistAgent(StrategistAgent):
            def plan(self, analysis):
                time.sleep(4)  # Sleep longer than 3s timeout
                return super().plan(analysis)

        pipeline = AgentPipeline(ai_symbol="O", strategist_timeout=0.5)  # Short timeout for testing
        # Replace strategist with slow version
        pipeline.strategist = SlowStrategistAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = pipeline.execute_pipeline(game_state)

        # With fallback implemented, Strategist timeout triggers Fallback Rule Set 2
        # Pipeline should succeed with fallback
        assert result.success  # Fallback allows pipeline to succeed
        assert result.data is not None
        assert result.data.success
        # Metadata should indicate fallback was used (due to timeout)
        # Note: Executor may also use fallback, so metadata might show "strategist_primary"
        assert result.metadata is not None
        assert "fallback_used" in result.metadata

    def test_subsection_3_3_2_enforces_executor_timeout(self) -> None:
        """Subsection 3.3.2: Enforces Executor timeout at 2 seconds."""

        # Create a slow Executor agent that sleeps for longer than timeout
        class SlowExecutorAgent(ExecutorAgent):
            def execute(self, game_state, strategy):
                time.sleep(3)  # Sleep longer than 2s timeout
                return super().execute(game_state, strategy)

        pipeline = AgentPipeline(ai_symbol="O", executor_timeout=0.5)  # Short timeout for testing
        # Replace executor with slow version
        pipeline.executor = SlowExecutorAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = pipeline.execute_pipeline(game_state)

        # With fallback implemented, Executor timeout triggers Fallback Rule Set 3
        # Pipeline should succeed with fallback
        assert result.success  # Fallback allows pipeline to succeed
        assert result.data is not None
        assert result.data.success
        # Metadata should indicate fallback was used (due to timeout)
        assert result.metadata is not None
        assert result.metadata.get("fallback_used") == "strategist_primary"

    def test_subsection_3_3_2_enforces_total_pipeline_timeout(self) -> None:
        """Subsection 3.3.2: Enforces total pipeline timeout at 15 seconds."""

        # Create slow agents that would take longer than total timeout
        class SlowScoutAgent(ScoutAgent):
            def analyze(self, game_state):
                time.sleep(10)  # Sleep longer than total timeout
                return super().analyze(game_state)

        # Set total timeout shorter than scout_timeout to test total timeout enforcement
        pipeline = AgentPipeline(
            ai_symbol="O", scout_timeout=20.0, total_timeout=1.0
        )  # Short total timeout for testing
        # Replace scout with slow version
        pipeline.scout = SlowScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = pipeline.execute_pipeline(game_state)

        # Should timeout at total pipeline timeout (scout_timeout is 20s, but total_timeout is 1s)
        # The remaining_timeout calculation limits scout to 1s, which times out
        assert not result.success
        assert result.error_code == E_LLM_TIMEOUT
        # Error message should indicate total timeout was exceeded
        assert (
            "total timeout" in (result.error_message or "").lower()
            or "timeout" in (result.error_message or "").lower()
        )


# ==============================================================================
# SUBSECTION 3.3.3: Fallback Strategy
# ==============================================================================
class TestFallbackStrategy:
    """Development tests for fallback strategy implementation."""

    def test_subsection_3_3_3_scout_timeout_triggers_rule_based_fallback(self) -> None:
        """Subsection 3.3.3: Scout timeout triggers rule-based analysis fallback."""

        # Create a slow Scout agent that sleeps for longer than timeout
        class SlowScoutAgent(ScoutAgent):
            def analyze(self, game_state):
                time.sleep(6)  # Sleep longer than timeout
                return super().analyze(game_state)

        pipeline = AgentPipeline(ai_symbol="O", scout_timeout=0.1)  # Very short timeout
        pipeline.scout = SlowScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = pipeline.execute_pipeline(game_state)

        # Should succeed due to fallback rule-based analysis
        assert result.success
        assert result.data is not None
        assert result.data.success
        assert result.data.position is not None
        # Should have fallback metadata (may be overwritten by later fallbacks, but should contain fallback info)
        assert result.metadata is not None
        # Metadata should indicate a fallback was used (could be rule_based_analysis, scout_opportunity, or strategist_primary)
        assert "fallback_used" in result.metadata

    def test_subsection_3_3_3_strategist_timeout_triggers_priority_fallback(self) -> None:
        """Subsection 3.3.3: Strategist timeout triggers priority-based selection fallback."""

        # Create a slow Strategist agent
        class SlowStrategistAgent(StrategistAgent):
            def plan(self, analysis):
                time.sleep(4)  # Sleep longer than timeout
                return super().plan(analysis)

        pipeline = AgentPipeline(ai_symbol="O", strategist_timeout=0.1)  # Very short timeout
        pipeline.strategist = SlowStrategistAgent(ai_symbol="O")

        # Create game state with an opportunity (O can win)
        board = Board(
            cells=[
                ["O", "O", "EMPTY"],  # Opportunity - O can win
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        result = pipeline.execute_pipeline(game_state)

        # Should succeed due to fallback selecting from BoardAnalysis.opportunities
        assert result.success
        assert result.data is not None
        assert result.data.success
        assert result.data.position == Position(row=0, col=2)  # Should block/win at (0,2)
        assert result.metadata is not None
        assert result.metadata.get("fallback_used") == "scout_opportunity"

    def test_subsection_3_3_3_executor_timeout_triggers_random_valid_fallback(self) -> None:
        """Subsection 3.3.3: Executor timeout triggers random valid move fallback."""

        # Create a slow Executor agent
        class SlowExecutorAgent(ExecutorAgent):
            def execute(self, game_state, strategy):
                time.sleep(3)  # Sleep longer than timeout
                return super().execute(game_state, strategy)

        pipeline = AgentPipeline(ai_symbol="O", executor_timeout=0.1)  # Very short timeout
        pipeline.executor = SlowExecutorAgent(ai_symbol="O")

        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        result = pipeline.execute_pipeline(game_state)

        # Should succeed due to fallback using Strategy primary move or random valid move
        assert result.success
        assert result.data is not None
        assert result.data.success
        assert result.data.position is not None
        # Should be a valid empty position
        assert game_state.board.is_empty(result.data.position)
        assert result.metadata is not None
        assert result.metadata.get("fallback_used") == "strategist_primary"

    def test_subsection_3_3_3_pipeline_completes_within_15_seconds_with_timeouts(self) -> None:
        """Subsection 3.3.3: Pipeline completes within 15 seconds even with all timeouts."""

        # Create slow agents (but not too slow to avoid test timeout)
        # Note: Fallback Rule Set 1 calls scout.analyze() directly, so it will still be slow
        # In real scenario, fallback would use fast rule-based logic, but here we're testing
        # that timeouts work correctly
        class SlowStrategistAgent(StrategistAgent):
            def plan(self, analysis):
                time.sleep(2)  # Sleep longer than timeout
                return super().plan(analysis)

        class SlowExecutorAgent(ExecutorAgent):
            def execute(self, game_state, strategy):
                time.sleep(2)  # Sleep longer than timeout
                return super().execute(game_state, strategy)

        # Set short timeouts for Strategist and Executor only
        # Scout will complete normally, then Strategist and Executor will timeout and use fallbacks
        pipeline = AgentPipeline(
            ai_symbol="O",
            scout_timeout=5.0,  # Normal timeout for Scout
            strategist_timeout=0.1,  # Short timeout to trigger fallback
            executor_timeout=0.1,  # Short timeout to trigger fallback
            total_timeout=15.0,
        )
        pipeline.strategist = SlowStrategistAgent(ai_symbol="O")
        pipeline.executor = SlowExecutorAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = pipeline.execute_pipeline(game_state)

        # Should still produce a result using fallbacks
        assert result.success
        assert result.data is not None
        assert result.data.success
        # Should have fallback metadata indicating fallbacks were used
        assert result.metadata is not None
        assert "fallback_used" in result.metadata

    def test_subsection_3_3_3_fallback_produces_valid_move(self) -> None:
        """Subsection 3.3.3: Fallback strategy produces valid move."""

        # Create slow Executor to trigger fallback
        class SlowExecutorAgent(ExecutorAgent):
            def execute(self, game_state, strategy):
                time.sleep(3)
                return super().execute(game_state, strategy)

        pipeline = AgentPipeline(ai_symbol="O", executor_timeout=0.1)
        pipeline.executor = SlowExecutorAgent(ai_symbol="O")

        board = Board(
            cells=[
                ["X", "EMPTY", "O"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = pipeline.execute_pipeline(game_state)

        # Should produce a valid move
        assert result.success
        assert result.data is not None
        assert result.data.success
        position = result.data.position
        assert position is not None
        # Validate position is in bounds and cell is empty
        assert 0 <= position.row <= 2
        assert 0 <= position.col <= 2
        assert game_state.board.is_empty(position)

    def test_subsection_3_3_3_records_fallback_in_metadata(self) -> None:
        """Subsection 3.3.3: Records which fallback was used in result metadata."""

        # Trigger Strategist timeout to use Fallback Rule Set 2
        class SlowStrategistAgent(StrategistAgent):
            def plan(self, analysis):
                time.sleep(4)
                return super().plan(analysis)

        pipeline = AgentPipeline(ai_symbol="O", strategist_timeout=0.1)
        pipeline.strategist = SlowStrategistAgent(ai_symbol="O")

        board = Board(
            cells=[
                ["O", "O", "EMPTY"],  # Opportunity
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        result = pipeline.execute_pipeline(game_state)

        # Should have metadata recording fallback
        assert result.metadata is not None
        assert "fallback_used" in result.metadata
        assert result.metadata["fallback_used"] == "scout_opportunity"
