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
        # but Executor should fail validation
        board = Board(
            cells=[
                ["X", "X", "X"],  # X has won
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        # Execute pipeline - should fail because game is over
        result = pipeline.execute_pipeline(game_state)

        # Should return error result (game is over, can't make move)
        assert not result.success or (result.data is not None and not result.data.success)


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

        # Should timeout and return error
        assert not result.success
        assert result.error_code == E_LLM_TIMEOUT
        assert "Scout exceeded timeout" in (result.error_message or "")
        # Note: ThreadPoolExecutor timeout cancels the future but thread may continue running
        # The important thing is that we get the timeout error, which we verify above

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

        # Should timeout and return error
        assert not result.success
        assert result.error_code == E_LLM_TIMEOUT
        assert "Strategist exceeded timeout" in (result.error_message or "")
        # Note: ThreadPoolExecutor timeout cancels the future but thread may continue running
        # The important thing is that we get the timeout error, which we verify above

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

        # Should timeout and return error
        assert not result.success
        assert result.error_code == E_LLM_TIMEOUT
        assert "Executor exceeded timeout" in (result.error_message or "")
        # Note: ThreadPoolExecutor timeout cancels the future but thread may continue running
        # The important thing is that we get the timeout error, which we verify above

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
        # The remaining_timeout calculation should limit scout to 1s
        assert not result.success
        assert result.error_code == E_LLM_TIMEOUT
        # The timeout should be due to total timeout constraint (remaining_timeout limits it)
        assert "Scout exceeded timeout" in (result.error_message or "")
        # Note: The total timeout is enforced by limiting remaining_timeout,
        # which gets passed to _execute_with_timeout, so it shows as "Scout exceeded timeout"
        # This is correct behavior - the total timeout is enforced by limiting per-agent timeouts
