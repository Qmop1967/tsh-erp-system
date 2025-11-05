"""
Redis Cache Manager for TSH ERP
================================

Provides caching layer for API responses, database queries, and expensive computations.

Features:
- Redis-based caching
- TTL (Time-To-Live) support
- Key prefix management
- Cache invalidation
- Decorator for easy caching
- JSON serialization support
- Memory fallback if Redis unavailable

Usage:
------

    from app.core.cache import cache_manager, cached

    # Using decorator
    @cached(ttl=600, key_prefix="products")
    async def get_products():
        # Expensive database query
        return products

    # Using manager directly
    await cache_manager.set("key", value, ttl=300)
    value = await cache_manager.get("key")

"""

import json
import asyncio
import logging
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with fallback to in-memory cache"""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._memory_cache: dict = {}  # Fallback cache
        self._memory_cache_ttl: dict = {}  # TTL tracking
        self._enabled = False
        self._use_memory_fallback = False

    async def initialize(self):
        """Initialize Redis connection"""
        if not settings.REDIS_ENABLED:
            logger.warning("Redis caching is disabled in configuration")
            self._use_memory_fallback = True
            return

        try:
            self._redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            await self._redis.ping()
            self._enabled = True
            logger.info(f"✅ Redis cache connected: {settings.REDIS_URL}")

        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.warning("⚠️  Using in-memory cache fallback")
            self._use_memory_fallback = True

    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")

    def _build_key(self, key: str, prefix: Optional[str] = None) -> str:
        """Build cache key with optional prefix"""
        if prefix:
            return f"{prefix}:{key}"
        return key

    async def get(self, key: str, prefix: Optional[str] = None) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key
            prefix: Optional key prefix

        Returns:
            Cached value or None if not found
        """
        full_key = self._build_key(key, prefix)

        try:
            if self._use_memory_fallback:
                # Memory cache fallback
                value = self._memory_cache.get(full_key)
                if value is not None:
                    # Check TTL
                    ttl = self._memory_cache_ttl.get(full_key)
                    if ttl is not None and ttl < asyncio.get_event_loop().time():
                        # Expired
                        del self._memory_cache[full_key]
                        del self._memory_cache_ttl[full_key]
                        return None
                return value

            if not self._redis or not self._enabled:
                return None

            value = await self._redis.get(full_key)
            if value is not None:
                # Deserialize JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value

            return None

        except Exception as e:
            logger.error(f"Cache GET error for key '{full_key}': {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
        prefix: Optional[str] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 5 minutes)
            prefix: Optional key prefix

        Returns:
            True if successful, False otherwise
        """
        full_key = self._build_key(key, prefix)

        try:
            if self._use_memory_fallback:
                # Memory cache fallback
                self._memory_cache[full_key] = value
                self._memory_cache_ttl[full_key] = asyncio.get_event_loop().time() + ttl
                return True

            if not self._redis or not self._enabled:
                return False

            # Serialize to JSON if not string
            if not isinstance(value, str):
                value = json.dumps(value, default=str)

            await self._redis.setex(full_key, ttl, value)
            return True

        except Exception as e:
            logger.error(f"Cache SET error for key '{full_key}': {e}")
            return False

    async def delete(self, key: str, prefix: Optional[str] = None) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key
            prefix: Optional key prefix

        Returns:
            True if successful, False otherwise
        """
        full_key = self._build_key(key, prefix)

        try:
            if self._use_memory_fallback:
                # Memory cache fallback
                if full_key in self._memory_cache:
                    del self._memory_cache[full_key]
                if full_key in self._memory_cache_ttl:
                    del self._memory_cache_ttl[full_key]
                return True

            if not self._redis or not self._enabled:
                return False

            await self._redis.delete(full_key)
            return True

        except Exception as e:
            logger.error(f"Cache DELETE error for key '{full_key}': {e}")
            return False

    async def delete_pattern(self, pattern: str, prefix: Optional[str] = None) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "products:*")
            prefix: Optional key prefix

        Returns:
            Number of keys deleted
        """
        if prefix:
            pattern = f"{prefix}:{pattern}"

        try:
            if self._use_memory_fallback:
                # Memory cache fallback (simple pattern matching)
                import fnmatch
                deleted = 0
                keys_to_delete = [
                    k for k in self._memory_cache.keys()
                    if fnmatch.fnmatch(k, pattern)
                ]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                    if key in self._memory_cache_ttl:
                        del self._memory_cache_ttl[key]
                    deleted += 1
                return deleted

            if not self._redis or not self._enabled:
                return 0

            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._redis.delete(*keys)
                    deleted += len(keys)
                if cursor == 0:
                    break

            return deleted

        except Exception as e:
            logger.error(f"Cache DELETE_PATTERN error for pattern '{pattern}': {e}")
            return 0

    async def exists(self, key: str, prefix: Optional[str] = None) -> bool:
        """Check if key exists in cache"""
        full_key = self._build_key(key, prefix)

        try:
            if self._use_memory_fallback:
                return full_key in self._memory_cache

            if not self._redis or not self._enabled:
                return False

            return await self._redis.exists(full_key) > 0

        except Exception as e:
            logger.error(f"Cache EXISTS error for key '{full_key}': {e}")
            return False

    async def get_ttl(self, key: str, prefix: Optional[str] = None) -> int:
        """
        Get remaining TTL for key

        Returns:
            TTL in seconds, -1 if key doesn't exist, -2 if key has no expiry
        """
        full_key = self._build_key(key, prefix)

        try:
            if self._use_memory_fallback:
                if full_key not in self._memory_cache:
                    return -1
                ttl = self._memory_cache_ttl.get(full_key)
                if ttl is None:
                    return -2
                remaining = int(ttl - asyncio.get_event_loop().time())
                return max(0, remaining)

            if not self._redis or not self._enabled:
                return -1

            return await self._redis.ttl(full_key)

        except Exception as e:
            logger.error(f"Cache GET_TTL error for key '{full_key}': {e}")
            return -1

    async def clear_all(self) -> bool:
        """Clear all cache (use with caution!)"""
        try:
            if self._use_memory_fallback:
                self._memory_cache.clear()
                self._memory_cache_ttl.clear()
                logger.info("Memory cache cleared")
                return True

            if not self._redis or not self._enabled:
                return False

            await self._redis.flushdb()
            logger.info("Redis cache cleared")
            return True

        except Exception as e:
            logger.error(f"Cache CLEAR_ALL error: {e}")
            return False

    async def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            if self._use_memory_fallback:
                return {
                    "enabled": True,
                    "backend": "memory",
                    "keys": len(self._memory_cache),
                    "memory_usage_mb": 0,  # Would need sys.getsizeof for accurate calculation
                }

            if not self._redis or not self._enabled:
                return {
                    "enabled": False,
                    "backend": "none",
                }

            info = await self._redis.info()
            return {
                "enabled": True,
                "backend": "redis",
                "keys": info.get("db0", {}).get("keys", 0),
                "memory_usage_mb": info.get("used_memory", 0) / (1024 * 1024),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
            }

        except Exception as e:
            logger.error(f"Cache GET_STATS error: {e}")
            return {"enabled": False, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

    @property
    def is_enabled(self) -> bool:
        """Check if cache is enabled"""
        return self._enabled or self._use_memory_fallback

    @property
    def backend(self) -> str:
        """Get cache backend type"""
        if self._use_memory_fallback:
            return "memory"
        elif self._enabled:
            return "redis"
        return "none"


# Global cache manager instance
cache_manager = CacheManager()


def cached(
    ttl: int = 300,
    key_prefix: Optional[str] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results

    Args:
        ttl: Cache time-to-live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys
        key_builder: Custom function to build cache key from arguments

    Usage:
        @cached(ttl=600, key_prefix="products")
        async def get_products(category_id: int):
            return await db.query(Product).filter_by(category_id=category_id).all()

    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key builder: function name + args + kwargs
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key, prefix=key_prefix)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {key_prefix}:{cache_key}")
                return cached_value

            # Cache miss - execute function
            logger.debug(f"Cache MISS: {key_prefix}:{cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl=ttl, prefix=key_prefix)

            return result

        return wrapper
    return decorator


# Cache invalidation helpers
async def invalidate_product_cache(product_id: Optional[int] = None):
    """Invalidate product-related cache"""
    if product_id:
        await cache_manager.delete_pattern(f"*product*{product_id}*")
    else:
        await cache_manager.delete_pattern("products:*")
    logger.info(f"Invalidated product cache (ID: {product_id or 'all'})")


async def invalidate_order_cache(order_id: Optional[int] = None):
    """Invalidate order-related cache"""
    if order_id:
        await cache_manager.delete_pattern(f"*order*{order_id}*")
    else:
        await cache_manager.delete_pattern("orders:*")
    logger.info(f"Invalidated order cache (ID: {order_id or 'all'})")


async def invalidate_customer_cache(customer_id: Optional[int] = None):
    """Invalidate customer-related cache"""
    if customer_id:
        await cache_manager.delete_pattern(f"*customer*{customer_id}*")
    else:
        await cache_manager.delete_pattern("customers:*")
    logger.info(f"Invalidated customer cache (ID: {customer_id or 'all'})")


async def invalidate_mobile_bff_cache():
    """Invalidate all Mobile BFF cache"""
    await cache_manager.delete_pattern("mobile:*")
    logger.info("Invalidated Mobile BFF cache")
