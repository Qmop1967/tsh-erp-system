"""
BFF Performance Monitoring Middleware
Tracks response times, cache hits, and performance metrics
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import statistics


class PerformanceMonitor:
    """
    Performance monitoring for BFF endpoints

    Tracks:
    - Response times (min, max, avg, p95, p99)
    - Request counts
    - Error rates
    - Cache hit rates
    - Endpoint usage statistics
    """

    def __init__(self):
        self.metrics = defaultdict(lambda: {
            "count": 0,
            "errors": 0,
            "response_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "last_reset": datetime.now()
        })
        self.reset_interval = timedelta(hours=1)  # Reset stats every hour

    def record_request(self, endpoint: str, response_time: float, status_code: int, cached: bool):
        """
        Record a request metric

        Args:
            endpoint: API endpoint path
            response_time: Response time in milliseconds
            status_code: HTTP status code
            cached: Whether response was from cache
        """
        metric = self.metrics[endpoint]

        # Increment counters
        metric["count"] += 1

        # Record error
        if status_code >= 400:
            metric["errors"] += 1

        # Record response time (keep last 1000 for statistics)
        metric["response_times"].append(response_time)
        if len(metric["response_times"]) > 1000:
            metric["response_times"] = metric["response_times"][-1000:]

        # Record cache hit/miss
        if cached:
            metric["cache_hits"] += 1
        else:
            metric["cache_misses"] += 1

        # Auto-reset if interval passed
        if datetime.now() - metric["last_reset"] > self.reset_interval:
            self._reset_metric(endpoint)

    def _reset_metric(self, endpoint: str):
        """Reset metrics for an endpoint"""
        self.metrics[endpoint] = {
            "count": 0,
            "errors": 0,
            "response_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "last_reset": datetime.now()
        }

    def get_stats(self, endpoint: Optional[str] = None) -> dict:
        """
        Get performance statistics

        Args:
            endpoint: Specific endpoint or None for all

        Returns:
            Dictionary with performance stats
        """
        if endpoint:
            return self._calculate_endpoint_stats(endpoint)

        # Return stats for all endpoints
        all_stats = {}
        for ep, metric in self.metrics.items():
            all_stats[ep] = self._calculate_endpoint_stats(ep)

        return all_stats

    def _calculate_endpoint_stats(self, endpoint: str) -> dict:
        """Calculate statistics for an endpoint"""
        metric = self.metrics[endpoint]

        if not metric["response_times"]:
            return {
                "endpoint": endpoint,
                "count": metric["count"],
                "errors": metric["errors"],
                "error_rate": 0.0,
                "response_times": {},
                "cache_hit_rate": 0.0,
                "last_reset": metric["last_reset"].isoformat()
            }

        times = metric["response_times"]

        # Calculate response time statistics
        response_stats = {
            "min": round(min(times), 2),
            "max": round(max(times), 2),
            "avg": round(statistics.mean(times), 2),
            "median": round(statistics.median(times), 2),
        }

        # Calculate percentiles
        sorted_times = sorted(times)
        n = len(sorted_times)
        response_stats["p95"] = round(sorted_times[int(n * 0.95)], 2) if n > 0 else 0
        response_stats["p99"] = round(sorted_times[int(n * 0.99)], 2) if n > 0 else 0

        # Calculate rates
        total_requests = metric["count"]
        error_rate = (metric["errors"] / total_requests * 100) if total_requests > 0 else 0

        total_cache_requests = metric["cache_hits"] + metric["cache_misses"]
        cache_hit_rate = (metric["cache_hits"] / total_cache_requests * 100) if total_cache_requests > 0 else 0

        return {
            "endpoint": endpoint,
            "count": total_requests,
            "errors": metric["errors"],
            "error_rate": round(error_rate, 2),
            "response_times": response_stats,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "cache_hits": metric["cache_hits"],
            "cache_misses": metric["cache_misses"],
            "last_reset": metric["last_reset"].isoformat()
        }

    def get_summary(self) -> dict:
        """
        Get overall summary statistics

        Returns:
            Dictionary with summary stats
        """
        total_requests = sum(m["count"] for m in self.metrics.values())
        total_errors = sum(m["errors"] for m in self.metrics.values())
        total_cache_hits = sum(m["cache_hits"] for m in self.metrics.values())
        total_cache_misses = sum(m["cache_misses"] for m in self.metrics.values())

        # Collect all response times
        all_times = []
        for metric in self.metrics.values():
            all_times.extend(metric["response_times"])

        if not all_times:
            avg_response_time = 0
            p95_response_time = 0
        else:
            avg_response_time = statistics.mean(all_times)
            sorted_times = sorted(all_times)
            p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]

        total_cache_requests = total_cache_hits + total_cache_misses
        cache_hit_rate = (total_cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0

        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 2),
            "avg_response_time": round(avg_response_time, 2),
            "p95_response_time": round(p95_response_time, 2),
            "cache_hit_rate": round(cache_hit_rate, 2),
            "total_endpoints": len(self.metrics),
            "top_endpoints": self._get_top_endpoints(5)
        }

    def _get_top_endpoints(self, limit: int = 5) -> list:
        """Get top N endpoints by request count"""
        sorted_endpoints = sorted(
            self.metrics.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]

        return [
            {
                "endpoint": endpoint,
                "count": metric["count"],
                "avg_response_time": round(statistics.mean(metric["response_times"]), 2)
                if metric["response_times"] else 0
            }
            for endpoint, metric in sorted_endpoints
        ]

    def reset_all(self):
        """Reset all metrics"""
        self.metrics.clear()
        print("📊 All performance metrics reset")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# ============================================================================
# FastAPI Middleware
# ============================================================================

class BFFPerformanceMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to track BFF performance

    Automatically records:
    - Response times
    - Status codes
    - Cache hits/misses
    - Endpoint usage
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only monitor BFF endpoints
        if not request.url.path.startswith("/api/bff/"):
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate response time in milliseconds
        response_time = (time.time() - start_time) * 1000

        # Check if response was cached
        cached = response.headers.get("X-Cache", "MISS") == "HIT"

        # Record metrics
        endpoint = request.url.path
        performance_monitor.record_request(
            endpoint=endpoint,
            response_time=response_time,
            status_code=response.status_code,
            cached=cached
        )

        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        response.headers["X-Cache"] = "HIT" if cached else "MISS"

        return response


# ============================================================================
# Performance Monitoring Endpoints
# ============================================================================

from fastapi import APIRouter

performance_router = APIRouter(prefix="/bff/monitoring", tags=["BFF Monitoring"])


@performance_router.get("/stats")
async def get_performance_stats(endpoint: Optional[str] = None):
    """
    Get performance statistics

    Args:
        endpoint: Optional specific endpoint to get stats for

    Returns:
        Performance statistics
    """
    if endpoint:
        stats = performance_monitor.get_stats(endpoint)
    else:
        stats = performance_monitor.get_stats()

    return {
        "success": True,
        "data": stats
    }


@performance_router.get("/summary")
async def get_performance_summary():
    """
    Get overall performance summary

    Returns:
        Summary statistics for all BFF endpoints
    """
    summary = performance_monitor.get_summary()

    return {
        "success": True,
        "data": summary
    }


@performance_router.post("/reset")
async def reset_performance_stats():
    """
    Reset all performance statistics

    Returns:
        Success message
    """
    performance_monitor.reset_all()

    return {
        "success": True,
        "message": "Performance statistics reset successfully"
    }


@performance_router.get("/health")
async def performance_monitoring_health():
    """
    Health check for performance monitoring

    Returns:
        Health status
    """
    summary = performance_monitor.get_summary()

    # Determine health based on metrics
    is_healthy = (
        summary["error_rate"] < 5.0 and  # Less than 5% error rate
        summary["avg_response_time"] < 1000  # Less than 1 second avg
    )

    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "bff-performance-monitoring",
        "metrics": {
            "total_requests": summary["total_requests"],
            "error_rate": summary["error_rate"],
            "avg_response_time": summary["avg_response_time"],
            "cache_hit_rate": summary["cache_hit_rate"]
        }
    }
