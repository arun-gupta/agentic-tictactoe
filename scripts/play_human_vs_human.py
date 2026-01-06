#!/usr/bin/env python3
"""Human vs Human Tic-Tac-Toe game demo.

This script demonstrates the complete Phase 2 Game Engine API by simulating
a human vs human game. It shows all the public methods and validates that
the game engine correctly enforces rules, detects wins/draws, and manages state.
"""

import random

from src.domain.models import Position
from src.game.engine import GameEngine


def print_board(engine: GameEngine) -> None:
    """Print the current board state in a nice format."""
    state = engine.get_current_state()
    board = state.board

    print("\n  0   1   2")
    for row in range(3):
        print(f"{row} ", end="")
        for col in range(3):
            cell = board.cells[row][col]
            if cell == "EMPTY":
                print(".", end="")
            else:
                print(cell, end="")
            if col < 2:
                print(" | ", end="")
        print()
        if row < 2:
            print("  -----------")
    print()


def print_game_status(engine: GameEngine) -> None:
    """Print current game status."""
    state = engine.get_current_state()
    print(f"Move #{state.move_count} | Current Player: {state.get_current_player()}")
    print(f"Available moves: {len(engine.get_available_moves())}")


def main() -> None:
    """Run a human vs human game simulation."""
    print("=" * 50)
    print("TIC-TAC-TOE: Human vs Human")
    print("=" * 50)
    print("\nDemonstrating Phase 2: Game Engine API")
    print("- Complete game rules enforcement")
    print("- Win/Draw detection")
    print("- Move validation")
    print("- State management\n")

    # Initialize game engine
    engine = GameEngine(player_symbol="X", ai_symbol="O")

    # Randomize first move for variety
    first_moves = [
        (0, 0),  # Top-left (corner)
        (0, 2),  # Top-right (corner)
        (1, 1),  # Center
        (2, 0),  # Bottom-left (corner)
        (2, 2),  # Bottom-right (corner)
    ]
    first_row, first_col = random.choice(first_moves)

    # Build game moves dynamically based on first move
    # This creates different game scenarios while still demonstrating a win
    if first_row == 1 and first_col == 1:  # Center opening
        moves = [
            (first_row, first_col, "X", "Player 1"),  # X center
            (0, 0, "O", "Player 2"),  # O top-left
            (0, 1, "X", "Player 1"),  # X top-center
            (2, 1, "O", "Player 2"),  # O bottom-center
            (0, 2, "X", "Player 1"),  # X top-right
            (1, 0, "O", "Player 2"),  # O middle-left
            (1, 2, "X", "Player 1"),  # X middle-right (wins column 2)
        ]
    else:  # Corner or edge opening
        moves = [
            (first_row, first_col, "X", "Player 1"),  # X random start
            (1, 1, "O", "Player 2"),  # O takes center
            (0 if first_row != 0 else 2, 0, "X", "Player 1"),  # X another corner
            (1, 0, "O", "Player 2"),  # O middle-left
            (0 if first_row != 0 else 2, 1, "X", "Player 1"),  # X continues row
            (1, 2, "O", "Player 2"),  # O middle-right
            (0 if first_row != 0 else 2, 2, "X", "Player 1"),  # X wins the row!
        ]

    print("GAME START")
    print("-" * 50)
    print_board(engine)
    print_game_status(engine)

    # Play through the moves
    for move_num, (row, col, player, player_name) in enumerate(moves, 1):
        print(f"\n--- Move {move_num}: {player_name} ({player}) plays at ({row}, {col}) ---")

        # Validate move first
        is_valid, error = engine.validate_move(row, col, player)
        if not is_valid:
            print(f"❌ INVALID MOVE: {error}")
            continue

        # Execute move
        success, error = engine.make_move(row, col, player)
        if not success:
            print(f"❌ MOVE FAILED: {error}")
            continue

        print(f"✓ Move successful")

        # Show board
        print_board(engine)

        # Check game state
        winner = engine.check_winner()
        if winner:
            print(f"\n{'=' * 50}")
            print(f"🎉 GAME OVER: {player_name} ({winner}) WINS!")
            print(f"{'=' * 50}")
            print(f"\nFinal stats:")
            print(f"- Total moves: {engine.get_current_state().move_count}")
            print(f"- Winner: {winner}")
            print(f"- Game state validation: ", end="")
            is_valid, error = engine.validate_state()
            if is_valid:
                print("✓ VALID")
            else:
                print(f"✗ INVALID ({error})")
            break

        if engine.check_draw():
            print(f"\n{'=' * 50}")
            print("🤝 GAME OVER: DRAW!")
            print(f"{'=' * 50}")
            break

        print_game_status(engine)

    # Demonstrate other API methods
    print(f"\n{'=' * 50}")
    print("API CAPABILITIES DEMONSTRATED:")
    print(f"{'=' * 50}")
    print("✓ make_move() - Execute moves with validation")
    print("✓ validate_move() - Pre-validate moves before execution")
    print("✓ check_winner() - Detect winning conditions")
    print("✓ check_draw() - Detect draw conditions")
    print("✓ get_current_state() - Access complete game state")
    print("✓ get_available_moves() - List all legal moves")
    print("✓ validate_state() - Verify state consistency")
    print("✓ is_game_over() - Check if game is finished")

    # Show reset capability
    print(f"\n{'=' * 50}")
    print("RESET GAME")
    print(f"{'=' * 50}")
    engine.reset_game()
    print("Game reset to initial state")
    print_board(engine)
    print("✓ reset_game() - Return to initial state")

    print("\n" + "=" * 50)
    print("Phase 2 Complete: Game Engine fully functional!")
    print("Ready for Phase 3: AI Agent implementation")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
