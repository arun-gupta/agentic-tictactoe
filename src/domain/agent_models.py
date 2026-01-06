"""Agent domain models.

This module contains domain models for agent analysis: Threat, Opportunity,
StrategicMove, BoardAnalysis, and related models.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.domain.errors import (
    E_INVALID_LINE_TYPE,
)
from src.domain.models import Position

LineType = Literal["row", "column", "diagonal"]


class Threat(BaseModel):
    """Represents an immediate threat where the opponent will win on next move if not blocked.

    Threat contains the position that must be blocked, the type of winning line
    that is threatened, the line index, and severity (always 'critical' for Tic-Tac-Toe).

    Attributes:
        position: The Position that must be blocked to prevent the opponent from winning
        line_type: Type of winning line ('row', 'column', or 'diagonal')
        line_index: Index of the line (0-2 for rows/columns, 0 for main diagonal, 1 for anti-diagonal)
        severity: Always 'critical' for Tic-Tac-Toe threats

    Raises:
        ValueError: If line_type is invalid (error code: E_INVALID_LINE_TYPE)
        ValueError: If line_index is out of range (error code: E_INVALID_LINE_INDEX)
    """

    position: Position = Field(..., description="Position that must be blocked")
    line_type: LineType = Field(
        ..., description="Type of winning line ('row', 'column', or 'diagonal')"
    )
    line_index: int = Field(..., ge=0, le=2, description="Index of the line (0-2)")
    severity: Literal["critical"] = Field(
        default="critical", description="Always 'critical' for Tic-Tac-Toe"
    )

    @field_validator("line_type")
    @classmethod
    def validate_line_type(cls, v: str) -> str:
        """Validate that line_type is one of: 'row', 'column', 'diagonal'.

        Args:
            v: The line_type value to validate

        Returns:
            The validated line_type value

        Raises:
            ValueError: If line_type is not one of the valid values (error code: E_INVALID_LINE_TYPE)
        """
        valid_types = ["row", "column", "diagonal"]
        if v not in valid_types:
            raise ValueError(
                f"line_type must be one of {valid_types}, got '{v}'. "
                f"Error code: {E_INVALID_LINE_TYPE}"
            )
        return v  # type: ignore[return-value]
