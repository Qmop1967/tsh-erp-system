# Performance Optimization - TSH ERP Scale Strategies

**Purpose:** Actionable performance optimization strategies calibrated for TSH ERP's scale (500+ clients, 2,218+ products, 30+ daily orders).

**Last Updated:** 2025-11-12

---

## 🎯 Performance Philosophy

**Optimize based on data, not assumptions.**

- Measure first, optimize second
- Focus on user-impacting bottlenecks
- Understand the cost/benefit of each optimization
- Premature optimization is wasteful

**TSH ERP Scale Context:**
```yaml
Current Scale:
  - 500+ wholesale clients
  - 2,218+ products in inventory
  - 30 wholesale + 30 retail orders daily
  - 100+ partner salesmen
  - 12 travel salespeople
  - 8 Flutter mobile apps
  - 57 database tables (127 MB)

Growth Target (10x):
  - 5,000+ clients
  - 20,000+ products
  - 300+ daily orders
  - 1,000+ salespeople
```

---

## 📊 Performance Thresholds (TSH ERP Specific)

### Response Time Standards

```yaml
API Endpoints:
  Excellent: < 200ms (feels instant)
  Good: 200-500ms (acceptable for most operations)
  Acceptable: 500ms-2s (complex operations only)
  Slow: 2-5s (optimization required)
  Unacceptable: > 5s (users will complain)

Database Queries:
  Excellent: < 50ms (indexed queries)
  Good: 50-200ms (simple queries)
  Acceptable: 200ms-1s (complex joins, aggregations)
  Slow: 1-3s (optimization required)
  Unacceptable: > 3s (missing indexes, N+1 queries)

Page Load (Mobile Apps):
  Excellent: < 1s (instant feel)
  Good: 1-3s (acceptable)
  Acceptable: 3-5s (complex screens)
  Slow: > 5s (optimization required)
```

### Scale-Based Triggers

```yaml
MUST Paginate When:
  - Query returns > 100 records
  - List endpoint for products (2,218+)
  - List endpoint for clients (500+)
  - Order history, reports

MUST Add Index When:
  - Table has > 1,000 rows
  - Column used in WHERE clause frequently
  - Foreign key columns (always)
  - Search fields (name, SKU, email)

MUST Use Background Job When:
  - Operation takes > 5 seconds
  - Zoho sync operations
  - Report generation
  - Bulk imports/exports
  - Email sending (bulk)

MUST Implement Caching When:
  - Read:write ratio > 10:1
  - Data rarely changes (categories, settings)
  - Expensive computations (analytics, dashboards)
  - External API responses (Zoho data)
```

---

## 🤖 AI Performance Optimization (Claude Code)

### Minimize Context Loading Overhead

**Smart Loading Strategy:**
```yaml
Session Start:
✅ Load only Priority 1 files (AI_CONTEXT_RULES, PROJECT_VISION, QUICK_REFERENCE)
✅ Load additional files as needed for specific tasks
✅ Don't reload files already in context
✅ Reference .claude/ files instead of repeating content

During Session:
✅ Cache stable facts (tech stack, deployment rules, phase)
✅ Reuse previous reasoning for similar problems
✅ Build incrementally on previous work
✅ Avoid regenerating full responses when partial updates suffice
```

**Incremental Reasoning Patterns:**
```yaml
Instead of Full Regeneration:
❌ "Let me explain the entire Zoho migration strategy again..."
✅ "As covered in PROJECT_VISION.md, we're in Phase 1. For this task..."

Instead of Repeated Explanations:
❌ Explain FastAPI basics every time
✅ Reference ARCHITECTURE_RULES.md and focus on task-specific details

Instead of Full Code Rewrites:
❌ Rewrite entire file when only one function changed
✅ Use Edit tool to modify specific sections
```

### Context Caching Strategy

