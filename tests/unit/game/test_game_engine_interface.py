"""Tests for game engine interface (Task 2.5).

Tests AC-4.1.6.1 through AC-4.1.6.13 - Game Engine Interface
"""

from src.domain.errors import E_CELL_OCCUPIED, E_MOVE_OUT_OF_BOUNDS
from src.domain.models import Position
from src.game.engine import GameEngine


class TestMakeMove:
    """Test make_move() method."""

    def test_ac_4_1_6_1_valid_move_success(self) -> None:
        """AC-4.1.6.1: Valid move returns success and updates board."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Make valid move at (1,1)
        success, error = engine.make_move(1, 1, "X")

        assert success
        assert error is None
        assert engine.game_state.board.get_cell(Position(row=1, col=1)) == "X"
        assert engine.game_state.move_count == 1

    def test_ac_4_1_6_2_invalid_position_out_of_bounds(self) -> None:
        """AC-4.1.6.2: Invalid position returns E_MOVE_OUT_OF_BOUNDS."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Try to move at invalid position (3,3)
        success, error = engine.make_move(3, 3, "X")

        assert not success
        assert error == E_MOVE_OUT_OF_BOUNDS

    def test_ac_4_1_6_3_occupied_cell_error(self) -> None:
        """AC-4.1.6.3: Occupied position returns E_CELL_OCCUPIED."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # First move at (0,0)
        engine.make_move(0, 0, "X")

        # Try to move at same position
        success, error = engine.make_move(0, 0, "O")

        assert not success
        assert error == E_CELL_OCCUPIED


class TestCheckWinner:
    """Test check_winner() method."""

    def test_ac_4_1_6_4_winner_detected(self) -> None:
        """AC-4.1.6.4: Winning line for X returns X."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create winning line for X (top row)
        engine.make_move(0, 0, "X")
        engine.make_move(1, 0, "O")
        engine.make_move(0, 1, "X")
        engine.make_move(1, 1, "O")
        engine.make_move(0, 2, "X")  # X wins!

        winner = engine.check_winner()
        assert winner == "X"

    def test_ac_4_1_6_5_no_winner_returns_none(self) -> None:
        """AC-4.1.6.5: No winning lines returns None."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Make some moves without winning
        engine.make_move(0, 0, "X")
        engine.make_move(0, 1, "O")
        engine.make_move(1, 1, "X")

        winner = engine.check_winner()
        assert winner is None


class TestCheckDraw:
    """Test check_draw() method."""

    def test_ac_4_1_6_6_full_board_no_winner_is_draw(self) -> None:
        """AC-4.1.6.6: MoveCount=9 and no winner returns true."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create draw scenario
        # X | O | X
        # X | O | O
        # O | X | X
        engine.make_move(0, 0, "X")  # Move 0
        engine.make_move(0, 1, "O")  # Move 1
        engine.make_move(0, 2, "X")  # Move 2
        engine.make_move(1, 1, "O")  # Move 3
        engine.make_move(1, 0, "X")  # Move 4
        engine.make_move(1, 2, "O")  # Move 5
        engine.make_move(2, 1, "X")  # Move 6
        engine.make_move(2, 0, "O")  # Move 7
        engine.make_move(2, 2, "X")  # Move 8 - draw!

        is_draw = engine.check_draw()
        assert is_draw
        assert engine.game_state.move_count == 9

    def test_ac_4_1_6_7_incomplete_game_not_draw(self) -> None:
        """AC-4.1.6.7: MoveCount<9 returns false."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Make a few moves
        engine.make_move(0, 0, "X")
        engine.make_move(0, 1, "O")
        engine.make_move(1, 1, "X")

        is_draw = engine.check_draw()
        assert not is_draw
        assert engine.game_state.move_count < 9


class TestGetAvailableMoves:
    """Test get_available_moves() method."""

    def test_ac_4_1_6_8_five_empty_cells(self) -> None:
        """AC-4.1.6.8: 5 empty cells returns list of 5 positions."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Make 4 moves (4 occupied cells, 5 empty)
        engine.make_move(0, 0, "X")
        engine.make_move(0, 1, "O")
        engine.make_move(1, 1, "X")
        engine.make_move(0, 2, "O")

        available_moves = engine.get_available_moves()
        assert len(available_moves) == 5
        assert all(isinstance(pos, Position) for pos in available_moves)

    def test_ac_4_1_6_9_full_board_empty_list(self) -> None:
        """AC-4.1.6.9: All cells occupied returns empty list."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Fill entire board
        engine.make_move(0, 0, "X")
        engine.make_move(0, 1, "O")
        engine.make_move(0, 2, "X")
        engine.make_move(1, 1, "O")
        engine.make_move(1, 0, "X")
        engine.make_move(1, 2, "O")
        engine.make_move(2, 1, "X")
        engine.make_move(2, 0, "O")
        engine.make_move(2, 2, "X")

        available_moves = engine.get_available_moves()
        assert len(available_moves) == 0
        assert available_moves == []

    def test_empty_board_nine_available_moves(self) -> None:
        """Empty board returns all 9 positions."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        available_moves = engine.get_available_moves()
        assert len(available_moves) == 9


