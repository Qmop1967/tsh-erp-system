"""
Global Security Middleware for TSH ERP
=======================================

This middleware provides additional security layers across all endpoints:
- Rate limiting
- Security headers
- Request validation
- Audit logging

Author: Security Agent
Date: 2025-11-15
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Dict
import time
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, consider Redis-based rate limiting.
    """

    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.limits = {
            "default": (100, 60),  # 100 requests per 60 seconds
            "login": (5, 60),       # 5 login attempts per 60 seconds
            "api": (1000, 60),      # 1000 API calls per 60 seconds
        }

    def is_allowed(self, key: str, limit_type: str = "default") -> bool:
        """
        Check if request is allowed based on rate limit.

        Args:
            key: Identifier (usually IP address or user ID)
            limit_type: Type of limit to apply

        Returns:
            bool: True if request is allowed
        """
        max_requests, window_seconds = self.limits.get(limit_type, self.limits["default"])
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        # Remove old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ]

        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(now)
            return True

        return False


rate_limiter = RateLimiter()


# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    Protects against common web vulnerabilities.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )

        # Remove server header (don't reveal FastAPI/Uvicorn version)
        if "Server" in response.headers:
            del response.headers["Server"]

        return response


# ============================================================================
# RATE LIMITING MIDDLEWARE
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Apply rate limiting to requests.
    Prevents abuse and DoS attacks.
    """

    def __init__(self, app: ASGIApp, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/docs", "/redoc", "/openapi.json", "/health"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        # Determine rate limit type based on path
        limit_type = "default"
        if "/auth/login" in request.url.path or "/login" in request.url.path:
            limit_type = "login"
        elif "/api/" in request.url.path:
            limit_type = "api"

        # Check rate limit
        if not rate_limiter.is_allowed(f"{client_ip}:{user_agent}", limit_type):
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "user_agent": user_agent
                }
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )

        return await call_next(request)


# ============================================================================
# REQUEST VALIDATION MIDDLEWARE
# ============================================================================

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate incoming requests for common attack patterns.
    Blocks suspicious requests before they reach endpoints.
    """

    SUSPICIOUS_PATTERNS = [
        # SQL injection attempts
        r"(?i)(union.*select|insert.*into|delete.*from|drop.*table|exec\(|script>)",

        # XSS attempts
        r"(?i)(<script|javascript:|onerror=|onload=)",

        # Path traversal attempts
        r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow)",

        # Command injection attempts
        r"(?i)(;.*\||&&|\$\(|\`)",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import re

        # Check URL for suspicious patterns
        url_str = str(request.url)
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url_str):
                logger.warning(
                    f"Suspicious request blocked: {url_str}",
                    extra={
                        "client_ip": request.client.host if request.client else "unknown",
                        "pattern": pattern,
                        "url": url_str
                    }
                )
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid request"}
                )

        # Check request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Only check if content type is JSON
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    body = await request.body()
                    body_str = body.decode("utf-8")

                    for pattern in self.SUSPICIOUS_PATTERNS:
                        if re.search(pattern, body_str):
                            logger.warning(
                                f"Suspicious request body blocked",
                                extra={
                                    "client_ip": request.client.host if request.client else "unknown",
                                    "pattern": pattern,
                                    "path": request.url.path
                                }
                            )
                            return JSONResponse(
                                status_code=400,
                                content={"detail": "Invalid request data"}
                            )

                    # Important: Store the body so it can be read again by the endpoint
                    async def receive():
                        return {"type": "http.request", "body": body}

                    request._receive = receive

            except Exception as e:
                logger.error(f"Error validating request body: {e}")

        return await call_next(request)


# ============================================================================
# AUDIT LOGGING MIDDLEWARE
# ============================================================================

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests for security auditing.
    Helps detect and investigate security incidents.
    """

    def __init__(self, app: ASGIApp, log_sensitive: bool = False):
        super().__init__(app)
        self.log_sensitive = log_sensitive
        self.sensitive_paths = [
            "/login",
            "/register",
            "/password",
            "/token",
            "/auth"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Determine if this is a sensitive endpoint
        is_sensitive = any(path in request.url.path for path in self.sensitive_paths)

        # Log request
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": request.client.host if request.client else "unknown",
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", ""),
        }

        # Add auth info if available
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            log_data["authenticated"] = True
        else:
            log_data["authenticated"] = False

        # Process request
        try:
            response = await call_next(request)

            # Add response info
            process_time = time.time() - start_time
            log_data["status_code"] = response.status_code
            log_data["process_time_ms"] = round(process_time * 1000, 2)

            # Log based on status code
            if response.status_code >= 400:
                logger.warning(
                    f"{request.method} {request.url.path} - {response.status_code}",
                    extra=log_data
                )
            elif is_sensitive or self.log_sensitive:
                logger.info(
                    f"{request.method} {request.url.path} - {response.status_code}",
                    extra=log_data
                )

            return response

        except Exception as e:
            # Log errors
            process_time = time.time() - start_time
            log_data["error"] = str(e)
            log_data["process_time_ms"] = round(process_time * 1000, 2)

            logger.error(
                f"{request.method} {request.url.path} - Error: {str(e)}",
                extra=log_data
            )
            raise


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SecurityHeadersMiddleware',
    'RateLimitMiddleware',
    'RequestValidationMiddleware',
    'AuditLoggingMiddleware',
    'rate_limiter'
]
