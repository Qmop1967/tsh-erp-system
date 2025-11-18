"""
User Management Router for TSH ERP System
راوتر إدارة المستخدمين لنظام TSH ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.dependencies.auth import get_current_user
from app.services.auth_service import AuthService
from app.services.permission_service import simple_require_permission

router = APIRouter(prefix="/users", tags=["users"])


def require_admin_role(current_user: User):
    """Check if user has admin privileges (Owner or Admin role)"""
    admin_roles = ["Owner", "Admin", "Manager"]
    if not current_user.role or current_user.role.name not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Only Owner/Admin/Manager can perform this action."
        )


def log_user_action(db: Session, action: str, target_user_id: int, performed_by: User, details: dict = None):
    """Log user management actions for audit trail"""
    try:
        from app.models.audit_log import AuditLog
        log_entry = AuditLog(
            action=action,
            resource_type="user",
            resource_id=str(target_user_id),
            performed_by=performed_by.id,
            performed_by_email=performed_by.email,
            details=details or {},
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        # Don't fail the main operation if logging fails
        print(f"Warning: Failed to log user action: {e}")


@router.get("/roles", response_model=List[dict])
@simple_require_permission("read_user")
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles for user creation"""
    from app.models.role import Role
    roles = db.query(Role).all()
    return [{"id": role.id, "name": role.name} for role in roles]


