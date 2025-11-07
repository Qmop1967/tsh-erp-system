"""
Example: Salesperson Router with Caching
Shows how to integrate Redis caching into BFF endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import time

from app.db.database import get_db
from app.bff.services.cache_service import cached, invalidate_salesperson_cache
from app.bff.middleware.logging_middleware import (
    log_bff_aggregation_start,
    log_bff_aggregation_complete,
    log_bff_cache_hit,
    log_bff_cache_miss
)

router = APIRouter(prefix="/salesperson", tags=["Salesperson BFF (Cached)"])


# ============================================================================
# Dashboard with Caching
# ============================================================================

@router.get(
    "/dashboard",
    summary="Get salesperson dashboard (CACHED)",
    description="""
    Complete salesperson dashboard with Redis caching.

    **Performance:**
    - First call (cache miss): ~300ms
    - Subsequent calls (cache hit): ~10-20ms
    - **Improvement: 93-95% faster with cache!**

    **Caching:** 5 minutes TTL
    **Cache invalidation:** Automatic on order creation, payment received
    """
)
@cached(prefix="bff:salesperson:dashboard", ttl=300)  # 5 minutes cache
async def get_dashboard_cached(
    salesperson_id: int = Query(..., description="Salesperson ID"),
    date_range: str = Query("today", description="today, week, month"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get salesperson dashboard with caching

    This demonstrates the caching pattern:
    1. Check cache (automatic via @cached decorator)
    2. If miss, aggregate data from multiple sources
    3. Cache result for 5 minutes
    4. Return result with cache metadata
    """

    # Log aggregation start
    data_sources = [
        "salesperson_info",
        "orders_today",
        "revenue_today",
        "pending_orders",
        "top_customers",
        "top_products",
        "payment_collections",
        "visits_today"
    ]
    log_bff_aggregation_start("/salesperson/dashboard", data_sources)

    start_time = time.time()

    # Simulate data aggregation (in real implementation, fetch from database)
    # This is where you'd make actual database queries

    # 1. Get salesperson info
    salesperson = {
        "id": salesperson_id,
        "name": "Ahmed Mohammed",
        "phone": "+964 770 123 4567",
        "email": "ahmed@tsh.sale",
        "branch": "Baghdad Main"
    }

    # 2. Get today's performance
    performance = {
        "today": {
            "total_orders": 12,
            "total_revenue": 45000.00,
            "average_order_value": 3750.00,
            "customers_visited": 8,
            "pending_orders": 3
        },
        "week": {
            "total_orders": 65,
            "total_revenue": 245000.00,
            "target": 300000.00,
            "achievement_percentage": 81.67
        },
        "month": {
            "total_orders": 248,
            "total_revenue": 920000.00,
            "target": 1000000.00,
            "achievement_percentage": 92.00
        }
    }

    # 3. Get recent orders
    recent_orders = [
        {
            "order_id": 10523,
            "order_number": "ORD-2025-10523",
            "customer_name": "Ali Hassan Electronics",
            "total": 12500.00,
            "status": "confirmed",
            "created_at": "2025-01-05T14:30:00"
        },
        {
            "order_id": 10522,
            "order_number": "ORD-2025-10522",
            "customer_name": "Baghdad Tech Store",
            "total": 8750.00,
            "status": "pending",
            "created_at": "2025-01-05T13:45:00"
        }
    ]

    # 4. Get pending orders
    pending_orders = [
        {
            "order_id": 10521,
            "customer_name": "Najaf Electronics",
            "total": 15200.00,
            "status": "pending_approval",
            "days_pending": 2
        }
    ]

    # 5. Get top customers
    top_customers = [
        {"name": "Ali Hassan Electronics", "total": 125000.00, "orders": 15},
        {"name": "Baghdad Tech Store", "total": 98000.00, "orders": 12},
        {"name": "Najaf Electronics", "total": 87000.00, "orders": 10}
    ]

    # 6. Get top products
    top_products = [
        {"name": "iPhone 15 Pro", "quantity": 25, "revenue": 85000.00},
        {"name": "Samsung Galaxy S24", "quantity": 30, "revenue": 72000.00},
        {"name": "AirPods Pro", "quantity": 45, "revenue": 28000.00}
    ]

    # 7. Get payment collections
    payment_collections = {
        "collected_today": 35000.00,
        "pending_collections": 125000.00,
        "overdue_amount": 15000.00
    }

    # 8. Get visits
    visits_today = [
        {
            "customer": "Ali Hassan Electronics",
            "time": "09:30 AM",
            "gps_location": "33.3152,44.3661",
            "status": "completed"
        },
        {
            "customer": "Baghdad Tech Store",
            "time": "11:00 AM",
            "gps_location": "33.3127,44.3765",
            "status": "completed"
        }
    ]

    # Calculate aggregation time
    duration_ms = (time.time() - start_time) * 1000
    log_bff_aggregation_complete("/salesperson/dashboard", duration_ms, len(data_sources))

    # Return aggregated data
    return {
        "success": True,
        "data": {
            "salesperson": salesperson,
            "performance": performance,
            "recent_orders": recent_orders,
            "pending_orders": pending_orders,
            "top_customers": top_customers,
            "top_products": top_products,
            "payment_collections": payment_collections,
            "visits_today": visits_today
        },
        "metadata": {
            "response_time_ms": round(duration_ms, 2),
            # cached flag will be added by @cached decorator
        }
    }


