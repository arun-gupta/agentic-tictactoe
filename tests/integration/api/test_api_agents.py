"""Integration tests for API agent status endpoints.

Phase 4.3.1: GET /api/agents/{agent_name}/status endpoint
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import _agent_status, app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    import src.api.main as main_module

    # Ensure service is ready for tests
    main_module._service_ready = True
    return TestClient(app)


class TestAgentStatusEndpoint:
    """Test Phase 4.3.1: GET /api/agents/{agent_name}/status endpoint."""

    @pytest.fixture
    def reset_agent_status(self) -> None:
        """Reset agent status to idle before each test."""
        global _agent_status
        for agent_name in ["scout", "strategist", "executor"]:
            _agent_status[agent_name] = {
                "status": "idle",
                "start_time": None,
                "execution_time_ms": None,
                "success": None,
                "error_message": None,
            }
        yield
        # Cleanup after test
        for agent_name in ["scout", "strategist", "executor"]:
            _agent_status[agent_name] = {
                "status": "idle",
                "start_time": None,
                "execution_time_ms": None,
                "success": None,
                "error_message": None,
            }

    def test_subsection_4_3_1_returns_200_with_status_idle_when_agent_idle(
        self, client: TestClient, reset_agent_status: None
    ) -> None:
        """Test GET /api/agents/scout/status returns 200 with status='idle' when agent idle (AC-5.8.1)."""
        response = client.get("/api/agents/scout/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "idle"
        assert data["elapsed_time_ms"] is None
        assert data["execution_time_ms"] is None
        assert data["success"] is None
        assert data["error_message"] is None

    def test_subsection_4_3_1_returns_status_processing_with_elapsed_time_ms_when_running(
        self, client: TestClient, reset_agent_status: None
    ) -> None:
        """Test GET /api/agents/scout/status returns status='processing' with elapsed_time_ms when running (AC-5.8.2)."""
        global _agent_status
        import time

        # Set agent to processing state
        _agent_status["scout"]["status"] = "processing"
        _agent_status["scout"]["start_time"] = time.time() - 0.5  # 0.5 seconds ago

        response = client.get("/api/agents/scout/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["elapsed_time_ms"] is not None
        assert isinstance(data["elapsed_time_ms"], float)
        assert data["elapsed_time_ms"] >= 450  # Approximately 500ms (0.5 seconds)
        assert data["elapsed_time_ms"] < 600  # Allow some margin for test execution time

    def test_subsection_4_3_1_returns_execution_time_ms_and_success_true_when_completed(
        self, client: TestClient, reset_agent_status: None
    ) -> None:
        """Test GET /api/agents/strategist/status returns execution_time_ms and success=true when completed (AC-5.8.3)."""
        global _agent_status

        # Set agent to success state
        _agent_status["strategist"]["status"] = "success"
        _agent_status["strategist"]["execution_time_ms"] = 123.45
        _agent_status["strategist"]["success"] = True
        _agent_status["strategist"]["error_message"] = None

        response = client.get("/api/agents/strategist/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["execution_time_ms"] == 123.45
        assert data["success"] is True
        assert data["error_message"] is None
        assert data["elapsed_time_ms"] is None  # Not processing, so no elapsed time

    def test_subsection_4_3_1_returns_error_message_and_success_false_when_failed_timed_out(
        self, client: TestClient, reset_agent_status: None
    ) -> None:
        """Test GET /api/agents/executor/status returns error_message and success=false when failed/timed out (AC-5.8.4)."""
        global _agent_status

        # Set agent to failed state
        _agent_status["executor"]["status"] = "failed"
        _agent_status["executor"]["execution_time_ms"] = 5000.0
        _agent_status["executor"]["success"] = False
        _agent_status["executor"]["error_message"] = "Agent exceeded timeout"

        response = client.get("/api/agents/executor/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["execution_time_ms"] == 5000.0
        assert data["success"] is False
        assert data["error_message"] == "Agent exceeded timeout"
        assert data["elapsed_time_ms"] is None  # Not processing, so no elapsed time

    def test_subsection_4_3_1_returns_404_for_invalid_agent_name(
        self, client: TestClient, reset_agent_status: None
    ) -> None:
        """Test GET /api/agents/{invalid}/status returns 404 for invalid agent name (AC-5.8.5)."""
        response = client.get("/api/agents/invalid_agent/status")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "failure"
        assert data["error_code"] == "E_AGENT_NOT_FOUND"
        assert "Agent 'invalid_agent' not found" in data["message"]
        assert "valid_agents" in data["details"]
        assert "scout" in data["details"]["valid_agents"]
        assert "strategist" in data["details"]["valid_agents"]
        assert "executor" in data["details"]["valid_agents"]

    def test_subsection_4_3_1_updates_agent_status_after_pipeline_execution(
        self, client: TestClient, reset_agent_status: None
    ) -> None:
        """Test that agent status is updated after pipeline execution."""
        global _agent_status

        # Create a new game
        new_game_response = client.post("/api/game/new")
        assert new_game_response.status_code == 201
        game_id = new_game_response.json()["game_id"]

        # Initially all agents should be idle
        scout_response = client.get("/api/agents/scout/status")
        assert scout_response.json()["status"] == "idle"

        # Make a move to trigger the pipeline
        move_response = client.post("/api/game/move", json={"game_id": game_id, "row": 1, "col": 1})
        assert move_response.status_code == 200

        # After pipeline execution, agents should be in success state (if pipeline succeeded)
        scout_response = client.get("/api/agents/scout/status")
        scout_data = scout_response.json()
        assert scout_data["status"] in ["success", "failed"]  # Pipeline completed
        if scout_data["status"] == "success":
            assert scout_data["execution_time_ms"] is not None
            assert scout_data["success"] is True
        else:
            assert scout_data["error_message"] is not None
            assert scout_data["success"] is False

        # Check other agents too
        strategist_response = client.get("/api/agents/strategist/status")
        executor_response = client.get("/api/agents/executor/status")
        assert strategist_response.json()["status"] in ["success", "failed"]
        assert executor_response.json()["status"] in ["success", "failed"]
