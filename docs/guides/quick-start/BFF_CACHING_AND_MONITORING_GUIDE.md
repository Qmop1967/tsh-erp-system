# BFF Caching & Monitoring Integration Guide

**Advanced Features for TSH ERP BFF Layer**

This guide covers the integration of Redis caching, performance monitoring, and structured logging into the BFF layer.

---

## 🚀 New Features Added

### 1. Redis Caching Service
- **File:** `app/bff/services/cache_service.py`
- **Features:**
  - Automatic cache key generation
  - TTL management (configurable per endpoint)
  - Cache invalidation helpers
  - Cache statistics and health monitoring
  - Decorator-based caching (`@cached`)
  - Fallback to no-cache if Redis unavailable

### 2. Performance Monitoring
- **File:** `app/bff/middleware/performance_monitor.py`
- **Features:**
  - Response time tracking (min, max, avg, p95, p99)
  - Request counting
  - Error rate monitoring
  - Cache hit/miss tracking
  - Endpoint usage statistics
  - Performance summary API

### 3. Structured Logging
- **File:** `app/bff/middleware/logging_middleware.py`
- **Features:**
  - Request/response logging
  - Request ID tracking
  - User authentication logging
  - Error and exception logging
  - Cache hit/miss logging
  - Slow query detection

---

## 📦 Installation

### Prerequisites

```bash
# Install Redis
# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server

# Start Redis
redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### Python Dependencies

Add to `requirements.txt`:
```
redis==5.0.1
```

Install:
```bash
pip install redis==5.0.1
```

---

## ⚙️ Configuration

### 1. Environment Variables

Add to `.env`:
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Cache TTL (seconds)
CACHE_TTL_SHORT=120      # 2 minutes
CACHE_TTL_MEDIUM=300     # 5 minutes
CACHE_TTL_LONG=900       # 15 minutes
```

### 2. Update Config File

Edit `app/core/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Cache TTL
    CACHE_TTL_SHORT: int = 120
    CACHE_TTL_MEDIUM: int = 300
    CACHE_TTL_LONG: int = 900

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🔌 Integration Steps

### Step 1: Add Middleware to Main App

Edit `app/main.py`:

```python
from app.bff.middleware.performance_monitor import (
    BFFPerformanceMiddleware,
    performance_router
)
from app.bff.middleware.logging_middleware import BFFLoggingMiddleware

# Add middleware (order matters!)
app.add_middleware(BFFLoggingMiddleware)  # Logging first
app.add_middleware(BFFPerformanceMiddleware)  # Then performance monitoring

# Add performance monitoring router
app.include_router(
    performance_router,
    prefix="/api",
    tags=["BFF Performance Monitoring"]
)
```

### Step 2: Apply Caching to BFF Endpoints

**Option A: Using Decorator (Recommended)**

```python
from app.bff.services.cache_service import cached

@router.get("/salesperson/dashboard")
@cached(prefix="bff:salesperson:dashboard", ttl=300)  # 5 minutes
async def get_dashboard(
    salesperson_id: int,
    date_range: str,
    db: AsyncSession = Depends(get_db)
):
    # Your existing implementation
    return {"data": ...}
```

**Option B: Manual Caching**

```python
from app.bff.services.cache_service import cache_service

@router.get("/salesperson/dashboard")
async def get_dashboard(
    salesperson_id: int,
    date_range: str,
    db: AsyncSession = Depends(get_db)
):
    # Generate cache key
    cache_key = f"bff:salesperson:dashboard:{salesperson_id}:{date_range}"

    # Try to get from cache
    cached_data = cache_service.get(cache_key)
    if cached_data:
        return cached_data

    # Fetch data
    data = await fetch_dashboard_data(salesperson_id, date_range, db)

    # Cache the result
    cache_service.set(cache_key, data, ttl=300)

    return data
```

### Step 3: Add Cache Invalidation

```python
from app.bff.services.cache_service import invalidate_salesperson_cache

@router.post("/orders/create")
async def create_order(
    salesperson_id: int,
    order_data: dict,
    db: AsyncSession = Depends(get_db)
):
    # Create order
    order = await create_order_in_db(order_data, db)

    # Invalidate cache
    invalidate_salesperson_cache(salesperson_id)

    return {"success": True, "order": order}
