"""Response contract validation tests.

Validates that API responses deserialize correctly to Pydantic models.
Ensures API implementation matches the contract defined by response models.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.models import AgentStatus, ErrorResponse, GameStatusResponse, NewGameResponse

pytestmark = pytest.mark.contract


def test_new_game_response_deserializes_correctly(client: TestClient) -> None:
    """Test that POST /api/game/new response deserializes to NewGameResponse."""
    response = client.post("/api/game/new", json={})

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    # Validate response deserializes to NewGameResponse
    try:
        new_game_response = NewGameResponse.model_validate(response.json())
        assert new_game_response.game_id is not None
        assert new_game_response.game_state is not None
        assert new_game_response.game_state.move_count == 0
    except Exception as e:
        pytest.fail(f"Failed to deserialize NewGameResponse: {e}")


def test_error_response_deserializes_correctly(client: TestClient) -> None:
    """Test that error responses deserialize to ErrorResponse."""
    # Request a non-existent game to get a 404 error
    response = client.get("/api/game/status?game_id=00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    # Validate response deserializes to ErrorResponse
    try:
        error_response = ErrorResponse.model_validate(response.json())
        assert error_response.status == "failure"
        assert error_response.error_code is not None
        assert error_response.message is not None
        assert error_response.timestamp is not None
    except Exception as e:
        pytest.fail(f"Failed to deserialize ErrorResponse: {e}")


def test_agent_status_deserializes_correctly(client: TestClient) -> None:
    """Test that GET /api/agents/{name}/status response deserializes to AgentStatus."""
    # Test with a valid agent name
    response = client.get("/api/agents/scout/status")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Validate response deserializes to AgentStatus
    try:
        agent_status = AgentStatus.model_validate(response.json())
        assert agent_status.status in ["idle", "processing", "success", "failed"]
    except Exception as e:
        pytest.fail(f"Failed to deserialize AgentStatus: {e}")


def test_game_status_response_deserializes_correctly(client: TestClient) -> None:
    """Test that GET /api/game/status response deserializes to GameStatusResponse."""
    # First create a game
    new_game_response = client.post("/api/game/new", json={})
    assert new_game_response.status_code == 201
    game_id = new_game_response.json()["game_id"]

    # Then get game status
    response = client.get(f"/api/game/status?game_id={game_id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Validate response deserializes to GameStatusResponse
    try:
        game_status_response = GameStatusResponse.model_validate(response.json())
        assert game_status_response.game_state is not None
        # agent_status and metrics are optional, so we don't assert they exist
    except Exception as e:
        pytest.fail(f"Failed to deserialize GameStatusResponse: {e}")


def test_error_response_for_invalid_agent_name(client: TestClient) -> None:
    """Test that invalid agent name returns ErrorResponse."""
    response = client.get("/api/agents/invalid-agent/status")

    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    # Validate response deserializes to ErrorResponse
    try:
        error_response = ErrorResponse.model_validate(response.json())
        assert error_response.status == "failure"
        assert error_response.error_code is not None
    except Exception as e:
        pytest.fail(f"Failed to deserialize ErrorResponse for invalid agent: {e}")
