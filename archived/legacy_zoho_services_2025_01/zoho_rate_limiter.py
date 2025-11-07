"""
Zoho API Rate Limiter
Prevents hitting Zoho API rate limits with intelligent request throttling
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration for Zoho API"""

    # Zoho API rate limits (as per official documentation)
    max_requests_per_minute: int = 60  # Conservative limit
    max_requests_per_day: int = 10000  # Daily limit

    # Burst protection
    max_concurrent_requests: int = 5  # Max concurrent API calls

    # Adaptive throttling
    throttle_on_error: bool = True
    throttle_duration: int = 60  # Seconds to throttle after rate limit error


@dataclass
class RateLimitStats:
    """Statistics for rate limiting"""
    requests_this_minute: int = 0
    requests_today: int = 0
    last_request_time: Optional[float] = None
    minute_start: Optional[float] = None
    day_start: Optional[float] = None
    throttled_until: Optional[float] = None
    concurrent_requests: int = 0
    total_throttles: int = 0
    total_requests: int = 0


class ZohoRateLimiter:
    """
    Rate limiter for Zoho API calls

    Features:
    - Per-minute request limiting
    - Per-day request limiting
    - Concurrent request limiting
    - Adaptive throttling on errors
    - Automatic cooldown periods
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.stats = RateLimitStats()
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

    async def acquire(self, endpoint: str = "unknown"):
        """
        Acquire permission to make an API request

        Args:
            endpoint: API endpoint being called (for logging)

        Raises:
            asyncio.TimeoutError: If throttled for too long
        """
        async with self._lock:
            # Check if we're currently throttled
            if self.stats.throttled_until and time.time() < self.stats.throttled_until:
                wait_time = self.stats.throttled_until - time.time()
                logger.warning(
                    f"⏸️ API throttled. Waiting {wait_time:.1f}s before retry "
                    f"(endpoint: {endpoint})"
                )
                await asyncio.sleep(wait_time)
                self.stats.throttled_until = None

            # Reset counters if needed
            current_time = time.time()
            self._reset_counters_if_needed(current_time)

            # Check per-minute limit
            if self.stats.requests_this_minute >= self.config.max_requests_per_minute:
                wait_time = 60 - (current_time - self.stats.minute_start)
                logger.warning(
                    f"⏸️  Minute limit reached ({self.stats.requests_this_minute} requests). "
                    f"Waiting {wait_time:.1f}s (endpoint: {endpoint})"
                )
                await asyncio.sleep(wait_time)
                self._reset_counters_if_needed(time.time())

            # Check per-day limit
            if self.stats.requests_today >= self.config.max_requests_per_day:
                logger.error(
                    f"🚨 Daily API limit reached ({self.stats.requests_today} requests)! "
                    f"Throttling for 1 hour."
                )
                self.stats.throttled_until = time.time() + 3600  # 1 hour
                raise Exception("Daily API rate limit exceeded")

            # Acquire concurrent request slot
            await self._semaphore.acquire()

            # Update stats
            self.stats.requests_this_minute += 1
            self.stats.requests_today += 1
            self.stats.total_requests += 1
            self.stats.last_request_time = time.time()
            self.stats.concurrent_requests += 1

            logger.debug(
                f"✅ API request permitted: {endpoint} "
                f"(minute: {self.stats.requests_this_minute}/{self.config.max_requests_per_minute}, "
                f"day: {self.stats.requests_today}/{self.config.max_requests_per_day}, "
                f"concurrent: {self.stats.concurrent_requests})"
            )

    def release(self):
        """Release a request slot"""
        self._semaphore.release()
        self.stats.concurrent_requests = max(0, self.stats.concurrent_requests - 1)

    def throttle_on_error(self, error_code: Optional[int] = None):
        """
        Throttle requests due to an error

        Args:
            error_code: HTTP error code (if any)
        """
        if not self.config.throttle_on_error:
            return

        self.stats.total_throttles += 1

        # Zoho rate limit error codes
        if error_code in [429, 503]:  # Too Many Requests or Service Unavailable
            throttle_time = self.config.throttle_duration * 2  # Double throttle for rate limit errors
            logger.warning(
                f"⚠️  Zoho rate limit detected (code: {error_code}). "
                f"Throttling for {throttle_time}s"
            )
        else:
            throttle_time = self.config.throttle_duration

        self.stats.throttled_until = time.time() + throttle_time

    def _reset_counters_if_needed(self, current_time: float):
        """Reset counters if time periods have elapsed"""

        # Reset minute counter
        if self.stats.minute_start is None or (current_time - self.stats.minute_start) >= 60:
            self.stats.requests_this_minute = 0
            self.stats.minute_start = current_time
            logger.debug(f"🔄 Minute counter reset")

        # Reset day counter
        if self.stats.day_start is None or (current_time - self.stats.day_start) >= 86400:
            self.stats.requests_today = 0
            self.stats.day_start = current_time
            logger.info(
                f"🔄 Daily counter reset. "
                f"Previous total: {self.stats.total_requests} requests"
            )

    def get_stats(self) -> Dict:
        """Get current rate limit statistics"""
        return {
            'requests_this_minute': self.stats.requests_this_minute,
            'requests_today': self.stats.requests_today,
            'max_per_minute': self.config.max_requests_per_minute,
            'max_per_day': self.config.max_requests_per_day,
            'concurrent_requests': self.stats.concurrent_requests,
            'max_concurrent': self.config.max_concurrent_requests,
            'total_requests': self.stats.total_requests,
            'total_throttles': self.stats.total_throttles,
            'is_throttled': self.stats.throttled_until is not None and time.time() < self.stats.throttled_until,
            'throttled_until': datetime.fromtimestamp(self.stats.throttled_until).isoformat() if self.stats.throttled_until else None
        }

    async def __aenter__(self):
        """Context manager support"""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.release()

        # Throttle on HTTP errors
        if exc_val and hasattr(exc_val, 'status_code'):
            self.throttle_on_error(exc_val.status_code)

        return False  # Don't suppress exceptions


# Global rate limiter instance
_rate_limiter_instance: Optional[ZohoRateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> ZohoRateLimiter:
    """Get or create the global rate limiter instance"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = ZohoRateLimiter(config)
    return _rate_limiter_instance
