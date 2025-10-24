"""
RLS-Aware Database Dependency for FastAPI
==========================================

This module provides database session dependencies that automatically set
PostgreSQL Row-Level Security (RLS) context based on the authenticated user.

Usage:
------
from app.db.rls_dependency import get_db_with_rls, get_current_user_with_rls

# In FastAPI endpoint
@router.get("/customers")
async def list_customers(
    db: Session = Depends(get_db_with_rls),
    current_user: User = Depends(get_current_user_with_rls)
):
    # RLS context is automatically set
    # Query will only return customers accessible to current_user
    customers = db.query(Customer).all()
    return customers
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Optional
import logging

from app.db.database import SessionLocal
from app.db.rls_context import set_rls_context
from app.models.user import User
from app.services.auth_service import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_db():
    """
    Basic database session dependency (without RLS context).
    Use this for public endpoints that don't require authentication.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate the current user from JWT token.

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    return user


def get_db_with_rls(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Session:
    """
    Database session dependency with automatic RLS context setting.

    This dependency:
    1. Validates the JWT token
    2. Retrieves the user information
    3. Sets PostgreSQL RLS session variables
    4. Returns the database session

    All queries in this session will be automatically filtered by RLS policies.

    Usage:
        @router.get("/data")
        async def get_data(db: Session = Depends(get_db_with_rls)):
            # All queries automatically filtered by RLS
            return db.query(Model).all()
    """
    try:
        # Get current user
        user = get_current_user_from_token(credentials, db)

        # Set RLS context
        set_rls_context(
            db=db,
            user_id=user.id,
            role_name=user.role.name if user.role else None,
            tenant_id=user.tenant_id,
            branch_id=user.branch_id,
            warehouse_id=user.warehouse_id
        )

        logger.debug(f"✅ RLS context set for user {user.id} ({user.email})")

        return db

    except Exception as e:
        logger.error(f"❌ Failed to setup RLS context: {e}")
        raise


def get_current_user_with_rls(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user AND set RLS context.

    Use this when you need both the user object and RLS protection.

    Usage:
        @router.get("/profile")
        async def get_profile(
            current_user: User = Depends(get_current_user_with_rls),
            db: Session = Depends(get_db)
        ):
            # RLS context already set
            # current_user contains authenticated user data
            return current_user
    """
    try:
        # Get current user
        user = get_current_user_from_token(credentials, db)

        # Set RLS context
        set_rls_context(
            db=db,
            user_id=user.id,
            role_name=user.role.name if user.role else None,
            tenant_id=user.tenant_id,
            branch_id=user.branch_id,
            warehouse_id=user.warehouse_id
        )

        logger.debug(f"✅ RLS context set for user {user.id} ({user.email})")

        return user

    except Exception as e:
        logger.error(f"❌ Failed to setup RLS context: {e}")
        raise


# Optional: RLS context manager for manual control
class RLSContextManager:
    """
    Context manager for manual RLS control within endpoints.

    Usage:
        @router.post("/admin-action")
        async def admin_action(
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            # Query as specific user (useful for admin impersonation)
            with RLSContextManager(db, user_id=123):
                customers = db.query(Customer).all()
                # Sees only what user 123 can see

            # Back to current user context
            customers_all = db.query(Customer).all()
    """

    def __init__(self, db: Session, user_id: int, **kwargs):
        self.db = db
        self.user_id = user_id
        self.kwargs = kwargs
        self._original_context = {}

    def __enter__(self):
        set_rls_context(self.db, self.user_id, **self.kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # RLS context is transaction-scoped, will reset on commit/rollback
        pass
