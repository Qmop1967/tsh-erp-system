"""
Rate Limiter for Zoho API
==========================

Implements rate limiting to comply with Zoho API limits.
Consolidates zoho_rate_limiter.py functionality.

محدد معدل الطلبات لـ Zoho API

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import time
import logging
from collections import deque
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int = 100
    burst_size: Optional[int] = None  # Max burst, defaults to requests_per_minute

    def __post_init__(self):
        if self.burst_size is None:
            self.burst_size = self.requests_per_minute


class RateLimiter:
    """
    Token bucket rate limiter for API requests
    محدد معدل الطلبات باستخدام خوارزمية Token Bucket

    Features:
    - Token bucket algorithm
    - Configurable rate and burst size
    - Async/await support
    - Request statistics
    """

    def __init__(
        self,
        requests_per_minute: int = 100,
        burst_size: Optional[int] = None
    ):
        """
        Initialize rate limiter

        Args:
            requests_per_minute: Maximum requests allowed per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
        """
        self.config = RateLimitConfig(requests_per_minute, burst_size)

        # Token bucket
        self.tokens = float(self.config.burst_size)
        self.max_tokens = float(self.config.burst_size)
        self.refill_rate = self.config.requests_per_minute / 60.0  # tokens per second
        self.last_refill = time.monotonic()

        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "requests_allowed": 0,
            "requests_throttled": 0,
            "total_wait_time": 0.0
        }

    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary

        Args:
            tokens: Number of tokens to acquire (default 1)
        """
        async with self._lock:
            while True:
                # Refill tokens based on time elapsed
                now = time.monotonic()
                elapsed = now - self.last_refill
                self.tokens = min(
                    self.max_tokens,
                    self.tokens + (elapsed * self.refill_rate)
                )
                self.last_refill = now

                # Check if we have enough tokens
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    self.stats["requests_allowed"] += 1
                    return

                # Not enough tokens, calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate

                self.stats["requests_throttled"] += 1
                self.stats["total_wait_time"] += wait_time

                logger.debug(
                    f"Rate limit: waiting {wait_time:.2f}s "
                    f"(tokens: {self.tokens:.2f}/{self.max_tokens})"
                )

                # Wait outside the lock
                await asyncio.sleep(wait_time)

    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without waiting

        Args:
            tokens: Number of tokens to acquire

        Returns:
            bool: True if tokens were acquired, False otherwise
        """
        # Refill tokens
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.max_tokens,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now

        # Check if we have enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            self.stats["requests_allowed"] += 1
            return True

        self.stats["requests_throttled"] += 1
        return False

    def reset(self):
        """Reset the rate limiter to full capacity"""
        self.tokens = float(self.max_tokens)
        self.last_refill = time.monotonic()
        logger.info("Rate limiter reset")

    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        return {
            **self.stats,
            "current_tokens": self.tokens,
            "max_tokens": self.max_tokens,
            "refill_rate_per_second": self.refill_rate,
            "requests_per_minute": self.config.requests_per_minute
        }

    def get_available_tokens(self) -> float:
        """Get number of currently available tokens"""
        # Refill tokens based on time elapsed
        now = time.monotonic()
        elapsed = now - self.last_refill
        return min(
            self.max_tokens,
            self.tokens + (elapsed * self.refill_rate)
        )

    def time_until_tokens(self, tokens: int = 1) -> float:
        """
        Calculate time until specified tokens are available

        Args:
            tokens: Number of tokens needed

        Returns:
            float: Time in seconds (0 if tokens already available)
        """
        available = self.get_available_tokens()

        if available >= tokens:
            return 0.0

        tokens_needed = tokens - available
        return tokens_needed / self.refill_rate

    def __repr__(self) -> str:
        return (
            f"RateLimiter("
            f"rate={self.config.requests_per_minute}/min, "
            f"tokens={self.tokens:.2f}/{self.max_tokens})"
        )
