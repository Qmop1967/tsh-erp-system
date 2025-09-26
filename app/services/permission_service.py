# Permission Service for Advanced RBAC/ABAC
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json
from datetime import datetime

from app.models.permissions import Permission, RolePermission, UserPermission, AuditLog
from app.models.permissions import PermissionType, ResourceType
from app.models.user import User
from app.models.role import Role
from app.db.database import get_db

class PermissionService:
    """Advanced permission management service with RBAC and ABAC support"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_permission(self, user_id: int, permission_name: str, 
                        resource_id: Optional[str] = None, 
                        context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if user has permission with optional attribute-based conditions
        """
        # Get user with roles
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return False
        
        # Check direct user permissions first (highest priority)
        user_permission = self._check_user_permission(user_id, permission_name, context)
        if user_permission is not None:
            return user_permission
        
        # Check role-based permissions
        return self._check_role_permissions(user.role_id, permission_name, context)
    
    def _check_user_permission(self, user_id: int, permission_name: str, 
                              context: Optional[Dict[str, Any]] = None) -> Optional[bool]:
        """Check direct user permissions"""
        query = self.db.query(UserPermission).join(Permission).filter(
            and_(
                UserPermission.user_id == user_id,
                Permission.name == permission_name,
                Permission.is_active == True,
                or_(
                    UserPermission.expires_at.is_(None),
                    UserPermission.expires_at > datetime.utcnow()
                )
            )
        ).order_by(UserPermission.granted_at.desc())
        
        user_permission = query.first()
        if not user_permission:
            return None
        
        # Check conditions if present
        if user_permission.conditions:
            return self._evaluate_conditions(user_permission.conditions, context)
        
        return user_permission.is_granted
    
    def _check_role_permissions(self, role_id: int, permission_name: str,
                               context: Optional[Dict[str, Any]] = None) -> bool:
        """Check role-based permissions"""
        role_permission = self.db.query(RolePermission).join(Permission).filter(
            and_(
                RolePermission.role_id == role_id,
                Permission.name == permission_name,
                Permission.is_active == True
            )
        ).first()
        
        if not role_permission:
            return False
        
        # Check conditions if present
        if role_permission.conditions:
            return self._evaluate_conditions(role_permission.conditions, context)
        
        return True
    
    def _evaluate_conditions(self, conditions_json: str, 
                           context: Optional[Dict[str, Any]] = None) -> bool:
        """Evaluate attribute-based conditions"""
        if not conditions_json or not context:
            return True
        
        try:
            conditions = json.loads(conditions_json)
            return self._evaluate_condition_tree(conditions, context)
        except (json.JSONDecodeError, Exception):
            return False
    
    def _evaluate_condition_tree(self, condition: Dict[str, Any], 
                               context: Dict[str, Any]) -> bool:
        """Recursively evaluate condition tree"""
        if "and" in condition:
            return all(self._evaluate_condition_tree(c, context) for c in condition["and"])
        elif "or" in condition:
            return any(self._evaluate_condition_tree(c, context) for c in condition["or"])
        elif "not" in condition:
            return not self._evaluate_condition_tree(condition["not"], context)
        else:
            # Simple condition: {"field": "branch_id", "operator": "eq", "value": 1}
            field = condition.get("field")
            operator = condition.get("operator")
            expected_value = condition.get("value")
            
            if field not in context:
                return False
            
            actual_value = context[field]
            
            if operator == "eq":
                return actual_value == expected_value
            elif operator == "ne":
                return actual_value != expected_value
            elif operator == "in":
                return actual_value in expected_value
            elif operator == "not_in":
                return actual_value not in expected_value
            elif operator == "gt":
                return actual_value > expected_value
            elif operator == "gte":
                return actual_value >= expected_value
            elif operator == "lt":
                return actual_value < expected_value
            elif operator == "lte":
                return actual_value <= expected_value
            
            return False
    
    def grant_permission(self, granter_id: int, user_id: int, permission_name: str,
                        conditions: Optional[Dict[str, Any]] = None,
                        expires_at: Optional[datetime] = None) -> bool:
        """Grant permission to user"""
        permission = self.db.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        
        if not permission:
            return False
        
        # Check if granter has permission to grant this permission
        if not self.check_permission(granter_id, f"grant_{permission_name}"):
            return False
        
        # Create or update user permission
        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission.id,
            is_granted=True,
            granted_by=granter_id,
            expires_at=expires_at,
            conditions=json.dumps(conditions) if conditions else None
        )
        
        self.db.add(user_permission)
        self.db.commit()
        
        # Log the action
        self.log_action(granter_id, "grant_permission", "permission", 
                       f"{user_id}:{permission_name}")
        
        return True
    
    def revoke_permission(self, revoker_id: int, user_id: int, permission_name: str) -> bool:
        """Revoke permission from user"""
        # Check if revoker has permission to revoke
        if not self.check_permission(revoker_id, f"revoke_{permission_name}"):
            return False
        
        permission = self.db.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        
        if not permission:
            return False
        
        # Add revocation record
        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission.id,
            is_granted=False,
            granted_by=revoker_id
        )
        
        self.db.add(user_permission)
        self.db.commit()
        
        # Log the action
        self.log_action(revoker_id, "revoke_permission", "permission",
                       f"{user_id}:{permission_name}")
        
        return True
    
    def get_user_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all effective permissions for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        permissions = []
        
        # Get role permissions
        role_perms = self.db.query(Permission).join(RolePermission).filter(
            and_(
                RolePermission.role_id == user.role_id,
                Permission.is_active == True
            )
        ).all()
        
        for perm in role_perms:
            permissions.append({
                "name": perm.name,
                "description": perm.description,
                "resource_type": perm.resource_type.value,
                "permission_type": perm.permission_type.value,
                "source": "role",
                "granted": True
            })
        
        # Get direct user permissions (these override role permissions)
        user_perms = self.db.query(UserPermission, Permission).join(Permission).filter(
            and_(
                UserPermission.user_id == user_id,
                Permission.is_active == True,
                or_(
                    UserPermission.expires_at.is_(None),
                    UserPermission.expires_at > datetime.utcnow()
                )
            )
        ).order_by(UserPermission.granted_at.desc()).all()
        
        # Group by permission to get latest grant/revoke
        user_perm_dict = {}
        for user_perm, perm in user_perms:
            if perm.name not in user_perm_dict:
                user_perm_dict[perm.name] = {
                    "name": perm.name,
                    "description": perm.description,
                    "resource_type": perm.resource_type.value,
                    "permission_type": perm.permission_type.value,
                    "source": "direct",
                    "granted": user_perm.is_granted,
                    "conditions": user_perm.conditions,
                    "expires_at": user_perm.expires_at
                }
        
        # Add direct permissions (they override role permissions)
        permissions.extend(user_perm_dict.values())
        
        return permissions
    
    def log_action(self, user_id: int, action: str, resource_type: str,
                   resource_id: str, old_values: Optional[Dict] = None,
                   new_values: Optional[Dict] = None, ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None, branch_id: Optional[int] = None):
        """Log user action for audit trail"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent,
            branch_id=branch_id
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    def get_audit_logs(self, user_id: Optional[int] = None, 
                      resource_type: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      limit: int = 100) -> List[AuditLog]:
        """Get audit logs with filters"""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

# Permission decorator for FastAPI endpoints
from functools import wraps
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def require_permission(permission_name: str, resource_id_param: Optional[str] = None):
    """Decorator to require specific permission for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and db from kwargs
            request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)
            db = kwargs.get('db') or next((arg for arg in args if hasattr(arg, 'query')), None)
            
            if not request or not db:
                raise HTTPException(status_code=500, detail="Internal server error")
            
            # Get user from request (assumes authentication middleware sets this)
            user_id = getattr(request.state, 'user_id', None)
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Build context
            context = {
                "branch_id": getattr(request.state, 'branch_id', None),
                "ip_address": request.client.host if request.client else None,
            }
            
            # Add resource_id if specified
            if resource_id_param and resource_id_param in kwargs:
                context["resource_id"] = kwargs[resource_id_param]
            
            # Check permission
            permission_service = PermissionService(db)
            if not permission_service.check_permission(user_id, permission_name, context=context):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Log the action
            permission_service.log_action(
                user_id=user_id,
                action=f"access_{func.__name__}",
                resource_type=permission_name.split('_')[0] if '_' in permission_name else "unknown",
                resource_id=str(context.get("resource_id", "")),
                ip_address=context.get("ip_address"),
                user_agent=request.headers.get("user-agent"),
                branch_id=context.get("branch_id")
            )
            
            # Call the function, handling both sync and async
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Simple permission decorator for FastAPI endpoints
def simple_require_permission(permission_name: str):
    """Simple decorator to require specific permission for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user and db from kwargs
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(status_code=500, detail="Authentication or database connection required")
            
            # Get user ID
            user_id = getattr(current_user, 'id', None) if hasattr(current_user, 'id') else current_user.get('id') if isinstance(current_user, dict) else None
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid user authentication")
            
            # Check permission using PermissionService
            permission_service = PermissionService(db)
            
            # Special case for admin users - check for wildcard permission
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.role and user.role.name == "Admin":
                # Admin role gets access to everything
                if hasattr(func, '__call__'):
                    import asyncio
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                return await func(*args, **kwargs)
            
            # Check specific permission
            if not permission_service.check_permission(user_id, permission_name):
                raise HTTPException(status_code=403, detail=f"Insufficient permissions: {permission_name} required")
            
            # Call the function, handling both sync and async
            if hasattr(func, '__call__'):
                import asyncio
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
