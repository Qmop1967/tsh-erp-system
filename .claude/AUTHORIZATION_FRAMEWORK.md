# TSH ERP Authorization Framework
**Hybrid ABAC + RBAC + RLS Security Model**

**Last Updated:** 2025-11-13
**Status:** IMMUTABLE - This framework is non-negotiable
**Version:** 1.0.0

---

## 🎯 Executive Summary

TSH ERP implements a **3-layer hybrid authorization framework** combining:
1. **RBAC** (Role-Based Access Control) - Broad permission sets
2. **ABAC** (Attribute-Based Access Control) - Fine-grained contextual policies
3. **RLS** (Row-Level Security) - Database-level data isolation

**Every endpoint, service, and database query MUST implement all three layers.**

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     INCOMING REQUEST                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 0: Authentication (JWT Token Validation)             │
│  ✓ Valid token? → Continue                                  │
│  ✗ Invalid token? → 401 Unauthorized                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: RBAC (Role-Based Access Control)                  │
│  Question: "Can this ROLE perform this ACTION?"             │
│  ✓ Role has permission? → Continue                          │
│  ✗ Role lacks permission? → 403 Forbidden                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: ABAC (Attribute-Based Access Control)             │
│  Question: "Do user ATTRIBUTES satisfy POLICY?"             │
│  Checks: Time, Location, Department, Clearance              │
│  ✓ Attributes satisfy policy? → Continue                    │
│  ✗ Policy violation? → 403 Forbidden                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: RLS (Row-Level Security)                          │
│  Question: "Which specific ROWS can user see?"              │
│  Applies SQL filters based on user context                  │
│  • Wholesale clients: Own orders only                       │
│  • Travel sales: Assigned customers only                    │
│  • Inventory managers: Own warehouse only                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              AUTHORIZED DATA RETURNED                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Layer 1: RBAC (Role-Based Access Control)

### Purpose
Define **broad permission sets** based on user roles in the organization.

### User Roles Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                          OWNER                               │
│                  (Full System Access)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
┌────────▼────────┐                 ┌────────▼────────┐
│     ADMIN       │                 │  HR_MANAGER     │
│  (Operational)  │                 │  (HR Module)    │
└────────┬────────┘                 └─────────────────┘
         │
    ┌────┴────┬─────────────┬──────────────┐
    │         │             │              │
┌───▼───┐ ┌──▼──┐  ┌───────▼─────┐  ┌────▼────┐
│RETAIL │ │INVEN│  │TRAVEL_SALES │  │WHOLESALE│
│STAFF  │ │TORY │  │             │  │CLIENT   │
└───────┘ │MGR  │  └─────────────┘  └─────────┘
          └─────┘
```

### Role Definitions

| Role | Code | Permissions | Use Cases |
|------|------|-------------|-----------|
| **Owner** | `OWNER` | Full system access, all operations | Business owner, CEO |
| **Admin** | `ADMIN` | Full operational access, cannot modify system settings | Operations manager |
| **HR Manager** | `HR_MANAGER` | HR module (payroll, attendance, performance) | HR department |
| **Retail Staff** | `RETAIL_STAFF` | POS operations, customer service | Retail shop employees |
| **Inventory Manager** | `INVENTORY_MANAGER` | Inventory control for assigned warehouse | Warehouse supervisor |
| **Travel Salesperson** | `TRAVEL_SALES` | Assigned customers, order entry, GPS tracking | Field sales |
| **Wholesale Client** | `WHOLESALE_CLIENT` | View own orders, invoices, place orders | B2B customers |
| **Consumer** | `CONSUMER` | Browse products, place orders, view own history | B2C customers |
| **Partner Salesman** | `PARTNER_SALESMAN` | View assigned products, track commissions | Affiliate sellers |

### Implementation

```python
from enum import Enum
from fastapi import Depends, HTTPException, status

class UserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    RETAIL_STAFF = "retail_staff"
    INVENTORY_MANAGER = "inventory_manager"
    TRAVEL_SALES = "travel_sales"
    WHOLESALE_CLIENT = "wholesale_client"
    CONSUMER = "consumer"
    PARTNER_SALESMAN = "partner_salesman"

