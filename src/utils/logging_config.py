"""Logging configuration with structured JSON logging (Section 17)."""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger  # type: ignore


class StructuredJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging (Section 17)."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add fields to log record according to Section 17 schema."""
        super().add_fields(log_record, record, message_dict)

        # Required fields per Section 17
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["message"] = record.getMessage()

        # Service and component extracted from logger name
        # Format: "service.component" or "service"
        logger_parts = record.name.split(".")
        log_record["service"] = logger_parts[0] if len(logger_parts) > 0 else "unknown"
        log_record["component"] = (
            logger_parts[1] if len(logger_parts) > 1 else logger_parts[0]
        )

        # Event type from extra or default based on level
        log_record["event_type"] = getattr(record, "event_type", self._default_event_type(record.levelname))

        # Context from extra
        if hasattr(record, "context"):
            log_record["context"] = record.context

        # Error from extra (for ERROR/CRITICAL levels)
        if record.levelno >= logging.ERROR and hasattr(record, "error"):
            log_record["error"] = record.error
            if record.levelno >= logging.CRITICAL and hasattr(record, "stack_trace"):
                log_record["error"]["stack_trace"] = record.stack_trace

        # Metadata from extra
        if hasattr(record, "metadata"):
            log_record["metadata"] = record.metadata

    @staticmethod
    def _default_event_type(level: str) -> str:
        """Default event_type based on log level."""
        mapping = {
            "INFO": "state_change",
            "WARNING": "error",
            "ERROR": "error",
            "CRITICAL": "error",
        }
        return mapping.get(level, "state_change")


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_file_logging: bool = True,
) -> None:
    """
    Set up structured JSON logging (Section 17).

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/app-{date}.log)
        enable_file_logging: Whether to enable file logging
    """
    # Create logs directory if it doesn't exist
    if enable_file_logging:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        if log_file is None:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log_file = log_dir / f"app-{date_str}.log"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (stdout) - JSON format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = StructuredJSONFormatter()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler - JSON format (JSONL: one JSON object per line)
    if enable_file_logging and log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = StructuredJSONFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with structured logging support.

    Args:
        name: Logger name (should follow "service.component" format)

    Returns:
        Logger instance configured for structured logging
    """
    return logging.getLogger(name)