```

---

## 📊 Monitoring Endpoints

### Get Performance Statistics

```bash
# Get stats for all endpoints
GET /api/bff/monitoring/stats

# Get stats for specific endpoint
GET /api/bff/monitoring/stats?endpoint=/api/bff/mobile/salesperson/dashboard

# Response:
{
  "success": true,
  "data": {
    "/api/bff/mobile/salesperson/dashboard": {
      "endpoint": "/api/bff/mobile/salesperson/dashboard",
      "count": 1523,
      "errors": 5,
      "error_rate": 0.33,
      "response_times": {
        "min": 12.5,
        "max": 450.2,
        "avg": 85.3,
        "median": 75.1,
        "p95": 125.6,
        "p99": 180.2
      },
      "cache_hit_rate": 87.5,
      "cache_hits": 1332,
      "cache_misses": 191
    }
  }
}
```

### Get Performance Summary

```bash
GET /api/bff/monitoring/summary

# Response:
{
  "success": true,
  "data": {
    "total_requests": 15234,
    "total_errors": 45,
    "error_rate": 0.30,
    "avg_response_time": 95.2,
    "p95_response_time": 180.5,
    "cache_hit_rate": 85.3,
    "total_endpoints": 198,
    "top_endpoints": [
      {
        "endpoint": "/api/bff/mobile/home",
        "count": 3456,
        "avg_response_time": 120.5
      },
      ...
    ]
  }
}
```

### Reset Performance Statistics

```bash
POST /api/bff/monitoring/reset

# Response:
{
  "success": true,
  "message": "Performance statistics reset successfully"
}
```

### Health Check

```bash
GET /api/bff/monitoring/health

# Response:
{
  "status": "healthy",
  "service": "bff-performance-monitoring",
  "metrics": {
    "total_requests": 15234,
    "error_rate": 0.30,
    "avg_response_time": 95.2,
    "cache_hit_rate": 85.3
  }
}
```

---

## 🎯 Caching Strategies

### Cache TTL Recommendations

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Dashboard | 5 min | Frequently changing, balance freshness vs performance |
| Product Catalog | 10 min | Changes less often, can tolerate slight delays |
| Customer List | 2 min | May change frequently with new visits |
| Order Details | 3 min | Status updates need reasonable freshness |
| Inventory | 1 min | Critical data, needs frequent updates |
| Reports | 15 min | Historical data, rarely changes |
| User Profile | 10 min | Changes infrequently |
| Cart | No cache | Real-time data, must be fresh |

### Cache Invalidation Strategy

**Automatic Invalidation:**
```python
# After order creation
invalidate_salesperson_cache(salesperson_id)
invalidate_customer_cache(customer_id)

# After product update
invalidate_product_cache(product_id)

# After payment received
invalidate_salesperson_cache(salesperson_id)
invalidate_customer_cache(customer_id)
```

**Manual Invalidation Endpoints:**
```python
POST /api/bff/mobile/salesperson/dashboard/invalidate-cache?salesperson_id=1
POST /api/bff/mobile/customer/{id}/invalidate-cache
POST /api/bff/mobile/product/{id}/invalidate-cache
```

---

## 📈 Performance Impact

### Before Caching

```
Dashboard Load:
├── Database Query 1: 50ms
├── Database Query 2: 60ms
├── Database Query 3: 45ms
├── Database Query 4: 55ms
├── Database Query 5: 40ms
├── Database Query 6: 35ms
├── Database Query 7: 30ms
└── Database Query 8: 35ms
────────────────────────────
Total: ~350ms
```

### After Caching (Cache Hit)

```
Dashboard Load:
└── Redis Get: 10-15ms
────────────────────────────
Total: ~15ms
Improvement: 95% faster! ⚡
```

### Cache Performance

```
Cache Hit (Redis):           10-20ms
Cache Miss (DB + Redis):     300-400ms
Cache Hit Rate Target:       80-95%
```

---

## 🔍 Logging Examples

### Structured Log Output

```json
{
  "timestamp": "2025-01-05T15:30:45.123Z",
  "level": "INFO",
  "event": "bff_request_success",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "GET",
  "path": "/api/bff/mobile/salesperson/dashboard",
  "query_params": {
    "salesperson_id": "1",
    "date_range": "today"
  },
  "status_code": 200,
  "duration_ms": 85.32,
  "cached": true,
  "authenticated": true,
  "client_ip": "192.168.1.100"
}
```

### Cache Hit Log

```json
{
  "timestamp": "2025-01-05T15:30:45.120Z",
  "level": "DEBUG",
  "event": "bff_cache_hit",
  "endpoint": "/api/bff/mobile/salesperson/dashboard",
  "cache_key": "bff:salesperson:dashboard:1:today"
}
```

### Cache Miss Log

```json
{
  "timestamp": "2025-01-05T15:30:45.120Z",
  "level": "DEBUG",
  "event": "bff_cache_miss",
  "endpoint": "/api/bff/mobile/salesperson/dashboard",
  "cache_key": "bff:salesperson:dashboard:1:today"
}
```

---

## 🧪 Testing

### Test Cache Functionality

```bash
# Test Redis connection
redis-cli ping

