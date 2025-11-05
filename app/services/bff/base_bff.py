"""
Base BFF Service

Provides common functionality for all BFF services:
- Caching strategy
- Parallel data fetching
- Error handling
- Response formatting
"""

from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.cache import cache_manager
import asyncio
import logging

logger = logging.getLogger(__name__)


class BaseBFFService:
    """
    Base class for all BFF services

    Provides:
    - Caching utilities
    - Parallel execution helpers
    - Common response formatting
    - Error handling patterns
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = cache_manager

    async def get_cached_or_fetch(
        self,
        cache_key: str,
        fetch_func,
        ttl: int = 300,  # 5 minutes default
        **kwargs
    ) -> Any:
        """
        Get data from cache or fetch from database

        Args:
            cache_key: Redis cache key
            fetch_func: Async function to fetch data if not cached
            ttl: Time to live in seconds
            **kwargs: Arguments to pass to fetch_func

        Returns:
            Cached or freshly fetched data
        """
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return cached

        # Cache miss - fetch from database
        logger.debug(f"Cache MISS: {cache_key}")
        data = await fetch_func(**kwargs)

        # Store in cache
        if data is not None:
            await self.cache.set(cache_key, data, ttl=ttl)

        return data

    async def fetch_parallel(self, *tasks) -> List[Any]:
        """
        Execute multiple async tasks in parallel

        Args:
            *tasks: Async tasks to execute

        Returns:
            List of results in the same order as tasks

        Example:
            results = await self.fetch_parallel(
                self.get_product(product_id),
                self.get_inventory(product_id),
                self.get_pricing(product_id)
            )
            product, inventory, pricing = results
        """
        return await asyncio.gather(*tasks, return_exceptions=True)

    def handle_exception(self, result: Any, default: Any = None) -> Any:
        """
        Handle exceptions from parallel fetch results

        Args:
            result: Result from asyncio.gather (could be exception)
            default: Default value if result is an exception

        Returns:
            Result or default value
        """
        if isinstance(result, Exception):
            logger.error(f"BFF fetch error: {result}")
            return default
        return result

    def format_response(
        self,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format BFF response with consistent structure

        Args:
            data: Main data payload
            metadata: Optional metadata (cache status, timing, etc.)

        Returns:
            Formatted response dictionary
        """
        response = {
            "data": data,
            "success": True
        }

        if metadata:
            response["metadata"] = metadata

        return response

    def format_error(
        self,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format error response

        Args:
            error: Error message
            details: Optional error details

        Returns:
            Formatted error response
        """
        response = {
            "success": False,
            "error": error
        }

        if details:
            response["details"] = details

        return response

    async def invalidate_cache(self, pattern: str):
        """
        Invalidate cache keys matching a pattern

        Args:
            pattern: Redis key pattern (e.g., "product:123:*")
        """
        await self.cache.delete_pattern(pattern)
        logger.info(f"Invalidated cache pattern: {pattern}")
