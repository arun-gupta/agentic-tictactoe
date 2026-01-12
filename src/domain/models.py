"""Core game entity domain models.

This module contains the core game entities: Position, Board, and GameState.
"""

from typing import Any, Callable, Literal

from pydantic import BaseModel, Field, field_validator, model_serializer

from src.domain.errors import E_INVALID_BOARD_SIZE, E_POSITION_OUT_OF_BOUNDS

CellState = Literal["EMPTY", "X", "O"]
PlayerSymbol = Literal["X", "O"]
WinnerSymbol = Literal["X", "O", "DRAW"]


class Position(BaseModel):
    """Represents a cell position on the 3x3 game board.

    Position is immutable and hashable, making it suitable for use in
    dictionaries and sets. Row and column values must be in the range 0-2.

    Attributes:
        row: Row index (0-2)
        col: Column index (0-2)

    Raises:
        ValueError: If row or col is not in range 0-2 (error code: E_POSITION_OUT_OF_BOUNDS)
    """

    row: int = Field(..., ge=0, le=2, description="Row index (0-2)")
    col: int = Field(..., ge=0, le=2, description="Column index (0-2)")

    model_config = {"frozen": True}  # Makes Position immutable and hashable

    def __hash__(self) -> int:
        """Make Position hashable for use in dictionaries and sets."""
        return hash((self.row, self.col))

    def __eq__(self, other: object) -> bool:
        """Compare two Position objects for equality."""
        if not isinstance(other, Position):
            return NotImplemented
        return self.row == other.row and self.col == other.col


class Board(BaseModel):
    """Represents a 3x3 Tic-Tac-Toe game board.

    Board stores cell states as a 3x3 grid. Each cell can be EMPTY, X, or O.
    Board validates that the grid is exactly 3x3 and provides methods to
    interact with cells.

    Attributes:
        cells: 3x3 matrix of cell states (list of 3 lists, each containing 3 CellState values)

    Raises:
        ValueError: If cells is not exactly 3x3 (error code: E_INVALID_BOARD_SIZE)
    """

    cells: list[list[CellState]] = Field(
        default_factory=lambda: [["EMPTY" for _ in range(3)] for _ in range(3)],  # type: ignore[arg-type]
        description="3x3 matrix of cell states",
    )

    @field_validator("cells")
    @classmethod
    def validate_board_size(cls, v: list[list[CellState]]) -> list[list[CellState]]:
        """Validate that cells is exactly 3x3.

        Args:
            v: The cells matrix to validate

        Returns:
            The validated cells matrix

        Raises:
            ValueError: If cells is not exactly 3x3
        """
        if len(v) != 3:
            raise ValueError(
                f"Board must have exactly 3 rows, got {len(v)}. "
                f"Error code: {E_INVALID_BOARD_SIZE}"
            )
        for i, row in enumerate(v):
            if len(row) != 3:
                raise ValueError(
                    f"Board row {i} must have exactly 3 columns, got {len(row)}. "
                    f"Error code: {E_INVALID_BOARD_SIZE}"
                )
        return v

    def get_cell(self, position: Position) -> CellState:
        """Get the symbol at the given position.

        Args:
            position: The position to get the cell value from

        Returns:
            The cell state ('EMPTY', 'X', or 'O')

        Raises:
            ValueError: If position is out of bounds (error code: E_POSITION_OUT_OF_BOUNDS)
        """
        if not (0 <= position.row < 3) or not (0 <= position.col < 3):
            raise ValueError(
                f"Position ({position.row}, {position.col}) is out of bounds. "
                f"Error code: {E_POSITION_OUT_OF_BOUNDS}"
            )
        return self.cells[position.row][position.col]

    def set_cell(self, position: Position, symbol: CellState) -> None:
        """Set the symbol at the given position.

        Args:
            position: The position to set
            symbol: The symbol to set ('X', 'O', or 'EMPTY')

        Raises:
            ValueError: If position is out of bounds (error code: E_POSITION_OUT_OF_BOUNDS)
        """
        if not (0 <= position.row < 3) or not (0 <= position.col < 3):
            raise ValueError(
                f"Position ({position.row}, {position.col}) is out of bounds. "
                f"Error code: {E_POSITION_OUT_OF_BOUNDS}"
            )
        self.cells[position.row][position.col] = symbol

    def is_empty(self, position: Position) -> bool:
        """Check if the cell at the given position is empty.

        Args:
            position: The position to check

        Returns:
            True if the cell is empty, False otherwise

        Raises:
            ValueError: If position is out of bounds (error code: E_POSITION_OUT_OF_BOUNDS)
        """
        return self.get_cell(position) == "EMPTY"

    def get_empty_positions(self) -> list[Position]:
        """Get a list of all empty positions on the board.

        Returns:
            A list of Position objects representing empty cells
        """
        empty_positions = []
        for row in range(3):
            for col in range(3):
                pos = Position(row=row, col=col)
                if self.is_empty(pos):
                    empty_positions.append(pos)
        return empty_positions


