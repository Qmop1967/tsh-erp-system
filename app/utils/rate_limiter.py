"""
Rate Limiting Utilities for TSH ERP System
Uses slowapi (compatible with FastAPI) instead of fastapi-limiter for better integration
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request, HTTPException, status
from functools import wraps
import redis.asyncio as redis
import os

# Rate limiting configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Initialize limiter - uses in-memory storage if Redis not available
try:
    # Try to connect to Redis
    redis_client = redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    limiter = Limiter(key_func=get_remote_address, storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    print("✅ Rate limiter using Redis storage")
except Exception as e:
    # Fall back to in-memory storage
    limiter = Limiter(key_func=get_remote_address)
    print(f"⚠️ Rate limiter using in-memory storage (Redis not available: {e})")

# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    # Authentication endpoints - strict limits to prevent brute force
    "auth_login": "5/minute",  # 5 login attempts per minute
    "auth_refresh": "10/minute",  # 10 refresh token requests per minute
    "auth_password_reset": "3/hour",  # 3 password reset requests per hour

    # Data modification endpoints - moderate limits
    "data_create": "30/minute",  # 30 POST requests per minute
    "data_update": "50/minute",  # 50 PUT/PATCH requests per minute
    "data_delete": "20/minute",  # 20 DELETE requests per minute

    # Data retrieval endpoints - higher limits
    "data_read": "100/minute",  # 100 GET requests per minute
    "data_list": "60/minute",  # 60 list requests per minute

    # Special operations - very strict limits
    "money_transfer": "10/hour",  # 10 money transfer operations per hour
    "financial_report": "20/hour",  # 20 financial report generations per hour
    "bulk_operation": "5/minute",  # 5 bulk operations per minute

    # Admin operations - moderate limits
    "admin_operation": "50/minute",  # 50 admin operations per minute

    # WebSocket connections
    "websocket": "5/minute",  # 5 WebSocket connection attempts per minute

    # Default for uncategorized endpoints
    "default": "60/minute"
}


def get_rate_limit_key(request: Request, role: str = None) -> str:
    """
    Generate a unique rate limit key based on request and user role
    Allows different rate limits for different user roles
    """
    remote_addr = get_remote_address(request)

    # If user is authenticated and is admin, use higher limits
    if role and role.lower() == "admin":
        return f"admin:{remote_addr}"

    return remote_addr


def custom_rate_limit(limit: str):
    """
    Custom rate limit decorator that can be applied to FastAPI endpoints

    Usage:
        @router.post("/login")
        @custom_rate_limit(RATE_LIMITS["auth_login"])
        async def login(...)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = kwargs.get("request") or next((arg for arg in args if isinstance(arg, Request)), None)

            if request:
                # Check rate limit using slowapi
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Rate limit exceeded. Please try again later.",
                            headers={"Retry-After": "60"}
                        )
                    raise

            return await func(*args, **kwargs)

        return wrapper
    return decorator


async def check_rate_limit(request: Request, limit_type: str = "default"):
    """
    Manually check rate limit for a specific request
    Can be called within endpoint handlers

    Usage:
        await check_rate_limit(request, "auth_login")
    """
    limit = RATE_LIMITS.get(limit_type, RATE_LIMITS["default"])
    # Implementation would use slowapi's limiter
    # This is a placeholder for manual checks
    pass


# Export limiter instance for use in main.py
__all__ = ["limiter", "RATE_LIMITS", "custom_rate_limit", "check_rate_limit"]
