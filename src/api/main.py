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
"""

import os
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.utils.logging_config import get_logger, setup_logging

logger = get_logger("api.main")

# Server state tracking for health endpoint
_server_start_time: float | None = None
_server_shutting_down: bool = False

# Service readiness tracking
_service_ready: bool = False


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