**Cache These Facts (Never Change):**
```yaml
Tech Stack:
- Backend: FastAPI + Python 3.9+
- Database: PostgreSQL 12+
- Frontend: React 18+ / Flutter Web
- Mobile: Flutter 3.0+
- Deployment: GitHub Actions → VPS
- Backup: AWS S3

Architecture Rules:
- All Zoho sync through TDS Core
- Deploy all components together
- Staging first, then production
- Arabic RTL mandatory
- Mobile-first design

Current Infrastructure:
- VPS IP: 167.71.39.50
- Database: PostgreSQL (127 MB, 57 tables)
- Products: 2,218+
- Clients: 500+
- Daily orders: 30+ wholesale, 30+ retail
```

**Re-verify Each Session (May Change):**
```yaml
- Current Zoho migration phase
- Active tasks/priorities
- Recent commits/changes
- Known bugs/issues
- New features added
```

### Efficient Communication

**Concise Responses:**
```yaml
For Simple Confirmations:
✅ "Done. Deployed to staging at staging.erp.tsh.sale"
❌ "I have successfully completed the deployment process to the staging
   environment. The application is now available at staging.erp.tsh.sale.
   All components including backend, frontend, and TDS Core have been deployed
   successfully. You can now proceed with testing..." (unnecessarily verbose)

For Status Updates:
✅ "Fixed bug in commission calculation. Testing now."
❌ "I have identified the root cause of the issue in the commission calculation
   logic and have implemented a fix. I am now proceeding to test the fix locally
   before deploying to staging..." (too verbose)

For Explanations:
✅ Explain WHY and WHAT, skip obvious details
❌ Explain every single step in exhaustive detail
```

### Structured Thinking Patterns

**Use Established Patterns from REASONING_PATTERNS.md:**
```yaml
For Debugging:
✅ Follow Root-Cause Analysis (5 Whys)
✅ Don't random-walk through solutions

For Trade-offs:
✅ Use Trade-Off Decision Framework
✅ Present pros/cons systematically

For Performance:
✅ Measure → Analyze → Optimize → Verify
✅ Don't optimize prematurely
```

### Detect Repetition (Auto-Summarize)

**When Same Task Repeats:**
```yaml
First Time:
- Explain fully
- Show code examples
- Provide context

Second Time (Same Session):
- Brief reminder
- Focus on differences
- Skip repeated explanations

Third+ Time:
- Recognize pattern
- Suggest abstraction/template
- Minimal explanation
```

**Example:**
```
First Request: "Add pagination to products endpoint"
Response: Full explanation of pagination, code example, testing steps

Second Request: "Add pagination to clients endpoint"
Response: "Same pagination pattern as products endpoint. Implementing..."
(No need to re-explain pagination concept)
```

---

## 🗄️ Database Optimization

### 1. Index Strategy for TSH ERP

**Required Indexes (MANDATORY):**

```sql
-- Products table (2,218+ rows, growing)
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_name_ar ON products(name_ar);
CREATE INDEX idx_products_zoho_item_id ON products(zoho_item_id);
CREATE INDEX idx_products_created_at ON products(created_at DESC);

-- Compound index for common filter combinations
CREATE INDEX idx_products_active_category ON products(is_active, category_id);

-- Clients table (500+ rows, growing)
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_name_ar ON clients(name_ar);
CREATE INDEX idx_clients_type ON clients(client_type);
CREATE INDEX idx_clients_is_active ON clients(is_active);
CREATE INDEX idx_clients_zoho_contact_id ON clients(zoho_contact_id);

-- Orders table (30+ daily, accumulating)
CREATE INDEX idx_orders_client_id ON orders(client_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_salesperson_id ON orders(salesperson_id);
CREATE INDEX idx_orders_order_date ON orders(order_date DESC);

-- Compound index for common queries
CREATE INDEX idx_orders_status_date ON orders(status, created_at DESC);

-- Order items (many per order)
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Audit/logging tables
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

**Index Maintenance:**

```sql
-- Check index usage (PostgreSQL)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- Find unused indexes (candidates for removal)
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexname NOT LIKE '%_pkey'  -- Exclude primary keys
ORDER BY schemaname, tablename;

