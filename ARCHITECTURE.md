# 🏗️ TSH ERP Architecture Documentation

**Last Updated:** November 5, 2025
**Version:** 2.0 (BFF Migration)
**Status:** 🔄 Migration to BFF Architecture in Progress

---

## 📊 System Overview

TSH ERP is a comprehensive Enterprise Resource Planning system built with:

### Technology Stack
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 14+ with Row-Level Security (RLS)
- **Cache:** Redis (for performance optimization)
- **Mobile Apps:** Flutter (11 apps)
- **Authentication:** JWT (JSON Web Tokens)
- **Background Jobs:** Async workers for Zoho sync
- **API Documentation:** OpenAPI/Swagger

### System Scale
- **230 Python files** in codebase
- **538 API endpoints** currently available
- **49 routers** registered
- **11 mobile applications** supported
- **Production deployment** at https://erp.tsh.sale

---

## 🎯 Current Architecture Status

### ⚠️ IMPORTANT: We are migrating from Legacy to BFF Architecture

The system currently runs **two architectural patterns simultaneously** during the migration period:

---

## 1️⃣ Legacy Pattern (⚠️ MAINTENANCE MODE ONLY)

### Location
- `app/routers/` (most routers)
- `app/services/` (direct service calls)
- `app/models/` and `app/schemas/`

### Characteristics
- ❌ Direct API endpoints for each entity
- ❌ Multiple API calls required for complex screens
- ❌ Large response payloads
- ❌ No mobile optimization
- ❌ Limited caching

### Status
**🔴 DEPRECATED - Only for bug fixes**

**Guidelines:**
- ✅ Fix bugs in existing endpoints
- ❌ Do NOT add new features here
- ❌ Do NOT add new routers to this pattern
- 📋 Plan migration of each endpoint to BFF

### Example Endpoints
```
GET  /api/customers
GET  /api/products
GET  /api/orders
POST /api/sales
```

---

## 2️⃣ BFF Pattern (✅ TARGET ARCHITECTURE)

### Location
- `app/bff/` - All BFF implementations
- `app/bff/mobile/` - Mobile-specific BFF layer
- `app/services/bff/` - BFF service layer

### Characteristics
- ✅ Mobile-optimized endpoints
- ✅ Aggregates multiple service calls
- ✅ Minimized response payloads (-80% size)
- ✅ Aggressive caching strategies
- ✅ Offline-first ready
- ✅ Single API call per screen

### Status
**🟢 ACTIVE - Use for all new features**

### BFF Endpoints by App

#### Consumer App
```
/api/mobile/consumer/home              - Home screen data aggregation
/api/mobile/consumer/products/{id}     - Product detail
/api/mobile/consumer/categories/{id}   - Category products
/api/mobile/consumer/search            - Product search
/api/mobile/consumer/cart              - Shopping cart
/api/mobile/consumer/checkout/prepare  - Checkout data
```

#### Salesperson App
```
/api/mobile/salesperson/home           - Dashboard & stats
/api/mobile/salesperson/customers/{id} - Customer profile
/api/mobile/salesperson/orders/draft   - Create draft order
/api/mobile/salesperson/orders/submit  - Submit order
/api/mobile/salesperson/visits/record  - Record customer visit
```

#### POS App
```
/api/mobile/pos/home                   - POS home screen
/api/mobile/pos/transaction/start      - Start new transaction
/api/mobile/pos/transaction/add-item   - Add item to transaction
/api/mobile/pos/transaction/pay        - Process payment
```

### BFF Implementation Status

| Mobile App | Endpoint Prefix | Status |
|-----------|-----------------|--------|
| Consumer | `/api/mobile/consumer/` | 🟡 Partial |
| Salesperson | `/api/mobile/salesperson/` | ⏳ Planned |
| POS | `/api/mobile/pos/` | ⏳ Planned |
| Admin | `/api/mobile/admin/` | ⏳ Planned |
| Accounting | `/api/mobile/accounting/` | ⏳ Planned |
| Warehouse | `/api/mobile/warehouse/` | ⏳ Planned |
| Reports | `/api/mobile/reports/` | ⏳ Planned |
| HR | `/api/mobile/hr/` | ⏳ Planned |
| Maintenance | `/api/mobile/maintenance/` | ⏳ Planned |
| Inventory | `/api/mobile/inventory/` | ⏳ Planned |
| Delivery | `/api/mobile/delivery/` | ⏳ Planned |

---

## 📁 Directory Structure

