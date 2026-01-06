"""Core game entity domain models.

This module contains the core game entities: Position, Board, and GameState.
"""

from pydantic import BaseModel, Field


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
