# Phase 2 Implementation Plan - Mobile BFF & Background Jobs

**Created:** November 5, 2025
**Status:** Ready to Start
**Prerequisites:** ✅ Phase 1 Complete (Monolithic Backend + Redis)
**Timeline:** 2-3 weeks
**Priority:** High

---

## Phase 2 Overview

### Goals:
1. **Mobile BFF Expansion** - Reduce API calls by 72%
2. **Background Jobs (Celery)** - Improve API response times by 30%
3. **Advanced Caching** - Implement cache warming and invalidation
4. **Performance Monitoring** - Set up comprehensive monitoring

### Expected Impact:
- **API Calls:** -72% (from mobile apps)
- **Response Time:** -30% (for long-running operations)
- **Data Transfer:** -80% (mobile bandwidth savings)
- **Battery Life:** +20% improvement (mobile)
- **User Experience:** Significantly smoother and faster

---

## Part 1: Mobile BFF Expansion (Week 1-2)

### What is Mobile BFF?

**BFF = Backend for Frontend**

Instead of mobile apps making multiple API calls to fetch related data, BFF endpoints return everything in one call.

### Example Transformation:

#### Before (Multiple Calls):
```dart
// Mobile app makes 5 separate API calls
1. GET /api/products/{id}           // 150ms
2. GET /api/inventory/{product_id}  // 120ms
3. GET /api/pricing/{product_id}    // 100ms
4. GET /api/images/{product_id}     // 200ms
5. GET /api/reviews/{product_id}    // 130ms
// Total: 700ms + 5 network requests
```

#### After (Single BFF Call):
```dart
// Mobile app makes 1 BFF call
1. GET /api/mobile/products/{id}/complete  // 180ms
// Returns: product + inventory + pricing + images + reviews
// Total: 180ms + 1 network request
// Savings: 520ms (74%) + 4 fewer requests
```

---

## BFF Endpoints to Implement

### Priority 1: Salesperson App (Most Used)

#### 1.1 Product Complete View
```python
# app/routers/mobile_bff.py

@router.get("/mobile/products/{product_id}/complete")
async def get_product_complete(product_id: int):
    """
    Returns complete product data in single call

    Includes:
    - Product details
    - Current inventory (all branches)
    - Pricing (all pricelists)
    - Images
    - Recent sales history
    - Similar products
    """
    # Implementation uses Redis cache + parallel DB queries
    pass
```

**Benefit:** 5 API calls → 1 call (80% reduction)

#### 1.2 Customer Complete View
```python
@router.get("/mobile/customers/{customer_id}/complete")
async def get_customer_complete(customer_id: int):
    """
    Returns complete customer data

    Includes:
    - Customer details
    - Outstanding balance
    - Recent orders
    - Credit limit
    - Payment history
    - Assigned salesperson
    """
    pass
```

**Benefit:** 6 API calls → 1 call (83% reduction)

#### 1.3 Order Creation (Optimized)
```python
@router.post("/mobile/orders/create-complete")
async def create_order_complete(order_data: OrderCreate):
    """
    Creates order with all validations in one call

    Validates:
    - Customer credit limit
    - Product availability
    - Pricing validity
    - User permissions

    Returns:
    - Created order
    - Updated inventory
    - Customer balance
    - PDF invoice URL
    """
    pass
```

**Benefit:** 4 API calls → 1 call (75% reduction)

#### 1.4 Dashboard Summary
```python
@router.get("/mobile/salesperson/dashboard")
async def get_salesperson_dashboard(user_id: int):
    """
    Returns complete dashboard data

    Includes:
    - Today's sales summary
    - Monthly target progress
    - Top products
    - Recent orders
    - Pending approvals
    - Notifications
    """
    pass
```

**Benefit:** 8 API calls → 1 call (88% reduction)

---

### Priority 2: Admin App (Second Most Used)

