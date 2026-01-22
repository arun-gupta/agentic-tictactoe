"""Test fixtures for contract tests."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client with service ready state."""
    # Set service ready state for testing
    import src.api.main as main_module

    # Ensure service is ready for contract tests
    main_module._service_ready = True

    return TestClient(app)


@pytest.fixture
def openapi_schema(client: TestClient) -> dict[str, Any]:
    """Get the OpenAPI schema from the running API."""
    response = client.get("/openapi.json")
    assert response.status_code == 200, f"Failed to get OpenAPI schema: {response.text}"
    return dict(response.json())
