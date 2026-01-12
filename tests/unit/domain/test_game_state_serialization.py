"""Tests for GameState JSON serialization.

This module tests that GameState serialization includes computed fields
is_game_over and winner in the JSON output.
"""

from src.domain.models import Board, GameState, Position


class TestGameStateSerialization:
    """Test GameState JSON serialization includes computed fields."""

    def test_serialization_includes_is_game_over_when_game_in_progress(self) -> None:
        """Test that model_dump() includes is_game_over field when game is in progress."""
        game_state = GameState(
            board=Board(),
            player_symbol="X",
            ai_symbol="O",
            move_count=2,
        )

        data = game_state.model_dump()

        assert "is_game_over" in data
        assert data["is_game_over"] is False
        assert game_state.is_game_over() is False

    def test_serialization_includes_is_game_over_when_game_over_with_winner(
        self,
    ) -> None:
        """Test that model_dump() includes is_game_over field when game is over with winner."""
        board = Board()
        # Set up a winning board for X (row 0)
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "X")

        game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=3,
        )

        data = game_state.model_dump()

        assert "is_game_over" in data
        assert data["is_game_over"] is True
        assert game_state.is_game_over() is True

    def test_serialization_includes_is_game_over_when_draw(self) -> None:
        """Test that model_dump() includes is_game_over field when game is a draw."""
        board = Board()
        # Set up a draw board (full board, no winner)
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

        game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=9,
        )

        data = game_state.model_dump()

        assert "is_game_over" in data
        assert data["is_game_over"] is True
        assert game_state.is_game_over() is True

    def test_serialization_includes_winner_when_game_in_progress(self) -> None:
        """Test that model_dump() includes winner field when game is in progress."""
        game_state = GameState(
            board=Board(),
            player_symbol="X",
            ai_symbol="O",
            move_count=2,
        )

        data = game_state.model_dump()

        assert "winner" in data
        assert data["winner"] is None
        assert game_state.get_winner() is None

    def test_serialization_includes_winner_when_player_wins(self) -> None:
        """Test that model_dump() includes winner field when player wins."""
        board = Board()
        # Set up a winning board for X (row 0)
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=0, col=1), "X")
        board.set_cell(Position(row=0, col=2), "X")

        game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=3,
        )

        data = game_state.model_dump()

        assert "winner" in data
        assert data["winner"] == "X"
        assert game_state.get_winner() == "X"

    def test_serialization_includes_winner_when_ai_wins(self) -> None:
        """Test that model_dump() includes winner field when AI wins."""
        board = Board()
        # Set up a winning board for O (column 0)
        board.set_cell(Position(row=0, col=0), "O")
        board.set_cell(Position(row=1, col=0), "O")
        board.set_cell(Position(row=2, col=0), "O")

        game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=3,
        )

        data = game_state.model_dump()

        assert "winner" in data
        assert data["winner"] == "O"
        assert game_state.get_winner() == "O"

    def test_serialization_includes_winner_when_draw(self) -> None:
        """Test that model_dump() includes winner field as DRAW when game is a draw."""
        board = Board()
        # Set up a draw board (full board, no winner)
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

        game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=9,
        )

        data = game_state.model_dump()

        assert "winner" in data
        assert data["winner"] == "DRAW"
        assert game_state.get_winner() == "DRAW"

    def test_serialization_fields_match_method_results(self) -> None:
        """Test that serialized fields match the results of method calls."""
        # Test in-progress game
        game_state_in_progress = GameState(
            board=Board(),
            player_symbol="X",
            ai_symbol="O",
            move_count=2,
        )
        data = game_state_in_progress.model_dump()
        assert data["is_game_over"] == game_state_in_progress.is_game_over()
        assert data["winner"] == game_state_in_progress.get_winner()

        # Test winning game
        board_win = Board()
        board_win.set_cell(Position(row=0, col=0), "X")
        board_win.set_cell(Position(row=0, col=1), "X")
        board_win.set_cell(Position(row=0, col=2), "X")
        game_state_win = GameState(
            board=board_win,
            player_symbol="X",
            ai_symbol="O",
            move_count=3,
        )
        data_win = game_state_win.model_dump()
        assert data_win["is_game_over"] == game_state_win.is_game_over()
        assert data_win["winner"] == game_state_win.get_winner()
