"""
Data Scope Management API
Manage user data access scope for Row-Level Security (RLS)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.data_scope import (
    UserDataScope, DataScopeType, DataScopeTemplate,
    DataAccessLog, user_customers, user_warehouses, user_branches
)
from app.routers.auth_enhanced import get_current_user
from app.services.rls_service import RLSService


router = APIRouter(prefix="/data-scope", tags=["Data Scope - RLS Management"])


# Pydantic Schemas
class DataScopeConfigRequest(BaseModel):
    user_id: int
    scope_type: str  # "all", "branch", "warehouse", "customer", "region", "custom"
    auto_filter_customers: bool = False
    auto_filter_warehouses: bool = False
    auto_filter_branches: bool = False
    auto_filter_sales: bool = False
    auto_filter_inventory: bool = False
    auto_filter_transactions: bool = False
    include_subordinates: bool = False


class DataScopeResponse(BaseModel):
    id: int
    user_id: int
    scope_type: str
    auto_filter_customers: bool
    auto_filter_warehouses: bool
    auto_filter_branches: bool
    auto_filter_sales: bool
    auto_filter_inventory: bool
    auto_filter_transactions: bool
    include_subordinates: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignCustomersRequest(BaseModel):
    user_id: int
    customer_ids: List[int]


class AssignWarehousesRequest(BaseModel):
    user_id: int
    warehouse_ids: List[int]


class AssignBranchesRequest(BaseModel):
    user_id: int
    branch_ids: List[int]


class AssignmentResponse(BaseModel):
    user_id: int
    assigned_count: int
    message: str


class AccessCheckRequest(BaseModel):
    resource_type: str  # "customer", "warehouse", "branch"
    resource_id: int


class AccessCheckResponse(BaseModel):
    can_access: bool
    reason: Optional[str] = None


# ========== Data Scope Configuration Endpoints ==========

@router.post("/configure", response_model=DataScopeResponse)
async def configure_user_data_scope(
    config: DataScopeConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configure data access scope for a user
    Requires admin permission
    """
    # Check if current user has permission to configure data scope
    # TODO: Add permission check

    # Check if user exists
    target_user = db.query(User).filter(User.id == config.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if scope already exists
    existing_scope = db.query(UserDataScope).filter(
        UserDataScope.user_id == config.user_id
    ).first()

    if existing_scope:
        # Update existing scope
        existing_scope.scope_type = config.scope_type
        existing_scope.auto_filter_customers = config.auto_filter_customers
        existing_scope.auto_filter_warehouses = config.auto_filter_warehouses
        existing_scope.auto_filter_branches = config.auto_filter_branches
        existing_scope.auto_filter_sales = config.auto_filter_sales
        existing_scope.auto_filter_inventory = config.auto_filter_inventory
        existing_scope.auto_filter_transactions = config.auto_filter_transactions
        existing_scope.include_subordinates = config.include_subordinates
        existing_scope.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing_scope)
        return existing_scope

    # Create new scope
    new_scope = UserDataScope(
        user_id=config.user_id,
        scope_type=config.scope_type,
        auto_filter_customers=config.auto_filter_customers,
        auto_filter_warehouses=config.auto_filter_warehouses,
        auto_filter_branches=config.auto_filter_branches,
        auto_filter_sales=config.auto_filter_sales,
        auto_filter_inventory=config.auto_filter_inventory,
        auto_filter_transactions=config.auto_filter_transactions,
        include_subordinates=config.include_subordinates,
        created_by=current_user.id
    )

    db.add(new_scope)
    db.commit()
    db.refresh(new_scope)

    return new_scope


@router.get("/user/{user_id}", response_model=DataScopeResponse)
async def get_user_data_scope(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data scope configuration for a user"""
    scope = db.query(UserDataScope).filter(
        UserDataScope.user_id == user_id
    ).first()

    if not scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data scope not configured for this user"
        )

    return scope


@router.get("/my-scope", response_model=DataScopeResponse)
async def get_my_data_scope(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's data scope configuration"""
    scope = RLSService.get_user_scope(db, current_user)

    if not scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data scope not configured for your account"
        )

    return scope


# ========== Assignment Endpoints ==========

