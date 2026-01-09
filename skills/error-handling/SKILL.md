---
name: error-handling
description: Defines error handling patterns using custom error codes, AgentResult wrapper, and HTTP status code mapping. Use when implementing error handling in agents, game engine, or API endpoints to ensure consistent error responses.
license: MIT
metadata:
  version: "1.0.0"
  error_system: "custom error codes, AgentResult, HTTP mapping"
---

# Error Handling Pattern

This skill defines how to handle errors consistently across the codebase.

## Error Code System

### Error Code Definition

All error codes are defined in `src/domain/errors.py`:

```python
# Game Engine Errors
E_POSITION_OUT_OF_BOUNDS = "E_POSITION_OUT_OF_BOUNDS"
E_CELL_OCCUPIED = "E_CELL_OCCUPIED"
E_GAME_ALREADY_OVER = "E_GAME_ALREADY_OVER"
E_INVALID_PLAYER = "E_INVALID_PLAYER"
E_INVALID_TURN = "E_INVALID_TURN"

# Agent Errors
E_INVALID_EXECUTION_TIME = "E_INVALID_EXECUTION_TIME"
E_MISSING_REASONING = "E_MISSING_REASONING"
E_LLM_TIMEOUT = "E_LLM_TIMEOUT"

# API Errors
E_INVALID_REQUEST = "E_INVALID_REQUEST"
E_INTERNAL_ERROR = "E_INTERNAL_ERROR"
E_SERVICE_NOT_READY = "E_SERVICE_NOT_READY"
```

### Using Error Codes

```python
from src.domain.errors import E_POSITION_OUT_OF_BOUNDS

if not (0 <= row <= 2) or not (0 <= col <= 2):
    raise ValueError(
        f"Position ({row}, {col}) is out of bounds. "
        f"Error code: {E_POSITION_OUT_OF_BOUNDS}"
    )
```

## AgentResult Pattern

### AgentResult Structure

For agent operations, use `AgentResult[T]` wrapper:

```python
from src.domain.result import AgentResult

# Success case
result = AgentResult.success(data=move_execution)

# Error case
result = AgentResult.error(
    error_code="E_LLM_TIMEOUT",
    error_message="Agent exceeded timeout",
    metadata={"timeout_ms": 5000}
)
```

### AgentResult Usage

```python
def analyze(game_state: GameState) -> AgentResult[BoardAnalysis]:
    """Analyze board state."""
    try:
        analysis = perform_analysis(game_state)
        return AgentResult.success(data=analysis)
    except TimeoutError as e:
        return AgentResult.error(
            error_code="E_LLM_TIMEOUT",
            error_message=f"Analysis exceeded timeout: {e}",
            metadata={"timeout_seconds": 10}
        )
    except Exception as e:
        return AgentResult.error(
            error_code="E_INTERNAL_ERROR",
            error_message=f"Analysis failed: {e}"
        )
```

### Checking AgentResult

```python
result = agent.analyze(game_state)

if result.success:
    analysis = result.data  # Type-safe access
    # Use analysis
else:
    error_code = result.error_code
    error_message = result.error_message
    # Handle error
```

## API Error Responses

### Standard Error Response Format

Follow Section 5.4 error response schema:

```python
from fastapi.responses import JSONResponse
from fastapi import status
from datetime import UTC, datetime

def error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: dict | None = None
) -> JSONResponse:
    """Create standard error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "failure",
            "error_code": error_code,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "details": details
        }
    )
```

### HTTP Status Code Mapping

Follow Section 5.6 mapping:

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `E_POSITION_OUT_OF_BOUNDS` | 400 Bad Request | Invalid position coordinates |
| `E_CELL_OCCUPIED` | 409 Conflict | Cell already occupied |
| `E_GAME_ALREADY_OVER` | 409 Conflict | Game has ended |
| `E_INVALID_REQUEST` | 400 Bad Request | Invalid request format |
| `E_SERVICE_NOT_READY` | 503 Service Unavailable | Service not ready |
| `E_LLM_TIMEOUT` | 504 Gateway Timeout | LLM/Agent timeout |
| `E_INTERNAL_ERROR` | 500 Internal Server Error | Unexpected error |

### Exception Handlers