```
app/
├── main.py                  # FastAPI application entry point
├── core/                    # Core configuration & dependencies
│   ├── config.py           # Application settings
│   ├── dependencies.py     # Dependency injection
│   ├── cache.py            # Redis caching manager
│   └── database.py         # (use app/db/database.py instead)
├── db/                      # Database layer
│   ├── database.py         # SQLAlchemy setup & session management
│   ├── rls_context.py      # Row-Level Security context
│   └── rls_dependency.py   # RLS dependencies
├── models/                  # SQLAlchemy ORM models (34 files)
│   ├── user.py
│   ├── customer.py
│   ├── product.py
│   ├── order.py
│   ├── hr.py               # ⚠️ Large file (642 lines) - needs splitting
│   └── ...
├── schemas/                 # Pydantic validation schemas (23 files)
│   ├── auth.py
│   ├── customer.py
│   ├── product.py
│   └── ...
├── routers/                 # API endpoints (63 routers - NEEDS CLEANUP)
│   ├── auth.py             # ❌ Deprecated
│   ├── auth_enhanced.py    # ✅ Current auth system
│   ├── auth_simple.py      # ❌ Deprecated
│   ├── settings.py         # ⚠️ HUGE (1,764 lines) - needs splitting
│   ├── customers.py
│   ├── products.py
│   ├── orders.py
│   └── v2/                 # Clean Architecture (V2 APIs)
│       ├── customers.py
│       ├── products.py
│       ├── orders.py
│       └── inventory.py
├── services/                # Business logic layer (46 services)
│   ├── customer_service.py
│   ├── product_service.py
│   ├── order_service.py
│   ├── bff/                # BFF services
│   │   ├── base_bff.py
│   │   ├── customer_bff.py
│   │   ├── product_bff.py
│   │   └── order_bff.py
│   └── security/           # Security services (⚠️ needs consolidation)
│       ├── auth_service.py
│       ├── enhanced_auth_security.py
│       ├── advanced_security_service.py
│       └── ...
├── bff/                     # Backend For Frontend layer
│   └── mobile/             # Mobile BFF implementation
│       ├── router.py       # Main BFF router
│       ├── schemas.py      # Mobile-optimized schemas
│       ├── aggregators/    # Data aggregation logic
│       ├── cache/          # BFF-specific caching
│       └── transformers/   # Response transformers
├── background/              # Background workers
│   ├── worker_manager.py
│   ├── zoho_sync_worker.py
│   └── zoho_entity_handlers.py
├── utils/                   # Utility functions
│   ├── logging_config.py
│   ├── hashing.py
│   ├── rate_limiter.py
│   └── ...
└── tests/                   # Test suite (⚠️ needs expansion)
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 🔐 Authentication System

### Current System: Enhanced Authentication

**Router:** `app/routers/auth_enhanced.py` (748 lines)
**Service:** `app/services/auth_service.py`

#### Features
- ✅ JWT Token-based authentication
- ✅ Access tokens (30 min expiry)
- ✅ Refresh tokens (7 days expiry)
- ✅ Multi-Factor Authentication (MFA)
- ✅ Session management
- ✅ Role-Based Access Control (RBAC)
- ✅ Row-Level Security (RLS)

#### Authentication Endpoints
```python
POST /api/auth/login           # Login with email/password
POST /api/auth/logout          # Logout current user
POST /api/auth/refresh         # Refresh access token
POST /api/auth/forgot-password # Request password reset
POST /api/auth/reset-password  # Reset password with token
POST /api/auth/mfa/setup       # Setup MFA
POST /api/auth/mfa/verify      # Verify MFA code
```

#### Using Authentication in Requests

**Header:**
```
Authorization: Bearer <access_token>
```

**Example (curl):**
```bash
# Login
curl -X POST https://erp.tsh.sale/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@tsh.sale&password=yourpassword"

# Use token
curl https://erp.tsh.sale/api/customers \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### ❌ Deprecated Authentication Routers

**DO NOT USE:**
- `app/routers/auth.py` - Old implementation
- `app/routers/auth_simple.py` - Simplified version
- `app/routers/advanced_security.py` - Being merged into auth_enhanced

These will be removed in a future release.

---

## 🔄 Clean Architecture (V2 APIs)

### Status: Partially Implemented

**Location:** `app/routers/v2/`

### Layers

#### 1. Domain Layer (❌ NOT IMPLEMENTED)
```
app/domain/
├── entities/           # Business entities (empty)
└── exceptions/         # Domain exceptions (empty)
```

#### 2. Application Layer (🟡 Partial)
```
app/application/
├── services/           # Application services (4 files)
├── dtos/              # Data Transfer Objects (4 files)
├── interfaces/        # Repository interfaces
└── use_cases/         # Use cases (empty)
```

#### 3. Infrastructure Layer (✅ Implemented)
```
app/infrastructure/
└── repositories/
    └── sqlalchemy/    # SQLAlchemy repositories (4 files)
```

### V2 Endpoints

