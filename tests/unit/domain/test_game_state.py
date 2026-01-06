"""Unit tests for GameState domain model.

Test Coverage: AC-2.3.1 through AC-2.3.10 (10 acceptance criteria)
"""

import pytest
from pydantic import ValidationError

from src.domain.errors import E_INVALID_BOARD_SIZE
from src.domain.models import Board, GameState, Position


class TestGameStateCreation:
    """Test GameState creation and validation."""

    def test_ac_2_3_1_valid_gamestate(self):
        """AC-2.3.1: Given valid Board, player='X', AI='O', when GameState is created, then game state is valid with move_number=0."""
        game_state = GameState(player_symbol="X", ai_symbol="O")
        assert game_state.board is not None
        assert game_state.player_symbol == "X"
        assert game_state.ai_symbol == "O"
        assert game_state.move_count == 0

    def test_ac_2_3_10_invalid_board(self):
        """AC-2.3.10: Given invalid board (size ≠ 3x3), when GameState is created, then validation error E_INVALID_BOARD_SIZE is raised."""
        # GameState validates board through Board field, so we pass invalid cells data
        # which will cause Board validation to fail when GameState tries to create/validate the Board
        with pytest.raises(ValidationError) as exc_info:
            GameState.model_validate(
                {
                    "board": {"cells": [["EMPTY", "EMPTY"], ["EMPTY", "EMPTY"]]},  # 2x2 board
                    "player_symbol": "X",
                    "ai_symbol": "O",
                }
            )
        error_str = str(exc_info.value)
        assert E_INVALID_BOARD_SIZE in error_str or "3 rows" in error_str


class TestGetCurrentPlayer:
    """Test get_current_player() method."""

    def test_ac_2_3_2_move_count_0_returns_player(self):
        """AC-2.3.2: Given GameState with move_number=0, when get_current_player() is called, then returns player symbol 'X'."""
        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=0)
        assert game_state.get_current_player() == "X"

    def test_ac_2_3_3_move_count_1_returns_ai(self):
        """AC-2.3.3: Given GameState with move_number=1, when get_current_player() is called, then returns AI symbol 'O'."""
        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=1)
        assert game_state.get_current_player() == "O"

    def test_get_current_player_even_move_count(self):
        """Test that even move counts return player symbol."""
        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=2)
        assert game_state.get_current_player() == "X"

        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=4)
        assert game_state.get_current_player() == "X"

    def test_get_current_player_odd_move_count(self):
        """Test that odd move counts return AI symbol."""
        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=3)
        assert game_state.get_current_player() == "O"

        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=5)
        assert game_state.get_current_player() == "O"


class TestGetOpponent:
    """Test get_opponent() method."""

    def test_ac_2_3_9_player_x_returns_o(self):
        """AC-2.3.9: Given GameState with player='X', when get_opponent() is called, then returns 'O'."""
        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=0)
        # get_opponent should work with current player (X at move_count=0)
        assert game_state.get_opponent() == "O"
        # Also test explicit symbol
        assert game_state.get_opponent("X") == "O"

    def test_get_opponent_player_o_returns_x(self):
        """Test that get_opponent('O') returns 'X'."""
        game_state = GameState(player_symbol="X", ai_symbol="O")
        assert game_state.get_opponent("O") == "X"


