"""
TSH NeuroLink - JWT Authentication Middleware
Integrates with TSH ERP authentication system
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import User, TokenData


# Security scheme for JWT bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user

    This middleware:
    1. Extracts JWT from Authorization header
    2. Validates token signature
    3. Fetches user from TSH ERP database
    4. Verifies user is active
    5. Returns User object for route handlers

    Usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.full_name}"}
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # Extract user_id from token
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Extract additional claims
        email: str = payload.get("email")
        role: str = payload.get("role", "user")
        branch_id: Optional[int] = payload.get("branch_id")

    except JWTError:
        raise credentials_exception

    # Fetch user from database to verify they still exist and are active
    query = text("""
        SELECT
            u.id,
            u.email,
            u.full_name,
            r.name as role,
            u.branch_id,
            u.is_active
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.id = :user_id
    """)

    result = await db.execute(query, {"user_id": user_id})
    user_row = result.fetchone()

    if user_row is None:
        raise credentials_exception

    # Convert to User object
    user = User(
        id=user_row.id,
        email=user_row.email,
        full_name=user_row.full_name,
        role=user_row.role or "user",
        branch_id=user_row.branch_id,
        is_active=user_row.is_active
    )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Convenience dependency that ensures user is active

    Usage:
        @app.get("/items")
        async def get_items(user: User = Depends(get_current_active_user)):
            ...
    """
    return current_user


def require_role(*allowed_roles: str):
    """
    Role-based access control decorator

    Usage:
        @app.get("/admin/dashboard")
        async def admin_dashboard(
            user: User = Depends(require_role("admin", "superadmin"))
        ):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token

    Args:
        data: Payload to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Usage:
        token = create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role}
        )
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)

    to_encode.update({"exp": expire})

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


# Optional: Create a dependency for checking permissions
async def has_permission(permission: str):
    """
    Permission-based access control

    Usage:
        @app.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            current_user: User = Depends(has_permission("users.delete"))
        ):
            ...
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # Query user permissions from database
        # This is a placeholder - implement based on your permissions system
        # For now, admins have all permissions
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user

    return permission_checker
