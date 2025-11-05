"""
BFF Logging Middleware
Structured logging for BFF requests and responses
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class BFFLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all BFF requests and responses

    Logs:
    - Request method, path, params
    - Response status code, size
    - Request duration
    - User information (if authenticated)
    - Cache status
    - Errors and exceptions
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only log BFF endpoints
        if not request.url.path.startswith("/api/bff/"):
            return await call_next(request)

        # Generate request ID for tracking
        request_id = request.headers.get("X-Request-ID", self._generate_request_id())

        # Extract request information
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        # Extract user ID from authorization header if present
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                # Extract user_id from JWT token (simplified)
                request_info["authenticated"] = True
            except Exception:
                request_info["authenticated"] = False
        else:
            request_info["authenticated"] = False

        # Log incoming request
        logger.info(
            "bff_request_received",
            **request_info
        )

        # Record start time
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Extract response information
            response_info = {
                **request_info,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "cached": response.headers.get("X-Cache", "MISS") == "HIT",
                "response_size": response.headers.get("content-length", "unknown"),
            }

            # Log successful response
            if response.status_code < 400:
                logger.info(
                    "bff_request_success",
                    **response_info
                )
            elif response.status_code < 500:
                logger.warning(
                    "bff_request_client_error",
                    **response_info
                )
            else:
                logger.error(
                    "bff_request_server_error",
                    **response_info
                )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log exception
            logger.error(
                "bff_request_exception",
                **request_info,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )

            # Re-raise exception
            raise

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())


# ============================================================================
# Structured Logging Helpers
# ============================================================================

def log_bff_cache_hit(endpoint: str, cache_key: str):
    """Log cache hit"""
    logger.debug(
        "bff_cache_hit",
        endpoint=endpoint,
        cache_key=cache_key
    )


def log_bff_cache_miss(endpoint: str, cache_key: str):
    """Log cache miss"""
    logger.debug(
        "bff_cache_miss",
        endpoint=endpoint,
        cache_key=cache_key
    )


def log_bff_aggregation_start(endpoint: str, data_sources: list):
    """Log start of data aggregation"""
    logger.debug(
        "bff_aggregation_start",
        endpoint=endpoint,
        data_sources=data_sources,
        source_count=len(data_sources)
    )


def log_bff_aggregation_complete(endpoint: str, duration_ms: float, sources_fetched: int):
    """Log completion of data aggregation"""
    logger.info(
        "bff_aggregation_complete",
        endpoint=endpoint,
        duration_ms=round(duration_ms, 2),
        sources_fetched=sources_fetched
    )


def log_bff_error(endpoint: str, error: Exception, context: dict = None):
    """Log BFF error with context"""
    logger.error(
        "bff_error",
        endpoint=endpoint,
        error=str(error),
        error_type=type(error).__name__,
        context=context or {},
        exc_info=True
    )


def log_bff_slow_query(endpoint: str, query: str, duration_ms: float):
    """Log slow database query"""
    if duration_ms > 1000:  # Log queries slower than 1 second
        logger.warning(
            "bff_slow_query",
            endpoint=endpoint,
            query=query[:200],  # Truncate long queries
            duration_ms=round(duration_ms, 2)
        )


# ============================================================================
# Request/Response Body Logging (Optional - for debugging)
# ============================================================================

class BFFDebugLoggingMiddleware(BaseHTTPMiddleware):
    """
    Debug middleware to log request and response bodies

    ⚠️  WARNING: Only use in development!
    This logs sensitive data and should never be enabled in production.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only log BFF endpoints
        if not request.url.path.startswith("/api/bff/"):
            return await call_next(request)

        # Log request body if present
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    logger.debug(
                        "bff_request_body",
                        path=request.url.path,
                        body=body.decode("utf-8")[:1000]  # Limit size
                    )
            except Exception as e:
                logger.warning("Could not read request body", error=str(e))

        # Process request
        response = await call_next(request)

        return response


# ============================================================================
# Log Analysis Helpers
# ============================================================================

def get_slow_endpoints(threshold_ms: float = 500) -> list:
    """
    Analyze logs to find slow endpoints

    Args:
        threshold_ms: Response time threshold in milliseconds

    Returns:
        List of slow endpoints with statistics
    """
    # This would typically query your logging system
    # For now, return placeholder
    return []


def get_error_summary(time_period: str = "1h") -> dict:
    """
    Get summary of errors in time period

    Args:
        time_period: Time period (e.g., "1h", "24h", "7d")

    Returns:
        Error summary statistics
    """
    # This would typically query your logging system
    # For now, return placeholder
    return {
        "total_errors": 0,
        "error_rate": 0.0,
        "top_errors": []
    }
