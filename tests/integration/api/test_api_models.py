"""Tests for Phase 4.0.2: Request/Response Models.

Tests verify:
- MoveRequest validation (row/col bounds 0-2)
- MoveResponse structure and validation
- GameStatusResponse structure
- ErrorResponse structure and validation
- Model serialization/deserialization
"""

import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.api.models import ErrorResponse, GameStatusResponse, MoveRequest, MoveResponse
from src.domain.agent_models import MoveExecution, MovePriority
from src.domain.models import Board, GameState, Position


class TestMoveRequest:
    """Test MoveRequest model validation."""

    def test_move_request_validation_row_col_bounds_0_2(self) -> None:
        """Test that MoveRequest validates row/col bounds (0-2)."""
        # Valid requests
        request1 = MoveRequest(row=0, col=0)
        assert request1.row == 0
        assert request1.col == 0

        request2 = MoveRequest(row=2, col=2)
        assert request2.row == 2
        assert request2.col == 2

        request3 = MoveRequest(row=1, col=1)
        assert request3.row == 1
        assert request3.col == 1

    def test_move_request_rejects_invalid_values_row_col_less_than_0(self) -> None:
        """Test that MoveRequest rejects invalid values (row/col < 0)."""
        with pytest.raises(ValidationError) as exc_info:
            MoveRequest(row=-1, col=0)
        # Pydantic Field validation catches this before custom validator
        assert "greater than or equal to 0" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            MoveRequest(row=0, col=-1)
        assert "greater than or equal to 0" in str(exc_info.value).lower()

    def test_move_request_rejects_invalid_values_row_col_greater_than_2(self) -> None:
        """Test that MoveRequest rejects invalid values (row/col > 2)."""
        with pytest.raises(ValidationError) as exc_info:
            MoveRequest(row=3, col=0)
        # Pydantic Field validation catches this before custom validator
        assert "less than or equal to 2" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            MoveRequest(row=0, col=3)
        assert "less than or equal to 2" in str(exc_info.value).lower()


class TestMoveResponse:
    """Test MoveResponse model structure and validation."""

    def test_move_response_structure_success_true(self) -> None:
        """Test MoveResponse structure (success, position, updated_game_state when success=True)."""
        game_state = GameState(
            board=Board(),
            player_symbol="X",
            ai_symbol="O",
            move_count=1,
        )
        position = Position(row=1, col=1)

        response = MoveResponse(
            success=True,
            position=position,
            updated_game_state=game_state,
        )

        assert response.success is True
        assert response.position == position
        assert response.updated_game_state == game_state
        assert response.ai_move_execution is None
        assert response.error_message is None

    def test_move_response_includes_ai_move_execution_when_ai_moved(self) -> None:
        """Test MoveResponse includes ai_move_execution when AI moved."""
        game_state = GameState(
            board=Board(),
            player_symbol="X",
            ai_symbol="O",
            move_count=2,
        )
        position = Position(row=0, col=0)
        ai_move = MoveExecution(
            position=position,
            success=True,
            execution_time_ms=10.5,
            reasoning="AI made a move",
            actual_priority_used=MovePriority.CENTER_CONTROL,
        )

        response = MoveResponse(
            success=True,
            position=position,
            updated_game_state=game_state,
            ai_move_execution=ai_move,
            fallback_used=False,
            total_execution_time_ms=15.75,
        )

        assert response.success is True
        assert response.ai_move_execution == ai_move
        assert response.fallback_used is False
        assert response.total_execution_time_ms == 15.75

    def test_move_response_includes_error_message_when_success_false(self) -> None:
        """Test MoveResponse includes error_message when success=False."""
        response = MoveResponse(
            success=False,
            error_message="Cell is already occupied",
        )

        assert response.success is False
        assert response.error_message == "Cell is already occupied"
        assert response.position is None
        assert response.updated_game_state is None
        assert response.ai_move_execution is None

    def test_move_response_rejects_empty_error_message(self) -> None:
        """Test MoveResponse rejects empty error_message."""
        with pytest.raises(ValidationError) as exc_info:
            MoveResponse(success=False, error_message="")
        assert "non-empty" in str(exc_info.value).lower()

    def test_move_response_rounds_execution_time_to_2_decimals(self) -> None:
        """Test MoveResponse rounds total_execution_time_ms to 2 decimal places."""
        response = MoveResponse(
            success=True,
            position=Position(row=1, col=1),
            updated_game_state=GameState(
                board=Board(), player_symbol="X", ai_symbol="O", move_count=1
            ),
            total_execution_time_ms=15.756789,
        )

        assert response.total_execution_time_ms == 15.76


class TestGameStatusResponse:
    """Test GameStatusResponse model structure."""

    def test_game_status_response_structure(self) -> None:
        """Test GameStatusResponse structure (game_state, agent_status, metrics)."""
        game_state = GameState(
            board=Board(),
            player_symbol="X",
            ai_symbol="O",
            move_count=3,
        )
        agent_status = {"scout": "idle", "strategist": "processing"}
        metrics = {"total_moves": 3, "game_duration_ms": 1500.0}

        response = GameStatusResponse(
            game_state=game_state,
            agent_status=agent_status,
            metrics=metrics,
        )

        assert response.game_state == game_state
        assert response.agent_status == agent_status
        assert response.metrics == metrics

    def test_game_status_response_optional_fields(self) -> None:
        """Test GameStatusResponse with optional fields as None."""
        game_state = GameState(
            board=Board(),
            player_symbol="X",
            ai_symbol="O",
            move_count=0,
        )

        response = GameStatusResponse(game_state=game_state)

        assert response.game_state == game_state
        assert response.agent_status is None
        assert response.metrics is None


