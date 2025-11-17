#!/usr/bin/env python3
"""
Magic Link Authentication Service for TSH ERP
=============================================

Provides passwordless authentication via magic links sent to email.
Works with the production database schema (UUID-based).

Author: TSH ERP Team
Date: November 16, 2025
"""

import os
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://khaleel:Zcbbm.97531tsh@localhost:5432/tsh_erp")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
MAGIC_LINK_EXPIRE_MINUTES = 15  # Magic link valid for 15 minutes

# Email configuration (using Resend or SMTP)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@tsh.sale")

# Base URL for magic links
BASE_URL = os.getenv("BASE_URL", "https://erp.tsh.sale")

# Database setup
engine = create_engine(DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class MagicLinkService:
    """Service for handling magic link authentication"""

    @staticmethod
    def generate_magic_link_token() -> str:
        """Generate a secure random token for magic link"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_magic_link(email: str) -> Dict[str, Any]:
        """
        Create a magic link token for the given email.

        Returns:
            dict with token and magic link URL
        """
        db = SessionLocal()
        try:
            # Check if user exists
            user_query = text("SELECT id, email, full_name FROM users WHERE email = :email")
            user = db.execute(user_query, {"email": email.lower().strip()}).fetchone()

            if not user:
                # For security, don't reveal if email exists
                return {
                    "success": True,
                    "message": "If the email exists, a magic link has been sent.",
                    "token": None,
                    "magic_link": None
                }

            # Generate token
            token = MagicLinkService.generate_magic_link_token()
            expires_at = datetime.utcnow() + timedelta(minutes=MAGIC_LINK_EXPIRE_MINUTES)

            # Invalidate any existing unused tokens for this email
            invalidate_query = text("""
                UPDATE magic_link_tokens
                SET used = TRUE
                WHERE email = :email AND used = FALSE
            """)
            db.execute(invalidate_query, {"email": email})

            # Create new token
            insert_query = text("""
                INSERT INTO magic_link_tokens (email, token, expires_at)
                VALUES (:email, :token, :expires_at)
            """)
            db.execute(insert_query, {
                "email": email,
                "token": token,
                "expires_at": expires_at
            })
            db.commit()

            # Generate magic link URL
            magic_link = f"{BASE_URL}/auth/magic-link/verify?token={token}"

            return {
                "success": True,
                "message": "Magic link created successfully",
                "token": token,
                "magic_link": magic_link,
                "expires_at": expires_at.isoformat(),
                "user_name": user[2] or user[1]  # full_name or email
            }

        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create magic link: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def verify_magic_link(token: str) -> Dict[str, Any]:
        """
        Verify a magic link token and return JWT access token.

        Returns:
            dict with access_token and user info
        """
        db = SessionLocal()
        try:
            # Find the token
            token_query = text("""
                SELECT id, email, expires_at, used
                FROM magic_link_tokens
                WHERE token = :token
            """)
            magic_token = db.execute(token_query, {"token": token}).fetchone()

            if not magic_token:
                return {
                    "success": False,
                    "error": "Invalid magic link token"
                }

            token_id, email, expires_at, used = magic_token

            # Check if already used
            if used:
                return {
                    "success": False,
                    "error": "Magic link has already been used"
                }

            # Check if expired
            if datetime.utcnow() > expires_at.replace(tzinfo=None):
                return {
                    "success": False,
                    "error": "Magic link has expired"
                }

            # Mark token as used
            update_query = text("""
                UPDATE magic_link_tokens
                SET used = TRUE
                WHERE id = :token_id
            """)
            db.execute(update_query, {"token_id": token_id})

            # Get user info
            user_query = text("""
                SELECT id, email, full_name, role_id, is_active
                FROM users
                WHERE email = :email
            """)
            user = db.execute(user_query, {"email": email}).fetchone()

            if not user:
                db.rollback()
                return {
                    "success": False,
                    "error": "User not found"
                }

            user_id, user_email, full_name, role_id, is_active = user

            if not is_active:
                db.rollback()
                return {
                    "success": False,
                    "error": "User account is disabled"
                }

            db.commit()

            # Create JWT access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = MagicLinkService.create_access_token(
                data={
                    "sub": str(user_id),
                    "email": user_email,
                    "role_id": role_id
                },
                expires_delta=access_token_expires
            )

            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user_id),
                    "email": user_email,
                    "full_name": full_name,
                    "role_id": role_id
                }
            }

        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to verify magic link: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def send_magic_link_email(email: str, magic_link: str, user_name: str = None) -> bool:
        """
        Send magic link email to user.

        Uses Resend API if available, otherwise falls back to SMTP.
        """
        subject = "تسجيل الدخول إلى TSH ERP - رابط سحري"

        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; text-align: right; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 15px 32px;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .warning {{ color: #ff6600; font-size: 14px; }}
                .footer {{ color: #888; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>مرحباً {user_name or email}</h2>
                <p>لقد طلبت تسجيل الدخول إلى نظام TSH ERP.</p>
                <p>اضغط على الزر أدناه لتسجيل الدخول:</p>

                <a href="{magic_link}" class="button">تسجيل الدخول</a>

                <p class="warning">⚠️ هذا الرابط صالح لمدة 15 دقيقة فقط ويمكن استخدامه مرة واحدة.</p>

                <p>أو انسخ والصق هذا الرابط في متصفحك:</p>
                <code style="word-break: break-all; background: #f5f5f5; padding: 10px; display: block;">
                    {magic_link}
                </code>

                <p class="footer">
                    إذا لم تطلب هذا الرابط، يرجى تجاهل هذا البريد الإلكتروني.<br>
                    TSH ERP System - نظام إدارة الأعمال
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        مرحباً {user_name or email}

        لقد طلبت تسجيل الدخول إلى نظام TSH ERP.

        اضغط على الرابط أدناه لتسجيل الدخول:
        {magic_link}

        ⚠️ هذا الرابط صالح لمدة 15 دقيقة فقط ويمكن استخدامه مرة واحدة.

        إذا لم تطلب هذا الرابط، يرجى تجاهل هذا البريد الإلكتروني.

        TSH ERP System
        """

        # Try Resend API first
        if RESEND_API_KEY:
            try:
                import requests
                response = requests.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": FROM_EMAIL,
                        "to": [email],
                        "subject": subject,
                        "html": html_content,
                        "text": text_content
                    }
                )
                if response.status_code == 200:
                    print(f"✅ Email sent via Resend to {email}")
                    return True
                else:
                    print(f"⚠️ Resend failed: {response.text}")
            except Exception as e:
                print(f"⚠️ Resend error: {str(e)}")

        # Fallback to SMTP
        if SMTP_USER and SMTP_PASSWORD:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = FROM_EMAIL
                msg["To"] = email

                part1 = MIMEText(text_content, "plain", "utf-8")
                part2 = MIMEText(html_content, "html", "utf-8")
                msg.attach(part1)
                msg.attach(part2)

                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                    server.starttls()
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.sendmail(FROM_EMAIL, email, msg.as_string())

                print(f"✅ Email sent via SMTP to {email}")
                return True
            except Exception as e:
                print(f"⚠️ SMTP error: {str(e)}")

        print(f"❌ Could not send email to {email} - no email service configured")
        return False


def test_magic_link_flow():
    """Test the magic link authentication flow"""
    print("\n" + "=" * 80)
    print("MAGIC LINK AUTHENTICATION TEST")
    print("=" * 80)

    # Test with your email
    test_email = "kha89ahm@gmail.com"

    print(f"\n1. Creating magic link for: {test_email}")
    result = MagicLinkService.create_magic_link(test_email)
    print(f"   Result: {result}")

    if result.get("token"):
        print(f"\n2. Magic Link URL:")
        print(f"   {result['magic_link']}")

        print(f"\n3. Verifying magic link token...")
        verify_result = MagicLinkService.verify_magic_link(result["token"])
        print(f"   Result: {verify_result}")

        if verify_result.get("success"):
            print(f"\n✅ Authentication successful!")
            print(f"   User: {verify_result['user']['email']}")
            print(f"   Access Token: {verify_result['access_token'][:50]}...")
        else:
            print(f"\n❌ Authentication failed: {verify_result.get('error')}")
    else:
        print(f"\n❌ Failed to create magic link")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_magic_link_flow()
