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

        # Create game state with occupied cell - need to test validation directly
        # since fallback will now succeed with a random move
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Create move recommendation to occupied cell
        invalid_move = MoveRecommendation(
            position=Position(row=0, col=0),  # Already occupied by X
            priority=MovePriority.BLOCK_THREAT,
            confidence=0.95,
            reasoning="Block threat",
        )

        # Test validation directly
        validation_errors = executor._validate_move(game_state, invalid_move)

        # Should have validation error for occupied cell
        assert E_CELL_OCCUPIED in validation_errors

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


# ==============================================================================
# SUBSECTION 3.2.3: Fallback Handling
# ==============================================================================
class TestFallbackHandling:
    """Development tests for fallback handling logic."""

    def test_subsection_3_2_3_falls_back_to_first_alternative(self) -> None:
        """Subsection 3.2.3: Falls back to first alternative when primary move fails."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state where primary move position is occupied
        # Player (X) has moved at (1,1), so primary move to center will fail
        board = Board(
            cells=[
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "X", "EMPTY"],  # Center occupied
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=1)

        # Create strategy with invalid primary move (occupied) and valid alternative
        invalid_primary = MoveRecommendation(
            position=Position(row=1, col=1),  # Occupied by X
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.7,
            reasoning="Take center",
        )
        valid_alternative = MoveRecommendation(
            position=Position(row=0, col=0),  # Valid corner
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.4,
            reasoning="Take corner",
        )
        strategy = Strategy(
            primary_move=invalid_primary,
            alternatives=[valid_alternative],
            game_plan="Control board",
            risk_assessment="low",
        )

        # Execute should fallback to alternative
        result = executor.execute(game_state, strategy)

        # Should succeed using alternative
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.success
        assert execution.position == Position(row=0, col=0)
        assert "Fallback" in execution.reasoning
        assert "alternative" in execution.reasoning.lower()

    def test_subsection_3_2_3_falls_back_to_random_valid_move(self) -> None:
        """Subsection 3.2.3: Falls back to random valid move when all alternatives fail."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state where both primary and alternatives are invalid
        # Player (X) has moved at (0,0) and (1,1), AI (O) needs to move (odd move count)
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        # Create strategy with invalid primary and invalid alternatives (all occupied)
        invalid_primary = MoveRecommendation(
            position=Position(row=0, col=0),  # Occupied
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.4,
            reasoning="Take corner",
        )
        invalid_alt1 = MoveRecommendation(
            position=Position(row=1, col=1),  # Occupied
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.7,
            reasoning="Take center",
        )
        strategy = Strategy(
            primary_move=invalid_primary,
            alternatives=[invalid_alt1],
            game_plan="Control board",
            risk_assessment="low",
        )

        # Execute should fallback to random valid move
        result = executor.execute(game_state, strategy)

        # Should succeed using random valid move
        assert result.success
        assert result.data is not None
        execution = result.data
        assert execution.success
        assert execution.position is not None
        # Position should be one of the empty cells: (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)
        assert execution.position.row in [0, 1, 2]
        assert execution.position.col in [0, 1, 2]
        assert board.get_cell(execution.position) == "EMPTY"  # Should be empty
        assert "Fallback" in execution.reasoning
        assert "random" in execution.reasoning.lower()

    def test_subsection_3_2_3_returns_error_when_no_valid_moves(self) -> None:
        """Subsection 3.2.3: Returns clear error when no valid moves available."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state with board full (game over)
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["O", "X", "O"],
                ["X", "O", "X"],  # Board full, draw
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=9)

        # Create strategy with any move (doesn't matter, board is full)
        invalid_primary = MoveRecommendation(
            position=Position(row=0, col=0),  # Occupied
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.4,
            reasoning="Take corner",
        )
        strategy = Strategy(
            primary_move=invalid_primary,
            alternatives=[],
            game_plan="Control board",
            risk_assessment="low",
        )

        # Execute should return error
        result = executor.execute(game_state, strategy)

        # Should return error result
        assert not result.success
        assert result.data is not None
        execution = result.data
        assert not execution.success
        assert execution.position is None
        assert (
            "No valid moves available" in execution.reasoning or "Game over" in execution.reasoning
        )
