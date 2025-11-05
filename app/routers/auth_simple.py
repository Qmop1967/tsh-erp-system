"""
DEPRECATED: Simple Authentication Router for Unified Database

⚠️ WARNING: This router is deprecated and will be removed in v2.0.0
Please use /api/auth/login from auth_enhanced.py instead.

This router has been replaced by auth_enhanced.py which provides:
- Enhanced security (rate limiting, account lockout, MFA)
- Session management
- Security event logging
- No hardcoded secrets

Migration: Update your API calls from /api/auth-simple/login to /api/auth/login
"""
import warnings

warnings.warn(
    "auth_simple router is deprecated. Use auth_enhanced instead. "
    "This router will be removed in v2.0.0",
    DeprecationWarning,
    stacklevel=2
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt

from app.db.database import get_db
from app.core.config import settings

# JWT Settings - now using environment variables instead of hardcoded secrets
SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes

router = APIRouter(prefix="/api/auth-simple", tags=["Simple Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth-simple/token")


# Pydantic Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserInfo(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    is_active: bool = True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify bcrypt password"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=LoginResponse, deprecated=True)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    ⚠️ DEPRECATED: Simple login endpoint that works with unified database.

    **This endpoint is deprecated and will be removed in v2.0.0**

    Please migrate to: POST /api/auth/login

    The new endpoint provides enhanced security features:
    - Rate limiting (prevents brute force attacks)
    - Account lockout (after failed attempts)
    - MFA support (optional two-factor authentication)
    - Session management (track active sessions)
    - Security event logging (audit trail)

    Migration is simple - just change the endpoint URL:
    - Old: POST /api/auth-simple/login
    - New: POST /api/auth/login

    Request/response format remains the same.
    """
    try:
        # Query user from public.users table
        result = db.execute(
            """
            SELECT
                u.id, u.email, u.name, u.role_id, u.branch_id, u.is_active,
                au.encrypted_password
            FROM public.users u
            LEFT JOIN auth.users au ON u.id = au.id
            WHERE u.email = :email
            LIMIT 1
            """,
            {"email": login_data.email}
        )
        user_row = result.fetchone()

        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        user_id, email, name, role_id, branch_id, is_active, encrypted_password = user_row

        # Check if user is active
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Verify password (from auth.users)
        if not encrypted_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password not set for user"
            )

        if not verify_password(login_data.password, encrypted_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email, "user_id": str(user_id)},
            expires_delta=access_token_expires
        )

        # Update last_login
        db.execute(
            "UPDATE public.users SET last_login = NOW() WHERE id = :user_id",
            {"user_id": user_id}
        )
        db.commit()

        return LoginResponse(
            access_token=access_token,
            user={
                "id": str(user_id),
                "email": email,
                "name": name or email.split('@')[0],
                "role_id": role_id,
                "branch_id": branch_id,
                "is_active": is_active
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/token")
async def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token endpoint"""
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    return await login(login_data, db)


@router.get("/me", response_model=UserInfo)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user info from token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Get user from database
    result = db.execute(
        """
        SELECT id, email, name, role_id, branch_id, is_active
        FROM public.users
        WHERE email = :email
        """,
        {"email": email}
    )
    user_row = result.fetchone()

    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_id, email, name, role_id, branch_id, is_active = user_row

    return UserInfo(
        id=str(user_id),
        email=email,
        name=name,
        role_id=role_id,
        branch_id=branch_id,
        is_active=is_active
    )
