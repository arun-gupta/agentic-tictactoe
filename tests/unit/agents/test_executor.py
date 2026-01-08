"""Tests for Executor Agent - Move Execution and Validation.

This file includes:
1. Subsection tests (for incremental development/debugging)
2. Official acceptance criteria tests (AC-3.3.1 through AC-3.3.7)
"""

from src.agents.executor import ExecutorAgent
from src.domain.agent_models import (
    MovePriority,
    MoveRecommendation,
    Strategy,
)
from src.domain.errors import (
    E_CELL_OCCUPIED,
    E_GAME_ALREADY_OVER,
    E_MOVE_OUT_OF_BOUNDS,
)
from src.domain.models import Board, GameState, Position


# ==============================================================================
# SUBSECTION 3.2.1: Move Validation
# ==============================================================================
class TestMoveValidation:
    """Development tests for move validation logic."""

    def test_subsection_3_2_1_validates_position_bounds(self) -> None:
        """Subsection 3.2.1: Validates position is within bounds (0-2)."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state with empty board
        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        # Create strategy with valid position
        # Note: Position validates bounds at construction, so we can't create an invalid Position
        # Instead, we test the validation logic by directly testing _validate_move with a Position
        # that has out-of-bounds values. We use model_construct to bypass validation.

        # Test that Position itself validates bounds (defensive check)
        # Since Position validates bounds, a Strategy with invalid Position can't exist
        # But we still test the _validate_move method's bounds check logic
        # Create a mock MoveRecommendation with out-of-bounds position using model_construct
        # This bypasses Pydantic validation for testing purposes
        invalid_move_recommendation = MoveRecommendation.model_construct(
            position=Position.model_construct(row=3, col=1),  # Out of bounds
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.7,
            reasoning="Test move",
        )

        # Test _validate_move directly with invalid position
        validation_errors = executor._validate_move(game_state, invalid_move_recommendation)

        # Should return bounds error
        assert E_MOVE_OUT_OF_BOUNDS in validation_errors

    def test_subsection_3_2_1_validates_cell_empty(self) -> None:
        """Subsection 3.2.1: Validates cell is empty."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state with occupied cell
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Create strategy with move to occupied cell
        invalid_move = MoveRecommendation(
            position=Position(row=0, col=0),  # Already occupied by X
            priority=MovePriority.BLOCK_THREAT,
            confidence=0.95,
            reasoning="Block threat",
        )
        strategy = Strategy(
            primary_move=invalid_move,
            alternatives=[],
            game_plan="Block opponent",
            risk_assessment="medium",
        )

        # Execute should return validation error
        result = executor.execute(game_state, strategy)

        # Should return error result with validation errors
        assert not result.success
        assert result.data is not None
        execution = result.data
        assert not execution.success
        assert E_CELL_OCCUPIED in execution.validation_errors

    def test_subsection_3_2_1_validates_game_not_over(self) -> None:
        """Subsection 3.2.1: Validates game is not over."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state with winner (game over)
        board = Board(
            cells=[
                ["X", "X", "X"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
        # Game is over - X wins

        # Create strategy with valid move position
        valid_move = MoveRecommendation(
            position=Position(row=1, col=0),  # Valid position, but game is over
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.4,
            reasoning="Take corner",
        )
        strategy = Strategy(
            primary_move=valid_move,
            alternatives=[],
            game_plan="Take corner",
            risk_assessment="low",
        )

        # Execute should return validation error
        result = executor.execute(game_state, strategy)

        # Should return error result with validation errors
        assert not result.success
        assert result.data is not None
        execution = result.data
        assert not execution.success
        assert E_GAME_ALREADY_OVER in execution.validation_errors


# ==============================================================================
# SUBSECTION 3.2.2: Move Execution
# ==============================================================================
class TestMoveExecution:
    """Development tests for move execution logic."""

    def test_subsection_3_2_2_executes_valid_move_via_engine(self) -> None:
        """Subsection 3.2.2: Successfully executes valid move via game engine."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state where it's AI's turn (odd move count)
        # Player (X) has already made first move at (0,0)
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Create strategy with valid move
        valid_move = MoveRecommendation(
            position=Position(row=1, col=1),  # Center position
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.7,
            reasoning="Take center",
        )
        strategy = Strategy(
            primary_move=valid_move,
            alternatives=[],
            game_plan="Control center",
            risk_assessment="low",
        )

        # Execute should succeed
        result = executor.execute(game_state, strategy)

        # Should return success result
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.success
        assert execution.position == Position(row=1, col=1)
        assert execution.validation_errors == []

    def test_subsection_3_2_2_tracks_execution_time(self) -> None:
        """Subsection 3.2.2: Tracks execution time in milliseconds."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state where it's AI's turn (odd move count)
        # Player (X) has already made first move at (0,1)
        board = Board(
            cells=[
                ["EMPTY", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Create strategy with valid move
        valid_move = MoveRecommendation(
            position=Position(row=0, col=0),  # Corner position
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.4,
            reasoning="Take corner",
        )
        strategy = Strategy(
            primary_move=valid_move,
            alternatives=[],
            game_plan="Take corner",
            risk_assessment="low",
        )

        # Execute and check execution time
        result = executor.execute(game_state, strategy)

        # Should have execution time recorded
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.execution_time_ms >= 0.0
        assert result.execution_time_ms >= 0.0

    def test_subsection_3_2_2_records_actual_priority_used(self) -> None:
        """Subsection 3.2.2: Records actual priority used in MoveExecution."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state where it's AI's turn (odd move count)
        # Player (X) has already made first move at (2,2)
        board = Board(
            cells=[
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "X"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Create strategy with high priority move
        high_priority_move = MoveRecommendation(
            position=Position(row=1, col=1),  # Center position
            priority=MovePriority.IMMEDIATE_WIN,  # High priority
            confidence=1.0,
            reasoning="Winning move",
        )
        strategy = Strategy(
            primary_move=high_priority_move,
            alternatives=[],
            game_plan="Win game",
            risk_assessment="low",
        )

        # Execute and check priority is recorded
        result = executor.execute(game_state, strategy)

        # Should have actual_priority_used recorded
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.actual_priority_used == MovePriority.IMMEDIATE_WIN