```
GET  /api/v2/customers
POST /api/v2/customers
GET  /api/v2/customers/{id}

GET  /api/v2/products
POST /api/v2/products
GET  /api/v2/products/{id}

GET  /api/v2/orders
POST /api/v2/orders
GET  /api/v2/orders/{id}

GET  /api/v2/inventory
POST /api/v2/inventory/stock-movement
```

---

## 🔄 Data Flow

### Legacy Pattern (Current)
```
Mobile App → API Endpoint → Service → Database → Service → API → Mobile App
  (5-10 API calls per screen)
```

### BFF Pattern (Target)
```
Mobile App → BFF Endpoint → Aggregator → [Multiple Services] → Database
                                      ↓
                                  Transformer → Cache → Mobile App
  (1 API call per screen)
```

### Example: Consumer Home Screen

**Legacy (5 API calls):**
```javascript
// Mobile app makes 5 separate calls
GET /api/banners
GET /api/products/featured
GET /api/categories
GET /api/orders?user_id=123&recent=true
GET /api/recommendations?user_id=123
```

**BFF (1 API call):**
```javascript
// Mobile app makes 1 call
GET /api/mobile/consumer/home

// Backend aggregates and returns everything:
{
  "banners": [...],
  "featuredProducts": [...],
  "categories": [...],
  "recentOrders": [...],
  "recommendations": [...]
}
```

**Benefits:**
- 80% fewer API calls
- 80% smaller total payload size
- 70% faster screen load time
- Better offline support
- Reduced mobile data usage

---

## 🗄️ Database Architecture

### Database: PostgreSQL 14+

**Connection Details:**
- Host: localhost
- Port: 5432
- Database: tsh_erp
- User: postgres

### Key Features

#### 1. Row-Level Security (RLS)
- User-specific data access
- Branch-based data scoping
- Automatic filtering in queries

#### 2. Multi-Branch Support
- Each transaction tied to a branch
- Branch-specific inventory
- Branch-level reporting

#### 3. Audit Trail
- All changes logged
- User tracking
- Timestamp tracking

### Main Tables

```sql
-- Core Tables
users                -- System users
roles                -- User roles
branches             -- Company branches
warehouses           -- Warehouses

-- Business Tables
customers            -- Customer records
products             -- Product catalog
orders               -- Sales orders
inventory_items      -- Inventory tracking
invoices             -- Sales/Purchase invoices

-- Accounting
accounts             -- Chart of accounts
journal_entries      -- Accounting entries
cash_transactions    -- Cash flow

-- HR
employees            -- Employee records
attendance           -- Attendance tracking
payroll              -- Payroll processing
```

---

## ⚡ Performance Optimization

### Caching Strategy

**Redis Cache:**
- Product catalog (10 min TTL)
- Home screen data (5 min TTL)
- User sessions (30 min TTL)
- Search results (15 min TTL)

**Cache Patterns:**
```python
# Product caching
@cache_manager.cache(key="product:{id}", ttl=600)
async def get_product(product_id: int):
    return await product_service.get(product_id)

# BFF caching
@BFFCache.cache_home_screen(ttl=300)
async def get_home_data(user_id: int):
    return await consumer_bff.get_home_data(user_id)
```

### Database Optimization

**Indexes Applied:**
- Customer email (unique)
- Product SKU (unique)
- Order date (btree)
- Invoice number (unique)
- All foreign keys

**Query Optimization:**
- Connection pooling (20 connections)
- Prepared statements
- Batch operations
- Async queries

---

## 🔒 Security

### Authentication
- JWT tokens with 30-minute expiry
- Refresh tokens for re-authentication
- Password hashing (bcrypt)
- MFA support

### Authorization
- Role-Based Access Control (RBAC)
- Permission-based access
- Row-Level Security (RLS)
- Data scope filtering

### API Security
- Rate limiting (100 req/min authenticated, 20 req/min anonymous)
- CORS restrictions (production)
- SQL injection prevention (ORM)
- XSS prevention (input validation)

### CORS Configuration
```python
# Production allowed origins
allowed_origins = [
    "https://erp.tsh.sale",
    "https://shop.tsh.sale",
    "capacitor://localhost",  # Mobile apps
    # ... specific domains only
]
```

---

## 📱 Mobile Applications

### 11 Flutter Applications

1. **Consumer App** - Product browsing & ordering
2. **Salesperson App** - Field sales & customer management
3. **POS App** - Point of sale for retail
4. **Admin App** - System administration
5. **Accounting App** - Financial management
6. **Warehouse App** - Inventory management
7. **Reports App** - Analytics & reporting
8. **HR App** - Employee management
9. **Maintenance App** - Equipment maintenance
10. **Inventory App** - Stock management
11. **Delivery App** - Delivery tracking

### Mobile App Architecture