-- Check index size (large indexes slow down writes)
SELECT
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

### 2. Query Optimization Patterns

**Pattern 1: Prevent N+1 Queries**

```python
# ❌ BAD: N+1 queries (101 queries for 100 orders)
def get_orders_bad(db: Session):
    orders = db.query(Order).limit(100).all()  # 1 query

    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "client": order.client.name,  # 100 additional queries!
            "items": [item.product.name for item in order.items]  # More N+1!
        })
    return result

# ✅ GOOD: Eager loading (2-3 queries total)
from sqlalchemy.orm import joinedload, selectinload

def get_orders_good(db: Session):
    orders = db.query(Order).options(
        joinedload(Order.client),              # Load clients in same query
        selectinload(Order.items).             # Load items in 2nd query
            joinedload(OrderItem.product)      # Load products with items
    ).limit(100).all()

    # All data loaded, no additional queries
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "client": order.client.name,       # No query
            "items": [item.product.name for item in order.items]  # No query
        })
    return result

# Performance: 2-3 queries vs 100+, ~50x faster
```

**Pattern 2: Optimize Aggregations**

```python
# ❌ BAD: Load all records to count
def get_order_stats_bad(db: Session):
    orders = db.query(Order).all()  # Loads ALL orders into memory
    total_orders = len(orders)
    total_revenue = sum(o.total_amount for o in orders)
    return {"total_orders": total_orders, "total_revenue": total_revenue}

# ✅ GOOD: Database-level aggregation
from sqlalchemy import func

def get_order_stats_good(db: Session):
    result = db.query(
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_amount).label('total_revenue')
    ).filter(Order.status == 'completed').first()

    return {
        "total_orders": result.total_orders,
        "total_revenue": float(result.total_revenue or 0)
    }

# Performance: Database does aggregation (100x faster, minimal memory)
```

**Pattern 3: Selective Column Loading**

```python
# ❌ BAD: Load all columns when only need few
def get_product_names_bad(db: Session):
    products = db.query(Product).all()  # Loads ALL columns
    return [{"id": p.id, "name": p.name} for p in products]

# ✅ GOOD: Load only needed columns
def get_product_names_good(db: Session):
    products = db.query(Product.id, Product.name).all()
    return [{"id": p.id, "name": p.name} for p in products]

# Performance: ~5x faster for large tables, less memory
```

**Pattern 4: Batch Operations**

```python
# ❌ BAD: Individual inserts (N queries)
def import_products_bad(products_data: list, db: Session):
    for product_data in products_data:
        product = Product(**product_data)
        db.add(product)
        db.commit()  # Commit each one (slow!)
    # 1000 products = 1000 commits

# ✅ GOOD: Bulk insert
def import_products_good(products_data: list, db: Session):
    products = [Product(**data) for data in products_data]
    db.bulk_save_objects(products)
    db.commit()  # Single commit
    # 1000 products = 1 commit (50-100x faster)

# Even better: Use bulk_insert_mappings for large imports
def import_products_best(products_data: list, db: Session):
    db.bulk_insert_mappings(Product, products_data)
    db.commit()
    # Fastest for large datasets
```

---

### 3. Connection Pool Tuning

**Current TSH ERP Scale:**

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

DATABASE_URL = os.getenv("DATABASE_URL")

# Optimized for TSH ERP scale
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,              # Base connections (current scale: 500 clients)
    max_overflow=40,           # Extra connections under load (total max: 60)
    pool_timeout=30,           # Wait 30s for connection before error
    pool_recycle=3600,         # Recycle connections every hour
    pool_pre_ping=True,        # Verify connection health before use
    echo=False                 # Set True for debugging SQL
)
```

**Scale Guidelines:**

```yaml
Small Scale (< 100 concurrent users):
  pool_size: 10
  max_overflow: 20
  Total max: 30

Current TSH Scale (500+ clients, 100+ salesmen):
  pool_size: 20
  max_overflow: 40
  Total max: 60

