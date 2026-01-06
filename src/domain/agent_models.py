"""Agent domain models.

This module contains domain models for agent analysis: Threat, Opportunity,
StrategicMove, BoardAnalysis, and related models.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.domain.errors import (
    E_INVALID_CONFIDENCE,
    E_INVALID_LINE_TYPE,
    E_INVALID_MOVE_TYPE,
    E_INVALID_PRIORITY,
    E_MISSING_REASONING,
)
from src.domain.models import Position

LineType = Literal["row", "column", "diagonal"]
MoveType = Literal["center", "corner", "edge", "fork", "block_fork"]


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


class Opportunity(BaseModel):
    """Represents a winning opportunity where AI can win on this move.

    Opportunity contains the position that would complete a winning line,
    the type of winning line, the line index, and confidence score (0.0-1.0).

    Attributes:
        position: The Position that would complete a winning line
        line_type: Type of winning line ('row', 'column', or 'diagonal')
        line_index: Index of the line (0-2 for rows/columns, 0 for main diagonal, 1 for anti-diagonal)
        confidence: Confidence score (0.0-1.0) indicating likelihood of success

    Raises:
        ValueError: If line_type is invalid (error code: E_INVALID_LINE_TYPE)
        ValueError: If line_index is out of range (error code: E_INVALID_LINE_INDEX)
        ValueError: If confidence is out of range (error code: E_INVALID_CONFIDENCE)
    """

    position: Position = Field(..., description="Position that would complete a winning line")
    line_type: LineType = Field(
        ..., description="Type of winning line ('row', 'column', or 'diagonal')"
    )
    line_index: int = Field(..., ge=0, le=2, description="Index of the line (0-2)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")

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

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate that confidence is in range 0.0-1.0.

        Args:
            v: The confidence value to validate

        Returns:
            The validated confidence value (rounded to 2 decimal places)

        Raises:
            ValueError: If confidence is not in range 0.0-1.0 (error code: E_INVALID_CONFIDENCE)
        """
        if not (0.0 <= v <= 1.0):
            raise ValueError(
                f"confidence must be between 0.0 and 1.0, got {v}. "
                f"Error code: {E_INVALID_CONFIDENCE}"
            )
        # Round to 2 decimal places as per spec
        return round(v, 2)


class StrategicMove(BaseModel):
    """Represents a strategic position recommendation.

    StrategicMove contains a position recommendation with move type,
    priority, and reasoning. Used by the Strategist agent to recommend moves.

    Attributes:
        position: The Position recommended for the move
        move_type: Type of strategic move ('center', 'corner', 'edge', 'fork', 'block_fork')
        priority: Priority ranking (1-10, higher is more important)
        reasoning: Human-readable explanation for the move (required, non-empty)

    Raises:
        ValueError: If move_type is invalid (error code: E_INVALID_MOVE_TYPE)
        ValueError: If priority is out of range (error code: E_INVALID_PRIORITY)
        ValueError: If reasoning is empty (error code: E_MISSING_REASONING)
    """

    position: Position = Field(..., description="Recommended position for the move")
    move_type: MoveType = Field(
        ..., description="Type of strategic move ('center', 'corner', 'edge', 'fork', 'block_fork')"
    )
    priority: int = Field(..., ge=1, le=10, description="Priority ranking (1-10)")
    reasoning: str = Field(
        ..., min_length=1, max_length=1000, description="Human-readable explanation"
    )

    @field_validator("move_type")
    @classmethod
    def validate_move_type(cls, v: str) -> str:
        """Validate that move_type is one of the valid values.

        Args:
            v: The move_type value to validate

        Returns:
            The validated move_type value

        Raises:
            ValueError: If move_type is not one of the valid values (error code: E_INVALID_MOVE_TYPE)
        """
        valid_types = ["center", "corner", "edge", "fork", "block_fork"]
        if v not in valid_types:
            raise ValueError(
                f"move_type must be one of {valid_types}, got '{v}'. "
                f"Error code: {E_INVALID_MOVE_TYPE}"
            )
        return v  # type: ignore[return-value]

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        """Validate that priority is in range 1-10.

        Args:
            v: The priority value to validate

        Returns:
            The validated priority value

        Raises:
            ValueError: If priority is not in range 1-10 (error code: E_INVALID_PRIORITY)
        """
        if not (1 <= v <= 10):
            raise ValueError(
                f"priority must be between 1 and 10, got {v}. " f"Error code: {E_INVALID_PRIORITY}"
            )
        return v

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        """Validate that reasoning is non-empty.

        Args:
            v: The reasoning value to validate

        Returns:
            The validated reasoning value

        Raises:
            ValueError: If reasoning is empty (error code: E_MISSING_REASONING)
        """
        if not v or not v.strip():
            raise ValueError(
                f"reasoning must be a non-empty string, got empty value. "
                f"Error code: {E_MISSING_REASONING}"
            )
        return v
