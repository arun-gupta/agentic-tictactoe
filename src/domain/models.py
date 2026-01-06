"""Core game entity domain models.

This module contains the core game entities: Position, Board, and GameState.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.domain.errors import E_INVALID_BOARD_SIZE, E_POSITION_OUT_OF_BOUNDS

CellState = Literal["EMPTY", "X", "O"]


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
        default_factory=lambda: [["EMPTY"] * 3 for _ in range(3)],
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
