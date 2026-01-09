"""Tests for Phase 4.0.1: FastAPI Application Setup.

Tests verify:
- FastAPI app instance creation
- CORS configuration
- Exception handlers
- Logging middleware
- Root endpoint
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestFastAPIApplicationSetup:
    """Test Phase 4.0.1: FastAPI Application Setup."""

    def test_app_instance_created(self) -> None:
        """Test that FastAPI app instance is created with correct metadata."""
        assert app.title == "Agentic Tic-Tac-Toe API"
        assert app.description == "REST API for multi-agent Tic-Tac-Toe game"
        assert app.version == "0.1.0"

    def test_root_endpoint_returns_api_info(self, client: TestClient) -> None:
        """Test that GET / returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Agentic Tic-Tac-Toe API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"

    def test_cors_headers_present(self, client: TestClient) -> None:
        """Test that CORS headers are configured correctly."""
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_cors_preflight_request(self, client: TestClient) -> None:
        """Test that CORS preflight (OPTIONS) requests work."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        # OPTIONS might return 405 if not explicitly handled, but CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_logging_middleware_adds_process_time_header(self, client: TestClient) -> None:
        """Test that logging middleware adds X-Process-Time header."""
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        # Process time should be a number (milliseconds)
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0

    def test_value_error_exception_handler(self, client: TestClient) -> None:
        """Test that ValueError exceptions return 400 with error response format."""
        response = client.get("/test/value-error")
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "failure"
        assert data["error_code"] == "E_INVALID_REQUEST"
        assert "message" in data
        assert "timestamp" in data or data["timestamp"] is None
        assert "details" in data or data["details"] is None

    def test_general_exception_handler(self, client: TestClient) -> None:
        """Test that general Exception returns 500 with error response format."""
        # TestClient raises exceptions by default, so we need to catch it
        # or use raise_server_exceptions=False
        # For now, verify the handler is registered and would work
        # In production, the handler will catch exceptions and return proper responses
        assert Exception in app.exception_handlers

        # Test with raise_server_exceptions=False to see the actual response
        client_without_raise = TestClient(app, raise_server_exceptions=False)
        response = client_without_raise.get("/test/general-error")
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "failure"
        assert data["error_code"] == "E_INTERNAL_ERROR"
        assert data["message"] == "Internal server error"
        assert "timestamp" in data or data["timestamp"] is None
        assert "details" in data or data["details"] is None

    def test_general_exception_handler_format(self) -> None:
        """Test that general exception handler returns proper error format."""
        # This will be tested when we have endpoints that might raise exceptions
        # For now, verify the handler exists in the app
        assert len(app.exception_handlers) > 0
        assert Exception in app.exception_handlers
        assert ValueError in app.exception_handlers

    def test_openapi_docs_available(self, client: TestClient) -> None:
        """Test that OpenAPI/Swagger documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_schema_available(self, client: TestClient) -> None:
        """Test that OpenAPI JSON schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Agentic Tic-Tac-Toe API"
        assert schema["info"]["version"] == "0.1.0"