#### 2.1 Admin Dashboard
```python
@router.get("/mobile/admin/dashboard")
async def get_admin_dashboard():
    """
    Complete admin overview

    Includes:
    - Sales summary (today, week, month)
    - Inventory alerts
    - Pending approvals
    - System health
    - Recent activities
    - Financial summary
    """
    pass
```

#### 2.2 Inventory Complete View
```python
@router.get("/mobile/inventory/{product_id}/complete")
async def get_inventory_complete(product_id: int):
    """
    Complete inventory status

    Includes:
    - Stock levels (all branches)
    - Pending transfers
    - Recent movements
    - Reorder recommendations
    - Supplier information
    """
    pass
```

---

### Priority 3: Other Apps (Weeks 2)

#### 3.1 Accounting App BFF
- Financial dashboard
- Invoice complete view
- Payment complete view

#### 3.2 HR App BFF
- Employee complete view
- Attendance dashboard
- Payroll summary

#### 3.3 Inventory App BFF
- Stock movements complete
- Transfer complete view
- Adjustment complete view

---

## Implementation Strategy

### Week 1: Core BFF Infrastructure

#### Day 1-2: Setup & Architecture
```python
# File structure:
app/
├── routers/
│   └── mobile_bff.py          # Main BFF router
├── services/
│   ├── bff/
│   │   ├── __init__.py
│   │   ├── product_bff.py     # Product BFF service
│   │   ├── customer_bff.py    # Customer BFF service
│   │   └── order_bff.py       # Order BFF service
│   └── cache/
│       └── bff_cache.py       # BFF-specific caching
└── schemas/
    └── mobile/
        ├── product_complete.py
        ├── customer_complete.py
        └── order_complete.py
```

**Tasks:**
- [x] Phase 1 complete
- [ ] Create BFF directory structure
- [ ] Implement base BFF service class
- [ ] Set up BFF caching strategy
- [ ] Create response schemas

#### Day 3-4: Salesperson App BFF (Priority 1)
- [ ] Implement product complete endpoint
- [ ] Implement customer complete endpoint
- [ ] Implement order creation endpoint
- [ ] Implement dashboard endpoint
- [ ] Add comprehensive caching
- [ ] Write unit tests

#### Day 5: Testing & Optimization
- [ ] Load testing
- [ ] Performance optimization
- [ ] Cache tuning
- [ ] Documentation

### Week 2: Expand to Other Apps

#### Day 6-7: Admin App BFF
- [ ] Admin dashboard endpoint
- [ ] Inventory complete endpoint
- [ ] Reports BFF endpoints
- [ ] Testing

#### Day 8-9: Remaining Apps
- [ ] Accounting BFF
- [ ] HR BFF
- [ ] Other apps BFF endpoints

#### Day 10: Integration & Testing
- [ ] End-to-end testing
- [ ] Performance validation
- [ ] Documentation updates
- [ ] Deploy to production

---

## Part 2: Background Jobs with Celery (Week 2-3)

### Why Celery?

Move long-running tasks to background workers:
- **Email sending** - Don't block API response
- **Zoho sync** - Run async
- **Report generation** - Process in background
- **Image processing** - Optimize async
- **Bulk operations** - Handle efficiently

### Installation & Setup

#### Day 1: Infrastructure Setup
```bash
# Install dependencies
pip install celery redis flower

# Create Celery app
# app/background/__init__.py
from celery import Celery

celery_app = Celery(
    "tsh_erp",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2"
)
```

**Tasks:**
- [ ] Install Celery and dependencies
- [ ] Configure Celery app
- [ ] Set up Redis as broker
- [ ] Create worker service
- [ ] Set up Flower (monitoring UI)

#### Day 2-3: Migrate Tasks to Background

##### Task 1: Email Sending
```python
# Before: Blocking
@router.post("/api/orders/create")
async def create_order(order_data: OrderCreate):
    order = await create_order_in_db(order_data)
    await send_email(order)  # Blocks for 2-3 seconds ❌
    return order

# After: Non-blocking
@router.post("/api/orders/create")
async def create_order(order_data: OrderCreate):
    order = await create_order_in_db(order_data)
    send_email_task.delay(order.id)  # Returns immediately ✅
    return order

# Background task
@celery_app.task
def send_email_task(order_id: int):
    order = get_order(order_id)
    send_email(order)
```

