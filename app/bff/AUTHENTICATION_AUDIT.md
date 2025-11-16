# BFF Authentication & Authorization Audit Report

**Date:** 2025-11-15
**Version:** 1.0.0
**Auditor:** BFF Agent
**Scope:** All BFF (Backend-for-Frontend) endpoints across 8+ mobile apps

---

## Executive Summary

**STATUS: CRITICAL SECURITY VIOLATIONS DETECTED**

All 100+ BFF endpoints across 8 mobile applications are **completely unprotected**. Every endpoint:
- ❌ NO authentication implemented
- ❌ NO authorization checks (RBAC)
- ❌ NO data scoping (RLS)
- ❌ NO permission validation (ABAC)

**Risk Level:** 🔴 CRITICAL - Any anonymous user can access ALL data from ALL mobile apps.

---

## TSH Authorization Framework Overview

TSH ERP implements a **HYBRID AUTHORIZATION** system with THREE mandatory layers:

### Layer 1: RBAC (Role-Based Access Control)
- **Purpose:** Control access based on user roles (admin, manager, salesperson, etc.)
- **Implementation:** `RoleChecker` or `PermissionChecker` dependencies
- **Location:** `app/dependencies/rbac.py`

### Layer 2: ABAC (Attribute-Based Access Control)
- **Purpose:** Fine-grained permission checks based on user attributes
- **Implementation:** JWT token validation with embedded permissions
- **Location:** `app/dependencies/auth.py`

### Layer 3: RLS (Row-Level Security)
- **Purpose:** Database-level data scoping (users only see their own data)
- **Implementation:** PostgreSQL session variables + RLS policies
- **Location:** `app/db/rls_dependency.py`, `app/db/rls_context.py`

---

## Current State Analysis

### Files Audited

| File | Lines | Endpoints | Auth Status | Priority |
|------|-------|-----------|-------------|----------|
| `app/bff/routers/security.py` | 587 | 21 | ❌ None | 🔴 Critical |
| `app/bff/routers/hr.py` | 795 | 24 | ❌ None | 🔴 Critical |
| `app/bff/routers/pos.py` | 674 | 18 | 🔴 Critical | 🔴 Critical |
| `app/bff/routers/inventory.py` | 705 | 25 | ❌ None | 🔴 Critical |
| `app/bff/routers/accounting.py` | 860 | 28 | ❌ None | 🔴 Critical |
| `app/bff/routers/aso.py` | 846 | 22 | ❌ None | 🔴 Critical |
| **TOTAL** | **4,467** | **138** | **0** | **🔴 CRITICAL** |

### Common Pattern (WRONG)

Every endpoint follows this insecure pattern:

```python
# ❌ WRONG: No authentication, no authorization, no RLS
@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db)  # ❌ No user context!
):
    """Get dashboard"""
    # TODO: Implement dashboard
    return {"success": True, "data": {...}}
```

