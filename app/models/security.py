"""
Security Models for Enhanced Authentication and Authorization
Includes: Login attempts, MFA, Session management, Token blacklist, Password history
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

from app.db.database import Base


class LoginAttempt(Base):
    """Track login attempts for rate limiting and account lockout"""
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500))
    success = Column(Boolean, default=False)
    failure_reason = Column(String(255))
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Geolocation data (optional)
    country = Column(String(100))
    city = Column(String(100))


class AccountLockout(Base):
    """Track locked accounts due to failed login attempts"""
    __tablename__ = "account_lockouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    locked_at = Column(DateTime, default=datetime.utcnow)
    locked_until = Column(DateTime, nullable=False)
    reason = Column(String(255), default="Too many failed login attempts")
    unlocked_at = Column(DateTime)
    unlocked_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    unlocker = relationship("User", foreign_keys=[unlocked_by])


class TokenBlacklist(Base):
    """Blacklist for revoked JWT tokens (proper logout)"""
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    reason = Column(String(255), default="User logout")

    # Relationships
    user = relationship("User")


class MFAMethod(enum.Enum):
    """Multi-Factor Authentication methods"""
    TOTP = "totp"  # Time-based OTP (Google Authenticator, Authy)
    SMS = "sms"  # SMS code
    EMAIL = "email"  # Email code
    BACKUP_CODES = "backup_codes"  # Backup recovery codes


class UserMFA(Base):
    """Multi-Factor Authentication configuration for users"""
    __tablename__ = "user_mfa"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    is_enabled = Column(Boolean, default=False)
    method = Column(Enum(MFAMethod), default=MFAMethod.TOTP)

    # TOTP settings
    totp_secret = Column(String(32))  # Base32 encoded secret
    totp_verified = Column(Boolean, default=False)

    # SMS/Email settings
    phone_number = Column(String(20))
    phone_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)

    # Backup codes (hashed)
    backup_codes = Column(Text)  # JSON array of hashed codes

    # Metadata
    enabled_at = Column(DateTime)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="mfa_config")


class MFAVerification(Base):
    """Track MFA verification attempts"""
    __tablename__ = "mfa_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    method = Column(Enum(MFAMethod), nullable=False)
    code = Column(String(10))  # Temporary code (hashed)
    success = Column(Boolean, default=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    attempted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User")


class UserSession(Base):
    """Track active user sessions across devices"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True)

    # Device information
    device_name = Column(String(255))
    device_type = Column(String(50))  # web, mobile, tablet
    device_id = Column(String(255))  # Unique device identifier
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Geolocation
    country = Column(String(100))
    city = Column(String(100))

    # Session state
    is_active = Column(Boolean, default=True)
    is_trusted = Column(Boolean, default=False)  # Remember this device
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    terminated_at = Column(DateTime)
    termination_reason = Column(String(255))

    # Relationships
    user = relationship("User", back_populates="sessions")


class PasswordHistory(Base):
    """Track password history to prevent reuse"""
    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")


class PasswordResetToken(Base):
    """Secure password reset tokens"""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    ip_address = Column(String(45))

    # Relationships
    user = relationship("User")


class EmailVerificationToken(Base):
    """Email verification tokens for new accounts"""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime)

    # Relationships
    user = relationship("User")


class TrustedDevice(Base):
    """Track and manage trusted devices"""
    __tablename__ = "trusted_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(String(255), nullable=False)
    device_name = Column(String(255))
    device_type = Column(String(50))
    device_fingerprint = Column(Text)  # JSON with device details

    is_trusted = Column(Boolean, default=True)
    trust_expires_at = Column(DateTime)

    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)

    # Relationships
    user = relationship("User")


# SecurityEvent class has been moved to app/models/advanced_security.py
# as AdvancedSecurityEvent to avoid mapper conflicts
# See: AdvancedSecurityEvent class which maps to "security_events" table

# Backwards compatibility alias - import AdvancedSecurityEvent and alias as SecurityEvent
from app.models.advanced_security import AdvancedSecurityEvent as SecurityEvent

__all__ = [
    "LoginAttempt",
    "AccountLockout",
    "TokenBlacklist",
    "MFAMethod",
    "UserMFA",
    "MFAVerification",
    "UserSession",
    "PasswordHistory",
    "PasswordResetToken",
    "EmailVerificationToken",
    "TrustedDevice",
    "SecurityEvent",  # Re-exported from advanced_security for backwards compatibility
]
