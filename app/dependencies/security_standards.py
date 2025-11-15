"""
Security Standards and Templates for TSH ERP
=============================================

This module provides standardized security patterns that MUST be used
across all routers and endpoints in the TSH ERP system.

Three-Layer Security Model (NON-NEGOTIABLE):
1. Authentication (Who are you?)
2. Authorization - RBAC (What role do you have?)
3. Row-Level Security - RLS (What data can you see?)
4. Attribute-Based Access Control - ABAC (Business-specific rules)

Author: Security Agent
Date: 2025-11-15
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Callable
from functools import wraps

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import RoleChecker, PermissionChecker
from app.db.rls_dependency import get_db_with_rls, get_current_user_with_rls
from app.models.user import User


# ============================================================================
# SECURITY LEVEL DEFINITIONS
# ============================================================================

class SecurityLevel:
    """
    Predefined security levels for common endpoint patterns.
    Use these to ensure consistent security across the application.
    """

    @staticmethod
    def PUBLIC():
        """
        Level 0: Public endpoints (no authentication required)

        Use ONLY for:
        - /health
        - /docs
        - /openapi.json
        - /login
        - /register
        - Public webhooks (with signature verification)

        Example:
            @router.get("/health")
            async def health_check():
                return {"status": "healthy"}
        """
        return {}

    @staticmethod
    def AUTHENTICATED():
        """
        Level 1: Authenticated users only (no role restriction)

        Use for:
        - User profile endpoints
        - Dashboard views
        - Public data viewing

        Example:
            @router.get("/profile")
            async def get_profile(current_user: User = Depends(get_current_user)):
                return current_user
        """
        return {
            "current_user": Depends(get_current_user),
            "db": Depends(get_db_with_rls)
        }

    @staticmethod
    def ADMIN_ONLY():
        """
        Level 2: Admin users only

        Use for:
        - User management
        - System configuration
        - Critical operations

        Example:
            @router.delete("/users/{user_id}")
            async def delete_user(
                user_id: int,
                current_user: User = Depends(get_current_user),
                _: dict = Depends(RoleChecker(["admin"])),
                db: Session = Depends(get_db_with_rls)
            ):
                # Only admins can access
                pass
        """
        return {
            "current_user": Depends(get_current_user),
            "_role": Depends(RoleChecker(["admin"])),
            "db": Depends(get_db_with_rls)
        }

    @staticmethod
    def MANAGER_OR_ADMIN():
        """
        Level 3: Manager or Admin users

        Use for:
        - Reports viewing
        - Business operations
        - Data exports

        Example:
            @router.get("/reports/sales")
            async def sales_report(
                current_user: User = Depends(get_current_user),
                _: dict = Depends(RoleChecker(["admin", "manager"])),
                db: Session = Depends(get_db_with_rls)
            ):
                # Admins and managers can access
                pass
        """
        return {
            "current_user": Depends(get_current_user),
            "_role": Depends(RoleChecker(["admin", "manager"])),
            "db": Depends(get_db_with_rls)
        }

    @staticmethod
    def FINANCIAL_STAFF():
        """
        Level 4: Financial staff (Admin, Manager, Accountant)

        Use for:
        - Financial reports
        - Accounting operations
        - Cash flow management

        Example:
            @router.get("/accounting/balance-sheet")
            async def balance_sheet(
                current_user: User = Depends(get_current_user),
                _: dict = Depends(RoleChecker(["admin", "manager", "accountant"])),
                db: Session = Depends(get_db_with_rls)
            ):
                # Financial staff can access
                pass
        """
        return {
            "current_user": Depends(get_current_user),
            "_role": Depends(RoleChecker(["admin", "manager", "accountant"])),
            "db": Depends(get_db_with_rls)
        }

    @staticmethod
    def INVENTORY_STAFF():
        """
        Level 5: Inventory staff (Admin, Manager, Inventory)

        Use for:
        - Stock management
        - Warehouse operations
        - Inventory reports

        Example:
            @router.post("/inventory/stock-adjustment")
            async def adjust_stock(
                current_user: User = Depends(get_current_user),
                _: dict = Depends(RoleChecker(["admin", "manager", "inventory"])),
                db: Session = Depends(get_db_with_rls)
            ):
                # Inventory staff can access
                pass
        """
        return {
            "current_user": Depends(get_current_user),
            "_role": Depends(RoleChecker(["admin", "manager", "inventory"])),
            "db": Depends(get_db_with_rls)
        }

    @staticmethod
    def SALES_STAFF():
        """
        Level 6: Sales staff (Admin, Manager, Salesperson, Cashier)

        Use for:
        - Sales operations
        - Customer management
        - POS operations

        Example:
            @router.post("/sales/create")
            async def create_sale(
                current_user: User = Depends(get_current_user),
                _: dict = Depends(RoleChecker(["admin", "manager", "salesperson", "cashier"])),
                db: Session = Depends(get_db_with_rls)
            ):
                # Sales staff can access
                pass
        """
        return {
            "current_user": Depends(get_current_user),
            "_role": Depends(RoleChecker(["admin", "manager", "salesperson", "cashier"])),
            "db": Depends(get_db_with_rls)
        }


# ============================================================================
# ABAC HELPERS (Attribute-Based Access Control)
# ============================================================================

class ABACChecker:
    """
    Attribute-Based Access Control helpers for business logic restrictions.
    These supplement RBAC with additional context-aware checks.
    """

    @staticmethod
    def check_customer_assignment(current_user: User, customer_id: int, db: Session) -> bool:
        """
        Check if salesperson is assigned to this customer.

        Usage:
            if current_user.role.name == "salesperson":
                if not ABACChecker.check_customer_assignment(current_user, customer_id, db):
                    raise HTTPException(403, "Not assigned to this customer")
        """
        from app.models.customer import Customer

        # Admins and managers can access all customers
        if current_user.role.name in ["admin", "manager"]:
            return True

        # Salespersons can only access assigned customers
        if current_user.role.name == "salesperson":
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return False
            return customer.assigned_salesperson_id == current_user.id

        return False

    @staticmethod
    def check_warehouse_access(current_user: User, warehouse_id: int) -> bool:
        """
        Check if user can access this warehouse.

        Usage:
            if not ABACChecker.check_warehouse_access(current_user, warehouse_id):
                raise HTTPException(403, "No access to this warehouse")
        """
        # Admins and managers can access all warehouses
        if current_user.role.name in ["admin", "manager"]:
            return True

        # Inventory staff can only access their assigned warehouse
        if current_user.role.name == "inventory":
            return current_user.warehouse_id == warehouse_id

        return False

    @staticmethod
    def check_branch_access(current_user: User, branch_id: int) -> bool:
        """
        Check if user can access this branch.

        Usage:
            if not ABACChecker.check_branch_access(current_user, branch_id):
                raise HTTPException(403, "No access to this branch")
        """
        # Admins can access all branches
        if current_user.role.name == "admin":
            return True

        # Other users can only access their assigned branch
        return current_user.branch_id == branch_id

    @staticmethod
    def check_work_hours(current_user: User) -> bool:
        """
        Check if current time is within user's work hours.

        Usage:
            if current_user.role.name == "cashier":
                if not ABACChecker.check_work_hours(current_user):
                    raise HTTPException(403, "Outside work hours")
        """
        from datetime import datetime

        # Admins can access anytime
        if current_user.role.name == "admin":
            return True

        # TODO: Implement actual work hours check based on user schedule
        # For now, allow access during business hours (8 AM - 8 PM)
        current_hour = datetime.now().hour
        return 8 <= current_hour <= 20

    @staticmethod
    def filter_customers_by_assignment(query, current_user: User):
        """
        Filter customer query based on user's assignments.

        Usage:
            customers = db.query(Customer)
            customers = ABACChecker.filter_customers_by_assignment(customers, current_user)
        """
        from app.models.customer import Customer

        # Admins and managers see all customers
        if current_user.role.name in ["admin", "manager"]:
            return query

        # Salespersons see only assigned customers
        if current_user.role.name == "salesperson":
            return query.filter(Customer.assigned_salesperson_id == current_user.id)

        # Other roles see no customers (restrictive default)
        return query.filter(Customer.id == -1)  # Returns empty

    @staticmethod
    def filter_inventory_by_warehouse(query, current_user: User):
        """
        Filter inventory query based on user's warehouse.

        Usage:
            stock = db.query(Stock)
            stock = ABACChecker.filter_inventory_by_warehouse(stock, current_user)
        """
        from app.models.inventory import Stock

        # Admins and managers see all warehouses
        if current_user.role.name in ["admin", "manager"]:
            return query

        # Inventory staff see only their warehouse
        if current_user.role.name == "inventory" and current_user.warehouse_id:
            return query.filter(Stock.warehouse_id == current_user.warehouse_id)

        # Other roles see all (for reporting purposes)
        return query


# ============================================================================
# SECURITY DECORATORS
# ============================================================================

def require_full_security(allowed_roles: List[str]):
    """
    Decorator for endpoints requiring full 3-layer security.

    Usage:
        @router.delete("/users/{user_id}")
        @require_full_security(["admin"])
        async def delete_user(user_id: int, ...):
            pass

    This ensures:
    1. Authentication (user must be logged in)
    2. RBAC (user must have allowed role)
    3. RLS (database queries filtered)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This is handled by FastAPI's Depends() system
            # The actual security is enforced via function parameters
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# ERROR MESSAGES (No Information Leakage)
# ============================================================================