class TestErrorResponse:
    """Test ErrorResponse model structure and validation."""

    def test_error_response_structure(self) -> None:
        """Test ErrorResponse structure (status='failure', error_code, message, timestamp, details)."""
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        details = {"field": "position", "expected": "empty cell", "actual": "cell contains 'X'"}

        response = ErrorResponse(
            error_code="E_CELL_OCCUPIED",
            message="Cell is already occupied",
            timestamp=timestamp,
            details=details,
        )

        assert response.status == "failure"
        assert response.error_code == "E_CELL_OCCUPIED"
        assert response.message == "Cell is already occupied"
        assert response.timestamp == timestamp
        assert response.details == details

    def test_error_response_timestamp_is_iso_8601_format(self) -> None:
        """Test ErrorResponse timestamp is ISO 8601 format."""
        # Valid ISO 8601 timestamps
        valid_timestamps = [
            "2025-01-15T10:30:00Z",
            "2025-01-15T10:30:00.123Z",
            "2025-01-15T10:30:00+00:00",
        ]

        for timestamp in valid_timestamps:
            response = ErrorResponse(
                error_code="E_TEST",
                message="Test error",
                timestamp=timestamp,
            )
            assert response.timestamp == timestamp

        # Invalid timestamp
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                error_code="E_TEST",
                message="Test error",
                timestamp="invalid-timestamp",
            )
        assert "ISO 8601 format" in str(exc_info.value)

    def test_error_response_timestamp_defaults_to_current_time(self) -> None:
        """Test ErrorResponse can be created with current timestamp."""
        # Use timezone-aware datetime
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        response = ErrorResponse(
            error_code="E_TEST",
            message="Test error",
            timestamp=timestamp,
        )
        assert response.timestamp == timestamp

    def test_error_response_status_must_be_failure(self) -> None:
        """Test ErrorResponse status must be 'failure'."""
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")

        # Default status is "failure"
        response = ErrorResponse(
            error_code="E_TEST",
            message="Test error",
            timestamp=timestamp,
        )
        assert response.status == "failure"

        # Cannot set status to something else
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse(
                status="success",  # type: ignore[arg-type]
                error_code="E_TEST",
                message="Test error",
                timestamp=timestamp,
            )
        assert "must be 'failure'" in str(exc_info.value).lower()


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_all_models_serialize_to_json_correctly(self) -> None:
        """Test all models serialize to JSON correctly."""
        # MoveRequest
        move_request = MoveRequest(row=1, col=1)
        json_str = move_request.model_dump_json()
        data = json.loads(json_str)
        assert data == {"row": 1, "col": 1}

        # MoveResponse
        game_state = GameState(board=Board(), player_symbol="X", ai_symbol="O", move_count=1)
        move_response = MoveResponse(
            success=True,
            position=Position(row=1, col=1),
            updated_game_state=game_state,
        )
        json_str = move_response.model_dump_json()
        data = json.loads(json_str)
        assert data["success"] is True
        assert "position" in data
        assert "updated_game_state" in data

        # GameStatusResponse
        status_response = GameStatusResponse(game_state=game_state)
        json_str = status_response.model_dump_json()
        data = json.loads(json_str)
        assert "game_state" in data

        # ErrorResponse
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        error_response = ErrorResponse(
            error_code="E_TEST",
            message="Test error",
            timestamp=timestamp,
        )
        json_str = error_response.model_dump_json()
        data = json.loads(json_str)
        assert data["status"] == "failure"
        assert data["error_code"] == "E_TEST"

    def test_all_models_deserialize_from_json_correctly(self) -> None:
        """Test all models deserialize from JSON correctly."""
        # MoveRequest
        json_data = {"row": 1, "col": 1}
        move_request = MoveRequest.model_validate(json_data)
        assert move_request.row == 1
        assert move_request.col == 1

        # MoveResponse
        game_state_dict = GameState(
            board=Board(), player_symbol="X", ai_symbol="O", move_count=1
        ).model_dump()
        json_data = {
            "success": True,
            "position": {"row": 1, "col": 1},
            "updated_game_state": game_state_dict,
        }
        move_response = MoveResponse.model_validate(json_data)
        assert move_response.success is True
        assert move_response.position == Position(row=1, col=1)

        # GameStatusResponse
        json_data = {"game_state": game_state_dict}
        status_response = GameStatusResponse.model_validate(json_data)
        assert status_response.game_state.move_count == 1

        # ErrorResponse
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        json_data = {
            "status": "failure",
            "error_code": "E_TEST",
            "message": "Test error",
            "timestamp": timestamp,
        }
        error_response = ErrorResponse.model_validate(json_data)
        assert error_response.status == "failure"
        assert error_response.error_code == "E_TEST"
