#!/usr/bin/env python3
"""Play Tic-Tac-Toe via REST API demo.

This script demonstrates Phase 4 REST API by playing a complete game via HTTP requests.
It shows all API endpoints and displays the game board from API responses.
Human vs AI gameplay through the REST API.
"""

import json
import subprocess
import sys
import time
from typing import Any

import httpx

# API base URL (default: http://localhost:8000)
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30.0  # 30 seconds timeout for API requests


def print_board(board_data: list[list[str | None]] | dict[str, Any]) -> None:
    """Print the current board state from API response.

    Args:
        board_data: Board data from API response - either a 2D array or dict with cells
    """
    # Handle both formats: direct 2D array or dict with "cells" key
    if isinstance(board_data, list):
        cells = board_data
    else:
        cells = board_data.get("cells", [])

    print("\n  0   1   2")
    for row in range(3):
        print(f"{row} ", end="")
        for col in range(3):
            cell = cells[row][col] if row < len(cells) and col < len(cells[row]) else None
            if cell is None:
                print(".", end="")
            else:
                print(cell, end="")
            if col < 2:
                print(" | ", end="")
        print()
        if row < 2:
            print("  -----------")
    print()


def print_game_status(game_state: dict[str, Any]) -> None:
    """Print current game status from API response.

    Args:
        game_state: GameState data from API response
    """
    move_count = game_state.get("move_count", 0)
    player_symbol = game_state.get("player_symbol", "X")
    ai_symbol = game_state.get("ai_symbol", "O")
    is_game_over = game_state.get("is_game_over", False)
    winner = game_state.get("winner")

    print(f"Move #{move_count} | Player: {player_symbol} | AI: {ai_symbol}")
    if is_game_over:
        if winner:
            print(f"🎉 Game Over! Winner: {winner}")
        else:
            print("🤝 Game Over! Draw")
    print()


def check_server_health(client: httpx.Client) -> bool:
    """Check if the API server is running and healthy.

    Args:
        client: HTTP client instance

    Returns:
        True if server is healthy, False otherwise
    """
    try:
        response = client.get(f"{API_BASE_URL}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy (uptime: {data.get('uptime_seconds', 0):.2f}s)")
            return True
        else:
            print(f"⚠️  Server returned status {response.status_code}")
            return False
    except httpx.ConnectError:
        print(f"❌ Cannot connect to API server at {API_BASE_URL}")
        print(f"   Please start the server with: uvicorn src.api.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error checking server health: {e}")
        return False


