"""
Centralized Dependencies Module

This module provides easy imports for all authentication and authorization dependencies.
"""

from app.dependencies.auth import (
    get_current_user,
    get_current_user_async,
    get_user_permissions,
    security
)

from app.dependencies.rbac import (
    PermissionChecker,
    RoleChecker,
    get_current_user_from_token,
    require_permissions,
    require_role
)

__all__ = [
    # Auth dependencies
    'get_current_user',
    'get_current_user_async',
    'get_user_permissions',
    'security',
    # RBAC dependencies
    'PermissionChecker',
    'RoleChecker',
    'get_current_user_from_token',
    'require_permissions',
    'require_role',
]