# Permission matrix
ROLE_PERMISSIONS = {
    UserRole.OWNER: ["*"],  # All permissions
    UserRole.ADMIN: [
        "read:all", "write:all", "delete:orders", "approve:invoices"
    ],
    UserRole.HR_MANAGER: [
        "read:employees", "write:payroll", "read:attendance"
    ],
    UserRole.RETAIL_STAFF: [
        "read:products", "write:sales", "read:customers"
    ],
    UserRole.INVENTORY_MANAGER: [
        "read:inventory", "write:stock", "read:warehouse"
    ],
    UserRole.TRAVEL_SALES: [
        "read:assigned_customers", "write:orders", "read:products"
    ],
    UserRole.WHOLESALE_CLIENT: [
        "read:own_orders", "write:own_orders", "read:invoices"
    ],
    UserRole.CONSUMER: [
        "read:products", "write:own_orders"
    ],
    UserRole.PARTNER_SALESMAN: [
        "read:products", "read:own_sales", "read:commissions"
    ],
}

def require_role(allowed_roles: list[UserRole]):
    """
    RBAC decorator - requires user to have one of the allowed roles.

    Usage:
        @router.get("/financials")
        async def get_financials(
            user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
        ):
            return data
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} not authorized for this action"
            )
        return current_user
    return role_checker
```

### RBAC Examples

```python
# Example 1: Only OWNER and ADMIN can access financial reports
@router.get("/api/v1/financial-reports")
async def get_financial_reports(
    user: User = Depends(require_role([UserRole.OWNER, UserRole.ADMIN]))
):
    return await financial_service.get_reports()

# Example 2: Multiple roles can view inventory
@router.get("/api/v1/inventory")
async def get_inventory(
    user: User = Depends(require_role([
        UserRole.OWNER,
        UserRole.ADMIN,
        UserRole.INVENTORY_MANAGER,
        UserRole.RETAIL_STAFF
    ]))
):
    return await inventory_service.get_all()

# Example 3: HR-only endpoint
@router.post("/api/v1/payroll/process")
async def process_payroll(
    user: User = Depends(require_role([UserRole.OWNER, UserRole.HR_MANAGER]))
):
    return await hr_service.process_payroll()
```

---

## 🎯 Layer 2: ABAC (Attribute-Based Access Control)

### Purpose
Enforce **fine-grained access policies** based on:
- User attributes (department, location, clearance level)
- Resource attributes (sensitivity, ownership, department)
- Context attributes (time, IP address, device)

### Attribute Categories

#### User Attributes
- `role`: User's organizational role
- `department`: Department assignment (sales, inventory, HR)
- `location`: Physical location / warehouse ID
- `clearance_level`: Security clearance (0-10)
- `shift`: Work shift (morning, evening, night)
- `assigned_warehouse_id`: For inventory managers
- `assigned_region`: For travel salespersons

#### Resource Attributes
- `owner_id`: Resource owner
- `department`: Resource department
- `sensitivity_level`: Data classification (public, internal, confidential)
- `warehouse_id`: For inventory resources
- `customer_id`: For customer-specific data

#### Context Attributes
- `timestamp`: Current time
- `day_of_week`: Current day
- `ip_address`: Request IP
- `device_type`: Mobile, desktop, tablet
- `geo_location`: GPS coordinates (for travel sales)

### ABAC Policy Engine

```python
from typing import Dict, Any
from datetime import datetime, time

class AttributePolicy:
    """ABAC policy engine for fine-grained access control."""

    @staticmethod
    async def check_access(
        user: User,
        resource: str,
        action: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Evaluate access based on attributes.

        Returns True if access granted, False otherwise.
        """
        context = context or {}

        # Policy 1: Time-based access
        if not await AttributePolicy._check_time_policy(user, action, context):
            return False

        # Policy 2: Location-based access
        if not await AttributePolicy._check_location_policy(user, resource, context):
            return False

        # Policy 3: Department-based access
        if not await AttributePolicy._check_department_policy(user, resource, context):
            return False

        # Policy 4: Clearance level
        if not await AttributePolicy._check_clearance_policy(user, context):
            return False

        return True

    @staticmethod
    async def _check_time_policy(user: User, action: str, context: Dict) -> bool:
        """Time-based access policy."""
        current_time = datetime.now().time()

        # Retail staff can only work during business hours (8 AM - 8 PM)
        if user.role == UserRole.RETAIL_STAFF:
            work_start = time(8, 0)
            work_end = time(20, 0)
            if not (work_start <= current_time <= work_end):
                return False

        # Financial operations only during business days
        if action in ["write:payroll", "approve:invoices"]:
            if datetime.now().weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False

        return True

    @staticmethod
    async def _check_location_policy(user: User, resource: str, context: Dict) -> bool:
        """Location-based access policy."""

        # Inventory managers can only access their assigned warehouse
        if user.role == UserRole.INVENTORY_MANAGER:
            if resource == "inventory":
                resource_warehouse = context.get("warehouse_id")
                if resource_warehouse and resource_warehouse != user.warehouse_id:
                    return False

        # Travel salespersons must be in assigned region
        if user.role == UserRole.TRAVEL_SALES:
            if context.get("requires_region_check"):
                customer_region = context.get("customer_region")
                if customer_region != user.assigned_region:
                    return False

        return True

    @staticmethod
    async def _check_department_policy(user: User, resource: str, context: Dict) -> bool:
        """Department-based access policy."""
        resource_dept = context.get("resource_department")

        if resource_dept and hasattr(user, 'department'):
            # Cross-department access requires higher clearance
            if user.department != resource_dept:
                if user.clearance_level < 5:
                    return False

        return True

    @staticmethod
    async def _check_clearance_policy(user: User, context: Dict) -> bool:
        """Clearance level policy."""
        required_clearance = context.get("required_clearance", 0)
        user_clearance = getattr(user, 'clearance_level', 0)

        return user_clearance >= required_clearance
