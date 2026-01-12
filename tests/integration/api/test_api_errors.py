"""Tests for Phase 4.4: Error Handling.

Tests verify:
- Error responses follow ErrorResponse schema (status="failure", error_code, message, timestamp, details)
- Error codes map to correct HTTP status codes per Section 5.5 (HTTP Status Code Mapping)
- Error response timestamps are ISO 8601 format
- Error response details include field/expected/actual when applicable
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src import api
from src.domain.errors import (
    E_CELL_OCCUPIED,
    E_GAME_ALREADY_OVER,
    E_MOVE_OUT_OF_BOUNDS,
    E_SERVICE_NOT_READY,
)


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(api.main.app)


@pytest.fixture(autouse=True)
def reset_game_sessions() -> None:
    """Reset game sessions and service state before each test."""
    import src.api.main as main_module

    # Clear game sessions
    main_module._game_sessions.clear()
    # Ensure service is ready
    main_module._service_ready = True
    yield
    # Cleanup after test
    main_module._game_sessions.clear()


class TestErrorResponseSchema:
    """Test that error responses follow ErrorResponse schema."""

    def test_error_response_follows_error_response_schema(self, client: TestClient) -> None:
        """Test error responses follow ErrorResponse schema (status="failure", error_code, message, timestamp, details)."""
        # Create a game first
        response = client.post("/api/game/new")
        assert response.status_code == 201
        game_id = response.json()["game_id"]

        # Try to make a move with invalid row (out of bounds)
        response = client.post("/api/game/move", json={"game_id": game_id, "row": 3, "col": 1})

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "failure"
        assert "error_code" in data
        assert "message" in data
        assert "timestamp" in data
        # details is optional but should be present for move errors
        assert "details" in data

    def test_error_response_timestamp_is_iso_8601_format(self, client: TestClient) -> None:
        """Test error response timestamp is ISO 8601 format."""
        # Create a game first
        response = client.post("/api/game/new")
        assert response.status_code == 201
        game_id = response.json()["game_id"]

        # Try to make a move with invalid row (out of bounds)
        response = client.post("/api/game/move", json={"game_id": game_id, "row": 3, "col": 1})

        assert response.status_code == 400
        data = response.json()
        timestamp = data["timestamp"]
        # Verify it's a valid ISO 8601 format
        # Should be in format: YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS.ffffffZ
        assert "T" in timestamp
        assert timestamp.endswith("Z") or "+00:00" in timestamp
        # Try to parse it
        try:
            if timestamp.endswith("Z"):
                parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                parsed = datetime.fromisoformat(timestamp)
            assert parsed is not None
        except ValueError:
            pytest.fail(f"Timestamp {timestamp} is not valid ISO 8601 format")

    def test_error_response_details_includes_field_when_applicable(
        self, client: TestClient
    ) -> None:
        """Test error response details include field/expected/actual when applicable."""
        # Create a game first
        response = client.post("/api/game/new")
        assert response.status_code == 201
        game_id = response.json()["game_id"]

        # Try to make a move with invalid row (out of bounds)
        response = client.post("/api/game/move", json={"game_id": game_id, "row": 3, "col": 1})

        assert response.status_code == 400
        data = response.json()
        assert "details" in data
        details = data["details"]
        assert details is not None
        # Details should include game_id, row, col for move errors
        assert "game_id" in details
        assert "row" in details
        assert "col" in details


class TestErrorCodeToHttpStatusMapping:
    """Test that error codes map to correct HTTP status codes per Section 5.5."""

    def test_e_move_out_of_bounds_maps_to_400_bad_request(self, client: TestClient) -> None:
        """Test E_MOVE_OUT_OF_BOUNDS maps to 400 Bad Request."""
        # Create a game first
        response = client.post("/api/game/new")
        assert response.status_code == 201
        game_id = response.json()["game_id"]

        # Try to make a move with row out of bounds
        response = client.post("/api/game/move", json={"game_id": game_id, "row": 3, "col": 1})

        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == E_MOVE_OUT_OF_BOUNDS

    def test_e_cell_occupied_maps_to_400_bad_request(self, client: TestClient) -> None:
        """Test E_CELL_OCCUPIED maps to 400 Bad Request."""
        # Create a game first
        response = client.post("/api/game/new")
        assert response.status_code == 201
        game_id = response.json()["game_id"]

        # Make a valid move first
        response = client.post("/api/game/move", json={"game_id": game_id, "row": 0, "col": 0})
        assert response.status_code == 200

        # Try to make a move to the same cell (occupied)
        response = client.post("/api/game/move", json={"game_id": game_id, "row": 0, "col": 0})

        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == E_CELL_OCCUPIED

    def test_e_game_already_over_maps_to_400_bad_request(self, client: TestClient) -> None:
        """Test E_GAME_ALREADY_OVER maps to 400 Bad Request."""
        import src.api.main as main_module
        from src.domain.models import Position

        # Create a new game
        response = client.post("/api/game/new")
        assert response.status_code == 201
        game_id = response.json()["game_id"]
        engine = main_module._game_sessions[game_id]

        # Manually create a winning state (3 X's in a row)
        engine.game_state.board.set_cell(Position(row=0, col=0), "X")
        engine.game_state.board.set_cell(Position(row=0, col=1), "X")
        engine.game_state.board.set_cell(Position(row=0, col=2), "X")
        engine.game_state.move_count = 3

        # Verify game is over
        assert engine.is_game_over() is True

        # Try to make a move when game is over
        response = client.post("/api/game/move", json={"game_id": game_id, "row": 1, "col": 1})

        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == E_GAME_ALREADY_OVER

    def test_e_service_not_ready_maps_to_503_service_unavailable(self, client: TestClient) -> None:
        """Test E_SERVICE_NOT_READY maps to 503 Service Unavailable."""
        import src.api.main as main_module

        # Set service as not ready
        main_module._service_ready = False

        # Try to create a new game
        response = client.post("/api/game/new")

        assert response.status_code == 503
        data = response.json()
        assert data["error_code"] == E_SERVICE_NOT_READY

        # Restore service ready state
        main_module._service_ready = True

    def test_e_game_not_found_maps_to_404_not_found(self, client: TestClient) -> None:
        """Test E_GAME_NOT_FOUND maps to 404 Not Found."""
        # Try to make a move with non-existent game_id
        response = client.post(
            "/api/game/move",
            json={"game_id": "00000000-0000-0000-0000-000000000000", "row": 1, "col": 1},
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "E_GAME_NOT_FOUND"

    def test_e_internal_error_maps_to_500_internal_server_error(self, client: TestClient) -> None:
        """Test E_INTERNAL_ERROR maps to 500 Internal Server Error."""
        # Use the test endpoint that raises a general exception
        client_without_raise = TestClient(api.main.app, raise_server_exceptions=False)
        response = client_without_raise.get("/test/general-error")

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "E_INTERNAL_ERROR"
        assert data["status"] == "failure"