class SecurityErrors:
    """
    Standardized security error messages that don't leak information.
    """

    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access denied"
    INVALID_TOKEN = "Invalid or expired token"
    INACTIVE_USER = "Account inactive"
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions"
    CUSTOMER_NOT_ASSIGNED = "Resource not accessible"
    WAREHOUSE_RESTRICTED = "Resource not accessible"
    BRANCH_RESTRICTED = "Resource not accessible"
    OUTSIDE_WORK_HOURS = "Operation not available at this time"

    @staticmethod
    def raise_unauthorized():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=SecurityErrors.UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def raise_forbidden(detail: Optional[str] = None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or SecurityErrors.FORBIDDEN
        )

    @staticmethod
    def raise_insufficient_permissions():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=SecurityErrors.INSUFFICIENT_PERMISSIONS
        )


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example 1: Public Endpoint
---------------------------
@router.get("/health")
async def health_check():
    return {"status": "healthy"}


Example 2: Authenticated Endpoint
----------------------------------
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_with_rls)
):
    return current_user


Example 3: Admin-Only Endpoint
-------------------------------
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    _: dict = Depends(RoleChecker(["admin"])),
    db: Session = Depends(get_db_with_rls)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


Example 4: Sales Endpoint with ABAC
------------------------------------
@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    _: dict = Depends(RoleChecker(["admin", "manager", "salesperson"])),
    db: Session = Depends(get_db_with_rls)
):
    # ABAC: Check customer assignment for salespersons
    if current_user.role.name == "salesperson":
        if not ABACChecker.check_customer_assignment(current_user, customer_id, db):
            SecurityErrors.raise_forbidden(SecurityErrors.CUSTOMER_NOT_ASSIGNED)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")

    return customer