class TestValidateMove:
    """Test validate_move() method."""

    def test_ac_4_1_6_10_valid_move_returns_true(self) -> None:
        """AC-4.1.6.10: Valid move returns true with no error code."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        is_valid, error = engine.validate_move(1, 1, "X")

        assert is_valid
        assert error is None

    def test_ac_4_1_6_11_invalid_move_returns_false_with_error(self) -> None:
        """AC-4.1.6.11: Invalid move returns false with specific error code."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Try invalid position
        is_valid, error = engine.validate_move(3, 3, "X")

        assert not is_valid
        assert error == E_MOVE_OUT_OF_BOUNDS

    def test_multiple_invalid_move_scenarios(self) -> None:
        """Test various invalid move scenarios return specific errors."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Occupied cell
        engine.make_move(0, 0, "X")
        is_valid, error = engine.validate_move(0, 0, "O")
        assert not is_valid
        assert error == E_CELL_OCCUPIED


class TestResetGame:
    """Test reset_game() method."""

    def test_ac_4_1_6_12_reset_restores_initial_state(self) -> None:
        """AC-4.1.6.12: reset_game() restores initial state."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Play some moves
        engine.make_move(0, 0, "X")
        engine.make_move(0, 1, "O")
        engine.make_move(1, 1, "X")

        # Reset game
        engine.reset_game()

        # Verify initial state
        state = engine.get_current_state()
        assert state.move_count == 0
        assert state.get_current_player() == "X"
        assert not state.is_game_over()
        assert len(engine.get_available_moves()) == 9

    def test_reset_after_game_over(self) -> None:
        """Reset after game over restores playable state."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # X wins
        engine.make_move(0, 0, "X")
        engine.make_move(1, 0, "O")
        engine.make_move(0, 1, "X")
        engine.make_move(1, 1, "O")
        engine.make_move(0, 2, "X")  # X wins!

        assert engine.is_game_over()

        # Reset and verify playable
        engine.reset_game()
        assert not engine.is_game_over()
        success, _ = engine.make_move(0, 0, "X")
        assert success


class TestGetCurrentState:
    """Test get_current_state() method."""

    def test_ac_4_1_6_13_returns_complete_gamestate(self) -> None:
        """AC-4.1.6.13: Returns complete GameState with all properties."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Make some moves
        engine.make_move(0, 0, "X")
        engine.make_move(0, 1, "O")

        state = engine.get_current_state()

        # Verify all GameState properties exist
        assert hasattr(state, "board")
        assert hasattr(state, "player_symbol")
        assert hasattr(state, "ai_symbol")
        assert hasattr(state, "move_count")
        assert state.move_count == 2
        assert state.player_symbol == "X"
        assert state.ai_symbol == "O"

    def test_get_current_state_reflects_live_board(self) -> None:
        """get_current_state() reflects current board state."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Initial state
        state1 = engine.get_current_state()
        assert state1.move_count == 0

        # After move
        engine.make_move(1, 1, "X")
        state2 = engine.get_current_state()
        assert state2.move_count == 1
        assert state2.board.get_cell(Position(row=1, col=1)) == "X"


class TestCompleteGameFlow:
    """Test complete game flow using the public interface."""

    def test_complete_game_player_wins(self) -> None:
        """Complete game where player wins using public interface."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Player wins top row
        moves = [
            (0, 0, "X"),
            (1, 0, "O"),
            (0, 1, "X"),
            (1, 1, "O"),
            (0, 2, "X"),  # X wins!
        ]

        for row, col, player in moves:
            success, _ = engine.make_move(row, col, player)
            assert success

        assert engine.check_winner() == "X"
        assert engine.is_game_over()
        assert engine.get_current_state().get_winner() == "X"

    def test_complete_game_draw(self) -> None:
        """Complete game ending in draw using public interface."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create draw
        moves = [
            (0, 0, "X"),
            (0, 1, "O"),
            (0, 2, "X"),
            (1, 1, "O"),
            (1, 0, "X"),
            (1, 2, "O"),
            (2, 1, "X"),
            (2, 0, "O"),
            (2, 2, "X"),  # Draw
        ]

        for row, col, player in moves:
            success, _ = engine.make_move(row, col, player)
            assert success

        assert engine.check_draw()
        assert engine.is_game_over()
        assert engine.get_current_state().get_winner() == "DRAW"
