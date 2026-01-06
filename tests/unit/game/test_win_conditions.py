"""Unit tests for win condition detection (AC-4.1.1.1 through AC-4.1.1.10)."""


from src.domain.models import Board, GameState, Position
from src.game.engine import GameEngine


class TestWinConditionDetection:
    """Test win condition detection for all 8 winning lines."""

    def test_ac_4_1_1_1_row_0_win_x(self):
        """AC-4.1.1.1: Given board with X at (0,0), (0,1), (0,2), when checking win, then winner=X (Row 0)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place X in row 0
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "X")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "X"

    def test_ac_4_1_1_2_row_1_win_o(self):
        """AC-4.1.1.2: Given board with O at (1,0), (1,1), (1,2), when checking win, then winner=O (Row 1)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place O in row 1
        board.set_cell(Position(row=1, col=0), "O")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=1, col=2), "O")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "O"

    def test_ac_4_1_1_3_row_2_win_x(self):
        """AC-4.1.1.3: Given board with X at (2,0), (2,1), (2,2), when checking win, then winner=X (Row 2)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place X in row 2
        board.set_cell(Position(row=2, col=0), "X")
        board.set_cell(Position(row=2, col=1), "X")
        board.set_cell(Position(row=2, col=2), "X")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "X"

    def test_ac_4_1_1_4_col_0_win_o(self):
        """AC-4.1.1.4: Given board with O at (0,0), (1,0), (2,0), when checking win, then winner=O (Col 0)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place O in col 0
        board.set_cell(Position(row=0, col=0), "O")
        board.set_cell(Position(row=1, col=0), "O")
        board.set_cell(Position(row=2, col=0), "O")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "O"

    def test_ac_4_1_1_5_col_1_win_x(self):
        """AC-4.1.1.5: Given board with X at (0,1), (1,1), (2,1), when checking win, then winner=X (Col 1)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place X in col 1
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=1, col=1), "X")
        board.set_cell(Position(row=2, col=1), "X")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "X"

    def test_ac_4_1_1_6_col_2_win_o(self):
        """AC-4.1.1.6: Given board with O at (0,2), (1,2), (2,2), when checking win, then winner=O (Col 2)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place O in col 2
        board.set_cell(Position(row=0, col=2), "O")
        board.set_cell(Position(row=1, col=2), "O")
        board.set_cell(Position(row=2, col=2), "O")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "O"

    def test_ac_4_1_1_7_diagonal_main_win_x(self):
        """AC-4.1.1.7: Given board with X at (0,0), (1,1), (2,2), when checking win, then winner=X (Diagonal main)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place X in main diagonal
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=1, col=1), "X")
        board.set_cell(Position(row=2, col=2), "X")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "X"

    def test_ac_4_1_1_8_diagonal_anti_win_o(self):
        """AC-4.1.1.8: Given board with O at (0,2), (1,1), (2,0), when checking win, then winner=O (Diagonal anti)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place O in anti-diagonal
        board.set_cell(Position(row=0, col=2), "O")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=2, col=0), "O")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner == "O"

    def test_ac_4_1_1_9_no_win_mixed_line(self):
        """AC-4.1.1.9: Given board with 2 X's and 1 O in any line, when checking win, then winner=None (no win)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Place 2 X's and 1 O in row 0 (no win)
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "O")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()

        assert winner is None

    def test_ac_4_1_1_10_win_sets_game_over(self):
        """AC-4.1.1.10: Given move completes winning line, when win detection runs, then IsGameOver=true and Winner is set immediately."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Set up a winning line for X
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "X")
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O")

        winner = engine.check_winner()
        is_game_over = engine.game_state.is_game_over()
        winner_from_state = engine.game_state.get_winner()

        assert winner == "X"
        assert is_game_over is True
        assert winner_from_state == "X"
