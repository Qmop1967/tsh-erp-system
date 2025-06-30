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
from app.routers.auth import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/roles", response_model=List[dict])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles for user creation"""
    from app.models.role import Role
    roles = db.query(Role).all()
    return [{"id": role.id, "name": role.name} for role in roles]


@router.get("/branches", response_model=List[dict])
async def get_branches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all branches for user creation"""
    from app.models.branch import Branch
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    return [{"id": branch.id, "name": branch.name, "code": branch.branch_code} for branch in branches]


@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
