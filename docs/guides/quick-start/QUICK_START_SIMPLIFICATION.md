# 🚀 Quick Start: Backend Simplification

**Start Here →** This guide helps you begin simplifying the TSH ERP backend TODAY!

---

## ⚡ Immediate Actions (Today - 2 Hours)

### 1. Fix CORS Security Issue (15 minutes)

**File:** `app/main.py` line 80-85

**Current code:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ INSECURE!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Replace with:**
```python
# Secure CORS configuration
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://erp.tsh.sale",
    "https://admin.tsh.sale",
    "https://shop.tsh.sale",
    "capacitor://localhost",
    "http://localhost",
    "ionic://localhost",
]

if settings.ENVIRONMENT == "development":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

**Test:**
```bash
# Restart application
ssh root@167.71.39.50 "systemctl restart tsh-erp"

# Verify
curl -I https://erp.tsh.sale/health
```

---

### 2. Remove Commented Code (10 minutes)

**File:** `app/main.py` lines 42-56

Delete the commented table creation code.

---

### 3. Create Architecture Documentation (1 hour)

**File:** `ARCHITECTURE.md` (NEW)

```markdown
# TSH ERP Architecture

**Last Updated:** November 5, 2025
**Status:** Migration to BFF in Progress

---

## Current System Overview

TSH ERP is a FastAPI-based ERP system with:
- 230 Python files
- 538 API endpoints
- PostgreSQL database
- Redis caching
- 11 mobile Flutter apps

---

## Architecture Status: MIGRATION IN PROGRESS

### Active Patterns

#### 1. **BFF Pattern** (✅ TARGET - In Progress)
- **Location:** `app/bff/mobile/`
- **Status:** Partially implemented
- **Use For:** All new mobile features
- **Apps:** Consumer, Salesperson, POS, Admin, etc.

#### 2. **Legacy Pattern** (⚠️ DEPRECATED - Maintenance Only)
- **Location:** Most routers in `app/routers/`
- **Status:** Being phased out
- **Use For:** Bug fixes only, no new features

---

## Developer Guidelines

### For New Features
✅ **DO:**
- Add to BFF layer (`app/bff/mobile/`)
- Use repository pattern
- Write tests
- Use caching

❌ **DON'T:**
- Add to legacy routers
- Direct database access in routers
- Skip tests

### For Bug Fixes
- Fix in place for legacy code
- Plan migration to BFF for next sprint

---

## Authentication System

**Current System:** `app/routers/auth_enhanced.py`

Features:
- JWT tokens (access + refresh)
- MFA support
- Session management
- Role-based access control

**DEPRECATED Systems (DO NOT USE):**
- ❌ `app/routers/auth.py`
- ❌ `app/routers/auth_simple.py`

---

## Mobile Apps & Endpoints

| App | Endpoint | Status |
|-----|----------|--------|
| Consumer | `/api/mobile/consumer/` | ⏳ Planned |
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

## Directory Structure

```
app/
├── bff/              # Backend For Frontend (NEW)
│   └── mobile/       # Mobile BFF layer
├── routers/          # API endpoints (63 routers - needs cleanup)
├── services/         # Business logic (46 services)
├── models/           # Database models (34 files)
├── schemas/          # Pydantic schemas (23 files)
├── core/             # Configuration & dependencies
├── db/               # Database connections
└── utils/            # Utilities
```

---

## Questions?

Contact the architecture team or refer to:
- `BACKEND_SIMPLIFICATION_PLAN.md` - Full migration plan
- `QUICK_START_SIMPLIFICATION.md` - Quick start guide
```

**Save and commit:**
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
git add ARCHITECTURE.md
git commit -m "docs: Add architecture documentation for developer guidance"
git push origin main
```

---

### 4. Add Test Configuration (30 minutes)

**File:** `pytest.ini` (UPDATE)

