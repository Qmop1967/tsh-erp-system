"""
Correlation ID and Structured Logging
======================================

Provides correlation IDs for tracking requests across the system.
Implements structured logging with context.

معرفات الارتباط والتسجيل المنظم

Features:
- Correlation ID generation and tracking
- Context-aware logging
- Request tracing
- Performance profiling
- Structured log formatting

Author: TSH ERP Team
Date: November 9, 2025
"""

import logging
import uuid
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime
from contextvars import ContextVar
from functools import wraps

# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

# Context variable for request metadata
request_context_var: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class CorrelationIDFilter(logging.Filter):
    """
    Logging filter to add correlation ID to log records
    فلتر إضافة معرف الارتباط للسجلات
    """

    def filter(self, record):
        """Add correlation ID to log record"""
        correlation_id = correlation_id_var.get()
        record.correlation_id = correlation_id if correlation_id else "NO_CORRELATION_ID"

        # Add request context
        context = request_context_var.get()
        record.user_id = context.get('user_id', 'unknown')
        record.entity_type = context.get('entity_type', 'unknown')
        record.operation = context.get('operation', 'unknown')

        return True


class StructuredFormatter(logging.Formatter):
    """
    JSON structured log formatter
    منسق السجلات المنظمة بصيغة JSON
    """

    def format(self, record):
        """Format log record as structured JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'correlation_id', 'NO_CORRELATION_ID'),
            "user_id": getattr(record, 'user_id', 'unknown'),
            "entity_type": getattr(record, 'entity_type', 'unknown'),
            "operation": getattr(record, 'operation', 'unknown'),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


class CorrelationContext:
    """
    Context manager for correlation IDs and request context
    مدير سياق معرفات الارتباط
    """

    def __init__(
        self,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        operation: Optional[str] = None,
        **extra
    ):
        """
        Initialize correlation context

        Args:
            correlation_id: Correlation ID (generated if not provided)
            user_id: User ID performing the operation
            entity_type: Type of entity being operated on
            operation: Operation being performed
            **extra: Additional context fields
        """
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.context = {
            'user_id': user_id,
            'entity_type': entity_type,
            'operation': operation,
            **extra
        }

        self._correlation_token = None
        self._context_token = None

    def __enter__(self):
        """Enter context - set correlation ID and context"""
        self._correlation_token = correlation_id_var.set(self.correlation_id)
        self._context_token = request_context_var.set(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - reset correlation ID and context"""
        if self._correlation_token:
            correlation_id_var.reset(self._correlation_token)
        if self._context_token:
            request_context_var.reset(self._context_token)

    async def __aenter__(self):
        """Async context enter"""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context exit"""
        return self.__exit__(exc_type, exc_val, exc_tb)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id_var.get()


def get_request_context() -> Dict[str, Any]:
    """Get current request context"""
    return request_context_var.get()


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context"""
    correlation_id_var.set(correlation_id)


def with_correlation(func):
    """
    Decorator to automatically create correlation context
    ديكوريتور لإنشاء سياق الارتباط تلقائيًا
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract context from kwargs if provided
        correlation_id = kwargs.pop('correlation_id', None)
        user_id = kwargs.pop('user_id', None)
        entity_type = kwargs.pop('entity_type', None)
        operation = kwargs.pop('operation', func.__name__)

        async with CorrelationContext(
            correlation_id=correlation_id,
            user_id=user_id,
            entity_type=entity_type,
            operation=operation
        ):
            return await func(*args, **kwargs)

    return wrapper


class PerformanceLogger:
    """
    Performance profiling logger
    مسجل الأداء
    """

    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        """
        Initialize performance logger

        Args:
            operation: Operation name
            logger: Logger instance (uses root logger if not provided)
        """
        self.operation = operation
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
        self.end_time = None
        self.metadata: Dict[str, Any] = {}

    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log"""
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000

        # Determine log level based on duration
        if duration_ms > 5000:  # > 5 seconds
            log_level = logging.WARNING
            status = "SLOW"
        elif exc_type:
            log_level = logging.ERROR
            status = "FAILED"
        else:
            log_level = logging.INFO
            status = "SUCCESS"

        # Log performance
        self.logger.log(
            log_level,
            f"Performance: {self.operation} - {status} - {duration_ms:.2f}ms",
            extra={
                'extra_data': {
                    'operation': self.operation,
                    'duration_ms': round(duration_ms, 2),
                    'status': status,
                    **self.metadata
                }
            }
        )

    async def __aenter__(self):
        """Async context enter"""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context exit"""
        return self.__exit__(exc_type, exc_val, exc_tb)

    def add_metadata(self, **kwargs):
        """Add metadata to performance log"""
        self.metadata.update(kwargs)


def setup_structured_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    include_console: bool = True
):
    """
    Setup structured logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format (json or text)
        include_console: Include console handler
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # Add correlation ID filter
    correlation_filter = CorrelationIDFilter()

    if include_console:
        # Console handler
        console_handler = logging.StreamHandler()

        if log_format == "json":
            console_handler.setFormatter(StructuredFormatter())
        else:
            # Text format with correlation ID
            console_handler.setFormatter(
                logging.Formatter(
                    '[%(asctime)s] [%(correlation_id)s] [%(levelname)s] '
                    '[%(name)s] %(message)s'
                )
            )

        console_handler.addFilter(correlation_filter)
        root_logger.addHandler(console_handler)

    logger = logging.getLogger(__name__)
    logger.info(
        f"Structured logging configured: level={log_level}, format={log_format}"
    )


class StructuredLogger:
    """
    Enhanced logger with structured logging support
    مسجل منظم محسّن
    """

    def __init__(self, name: str):
        """
        Initialize structured logger

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)

    def _log(
        self,
        level: int,
        message: str,
        correlation_id: Optional[str] = None,
        **extra
    ):
        """
        Log with structured data

        Args:
            level: Log level
            message: Log message
            correlation_id: Optional correlation ID
            **extra: Additional structured data
        """
        # Get current correlation ID if not provided
        if not correlation_id:
            correlation_id = get_correlation_id()

        self.logger.log(
            level,
            message,
            extra={
                'extra_data': extra,
                'correlation_id': correlation_id
            }
        )

    def debug(self, message: str, **extra):
        """Log debug message"""
        self._log(logging.DEBUG, message, **extra)

    def info(self, message: str, **extra):
        """Log info message"""
        self._log(logging.INFO, message, **extra)

    def warning(self, message: str, **extra):
        """Log warning message"""
        self._log(logging.WARNING, message, **extra)

    def error(self, message: str, **extra):
        """Log error message"""
        self._log(logging.ERROR, message, **extra)

    def critical(self, message: str, **extra):
        """Log critical message"""
        self._log(logging.CRITICAL, message, **extra)
