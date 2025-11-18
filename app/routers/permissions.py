"""
Permissions Management Router for TSH ERP System
راوتر إدارة الصلاحيات لنظام TSH ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.permissions import Permission, RolePermission, UserPermission
from app.dependencies.auth import get_current_user
from app.services.permission_service import simple_require_permission
from pydantic import BaseModel

router = APIRouter(prefix="/permissions", tags=["permissions"])


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class UserPermissionResponse(BaseModel):
    permission_id: int
    permission_code: str
    permission_name: str
    is_granted: bool
    source: str  # "role" or "override"
    granted_by: Optional[int] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserPermissionsListResponse(BaseModel):
    user_id: int
    user_name: str
    role_name: str
    role_permissions: List[PermissionResponse]
    permission_overrides: List[UserPermissionResponse]
    effective_permissions: List[str]  # List of permission codes


class GrantPermissionRequest(BaseModel):
    permission_id: int
    expires_at: Optional[datetime] = None


class RevokePermissionRequest(BaseModel):
    permission_id: int


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


# User-specific permission management endpoints
@router.get("/users/{user_id}", response_model=UserPermissionsListResponse)
@simple_require_permission("admin")
async def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all permissions for a specific user (role + overrides)"""

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get user's role
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else "Unknown"

    # Get role permissions
    role_permissions = []
    if role:
        role_permissions = db.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).filter(RolePermission.role_id == role.id).all()

    # Get user permission overrides
    user_overrides = db.query(UserPermission).filter(
        UserPermission.user_id == user_id
    ).all()

    permission_overrides = []
    for override in user_overrides:
        perm = db.query(Permission).filter(Permission.id == override.permission_id).first()
        if perm:
            permission_overrides.append({
                "permission_id": perm.id,
                "permission_code": perm.code or f"{perm.module}.{perm.action}",
                "permission_name": perm.name,
                "is_granted": override.is_granted,
                "source": "override",
                "granted_by": override.granted_by,
                "granted_at": override.granted_at,
                "expires_at": override.expires_at
            })

    # Calculate effective permissions
    effective_permissions = set()

    # Add role permissions
    for perm in role_permissions:
        effective_permissions.add(perm.code or f"{perm.module}.{perm.action}")

    # Apply overrides
    for override in user_overrides:
        perm = db.query(Permission).filter(Permission.id == override.permission_id).first()
        if perm:
            perm_code = perm.code or f"{perm.module}.{perm.action}"
            if override.is_granted:
                effective_permissions.add(perm_code)
            else:
                effective_permissions.discard(perm_code)

    return {
        "user_id": user_id,
        "user_name": user.name,
        "role_name": role_name,
        "role_permissions": role_permissions,
        "permission_overrides": permission_overrides,
        "effective_permissions": list(effective_permissions)
    }


@router.post("/users/{user_id}/grant")
@simple_require_permission("admin")
async def grant_permission_to_user(
    user_id: int,
    request: GrantPermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Grant a specific permission to a user (override)"""

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify permission exists
    permission = db.query(Permission).filter(Permission.id == request.permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    # Check if override already exists
    existing_override = db.query(UserPermission).filter(
        UserPermission.user_id == user_id,
        UserPermission.permission_id == request.permission_id
    ).first()

    if existing_override:
        # Update existing override
        existing_override.is_granted = True
        existing_override.granted_by = current_user.id
        existing_override.granted_at = datetime.utcnow()
        existing_override.expires_at = request.expires_at
    else:
        # Create new override
        new_override = UserPermission(
            user_id=user_id,
            permission_id=request.permission_id,
            is_granted=True,
            granted_by=current_user.id,
            granted_at=datetime.utcnow(),
            expires_at=request.expires_at
        )
        db.add(new_override)

    db.commit()

    return {
        "message": f"Permission '{permission.name}' granted to user {user.name}",
        "permission_id": permission.id,
        "permission_code": permission.code or f"{permission.module}.{permission.action}",
        "user_id": user_id,
        "expires_at": request.expires_at
    }


@router.post("/users/{user_id}/revoke")
@simple_require_permission("admin")
async def revoke_permission_from_user(
    user_id: int,
    request: RevokePermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke a specific permission from a user (create negative override)"""

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify permission exists
    permission = db.query(Permission).filter(Permission.id == request.permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    # Check if override already exists
    existing_override = db.query(UserPermission).filter(
        UserPermission.user_id == user_id,
        UserPermission.permission_id == request.permission_id
    ).first()

    if existing_override:
        # Update to revoke
        existing_override.is_granted = False
        existing_override.granted_by = current_user.id
        existing_override.granted_at = datetime.utcnow()
        existing_override.expires_at = None
    else:
        # Create negative override
        new_override = UserPermission(
            user_id=user_id,
            permission_id=request.permission_id,
            is_granted=False,
            granted_by=current_user.id,
            granted_at=datetime.utcnow()
        )
        db.add(new_override)

    db.commit()

    return {
        "message": f"Permission '{permission.name}' revoked from user {user.name}",
        "permission_id": permission.id,
        "permission_code": permission.code or f"{permission.module}.{permission.action}",
        "user_id": user_id
    }


@router.delete("/users/{user_id}/overrides/{permission_id}")
@simple_require_permission("admin")
async def remove_permission_override(
    user_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a permission override (revert to role-based permission)"""

    # Get the override
    override = db.query(UserPermission).filter(
        UserPermission.user_id == user_id,
        UserPermission.permission_id == permission_id
    ).first()

    if not override:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission override not found"
        )

    db.delete(override)
    db.commit()

    return {
        "message": "Permission override removed. User will inherit role-based permission.",
        "user_id": user_id,
        "permission_id": permission_id
    }