```ini
[pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=50
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

**File:** `app/tests/conftest.py` (NEW)

```python
"""
Test Configuration
Fixtures and utilities for testing
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "test@tsh.sale",
        "password": "testpassword123",
        "name": "Test User",
        "role": "admin"
    }


@pytest.fixture
def authenticated_client(client, test_user_data):
    """Create authenticated test client"""
    # Register user
    client.post("/api/auth/register", json=test_user_data)

    # Login
    response = client.post("/api/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })

    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client
```

**Create first test:**

**File:** `app/tests/unit/test_health.py` (NEW)

```python
"""
Health Check Tests
"""
def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

**Run tests:**
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
pip install pytest pytest-cov pytest-asyncio
pytest app/tests/ -v
```

---

## 📋 Week 1 Tasks (Critical - Start Monday)

### Monday: Authentication Consolidation

**Task:** Start consolidating 5 auth routers into 2

1. **Create new directory:**
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
mkdir -p app/routers/auth
touch app/routers/auth/{__init__.py,authentication.py,admin.py,schemas.py}
```

2. **Copy best code from auth_enhanced.py to authentication.py**

3. **Copy security_admin.py to admin.py**

4. **Update main.py imports**

5. **Test thoroughly**

6. **Deploy to staging**

### Tuesday-Wednesday: Settings Router Split

**Task:** Split 1,764-line settings.py into modules

1. **Create settings module:**
```bash
mkdir -p app/routers/settings
cd app/routers/settings
touch __init__.py general.py security.py notifications.py integrations.py
touch tax.py payment.py inventory.py accounting.py hr.py permissions.py schemas.py
```

2. **Extract code from settings.py:**
   - General settings → general.py
   - Security settings → security.py
   - etc.

3. **Create module registration in __init__.py**

4. **Test each endpoint**

5. **Deploy incrementally**

### Thursday: Remove Duplicates

**Task:** Remove "simple" router duplicates

1. **Merge partner_salesmen_simple.py into partner_salesmen.py**
   - Add `simple_mode` query parameter
   - Keep both response formats

2. **Merge multi_price_system_simple.py into multi_price_system.py**
   - Same strategy

3. **Delete simple files**

4. **Update main.py**

5. **Test both modes**

### Friday: Clean main.py

**Task:** Reorganize main.py using router registry

1. **Create** `app/core/router_registry.py`

2. **Move router registrations** from main.py to registry

3. **Simplify main.py** to ~80 lines

4. **Test application startup**

5. **Deploy and verify**

---

## 🎯 Week 2 Tasks (High Priority)

### Monday-Tuesday: BFF Base Infrastructure

1. Create `app/bff/base.py` with BaseBFF class
2. Create `app/bff/cache.py` with caching strategies
3. Create `app/bff/transformers/` directory
4. Implement image transformer
5. Implement response transformer

### Wednesday-Thursday: Consumer BFF

1. Create `app/bff/consumer.py`
2. Implement home screen aggregation
3. Implement product detail aggregation
4. Create consumer router
5. Test with Consumer app

### Friday: Salesperson BFF

1. Create `app/bff/salesperson.py`
2. Implement salesperson home
3. Implement customer profile aggregation
4. Create salesperson router
5. Test with Salesperson app

---

## 📊 Progress Tracking

Use this checklist to track progress:

### Phase 1: Foundation ✅
- [ ] Fix CORS configuration
- [ ] Remove commented code
- [ ] Create ARCHITECTURE.md
- [ ] Add test configuration
- [ ] Consolidate authentication (5→2 routers)
- [ ] Add basic tests

### Phase 2: Router Cleanup 🔄
- [ ] Split settings router (1→10 files)
- [ ] Remove duplicate routers
- [ ] Consolidate POS/Sales routers
- [ ] Clean up main.py
- [ ] Create router registry

### Phase 3: BFF Completion ⏳
- [ ] Complete BFF infrastructure
- [ ] Implement Consumer BFF
- [ ] Implement Salesperson BFF
- [ ] Implement POS BFF
- [ ] Add caching layer
- [ ] Image optimization
- [ ] Response transformers

### Phase 4: Service Cleanup ⏳
- [ ] Consolidate security services (8→3)
- [ ] Split large models
- [ ] Reorganize service layer

### Phase 5: Testing & Docs ⏳
- [ ] Unit tests (80% coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] API documentation

### Phase 6: Optimization ⏳
- [ ] Query optimization
- [ ] Caching strategy
- [ ] Background jobs
- [ ] Performance monitoring

---

## 🚨 Important Notes

### DO NOT Break Production

- Always test locally first
- Deploy to staging before production
- Keep rollback plan ready
- Monitor logs after deployment

### Backward Compatibility

- Keep old endpoints working during migration
- Add deprecation warnings
- Give mobile apps time to migrate
- Remove old code only after all apps updated

### Communication

- Update mobile app developers about changes
- Document all breaking changes
- Provide migration guides
- Schedule maintenance windows if needed

---

## 📞 Need Help?

**Resources:**
- Full plan: `BACKEND_SIMPLIFICATION_PLAN.md`
- Architecture: `ARCHITECTURE.md`
- Analysis report: (in session output)

**Questions?**
- Check documentation first
- Review analysis report for context
- Refer to implementation examples in plan

---

**Created:** November 5, 2025
**Ready to Start:** ✅ YES
**Estimated Time:** 14 weeks (phased approach)
**Priority:** Start with Week 1 tasks immediately

---

🚀 **Let's simplify and optimize the TSH ERP backend!**
