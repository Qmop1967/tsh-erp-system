"""
TDS Core - Retry Logic Utilities
Exponential backoff and retry strategy helpers
"""
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


def calculate_backoff_delay(
    attempt_number: int,
    base_delay_ms: int = 1000,
    max_delay_ms: int = 60000,
    exponential: bool = True,
    jitter: bool = True
) -> int:
    """
    Calculate retry delay using exponential backoff with jitter

    Args:
        attempt_number: Current attempt number (1-indexed)
        base_delay_ms: Base delay in milliseconds (default: 1000ms)
        max_delay_ms: Maximum delay cap (default: 60000ms)
        exponential: Use exponential backoff (default: True)
        jitter: Add random jitter to prevent thundering herd (default: True)

    Returns:
        Delay in milliseconds

    Examples:
        Attempt 1: ~1000ms
        Attempt 2: ~2000ms
        Attempt 3: ~4000ms
        Attempt 4: ~8000ms
        Attempt 5: ~16000ms

    Strategy:
        - Exponential: delay = base * (2 ^ (attempt - 1))
        - Linear: delay = base * attempt
        - Jitter: Add random ±25% variation
        - Cap: Never exceed max_delay_ms
    """
    if exponential:
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s, ...
        delay = base_delay_ms * (2 ** (attempt_number - 1))
    else:
        # Linear backoff: 1s, 2s, 3s, 4s, 5s, ...
        delay = base_delay_ms * attempt_number

    # Apply cap
    delay = min(delay, max_delay_ms)

    # Add jitter (±25% random variation)
    if jitter:
        jitter_range = delay * 0.25
        jitter_value = random.uniform(-jitter_range, jitter_range)
        delay = int(delay + jitter_value)

    return max(delay, base_delay_ms)  # Ensure minimum delay


def should_retry(
    attempt_count: int,
    max_attempts: int,
    error_code: str = None,
    retryable_codes: list = None
) -> bool:
    """
    Determine if operation should be retried

    Args:
        attempt_count: Current number of attempts
        max_attempts: Maximum retry attempts allowed
        error_code: Optional error code from failure
        retryable_codes: List of error codes that are retryable

    Returns:
        True if should retry

    Non-Retryable Errors:
        - Validation errors (400)
        - Authentication errors (401, 403)
        - Not found errors (404)
        - Conflict errors (409)
        - Unprocessable entity (422)

    Retryable Errors:
        - Rate limiting (429)
        - Server errors (500, 502, 503, 504)
        - Network errors (connection refused, timeout)
        - Database errors (deadlock, connection lost)
    """
    # Check attempt limit
    if attempt_count >= max_attempts:
        return False

    # If no error code provided, retry
    if error_code is None:
        return True

    # Check if error is in retryable list
    if retryable_codes and error_code in retryable_codes:
        return True

    # Default non-retryable HTTP status codes
    non_retryable = ['400', '401', '403', '404', '409', '422']
    if error_code in non_retryable:
        return False

    # Default retryable HTTP status codes
    retryable = ['429', '500', '502', '503', '504']
    if error_code in retryable:
        return True

    # Unknown error codes - retry by default
    return True


def calculate_next_retry_time(
    attempt_number: int,
    base_delay_ms: int = 1000,
    max_delay_ms: int = 60000
) -> datetime:
    """
    Calculate next retry timestamp

    Args:
        attempt_number: Current attempt number
        base_delay_ms: Base delay in milliseconds
        max_delay_ms: Maximum delay cap

    Returns:
        Datetime for next retry
    """
    delay_ms = calculate_backoff_delay(attempt_number, base_delay_ms, max_delay_ms)
    return datetime.utcnow() + timedelta(milliseconds=delay_ms)


def is_transient_error(error: Exception) -> bool:
    """
    Check if error is transient and retryable

    Args:
        error: Exception to check

    Returns:
        True if error is transient
    """
    # Network errors
    transient_types = [
        'ConnectionError',
        'TimeoutError',
        'ConnectionRefusedError',
        'ConnectionResetError',
    ]

    error_type = type(error).__name__

    # Check error type
    if error_type in transient_types:
        return True

    # Check error message for keywords
    error_msg = str(error).lower()
    transient_keywords = [
        'timeout',
        'connection refused',
        'connection reset',
        'deadlock',
        'lock wait timeout',
        'too many connections',
        'server is busy',
        'rate limit',
        'throttled',
    ]

    return any(keyword in error_msg for keyword in transient_keywords)


def get_retry_strategy(entity_type: str) -> dict:
    """
    Get retry strategy configuration for entity type

    Args:
        entity_type: Entity type (product, customer, invoice, etc.)

    Returns:
        Dictionary with retry configuration

    Example:
        >>> strategy = get_retry_strategy("product")
        >>> {
        >>>     "max_attempts": 3,
        >>>     "base_delay_ms": 1000,
        >>>     "max_delay_ms": 60000,
        >>>     "exponential": True
        >>> }
    """
    # Default strategy
    default = {
        "max_attempts": 3,
        "base_delay_ms": 1000,
        "max_delay_ms": 60000,
        "exponential": True,
        "jitter": True
    }

    # Entity-specific overrides
    strategies = {
        # Critical entities - more aggressive retries
        "invoice": {
            "max_attempts": 5,
            "base_delay_ms": 500,
            "max_delay_ms": 30000,
        },
        "order": {
            "max_attempts": 5,
            "base_delay_ms": 500,
            "max_delay_ms": 30000,
        },

        # Standard entities
        "product": default,
        "customer": default,

        # Low priority - less aggressive
        "stock_adjustment": {
            "max_attempts": 2,
            "base_delay_ms": 2000,
            "max_delay_ms": 60000,
        },
    }

    return strategies.get(entity_type, default)


class RetryContext:
    """
    Context manager for retry operations with logging

    Usage:
        >>> async with RetryContext("product_sync", max_attempts=3) as ctx:
        >>>     if ctx.should_retry:
        >>>         # Perform operation
        >>>         result = await sync_product(...)
        >>>         ctx.success()
        >>>     else:
        >>>         ctx.skip("Max attempts reached")
    """

    def __init__(self, operation_name: str, max_attempts: int = 3):
        self.operation_name = operation_name
        self.max_attempts = max_attempts
        self.attempt = 0
        self.should_retry = True
        self.last_error = None

    async def __aenter__(self):
        self.attempt += 1
        self.should_retry = self.attempt <= self.max_attempts
        logger.debug(f"{self.operation_name}: Attempt {self.attempt}/{self.max_attempts}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.last_error = exc_val
            if self.should_retry and is_transient_error(exc_val):
                logger.warning(
                    f"{self.operation_name}: Attempt {self.attempt} failed (retryable): {exc_val}"
                )
                return True  # Suppress exception for retry
            else:
                logger.error(
                    f"{self.operation_name}: Attempt {self.attempt} failed (non-retryable): {exc_val}"
                )
                return False  # Propagate exception

    def success(self):
        """Mark operation as successful"""
        logger.info(f"{self.operation_name}: Success on attempt {self.attempt}")
        self.should_retry = False

    def skip(self, reason: str):
        """Skip retry with reason"""
        logger.info(f"{self.operation_name}: Skipped - {reason}")
        self.should_retry = False