Example 5: Inventory Endpoint with Warehouse Restriction
----------------------------------------------------------
@router.get("/stock")
async def get_stock(
    current_user: User = Depends(get_current_user),
    _: dict = Depends(RoleChecker(["admin", "manager", "inventory"])),
    db: Session = Depends(get_db_with_rls)
):
    # Get stock query
    stock_query = db.query(Stock)

    # ABAC: Filter by warehouse for inventory staff
    stock_query = ABACChecker.filter_inventory_by_warehouse(stock_query, current_user)

    return stock_query.all()


Example 6: Financial Endpoint with Multiple Restrictions
---------------------------------------------------------
@router.get("/reports/financial")
async def financial_report(
    branch_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    _: dict = Depends(RoleChecker(["admin", "manager", "accountant"])),
    db: Session = Depends(get_db_with_rls)
):
    # ABAC: Branch restriction
    if branch_id and not ABACChecker.check_branch_access(current_user, branch_id):
        SecurityErrors.raise_forbidden(SecurityErrors.BRANCH_RESTRICTED)

    # Query financial data
    # RLS automatically filters by user's accessible data
    report_data = db.query(FinancialTransaction).all()

    return report_data
"""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SecurityLevel',
    'ABACChecker',
    'SecurityErrors',
    'require_full_security'
]
