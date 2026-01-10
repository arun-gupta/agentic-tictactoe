"""FastAPI application setup and routes.

Phase 4.0.1: FastAPI Application Setup
- Create FastAPI app instance
- Configure CORS (Section 5)
- Set up exception handlers
- Configure logging middleware

Phase 4.1.1: GET /health endpoint
- Return basic health status with uptime tracking

Phase 4.1.2: GET /ready endpoint
- Check game engine is initialized
- Check agent system is ready
- Verify LLM providers are configured (optional in Phase 4)
- Return detailed readiness status

Phase 4.2.1: POST /api/game/new endpoint
- Create new game session
- Initialize game engine
- Return game ID and initial state
- Optionally accept player symbol preference
"""

import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.agents.pipeline import AgentPipeline
from src.api.models import (
    ErrorResponse,
    GameStatusResponse,
    MoveRequest,
    MoveResponse,
    NewGameRequest,
    NewGameResponse,
)
from src.domain.errors import (
    E_CELL_OCCUPIED,
    E_GAME_ALREADY_OVER,
    E_INTERNAL_ERROR,
    E_INVALID_PLAYER,
    E_INVALID_REQUEST,
    E_INVALID_TURN,
    E_MOVE_OUT_OF_BOUNDS,
    E_SERVICE_NOT_READY,
)
from src.domain.models import PlayerSymbol, Position
from src.game.engine import GameEngine
from src.utils.logging_config import get_logger, setup_logging

logger = get_logger("api.main")


def _get_error_message(error_code: str | None) -> str:
    """Get human-readable error message from error code.

    Args:
        error_code: Error code string or None.

    Returns:
        Human-readable error message.
    """
    error_messages = {
        E_MOVE_OUT_OF_BOUNDS: "Position out of bounds (0-2 only)",
        E_CELL_OCCUPIED: "Cell already occupied",
        E_GAME_ALREADY_OVER: "Game is already over",
        E_INVALID_PLAYER: "Invalid player symbol",
        E_INVALID_TURN: "Not your turn",
        E_SERVICE_NOT_READY: "Service not ready. Check /ready endpoint.",
        E_INVALID_REQUEST: "Invalid request",
        E_INTERNAL_ERROR: "Internal server error",
    }
    if error_code:
        return error_messages.get(error_code, f"Error: {error_code}")
    return "Unknown error"


# Server state tracking for health endpoint
_server_start_time: float | None = None
_server_shutting_down: bool = False

# Service readiness tracking
_service_ready: bool = False

