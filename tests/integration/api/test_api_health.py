"""Tests for Phase 4.1.1: GET /health endpoint.

Tests verify:
- Health endpoint returns 200 with status="healthy" when server is running
- Response includes timestamp in ISO 8601 format
- Response includes uptime_seconds with 2 decimal precision
- Response completes within 100ms
- Returns 503 with status="unhealthy" when shutting down
"""

import time

import pytest
from fastapi.testclient import TestClient

from src import api


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(api.main.app)


@pytest.fixture(autouse=True)
def reset_server_state() -> None:
    """Reset server state before each test."""
    import src.api.main as main_module

    main_module._server_start_time = time.time()
    main_module._server_shutting_down = False
    yield
    # Cleanup after test
    main_module._server_shutting_down = False


class TestHealthEndpoint:
    """Test Phase 4.1.1: GET /health endpoint."""

    def test_get_health_returns_200_with_healthy_status(self, client: TestClient) -> None:
        """Test GET /health returns 200 with status='healthy' when server is running."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    def test_get_health_response_includes_timestamp_iso_8601_format(
        self, client: TestClient
    ) -> None:
        """Test GET /health response includes timestamp in ISO 8601 format."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        timestamp = data["timestamp"]

        # Validate ISO 8601 format (ends with Z or has timezone)
        assert timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp

        # Validate it's parseable
        from datetime import datetime

        # Handle Z suffix by replacing with +00:00 for parsing
        timestamp_parsed = timestamp.replace("Z", "+00:00")
        datetime.fromisoformat(timestamp_parsed)

    def test_get_health_response_includes_uptime_seconds_with_2_decimal_precision(
        self, client: TestClient
    ) -> None:
        """Test GET /health response includes uptime_seconds as float with 2 decimal precision."""
        # Small delay to ensure uptime > 0
        time.sleep(0.1)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        uptime_seconds = data["uptime_seconds"]

        assert isinstance(uptime_seconds, (int, float))
        assert uptime_seconds >= 0

        # Check precision: should have at most 2 decimal places
        uptime_str = str(uptime_seconds)
        if "." in uptime_str:
            decimal_part = uptime_str.split(".")[1]
            assert (
                len(decimal_part) <= 2
            ), f"uptime_seconds should have max 2 decimals, got {uptime_str}"

    def test_get_health_response_completes_within_100ms(self, client: TestClient) -> None:
        """Test GET /health response completes within 100ms (AC-5.1.2)."""
        start_time = time.time()
        response = client.get("/health")
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        assert response.status_code == 200
        # Allow some buffer for test execution overhead, but should be much less than 100ms
        assert elapsed_time < 100, f"Health check took {elapsed_time}ms, should be < 100ms"

    def test_get_health_returns_503_when_shutting_down(self, client: TestClient) -> None:
        """Test GET /health returns 503 with status='unhealthy' when shutting down (AC-5.1.3)."""
        import src.api.main as main_module

        # Simulate shutdown state
        main_module._server_shutting_down = True

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "timestamp" in data
        assert "message" in data
        assert "shutting down" in data["message"].lower()

        # Reset for other tests (fixture will also clean up, but explicit here)
        main_module._server_shutting_down = False
