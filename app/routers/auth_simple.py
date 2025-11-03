"""
Simple Authentication Router for Unified Database
Works with the merged TSH Online Store + ERP database schema
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt

from app.db.database import get_db

# JWT Settings
SECRET_KEY = "CHANGE_THIS_TO_STRONG_RANDOM_KEY_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Simple login endpoint that works with unified database.
    Uses direct SQL queries to avoid model complications.
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