class TestWinDetection:
    """Test win detection (is_game_over and get_winner)."""

    def test_ac_2_3_4_three_x_in_row(self):
        """AC-2.3.4: Given GameState with three X's in a row, when game state is evaluated, then is_game_over=True and winner='X'."""
        board = Board()
        # Set three X's in row 0
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "X")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
        assert game_state.is_game_over() is True
        assert game_state.get_winner() == "X"

    def test_ac_2_3_5_three_o_in_column(self):
        """AC-2.3.5: Given GameState with three O's in a column, when game state is evaluated, then is_game_over=True and winner='O'."""
        board = Board()
        # Set three O's in column 1
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=2, col=1), "O")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
        assert game_state.is_game_over() is True
        assert game_state.get_winner() == "O"

    def test_ac_2_3_6_three_x_on_diagonal(self):
        """AC-2.3.6: Given GameState with three X's on diagonal, when game state is evaluated, then is_game_over=True and winner='X'."""
        board = Board()
        # Set three X's on main diagonal
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=1, col=1), "X")
        board.set_cell(Position(row=2, col=2), "X")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
        assert game_state.is_game_over() is True
        assert game_state.get_winner() == "X"

    def test_three_o_on_anti_diagonal(self):
        """Test win detection for three O's on anti-diagonal."""
        board = Board()
        # Set three O's on anti-diagonal
        board.set_cell(Position(row=0, col=2), "O")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=2, col=0), "O")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
        assert game_state.is_game_over() is True
        assert game_state.get_winner() == "O"


class TestDrawDetection:
    """Test draw detection."""

    def test_ac_2_3_7_all_cells_occupied_no_winner(self):
        """AC-2.3.7: Given GameState with all 9 cells occupied and no winner, when game state is evaluated, then is_game_over=True and winner='DRAW'."""
        board = Board()
        # Create a draw scenario (no winner, all cells filled)
        # X O X
        # O O X
        # O X O
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=0, col=2), "X")
        board.set_cell(Position(row=1, col=0), "O")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=1, col=2), "X")
        board.set_cell(Position(row=2, col=0), "O")
        board.set_cell(Position(row=2, col=1), "X")
        board.set_cell(Position(row=2, col=2), "O")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=9)
        assert game_state.is_game_over() is True
        assert game_state.get_winner() == "DRAW"

    def test_ac_2_3_8_five_moves_no_winner(self):
        """AC-2.3.8: Given GameState with 5 moves and no winner, when game state is evaluated, then is_game_over=False."""
        board = Board()
        # Create a partial game scenario (5 moves, no winner)
        # X O _
        # _ X _
        # O _ _
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=1, col=1), "X")
        board.set_cell(Position(row=2, col=0), "O")
        # Don't create a diagonal win - use a different position
        board.set_cell(Position(row=1, col=0), "X")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=5)
        assert game_state.is_game_over() is False
        assert game_state.get_winner() is None


class TestGameStateEdgeCases:
    """Test edge cases for GameState."""

    def test_empty_board_not_game_over(self):
        """Test that an empty board is not game over."""
        game_state = GameState(player_symbol="X", ai_symbol="O", move_count=0)
        assert game_state.is_game_over() is False
        assert game_state.get_winner() is None

    def test_partial_game_not_game_over(self):
        """Test that a partial game with no winner is not game over."""
        board = Board()
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=1, col=1), "O")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)
        assert game_state.is_game_over() is False
        assert game_state.get_winner() is None

    def test_win_before_all_cells_filled(self):
        """Test that a win is detected even if not all cells are filled."""
        board = Board()
        # X wins on row 0 (only 3 moves)
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "X")
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
        assert game_state.is_game_over() is True
        assert game_state.get_winner() == "X"

    def test_all_rows_win_detection(self):
        """Test win detection for all three rows."""
        for row in range(3):
            board = Board()
            board.set_cell(Position(row=row, col=0), "X")
            board.set_cell(Position(row=row, col=1), "X")
            board.set_cell(Position(row=row, col=2), "X")
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
            assert game_state.is_game_over() is True
            assert game_state.get_winner() == "X"

    def test_all_columns_win_detection(self):
        """Test win detection for all three columns."""
        for col in range(3):
            board = Board()
            board.set_cell(Position(row=0, col=col), "O")
            board.set_cell(Position(row=1, col=col), "O")
            board.set_cell(Position(row=2, col=col), "O")
            game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)
            assert game_state.is_game_over() is True
            assert game_state.get_winner() == "O"