# Game session storage (in-memory for Phase 4)
# Maps game_id (UUID string) to GameEngine instance
_game_sessions: dict[str, GameEngine] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager for FastAPI app startup/shutdown."""
    global _server_start_time, _server_shutting_down, _service_ready

    # Startup
    _server_start_time = time.time()
    _server_shutting_down = False
    _service_ready = False
    logger.info("Starting API server", extra={"event_type": "startup"})
    setup_logging(log_level="INFO", enable_file_logging=True)

    # Perform readiness checks
    _service_ready = _check_service_readiness()
    if _service_ready:
        logger.info("Service is ready", extra={"event_type": "startup"})
    else:
        logger.warning("Service is not ready", extra={"event_type": "startup"})

    yield
    # Shutdown
    _server_shutting_down = True
    _service_ready = False
    logger.info("Shutting down API server", extra={"event_type": "shutdown"})


# Create FastAPI app instance
app = FastAPI(
    title="Agentic Tic-Tac-Toe API",
    description="REST API for multi-agent Tic-Tac-Toe game",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS (Section 5 - CORS support for web clients)
# Allow all origins in development, restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions (e.g., validation errors)."""
    logger.warning(
        "ValueError in request",
        extra={
            "event_type": "error",
            "error": {"message": str(exc), "type": "ValueError"},
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "failure",
            "error_code": "E_INVALID_REQUEST",
            "message": str(exc),
            "timestamp": None,  # Will be set by middleware if needed
            "details": None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "Unhandled exception in request",
        extra={
            "event_type": "error",
            "error": {
                "message": str(exc),
                "type": type(exc).__name__,
            },
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "failure",
            "error_code": "E_INTERNAL_ERROR",
            "message": "Internal server error",
            "timestamp": None,
            "details": None,
        },
    )


# Logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next: Any) -> Any:
    """Log all HTTP requests and responses."""
    import time

    start_time = time.time()

    # Log request
    logger.info(
        "Request received",
        extra={
            "event_type": "request",
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client": request.client.host if request.client else None,
        },
    )

    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            extra={
                "event_type": "response",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            },
        )

        # Add process time header
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        return response

    except Exception:
        # Don't log here - let exception handlers log it
        # Just re-raise so FastAPI's exception handlers can catch it
        raise


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - API information."""
    return {
        "name": "Agentic Tic-Tac-Toe API",
        "version": "0.1.0",
        "status": "running",
    }


def _check_game_engine() -> tuple[str, str | None]:
    """Check if game engine can be initialized.

    Returns:
        Tuple of (status, error_message). Status is "ok" or "error".
    """
    try:
        from src.game.engine import GameEngine

        # Try to instantiate game engine
        engine = GameEngine()
        # Try to get current state to verify it works
        engine.get_current_state()
        return "ok", None
    except Exception as e:
        logger.error(f"Game engine check failed: {e}", exc_info=True)
        return "error", str(e)


def _check_agent_system() -> tuple[str, str | None]:
    """Check if agent system can be initialized.

    Returns:
        Tuple of (status, error_message). Status is "ok" or "error".
    """
    try:
        from src.agents.pipeline import AgentPipeline

        # Try to instantiate agent pipeline
        pipeline = AgentPipeline()
        # Verify agents are initialized
        assert pipeline.scout is not None
        assert pipeline.strategist is not None
        assert pipeline.executor is not None
        return "ok", None
    except Exception as e:
        logger.error(f"Agent system check failed: {e}", exc_info=True)
        return "error", str(e)


def _check_llm_configuration() -> tuple[str, str | None]:
    """Check if LLM configuration is available.

    For Phase 4, LLM configuration is optional, so this check doesn't block readiness.

    Returns:
        Tuple of (status, error_message). Status is "ok", "not_configured", or "error".
    """
    # Check for OpenAI key
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if openai_key or anthropic_key or google_key:
        return "ok", None
    else:
        # In Phase 4, LLM is optional, so return "not_configured" instead of "error"
        return "not_configured", "No LLM API keys configured (optional in Phase 4)"


def _check_configuration() -> tuple[str, str | None]:
    """Check if basic configuration is valid.

    Returns:
        Tuple of (status, error_message). Status is "ok" or "error".
    """
    try:
        # Basic configuration validation
        # For Phase 4, we can just verify the app is configured correctly
        # More checks can be added later
        return "ok", None
    except Exception as e:
        logger.error(f"Configuration check failed: {e}", exc_info=True)
        return "error", str(e)


def _check_service_readiness() -> bool:
    """Check if service is ready by running all checks.

    Returns:
        True if all required checks pass, False otherwise.
    """
    game_engine_status, _ = _check_game_engine()
    agent_system_status, _ = _check_agent_system()
    configuration_status, _ = _check_configuration()

    # LLM configuration is optional in Phase 4, so don't include it in readiness check
    # Required checks must all be "ok"
    required_checks = {
        "game_engine": game_engine_status,
        "agent_system": agent_system_status,
        "configuration": configuration_status,
    }

    return all(status == "ok" for status in required_checks.values())


# Health endpoint
@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint (liveness probe).

    Returns basic health status without checking dependencies.
    Must complete within 100ms (AC-5.1.2).

    Returns:
        JSONResponse with status 200 and health information if healthy,
        or status 503 if server is shutting down
    """
    global _server_start_time, _server_shutting_down

    # Check if server is shutting down (AC-5.1.3)
    if _server_shutting_down:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "message": "Server is shutting down",
            },
        )

    # Calculate uptime (AC-5.1.1)
    if _server_start_time is None:
        uptime_seconds = 0.0
    else:
        uptime_seconds = round(time.time() - _server_start_time, 2)

    # Return healthy status (AC-5.1.1)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "uptime_seconds": uptime_seconds,
            "version": "0.1.0",
        },
    )


# Test endpoint for exception handlers (for testing only)
@app.get("/test/value-error")
async def test_value_error() -> None:
    """Test endpoint that raises ValueError (for testing exception handlers)."""
    raise ValueError("Test ValueError for exception handler")


