"""FastAPI application setup and routes.

Phase 4.0.1: FastAPI Application Setup
- Create FastAPI app instance
- Configure CORS (Section 5)
- Set up exception handlers
- Configure logging middleware

Phase 4.1.1: GET /health endpoint
- Return basic health status with uptime tracking
"""

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


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager for FastAPI app startup/shutdown."""
    global _server_start_time, _server_shutting_down

    # Startup
    _server_start_time = time.time()
    _server_shutting_down = False
    logger.info("Starting API server", extra={"event_type": "startup"})
    setup_logging(log_level="INFO", enable_file_logging=True)
    yield
    # Shutdown
    _server_shutting_down = True
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