```
Flutter App
    ↓
BFF Endpoint (/api/mobile/{app}/)
    ↓
Aggregator Service
    ↓
[Multiple Backend Services]
    ↓
Database
```

---

## 🚀 Deployment

### Production Environment
- **URL:** https://erp.tsh.sale
- **Server:** VPS (167.71.39.50)
- **Location:** /home/deploy/TSH_ERP_Ecosystem
- **Service:** systemd (tsh-erp.service)
- **Workers:** 4 Gunicorn workers
- **Proxy:** Nginx

### Health Check
```bash
curl https://erp.tsh.sale/health

# Response:
{
  "status": "healthy",
  "message": "النظام يعمل بشكل طبيعي"
}
```

### Monitoring
- Application logs: `/var/log/tsh-erp/`
- System logs: `journalctl -u tsh-erp`
- Redis stats: `redis-cli info stats`

---

## 📚 Developer Guidelines

### For New Features

✅ **DO:**
1. Use BFF pattern for mobile features
2. Add to `app/bff/mobile/{app}/`
3. Create aggregator functions
4. Implement caching
5. Write tests (unit + integration)
6. Update this documentation

❌ **DON'T:**
1. Add new routers to legacy pattern
2. Create direct service calls from mobile
3. Skip caching for frequently accessed data
4. Return large payloads to mobile
5. Skip tests

### For Bug Fixes

**Legacy Code:**
- Fix in place
- Add tests
- Plan migration to BFF

**BFF Code:**
- Fix and add tests
- Update cache invalidation if needed

### Code Review Checklist

- [ ] Uses BFF pattern for mobile endpoints
- [ ] Implements caching where appropriate
- [ ] Includes unit tests (80% coverage)
- [ ] Includes integration tests
- [ ] Updates API documentation
- [ ] Follows naming conventions
- [ ] Handles errors properly
- [ ] Logs important events

---

## 🐛 Troubleshooting

### Common Issues

#### 1. CORS Errors
**Problem:** Mobile app can't connect
**Solution:** Add origin to `allowed_origins` in main.py

#### 2. Authentication Failed
**Problem:** 401 Unauthorized
**Solution:** Check token expiry, refresh if needed

#### 3. Slow API Response
**Problem:** Endpoint takes >1 second
**Solution:**
- Check if cached
- Review database queries
- Use BFF aggregation

#### 4. Database Connection Error
**Problem:** Can't connect to database
**Solution:**
- Check PostgreSQL is running
- Verify connection string
- Check connection pool

---

## 📞 Support & Resources

### Documentation
- **This File:** Architecture overview
- **BACKEND_SIMPLIFICATION_PLAN.md:** Full migration plan
- **QUICK_START_SIMPLIFICATION.md:** Quick start guide
- **API Docs:** https://erp.tsh.sale/docs

### Key Files
- `app/main.py` - Application entry point
- `app/core/config.py` - Configuration
- `app/bff/mobile/router.py` - Mobile BFF
- `app/routers/auth_enhanced.py` - Authentication

### Commands
```bash
# Local development
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
source .venv/bin/activate
uvicorn app.main:app --reload

# Run tests
pytest app/tests/ -v

# Deploy to production
ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && git pull && systemctl restart tsh-erp"
```

---

## 🔮 Future Roadmap

### Phase 1: Foundation (Weeks 1-2) ✅
- [x] Fix security issues
- [x] Document architecture
- [x] Setup testing

### Phase 2: Cleanup (Weeks 3-4) 🔄
- [ ] Consolidate routers (63→30)
- [ ] Split large files
- [ ] Remove duplicates

### Phase 3: BFF Completion (Weeks 5-8) ⏳
- [ ] Complete all 11 app BFFs
- [ ] Implement full caching
- [ ] Add transformers

### Phase 4: Testing (Weeks 9-10) ⏳
- [ ] 80% test coverage
- [ ] Integration tests
- [ ] E2E tests

### Phase 5: Optimization (Weeks 11-14) ⏳
- [ ] Performance tuning
- [ ] Query optimization
- [ ] Load testing

---

## 📄 Changelog

### Version 2.0 (November 5, 2025)
- ✅ Fixed CORS security configuration
- ✅ Removed commented code from main.py
- ✅ Created comprehensive architecture documentation
- ✅ Defined BFF migration strategy
- 🔄 Started router consolidation

### Version 1.0 (Initial)
- ✅ FastAPI backend
- ✅ PostgreSQL database
- ✅ 11 Flutter mobile apps
- ✅ JWT authentication
- ✅ Zoho integration

---

**Maintained by:** TSH ERP Development Team
**Last Review:** November 5, 2025
**Next Review:** December 5, 2025

---

🚀 **Building a world-class ERP system for TSH!**
