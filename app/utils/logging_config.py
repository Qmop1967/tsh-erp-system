"""
Structured Logging Configuration for TSH ERP System
Provides JSON-formatted logs with contextual information for better debugging
"""
import structlog
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Configure structured logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("app/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Default log file with timestamp
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"tsh_erp_{timestamp}.log"

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.dev.ConsoleRenderer() if sys.stdout.isatty() else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def get_logger(name: str = None):
    """
    Get a configured logger instance

    Args:
        name: Optional logger name (usually __name__ of the module)

    Returns:
        Configured structlog logger
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


# Context managers for adding context to logs
def log_context(**kwargs):
    """
    Add context to all logs within this context

    Usage:
        with log_context(user_id=123, request_id="abc"):
            logger.info("user_action", action="login")
    """
    return structlog.contextvars.bound_contextvars(**kwargs)


# Convenience functions for common log patterns
def log_api_request(logger, method: str, path: str, user_id: int = None, **extra):
    """Log an incoming API request"""
    logger.info(
        "api_request",
        method=method,
        path=path,
        user_id=user_id,
        **extra
    )


def log_api_response(logger, method: str, path: str, status_code: int, duration_ms: float, **extra):
    """Log an API response"""
    logger.info(
        "api_response",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **extra
    )


def log_database_query(logger, operation: str, table: str, duration_ms: float = None, **extra):
    """Log a database operation"""
    logger.debug(
        "database_query",
        operation=operation,
        table=table,
        duration_ms=round(duration_ms, 2) if duration_ms else None,
        **extra
    )


def log_authentication(logger, success: bool, email: str, reason: str = None, **extra):
    """Log authentication attempts"""
    logger.info(
        "authentication_attempt",
        success=success,
        email=email,
        reason=reason,
        **extra
    )


def log_business_event(logger, event_type: str, **extra):
    """Log business events (orders, payments, etc.)"""
    logger.info(
        "business_event",
        event_type=event_type,
        **extra
    )


def log_error(logger, error: Exception, context: str = None, **extra):
    """Log an error with full context"""
    logger.error(
        "application_error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context,
        **extra,
        exc_info=True
    )


def log_security_event(logger, event_type: str, severity: str, **extra):
    """Log security-related events"""
    logger.warning(
        "security_event",
        event_type=event_type,
        severity=severity,
        **extra
    )


# Initialize logging when module is imported
# This ensures logging is set up before any other imports
try:
    # Try to get log level from environment
    import os
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level=log_level)
except Exception as e:
    print(f"Warning: Failed to initialize structured logging: {e}")
    print("Falling back to basic logging configuration")