def check_server_ready(client: httpx.Client) -> bool:
    """Check if the API server is ready to accept requests.

    Args:
        client: HTTP client instance

    Returns:
        True if server is ready, False otherwise
    """
    try:
        response = client.get(f"{API_BASE_URL}/ready", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ready":
                print("✅ Server is ready")
                return True
            else:
                print(f"⚠️  Server is not ready: {data.get('status')}")
                return False
        else:
            print(f"⚠️  Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking server readiness: {e}")
        return False


def create_new_game(client: httpx.Client) -> str | None:
    """Create a new game via API.

    Args:
        client: HTTP client instance

    Returns:
        Game ID if successful, None otherwise
    """
    print("\n--- Creating new game (POST /api/game/new) ---")
    try:
        response = client.post(f"{API_BASE_URL}/api/game/new", timeout=API_TIMEOUT)
        if response.status_code == 201:
            data = response.json()
            game_id = data.get("game_id")
            game_state = data.get("game_state", {})
            print(f"✅ Game created! Game ID: {game_id}")
            print_board(game_state.get("board", {}))
            print_game_status(game_state)
            return game_id
        else:
            print(f"❌ Failed to create game: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Error creating game: {e}")
        return None


def make_move(client: httpx.Client, game_id: str, row: int, col: int) -> dict[str, Any] | None:
    """Make a player move via API.

    Args:
        client: HTTP client instance
        game_id: Game ID
        row: Row index (0-2)
        col: Column index (0-2)

    Returns:
        Move response data if successful, None otherwise
    """
    print(f"\n--- Making move at ({row}, {col}) (POST /api/game/move) ---")
    try:
        payload = {"game_id": game_id, "row": row, "col": col}
        response = client.post(
            f"{API_BASE_URL}/api/game/move", json=payload, timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Move successful!")
            updated_state = data.get("updated_game_state", {})
            print_board(updated_state.get("board", {}))
            print_game_status(updated_state)

            # Show AI move execution details if available
            ai_execution = data.get("ai_move_execution")
            if ai_execution:
                position = ai_execution.get("position")
                if position:
                    print(f"🤖 AI played at ({position.get('row')}, {position.get('col')})")
                if ai_execution.get("reasoning"):
                    print(f"   Reasoning: {ai_execution['reasoning']}")
                exec_time = ai_execution.get("execution_time_ms", 0)
                if exec_time:
                    print(f"   Execution time: {exec_time:.2f}ms")

            return data
        else:
            print(f"❌ Move failed: {response.status_code}")
            error_data = response.json()
            error_code = error_data.get("error_code", "UNKNOWN")
            error_message = error_data.get("message", "Unknown error")
            print(f"   Error Code: {error_code}")
            print(f"   Message: {error_message}")
            if error_data.get("details"):
                print(f"   Details: {json.dumps(error_data['details'], indent=2)}")
            return None
    except Exception as e:
        print(f"❌ Error making move: {e}")
        return None


def get_game_status(client: httpx.Client, game_id: str) -> dict[str, Any] | None:
    """Get current game status via API.

    Args:
        client: HTTP client instance
        game_id: Game ID

    Returns:
        Game status data if successful, None otherwise
    """
    print(f"\n--- Getting game status (GET /api/game/status?game_id={game_id}) ---")
    try:
        response = client.get(
            f"{API_BASE_URL}/api/game/status", params={"game_id": game_id}, timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            game_state = data.get("game_state", {})
            print_board(game_state.get("board", {}))
            print_game_status(game_state)

            # Show agent status if available
            agent_status = data.get("agent_status")
            if agent_status:
                print("Agent Status:")
                for agent_name, status_data in agent_status.items():
                    status = status_data.get("status", "unknown")
                    print(f"  - {agent_name}: {status}")

            # Show metrics if game is over
            metrics = data.get("metrics")
            if metrics:
                print("\nGame Metrics:")
                print(json.dumps(metrics, indent=2))

            return data
        else:
            print(f"❌ Failed to get game status: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Error getting game status: {e}")
        return None


def reset_game(client: httpx.Client, game_id: str) -> dict[str, Any] | None:
    """Reset game via API.

    Args:
        client: HTTP client instance
        game_id: Game ID

    Returns:
        Reset response data if successful, None otherwise
    """
    print(f"\n--- Resetting game (POST /api/game/reset) ---")
    try:
        payload = {"game_id": game_id}
        response = client.post(
            f"{API_BASE_URL}/api/game/reset", json=payload, timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            game_state = data.get("game_state", {})
            print("✅ Game reset!")
            print_board(game_state.get("board", {}))
            print_game_status(game_state)
            return data
        else:
            print(f"❌ Failed to reset game: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Error resetting game: {e}")
        return None


def get_human_move() -> tuple[int, int] | None:
    """Get move from human player via input.

    Returns:
        Tuple of (row, col) if valid, None if quit
    """
    print("\nYour turn! Enter row and column (0-2), or 'q' to quit:")
    while True:
        try:
            user_input = input("Enter move (row,col or 'q'): ").strip().lower()
            if user_input == "q":
                return None

            parts = user_input.split(",")
            if len(parts) != 2:
                print("Invalid format. Use: row,col (e.g., 0,1)")
                continue

            row = int(parts[0].strip())
            col = int(parts[1].strip())

            if not (0 <= row <= 2 and 0 <= col <= 2):
                print("Row and column must be between 0 and 2")
                continue

            return (row, col)
        except ValueError:
            print("Invalid input. Enter two numbers separated by comma (e.g., 0,1)")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None


def main() -> None:
    """Run the API demo."""
    print("=" * 60)
    print("TIC-TAC-TOE: Human vs AI via REST API")
    print("=" * 60)
    print("\nDemonstrating Phase 4: REST API Layer")
    print("- Complete game via HTTP requests")
    print("- All API endpoints")
    print("- Game state management")
    print("- Human vs AI gameplay\n")

    # Create HTTP client
    with httpx.Client() as client:
        # Check server health and readiness
        if not check_server_health(client):
            sys.exit(1)

        if not check_server_ready(client):
            print("⚠️  Server is not ready, but continuing anyway...")

        # Create new game
        game_id = create_new_game(client)
        if not game_id:
            print("❌ Failed to create game. Exiting.")
            sys.exit(1)

        # Play game interactively
        print("\n" + "=" * 60)
        print("PLAYING GAME")
        print("=" * 60)
        print("Make moves by entering row,col (e.g., 0,1)")
        print("Enter 'q' to quit\n")

        while True:
            # Get player move
            move = get_human_move()
            if move is None:
                break

            row, col = move
            result = make_move(client, game_id, row, col)

            if result:
                updated_state = result.get("updated_game_state", {})
                if updated_state.get("is_game_over"):
                    winner = updated_state.get("winner")
                    if winner:
                        print(f"\n🎉 Game Over! Winner: {winner}")
                    else:
                        print("\n🤝 Game Over! Draw")
                    break

        # Show final status
        print("\n" + "=" * 60)
        print("FINAL GAME STATUS")
        print("=" * 60)
        get_game_status(client, game_id)

    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main()
