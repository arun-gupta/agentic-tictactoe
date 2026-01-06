"""Tests for turn order and state transitions (Task 2.3).

Tests AC-4.1.4.1 through AC-4.1.4.9 - Turn Order Rules and State Transitions
"""


from src.domain.errors import E_GAME_ALREADY_OVER, E_INVALID_TURN
from src.game.engine import GameEngine


class TestTurnAlternation:
    """Test turn alternation between Player and AI."""

    def test_player_starts_on_even_move_zero(self) -> None:
        """AC-4.1.4.1: Player moves on even move numbers (move 0)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")
        state = engine.get_current_state()

        # Move 0 (even) - should be Player's turn
        assert state.move_count == 0
        assert state.get_current_player() == "X"  # Player

    def test_ai_moves_on_odd_move_one(self) -> None:
        """AC-4.1.4.2: AI moves on odd move numbers (move 1)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Player makes move 0
        success, _ = engine.make_move(0, 0, "X")
        assert success

        state = engine.get_current_state()
        # Move 1 (odd) - should be AI's turn
        assert state.move_count == 1
        assert state.get_current_player() == "O"  # AI

    def test_turn_alternates_player_ai_player(self) -> None:
        """AC-4.1.4.3: Turn alternates Player → AI → Player → AI..."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Move 0 (even) - Player
        assert engine.get_current_state().get_current_player() == "X"
        engine.make_move(0, 0, "X")

        # Move 1 (odd) - AI
        assert engine.get_current_state().get_current_player() == "O"
        engine.make_move(0, 1, "O")

        # Move 2 (even) - Player
        assert engine.get_current_state().get_current_player() == "X"
        engine.make_move(0, 2, "X")

        # Move 3 (odd) - AI
        assert engine.get_current_state().get_current_player() == "O"
        engine.make_move(1, 0, "O")

        # Move 4 (even) - Player
        assert engine.get_current_state().get_current_player() == "X"

    def test_invalid_turn_error_when_wrong_player_moves(self) -> None:
        """AC-4.1.4.4: E_INVALID_TURN error if wrong player moves out of turn."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Move 0 - Player's turn, but AI tries to move
        success, error = engine.make_move(0, 0, "O")  # AI tries to move
        assert not success
        assert error == E_INVALID_TURN

    def test_invalid_turn_error_when_same_player_moves_twice(self) -> None:
        """AC-4.1.4.5: E_INVALID_TURN error if same player moves twice in a row."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Move 0 - Player moves
        engine.make_move(0, 0, "X")

        # Move 1 - Player tries to move again (should be AI's turn)
        success, error = engine.make_move(0, 1, "X")
        assert not success
        assert error == E_INVALID_TURN


class TestMoveNumberIncrement:
    """Test move number increments after each move."""

    def test_move_number_starts_at_zero(self) -> None:
        """AC-4.1.4.6: Move number starts at 0."""
        engine = GameEngine()
        assert engine.get_current_state().move_count == 0

    def test_move_number_increments_after_each_move(self) -> None:
        """AC-4.1.4.7: Move number increments by 1 after each move."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Initial state
        assert engine.get_current_state().move_count == 0

        # Move 1
        engine.make_move(0, 0, "X")
        assert engine.get_current_state().move_count == 1

        # Move 2
        engine.make_move(0, 1, "O")
        assert engine.get_current_state().move_count == 2

        # Move 3
        engine.make_move(0, 2, "X")
        assert engine.get_current_state().move_count == 3


class TestStateTransitions:
    """Test state transitions: IN_PROGRESS → WON or DRAW."""

    def test_game_starts_in_progress(self) -> None:
        """AC-4.1.4.8: Game starts in IN_PROGRESS state."""
        engine = GameEngine()
        state = engine.get_current_state()

        assert not state.is_game_over()
        assert state.get_winner() is None

    def test_transition_to_won_when_player_wins(self) -> None:
        """AC-4.1.4.8: State transitions to WON when a player wins."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Player wins top row
        engine.make_move(0, 0, "X")  # X at (0,0)
        engine.make_move(1, 0, "O")  # O at (1,0)
        engine.make_move(0, 1, "X")  # X at (0,1)
        engine.make_move(1, 1, "O")  # O at (1,1)
        engine.make_move(0, 2, "X")  # X at (0,2) - wins!

        state = engine.get_current_state()
        assert state.is_game_over()
        assert state.get_winner() == "X"
        assert not state._check_draw()

    def test_transition_to_draw_when_board_full_no_winner(self) -> None:
        """AC-4.1.4.8: State transitions to DRAW when board is full, no winner."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create a draw scenario - all 9 moves with proper turn order
        # X | O | X
        # X | O | O
        # O | X | X
        engine.make_move(0, 0, "X")  # Move 0 - Player
        engine.make_move(0, 1, "O")  # Move 1 - AI
        engine.make_move(0, 2, "X")  # Move 2 - Player
        engine.make_move(1, 1, "O")  # Move 3 - AI
        engine.make_move(1, 0, "X")  # Move 4 - Player
        engine.make_move(1, 2, "O")  # Move 5 - AI
        engine.make_move(2, 1, "X")  # Move 6 - Player
        engine.make_move(2, 0, "O")  # Move 7 - AI
        engine.make_move(2, 2, "X")  # Move 8 - Player - draw!

        state = engine.get_current_state()
        assert state.move_count == 9
        assert state.is_game_over()
        assert state.get_winner() == "DRAW"
        assert state._check_draw()

    def test_state_transitions_are_immutable(self) -> None:
        """AC-4.1.4.9: State transitions are immutable (cannot restart without reset)."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Player wins
        engine.make_move(0, 0, "X")
        engine.make_move(1, 0, "O")
        engine.make_move(0, 1, "X")
        engine.make_move(1, 1, "O")
        engine.make_move(0, 2, "X")  # X wins

        # Attempt to make another move should fail
        success, error = engine.make_move(2, 0, "O")
        assert not success
        assert error == E_GAME_ALREADY_OVER

        # Game state remains in terminal state
        state = engine.get_current_state()
        assert state.is_game_over()
        assert state.get_winner() == "X"

    def test_reset_game_returns_to_initial_state(self) -> None:
        """AC-4.1.4.9: reset() can return to initial state after game over."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Player wins
        engine.make_move(0, 0, "X")
        engine.make_move(1, 0, "O")
        engine.make_move(0, 1, "X")
        engine.make_move(1, 1, "O")
        engine.make_move(0, 2, "X")  # X wins

        # Reset game
        engine.reset_game()

        # Verify initial state restored
        state = engine.get_current_state()
        assert not state.is_game_over()
        assert state.get_winner() is None
        assert not state._check_draw()
        assert state.move_count == 0
        assert state.get_current_player() == "X"  # Player starts