**Tasks to Move to Background:**
- [ ] Email notifications
- [ ] PDF generation
- [ ] Image optimization
- [ ] Report generation
- [ ] Zoho synchronization
- [ ] Data exports
- [ ] Bulk updates

#### Day 4: Scheduled Tasks

```python
# Celery beat for scheduled tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'sync-zoho-every-hour': {
        'task': 'app.background.tasks.sync_zoho',
        'schedule': crontab(minute=0),  # Every hour
    },
    'cleanup-old-logs': {
        'task': 'app.background.tasks.cleanup_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

**Scheduled Tasks:**
- [ ] Zoho sync (hourly)
- [ ] Database cleanup (daily)
- [ ] Report generation (daily)
- [ ] Cache warming (hourly)
- [ ] Backup creation (daily)

---

## Part 3: Advanced Caching Strategy

### Cache Warming

```python
# app/services/cache/warming.py

async def warm_critical_caches():
    """
    Pre-populate Redis cache with frequently accessed data
    """
    # Products
    await cache_all_active_products()

    # Customers
    await cache_active_customers()

    # Pricelists
    await cache_all_pricelists()

    # Users
    await cache_active_users()
```

**Schedule:** Run every 6 hours

### Cache Invalidation

```python
# app/services/cache/invalidation.py

async def invalidate_product_cache(product_id: int):
    """
    Invalidate all cache entries related to a product
    """
    patterns = [
        f"product:{product_id}:*",
        f"products:list:*",
        f"inventory:{product_id}:*",
    ]

    for pattern in patterns:
        await redis.delete_pattern(pattern)
```

**Tasks:**
- [ ] Implement cache warming
- [ ] Implement smart invalidation
- [ ] Set up cache monitoring
- [ ] Document cache patterns

---

## Part 4: Performance Monitoring

### Prometheus + Grafana Setup

#### Metrics to Track:
- **API Response Times** (by endpoint)
- **Cache Hit Rate** (by key pattern)
- **Database Query Times**
- **Celery Task Status**
- **Error Rates**
- **Active Users**

### Implementation:
```python
# Install prometheus client
pip install prometheus-client

# app/core/metrics.py
from prometheus_client import Counter, Histogram