@app.get("/test/general-error")
async def test_general_error() -> None:
    """Test endpoint that raises general Exception (for testing exception handlers)."""
    raise RuntimeError("Test RuntimeError for exception handler")


# Ready endpoint
@app.get("/ready")
async def ready() -> JSONResponse:
    """Readiness check endpoint (readiness probe).

    Checks dependencies and configuration to verify service is ready to accept requests.
    Returns 200 if all required checks pass, 503 otherwise.

    Required checks (must all pass):
    - Game engine can be initialized
    - Agent system can be initialized
    - Configuration is valid

    Optional checks (don't block readiness in Phase 4):
    - LLM configuration (checked but doesn't block)

    Returns:
        JSONResponse with status 200 if ready, or status 503 if not ready
    """
    global _service_ready

    # Run all checks
    game_engine_status, game_engine_error = _check_game_engine()
    agent_system_status, agent_system_error = _check_agent_system()
    llm_config_status, llm_config_error = _check_llm_configuration()
    configuration_status, configuration_error = _check_configuration()

    checks = {
        "game_engine": game_engine_status,
        "agent_system": agent_system_status,
        "llm_configuration": llm_config_status,
        "configuration": configuration_status,
    }

    # Required checks (exclude LLM for Phase 4)
    required_checks = {
        "game_engine": game_engine_status,
        "agent_system": agent_system_status,
        "configuration": configuration_status,
    }

    # Update global service ready state
    _service_ready = all(status == "ok" for status in required_checks.values())

    # If all required checks pass, return ready
    if _service_ready:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "checks": checks,
            },
        )

    # Build error details
    errors = []
    if game_engine_status == "error":
        errors.append(
            {
                "check": "game_engine",
                "message": game_engine_error or "Game engine initialization failed",
            }
        )
    if agent_system_status == "error":
        errors.append(
            {
                "check": "agent_system",
                "message": agent_system_error or "Agent system initialization failed",
            }
        )
    if configuration_status == "error":
        errors.append(
            {
                "check": "configuration",
                "message": configuration_error or "Configuration validation failed",
            }
        )
    # LLM config doesn't add to errors if not configured (optional in Phase 4)
    if llm_config_status == "error":
        errors.append(
            {
                "check": "llm_configuration",
                "message": llm_config_error or "LLM configuration failed",
            }
        )

    # Return not ready
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "not_ready",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "checks": checks,
            "errors": errors,
        },
    )


# Game endpoints
@app.post("/api/game/new", response_model=NewGameResponse, status_code=status.HTTP_201_CREATED)
async def create_new_game(request: NewGameRequest | None = None) -> NewGameResponse | JSONResponse:
    """Create a new game session.

    Creates a new game session with a unique game_id, initializes a GameEngine,
    and returns the game_id and initial GameState.

    Args:
        request: Optional NewGameRequest with player_symbol preference. If None or
            player_symbol not specified, defaults to 'X' for player.

    Returns:
        NewGameResponse with game_id and initial GameState (MoveCount=0, empty board),
        or JSONResponse with 503 if service is not ready (AC-5.3.1).

    Raises:
        HTTPException: 503 if service is not ready (AC-5.3.1)
    """
    global _service_ready, _game_sessions

    # Check service readiness (AC-5.3.1)
    if not _service_ready:
        logger.warning(
            "Game endpoint called when service not ready",
            extra={
                "event_type": "error",
                "error_code": E_SERVICE_NOT_READY,
                "endpoint": "/api/game/new",
            },
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                status="failure",
                error_code=E_SERVICE_NOT_READY,
                message="Service not ready. Check /ready endpoint.",
                timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                details=None,
            ).model_dump(),
        )

    # Determine player symbol (default to 'X' if not specified)
    player_symbol: PlayerSymbol = "X"
    if request is not None and request.player_symbol is not None:
        player_symbol = request.player_symbol

    # Determine AI symbol (opposite of player)
    ai_symbol: PlayerSymbol = "O" if player_symbol == "X" else "X"

    # Generate unique game ID (UUID v4)
    game_id = str(uuid.uuid4())

    # Initialize game engine
    engine = GameEngine(player_symbol=player_symbol, ai_symbol=ai_symbol)

    # Store game session
    _game_sessions[game_id] = engine

    # Get initial game state
    initial_state = engine.get_current_state()

    logger.info(
        "New game created",
        extra={
            "event_type": "game_created",
            "game_id": game_id,
            "player_symbol": player_symbol,
            "ai_symbol": ai_symbol,
        },
    )

    # Return response
    return NewGameResponse(game_id=game_id, game_state=initial_state)