Large Scale (5,000+ clients, 1,000+ salesmen):
  pool_size: 50
  max_overflow: 100
  Total max: 150
  Consider: Connection pooler (PgBouncer)
```

**Monitor Connection Usage:**

```python
# Add to monitoring dashboard
from app.database import engine

def get_pool_status():
    """Get current connection pool statistics."""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }

# Alert if checked_out approaches max (pool exhaustion)
```

---

## 🚀 API Optimization

### 1. Response Payload Optimization

**Pattern: Selective Field Returns**

```python
# Define response schemas with only needed fields
from pydantic import BaseModel
from typing import Optional

# Minimal schema for list endpoints
class ProductMinimal(BaseModel):
    id: int
    name: str
    name_ar: str
    sku: str
    unit_price: float
    stock_quantity: int

    class Config:
        from_attributes = True

# Full schema for detail endpoints
class ProductDetail(ProductMinimal):
    description: Optional[str]
    description_ar: Optional[str]
    category: CategoryMinimal
    cost_price: float
    supplier: Optional[SupplierMinimal]
    created_at: datetime
    # ... more fields

# Usage
@router.get("/products", response_model=list[ProductMinimal])  # Lightweight
async def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.get("/products/{id}", response_model=ProductDetail)  # Full data
async def get_product(id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == id).first()
```

**Pattern: Response Compression**

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZIPMiddleware

app = FastAPI()

# Enable GZIP compression for responses > 1KB
app.add_middleware(
    GZIPMiddleware,
    minimum_size=1000,  # Only compress if > 1KB
    compresslevel=6     # Balance between speed and compression (1-9)
)

# Reduces payload size by 60-80% for large JSON responses
# Critical for mobile apps on slow networks
```

---

### 2. Caching Strategies

**What to Cache in TSH ERP:**

```yaml
Good Candidates (Read >> Write):
  - Categories: Rarely change, frequently accessed
  - System settings: Almost never change
  - User permissions: Change infrequently
  - Product list (with short TTL): High read, moderate write
  - Dashboard statistics (with TTL): Expensive to compute

Bad Candidates (Write-heavy or real-time):
  - Stock levels: Change frequently, must be accurate
  - Order status: Real-time updates needed
  - Client balances: Financial accuracy critical
  - Zoho sync data: Must be fresh
```

**Redis Cache Implementation:**

```python
# app/cache.py
import redis
import json
from typing import Optional, Any
from functools import wraps
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def cache_response(ttl: int = 300):  # Default 5 minutes
    """Decorator to cache API responses."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{func.__name__}:{json.dumps(kwargs, sort_keys=True)}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function if cache miss
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )

            return result
        return wrapper
    return decorator

# Usage
@router.get("/categories")
@cache_response(ttl=3600)  # Cache for 1 hour
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories (cached)."""
    categories = db.query(Category).filter(Category.is_active == True).all()
    return [{"id": c.id, "name": c.name, "name_ar": c.name_ar} for c in categories]

# Invalidate cache when categories are modified
@router.post("/categories")
async def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    new_category = Category(**category_data.dict())
    db.add(new_category)
    db.commit()

    # Invalidate cache
    redis_client.delete("get_categories:{}")

    return new_category
```

**Application-Level Cache (Simple, No Redis):**

```python
# For small datasets that fit in memory
from functools import lru_cache
from typing import List

@lru_cache(maxsize=1)
def get_categories_cached(db_url: str) -> List[dict]:
    """Cache categories in memory (evicted on app restart)."""
    db = Session(bind=create_engine(db_url))
    categories = db.query(Category).filter(Category.is_active == True).all()
    return [{"id": c.id, "name": c.name, "name_ar": c.name_ar} for c in categories]

# Note: LRU cache doesn't invalidate automatically
# Use Redis for production if possible
```

---

### 3. Async Operations for I/O-Bound Tasks

**When to Use Async:**