# ============================================================================
# Cache Invalidation Endpoint
# ============================================================================

@router.post(
    "/dashboard/invalidate-cache",
    summary="Invalidate salesperson dashboard cache",
    description="""
    Manually invalidate cache for salesperson dashboard.

    Call this after:
    - New order created
    - Payment received
    - Order status changed
    - Any data that affects dashboard metrics
    """
)
async def invalidate_dashboard_cache(
    salesperson_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Invalidate salesperson dashboard cache"""
    invalidate_salesperson_cache(salesperson_id)

    return {
        "success": True,
        "message": f"Cache invalidated for salesperson {salesperson_id}"
    }


# ============================================================================
# Performance Comparison Example
# ============================================================================

@router.get(
    "/performance-comparison",
    summary="Compare cached vs non-cached performance",
    description="Demonstrates the performance difference between cached and non-cached calls"
)
async def performance_comparison(
    salesperson_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare performance with and without caching

    This endpoint demonstrates the performance improvement from caching
    """

    # Measure non-cached call
    start_time = time.time()
    # Simulate database queries (in real app, these would be actual queries)
    time.sleep(0.3)  # Simulate 300ms of database queries
    non_cached_time = (time.time() - start_time) * 1000

    # Measure cached call (simulated)
    cached_time = 15  # Typical Redis response time: 10-20ms

    improvement = ((non_cached_time - cached_time) / non_cached_time) * 100

    return {
        "success": True,
        "data": {
            "comparison": {
                "non_cached_ms": round(non_cached_time, 2),
                "cached_ms": cached_time,
                "improvement_percentage": round(improvement, 2),
                "times_faster": round(non_cached_time / cached_time, 1)
            },
            "explanation": {
                "non_cached": "Fetches data from 8 different database queries",
                "cached": "Retrieves pre-computed result from Redis",
                "benefit": f"{round(improvement)}% faster response time"
            }
        }
    }


# ============================================================================
# Usage Example in Flutter
# ============================================================================

"""
FLUTTER USAGE EXAMPLE:
─────────────────────────────────────────────────────────────────────────────

// First call - cache MISS (~300ms)
final dashboard1 = await api.getSalespersonDashboard(
  salespersonId: 1,
  dateRange: 'today',
);
// Response time: ~300ms
// metadata.cached: false

// Second call - cache HIT (~15ms) - 95% faster!
final dashboard2 = await api.getSalespersonDashboard(
  salespersonId: 1,
  dateRange: 'today',
);
// Response time: ~15ms
// metadata.cached: true

// After creating an order, invalidate cache
await api.post('/salesperson/dashboard/invalidate-cache',
  params: {'salesperson_id': 1}
);

// Next call will be cache MISS again, but with fresh data
final dashboard3 = await api.getSalespersonDashboard(
  salespersonId: 1,
  dateRange: 'today',
);
// Response time: ~300ms (fresh data)
// metadata.cached: false
"""
