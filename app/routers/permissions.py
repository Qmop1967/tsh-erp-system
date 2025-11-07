"""
Permissions Management Router for TSH ERP System
راوتر إدارة الصلاحيات لنظام TSH ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.permissions import Permission, RolePermission
from app.dependencies.auth import get_current_user
from app.services.permission_service import simple_require_permission
from pydantic import BaseModel

router = APIRouter(prefix="/permissions", tags=["permissions"])


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permission_ids: List[int] = []
    is_active: bool = True


@router.get("/", response_model=List[PermissionResponse])
@simple_require_permission("admin")
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all permissions"""
    permissions = db.query(Permission).all()
    return permissions


@router.get("/roles", response_model=List[RoleResponse])
@simple_require_permission("admin")
async def get_roles_with_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles with their permissions"""
    roles = db.query(Role).all()
    
    # For each role, get its permissions
    result = []
    for role in roles:
        role_permissions = db.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(RolePermission.role_id == role.id).all()
        
        result.append({
            "id": role.id,
            "name": role.name,
            "description": role.description or "",
            "is_active": role.is_active if role.is_active is not None else True,
            "permissions": role_permissions
        })
    
    return result


@router.post("/roles", response_model=RoleResponse)
@simple_require_permission("admin")
async def create_role(
    role_data: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new role with permissions"""
    
    # Check if role name already exists
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    # Create the role
    new_role = Role(
        name=role_data.name,
        description=role_data.description,
        is_active=role_data.is_active
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    # Add permissions to the role
    for permission_id in role_data.permission_ids:
        # Verify permission exists
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            role_permission = RolePermission(
                role_id=new_role.id,
                permission_id=permission_id
            )
            db.add(role_permission)
    
    db.commit()
    
    # Return role with permissions
    role_permissions = db.query(Permission).join(
        RolePermission, Permission.id == RolePermission.permission_id
    ).filter(RolePermission.role_id == new_role.id).all()
    
    return {
        "id": new_role.id,
        "name": new_role.name,
        "description": new_role.description,
        "is_active": new_role.is_active,
        "permissions": role_permissions
    }


@router.put("/roles/{role_id}", response_model=RoleResponse)
@simple_require_permission("admin")
async def update_role(
    role_id: int,
    role_data: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update role and its permissions"""
    
    # Get the role
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Update role fields
    role.name = role_data.name
    role.description = role_data.description
    role.is_active = role_data.is_active
    
    # Remove existing permissions
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    
    # Add new permissions
    for permission_id in role_data.permission_ids:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id
            )
            db.add(role_permission)
    
    db.commit()
    
    # Return updated role with permissions
    role_permissions = db.query(Permission).join(
        RolePermission, Permission.id == RolePermission.permission_id
    ).filter(RolePermission.role_id == role_id).all()
    
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_active": role.is_active,
        "permissions": role_permissions
    }


@router.delete("/roles/{role_id}")
@simple_require_permission("admin")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a role (only if no users are assigned to it)"""
    
    # Check if role exists
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if any users have this role
    users_with_role = db.query(User).filter(User.role_id == role_id).count()
    if users_with_role > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role. {users_with_role} users are assigned to this role."
        )
    
    # Remove role permissions
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    
    # Delete the role
    db.delete(role)
    db.commit()
    
    return {"message": "Role deleted successfully"}


@router.get("/categories")
@simple_require_permission("admin")
async def get_permission_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all permission categories"""
    categories = db.query(Permission.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]
