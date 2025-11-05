"""
BFF Cache Service
Redis-based caching for BFF endpoints with TTL management
"""
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis
from datetime import timedelta

from app.core.config import settings


class BFFCacheService:
    """
    Redis cache service for BFF endpoints

    Features:
    - Automatic key generation from function args
    - TTL management
    - Cache invalidation
    - Cache statistics
    - Fallback to no-cache if Redis unavailable
    """

    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
        except Exception as e:
            print(f"⚠️  Redis unavailable: {e}. Caching disabled.")
            self.redis_client = None
            self.available = False

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate unique cache key from function arguments

        Args:
            prefix: Cache key prefix (e.g., "bff:salesperson:dashboard")
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Hashed cache key
        """
        # Create deterministic string from arguments
        key_parts = [prefix]

        # Add args
        for arg in args:
            if arg is not None:
                key_parts.append(str(arg))

        # Add kwargs (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if v is not None and k != 'db':  # Exclude database session
                key_parts.append(f"{k}:{v}")

        # Create hash for long keys
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"

        return key_string

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.available:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"⚠️  Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False

        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"⚠️  Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"⚠️  Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "bff:salesperson:*")

        Returns:
            Number of keys deleted
        """
        if not self.available:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"⚠️  Cache delete pattern error: {e}")
            return 0

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.available:
            return {
                "available": False,
                "total_keys": 0,
                "memory_used": "0B",
                "hit_rate": 0.0
            }

        try:
            info = self.redis_client.info("stats")
            keyspace = self.redis_client.info("keyspace")

            # Calculate total keys
            total_keys = sum(
                db_info["keys"]
                for db_info in keyspace.values()
                if isinstance(db_info, dict)
            )

            # Calculate hit rate
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0.0

            return {
                "available": True,
                "total_keys": total_keys,
                "memory_used": self.redis_client.info("memory")["used_memory_human"],
                "hit_rate": round(hit_rate, 2),
                "hits": hits,
                "misses": misses
            }
        except Exception as e:
            print(f"⚠️  Cache stats error: {e}")
            return {
                "available": False,
                "error": str(e)
            }


# Global cache service instance
cache_service = BFFCacheService()


# ============================================================================
# Cache Decorator
# ============================================================================

def cached(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results

    Usage:
        @cached(prefix="bff:salesperson:dashboard", ttl=300)
        async def get_salesperson_dashboard(salesperson_id: int, date_range: str):
            # Function implementation
            return data

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 5 minutes)

    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service._generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                # Add cache metadata
                if isinstance(cached_result, dict):
                    if "metadata" not in cached_result:
                        cached_result["metadata"] = {}
                    cached_result["metadata"]["cached"] = True
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                # Add cache metadata
                if isinstance(result, dict):
                    if "metadata" not in result:
                        result["metadata"] = {}
                    result["metadata"]["cached"] = False

                cache_service.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


# ============================================================================
# Cache Invalidation Helpers
# ============================================================================

def invalidate_salesperson_cache(salesperson_id: int):
    """Invalidate all cache for a salesperson"""
    pattern = f"bff:salesperson:*:salesperson_id:{salesperson_id}:*"
    deleted = cache_service.delete_pattern(pattern)
    print(f"🗑️  Invalidated {deleted} cache keys for salesperson {salesperson_id}")


def invalidate_customer_cache(customer_id: int):
    """Invalidate all cache for a customer"""
    pattern = f"bff:*:customer_id:{customer_id}:*"
    deleted = cache_service.delete_pattern(pattern)
    print(f"🗑️  Invalidated {deleted} cache keys for customer {customer_id}")


def invalidate_product_cache(product_id: int):
    """Invalidate all cache for a product"""
    pattern = f"bff:*:product_id:{product_id}:*"
    deleted = cache_service.delete_pattern(pattern)
    print(f"🗑️  Invalidated {deleted} cache keys for product {product_id}")


def invalidate_order_cache(order_id: int):
    """Invalidate all cache for an order"""
    pattern = f"bff:*:order_id:{order_id}:*"
    deleted = cache_service.delete_pattern(pattern)
    print(f"🗑️  Invalidated {deleted} cache keys for order {order_id}")


def invalidate_all_bff_cache():
    """Invalidate all BFF cache (use with caution!)"""
    pattern = "bff:*"
    deleted = cache_service.delete_pattern(pattern)
    print(f"🗑️  Invalidated ALL BFF cache: {deleted} keys deleted")


# ============================================================================
# Cache Warming (Optional)
# ============================================================================

async def warm_cache_on_startup():
    """
    Warm cache on application startup
    Pre-load frequently accessed data
    """
    if not cache_service.available:
        print("⚠️  Cache warming skipped: Redis unavailable")
        return

    print("🔥 Warming BFF cache...")

    # Example: Pre-load common data
    # You can implement specific cache warming logic here
    # For now, just log that we're ready

    print("✅ Cache warming complete")


# ============================================================================
# Cache Health Check
# ============================================================================

async def check_cache_health() -> dict:
    """
    Check cache health and return status

    Returns:
        Dictionary with cache health info
    """
    stats = cache_service.get_stats()

    health_status = {
        "service": "bff-cache",
        "available": stats.get("available", False),
        "healthy": stats.get("available", False) and stats.get("hit_rate", 0) > 0,
        "stats": stats
    }

    return health_status
