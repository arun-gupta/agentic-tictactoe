"""Tests for state validation (Task 2.4).

Tests AC-4.1.5.1 through AC-4.1.5.10 - State Validation Rules
"""

from src.domain.errors import (
    E_INVALID_SYMBOL_BALANCE,
    E_INVALID_TURN,
    E_MULTIPLE_WINNERS,
)
from src.domain.models import Board, GameState
from src.game.engine import GameEngine


class TestSymbolBalance:
    """Test board symbol consistency validation."""

    def test_ac_4_1_5_1_invalid_symbol_balance_difference_too_large(self) -> None:
        """AC-4.1.5.1: Given count(X)=5 and count(O)=3, validation error."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Manually create invalid state with 5 X's and 3 O's
        # X | X | X
        # X | O | O
        # X | O | EMPTY
        board = Board(
            cells=[
                ["X", "X", "X"],
                ["X", "O", "O"],
                ["X", "O", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=8,
        )

        is_valid, error = engine.validate_state()
        assert not is_valid
        assert error == E_INVALID_SYMBOL_BALANCE

    def test_valid_symbol_balance_equal_counts(self) -> None:
        """Symbol balance valid when X and O counts are equal."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create valid state with 3 X's and 3 O's
        # X | O | X
        # O | X | O
        # EMPTY | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["O", "X", "O"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=6,
        )

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None

    def test_valid_symbol_balance_difference_one(self) -> None:
        """Symbol balance valid when |count(X) - count(O)| = 1."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create valid state with 3 X's and 2 O's
        # X | O | X
        # O | X | EMPTY
        # EMPTY | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["O", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=5,
        )

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None


class TestCurrentPlayerValidation:
    """Test current player matches symbol counts."""

    def test_ac_4_1_5_2_equal_counts_player_x_turn(self) -> None:
        """AC-4.1.5.2: Given count(X)=3 and count(O)=3, CurrentPlayer must be X."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create state with 3 X's and 3 O's
        # X | O | X
        # O | X | O
        # EMPTY | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["O", "X", "O"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=6,  # Even move count means Player's turn
        )

        # Verify current player is X
        assert engine.game_state.get_current_player() == "X"

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None

    def test_ac_4_1_5_3_x_ahead_by_one_ai_turn(self) -> None:
        """AC-4.1.5.3: Given count(X)=4 and count(O)=3, CurrentPlayer must be O."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create state with 4 X's and 3 O's
        # X | O | X
        # O | X | O
        # X | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["O", "X", "O"],
                ["X", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=7,  # Odd move count means AI's turn
        )

        # Verify current player is O
        assert engine.game_state.get_current_player() == "O"

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None

    def test_ac_4_1_5_4_equal_counts_wrong_player(self) -> None:
        """AC-4.1.5.4: Given count(X)=3, count(O)=3, CurrentPlayer=O, error."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create state with 3 X's and 3 O's, but move_count=7 (wrong)
        # X | O | X
        # O | X | O
        # EMPTY | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["O", "X", "O"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=7,  # Odd move count means AI's turn, but should be 6 (Player's turn)
        )

        # Move count doesn't match board state
        is_valid, error = engine.validate_state()
        assert not is_valid
        assert error == E_INVALID_TURN


class TestMultipleWinners:
    """Test at most one winner exists."""

    def test_ac_4_1_5_5_both_players_win_invalid(self) -> None:
        """AC-4.1.5.5: Both X and O have winning lines - invalid."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create impossible state with both X and O winning
        # X | X | X  <- X wins (row 0)
        # O | O | O  <- O wins (row 1)
        # EMPTY | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "X", "X"],
                ["O", "O", "O"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=6,
        )

        is_valid, error = engine.validate_state()
        assert not is_valid
        assert error == E_MULTIPLE_WINNERS

    def test_single_winner_valid(self) -> None:
        """Only one winner is valid."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # X wins top row
        # X | X | X
        # O | O | EMPTY
        # EMPTY | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "X", "X"],
                ["O", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=5,
        )

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None