**Problems:**
1. No `get_current_user` dependency → anyone can call this
2. No `RoleChecker` → no role validation
3. No `get_db_with_rls` → sees ALL data (not just user's data)
4. Not implemented (TODO placeholder)

---

## Required Implementation Pattern

### Pattern 1: Standard Protected Endpoint (RECOMMENDED)

```python
# ✅ CORRECT: All 3 authorization layers present
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import RoleChecker
from app.db.rls_dependency import get_db_with_rls
from app.models.user import User

@router.get(
    "/dashboard",
    dependencies=[Depends(RoleChecker(["admin", "manager", "salesperson"]))]
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),  # ABAC Layer
    db: AsyncSession = Depends(get_db_with_rls)      # RLS Layer
):
    """
    Get dashboard data

    Security:
    - RBAC: Requires admin, manager, or salesperson role
    - ABAC: Requires valid JWT token
    - RLS: Database queries scoped to user's data
    """
    # All queries automatically scoped by RLS
    # current_user contains authenticated user info
    return {"success": True, "data": {...}}
```

### Pattern 2: Public Endpoint (No Auth Required)

```python
# ✅ CORRECT: Truly public endpoint (health check, etc.)
@router.get("/health")
async def health_check():
    """Health check endpoint - no auth required"""
    return {"status": "healthy", "service": "pos-bff", "version": "1.0.0"}
```

### Pattern 3: Admin-Only Endpoint

```python
# ✅ CORRECT: Admin-only access
@router.post(
    "/sessions/{session_id}/terminate",
    dependencies=[Depends(RoleChecker(["admin"]))]
)
async def terminate_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_with_rls)
):
    """Terminate user session (admin only)"""
    # Only admins can access this endpoint
    # RLS still applies (admin can see all data)
    return {"success": True}
```

### Pattern 4: Permission-Based Endpoint

```python
# ✅ CORRECT: Specific permission check
from app.dependencies.rbac import PermissionChecker

@router.post(
    "/transactions/{transaction_id}/refund",
    dependencies=[Depends(PermissionChecker(["pos.refund", "accounting.write"]))]
)
async def process_refund(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_with_rls)
):
    """Process refund (requires specific permissions)"""
    return {"success": True}
```

---

## Endpoint-by-Endpoint Analysis

### Security BFF (`app/bff/routers/security.py`)

**Risk Level:** 🔴 CRITICAL (Security monitoring endpoints are unprotected!)

| Endpoint | Current Auth | Required Auth | Data Sensitivity |
|----------|--------------|---------------|------------------|
| `GET /dashboard` | ❌ None | Admin only | 🔴 Critical |
| `GET /threats` | ❌ None | Admin/Security | 🔴 Critical |
| `POST /threats/{id}/resolve` | ❌ None | Admin only | 🔴 Critical |
| `GET /login-attempts` | ❌ None | Admin only | 🔴 Critical |
| `POST /ip-addresses/{ip}/block` | ❌ None | Admin only | 🔴 Critical |
| `GET /sessions` | ❌ None | Admin/Security | 🔴 Critical |
| `POST /sessions/{id}/terminate` | ❌ None | Admin only | 🔴 Critical |
| `GET /audit-log` | ❌ None | Admin only | 🔴 Critical |
| `GET /permissions/matrix` | ❌ None | Admin only | 🔴 Critical |
| `GET /violations` | ❌ None | Admin/Security | 🔴 Critical |

**Recommendation:** ALL endpoints require `RoleChecker(["admin"])` - these are administrative security functions.

---

### POS BFF (`app/bff/routers/pos.py`)

**Risk Level:** 🔴 CRITICAL (Financial transactions unprotected!)

| Endpoint | Current Auth | Required Auth | Data Sensitivity |
|----------|--------------|---------------|------------------|
| `GET /dashboard` | ❌ None | Cashier+ | 🟡 Medium |
| `POST /transaction/start` | ❌ None | Cashier+ | 🔴 Critical |
| `POST /transaction/{id}/add-item` | ❌ None | Cashier+ | 🔴 Critical |
| `POST /transaction/{id}/payment` | ❌ None | Cashier+ | 🔴 Critical |
| `POST /transaction/{id}/split-payment` | ❌ None | Cashier+ | 🔴 Critical |
| `GET /cash-drawer` | ❌ None | Cashier+ | 🔴 Critical |
| `POST /cash-drawer/open` | ❌ None | Cashier/Manager | 🔴 Critical |
| `POST /cash-drawer/close` | ❌ None | Cashier/Manager | 🔴 Critical |
| `POST /return/process` | ❌ None | Manager only | 🔴 Critical |

**Recommendation:**
- Dashboard/transactions: `RoleChecker(["cashier", "manager", "admin"])`
- Cash drawer open/close: `RoleChecker(["cashier", "manager"])`
- Refunds: `RoleChecker(["manager", "admin"])` (manager approval required)

---

### Inventory BFF (`app/bff/routers/inventory.py`)

**Risk Level:** 🔴 CRITICAL (Inventory data exposed!)

| Endpoint | Current Auth | Required Auth | Data Sensitivity |
|----------|--------------|---------------|------------------|
| `GET /dashboard` | ❌ None | Inventory+ | 🟡 Medium |
| `GET /stock-levels` | ❌ None | Inventory+ | 🟡 Medium |
| `POST /movements/record` | ❌ None | Inventory/Manager | 🔴 Critical |
| `POST /transfers/create` | ❌ None | Inventory/Manager | 🔴 Critical |
| `POST /transfers/{id}/send` | ❌ None | Inventory+ | 🔴 Critical |
| `POST /transfers/{id}/receive` | ❌ None | Inventory+ | 🔴 Critical |
| `POST /count-sessions/start` | ❌ None | Inventory/Manager | 🔴 Critical |
| `POST /adjustments/create` | ❌ None | Manager only | 🔴 Critical |

**Recommendation:**
- Read operations: `RoleChecker(["inventory", "manager", "admin"])`
- Write operations: `RoleChecker(["inventory", "manager", "admin"])`
- Adjustments: `RoleChecker(["manager", "admin"])` (requires approval)

---

### HR BFF (`app/bff/routers/hr.py`)

**Risk Level:** 🔴 CRITICAL (Sensitive employee data!)

| Endpoint | Current Auth | Required Auth | Data Sensitivity |
|----------|--------------|---------------|------------------|
| `GET /dashboard` | ❌ None | HR/Manager | 🟡 Medium |
| `GET /employees` | ❌ None | HR/Manager | 🔴 Critical |
| `POST /employees/create` | ❌ None | HR/Admin | 🔴 Critical |
| `GET /attendance` | ❌ None | HR/Manager | 🔴 Critical |
| `POST /attendance/check-in` | ❌ None | Employee | 🟡 Medium |
| `POST /leave/request` | ❌ None | Employee | 🟡 Medium |
| `POST /leave/{id}/approve` | ❌ None | Manager only | 🔴 Critical |
| `GET /payroll` | ❌ None | HR/Admin | 🔴 Critical |

**Recommendation:**
- Dashboard/read: `RoleChecker(["hr", "manager", "admin"])`
- Create/update employees: `RoleChecker(["hr", "admin"])`
- Approve leave: `RoleChecker(["manager", "admin"])`
- Payroll: `RoleChecker(["hr", "admin"])`
- Self-service (attendance, leave request): `get_current_user` (any authenticated user)

---

### Accounting BFF (`app/bff/routers/accounting.py`)

**Risk Level:** 🔴 CRITICAL (Financial data exposed!)

| Endpoint | Current Auth | Required Auth | Data Sensitivity |
|----------|--------------|---------------|------------------|
| `GET /dashboard` | ❌ None | Accountant+ | 🟡 Medium |
| `GET /chart-of-accounts` | ❌ None | Accountant+ | 🟡 Medium |
| `POST /journal-entries/create` | ❌ None | Accountant/Admin | 🔴 Critical |
| `GET /balance-sheet` | ❌ None | Accountant+ | 🔴 Critical |
| `GET /profit-loss` | ❌ None | Accountant+ | 🔴 Critical |
| `GET /cash-flow` | ❌ None | Accountant+ | 🔴 Critical |
| `POST /reconcile` | ❌ None | Accountant only | 🔴 Critical |

**Recommendation:**
- All endpoints: `RoleChecker(["accountant", "manager", "admin"])`
- Write operations: Add audit logging

---

### ASO BFF (`app/bff/routers/aso.py`)

**Risk Level:** 🟡 HIGH (Customer service data)

| Endpoint | Current Auth | Required Auth | Data Sensitivity |
|----------|--------------|---------------|------------------|
| `GET /dashboard` | ❌ None | ASO/Manager | 🟡 Medium |
| `GET /service-requests` | ❌ None | ASO+ | 🟡 Medium |
| `POST /service-requests/create` | ❌ None | ASO/Customer | 🟡 Medium |
| `POST /returns/process` | ❌ None | Manager only | 🔴 Critical |
| `POST /warranty/validate` | ❌ None | ASO+ | 🟡 Medium |

**Recommendation:**
- Dashboard/read: `RoleChecker(["aso", "manager", "admin"])`
- Write operations: `RoleChecker(["aso", "manager", "admin"])`
- Returns/refunds: `RoleChecker(["manager", "admin"])`

---

## Available Dependencies

### From `app/dependencies/auth.py`
```python
from app.dependencies.auth import (
    get_current_user,           # Get authenticated user (ABAC)
    get_current_user_async,     # Async version
    get_user_permissions,       # Get user's permission list
    security                     # HTTPBearer security scheme
)
```

### From `app/dependencies/rbac.py`
```python
from app.dependencies.rbac import (
    RoleChecker,                # Check user role(s)
    PermissionChecker,          # Check specific permissions
    get_current_user_from_token # Basic token validation
)
```

### From `app/db/rls_dependency.py`
```python
from app.db.rls_dependency import (
    get_db_with_rls,            # DB session with RLS context
    get_current_user_with_rls,  # User + RLS context
    get_db                       # Basic DB session (no RLS)
)
```

---

## Implementation Priority

### Phase 1: CRITICAL (Immediate - This Week)
1. **Security BFF** - Admin functions are completely exposed
2. **POS BFF** - Financial transactions unprotected
3. **Accounting BFF** - Financial data exposed
4. **HR BFF** - Sensitive employee data

### Phase 2: HIGH (Next Week)
5. **Inventory BFF** - Stock management needs protection
6. **ASO BFF** - Customer service data

### Phase 3: MEDIUM (Following Week)
7. Remaining BFF routers (Salesperson, Wholesale, Partner, Admin, TDS)

---

## Migration Strategy

### Step 1: Add Required Imports
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import RoleChecker
from app.db.rls_dependency import get_db_with_rls
from app.models.user import User
```

### Step 2: Update Each Endpoint Signature
Before:
```python
@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    # ...
```

After:
```python
@router.get(
    "/dashboard",
    dependencies=[Depends(RoleChecker(["cashier", "manager", "admin"]))]
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_with_rls)
):
    # ...