# Monitor cache keys
redis-cli KEYS "bff:*"

# Get cache statistics
redis-cli INFO stats

# Check memory usage
redis-cli INFO memory

# Flush cache (testing only!)
redis-cli FLUSHDB
```

### Test Performance Monitoring

```bash
# Make some requests
for i in {1..100}; do
  curl http://localhost:8000/api/bff/mobile/home
done

# Check stats
curl http://localhost:8000/api/bff/monitoring/summary
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Ubuntu
brew install httpd  # macOS

# Test endpoint
ab -n 1000 -c 10 http://localhost:8000/api/bff/mobile/home

# Check cache hit rate
curl http://localhost:8000/api/bff/monitoring/stats
```

---

## 🐛 Troubleshooting

### Redis Not Available

**Symptom:** Logs show "Redis unavailable. Caching disabled."

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server

# Check Redis logs
tail -f /usr/local/var/log/redis.log  # macOS
tail -f /var/log/redis/redis-server.log  # Ubuntu
```

### Low Cache Hit Rate

**Symptom:** Cache hit rate < 50%

**Possible Causes:**
1. TTL too short - increase cache TTL
2. Frequent invalidations - review invalidation logic
3. High traffic with unique queries - expected behavior

**Solution:**
```python
# Increase TTL for less critical data
@cached(prefix="bff:reports", ttl=900)  # 15 minutes

# Review invalidation frequency
# Only invalidate when data actually changes
```

### High Memory Usage

**Symptom:** Redis using too much memory

**Solution:**
```bash
# Set max memory in redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru

# Restart Redis
redis-server /path/to/redis.conf

# Or set at runtime
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## 📚 Best Practices

### 1. Cache Key Naming Convention
```
bff:{app}:{endpoint}:{param1}:{param2}
```

Examples:
```
bff:salesperson:dashboard:1:today
bff:consumer:product:123
bff:pos:transaction:456
```

### 2. TTL Selection
- **Real-time data:** No cache
- **Frequently changing:** 1-2 minutes
- **Moderate changes:** 5-10 minutes
- **Rarely changes:** 15-30 minutes

### 3. Cache Invalidation
- Invalidate on data mutations (CREATE, UPDATE, DELETE)
- Use specific invalidation (by ID) rather than clearing all cache
- Log all cache invalidations for debugging

### 4. Monitoring
- Monitor cache hit rate (target: 80-95%)
- Alert if error rate > 5%
- Alert if p95 response time > 1000ms
- Review performance stats daily

---

## 🚀 Deployment Checklist

- [ ] Redis installed and running
- [ ] Environment variables configured
- [ ] Middleware added to main.py
- [ ] Caching applied to high-traffic endpoints
- [ ] Cache invalidation implemented
- [ ] Performance monitoring endpoints accessible
- [ ] Logging configured and tested
- [ ] Load testing completed
- [ ] Cache hit rate > 80%
- [ ] Documentation updated

---

## 📞 Support

For issues or questions:
- Check logs: `logs/error.log`
- Monitor Redis: `redis-cli MONITOR`
- Performance stats: `GET /api/bff/monitoring/summary`
- Cache stats: Check Redis INFO stats

---

**Status:** ✅ Ready for integration

**Next Steps:** Apply caching to remaining BFF endpoints following the examples

