"""Game engine for Tic-Tac-Toe.

This module implements the game engine with win condition detection, move validation,
and state management as per Section 4.1 of the spec.
"""

# Error codes will be used in later phases for move validation
from src.domain.models import Board, GameState, PlayerSymbol, Position


class GameEngine:
    """Game engine that manages game rules and state."""

    def __init__(self, player_symbol: PlayerSymbol = "X", ai_symbol: PlayerSymbol = "O"):
        """Initialize the game engine.

        Args:
            player_symbol: Symbol for the human player (default: 'X')
            ai_symbol: Symbol for the AI player (default: 'O')
        """
        self.player_symbol = player_symbol
        self.ai_symbol = ai_symbol
        self.game_state = GameState(
            board=Board(),
            player_symbol=player_symbol,
            ai_symbol=ai_symbol,
        )

    def check_winner(self) -> PlayerSymbol | None:
        """Check for a winner on the board.

        Checks all 8 winning lines (3 rows, 3 columns, 2 diagonals) for three
        matching symbols. MUST check all lines after each move per spec.

        Returns:
            Winner symbol ('X' or 'O') if there is a winner, None otherwise
        """
        return self.game_state._check_win()

    def reset_game(self) -> None:
        """Reset the game to initial conditions.

        Clears the board and resets the game state.
        """
        self.game_state = GameState(
            board=Board(),
            player_symbol=self.player_symbol,
            ai_symbol=self.ai_symbol,
        )

    def check_draw(self) -> bool:
        """Check if the game is a draw.

        Implements both mandatory complete draw detection (MoveCount=9, no winner)
        and optional inevitable draw detection (no winning moves remain).

        Returns:
            True if the game is a draw, False otherwise
        """
        # Mandatory: Complete draw (MoveCount=9, no winner)
        if self.game_state.move_count == 9:
            return self.check_winner() is None

        # Optional: Inevitable draw detection (MoveCount >= 7)
        if self.game_state.move_count >= 7:
            return self._check_inevitable_draw()

        return False

    def _check_inevitable_draw(self) -> bool:
        """Check for inevitable draw by simulating all remaining moves.

        Algorithm (per spec Section 4.1):
        For each empty cell, simulate placing both player symbols and check
        if either can create a winning line. If no empty cell allows either
        player to win, declare inevitable draw.

        Returns:
            True if no winning moves remain for either player, False otherwise
        """
        board = self.game_state.board
        empty_positions = board.get_empty_positions()

        # If no empty positions, use complete draw check
        if not empty_positions:
            return self.check_winner() is None

        current_player = self.game_state.get_current_player()
        opponent = self.game_state.get_opponent()

        # Check each empty cell to see if either player can win from it
        for pos in empty_positions:
            # Try current player's symbol at this position
            if self._can_win_from_position(board, pos, current_player):
                return False

            # Try opponent's symbol at this position
            if self._can_win_from_position(board, pos, opponent):
                return False

        # No winning moves remain for either player - inevitable draw
        return True

    def _can_win_from_position(
        self, board: Board, position: Position, symbol: PlayerSymbol
    ) -> bool:
        """Check if placing a symbol at a position creates a winning line.

        This is a simulation - it does not modify the actual board.

        Args:
            board: The current board state
            position: The position to check
            symbol: The symbol to place ('X' or 'O')

        Returns:
            True if placing this symbol at this position creates a winning line
        """
        # Create a temporary copy of cells to simulate the move
        temp_cells = [row[:] for row in board.cells]
        temp_cells[position.row][position.col] = symbol

        # Check all 8 winning lines for three matching symbols
        # Check rows
        for row in range(3):
            if (
                temp_cells[row][0] != "EMPTY"
                and temp_cells[row][0] == temp_cells[row][1]
                and temp_cells[row][1] == temp_cells[row][2]
            ):
                return True

        # Check columns
        for col in range(3):
            if (
                temp_cells[0][col] != "EMPTY"
                and temp_cells[0][col] == temp_cells[1][col]
                and temp_cells[1][col] == temp_cells[2][col]
            ):
                return True

        # Check main diagonal (0,0), (1,1), (2,2)
        if (
            temp_cells[0][0] != "EMPTY"
            and temp_cells[0][0] == temp_cells[1][1]
            and temp_cells[1][1] == temp_cells[2][2]
        ):
            return True

        # Check anti-diagonal (0,2), (1,1), (2,0)
        if (
            temp_cells[0][2] != "EMPTY"
            and temp_cells[0][2] == temp_cells[1][1]
            and temp_cells[1][1] == temp_cells[2][0]
        ):
            return True

        return False

    def get_current_state(self) -> GameState:
        """Get the current game state.

        Returns:
            Complete GameState domain model with all properties
        """
        return self.game_state
