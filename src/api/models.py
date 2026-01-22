"""API request and response models.

Phase 4.0.2: Request/Response Models
- MoveRequest: Player move request (row, col)
- MoveResponse: Move response with updated state and AI move
- GameStatusResponse: Complete game status including agents and metrics
- ErrorResponse: Standard error response for all API errors

Phase 4.2.1: New Game Models
- NewGameRequest: Request to create a new game (optional player_symbol)
- NewGameResponse: Response with game_id and initial GameState
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from src.domain.agent_models import MoveExecution
from src.domain.models import GameState, PlayerSymbol, Position


class MoveRequest(BaseModel):
    """Player move request model.

    Contains game_id to identify the game session, and row and column integers (0-2) for the move position.

    Attributes:
        game_id: Unique game identifier (UUID v4) - required to identify which game session
        row: Row index (0-2)
        col: Column index (0-2)

    Raises:
        ValueError: If row or col is not in range 0-2 (error code: E_MOVE_OUT_OF_BOUNDS)
    """

    model_config = ConfigDict(extra="forbid")  # Reject extra fields for strict validation

    game_id: str = Field(..., description="Unique game identifier (UUID v4)")
    row: int = Field(..., description="Row index (0-2) - validated in endpoint")
    col: int = Field(..., description="Column index (0-2) - validated in endpoint")


class MoveResponse(BaseModel):
    """Move response model.

    Contains success status, position (if successful), updated GameState,
    AI move execution details (if AI moved), and error message (if failed).

    Attributes:
        success: Whether the move was successful
        position: Position where move was made (required if success=True)
        updated_game_state: Updated game state after move (required if success=True)
        ai_move_execution: AI move execution details (optional, present if AI moved)
        error_message: Error message if move failed (required if success=False)
        fallback_used: Whether fallback strategy was used (optional)
        total_execution_time_ms: Total execution time in milliseconds (optional)
    """

    success: bool = Field(..., description="Whether the move was successful")
    position: Position | None = Field(
        default=None, description="Position where move was made (required if success=True)"
    )
    updated_game_state: GameState | None = Field(
        default=None,
        description="Updated game state after move (required if success=True)",
    )
    ai_move_execution: MoveExecution | None = Field(
        default=None, description="AI move execution details (optional, present if AI moved)"
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if move failed (required if success=False, max 500 chars)",
        max_length=500,
    )
    fallback_used: bool | None = Field(
        default=None, description="Whether fallback strategy was used (optional)"
    )
    total_execution_time_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Total execution time in milliseconds (optional, >= 0.0, precision: 2 decimal places)",
    )

    @field_validator("error_message")
    @classmethod
    def validate_error_message(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Validate error_message is non-empty if provided."""
        if v is not None and len(v) == 0:
            raise ValueError("error_message must be non-empty if provided")
        return v

    @field_validator("total_execution_time_ms")
    @classmethod
    def validate_execution_time(cls, v: float | None) -> float | None:
        """Round execution time to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v


class GameStatusResponse(BaseModel):
    """Game status response model.

    Contains current GameState, agent status dictionary, and metrics dictionary.

    Attributes:
        game_state: Current game state
        agent_status: Dictionary with agent status information (optional)
        metrics: Dictionary with game metrics (optional)
    """

    game_state: GameState = Field(..., description="Current game state")
    agent_status: dict[str, Any] | None = Field(
        default=None, description="Dictionary with agent status information (optional)"
    )
    metrics: dict[str, Any] | None = Field(
        default=None, description="Dictionary with game metrics (optional)"
    )


class NewGameRequest(BaseModel):
    """Request model for creating a new game.

    Attributes:
        player_symbol: Optional player symbol preference ('X' or 'O'). Defaults to 'X' if not specified.
    """

    model_config = ConfigDict(extra="forbid")  # Reject extra fields for strict validation

    player_symbol: PlayerSymbol | None = Field(
        default=None,
        description="Player symbol preference ('X' or 'O'). Defaults to 'X' if not specified.",
    )


class NewGameResponse(BaseModel):
    """Response model for new game creation.

    Attributes:
        game_id: Unique game identifier (UUID v4)
        game_state: Initial game state with MoveCount=0, empty board
    """

    game_id: str = Field(..., description="Unique game identifier (UUID v4)")
    game_state: GameState = Field(
        ..., description="Initial game state with MoveCount=0, empty board"
    )


class ResetGameRequest(BaseModel):
    """Request model for resetting a game.

    Attributes:
        game_id: Unique game identifier (UUID v4) for the game to reset
    """

    model_config = ConfigDict(extra="forbid")  # Reject extra fields for strict validation

    game_id: str = Field(..., description="Unique game identifier (UUID v4)")


class ResetGameResponse(BaseModel):
    """Response model for game reset.

    Attributes:
        game_id: Game identifier (UUID v4) - same as request if reset, or new if new game created
        game_state: Reset game state with MoveCount=0, empty board, CurrentPlayer=X
    """

    game_id: str = Field(..., description="Game identifier (UUID v4)")
    game_state: GameState = Field(..., description="Reset game state with MoveCount=0, empty board")


class MoveHistory(BaseModel):
    """Move history entry model.

    Represents a single move in the game history with all relevant details.

    Attributes:
        move_number: Move sequence number (1-based, increments with each move)
        player: Player symbol who made the move ('X' or 'O')
        position: Position where the move was made
        timestamp: ISO 8601 timestamp when the move was made
        agent_reasoning: Optional agent reasoning for AI moves (if available)
    """

    move_number: int = Field(..., ge=1, description="Move sequence number (1-based)")
    player: PlayerSymbol = Field(..., description="Player symbol who made the move ('X' or 'O')")
    position: Position = Field(..., description="Position where the move was made")
    timestamp: str = Field(..., description="ISO 8601 timestamp when the move was made")
    agent_reasoning: str | None = Field(
        default=None, description="Optional agent reasoning for AI moves"
    )


class AgentStatus(BaseModel):
    """Agent status response model.

    Represents the current status of an agent (scout, strategist, executor).

    Attributes:
        status: Current agent status ('idle', 'processing', 'success', 'failed')
        elapsed_time_ms: Elapsed time in milliseconds for current operation (if processing)
        execution_time_ms: Execution time in milliseconds for last completed operation (if completed)
        success: Whether the last operation was successful (if completed)
        error_message: Error message if the last operation failed (if failed)
    """

    status: str = Field(
        ..., description="Current agent status ('idle', 'processing', 'success', 'failed')"
    )
    elapsed_time_ms: float | None = Field(
        default=None,
        description="Elapsed time in milliseconds for current operation (if processing)",
    )
    execution_time_ms: float | None = Field(
        default=None,
        description="Execution time in milliseconds for last completed operation (if completed)",
    )
    success: bool | None = Field(
        default=None, description="Whether the last operation was successful (if completed)"
    )
    error_message: str | None = Field(
        default=None, description="Error message if the last operation failed (if failed)"
    )


class ErrorResponse(BaseModel):
    """Standard error response model for all API errors.

    Follows Section 5.4 error response schema.

    Attributes:
        status: Always "failure" for error responses
        error_code: Error code enum value
        message: Human-readable error message
        timestamp: ISO 8601 timestamp (UTC) when error occurred
        details: Additional error context (optional)
    """

    status: str = Field(default="failure", description="Always 'failure' for error responses")
    error_code: str = Field(..., description="Error code enum value")
    message: str = Field(..., description="Human-readable error message")
    timestamp: str = Field(..., description="ISO 8601 timestamp (UTC) when error occurred")
    details: dict[str, Any] | None = Field(
        default=None, description="Additional error context (optional)"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is always 'failure'."""
        if v != "failure":
            raise ValueError("status must be 'failure' for error responses")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp is ISO 8601 format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"timestamp must be ISO 8601 format: {e}") from e
        return v
