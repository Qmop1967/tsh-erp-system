"""
Centralized Authentication Dependencies
Single source of truth for authentication logic across the application.

This module consolidates authentication dependencies previously scattered across:
- app.routers.auth (DEPRECATED)
- app.routers.auth_simple (DEPRECATED)
- app.routers.auth_enhanced (current implementation)

Migration: All routers should import from this module instead of individual router files.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.services.enhanced_auth_security import TokenBlacklistService
from app.models.user import User

# Import structured logging
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


def get_user_permissions(user: User) -> List[str]:
    """
    Get permissions based on user role

    Centralized permission mapping - SINGLE SOURCE OF TRUTH

    Args:
        user: User object with role relationship

    Returns:
        List of permission strings

    Note:
        This function replaces duplicated logic in:
        - app.routers.auth.py:40
        - app.routers.auth_enhanced.py:41
    """
    if not user.role:
        return []

    role_name = user.role.name.lower()

    # Normalize role names to handle variations
    # Map "Travel Salesperson", "Sales", "Salesperson" to same permissions
    if 'sales' in role_name or 'salesperson' in role_name:
        role_name = 'salesperson'

    # Define permissions for each role
    permissions = {
        'admin': [
            'admin',
            'dashboard.view',
            'users.view',
            'users.create',
            'users.update',
            'users.delete',
            'hr.view',
            'branches.view',
            'warehouses.view',
            'items.view',
            'products.view',
            'inventory.view',
            'customers.view',
            'vendors.view',
            'sales.view',
            'sales.create',
            'purchase.view',
            'accounting.view',
            'pos.view',
            'cashflow.view',
            'migration.view',
            'reports.view',
            'settings.view',
            'security.view',
            'mfa.setup',
            'sessions.manage'
        ],
        'manager': [
            'dashboard.view',
            'users.view',
            'hr.view',
            'branches.view',
            'warehouses.view',
            'items.view',
            'products.view',
            'inventory.view',
            'customers.view',
            'vendors.view',
            'sales.view',
            'sales.create',
            'purchase.view',
            'accounting.view',
            'pos.view',
            'cashflow.view',
            'reports.view'
        ],
        'salesperson': [
            'dashboard.view',
            'customers.view',
            'customers.create',
            'customers.update',
            'sales.view',
            'sales.create',
            'sales.update',
            'products.view',
            'inventory.view',
            'pos.view',
            'cashflow.view',
            'reports.view'
        ],
        'inventory': [
            'dashboard.view',
            'items.view',
            'items.create',
            'items.update',
            'products.view',
            'inventory.view',
            'inventory.create',
            'inventory.update',
            'warehouses.view'
        ],
        'accountant': [
            'dashboard.view',
            'accounting.view',
            'accounting.create',
            'accounting.update',
            'cashflow.view',
            'reports.view',
            'sales.view',
            'purchase.view'
        ],
        'cashier': [
            'dashboard.view',
            'pos.view',
            'pos.create',
            'sales.view',
            'sales.create',
            'customers.view',
            'products.view'
        ],
        'hr': [
            'dashboard.view',
            'hr.view',
            'hr.create',
            'hr.update',
            'users.view',
            'reports.view'
        ],
        'viewer': [
            'dashboard.view',
            'reports.view'
        ]
    }

    return permissions.get(role_name, ['dashboard.view'])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Enhanced dependency to get current authenticated user with security checks

    This is the PRODUCTION-READY implementation with:
    - Token validation
    - Token blacklist checking
    - Comprehensive error handling
    - Structured logging

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        User object if authentication successful

    Raises:
        HTTPException: 401 if token invalid or revoked

    Note:
        This replaces get_current_user from:
        - app.routers.auth.py:373 (basic version)
        - app.routers.auth_enhanced.py:714 (enhanced version)
    """
    token = credentials.credentials

    # Check if token is blacklisted (revoked tokens)
    if TokenBlacklistService.is_token_blacklisted(db, token):
        logger.warning(
            "token_blacklisted_access_attempt",
            token_prefix=token[:20] if token else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Validate token and get user
    user = AuthService.get_current_user(db, token)
    if not user:
        logger.warning(
            "invalid_token_access_attempt",
            token_prefix=token[:20] if token else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is active
    if not user.is_active:
        logger.warning(
            "inactive_user_access_attempt",
            user_email=user.email,
            user_id=user.id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive. Contact administrator."
        )

    return user


async def get_current_user_async(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Async version of get_current_user for async route handlers

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        User object if authentication successful

    Raises:
        HTTPException: 401 if token invalid or revoked
    """
    # Async version uses the same logic
    return get_current_user(credentials, db)


# Export commonly used dependencies
__all__ = [
    'get_current_user',
    'get_current_user_async',
    'get_user_permissions',
    'security'
]
