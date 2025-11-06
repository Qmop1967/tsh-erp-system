# 🚀 TSH ERP - Performance Optimization Guide

**Date:** November 5, 2025
**Purpose:** Comprehensive performance optimization strategies
**Current Performance:** Excellent (< 150ms API response)
**Target:** World-class (< 100ms API response)

---

## 📊 Current Performance Baseline

### Current Metrics (Production)

```yaml
API Performance:
  Average Response Time: 150ms ✅
  95th Percentile: 250ms ✅
  99th Percentile: 500ms ⚠️
  Database Query Time: < 50ms ✅

Server Resources:
  CPU Usage: 35% ✅
  Memory Usage: 1.5 GB / 4 GB ✅
  Disk I/O: Normal ✅
  Network: < 20% utilization ✅

Application:
  Concurrent Users: 1,000+ ✅
  Requests/Second: ~50 ✅
  Error Rate: < 0.1% ✅
  Uptime: 99.9% ✅
```

**Status:** ✅ Already excellent performance
**Goal:** Optimize for 5,000+ concurrent users

---

## 🎯 Optimization Strategies

---

## 1️⃣ Redis Caching Implementation

### Why Redis?

- **50-70% reduction** in database load
- **3-10x faster** response times for cached data
- **Scalable** to millions of cache entries
- **Simple** to implement and maintain

### Implementation Plan

#### Step 1: Install Redis

```bash
# On VPS (Ubuntu)
sudo apt update
sudo apt install redis-server -y

# Configure Redis
sudo nano /etc/redis/redis.conf

# Change:
supervised no → supervised systemd
bind 127.0.0.1 ::1 (keep as is for local only)
maxmemory 512mb (set cache limit)
maxmemory-policy allkeys-lru (evict least recently used)

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Test
redis-cli ping
# Should return: PONG
```

#### Step 2: Add Python Dependencies

```bash
# Add to requirements.txt
redis==5.0.1
redis-om==0.2.1  # Optional: Redis Object Mapper
```

#### Step 3: Create Cache Layer

```python
# app/core/cache.py

import redis
from functools import wraps
from typing import Optional, Any
import json
import hashlib
from datetime import timedelta

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)"""
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    def delete(self, key: str):
        """Delete key from cache"""
        self.redis_client.delete(key)

    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)

# Global cache instance
cache = RedisCache()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results

    Usage:
        @cached(ttl=600, key_prefix="products")
        async def get_products():
            return products
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_data = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
```

#### Step 4: Apply Caching to APIs

```python
# app/routers/products.py

from app.core.cache import cached, cache

@router.get("/products")
@cached(ttl=600, key_prefix="products")  # Cache for 10 minutes
async def get_products(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Get products with caching"""
    products = db.query(Product)\
        .filter(Product.is_active == True)\
        .limit(page_size)\
        .offset((page - 1) * page_size)\
        .all()

    return products


@router.get("/products/{product_id}")
@cached(ttl=1800, key_prefix="product")  # Cache for 30 minutes
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get single product with caching"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update product and invalidate cache"""
    # Update product
    product = db.query(Product).filter(Product.id == product_id).first()
    # ... update logic ...

    # Invalidate cache
    cache.delete(f"product:{product_id}")
    cache.clear_pattern("products:*")  # Clear product lists

    return product
```

### What to Cache

**High Priority (Cache First):**
```python
# Products (rarely change)
@cached(ttl=3600)  # 1 hour
def get_products(): pass

# Categories (rarely change)
@cached(ttl=7200)  # 2 hours
def get_categories(): pass

# Pricelists (change daily)
@cached(ttl=1800)  # 30 minutes
def get_pricelists(): pass

# User profiles (change occasionally)
@cached(ttl=600)  # 10 minutes
def get_user_profile(): pass

# Dashboard stats (change frequently)
@cached(ttl=60)  # 1 minute
def get_dashboard_stats(): pass
```

**Don't Cache:**
- Real-time data (stock levels during active sales)
- Financial transactions
- Security-sensitive data
- User sessions (use Redis sessions instead)

