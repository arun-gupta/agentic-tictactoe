"""Integration tests for Agent Pipeline Orchestration.

Tests the complete pipeline flow: Scout → Strategist → Executor
"""

from src.agents.pipeline import AgentPipeline
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
