---
name: api-endpoint-implementation
description: Defines the pattern for implementing FastAPI REST endpoints, including route definition, request/response models, error handling, and integration tests. Use when implementing any API endpoint to ensure consistency with existing endpoints.
license: MIT
metadata:
  version: "1.0.0"
  framework: "FastAPI"
  conventions: "Pydantic models, TestClient, error codes"
---

# API Endpoint Implementation Pattern

This skill defines how to implement FastAPI REST endpoints following established patterns.

## Endpoint Structure

### Basic Endpoint

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.api.models import RequestModel, ResponseModel

@app.get("/endpoint")
async def endpoint_handler() -> JSONResponse:
    """Endpoint description.

    Returns:
        JSONResponse with status 200 and data
    """
    # Implementation
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "field": "value"
        }
    )
```

### Endpoint with Request Body

```python
from src.api.models import MoveRequest, MoveResponse

@app.post("/api/game/move")
async def make_move(request: MoveRequest) -> JSONResponse:
    """Make a move in the game.

    Args:
        request: Move request with row and col

    Returns:
        JSONResponse with updated game state and AI move
    """
    # Validate and process
    # Return response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=MoveResponse(...).model_dump()
    )
```

## Request/Response Models

### Request Models

Define in `src/api/models.py`:

```python
from pydantic import BaseModel, Field

class MoveRequest(BaseModel):
    """Request model for making a move."""

    row: int = Field(ge=0, le=2, description="Row index (0-2)")
    col: int = Field(ge=0, le=2, description="Column index (0-2)")
```

### Response Models

```python
class MoveResponse(BaseModel):
    """Response model for move endpoint."""

    success: bool
    position: Position | None = None
    updated_game_state: GameState | None = None
    ai_move_execution: MoveExecution | None = None
    error_message: str | None = None
    fallback_used: bool = False
    total_execution_time_ms: float | None = None
```

## Error Handling

### Standard Error Response

Use error codes from `src/domain/errors.py`:

```python
from src.domain.errors import E_INVALID_REQUEST, E_SERVICE_NOT_READY

@app.post("/endpoint")
async def endpoint() -> JSONResponse:
    """Endpoint handler."""
    try:
        # Implementation
        return JSONResponse(status_code=200, content={...})
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "failure",
                "error_code": "E_INVALID_REQUEST",
                "message": str(e),
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "details": None
            }
        )
```

### Error Code to HTTP Status Mapping

Follow Section 5.6 mapping:

- `E_POSITION_OUT_OF_BOUNDS` → 400 Bad Request
- `E_CELL_OCCUPIED` → 409 Conflict
- `E_GAME_ALREADY_OVER` → 409 Conflict
- `E_INVALID_REQUEST` → 400 Bad Request
- `E_SERVICE_NOT_READY` → 503 Service Unavailable
- `E_LLM_TIMEOUT` → 504 Gateway Timeout
- `E_INTERNAL_ERROR` → 500 Internal Server Error

## Integration Tests

### Test Structure

```python
"""Tests for Phase X.Y.Z: GET /endpoint endpoint.

Tests verify:
- Endpoint returns 200 with correct data
- Error handling works correctly
- Response format matches schema
"""

import pytest
from fastapi.testclient import TestClient

from src import api

@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(api.main.app)

class TestEndpoint:
    """Test Phase X.Y.Z: GET /endpoint endpoint."""

    def test_get_endpoint_returns_200(self, client: TestClient) -> None:
        """Test GET /endpoint returns 200 with correct data."""
        response = client.get("/endpoint")

        assert response.status_code == 200
        data = response.json()
        assert data["field"] == expected_value

    def test_endpoint_handles_errors(self, client: TestClient) -> None:
        """Test endpoint handles errors correctly."""
        response = client.post("/endpoint", json={"invalid": "data"})

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "failure"
        assert data["error_code"] == "E_INVALID_REQUEST"
```

## Health and Ready Endpoints

### Health Endpoint Pattern

```python
# Track server state
_server_start_time: float | None = None
_server_shutting_down: bool = False

@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint (liveness probe)."""
    if _server_shutting_down:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", ...}
        )

    uptime_seconds = round(time.time() - _server_start_time, 2)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "uptime_seconds": uptime_seconds,
            "version": "0.1.0"
        }
    )
```

### Ready Endpoint Pattern

```python
@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness probe - checks dependencies."""
    checks = {
        "game_engine": "ok",
        "agents": "ok",
        "llm_configuration": "ok"  # Optional in Phase 4
    }

    if all(v == "ok" for v in checks.values()):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready", "checks": checks}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks}
        )
```

## Game Control Endpoints

### POST /api/game/new

```python
@app.post("/api/game/new")
async def new_game(player_symbol: str = "X") -> JSONResponse:
    """Create new game session."""
    game_engine = GameEngine()
    game_state = game_engine.get_current_state()
    game_id = str(uuid.uuid4())

    # Store game session (implementation specific)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "game_id": game_id,
            "game_state": game_state.model_dump()
        }
    )
```

### POST /api/game/move

```python
@app.post("/api/game/move")
async def make_move(request: MoveRequest, game_id: str) -> JSONResponse:
    """Make a move in the game."""
    # Get game session
    # Validate move
    # Execute player move
    # Run agent pipeline for AI move
    # Return updated state
```

## Testing Requirements

### Minimum Test Coverage

Each endpoint should have tests for:

1. **Success case**: Returns 200 with correct data
2. **Error case**: Returns appropriate error status
3. **Request validation**: Invalid requests are rejected
4. **Response format**: Matches defined schema
5. **Edge cases**: Boundary conditions and error scenarios

### Test File Location

- API foundation tests: `tests/integration/api/test_api_foundation.py`
- Endpoint-specific tests: `tests/integration/api/test_api_<endpoint>.py`
- Model tests: `tests/integration/api/test_api_models.py`
- Error tests: `tests/integration/api/test_api_errors.py`

## Best Practices

1. **Use type hints**: All functions should have type annotations
2. **Document endpoints**: Include docstrings describing behavior
3. **Validate inputs**: Use Pydantic models for validation
4. **Handle errors**: Return appropriate error codes and status codes
5. **Test thoroughly**: Write tests for success and error cases
6. **Follow conventions**: Use established patterns from existing endpoints
7. **Return consistent format**: Use standard response models

## Common Patterns

### Stateful Endpoints

For endpoints that need to track state:

```python
# Use global state or session storage
_game_sessions: dict[str, GameEngine] = {}

@app.post("/api/game/move")
async def make_move(request: MoveRequest, game_id: str) -> JSONResponse:
    if game_id not in _game_sessions:
        return JSONResponse(status_code=404, content={"error": "Game not found"})

    game_engine = _game_sessions[game_id]
    # Use game_engine
```

### Async Operations

For endpoints that trigger async operations:

```python
@app.post("/api/game/move")
async def make_move(request: MoveRequest) -> JSONResponse:
    """Make move and trigger AI agent pipeline."""
    # Execute player move (synchronous)
    game_engine.make_move(position)

    # Trigger AI pipeline (can be async)
    if game_engine.get_current_state().status == "IN_PROGRESS":
        pipeline_result = await pipeline.execute_pipeline(game_state)
        # Handle result
```
