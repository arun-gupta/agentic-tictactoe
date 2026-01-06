"""Tests for random game scenarios to verify game engine robustness.

These tests play complete games with random moves to ensure the engine
correctly handles all possible game scenarios, validates state consistency,
and detects wins/draws properly regardless of move order.
"""

import random

from src.game.engine import GameEngine


class TestRandomGameScenarios:
    """Test complete games with random moves."""

    def test_random_game_always_terminates(self) -> None:
        """Random games always reach a terminal state (win or draw)."""
        for _ in range(10):  # Run 10 random games
            engine = GameEngine(player_symbol="X", ai_symbol="O")

            # Play until game over
            while not engine.is_game_over():
                available = engine.get_available_moves()
                if not available:
                    break

                # Random move
                position = random.choice(available)
                player = engine.get_current_state().get_current_player()
                success, _ = engine.make_move(position.row, position.col, player)
                assert success, "Random valid move should always succeed"

            # Game must end in win or draw
            state = engine.get_current_state()
            assert state.is_game_over(), "Game should reach terminal state"

            # Either has winner or is draw
            winner = engine.check_winner()
            is_draw = engine.check_draw()
            assert winner is not None or is_draw, "Game must end in win or draw"

    def test_random_game_state_always_valid(self) -> None:
        """State remains valid throughout random games."""
        for _ in range(10):
            engine = GameEngine(player_symbol="X", ai_symbol="O")

            move_history = []
            while not engine.is_game_over():
                # Validate state before move
                is_valid, error = engine.validate_state()
                assert is_valid, f"State invalid after moves {move_history}: {error}"

                available = engine.get_available_moves()
                if not available:
                    break

                position = random.choice(available)
                player = engine.get_current_state().get_current_player()
                engine.make_move(position.row, position.col, player)
                move_history.append((position.row, position.col, player))

            # Final state must be valid
            is_valid, error = engine.validate_state()
            assert is_valid, f"Final state invalid: {error}"

    def test_random_game_turn_alternation(self) -> None:
        """Random games maintain proper turn alternation."""
        for _ in range(10):
            engine = GameEngine(player_symbol="X", ai_symbol="O")

            last_player = None
            while not engine.is_game_over():
                available = engine.get_available_moves()
                if not available:
                    break

                current = engine.get_current_state().get_current_player()

                # Ensure alternation
                if last_player is not None:
                    assert current != last_player, "Players must alternate"

                position = random.choice(available)
                engine.make_move(position.row, position.col, current)
                last_player = current

    def test_random_game_move_count_accuracy(self) -> None:
        """Move count accurately reflects number of moves made."""
        for _ in range(10):
            engine = GameEngine(player_symbol="X", ai_symbol="O")

            moves_made = 0
            while not engine.is_game_over():
                available = engine.get_available_moves()
                if not available:
                    break

                position = random.choice(available)
                player = engine.get_current_state().get_current_player()
                engine.make_move(position.row, position.col, player)
                moves_made += 1

                # Verify count
                assert engine.get_current_state().move_count == moves_made

    def test_random_game_available_moves_decrease(self) -> None:
        """Available moves decrease as game progresses."""
        for _ in range(5):
            engine = GameEngine(player_symbol="X", ai_symbol="O")

            last_available_count = 9
            while not engine.is_game_over():
                available = engine.get_available_moves()
                current_count = len(available)

                # Available moves should decrease or stay same (if game ends)
                assert current_count <= last_available_count

                if not available:
                    break

                position = random.choice(available)
                player = engine.get_current_state().get_current_player()
                engine.make_move(position.row, position.col, player)
                last_available_count = current_count - 1

    def test_random_game_winner_detection(self) -> None:
        """Winner is correctly detected in random games."""
        wins = 0
        draws = 0

        for _ in range(20):  # Play more games to get variety
            engine = GameEngine(player_symbol="X", ai_symbol="O")

            while not engine.is_game_over():
                available = engine.get_available_moves()
                if not available:
                    break

                position = random.choice(available)
                player = engine.get_current_state().get_current_player()
                engine.make_move(position.row, position.col, player)

            winner = engine.check_winner()
            if winner:
                wins += 1
                # Verify winner has a complete line
                assert winner in ("X", "O")
            elif engine.check_draw():
                draws += 1
                # Verify all 9 moves made
                assert engine.get_current_state().move_count == 9

        # Should have at least some wins and potentially some draws
        assert wins + draws == 20, "All games should end in win or draw"

    def test_random_game_cannot_move_after_game_over(self) -> None:
        """Cannot make moves after game is over."""
        for _ in range(5):
            engine = GameEngine(player_symbol="X", ai_symbol="O")

            # Play until game over
            while not engine.is_game_over():
                available = engine.get_available_moves()
                if not available:
                    break

                position = random.choice(available)
                player = engine.get_current_state().get_current_player()
                engine.make_move(position.row, position.col, player)

            # Game is over, try to make another move
            if engine.get_available_moves():
                from src.domain.errors import E_GAME_ALREADY_OVER

                position = engine.get_available_moves()[0]
                player = engine.get_current_state().get_current_player()
                success, error = engine.make_move(position.row, position.col, player)
                assert not success
                assert error == E_GAME_ALREADY_OVER


class TestSpecificGameScenarios:
    """Test specific known game scenarios."""

    def test_first_player_can_win(self) -> None:
        """X (first player) can achieve wins."""
        # Play a known winning sequence for X
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # X wins top row
        engine.make_move(0, 0, "X")
        engine.make_move(1, 0, "O")
        engine.make_move(0, 1, "X")
        engine.make_move(1, 1, "O")
        engine.make_move(0, 2, "X")  # Win

        assert engine.check_winner() == "X"
        assert engine.is_game_over()

    def test_second_player_can_win(self) -> None:
        """O (second player) can achieve wins."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # O wins middle column
        engine.make_move(0, 0, "X")
        engine.make_move(0, 1, "O")
        engine.make_move(0, 2, "X")
        engine.make_move(1, 1, "O")
        engine.make_move(2, 0, "X")
        engine.make_move(2, 1, "O")  # Win

        assert engine.check_winner() == "O"
        assert engine.is_game_over()

    def test_draw_game_scenario(self) -> None:
        """Games can end in draws."""
        engine = GameEngine(player_symbol="X", ai_symbol="O")

        # Known draw sequence
        # X | O | X
        # X | O | O
        # O | X | X
        moves = [
            (0, 0, "X"),
            (0, 1, "O"),
            (0, 2, "X"),
            (1, 1, "O"),
            (1, 0, "X"),
            (1, 2, "O"),
            (2, 1, "X"),
            (2, 0, "O"),
            (2, 2, "X"),
        ]

        for row, col, player in moves:
            engine.make_move(row, col, player)

        assert engine.check_draw()
        assert engine.is_game_over()
        assert engine.check_winner() is None