```yaml
Good for Async:
  - External API calls (Zoho, payment gateways)
  - File I/O operations (read/write files)
  - Network requests
  - Email sending
  - Multiple independent database queries

Not Good for Async:
  - CPU-intensive computations (use background jobs)
  - Single sequential database operations
  - Simple CRUD operations (overhead not worth it)
```

**Async Pattern:**

```python
# app/services/zoho_service.py
import httpx
from typing import List, Dict

class AsyncZohoService:
    """Async service for Zoho API calls."""

    def __init__(self):
        self.base_url = "https://www.zohoapis.com"
        self.timeout = httpx.Timeout(30.0)

    async def fetch_multiple_resources(self) -> Dict:
        """Fetch multiple Zoho resources in parallel."""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Execute multiple API calls concurrently
            products_task = client.get(f"{self.base_url}/inventory/v1/items")
            clients_task = client.get(f"{self.base_url}/books/v3/contacts")
            orders_task = client.get(f"{self.base_url}/books/v3/invoices")

            # Wait for all to complete
            products_res, clients_res, orders_res = await asyncio.gather(
                products_task,
                clients_task,
                orders_task
            )

        return {
            "products": products_res.json(),
            "clients": clients_res.json(),
            "orders": orders_res.json()
        }

        # Sequential: 3 x 500ms = 1.5s
        # Parallel: max(500ms) = 500ms (3x faster)
```

---

## 📱 Mobile App Optimization

### 1. Reduce Payload Size

**Optimizations for 8 Flutter Apps:**

```python
# Mobile-specific endpoint with minimal data
@router.get("/mobile/products")
async def list_products_mobile(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=50),  # Smaller pages for mobile
    db: Session = Depends(get_db)
):
    """Mobile-optimized product list."""

    offset = (page - 1) * per_page
    products = db.query(
        Product.id,
        Product.name,
        Product.name_ar,
        Product.sku,
        Product.unit_price,
        Product.stock_quantity,
        Product.image_url  # Only thumbnail, not full images
    ).filter(
        Product.is_active == True
    ).offset(offset).limit(per_page).all()

    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "name_ar": p.name_ar,
                "sku": p.sku,
                "price": p.unit_price,
                "stock": p.stock_quantity,
                "image": p.image_url  # Pre-optimized thumbnails
            }
            for p in products
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "has_more": len(products) == per_page
        }
    }
```

---

### 2. Image Optimization

```yaml
Image Guidelines for TSH ERP:
  Thumbnails (Lists): 200x200px, JPEG 80% quality, < 20KB
  Product Images (Detail): 800x800px, JPEG 85% quality, < 150KB
  Full Resolution (Zoom): 1600x1600px, JPEG 90% quality, < 500KB

Storage:
  - Use S3 or CDN for images (not VPS)
  - Generate thumbnails on upload (not on-demand)
  - Serve WebP format (50% smaller than JPEG)
  - Use lazy loading in mobile apps
```

---

## ⚡ Background Jobs for Long Operations

**Use Celery or RQ for:**

```yaml
Operations > 5 seconds:
  - Zoho full sync (15+ minutes)
  - Report generation (PDF, Excel)
  - Bulk data imports (CSV, Excel)
  - Bulk email sending
  - Image processing (resize, optimize)
  - Database maintenance tasks

Pattern:
  1. API endpoint creates job
  2. Returns job_id immediately
  3. Client polls job status
  4. Job completes, result available
```

**Example Implementation:**

```python
# Using Celery
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def generate_sales_report(start_date: str, end_date: str, user_id: int):
    """Generate sales report in background."""
    # Long-running operation
    report_data = compute_sales_report(start_date, end_date)
    pdf_path = generate_pdf(report_data)

    # Notify user via email or notification
    send_report_email(user_id, pdf_path)

    return {"status": "completed", "file": pdf_path}

# API endpoint
@router.post("/reports/sales")
async def request_sales_report(
    report_params: SalesReportRequest,
    current_user: User = Depends(get_current_user)
):
    """Request sales report generation (async)."""

    # Create background job
    task = generate_sales_report.delay(
        report_params.start_date,
        report_params.end_date,
        current_user.id
    )

    return {
        "job_id": task.id,
        "status": "processing",
        "message": "Report generation started. You'll receive an email when ready."
    }

# Status endpoint
@router.get("/reports/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Check report generation status."""
    task = celery.AsyncResult(job_id)

    return {
        "job_id": job_id,
        "status": task.state,  # PENDING, STARTED, SUCCESS, FAILURE
        "result": task.result if task.ready() else None
    }
```

