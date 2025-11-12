"""
Circuit Breaker Pattern Implementation
=======================================

Prevents cascading failures by stopping calls to failing services.
Implements the Circuit Breaker pattern for resilient API calls.

نمط قاطع الدائرة للمرونة

States:
- CLOSED: Normal operation, calls pass through
- OPEN: Service failing, calls fail fast
- HALF_OPEN: Testing if service recovered

Author: TSH ERP Team
Date: November 9, 2025
"""

import asyncio
import logging
from typing import Callable, Any, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation
    قاطع الدائرة

    Prevents cascading failures by:
    - Monitoring failure rate
    - Opening circuit when threshold exceeded
    - Testing recovery periodically
    - Closing circuit when service recovers
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60,
        half_open_max_calls: int = 3,
        excluded_exceptions: Optional[list] = None
    ):
        """
        Initialize circuit breaker

        Args:
            name: Circuit breaker name
            failure_threshold: Failures before opening circuit
            success_threshold: Successes in half-open before closing
            timeout_seconds: Seconds to wait before half-open
            half_open_max_calls: Max concurrent calls in half-open state
            excluded_exceptions: Exceptions that don't count as failures
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.half_open_max_calls = half_open_max_calls
        self.excluded_exceptions = tuple(excluded_exceptions or [])

        # State
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0

        # Statistics
        self.stats = CircuitBreakerStats()

        # Lock for thread-safe state changes
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception if call fails
        """
        async with self._lock:
            # Check if we should attempt the call
            await self._check_state()

            # Increment half-open call counter
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1

        # Track call
        self.stats.total_calls += 1

        try:
            # Execute the function
            result = await func(*args, **kwargs)

            # Call succeeded
            await self._on_success()

            return result

        except Exception as e:
            # Check if exception should be ignored
            if isinstance(e, self.excluded_exceptions):
                raise

            # Call failed
            await self._on_failure(e)

            raise

        finally:
            # Decrement half-open call counter
            if self.state == CircuitState.HALF_OPEN:
                async with self._lock:
                    self.half_open_calls -= 1

    async def _check_state(self):
        """Check current state and transition if needed"""
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                time_since_open = datetime.utcnow() - self.last_failure_time
                if time_since_open >= self.timeout:
                    # Transition to half-open
                    await self._transition_to(CircuitState.HALF_OPEN)
                else:
                    # Still open, reject call
                    self.stats.rejected_calls += 1
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service unavailable. Try again in "
                        f"{(self.timeout - time_since_open).total_seconds():.0f} seconds."
                    )

        elif self.state == CircuitState.HALF_OPEN:
            # Limit concurrent calls in half-open state
            if self.half_open_calls >= self.half_open_max_calls:
                self.stats.rejected_calls += 1
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is HALF_OPEN. "
                    f"Max concurrent test calls reached ({self.half_open_max_calls}). "
                    f"Please wait."
                )

    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            self.stats.successful_calls += 1
            self.stats.last_success_time = datetime.utcnow()

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.info(
                    f"Circuit breaker '{self.name}': Success in HALF_OPEN "
                    f"({self.success_count}/{self.success_threshold})"
                )

                # Check if we should close
                if self.success_count >= self.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)

    async def _on_failure(self, exception: Exception):
        """Handle failed call"""
        async with self._lock:
            self.stats.failed_calls += 1
            self.stats.last_failure_time = datetime.utcnow()
            self.last_failure_time = datetime.utcnow()

            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                logger.warning(
                    f"Circuit breaker '{self.name}': Failure in CLOSED "
                    f"({self.failure_count}/{self.failure_threshold}) - {str(exception)}"
                )

                # Check if we should open
                if self.failure_count >= self.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)

            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens circuit
                logger.warning(
                    f"Circuit breaker '{self.name}': Failure in HALF_OPEN "
                    f"- reopening circuit. Error: {str(exception)}"
                )
                await self._transition_to(CircuitState.OPEN)

    async def _transition_to(self, new_state: CircuitState):
        """
        Transition to a new state

        Args:
            new_state: Target state
        """
        old_state = self.state
        self.state = new_state
        self.stats.state_changes += 1

        # Reset counters based on new state
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
            logger.info(
                f"✅ Circuit breaker '{self.name}': "
                f"{old_state} -> CLOSED (service recovered)"
            )

        elif new_state == CircuitState.OPEN:
            self.failure_count = 0
            logger.error(
                f"🔴 Circuit breaker '{self.name}': "
                f"{old_state} -> OPEN (service failing - fast fail enabled)"
            )

        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0
            logger.warning(
                f"⚠️  Circuit breaker '{self.name}': "
                f"{old_state} -> HALF_OPEN (testing service recovery)"
            )

    async def reset(self):
        """Manually reset circuit breaker to closed state"""
        async with self._lock:
            await self._transition_to(CircuitState.CLOSED)
            self.failure_count = 0
            self.success_count = 0
            logger.info(f"Circuit breaker '{self.name}' manually reset")

    def get_state(self) -> str:
        """Get current state"""
        return self.state.value

    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self.state == CircuitState.OPEN

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "half_open_calls": self.half_open_calls,
            "statistics": {
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "failed_calls": self.stats.failed_calls,
                "rejected_calls": self.stats.rejected_calls,
                "state_changes": self.stats.state_changes,
                "last_failure": self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
                "last_success": self.stats.last_success_time.isoformat() if self.stats.last_success_time else None,
            },
            "configuration": {
                "failure_threshold": self.failure_threshold,
                "success_threshold": self.success_threshold,
                "timeout_seconds": int(self.timeout.total_seconds()),
                "half_open_max_calls": self.half_open_max_calls,
            },
            "success_rate": (
                (self.stats.successful_calls / self.stats.total_calls * 100)
                if self.stats.total_calls > 0 else 0
            )
        }


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers
    سجل قواطع الدائرة
    """

    def __init__(self):
        """Initialize circuit breaker registry"""
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(
        self,
        name: str,
        **kwargs
    ) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one

        Args:
            name: Circuit breaker name
            **kwargs: CircuitBreaker constructor arguments

        Returns:
            CircuitBreaker instance
        """
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name=name, **kwargs)
                logger.info(f"Created circuit breaker: {name}")

            return self._breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self._breakers.get(name)

    async def reset_all(self):
        """Reset all circuit breakers"""
        async with self._lock:
            for breaker in self._breakers.values():
                await breaker.reset()
            logger.info(f"Reset {len(self._breakers)} circuit breakers")

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }

    def get_open_breakers(self) -> list[str]:
        """Get list of open circuit breakers"""
        return [
            name for name, breaker in self._breakers.items()
            if breaker.is_open()
        ]


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()
