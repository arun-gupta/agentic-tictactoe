"""Game engine for Tic-Tac-Toe.

This module implements the game engine with win condition detection, move validation,
and state management as per Section 4.1 of the spec.
"""

# Error codes will be used in later phases for move validation
from src.domain.models import Board, GameState, PlayerSymbol


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

    def get_current_state(self) -> GameState:
        """Get the current game state.

        Returns:
            Complete GameState domain model with all properties
        """
        return self.game_state
