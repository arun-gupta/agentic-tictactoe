"""Game engine for Tic-Tac-Toe.

This module implements the game engine with win condition detection, move validation,
and state management as per Section 4.1 of the spec.
"""

from src.domain.errors import (
    E_CELL_OCCUPIED,
    E_GAME_ALREADY_OVER,
    E_INVALID_PLAYER,
    E_INVALID_SYMBOL_BALANCE,
    E_INVALID_TURN,
    E_MOVE_OUT_OF_BOUNDS,
    E_MULTIPLE_WINNERS,
    E_WIN_NOT_FINALIZED,
)
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

    def validate_move(self, row: int, col: int, player: PlayerSymbol) -> tuple[bool, str | None]:
        """Validate a move before execution.

        Validates all move conditions per spec Section 4.1 - Illegal Move Conditions.
        Checks: position bounds, cell empty, game not over, valid player symbol, correct turn.

        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            player: The player symbol making the move ('X' or 'O')

        Returns:
            Tuple of (is_valid, error_code). If valid, returns (True, None).
            If invalid, returns (False, error_code).
        """
        # Check 1: Position bounds (0-2 for both row and col)
        if not (0 <= row <= 2) or not (0 <= col <= 2):
            return (False, E_MOVE_OUT_OF_BOUNDS)

        # Create Position for remaining checks (now safe to create)
        try:
            position = Position(row=row, col=col)
        except Exception:
            # This shouldn't happen after bounds check, but handle it
            return (False, E_MOVE_OUT_OF_BOUNDS)

        # Check 2: Cell is empty
        if not self.game_state.board.is_empty(position):
            return (False, E_CELL_OCCUPIED)

        # Check 3: Game is not over
        if self.game_state.is_game_over():
            return (False, E_GAME_ALREADY_OVER)

        # Check 4: Valid player symbol (X or O)
        if player not in ("X", "O"):
            return (False, E_INVALID_PLAYER)

        # Check 5: Correct turn (player must match current player)
        current_player = self.game_state.get_current_player()
        if player != current_player:
            return (False, E_INVALID_TURN)

        # All checks passed - move is legal
        return (True, None)

    def get_current_state(self) -> GameState:
        """Get the current game state.

        Returns:
            Complete GameState domain model with all properties
        """
        return self.game_state

    def make_move(self, row: int, col: int, player: PlayerSymbol) -> tuple[bool, str | None]:
        """Execute a move on the board.

        Validates the move, executes it if valid, updates game state including turn
        and state transitions. Turn alternates: Player (even moves) → AI (odd moves).
        State transitions: IN_PROGRESS → WON or DRAW. Transitions are immutable.

        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            player: The player symbol making the move ('X' or 'O')

        Returns:
            Tuple of (success, error_code). If successful, returns (True, None).
            If failed, returns (False, error_code).
        """
        # Validate the move first
        is_valid, error_code = self.validate_move(row, col, player)
        if not is_valid:
            return (False, error_code)

        # Execute the move
        position = Position(row=row, col=col)
        self.game_state.board.set_cell(position, player)

        # Increment move count
        self.game_state.move_count += 1

        # Note: Game over status and winner are computed on-the-fly by GameState methods
        # (_check_win(), _check_draw(), is_game_over(), get_winner())
        # No need to set explicit flags - the state is determined by the board state

        return (True, None)

    def is_game_over(self) -> bool:
        """Check if the game is over.

        Returns:
            True if the game is over (win or draw), False otherwise
        """
        return self.game_state.is_game_over()

    def validate_state(self) -> tuple[bool, str | None]:
        """Validate the current game state consistency.

        Validates state consistency per spec Section 4.1 - State Validation Rules:
        1. Board symbol consistency (|count(X) - count(O)| <= 1)
        2. Move count matches board state
        3. Current player matches symbol counts
        4. At most one winner exists
        5. Winner implies game over
        6. Game over state is terminal

        Returns:
            Tuple of (is_valid, error_code). If valid, returns (True, None).
            If invalid, returns (False, error_code).
        """
        board = self.game_state.board

        # Count X and O symbols on the board
        count_x = 0
        count_o = 0
        for row in range(3):
            for col in range(3):
                cell = board.cells[row][col]
                if cell == "X":
                    count_x += 1
                elif cell == "O":
                    count_o += 1

        # Rule 1: Symbol balance (|count(X) - count(O)| <= 1)
        symbol_diff = abs(count_x - count_o)
        if symbol_diff > 1:
            return (False, E_INVALID_SYMBOL_BALANCE)

        # Rule 2: Move count matches board state
        total_moves = count_x + count_o
        if self.game_state.move_count != total_moves:
            return (False, E_INVALID_TURN)

        # Rule 3: Current player matches symbol counts
        # If counts are equal, Player (X) should be next
        # If X has one more, AI (O) should be next
        current_player = self.game_state.get_current_player()
        if count_x == count_o:
            # Even number of moves, Player's turn
            if current_player != self.player_symbol:
                return (False, E_INVALID_TURN)
        elif count_x == count_o + 1:
            # Odd number of moves, AI's turn
            if current_player != self.ai_symbol:
                return (False, E_INVALID_TURN)
        else:
            # Invalid balance already caught above
            return (False, E_INVALID_SYMBOL_BALANCE)

        # Rule 4: At most one winner exists
        # Check if both X and O have winning lines
        x_wins = self._has_winning_line("X")
        o_wins = self._has_winning_line("O")
        if x_wins and o_wins:
            return (False, E_MULTIPLE_WINNERS)

        # Rule 5: Winner implies game over
        winner = self.check_winner()
        if winner is not None:
            if not self.game_state.is_game_over():
                return (False, E_WIN_NOT_FINALIZED)

        # All validation checks passed
        return (True, None)

    def _has_winning_line(self, symbol: PlayerSymbol) -> bool:
        """Check if a specific symbol has a winning line on the board.

        Args:
            symbol: The player symbol to check ('X' or 'O')

        Returns:
            True if the symbol has a winning line, False otherwise
        """
        board = self.game_state.board

        # Check rows
        for row in range(3):
            if (
                board.cells[row][0] == symbol
                and board.cells[row][1] == symbol
                and board.cells[row][2] == symbol
            ):
                return True

        # Check columns
        for col in range(3):
            if (
                board.cells[0][col] == symbol
                and board.cells[1][col] == symbol
                and board.cells[2][col] == symbol
            ):
                return True

        # Check main diagonal
        if (
            board.cells[0][0] == symbol
            and board.cells[1][1] == symbol
            and board.cells[2][2] == symbol
        ):
            return True

        # Check anti-diagonal
        if (
            board.cells[0][2] == symbol
            and board.cells[1][1] == symbol
            and board.cells[2][0] == symbol
        ):
            return True

        return False