Register exception handlers in FastAPI app:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import status

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions."""
    # Extract error code from message if present
    error_code = "E_INVALID_REQUEST"
    if "Error code:" in str(exc):
        error_code = str(exc).split("Error code:")[-1].strip()

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "failure",
            "error_code": error_code,
            "message": str(exc),
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "details": None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "failure",
            "error_code": "E_INTERNAL_ERROR",
            "message": "Internal server error",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "details": None
        }
    )
```

## Game Engine Error Handling

### Move Validation Errors

```python
def validate_move(self, position: Position) -> None:
    """Validate move and raise ValueError with error code."""
    # Bounds check
    if not (0 <= position.row <= 2) or not (0 <= position.col <= 2):
        raise ValueError(
            f"Position ({position.row}, {position.col}) is out of bounds. "
            f"Error code: {E_POSITION_OUT_OF_BOUNDS}"
        )

    # Cell check
    if not self.board.is_empty(position):
        raise ValueError(
            f"Cell ({position.row}, {position.col}) is already occupied. "
            f"Error code: {E_CELL_OCCUPIED}"
        )

    # Game state check
    if self.game_state.status != "IN_PROGRESS":
        raise ValueError(
            f"Game is already over (status: {self.game_state.status}). "
            f"Error code: {E_GAME_ALREADY_OVER}"
        )
```

### Error Propagation

```python
def make_move(self, position: Position) -> MoveResult:
    """Make a move, handling errors."""
    try:
        self.validate_move(position)
        # Execute move
        return MoveResult(success=True, ...)
    except ValueError as e:
        # Extract error code from exception message
        error_code = extract_error_code(str(e))
        return MoveResult(success=False, error_code=error_code, error_message=str(e))
```

## Agent Error Handling

### Timeout Handling

```python
def execute_with_timeout(self, func, timeout: float) -> AgentResult[T]:
    """Execute function with timeout."""
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(func)
            result = future.result(timeout=timeout)
            return AgentResult.success(data=result)
    except TimeoutError:
        return AgentResult.error(
            error_code="E_LLM_TIMEOUT",
            error_message=f"Operation exceeded timeout of {timeout}s",
            metadata={"timeout_seconds": timeout}
        )
```

### Fallback Strategies

```python
def execute_pipeline(self, game_state: GameState) -> AgentResult[MoveExecution]:
    """Execute agent pipeline with fallbacks."""
    # Try Scout
    scout_result = self.scout.analyze(game_state)
    if not scout_result.success:
        # Fallback to rule-based analysis
        return self._fallback_rule_based_analysis(game_state)

    # Continue pipeline...
```

## Testing Error Handling

### Testing Error Codes

```python
def test_returns_correct_error_code(self) -> None:
    """Test returns correct error code."""
    result = component.operation(invalid_input)

    assert result.success is False
    assert result.error_code == "E_ERROR_CODE"
    assert result.error_message is not None
```

### Testing HTTP Error Responses

```python
def test_endpoint_returns_correct_error_status(self, client: TestClient) -> None:
    """Test endpoint returns correct HTTP status for error."""
    response = client.post("/endpoint", json={"invalid": "data"})

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "failure"
    assert data["error_code"] == "E_INVALID_REQUEST"
    assert "timestamp" in data
```

### Testing Error Message Format

```python
def test_error_message_includes_error_code(self) -> None:
    """Test error message includes error code."""
    try:
        component.operation(invalid_input)
    except ValueError as e:
        assert "Error code: E_ERROR_CODE" in str(e)
```

## Best Practices

1. **Use error codes**: Always include error codes in error messages
2. **Consistent format**: Follow established error response formats
3. **Log errors**: Log unexpected errors with full context
4. **Type safety**: Use `AgentResult` for type-safe error handling
5. **Map to HTTP**: Map error codes to appropriate HTTP status codes
6. **User-friendly messages**: Provide clear, actionable error messages
7. **Include context**: Add metadata for debugging when appropriate

## Error Code Naming

### Convention

- Prefix: `E_` (Error)
- Format: `E_<CATEGORY>_<DESCRIPTION>`
- Uppercase with underscores

### Categories

- `POSITION_*`: Position/coordinate errors
- `CELL_*`: Cell state errors
- `GAME_*`: Game state errors
- `INVALID_*`: Validation errors
- `LLM_*`: LLM/Agent errors
- `SERVICE_*`: Service availability errors
- `INTERNAL_*`: Unexpected errors

## Common Patterns

### Error Aggregation

```python
def validate_multiple_things(self) -> list[str]:
    """Validate multiple things and return all errors."""
    errors = []

    if not condition1:
        errors.append("E_ERROR_1")
    if not condition2:
        errors.append("E_ERROR_2")

    return errors
```

### Error with Details

```python
AgentResult.error(
    error_code="E_VALIDATION_ERROR",
    error_message="Validation failed",
    metadata={
        "field": "row",
        "expected": "0-2",
        "actual": 5
    }
)
```