```

### Step 3: Use `current_user` in Logic
```python
# Access user info
user_id = current_user.id
user_email = current_user.email
user_role = current_user.role.name
user_branch = current_user.branch_id

# Log user actions
logger.info(f"User {user_email} accessed dashboard")

# RLS automatically filters queries
orders = await db.execute(select(Order))  # Only sees own orders
```

---

## Testing Checklist

For each updated endpoint:

- [ ] Endpoint rejects unauthenticated requests (401)
- [ ] Endpoint rejects users with wrong role (403)
- [ ] Endpoint returns user-scoped data only (RLS verification)
- [ ] Authenticated user can access with correct role (200)
- [ ] `current_user` object is available in endpoint
- [ ] Database queries are properly scoped

---

## Role Mapping

| Role | Permissions | Typical Users |
|------|-------------|---------------|
| `admin` | ALL | System administrators |
| `manager` | Management, reports, approvals | Branch managers |
| `salesperson` | Sales, customers, products | Travel sales, partner salesmen |
| `cashier` | POS, retail sales | Retail store cashiers |
| `inventory` | Stock, warehouses, transfers | Warehouse staff |
| `accountant` | Financial reports, reconciliation | Accounting team |
| `hr` | Employee management, payroll | HR team |
| `aso` | After-sales service, returns | Customer service team |
| `viewer` | Dashboard, reports (read-only) | Observers |

---

## Security Recommendations

### Immediate Actions Required
1. ✅ Add authentication to ALL BFF endpoints (except health checks)
2. ✅ Implement role-based access control on sensitive operations
3. ✅ Use `get_db_with_rls` for all database access
4. ✅ Add audit logging for write operations
5. ✅ Test each endpoint with different user roles

### Long-Term Improvements
1. Implement rate limiting (prevent brute force)
2. Add request validation (prevent injection attacks)
3. Implement API versioning
4. Add comprehensive error handling
5. Create automated security tests

---

## Conclusion

**Current Status:** 🔴 CRITICAL SECURITY RISK

All BFF endpoints are completely unprotected, exposing:
- Financial data (transactions, cash drawer, accounting)
- Employee data (HR, payroll, attendance)
- Security data (login attempts, sessions, audit logs)
- Inventory data (stock levels, transfers)
- Customer data (orders, returns, service requests)

**Immediate Action Required:** Implement authentication on all 138 BFF endpoints before production deployment.

**Estimated Implementation Time:**
- Phase 1 (Critical): 2-3 days
- Phase 2 (High): 1-2 days
- Phase 3 (Medium): 1-2 days
- Testing: 1-2 days
- **Total:** 5-9 days

---

**Audit Report Generated:** 2025-11-15
**Next Review:** After implementation completion
**Reviewed By:** BFF Agent