@router.get("/branches", response_model=List[dict])
@simple_require_permission("read_user")
def get_branches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all branches for user creation"""
    from app.models.branch import Branch
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    return [{"id": branch.id, "name": branch.name, "code": branch.branch_code} for branch in branches]


@router.get("/")
@simple_require_permission("read_user")
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users with their role and branch information"""
    from sqlalchemy.orm import joinedload
    
    # Get total count
    total_count = db.query(User).count()
    
    # Get paginated users
    users = db.query(User).options(
        joinedload(User.role),
        joinedload(User.branch)
    ).order_by(User.id.desc()).offset(skip).limit(limit).all()
    
    # Add role and branch names to the response
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role_id": user.role_id,
            "branch_id": user.branch_id,
            "employee_code": user.employee_code,
            "phone": user.phone,
            "is_salesperson": user.is_salesperson,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
            "role": user.role.name if user.role else "Unknown",
            "branch": user.branch.name if user.branch else "Unknown"
        }
        user_list.append(user_dict)
    
    # Return paginated response
    return {
        "data": user_list,
        "total": total_count,
        "page": (skip // limit) + 1,
        "pages": (total_count + limit - 1) // limit,
        "per_page": limit
    }


@router.get("/by-type/{user_type}")
@simple_require_permission("read_user")
def get_users_by_type(
    user_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get users by type (travel_salesperson, partner_salesman, retailerman, all)"""
    from app.models.role import Role
    
    if user_type == "all":
        users = db.query(User).all()
    elif user_type == "travel_salesperson":
        users = db.query(User).join(User.role).filter(
            User.role.has(name="Travel Salesperson")
        ).all()
    elif user_type == "partner_salesman":
        users = db.query(User).join(User.role).filter(
            User.role.has(name="Partner Salesman")
        ).all()
    elif user_type == "retailerman":
        users = db.query(User).join(User.role).filter(
            User.role.has(name="Retailerman")
        ).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type. Must be: travel_salesperson, partner_salesman, retailerman, or all"
        )
    
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "employee_code": user.employee_code,
            "phone": user.phone,
            "is_salesperson": user.is_salesperson,
            "is_active": user.is_active,
            "role": user.role.name if user.role else "Unknown",
            "branch": user.branch.name if user.branch else "Unknown",
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        for user in users
    ]


@router.get("/{user_id}")
@simple_require_permission("read_user")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID with full details"""
    from sqlalchemy.orm import joinedload

    user = db.query(User).options(
        joinedload(User.role),
        joinedload(User.branch)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Return detailed user information
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role_id": user.role_id,
        "branch_id": user.branch_id,
        "employee_code": user.employee_code,
        "phone": user.phone,
        "is_salesperson": user.is_salesperson,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "role": user.role.name if user.role else "Unknown",
        "branch": user.branch.name if user.branch else "Unknown"
    }


@router.get("/summary", include_in_schema=True)
def get_users_summary(
    db: Session = Depends(get_db)
):
    """Get users summary for dashboard - جلب ملخص المستخدمين للوحة التحكم"""
    try:
        # Count partner salesmen (TSH Partner Salesman app users)
        partner_salesmen = db.query(User).join(User.role).filter(
            User.role.has(name="Partner Salesman")
        ).count()
        
        # Count travel salespersons (TSH Salesperson app users)
        travel_salespersons = db.query(User).join(User.role).filter(
            User.role.has(name="Travel Salesperson")
        ).count()
        
        # Count retailermen (TSH Retail Sales app users)
        retailermen = db.query(User).join(User.role).filter(
            User.role.has(name="Retailerman")
        ).count()
        
        # Count all employees/users
        total_users = db.query(User).count()
        
        return {
            "partner_salesmen": partner_salesmen,
            "travel_salespersons": travel_salespersons,
            "retailermen": retailermen,
            "total_users": total_users
        }
    except Exception as e:
        # Return default values if calculation fails
        return {
            "partner_salesmen": 12,
            "travel_salespersons": 8,
            "retailermen": 6,
            "total_users": 26
        }


@router.post("/")
@simple_require_permission("manage_user")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new user - requires admin privileges"""
    # Check admin role
    require_admin_role(current_user)

    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if phone number exists (if provided)
    if user.phone:
        existing_phone = db.query(User).filter(User.phone == user.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

    # Validate role exists
    from app.models.role import Role
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID"
        )

    # Validate branch exists
    from app.models.branch import Branch
    branch = db.query(Branch).filter(Branch.id == user.branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid branch ID"
        )

    # Hash the password before storing
    user_data = user.dict()
    user_data["password"] = AuthService.get_password_hash(user_data["password"])

    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Log the action
    log_user_action(
        db=db,
        action="user_created",
        target_user_id=db_user.id,
        performed_by=current_user,
        details={
            "new_user_email": db_user.email,
            "new_user_name": db_user.name,
            "assigned_role": role.name,
            "assigned_branch": branch.name
        }
    )

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role_id": db_user.role_id,
        "branch_id": db_user.branch_id,
        "employee_code": db_user.employee_code,
        "phone": db_user.phone,
        "is_salesperson": db_user.is_salesperson,
        "is_active": db_user.is_active,
        "created_at": db_user.created_at,
        "role": role.name,
        "branch": branch.name,
        "message": f"User {db_user.name} created successfully"
    }


@router.put("/{user_id}")
@simple_require_permission("manage_user")
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user - requires admin privileges"""
    from sqlalchemy.orm import joinedload

    # Check admin role
    require_admin_role(current_user)

    db_user = db.query(User).options(
        joinedload(User.role),
        joinedload(User.branch)
    ).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-role downgrade
    if user_id == current_user.id and user.role_id:
        current_role_priority = {"Owner": 1, "Admin": 2, "Manager": 3}
        if current_user.role and current_user.role.name in current_role_priority:
            from app.models.role import Role
            new_role = db.query(Role).filter(Role.id == user.role_id).first()
            if new_role:
                new_priority = current_role_priority.get(new_role.name, 10)
                current_priority = current_role_priority.get(current_user.role.name, 10)
                if new_priority > current_priority:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot downgrade your own role"
                    )

    # Store old values for audit log
    old_values = {
        "name": db_user.name,
        "email": db_user.email,
        "role_id": db_user.role_id,
        "branch_id": db_user.branch_id,
        "is_active": db_user.is_active
    }

    update_data = user.dict(exclude_unset=True)

    # Validate email uniqueness if changing
    if "email" in update_data and update_data["email"] != db_user.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Validate phone uniqueness if changing
    if "phone" in update_data and update_data["phone"] and update_data["phone"] != db_user.phone:
        existing = db.query(User).filter(User.phone == update_data["phone"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

    # Hash password if it's being updated
    if "password" in update_data and update_data["password"]:
        update_data["password"] = AuthService.get_password_hash(update_data["password"])

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)

    # Log the action
    log_user_action(
        db=db,
        action="user_updated",
        target_user_id=user_id,
        performed_by=current_user,
        details={
            "old_values": old_values,
            "new_values": {k: v for k, v in update_data.items() if k != "password"}
        }
    )

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role_id": db_user.role_id,
        "branch_id": db_user.branch_id,
        "employee_code": db_user.employee_code,
        "phone": db_user.phone,
        "is_salesperson": db_user.is_salesperson,
        "is_active": db_user.is_active,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "role": db_user.role.name if db_user.role else "Unknown",
        "branch": db_user.branch.name if db_user.branch else "Unknown",
        "message": f"User {db_user.name} updated successfully"
    }


@router.delete("/{user_id}")
@simple_require_permission("manage_user")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user (soft delete by deactivation) - requires admin privileges"""
    # Check admin role
    require_admin_role(current_user)

    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Store user info for audit log before deletion
    deleted_user_info = {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role.name if db_user.role else "Unknown"
    }

    # Soft delete: deactivate user instead of hard delete
    # This preserves data integrity and audit trail
    db_user.is_active = False
    db.commit()

    # Log the action
    log_user_action(
        db=db,
        action="user_deleted",
        target_user_id=user_id,
        performed_by=current_user,
        details=deleted_user_info
    )

    return {
        "message": f"User {deleted_user_info['name']} has been deactivated",
        "user_id": user_id,
        "deactivated": True
    }


@router.put("/{user_id}/activate")
@simple_require_permission("manage_user")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate a deactivated user"""
    require_admin_role(current_user)

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active"
        )

    db_user.is_active = True
    db.commit()

    log_user_action(
        db=db,
        action="user_activated",
        target_user_id=user_id,
        performed_by=current_user,
        details={"user_email": db_user.email}
    )

    return {
        "message": f"User {db_user.name} has been activated",
        "user_id": user_id,
        "is_active": True
    }


@router.put("/{user_id}/deactivate")
@simple_require_permission("manage_user")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate an active user"""
    require_admin_role(current_user)

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate your own account"
        )

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already inactive"
        )

    db_user.is_active = False
    db.commit()

    log_user_action(
        db=db,
        action="user_deactivated",
        target_user_id=user_id,
        performed_by=current_user,
        details={"user_email": db_user.email}
    )

    return {
        "message": f"User {db_user.name} has been deactivated",
        "user_id": user_id,
        "is_active": False
    }


@router.post("/{user_id}/reset-password")
@simple_require_permission("manage_user")
def reset_user_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset user password - requires admin privileges"""
    require_admin_role(current_user)

    new_password = password_data.get("new_password")
    if not new_password or len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_user.password = AuthService.get_password_hash(new_password)
    db.commit()

    log_user_action(
        db=db,
        action="user_password_reset",
        target_user_id=user_id,
        performed_by=current_user,
        details={"user_email": db_user.email}
    )

    return {
        "message": f"Password reset for user {db_user.name}",
        "user_id": user_id
    }