```

### ABAC Integration

```python
def check_abac_permission(
    resource: str,
    action: str,
    context: Dict[str, Any] = None
):
    """ABAC permission dependency for FastAPI routes."""
    async def abac_checker(current_user: User = Depends(get_current_user)):
        has_access = await AttributePolicy.check_access(
            user=current_user,
            resource=resource,
            action=action,
            context=context or {}
        )

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: attribute-based policy violation"
            )

        return current_user

    return abac_checker
```

### ABAC Examples

```python
# Example 1: Time-restricted inventory update
@router.put("/api/v1/inventory/{item_id}")
async def update_inventory(
    item_id: int,
    quantity: int,
    warehouse_id: int,
    user: User = Depends(require_role([UserRole.INVENTORY_MANAGER])),  # RBAC
    abac: User = Depends(check_abac_permission(  # ABAC
        resource="inventory",
        action="modify_inventory",
        context={"warehouse_id": warehouse_id}
    ))
):
    # Only inventory manager of THIS warehouse, during business hours
    return await inventory_service.update(item_id, quantity)

# Example 2: Department-restricted financial data
@router.get("/api/v1/expenses")
async def get_expenses(
    department: str,
    user: User = Depends(require_role([UserRole.ADMIN, UserRole.HR_MANAGER])),
    abac: User = Depends(check_abac_permission(
        resource="expenses",
        action="read",
        context={"resource_department": department}
    ))
):
    # Can only view expenses from own department (unless high clearance)
    return await finance_service.get_expenses(department)

# Example 3: High-sensitivity data
@router.get("/api/v1/salary-details/{employee_id}")
async def get_salary(
    employee_id: int,
    user: User = Depends(require_role([UserRole.OWNER, UserRole.HR_MANAGER])),
    abac: User = Depends(check_abac_permission(
        resource="salary",
        action="read",
        context={"required_clearance": 7, "sensitivity_level": "confidential"}
    ))
):
    # Requires clearance level 7+, HR role, during business hours
    return await hr_service.get_salary_details(employee_id)