@router.post("/assign-customers", response_model=AssignmentResponse)
async def assign_customers_to_user(
    assignment: AssignCustomersRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign customers to a user for RLS filtering
    Field sales reps can only access their assigned customers
    """
    # Check if user exists
    target_user = db.query(User).filter(User.id == assignment.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Clear existing assignments
    db.execute(f"DELETE FROM user_customers WHERE user_id = {assignment.user_id}")

    # Add new assignments
    for customer_id in assignment.customer_ids:
        db.execute(
            f"INSERT INTO user_customers (user_id, customer_id, assigned_by, assigned_at) "
            f"VALUES ({assignment.user_id}, {customer_id}, {current_user.id}, NOW())"
        )

    db.commit()

    return AssignmentResponse(
        user_id=assignment.user_id,
        assigned_count=len(assignment.customer_ids),
        message=f"Successfully assigned {len(assignment.customer_ids)} customers to user"
    )


@router.post("/assign-warehouses", response_model=AssignmentResponse)
async def assign_warehouses_to_user(
    assignment: AssignWarehousesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign warehouses to a user for RLS filtering
    Field sales reps can only access their assigned warehouses
    """
    target_user = db.query(User).filter(User.id == assignment.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Clear existing assignments
    db.execute(f"DELETE FROM user_warehouses WHERE user_id = {assignment.user_id}")

    # Add new assignments
    for warehouse_id in assignment.warehouse_ids:
        db.execute(
            f"INSERT INTO user_warehouses (user_id, warehouse_id, assigned_by, assigned_at) "
            f"VALUES ({assignment.user_id}, {warehouse_id}, {current_user.id}, NOW())"
        )

    db.commit()

    return AssignmentResponse(
        user_id=assignment.user_id,
        assigned_count=len(assignment.warehouse_ids),
        message=f"Successfully assigned {len(assignment.warehouse_ids)} warehouses to user"
    )


@router.post("/assign-branches", response_model=AssignmentResponse)
async def assign_branches_to_user(
    assignment: AssignBranchesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign branches to a user for RLS filtering"""
    target_user = db.query(User).filter(User.id == assignment.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Clear existing assignments
    db.execute(f"DELETE FROM user_branches WHERE user_id = {assignment.user_id}")

    # Add new assignments
    for branch_id in assignment.branch_ids:
        db.execute(
            f"INSERT INTO user_branches (user_id, branch_id, assigned_by, assigned_at) "
            f"VALUES ({assignment.user_id}, {branch_id}, {current_user.id}, NOW())"
        )

    db.commit()

    return AssignmentResponse(
        user_id=assignment.user_id,
        assigned_count=len(assignment.branch_ids),
        message=f"Successfully assigned {len(assignment.branch_ids)} branches to user"
    )


# ========== Access Check Endpoints ==========

@router.post("/check-access", response_model=AccessCheckResponse)
async def check_resource_access(
    check: AccessCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user can access a specific resource
    Used for client-side access control
    """
    can_access = False
    reason = None

    if check.resource_type == "customer":
        can_access = RLSService.can_access_customer(db, current_user, check.resource_id)
        if not can_access:
            reason = "Customer not assigned to your account"

    elif check.resource_type == "warehouse":
        can_access = RLSService.can_access_warehouse(db, current_user, check.resource_id)
        if not can_access:
            reason = "Warehouse not assigned to your account"

    else:
        reason = f"Unknown resource type: {check.resource_type}"

    return AccessCheckResponse(
        can_access=can_access,
        reason=reason
    )


@router.get("/my-customers")
async def get_my_assigned_customers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of customers assigned to current user"""
    customer_ids = RLSService.get_assigned_customer_ids(db, current_user)

    return {
        "user_id": current_user.id,
        "customer_ids": customer_ids,
        "count": len(customer_ids)
    }


@router.get("/my-warehouses")
async def get_my_assigned_warehouses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of warehouses assigned to current user"""
    warehouse_ids = RLSService.get_assigned_warehouse_ids(db, current_user)

    return {
        "user_id": current_user.id,
        "warehouse_ids": warehouse_ids,
        "count": len(warehouse_ids)
    }


@router.get("/my-branches")
async def get_my_assigned_branches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of branches assigned to current user"""
    branch_ids = RLSService.get_assigned_branch_ids(db, current_user)

    return {
        "user_id": current_user.id,
        "branch_ids": branch_ids,
        "count": len(branch_ids)
    }


# ========== Quick Setup Endpoints ==========

@router.post("/quick-setup/field-sales/{user_id}")
async def quick_setup_field_sales_scope(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick setup for field sales representative
    - Auto-filter customers, warehouses, sales, inventory, transactions
    - Access limited to assigned resources only
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    scope = RLSService.create_default_scope_for_field_sales(
        db, target_user, current_user.id
    )

    return {
        "message": "Field sales data scope configured successfully",
        "user_id": user_id,
        "scope": DataScopeResponse.from_orm(scope)
    }


@router.post("/quick-setup/finance/{user_id}")
async def quick_setup_finance_scope(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick setup for finance staff
    - Auto-filter transactions and sales by assigned customers
    - Access limited to linked customer transactions only
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    scope = RLSService.create_default_scope_for_finance(
        db, target_user, current_user.id
    )

    return {
        "message": "Finance data scope configured successfully",
        "user_id": user_id,
        "scope": DataScopeResponse.from_orm(scope)
    }


@router.post("/quick-setup/admin/{user_id}")
async def quick_setup_admin_scope(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick setup for admin users
    - Full access to all data (no filtering)
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    scope = RLSService.create_admin_scope(
        db, target_user, current_user.id
    )

    return {
        "message": "Admin data scope configured successfully",
        "user_id": user_id,
        "scope": DataScopeResponse.from_orm(scope)
    }