class GameState(BaseModel):
    """Represents the complete state of a Tic-Tac-Toe game.

    GameState tracks the board, players, move count, and game status.
    It provides helper methods to determine the current player and opponent.

    Attributes:
        board: The current 3x3 game board
        player_symbol: Human player's symbol ('X' or 'O')
        ai_symbol: AI player's symbol ('X' or 'O')
        move_count: Number of moves made (0-9)

    Raises:
        ValueError: If board is invalid (error code: E_INVALID_BOARD_SIZE)
    """

    board: Board = Field(default_factory=Board, description="Current 3x3 game board")
    player_symbol: PlayerSymbol = Field(..., description="Human player's symbol ('X' or 'O')")
    ai_symbol: PlayerSymbol = Field(..., description="AI player's symbol ('X' or 'O')")
    move_count: int = Field(default=0, ge=0, le=9, description="Number of moves made (0-9)")

    def get_current_player(self) -> PlayerSymbol:
        """Get the current player's symbol based on move count.

        Returns player symbol for even move counts, AI symbol for odd move counts.

        Returns:
            Current player's symbol ('X' or 'O')
        """
        if self.move_count % 2 == 0:
            return self.player_symbol
        else:
            return self.ai_symbol

    def get_opponent(self, symbol: PlayerSymbol | None = None) -> PlayerSymbol:
        """Get the opponent symbol for the current player or given symbol.

        If no symbol is provided, returns the opponent of the current player.

        Args:
            symbol: Optional player symbol ('X' or 'O'). If None, uses current player.

        Returns:
            The opponent symbol ('O' if symbol is 'X', 'X' if symbol is 'O')
        """
        if symbol is None:
            symbol = self.get_current_player()
        return "O" if symbol == "X" else "X"

    def _check_win(self) -> PlayerSymbol | None:
        """Check if there is a winner on the board.

        Checks all 8 winning lines (3 rows, 3 columns, 2 diagonals) for three
        matching symbols.

        Returns:
            Winner symbol ('X' or 'O') if there is a winner, None otherwise
        """
        # Check rows
        for row in range(3):
            if (
                self.board.cells[row][0] != "EMPTY"
                and self.board.cells[row][0] == self.board.cells[row][1]
                and self.board.cells[row][1] == self.board.cells[row][2]
            ):
                return self.board.cells[row][0]  # type: ignore[return-value]

        # Check columns
        for col in range(3):
            if (
                self.board.cells[0][col] != "EMPTY"
                and self.board.cells[0][col] == self.board.cells[1][col]
                and self.board.cells[1][col] == self.board.cells[2][col]
            ):
                return self.board.cells[0][col]  # type: ignore[return-value]

        # Check main diagonal (0,0), (1,1), (2,2)
        if (
            self.board.cells[0][0] != "EMPTY"
            and self.board.cells[0][0] == self.board.cells[1][1]
            and self.board.cells[1][1] == self.board.cells[2][2]
        ):
            return self.board.cells[0][0]

        # Check anti-diagonal (0,2), (1,1), (2,0)
        if (
            self.board.cells[0][2] != "EMPTY"
            and self.board.cells[0][2] == self.board.cells[1][1]
            and self.board.cells[1][1] == self.board.cells[2][0]
        ):
            return self.board.cells[0][2]

        return None

    def _check_draw(self) -> bool:
        """Check if the game is a draw.

        A draw occurs when all 9 cells are occupied and there is no winner.

        Returns:
            True if the game is a draw, False otherwise
        """
        if self.move_count < 9:
            return False
        return self._check_win() is None

    def is_game_over(self) -> bool:
        """Check if the game is over.

        The game is over if there is a winner or a draw.

        Returns:
            True if the game is over, False otherwise
        """
        return self._check_win() is not None or self._check_draw()

    def get_winner(self) -> WinnerSymbol | None:
        """Get the winner of the game.

        Returns:
            Winner symbol ('X', 'O', 'DRAW') if game is over, None if game is ongoing
        """
        winner = self._check_win()
        if winner is not None:
            return winner
        if self._check_draw():
            return "DRAW"
        return None

    @model_serializer(mode="wrap")
    def serialize(self, serializer: Callable[[Any], dict[str, Any]], info: Any) -> dict[str, Any]:
        """Serialize GameState to dict, including computed fields is_game_over and winner."""
        data = serializer(self)
        data["is_game_over"] = self.is_game_over()
        data["winner"] = self.get_winner()
        return data