@app.post("/api/game/move", response_model=MoveResponse, status_code=status.HTTP_200_OK)
async def make_move(request: MoveRequest) -> MoveResponse | JSONResponse:
    """Make a player move and trigger AI response.

    Accepts a player move (row, col), validates it via the game engine,
    executes it, triggers the AI agent pipeline if the game is not over,
    and returns the updated game state along with the AI move execution details.

    Args:
        request: MoveRequest containing game_id, row, and col for the player's move.

    Returns:
        MoveResponse with updated_game_state and ai_move_execution (if AI moved),
        or JSONResponse with 400/404/503 error response.

    Raises:
        HTTPException: 400 for invalid moves, 404 for game not found,
            503 if service is not ready.
    """
    global _service_ready, _game_sessions

    # Check service readiness (AC-5.3.1)
    if not _service_ready:
        logger.warning(
            "Game endpoint called when service not ready",
            extra={
                "event_type": "error",
                "error_code": E_SERVICE_NOT_READY,
                "endpoint": "/api/game/move",
            },
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                status="failure",
                error_code=E_SERVICE_NOT_READY,
                message="Service not ready. Check /ready endpoint.",
                timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                details=None,
            ).model_dump(),
        )

    # Look up game session
    game_id = request.game_id
    if game_id not in _game_sessions:
        logger.warning(
            "Game not found",
            extra={
                "event_type": "error",
                "error_code": "E_GAME_NOT_FOUND",
                "game_id": game_id,
                "endpoint": "/api/game/move",
            },
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                status="failure",
                error_code="E_GAME_NOT_FOUND",
                message=f"Game session {game_id} not found.",
                timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                details={"game_id": game_id},
            ).model_dump(),
        )

    engine = _game_sessions[game_id]
    game_state = engine.get_current_state()

    # Validate move via game engine
    player_symbol = game_state.player_symbol
    is_valid, error_code = engine.validate_move(request.row, request.col, player_symbol)

    if not is_valid:
        logger.warning(
            "Invalid move attempted",
            extra={
                "event_type": "error",
                "error_code": error_code,
                "game_id": game_id,
                "row": request.row,
                "col": request.col,
                "player": player_symbol,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                status="failure",
                error_code=error_code or E_INVALID_REQUEST,
                message=_get_error_message(error_code),
                timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                details={
                    "game_id": game_id,
                    "row": request.row,
                    "col": request.col,
                },
            ).model_dump(),
        )

    # Execute player move
    success, move_error = engine.make_move(request.row, request.col, player_symbol)
    if not success:
        # This shouldn't happen after validation, but handle it
        logger.error(
            "Move execution failed after validation",
            extra={
                "event_type": "error",
                "error_code": move_error,
                "game_id": game_id,
                "row": request.row,
                "col": request.col,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="failure",
                error_code=move_error or E_INTERNAL_ERROR,
                message="Move execution failed after validation.",
                timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                details={"game_id": game_id},
            ).model_dump(),
        )

    # Get updated game state after player move
    updated_state = engine.get_current_state()
    player_position = Position(row=request.row, col=request.col)

    # Check if game is over after player move
    ai_move_execution = None
    fallback_used = False
    total_execution_time_ms: float | None = None

    if not engine.is_game_over():
        # Trigger AI agent pipeline
        pipeline = AgentPipeline(ai_symbol=game_state.ai_symbol)
        pipeline_result = pipeline.execute_pipeline(updated_state)

        if pipeline_result.success and pipeline_result.data:
            # AI move was successful
            ai_move_execution = pipeline_result.data

            # Execute the AI move on the engine
            # Position is required in MoveExecution, so it should never be None
            # But we check to satisfy mypy's type checking
            if ai_move_execution.position is not None:
                ai_move_success, ai_move_error = engine.make_move(
                    ai_move_execution.position.row,
                    ai_move_execution.position.col,
                    game_state.ai_symbol,
                )
            else:
                # This should never happen, but handle it gracefully
                ai_move_success = False
                ai_move_error = "E_INVALID_MOVE"

            if ai_move_success:
                # Get final game state after AI move
                updated_state = engine.get_current_state()
            else:
                ai_pos_str = "unknown"
                if ai_move_execution.position is not None:
                    ai_pos_str = (
                        f"({ai_move_execution.position.row}, {ai_move_execution.position.col})"
                    )
                logger.error(
                    "AI move execution failed",
                    extra={
                        "event_type": "error",
                        "error_code": ai_move_error,
                        "game_id": game_id,
                        "ai_move_position": ai_pos_str,
                    },
                )

            # Extract fallback metadata
            if pipeline_result.metadata and "fallback_used" in pipeline_result.metadata:
                fallback_used = bool(pipeline_result.metadata.get("fallback_used", False))

            # Calculate total execution time
            if pipeline_result.execution_time_ms is not None:
                total_execution_time_ms = round(pipeline_result.execution_time_ms, 2)
        else:
            # AI pipeline failed - log but don't fail the request
            logger.warning(
                "AI pipeline failed",
                extra={
                    "event_type": "warning",
                    "error_code": pipeline_result.error_code,
                    "game_id": game_id,
                    "error_message": pipeline_result.error_message,
                },
            )
            # Continue with just the player move

    # Log move
    logger.info(
        "Move executed",
        extra={
            "event_type": "move_made",
            "game_id": game_id,
            "position": f"({request.row}, {request.col})",
            "player": player_symbol,
            "ai_move_executed": ai_move_execution is not None,
            "fallback_used": fallback_used,
        },
    )

    # Return response
    return MoveResponse(
        success=True,
        position=player_position,
        updated_game_state=updated_state,
        ai_move_execution=ai_move_execution,
        error_message=None,
        fallback_used=fallback_used if ai_move_execution else None,
        total_execution_time_ms=total_execution_time_ms,
    )


