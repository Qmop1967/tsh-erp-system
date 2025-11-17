"""
Magic Link Authentication Router
================================
Provides passwordless authentication via email magic links.

Endpoints:
- POST /auth/magic-link/request - Request a magic link
- GET /auth/magic-link/verify - Verify magic link and get JWT token
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import secrets
import psycopg2
import os
import json

from app.services.auth_service import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from jose import jwt

router = APIRouter(prefix="/auth/magic-link", tags=["Magic Link Authentication"])

# Configuration
MAGIC_LINK_EXPIRE_MINUTES = 15
BASE_URL = "https://erp.tsh.sale"

# Database connection helper (bypasses SQLAlchemy to avoid greenlet issues)
def get_db_connection():
    """Get a raw psycopg2 connection to bypass SQLAlchemy async issues"""
    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/erp_db")
    # Remove asyncpg driver prefix if present
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    # Parse the URL
    from urllib.parse import urlparse, unquote
    parsed = urlparse(db_url)
    print(f"Connecting to database: host={parsed.hostname}, port={parsed.port}, db={parsed.path.lstrip('/')}, user={parsed.username}")
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip('/'),
        user=unquote(parsed.username) if parsed.username else None,
        password=unquote(parsed.password) if parsed.password else None
    )


# Pydantic schemas
class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    success: bool
    message: str


class TokenVerifyResponse(BaseModel):
    success: bool
    access_token: str = None
    token_type: str = "bearer"
    user: dict = None
    error: str = None


def generate_magic_link_token() -> str:
    """Generate a secure random token for magic link"""
    return secrets.token_urlsafe(32)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/request", response_model=MagicLinkResponse)
async def request_magic_link(
    request_data: MagicLinkRequest,
    request: Request
):
    """
    Request a magic link for passwordless login.

    - Checks if email exists in database
    - Creates a one-time use token valid for 15 minutes
    - Returns the magic link URL (in production, this would be emailed)
    """
    email = request_data.email.lower().strip()
    ip_address = request.client.host if request.client else "unknown"

    # Use raw psycopg2 to avoid SQLAlchemy greenlet issues
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if user exists using raw SQL
        cursor.execute(
            "SELECT id, email, full_name, name FROM users WHERE email = %s AND is_active = true",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            # For security, don't reveal if email exists
            cursor.close()
            conn.close()
            return MagicLinkResponse(
                success=True,
                message="If the email exists and is active, a magic link has been sent."
            )

        user_id, user_email, full_name, name = user

        # Generate token
        token = generate_magic_link_token()
        expires_at = datetime.utcnow() + timedelta(minutes=MAGIC_LINK_EXPIRE_MINUTES)

        # Invalidate any existing unused tokens for this email
        cursor.execute(
            "UPDATE magic_link_tokens SET used = TRUE WHERE email = %s AND used = FALSE",
            (email,)
        )

        # Create new token
        cursor.execute(
            "INSERT INTO magic_link_tokens (email, token, expires_at) VALUES (%s, %s, %s)",
            (email, token, expires_at)
        )
        conn.commit()

        # Generate magic link URL
        magic_link = f"{BASE_URL}/auth/magic-link/verify?token={token}"

        # Log the event
        print(f"Magic link created for user: {email} (ID: {user_id})")
        print(f"MAGIC LINK FOR {email}: {magic_link}")

        return MagicLinkResponse(
            success=True,
            message=f"Magic link created. Link: {magic_link}"
        )

    except Exception as e:
        conn.rollback()
        print(f"Error creating magic link for {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create magic link"
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/verify")
async def verify_magic_link(
    token: str = Query(..., description="Magic link token"),
    request: Request = None
):
    """
    Verify a magic link token and return JWT access token.

    - Validates the token exists and is not expired
    - Marks token as used (one-time use)
    - Returns JWT access token for authentication
    """
    ip_address = request.client.host if request and request.client else "unknown"

    # Use raw psycopg2 to avoid SQLAlchemy greenlet issues
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Find the token
        cursor.execute(
            "SELECT id, email, expires_at, used FROM magic_link_tokens WHERE token = %s",
            (token,)
        )
        magic_token = cursor.fetchone()

        if not magic_token:
            print(f"Invalid magic link token attempted from IP: {ip_address}")
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid magic link token"
            )

        token_id, email, expires_at, used = magic_token

        # Check if already used
        if used:
            print(f"Reuse attempt of magic link token for {email} from IP: {ip_address}")
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Magic link has already been used"
            )

        # Check if expired
        if hasattr(expires_at, 'replace'):
            expires_at_naive = expires_at.replace(tzinfo=None)
        else:
            expires_at_naive = expires_at
        if datetime.utcnow() > expires_at_naive:
            print(f"Expired magic link token for {email} from IP: {ip_address}")
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Magic link has expired"
            )

        # Mark token as used
        cursor.execute(
            "UPDATE magic_link_tokens SET used = TRUE WHERE id = %s",
            (token_id,)
        )

        # Get user info
        cursor.execute(
            "SELECT id, email, full_name, name, role_id, is_active FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            conn.rollback()
            print(f"User not found for magic link email: {email}")
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )

        user_id, user_email, full_name, name, role_id, is_active = user

        if not is_active:
            conn.rollback()
            print(f"Disabled user attempted magic link login: {email}")
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.utcnow(), user_id)
        )
        conn.commit()

        # Create JWT access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user_id),
                "email": user_email,
                "role_id": role_id
            },
            expires_delta=access_token_expires
        )

        print(f"Magic link authentication successful for user: {email} (ID: {user_id})")

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user_email,
                "full_name": full_name or name,
                "role_id": role_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error verifying magic link: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify magic link"
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/test")
async def test_magic_link_endpoint():
    """
    Test endpoint to verify magic link router is working.
    """
    return {
        "status": "ok",
        "message": "Magic link authentication router is active",
        "endpoints": {
            "request": "POST /auth/magic-link/request",
            "verify": "GET /auth/magic-link/verify?token=<token>"
        }
    }
