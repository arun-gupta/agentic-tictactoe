"""Unit tests for move validation (AC-4.1.3.1 through AC-4.1.3.10)."""

from src.domain.errors import (
    E_CELL_OCCUPIED,
    E_GAME_ALREADY_OVER,
    E_INVALID_PLAYER,
    E_INVALID_TURN,
    E_MOVE_OUT_OF_BOUNDS,
)
from src.domain.models import Board, GameState, Position
from src.game.engine import GameEngine


class TestMoveValidation:
    """Test move validation with all illegal move conditions."""

    def test_ac_4_1_3_1_row_negative_out_of_bounds(self) -> None:
        """AC-4.1.3.1: Given row=-1, col=1, when validating move, then error=E_MOVE_OUT_OF_BOUNDS."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        is_valid, error_code = engine.validate_move(row=-1, col=1, player="X")

        assert is_valid is False
        assert error_code == E_MOVE_OUT_OF_BOUNDS

    def test_ac_4_1_3_2_row_too_high_out_of_bounds(self) -> None:
        """AC-4.1.3.2: Given row=3, col=1, when validating move, then error=E_MOVE_OUT_OF_BOUNDS."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        is_valid, error_code = engine.validate_move(row=3, col=1, player="X")

        assert is_valid is False
        assert error_code == E_MOVE_OUT_OF_BOUNDS

    def test_ac_4_1_3_3_col_negative_out_of_bounds(self) -> None:
        """AC-4.1.3.3: Given row=1, col=-1, when validating move, then error=E_MOVE_OUT_OF_BOUNDS."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        is_valid, error_code = engine.validate_move(row=1, col=-1, player="X")

        assert is_valid is False
        assert error_code == E_MOVE_OUT_OF_BOUNDS

    def test_ac_4_1_3_4_col_too_high_out_of_bounds(self) -> None:
        """AC-4.1.3.4: Given row=1, col=3, when validating move, then error=E_MOVE_OUT_OF_BOUNDS."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        is_valid, error_code = engine.validate_move(row=1, col=3, player="X")

        assert is_valid is False
        assert error_code == E_MOVE_OUT_OF_BOUNDS

    def test_ac_4_1_3_5_cell_occupied(self) -> None:
        """AC-4.1.3.5: Given Board[1][1]=X, when attempting move at (1,1), then error=E_CELL_OCCUPIED."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        position = Position(row=1, col=1)
        # Place X at (1,1)
        engine.game_state.board.set_cell(position, "X")

        is_valid, error_code = engine.validate_move(row=1, col=1, player="X")

        assert is_valid is False
        assert error_code == E_CELL_OCCUPIED

    def test_ac_4_1_3_6_game_already_over(self) -> None:
        """AC-4.1.3.6: Given IsGameOver=true, when attempting move, then error=E_GAME_ALREADY_OVER."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        # Create a board with a winner to make game over
        board = Board()
        # Row 0: X, X, X (winning line)
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "X")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        is_valid, error_code = engine.validate_move(row=2, col=2, player="X")

        assert is_valid is False
        assert error_code == E_GAME_ALREADY_OVER

    def test_ac_4_1_3_7_invalid_player_symbol(self) -> None:
        """AC-4.1.3.7: Given player='Z', when validating move, then error=E_INVALID_PLAYER."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Type ignore because we're testing invalid input
        is_valid, error_code = engine.validate_move(row=1, col=1, player="Z")  # type: ignore[arg-type]

        assert is_valid is False
        assert error_code == E_INVALID_PLAYER

    def test_ac_4_1_3_8_wrong_turn(self) -> None:
        """AC-4.1.3.8: Given CurrentPlayer=X and attempting move with player=O, when validating move, then error=E_INVALID_TURN."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        # Current player should be X (move_count=0, even)

        # Try to move with O when it's X's turn
        is_valid, error_code = engine.validate_move(row=1, col=1, player="O")

        assert is_valid is False
        assert error_code == E_INVALID_TURN

    def test_ac_4_1_3_9_legal_move(self) -> None:
        """AC-4.1.3.9: Given row=1, col=1, Board[1][1]=EMPTY, IsGameOver=false, player=CurrentPlayer, when validating move, then move is legal (no error)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        # Current player is X (move_count=0)
        # Position (1,1) is empty (default board)
        # Game is not over

        is_valid, error_code = engine.validate_move(row=1, col=1, player="X")

        assert is_valid is True
        assert error_code is None

    def test_ac_4_1_3_10_all_invariants_satisfied(self) -> None:
        """AC-4.1.3.10: Given all 6 invariants satisfied, when validating move, then returns success and allows move execution."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # All 6 invariants satisfied:
        # 1. 0 <= row <= 2 (0 is valid)
        # 2. 0 <= col <= 2 (0 is valid)
        # 3. Board[0][0] = EMPTY (default board)
        # 4. IsGameOver = false (new game)
        # 5. P = CurrentPlayer (X = X)
        # 6. P ∈ {X, O} (X is valid)

        is_valid, error_code = engine.validate_move(row=0, col=0, player="X")

        assert is_valid is True
        assert error_code is None

    def test_multiple_validation_checks_order(self) -> None:
        """Test that validation checks are performed in correct order."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        # Out of bounds should be checked first (before checking if cell is empty)

        is_valid, error_code = engine.validate_move(row=3, col=3, player="X")

        assert is_valid is False
        assert error_code == E_MOVE_OUT_OF_BOUNDS  # Not E_CELL_OCCUPIED

    def test_occupied_cell_with_different_player(self) -> None:
        """Test that occupied cell check happens before turn check."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        position = Position(row=1, col=1)
        # Place X at (1,1)
        engine.game_state.board.set_cell(position, "X")

        # Even if it's O's turn, should get E_CELL_OCCUPIED, not E_INVALID_TURN
        # But first we need to make it O's turn
        engine.game_state = GameState(
            board=engine.game_state.board,
            player_symbol="X",
            ai_symbol="O",
            move_count=1,  # O's turn
        )

        is_valid, error_code = engine.validate_move(row=1, col=1, player="O")

        assert is_valid is False
        assert error_code == E_CELL_OCCUPIED  # Cell occupied takes precedence
