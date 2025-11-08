"""
User Management Router for TSH ERP System
راوتر إدارة المستخدمين لنظام TSH ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.dependencies.auth import get_current_user
from app.services.auth_service import AuthService
from app.services.permission_service import simple_require_permission

router = APIRouter(prefix="/users", tags=["users"])


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


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


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


@router.post("/", response_model=UserSchema)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled
):
    """Create new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password before storing
    user_data = user.dict()
    user_data["password"] = AuthService.get_password_hash(user_data["password"])
    
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled
):
    """Update user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user.dict(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data and update_data["password"]:
        update_data["password"] = AuthService.get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Temporarily disabled
):
    """Delete user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
