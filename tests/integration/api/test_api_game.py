"""Tests for Phase 4.2.1: POST /api/game/new endpoint.

Tests verify:
- POST /api/game/new creates new game session and returns 200
- POST /api/game/new returns game_id in response
- POST /api/game/new returns initial GameState with MoveCount=0, empty board
- POST /api/game/new accepts optional player_symbol preference
- POST /api/game/new defaults to X for player if not specified
"""

import pytest
from fastapi.testclient import TestClient

from src import api
from src.domain.errors import E_SERVICE_NOT_READY


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(api.main.app)


@pytest.fixture(autouse=True)
def reset_game_sessions() -> None:
    """Reset game sessions before each test."""
    import src.api.main as main_module

    # Clear game sessions
    main_module._game_sessions.clear()
    # Ensure service is ready
    main_module._service_ready = True
    yield
    # Cleanup after test
    main_module._game_sessions.clear()


class TestNewGameEndpoint:
    """Test Phase 4.2.1: POST /api/game/new endpoint."""

    def test_subsection_4_2_1_creates_new_game_session_and_returns_200(
        self, client: TestClient
    ) -> None:
        """Test POST /api/game/new creates new game session and returns 200."""
        response = client.post("/api/game/new")

        assert response.status_code == 201
        data = response.json()
        assert "game_id" in data
        assert "game_state" in data
        assert isinstance(data["game_id"], str)
        assert len(data["game_id"]) > 0

    def test_subsection_4_2_1_returns_game_id_in_response(self, client: TestClient) -> None:
        """Test POST /api/game/new returns game_id in response."""
        response = client.post("/api/game/new")

        assert response.status_code == 201
        data = response.json()
        assert "game_id" in data
        game_id = data["game_id"]
        # Verify it's a valid UUID format (basic check)
        assert len(game_id) == 36  # UUID v4 format: 8-4-4-4-12
        assert game_id.count("-") == 4

    def test_subsection_4_2_1_returns_initial_game_state_with_move_count_0(
        self, client: TestClient
    ) -> None:
        """Test POST /api/game/new returns initial GameState with MoveCount=0, empty board."""
        response = client.post("/api/game/new")

        assert response.status_code == 201
        data = response.json()
        game_state = data["game_state"]
        assert game_state["move_count"] == 0
        # With move_count=0, current player is player_symbol (which defaults to "X")
        assert game_state["player_symbol"] == "X"
        # Verify board is empty
        board = game_state["board"]
        assert "cells" in board
        for row in board["cells"]:
            for cell in row:
                assert cell == "EMPTY"

    def test_subsection_4_2_1_accepts_optional_player_symbol_preference(
        self, client: TestClient
    ) -> None:
        """Test POST /api/game/new accepts optional player_symbol preference."""
        # Test with player_symbol="O"
        response = client.post("/api/game/new", json={"player_symbol": "O"})

        assert response.status_code == 201
        data = response.json()
        game_state = data["game_state"]
        assert game_state["player_symbol"] == "O"
        assert game_state["ai_symbol"] == "X"
        # With move_count=0, current player is player_symbol (which is "O")
        assert game_state["move_count"] == 0

    def test_subsection_4_2_1_defaults_to_x_for_player_if_not_specified(
        self, client: TestClient
    ) -> None:
        """Test POST /api/game/new defaults to X for player if not specified."""
        # Test without player_symbol (should default to "X")
        response = client.post("/api/game/new")

        assert response.status_code == 201
        data = response.json()
        game_state = data["game_state"]
        assert game_state["player_symbol"] == "X"
        assert game_state["ai_symbol"] == "O"
        # With move_count=0, current player is player_symbol (which is "X")
        assert game_state["move_count"] == 0

    def test_subsection_4_2_1_returns_503_when_service_not_ready(self, client: TestClient) -> None:
        """Test POST /api/game/new returns 503 when service is not ready (AC-5.3.1)."""
        import src.api.main as main_module

        # Set service as not ready
        main_module._service_ready = False

        response = client.post("/api/game/new")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "failure"
        assert data["error_code"] == E_SERVICE_NOT_READY
        assert "Service not ready" in data["message"]
        assert "timestamp" in data