### Expected Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Product API | 150ms | 10ms | **93% faster** |
| Category API | 80ms | 5ms | **94% faster** |
| Dashboard | 200ms | 20ms | **90% faster** |
| Database Load | 100% | 30% | **-70% queries** |
| Server CPU | 35% | 20% | **-43% usage** |

---

## 2️⃣ Database Query Optimization

### Identify Slow Queries

```python
# app/core/query_logger.py

import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Log slow queries
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log queries > 100ms
        print(f"Slow query ({total:.2f}s): {statement[:200]}")
```

### Add Missing Indexes

```sql
-- Find missing indexes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
  AND correlation < 0.1;

-- Add indexes for frequently queried columns
CREATE INDEX idx_products_is_active ON products(is_active) WHERE is_active = true;
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops);  -- Full-text search
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

### Optimize N+1 Queries

```python
# BAD: N+1 Query Problem
products = db.query(Product).all()
for product in products:
    print(product.category.name)  # Triggers N queries!

# GOOD: Eager Loading
from sqlalchemy.orm import joinedload

products = db.query(Product)\
    .options(joinedload(Product.category))\
    .all()
for product in products:
    print(product.category.name)  # No additional queries!
```

### Use Query Results Pagination

```python
# Always paginate large results
@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * page_size
    products = db.query(Product)\
        .filter(Product.is_active == True)\
        .order_by(Product.created_at.desc())\
        .limit(page_size)\
        .offset(offset)\
        .all()

    total = db.query(Product).filter(Product.is_active == True).count()

    return {
        "products": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
```

---

## 3️⃣ Background Job Queue (Celery)

### Why Background Jobs?

- **Faster API responses** (don't wait for slow operations)
- **Better user experience** (immediate feedback)
- **Scalable** (process jobs asynchronously)
- **Retry logic** (automatic retry on failures)

### Use Cases

1. **Email sending** - Don't block API
2. **Report generation** - Can take minutes
3. **Image processing** - Resize, optimize
4. **Zoho synchronization** - External API calls
5. **Bulk operations** - Process thousands of records
6. **Data export** - CSV, Excel generation

### Implementation

```bash
# Install dependencies
pip install celery redis

# Add to requirements.txt
celery==5.3.4
redis==5.0.1
```

```python
# app/core/celery_app.py

from celery import Celery

celery_app = Celery(
    'tsh_erp',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
)
```

```python
# app/tasks/email_tasks.py

from app.core.celery_app import celery_app

@celery_app.task
def send_order_confirmation(order_id: int, customer_email: str):
    """Send order confirmation email (background)"""
    # Send email logic
    send_email(
        to=customer_email,
        subject="Order Confirmation",
        template="order_confirmation",
        data={"order_id": order_id}
    )
    return {"status": "sent", "order_id": order_id}


@celery_app.task
def sync_product_to_zoho(product_id: int):
    """Sync product to Zoho Books (background)"""
    # Zoho API call (can be slow)
    zoho_service.sync_product(product_id)
    return {"status": "synced", "product_id": product_id}
```

```python
# app/routers/orders.py

from app.tasks.email_tasks import send_order_confirmation

@router.post("/orders")
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Create order and send confirmation email"""
    # Create order (fast)
    order = create_order_in_db(order_data, db)

    # Send email asynchronously (don't wait)
    send_order_confirmation.delay(order.id, order.customer.email)

    # Return immediately
    return {"order_id": order.id, "status": "created"}
```

### Start Celery Worker

```bash
# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A app.core.celery_app beat --loglevel=info

# Monitor with Flower (web UI)
pip install flower
celery -A app.core.celery_app flower
# Visit: http://localhost:5555
```

---

## 4️⃣ API Response Compression

### Enable Gzip Compression

```python
# app/main.py

from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# Add Gzip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
```

**Impact:** 60-80% smaller response sizes

---

## 5️⃣ Connection Pooling

### Database Connection Pool

```python
# app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Connections to keep open
    max_overflow=10,       # Additional connections when needed
    pool_timeout=30,       # Wait time for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connection before using
)
```

---

## 6️⃣ CDN for Static Assets

### Use CloudFlare (Free Tier)

```nginx
# nginx config
location /images/ {
    alias /var/www/html/images/;
    expires 30d;
    add_header Cache-Control "public, immutable";
    add_header X-Content-Type-Options "nosniff";
}
```

**Point CloudFlare to your domain:**
- Free SSL
- Free CDN (global caching)
- Free DDoS protection
- Free bandwidth

---

## 7️⃣ Monitoring & Observability

### Application Metrics

```python
# app/core/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
active_requests = Gauge('http_requests_active', 'Active HTTP requests')

# Database metrics
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration', ['query_type'])
db_connection_pool = Gauge('db_connection_pool_size', 'Database connection pool size')

# Cache metrics
cache_hits = Counter('cache_hits_total', 'Cache hits')
cache_misses = Counter('cache_misses_total', 'Cache misses')
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "services": {
            "database": check_database_health(),
            "redis": check_redis_health(),
            "disk_space": check_disk_space(),
            "memory": check_memory_usage()
        },
        "metrics": {
            "active_connections": get_active_connections(),
            "cache_hit_rate": get_cache_hit_rate(),
            "avg_response_time": get_avg_response_time()
        }
    }
```

---

## 📊 Performance Testing

### Load Testing with Locust

```python
# locustfile.py

from locust import HttpUser, task, between

class TSHERPUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_products(self):
        self.client.get("/api/products")

    @task(2)
    def get_dashboard(self):
        self.client.get("/api/dashboard")

    @task(1)
    def create_order(self):
        self.client.post("/api/orders", json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 2}]
        })

# Run load test
# locust -f locustfile.py --host=https://erp.tsh.sale
```

---

## 🎯 Implementation Priority

### Phase 1: Quick Wins (Week 1) ⭐
1. ✅ Enable Gzip compression (5 minutes)
2. ✅ Add database indexes (1 hour)
3. ✅ Optimize N+1 queries (2 hours)
4. ✅ Add query pagination (2 hours)

**Impact:** 30-40% performance improvement

### Phase 2: Caching (Week 2) ⭐⭐
1. Install Redis (30 minutes)
2. Implement cache layer (4 hours)
3. Add caching to hot endpoints (4 hours)
4. Test and tune cache TTLs (2 hours)

**Impact:** 50-70% performance improvement

### Phase 3: Background Jobs (Week 3)
1. Install Celery (1 hour)
2. Move email sending to background (2 hours)
3. Move Zoho sync to background (3 hours)
4. Add job monitoring (2 hours)

**Impact:** 20-30% faster API responses

### Phase 4: Advanced (Week 4)
1. Add monitoring (Prometheus)
2. Set up alerting
3. Optimize images
4. Add CDN

**Impact:** Production-grade observability

---

## ✅ Success Metrics

### Target Performance (After Optimization)

```yaml
API Performance:
  Average Response Time: < 100ms (current: 150ms)
  95th Percentile: < 150ms (current: 250ms)
  99th Percentile: < 300ms (current: 500ms)
  Database Query Time: < 20ms (current: 50ms)

Capacity:
  Concurrent Users: 5,000+ (current: 1,000+)
  Requests/Second: 200+ (current: 50)
  Cache Hit Rate: 80%+ (current: 0%)

Resources:
  CPU Usage: < 50% (current: 35%)
  Memory Usage: < 3 GB (current: 1.5 GB)
  Database Connections: < 15 (current: varies)
```

---

## 📝 Conclusion

Your TSH ERP already has **excellent performance**. These optimizations will:

1. ✅ **Handle 5x more users** (1,000 → 5,000)
2. ✅ **Improve response times** by 40-50%
3. ✅ **Reduce server costs** (better resource utilization)
4. ✅ **Better user experience** (faster apps)
5. ✅ **Production-grade monitoring** (proactive issue detection)

**Recommendation:** Start with Phase 1 & 2 (caching) for maximum impact with minimal effort.

---

**Created:** November 5, 2025
**Status:** Ready for Implementation
**Priority:** High (significant improvements possible)
**Estimated Effort:** 4 weeks (incremental)

