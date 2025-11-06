"""
Retry Strategy for Zoho API
============================

Implements retry logic with exponential backoff for failed API requests.

استراتيجية إعادة المحاولة مع تأخير أسي

Author: TSH ERP Team
Date: November 6, 2025
"""

import random
import logging
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd


class RetryStrategy:
    """
    Exponential backoff retry strategy
    استراتيجية إعادة المحاولة مع تأخير أسي

    Features:
    - Exponential backoff
    - Configurable max retries
    - Jitter to prevent thundering herd
    - Retry condition callback
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry strategy

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential calculation
            jitter: Add random jitter to delays
        """
        self.config = RetryConfig(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter
        )
        self.max_retries = max_retries

    def get_wait_time(self, attempt: int) -> float:
        """
        Calculate wait time for given attempt number

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            float: Wait time in seconds
        """
        # Calculate exponential delay
        delay = min(
            self.config.initial_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )

        # Add jitter if enabled
        if self.config.jitter:
            delay = delay * (0.5 + random.random())

        return delay

    def should_retry(
        self,
        attempt: int,
        exception: Optional[Exception] = None,
        retry_condition: Optional[Callable[[Exception], bool]] = None
    ) -> bool:
        """
        Determine if request should be retried

        Args:
            attempt: Current attempt number
            exception: Exception that occurred
            retry_condition: Optional callback to determine if should retry

        Returns:
            bool: True if should retry
        """
        # Check max retries
        if attempt >= self.config.max_retries:
            return False

        # Check custom retry condition if provided
        if retry_condition and exception:
            return retry_condition(exception)

        # Default: retry on any exception
        return True

    def get_retry_info(self, attempt: int) -> dict:
        """
        Get information about current retry state

        Args:
            attempt: Current attempt number

        Returns:
            dict: Retry information
        """
        return {
            "attempt": attempt,
            "max_retries": self.config.max_retries,
            "next_wait_time": self.get_wait_time(attempt),
            "retries_remaining": max(0, self.config.max_retries - attempt)
        }

    def __repr__(self) -> str:
        return (
            f"RetryStrategy("
            f"max_retries={self.config.max_retries}, "
            f"initial_delay={self.config.initial_delay}s)"
        )


class RetryableError(Exception):
    """Exception that indicates an operation should be retried"""
    pass


class NonRetryableError(Exception):
    """Exception that indicates an operation should NOT be retried"""
    pass
