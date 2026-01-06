"""Result wrappers for agent outputs.

This module contains generic result wrappers for agent outputs: AgentResult.
"""

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from src.domain.errors import (
    E_INVALID_EXECUTION_TIME,
    E_MISSING_DATA,
    E_MISSING_ERROR_MESSAGE,
)

T = TypeVar("T")


class AgentResult(BaseModel, Generic[T]):
    """Generic wrapper for agent outputs.

    AgentResult provides a consistent interface for all agent outputs, containing
    domain data, success/failure status, error message, execution time, and timestamp.

    Attributes:
        success: Boolean indicating if the operation was successful
        data: Typed domain data (required if success=True)
        error_message: Error message string (required if success=False)
        execution_time_ms: Execution time in milliseconds (required, >= 0.0)
        timestamp: ISO 8601 timestamp in UTC (auto-generated if not provided)

    Raises:
        ValueError: If execution_time_ms is negative (error code: E_INVALID_EXECUTION_TIME)
        ValueError: If data is missing when success=True (error code: E_MISSING_DATA)
        ValueError: If error_message is missing when success=False
    """

    success: bool = Field(..., description="Whether the operation was successful")
    data: T | None = Field(default=None, description="Typed domain data (required if success=True)")
    error_code: str | None = Field(
        default=None, description="Error code string (required if success=False, E_* pattern)"
    )
    error_message: str | None = Field(
        default=None,
        max_length=500,
        description="Error message string (required if success=False, max 500 chars)",
    )
    execution_time_ms: float = Field(
        ..., ge=0.0, description="Execution time in milliseconds (>= 0.0)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        description="ISO 8601 timestamp in UTC",
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional metadata dictionary (max 50 keys)"
    )

    @field_validator("execution_time_ms")
    @classmethod
    def validate_execution_time(cls, v: float) -> float:
        """Validate that execution_time_ms is >= 0.0.

        Args:
            v: The execution_time_ms value to validate

        Returns:
            The validated execution_time_ms value (rounded to 2 decimal places)

        Raises:
            ValueError: If execution_time_ms is negative (error code: E_INVALID_EXECUTION_TIME)
        """
        if v < 0.0:
            raise ValueError(
                f"execution_time_ms must be >= 0.0, got {v}. "
                f"Error code: {E_INVALID_EXECUTION_TIME}"
            )
        # Round to 2 decimal places as per spec
        return round(v, 2)

    @field_validator("data")
    @classmethod
    def validate_data_when_success(cls, v: T | None, info: "ValidationInfo") -> T | None:
        """Validate that data is present when success=True.

        Args:
            v: The data value to validate
            info: Validation info containing other field values

        Returns:
            The validated data value

        Raises:
            ValueError: If data is None when success=True (error code: E_MISSING_DATA)
        """
        if info.data.get("success") is True and v is None:
            raise ValueError(
                f"data is required when success=True, got None. " f"Error code: {E_MISSING_DATA}"
            )
        return v

    @field_validator("error_message")
    @classmethod
    def validate_error_message_when_failure(
        cls, v: str | None, info: "ValidationInfo"
    ) -> str | None:
        """Validate that error_message is present when success=False.

        Args:
            v: The error_message value to validate
            info: Validation info containing other field values

        Returns:
            The validated error_message value

        Raises:
            ValueError: If error_message is None or empty when success=False
        """
        if info.data.get("success") is False:
            if v is None or not v.strip():
                raise ValueError(
                    f"error_message is required when success=False, got empty value. "
                    f"Error code: {E_MISSING_ERROR_MESSAGE}"
                )
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        """Validate that metadata has max 50 keys and each value is max 200 chars.

        Args:
            v: The metadata dictionary to validate

        Returns:
            The validated metadata dictionary

        Note:
            This validator ensures metadata constraints are met.
        """
        if v is not None:
            if len(v) > 50:
                raise ValueError(f"metadata must have at most 50 keys, got {len(v)}")
            for key, value in v.items():
                if isinstance(value, str) and len(value) > 200:
                    raise ValueError(
                        f"metadata value for key '{key}' must be at most 200 characters, "
                        f"got {len(value)}"
                    )
        return v

    @staticmethod
    def _create_success(
        data: T, execution_time_ms: float, metadata: dict[str, Any] | None = None
    ) -> "AgentResult[T]":
        """Create a successful AgentResult.

        Args:
            data: The domain data to wrap
            execution_time_ms: Execution time in milliseconds
            metadata: Optional metadata dictionary

        Returns:
            AgentResult with success=True and the provided data
        """
        return AgentResult(
            success=True,
            data=data,
            error_code=None,
            error_message=None,
            execution_time_ms=execution_time_ms,
            metadata=metadata,
        )

    @staticmethod
    def _create_error(
        error_message: str,
        execution_time_ms: float,
        error_code: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "AgentResult[T]":
        """Create an error AgentResult.

        Args:
            error_message: Human-readable error message (required)
            execution_time_ms: Execution time in milliseconds
            error_code: Optional error code (E_* pattern, required if success=False per spec)
            metadata: Optional metadata dictionary

        Returns:
            AgentResult with success=False and the provided error message
        """
        return AgentResult(
            success=False,
            data=None,
            error_code=error_code,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            metadata=metadata,
        )


# Expose factory methods at class level to avoid Pydantic field shadowing
# Using setattr to avoid mypy errors about assignment to class
AgentResult.success = AgentResult._create_success
AgentResult.error = AgentResult._create_error