---

## 📈 Monitoring & Profiling

### 1. Performance Monitoring

**Key Metrics to Track:**

```python
# Add to monitoring middleware
from time import time
from fastapi import Request

@app.middleware("http")
async def add_performance_metrics(request: Request, call_next):
    """Track API performance metrics."""

    start_time = time()
    response = await call_next(request)
    duration = time() - start_time

    # Log slow requests
    if duration > 2.0:  # > 2 seconds
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {duration:.2f}s"
        )

    # Add performance header
    response.headers["X-Process-Time"] = f"{duration:.4f}"

    return response
```

**Database Query Profiling:**

```python
# Enable SQL logging in development
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Shows all SQL queries with timing
# Find slow queries and optimize
```

---

### 2. Load Testing

**Benchmark TSH ERP Endpoints:**

```python
# Use locust for load testing
from locust import HttpUser, task, between

class TSHERPUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)  # 30% of requests
    def list_products(self):
        self.client.get("/api/products?page=1&limit=100")

    @task(2)  # 20% of requests
    def get_product_detail(self):
        product_id = random.randint(1, 2218)
        self.client.get(f"/api/products/{product_id}")

    @task(1)  # 10% of requests
    def create_order(self):
        self.client.post("/api/orders", json={
            "client_id": random.randint(1, 500),
            "items": [{"product_id": 1, "quantity": 1}]
        })

# Run: locust -f test_performance.py --host=https://staging.erp.tsh.sale
# Simulate 500 concurrent users to test current scale
```

---

## ✅ Performance Optimization Checklist

**Before Declaring "Performance Optimized":**

```yaml
Database:
□ All foreign keys indexed
□ Search fields indexed (name, sku, email)
□ Filter fields indexed (is_active, status, category_id)
□ No N+1 queries (use joinedload/selectinload)
□ Aggregations done in database (not Python)
□ Pagination on all list endpoints (max 100)
□ Connection pool configured for scale

API:
□ Response payloads minimized (only needed fields)
□ GZIP compression enabled
□ Caching for read-heavy endpoints (categories, settings)
□ Mobile-specific endpoints (smaller payloads)
□ Background jobs for operations > 5 seconds
□ Async for I/O-bound operations

Mobile Apps:
□ Smaller page sizes (25-50 vs 100)
□ Thumbnail images (< 20KB)
□ Lazy loading implemented
□ Offline caching for static data

Monitoring:
□ Slow query logging enabled
□ Performance metrics tracked
□ Load testing completed (500 concurrent users)
□ Alert thresholds configured (> 2s response time)
```

---

## 🎯 Quick Wins for TSH ERP

**Immediate optimizations with high ROI:**

1. **Add missing indexes** (30 minutes, 10-50x faster queries)
2. **Fix N+1 queries** (1 hour per endpoint, 20-100x faster)
3. **Add pagination** (30 minutes per endpoint, prevents timeouts)
4. **Enable GZIP compression** (5 minutes, 60-80% smaller payloads)
5. **Cache categories/settings** (30 minutes, instant responses)

**Expected Results:**
- API response times: 2-5s → < 500ms
- Mobile app load times: 5-10s → < 2s
- Database query times: 1-3s → < 200ms
- Server load: 60-80% → 20-40%

---

**END OF PERFORMANCE_OPTIMIZATION.MD**

*Optimize based on measurement, not assumption. Focus on user-impacting bottlenecks first.*