@app.get("/api/game/status", response_model=GameStatusResponse, status_code=status.HTTP_200_OK)
async def get_game_status(game_id: str) -> GameStatusResponse | JSONResponse:
    """Get current game status.

    Returns the current game state, agent status (if AI is processing), and
    game metrics (if game is completed).

    Args:
        game_id: Query parameter - unique game identifier (UUID v4).

    Returns:
        GameStatusResponse with current GameState, optional agent_status,
        and optional metrics, or JSONResponse with 404/503 error response.

    Raises:
        HTTPException: 404 for game not found, 503 if service is not ready.
    """
    global _service_ready, _game_sessions

    # Check service readiness (AC-5.3.1)
    if not _service_ready:
        logger.warning(
            "Game endpoint called when service not ready",
            extra={
                "event_type": "error",
                "error_code": E_SERVICE_NOT_READY,
                "endpoint": "/api/game/status",
            },
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                status="failure",
                error_code=E_SERVICE_NOT_READY,
                message="Service not ready. Check /ready endpoint.",
                timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                details=None,
            ).model_dump(),
        )

    # Look up game session
    if game_id not in _game_sessions:
        logger.warning(
            "Game not found",
            extra={
                "event_type": "error",
                "error_code": "E_GAME_NOT_FOUND",
                "game_id": game_id,
                "endpoint": "/api/game/status",
            },
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                status="failure",
                error_code="E_GAME_NOT_FOUND",
                message=f"Game session {game_id} not found.",
                timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                details={"game_id": game_id},
            ).model_dump(),
        )

    engine = _game_sessions[game_id]
    game_state = engine.get_current_state()

    # Build agent_status (AC-5.5.3)
    # In Phase 4, we don't have async agent processing tracking yet.
    # This will be implemented in Phase 5 with LLM integration.
    # For now, agent_status is None (no active AI processing).
    agent_status: dict[str, Any] | None = None

    # Build metrics if game is completed (AC-5.5.4)
    metrics: dict[str, Any] | None = None
    if engine.is_game_over():
        winner = game_state.get_winner()
        metrics = {
            "game_outcome": winner if winner else "DRAW",
            "move_count": game_state.move_count,
            "is_game_over": True,
            "winner": winner,
        }

    logger.info(
        "Game status retrieved",
        extra={
            "event_type": "game_status_requested",
            "game_id": game_id,
            "move_count": game_state.move_count,
            "is_game_over": engine.is_game_over(),
        },
    )

    # Return response
    return GameStatusResponse(
        game_state=game_state,
        agent_status=agent_status,
        metrics=metrics,
    )