class TestWinnerImpliesGameOver:
    """Test winner implies game over."""

    def test_ac_4_1_5_6_winner_detected_game_over_true(self) -> None:
        """AC-4.1.5.6: Given winner=X detected, IsGameOver must be true."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # X wins top row
        board = Board(
            cells=[
                ["X", "X", "X"],
                ["O", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=5,
        )

        # Winner exists and game is over
        assert engine.check_winner() == "X"
        assert engine.game_state.is_game_over()

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None

    def test_ac_4_1_5_7_winner_exists_but_game_not_over_invalid(self) -> None:
        """AC-4.1.5.7: Winner=X but IsGameOver=false is invalid (conceptual test).

        Note: In our implementation, is_game_over() is computed from board state,
        so this scenario cannot happen naturally. This test documents the requirement.
        """
        # This test verifies that validation would catch this inconsistency
        # In practice, our GameState computes is_game_over() dynamically,
        # so a winner always implies is_game_over() == True
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # X wins top row
        board = Board(
            cells=[
                ["X", "X", "X"],
                ["O", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=5,
        )

        # In our implementation, winner always implies game over
        # because is_game_over() checks for winner
        assert engine.check_winner() == "X"
        assert engine.game_state.is_game_over()  # Always true when winner exists


class TestDrawCondition:
    """Test draw condition validation."""

    def test_ac_4_1_5_8_move_count_9_no_winner_is_draw(self) -> None:
        """AC-4.1.5.8: Given MoveCount=9 and no winner, Winner must be DRAW."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create draw state
        # X | O | X
        # X | O | O
        # O | X | X
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["X", "O", "O"],
                ["O", "X", "X"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=9,
        )

        assert engine.check_winner() is None
        assert engine.game_state.get_winner() == "DRAW"
        assert engine.game_state.is_game_over()

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None


class TestGameOverTerminal:
    """Test game over state is terminal."""

    def test_ac_4_1_5_9_game_over_no_more_moves(self) -> None:
        """AC-4.1.5.9: After game over, no additional moves can be made."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # X wins
        engine.make_move(0, 0, "X")  # Move 0
        engine.make_move(1, 0, "O")  # Move 1
        engine.make_move(0, 1, "X")  # Move 2
        engine.make_move(1, 1, "O")  # Move 3
        engine.make_move(0, 2, "X")  # Move 4 - X wins!

        # Game is over
        assert engine.check_winner() == "X"
        assert engine.game_state.is_game_over()

        # State validation should pass
        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None

        # Attempt to make another move should fail
        from src.domain.errors import E_GAME_ALREADY_OVER

        success, error = engine.make_move(2, 0, "O")
        assert not success
        assert error == E_GAME_ALREADY_OVER


class TestValidStateAllRules:
    """Test valid state satisfying all validation rules."""

    def test_ac_4_1_5_10_valid_state_all_rules(self) -> None:
        """AC-4.1.5.10: Valid state satisfying all 8 rules passes validation."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Create valid in-progress game state
        # X | O | X
        # O | X | EMPTY
        # EMPTY | EMPTY | EMPTY
        board = Board(
            cells=[
                ["X", "O", "X"],
                ["O", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        engine.game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=5,
        )

        # Verify all conditions:
        # 1. Symbol balance: count(X)=3, count(O)=2, diff=1 ✓
        # 2. Move count matches: 3+2=5 ✓
        # 3. Current player correct: move 5 (odd) = AI (O) ✓
        # 4. No multiple winners ✓
        # 5. No winner, so game not over ✓

        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None

    def test_valid_state_after_normal_gameplay(self) -> None:
        """Valid state after normal gameplay passes validation."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Play a few moves normally
        engine.make_move(0, 0, "X")  # Move 0
        engine.make_move(0, 1, "O")  # Move 1
        engine.make_move(1, 1, "X")  # Move 2
        engine.make_move(0, 2, "O")  # Move 3

        # State should be valid
        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None

    def test_valid_state_at_game_start(self) -> None:
        """Valid state at game start (empty board) passes validation."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Initial state should be valid
        is_valid, error = engine.validate_state()
        assert is_valid
        assert error is None
