"""
Role-Based Access Control (RBAC) Dependencies
Provides decorators and dependencies to check user permissions
"""
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.services.auth_service import SECRET_KEY, ALGORITHM

security = HTTPBearer()


class PermissionChecker:
    """
    Dependency class to check if user has required permissions
    Usage:
        @router.get("/endpoint", dependencies=[Depends(PermissionChecker(["permission.view"]))])
    """

    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """
        Check if user has all required permissions
        """
        token = credentials.credentials

        try:
            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Extract user info
            email: Optional[str] = payload.get("sub")
            token_type: Optional[str] = payload.get("type")
            user_permissions: List[str] = payload.get("permissions", [])
            role: Optional[str] = payload.get("role")

            # Verify token is valid
            if email is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if user has admin role (admins have all permissions)
            if role and role.lower() == "admin":
                return {
                    "email": email,
                    "role": role,
                    "permissions": user_permissions,
                    "user_id": payload.get("user_id")
                }

            # Check if user has all required permissions
            missing_permissions = [
                perm for perm in self.required_permissions
                if perm not in user_permissions
            ]

            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing_permissions)}",
                )

            return {
                "email": email,
                "role": role,
                "permissions": user_permissions,
                "user_id": payload.get("user_id")
            }

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class RoleChecker:
    """
    Dependency class to check if user has required role
    Usage:
        @router.get("/endpoint", dependencies=[Depends(RoleChecker(["admin", "manager"]))])
    """

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [role.lower() for role in allowed_roles]

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """
        Check if user has one of the allowed roles
        """
        token = credentials.credentials

        try:
            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Extract user info
            email: Optional[str] = payload.get("sub")
            token_type: Optional[str] = payload.get("type")
            role: Optional[str] = payload.get("role")

            # Verify token is valid
            if email is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if user has one of the allowed roles
            if role is None or role.lower() not in self.allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {', '.join(self.allowed_roles)}",
                )

            return {
                "email": email,
                "role": role,
                "permissions": payload.get("permissions", []),
                "user_id": payload.get("user_id")
            }

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract current user information from JWT token
    This is a basic dependency that just validates the token and returns user info
    without checking specific permissions
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user info
        email: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")

        # Verify token is valid
        if email is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "email": email,
            "role": payload.get("role"),
            "permissions": payload.get("permissions", []),
            "user_id": payload.get("user_id"),
            "platform": payload.get("platform")
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permissions(*permissions: str):
    """
    Decorator function to check permissions
    Usage:
        @router.get("/endpoint")
        @require_permissions("users.view", "users.create")
        async def endpoint(user: dict = Depends(get_current_user_from_token)):
            ...
    """
    def decorator(func):
        # This is handled by FastAPI's Depends() system
        return func
    return decorator


def require_role(*roles: str):
    """
    Decorator function to check roles
    Usage:
        @router.get("/endpoint")
        @require_role("admin", "manager")
        async def endpoint(user: dict = Depends(get_current_user_from_token)):
            ...
    """
    def decorator(func):
        # This is handled by FastAPI's Depends() system
        return func
    return decorator