```

---

## 🔐 Layer 3: RLS (Row-Level Security)

### Purpose
Ensure users **only see data they're authorized to access** at the database level.

### RLS Policies by Role

| Role | Orders | Customers | Inventory | Invoices |
|------|--------|-----------|-----------|----------|
| **OWNER** | All | All | All | All |
| **ADMIN** | All | All | All | All |
| **WHOLESALE_CLIENT** | Own only | Self only | None | Own only |
| **TRAVEL_SALES** | Assigned customers | Assigned only | View only | Assigned customers |
| **INVENTORY_MANAGER** | View all | View all | Own warehouse | View all |
| **RETAIL_STAFF** | View all | View all | View all | None |
| **PARTNER_SALESMAN** | Own referrals | Referred only | None | Own commissions |

### Application-Level RLS

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

class RLSPolicy:
    """Row-Level Security implementation."""

    @staticmethod
    def apply_rls_filter(query, model, user: User):
        """Apply RLS filters to SQLAlchemy queries."""

        table_name = model.__tablename__

        # Wholesale clients: only their data
        if user.role == UserRole.WHOLESALE_CLIENT:
            if table_name == "orders":
                query = query.filter(model.customer_id == user.customer_id)
            elif table_name == "invoices":
                query = query.filter(model.customer_id == user.customer_id)
            elif table_name == "customers":
                query = query.filter(model.id == user.customer_id)

        # Travel salespersons: assigned customers only
        elif user.role == UserRole.TRAVEL_SALES:
            if table_name == "customers":
                query = query.filter(model.assigned_salesperson_id == user.id)
            elif table_name == "orders":
                # Orders from assigned customers only
                query = query.filter(
                    model.customer_id.in_(
                        select([Customer.id]).where(
                            Customer.assigned_salesperson_id == user.id
                        )
                    )
                )

        # Inventory managers: own warehouse only
        elif user.role == UserRole.INVENTORY_MANAGER:
            if table_name == "inventory":
                query = query.filter(model.warehouse_id == user.warehouse_id)
            elif table_name == "stock_adjustments":
                query = query.filter(model.warehouse_id == user.warehouse_id)

        # Partner salesmen: own sales only
        elif user.role == UserRole.PARTNER_SALESMAN:
            if table_name == "sales":
                query = query.filter(model.salesman_id == user.id)
            elif table_name == "commissions":
                query = query.filter(model.salesman_id == user.id)

        # OWNER and ADMIN: no restrictions
        elif user.role in [UserRole.OWNER, UserRole.ADMIN]:
            pass  # See everything

        return query
```

### BaseService with RLS

```python
class BaseService:
    """Base service class with automatic RLS filtering."""

    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user

    def query(self, model):
        """Create query with RLS filters automatically applied."""
        query = self.db.query(model)
        return RLSPolicy.apply_rls_filter(query, model, self.current_user)

    async def get_all(self, model, skip: int = 0, limit: int = 100):
        """Get all records (filtered by RLS)."""
        query = self.query(model).offset(skip).limit(limit)
        return query.all()

    async def get_by_id(self, model, id: int):
        """Get record by ID (filtered by RLS)."""
        result = self.query(model).filter(model.id == id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Not found")
        return result
```

### Database-Level RLS (PostgreSQL)

```sql
-- Enable RLS on tables
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;

-- Policy: Wholesale clients see only their orders
CREATE POLICY wholesale_client_orders ON orders
    FOR SELECT
    TO wholesale_client_role
    USING (customer_id = current_setting('app.current_user_customer_id')::integer);

-- Policy: Travel salespersons see assigned customers
CREATE POLICY travel_sales_customers ON customers
    FOR SELECT
    TO travel_sales_role
    USING (assigned_salesperson_id = current_setting('app.current_user_id')::integer);

-- Policy: Inventory managers see only their warehouse
CREATE POLICY inventory_manager_warehouse ON inventory
    FOR ALL
    TO inventory_manager_role
    USING (warehouse_id = current_setting('app.current_user_warehouse_id')::integer);

-- Policy: Admins and owners bypass RLS
CREATE POLICY admin_bypass ON orders
    FOR ALL
    TO admin_role, owner_role
    USING (true);
```

### RLS Examples

```python
# Example 1: OrderService with automatic RLS
class OrderService(BaseService):
    async def get_orders(self, skip: int = 0, limit: int = 100):
        """
        Get orders with RLS filtering:
        - Wholesale client: only their orders
        - Travel sales: orders from assigned customers
        - Admin/Owner: all orders
        """
        return await self.get_all(Order, skip, limit)

# Example 2: Explicit RLS check
@router.get("/api/v1/orders/{order_id}")
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)

    # This will return 404 if user doesn't have access
    # (RLS filtered it out)
    order = await service.get_by_id(Order, order_id)
    return order
```

---

## ✅ Implementation Checklist

When creating ANY new endpoint, ensure:

### Layer 0: Authentication
- [ ] JWT token validation via `Depends(get_current_user)`
- [ ] Token includes user ID, role, and attributes