api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
api_latency = Histogram('api_latency_seconds', 'API latency', ['endpoint'])
cache_hits = Counter('cache_hits_total', 'Cache hits', ['pattern'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['pattern'])
```

**Tasks:**
- [ ] Install Prometheus
- [ ] Configure metrics collection
- [ ] Set up Grafana dashboards
- [ ] Create alerting rules
- [ ] Document monitoring setup

---

## Testing Strategy

### Performance Testing

```bash
# Load test BFF endpoints
ab -n 1000 -c 50 https://erp.tsh.sale/api/mobile/products/123/complete

# Expected results:
# - Response time < 200ms (p50)
# - Response time < 300ms (p95)
# - Response time < 500ms (p99)
# - 0 errors
```

### Comparison Testing

| Endpoint | Before (Multiple Calls) | After (BFF) | Improvement |
|----------|------------------------|-------------|-------------|
| Product View | 700ms (5 calls) | 180ms (1 call) | 74% |
| Customer View | 800ms (6 calls) | 200ms (1 call) | 75% |
| Order Create | 1200ms (4 calls) | 350ms (1 call) | 71% |
| Dashboard | 2500ms (8 calls) | 450ms (1 call) | 82% |

---

## Deployment Plan

### Phase 2A: BFF Endpoints (Week 2)
```bash
# Deploy BFF endpoints
git checkout -b feature/mobile-bff
# ... implement BFF endpoints ...
git push origin feature/mobile-bff

# Deploy to staging
ssh root@erp.tsh.sale 'cd /opt/tsh_erp/releases/green && git fetch && git checkout feature/mobile-bff && systemctl restart tsh_erp-green'

# Test thoroughly
# Deploy to production when ready
```

### Phase 2B: Celery Workers (Week 3)
```bash
# Install Celery on VPS
ssh root@erp.tsh.sale 'pip install celery redis flower'

# Create systemd services
# - celery-worker.service
# - celery-beat.service
# - flower.service

# Start services
systemctl enable --now celery-worker
systemctl enable --now celery-beat
systemctl enable --now flower

# Monitor at http://erp.tsh.sale:5555
```

---

## Success Metrics

### BFF Success Criteria:
- [ ] API calls reduced by > 70%
- [ ] Mobile data usage reduced by > 75%
- [ ] Response times improved by > 50%
- [ ] All mobile apps updated
- [ ] Zero regression in functionality

### Celery Success Criteria:
- [ ] Email sending < 100ms API response
- [ ] Background tasks completing successfully
- [ ] Worker health monitoring active
- [ ] Scheduled tasks running on time
- [ ] Zero task failures

### Overall Phase 2 Success:
- [ ] 72% reduction in mobile API calls
- [ ] 30% improvement in API response times
- [ ] Cache hit rate > 80%
- [ ] Monitoring dashboards operational
- [ ] Documentation complete

---

## Risk Management

### Risks & Mitigation:

#### Risk 1: BFF Endpoints Too Slow
**Mitigation:**
- Implement aggressive caching
- Use database query optimization
- Parallel data fetching
- Connection pooling

#### Risk 2: Celery Workers Overwhelmed
**Mitigation:**
- Set worker concurrency limits
- Implement task priorities
- Monitor queue lengths
- Scale workers if needed

#### Risk 3: Cache Memory Exhaustion
**Mitigation:**
- Set Redis maxmemory limit (256MB)
- Implement LRU eviction policy
- Monitor memory usage
- Optimize cache patterns

---

## Timeline Summary

### Week 1: BFF Core
- Days 1-2: Infrastructure setup
- Days 3-4: Salesperson App BFF
- Day 5: Testing & optimization

### Week 2: BFF Expansion + Celery Setup
- Days 6-7: Admin App BFF
- Days 8-9: Other Apps BFF
- Day 10: Celery infrastructure

### Week 3: Celery + Monitoring
- Days 11-12: Background tasks migration
- Days 13-14: Monitoring setup
- Day 15: Final testing & deployment

---

## Next Actions

### Immediate (Today):
1. ✅ Phase 1 deployed and monitored
2. ✅ Performance baseline established
3. ✅ Phase 2 plan created
4. [ ] Review plan with team
5. [ ] Get approval to proceed

### Tomorrow (Day 1):
1. [ ] Create feature branch
2. [ ] Set up BFF directory structure
3. [ ] Implement base BFF classes
4. [ ] Start salesperson BFF endpoints

### This Week:
1. [ ] Complete salesperson app BFF
2. [ ] Update Flutter salesperson app
3. [ ] Test and measure improvements
4. [ ] Deploy to staging

---

## Resources Needed

### Development:
- 1 Backend developer (full-time, 3 weeks)
- 1 Mobile developer (part-time, for Flutter updates)
- 1 DevOps engineer (part-time, for Celery setup)

### Infrastructure:
- Current VPS sufficient (already has Redis)
- No additional costs

### Tools:
- Celery (free, open source)
- Flower (free, open source)
- Prometheus (free, open source)
- Grafana (free, open source)

---

## Documentation to Create

- [ ] BFF API Documentation
- [ ] Celery Tasks Documentation
- [ ] Cache Patterns Guide
- [ ] Monitoring Setup Guide
- [ ] Flutter Integration Guide
- [ ] Performance Comparison Report

---

**Status:** ✅ Ready to Start
**Priority:** High
**Expected Duration:** 2-3 weeks
**Expected ROI:** 72% fewer API calls, 30% faster response times

**Created:** November 5, 2025
**Last Updated:** November 5, 2025

**Made with ❤️ for TSH Business Operations**
