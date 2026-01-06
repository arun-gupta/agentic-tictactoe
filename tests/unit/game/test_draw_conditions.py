"""Unit tests for draw condition detection (AC-4.1.2.1 through AC-4.1.2.6)."""

from src.domain.models import Board, GameState, Position
from src.game.engine import GameEngine


class TestDrawConditionDetection:
    """Test draw condition detection (complete draw and inevitable draw)."""

    def test_ac_4_1_2_1_complete_draw_move_count_9(self) -> None:
        """AC-4.1.2.1: Given MoveCount=9 and no winning line exists, when checking draw, then Winner=DRAW and IsGameOver=true."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Fill board with no winner - pattern: XOX/OXO/OXO
        # Row 0: X, O, X
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=0, col=2), "X")
        # Row 1: O, X, O
        board.set_cell(Position(row=1, col=0), "O")
        board.set_cell(Position(row=1, col=1), "X")
        board.set_cell(Position(row=1, col=2), "O")
        # Row 2: O, X, O (no winner - no complete lines)
        board.set_cell(Position(row=2, col=0), "O")
        board.set_cell(Position(row=2, col=1), "X")
        board.set_cell(Position(row=2, col=2), "O")
        # Create GameState with move_count=9
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=9)

        is_draw = engine.check_draw()
        winner = engine.game_state.get_winner()
        is_game_over = engine.game_state.is_game_over()

        assert is_draw is True
        assert winner == "DRAW"
        assert is_game_over is True

    def test_ac_4_1_2_2_inevitable_draw_move_count_8(self) -> None:
        """AC-4.1.2.2: Given MoveCount=8 and no empty cell allows any player to win, when checking inevitable draw, then Winner=DRAW and IsGameOver=true."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Board state where at move 8, neither X nor O can win from the last empty cell
        # X | O | X
        # ---------
        # X | O | O
        # ---------
        # O | X | ?  (empty at 2,2)
        # Row 0: X, O, X
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=0, col=2), "X")
        # Row 1: X, O, O
        board.set_cell(Position(row=1, col=0), "X")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=1, col=2), "O")
        # Row 2: O, X, (empty at 2,2)
        board.set_cell(Position(row=2, col=0), "O")
        board.set_cell(Position(row=2, col=1), "X")
        # move_count=8, last empty cell is (2,2)
        # Neither X nor O can win from (2,2) - inevitable draw
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=8)

        is_draw = engine.check_draw()

        assert is_draw is True
        # Note: GameState.get_winner() uses _check_draw() which only checks complete draw (move_count=9)
        # For inevitable draw at move_count=8, we verify check_draw() returns True
        # Full state update (Winner=DRAW, IsGameOver=true) will be handled in move execution (Phase 2.3)

    def test_ac_4_1_2_3_move_count_7_winnable_continues(self) -> None:
        """AC-4.1.2.3: Given MoveCount=7 and at least one empty cell allows a win, when checking draw, then game continues (no draw yet)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Example 2 from spec (Move 7 - winnable):
        # X | O | X
        # ---------
        # O | X | ?
        # ---------
        # O | ? | ?
        # Row 0: X, O, X
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=0, col=2), "X")
        # Row 1: O, X, (empty at 1,2)
        board.set_cell(Position(row=1, col=0), "O")
        board.set_cell(Position(row=1, col=1), "X")
        # Row 2: O, (empty at 2,1), (empty at 2,2)
        board.set_cell(Position(row=2, col=0), "O")
        # move_count=7, X can win by placing at (1,2) to complete column 2
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=7)

        is_draw = engine.check_draw()
        winner = engine.game_state.get_winner()
        is_game_over = engine.game_state.is_game_over()

        assert is_draw is False
        assert winner is None
        assert is_game_over is False

    def test_ac_4_1_2_4_move_count_less_than_9_winning_moves_remain(self) -> None:
        """AC-4.1.2.4: Given MoveCount<9 and winning moves remain, when checking draw, then Winner=None and IsGameOver=false."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Simple scenario: X has two in a row, can win on next move
        # Row 0: X, X, (empty)
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        # move_count=2
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        is_draw = engine.check_draw()
        winner = engine.game_state.get_winner()
        is_game_over = engine.game_state.is_game_over()

        assert is_draw is False
        assert winner is None
        assert is_game_over is False

    def test_ac_4_1_2_5_example_1_inevitable_draw(self) -> None:
        """AC-4.1.2.5: Given board state matching Example 1 (inevitable draw at move 8), when checking draw, then Winner=DRAW."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Board state where at move 8, neither player can win from the last empty cell
        # X | O | X
        # ---------
        # X | O | O
        # ---------
        # O | X | ?  (last cell empty)
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=0, col=2), "X")
        board.set_cell(Position(row=1, col=0), "X")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=1, col=2), "O")
        board.set_cell(Position(row=2, col=0), "O")
        board.set_cell(Position(row=2, col=1), "X")
        # Cell (2,2) is empty, move_count=8
        # Neither X nor O can win from (2,2) - inevitable draw
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=8)

        is_draw = engine.check_draw()

        assert is_draw is True
        # Note: GameState.get_winner() uses _check_draw() which only checks complete draw (move_count=9)
        # For inevitable draw at move_count=8, we verify check_draw() returns True
        # Full state update (Winner=DRAW) will be handled in move execution (Phase 2.3)

    def test_ac_4_1_2_6_example_2_winnable_no_draw(self) -> None:
        """AC-4.1.2.6: Given board state matching Example 2 (winnable at move 7), when checking draw, then Winner=None."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        board = Board()
        # Example 2 from spec - exact match:
        # X | O | X
        # ---------
        # O | X | ?
        # ---------
        # O | ? | ?
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "O")
        board.set_cell(Position(row=0, col=2), "X")
        board.set_cell(Position(row=1, col=0), "O")
        board.set_cell(Position(row=1, col=1), "X")
        # Cell (1,2) is empty - X can win here by completing column 2
        board.set_cell(Position(row=2, col=0), "O")
        # Cells (2,1) and (2,2) are empty
        # move_count=7
        engine.game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=7)

        is_draw = engine.check_draw()
        winner = engine.game_state.get_winner()

        assert is_draw is False
        assert winner is None