### Layer 1: RBAC
- [ ] `require_role()` dependency with appropriate roles
- [ ] Permission matrix consulted for role capabilities
- [ ] Error returns 403 with clear message

### Layer 2: ABAC
- [ ] `check_abac_permission()` dependency with context
- [ ] All relevant attributes considered (time, location, department)
- [ ] Policy violations logged for audit

### Layer 3: RLS
- [ ] Service inherits from `BaseService`
- [ ] Service receives `current_user` parameter
- [ ] Database queries use `self.query()` method
- [ ] Direct `db.query()` calls avoided

### Additional Security
- [ ] Audit logging enabled
- [ ] Error messages don't leak unauthorized data existence
- [ ] Input validation with Pydantic
- [ ] Rate limiting applied

---

## 🚫 Common Mistakes

### ❌ Missing RLS
```python
# WRONG: Direct database query bypasses RLS
@router.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()  # All users see ALL orders!
```

### ✅ Correct Implementation
```python
# CORRECT: Uses service with RLS
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_role([...])),        # RBAC
    abac: User = Depends(check_abac_permission(...)), # ABAC
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)  # RLS
    return await service.get_orders()
```

### ❌ Missing ABAC
```python
# WRONG: Role check only, no attribute checks
@router.put("/inventory/{id}")
async def update(
    id: int,
    user: User = Depends(require_role([UserRole.INVENTORY_MANAGER]))
):
    # Inventory manager from ANY warehouse can modify!
    return await service.update(id)
```

### ✅ Correct Implementation
```python
# CORRECT: ABAC checks warehouse location
@router.put("/inventory/{id}")
async def update(
    id: int,
    warehouse_id: int,
    user: User = Depends(require_role([UserRole.INVENTORY_MANAGER])),
    abac: User = Depends(check_abac_permission(
        "inventory", "modify", {"warehouse_id": warehouse_id}
    ))
):
    # Only manager of THIS warehouse can modify
    return await service.update(id)
```

---

## 📊 Decision Matrix

Use this matrix to determine required authorization layers:

| Scenario | RBAC | ABAC | RLS |
|----------|------|------|-----|
| Public product catalog | ❌ | ❌ | ❌ |
| User profile (own) | ✅ | ❌ | ✅ |
| Financial reports | ✅ | ✅ | ✅ |
| Inventory update | ✅ | ✅ | ✅ |
| HR payroll processing | ✅ | ✅ | ✅ |
| Customer orders list | ✅ | ✅ | ✅ |
| Travel sales dashboard | ✅ | ✅ | ✅ |

**Default: Use all three layers unless explicitly justified.**

---

## 🔍 Audit and Compliance

### Audit Logging

All authorization decisions MUST be logged:

```python
import logging

logger = logging.getLogger("authorization")

async def log_authorization(
    user: User,
    resource: str,
    action: str,
    granted: bool,
    reason: str = None
):
    """Log authorization decision for audit trail."""
    logger.info(
        f"Authorization: user={user.id} role={user.role} "
        f"resource={resource} action={action} granted={granted} reason={reason}"
    )
```

### Compliance Requirements

- **GDPR**: RLS ensures users only access authorized personal data
- **SOC 2**: Audit trail of all authorization decisions
- **PCI DSS**: Attribute-based controls for payment data access
- **Data Residency**: Location-based policies for regional compliance

---

## 📚 References

- **ARCHITECTURE_RULES.md** - Security Patterns § Authorization
- **AI_CONTEXT_RULES.md** - Rule 3: Authorization Framework
- **PROJECT_VISION.md** - Business requirements driving authorization
- PostgreSQL RLS Documentation: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- NIST ABAC Guide: https://csrc.nist.gov/publications/detail/sp/800-162/final

---

## 🎓 Training Resources

### For Developers

1. Read this document thoroughly
2. Review example implementations in codebase
3. Practice: Create test endpoint with all 3 layers
4. Code review: Ensure every PR follows framework

### For Security Auditors

1. Check: Every endpoint has RBAC decorator
2. Verify: ABAC policies match business requirements
3. Test: RLS filters work correctly per role
4. Audit: Logs capture authorization decisions

---

**Status:** PRODUCTION READY ✅
**Mandatory:** YES - Non-negotiable
**Last Review:** 2025-11-13
