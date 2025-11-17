"""
Enhanced Authentication Security Service
Handles: Rate limiting, account lockout, MFA, session management, token blacklist
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import os
import secrets
import hashlib

try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    print("Warning: pyotp not installed. MFA features will be limited.")

from app.models.security import (
    LoginAttempt, AccountLockout, TokenBlacklist,
    UserMFA, MFAVerification, UserSession,
    PasswordHistory, PasswordResetToken,
    EmailVerificationToken, TrustedDevice, SecurityEvent,
    MFAMethod
)
from app.models.user import User


# Configuration from environment
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
ACCOUNT_LOCKOUT_DURATION = int(os.getenv("ACCOUNT_LOCKOUT_DURATION", "900"))  # 15 minutes
PASSWORD_HISTORY_COUNT = int(os.getenv("PASSWORD_HISTORY_COUNT", "5"))
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
MAX_CONCURRENT_SESSIONS = int(os.getenv("MAX_CONCURRENT_SESSIONS", "3"))
MFA_TOKEN_VALIDITY = int(os.getenv("MFA_TOKEN_VALIDITY", "300"))  # 5 minutes


class RateLimitService:
    """Handle rate limiting and login attempt tracking"""

    @staticmethod
    def record_login_attempt(
        db: Session,
        email: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ) -> LoginAttempt:
        """Record a login attempt"""
        attempt = LoginAttempt(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # Log security event for failed attempts
        if not success:
            SecurityEventService.log_security_event(
                db=db,
                event_type="failed_login",
                severity="warning",
                description=f"Failed login attempt for {email}",
                ip_address=ip_address,
                user_agent=user_agent
            )

        return attempt

    @staticmethod
    def get_recent_failed_attempts(db: Session, email: str, minutes: int = 15) -> int:
        """Get count of failed login attempts in recent time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        count = db.query(LoginAttempt).filter(
            and_(
                LoginAttempt.email == email,
                LoginAttempt.success == False,
                LoginAttempt.attempted_at >= cutoff_time
            )
        ).count()
        return count

    @staticmethod
    def should_lockout_account(db: Session, email: str) -> bool:
        """Check if account should be locked due to too many failed attempts"""
        failed_attempts = RateLimitService.get_recent_failed_attempts(db, email)
        return failed_attempts >= MAX_LOGIN_ATTEMPTS

    @staticmethod
    def clear_failed_attempts(db: Session, email: str):
        """Clear failed login attempts after successful login"""
        # We don't delete them (for audit), but marking success=True on new record is enough
        pass


class AccountLockoutService:
    """Handle account lockout and unlocking"""

    @staticmethod
    def lockout_account(db: Session, user_id: int, reason: str = "Too many failed login attempts") -> AccountLockout:
        """Lock an account"""
        # Check if already locked
        existing_lockout = AccountLockoutService.get_active_lockout(db, user_id)
        if existing_lockout:
            return existing_lockout

        lockout = AccountLockout(
            user_id=user_id,
            locked_until=datetime.utcnow() + timedelta(seconds=ACCOUNT_LOCKOUT_DURATION),
            reason=reason
        )
        db.add(lockout)
        db.commit()
        db.refresh(lockout)

        # Log security event
        SecurityEventService.log_security_event(
            db=db,
            user_id=user_id,
            event_type="account_locked",
            severity="critical",
            description=f"Account locked: {reason}"
        )

        return lockout

    @staticmethod
    def get_active_lockout(db: Session, user_id: int) -> Optional[AccountLockout]:
        """Get active lockout for user"""
        return db.query(AccountLockout).filter(
            and_(
                AccountLockout.user_id == user_id,
                AccountLockout.is_active == True,
                AccountLockout.locked_until > datetime.utcnow()
            )
        ).first()

    @staticmethod
    def is_account_locked(db: Session, user_id: int) -> Tuple[bool, Optional[datetime]]:
        """
        Check if account is locked
        Returns: (is_locked, locked_until)
        """
        lockout = AccountLockoutService.get_active_lockout(db, user_id)
        if lockout:
            return True, lockout.locked_until
        return False, None

    @staticmethod
    def unlock_account(db: Session, user_id: int, unlocked_by: Optional[int] = None):
        """Unlock an account (manual or automatic)"""
        lockouts = db.query(AccountLockout).filter(
            and_(
                AccountLockout.user_id == user_id,
                AccountLockout.is_active == True
            )
        ).all()

        for lockout in lockouts:
            lockout.is_active = False
            lockout.unlocked_at = datetime.utcnow()
            lockout.unlocked_by = unlocked_by

        db.commit()


class TokenBlacklistService:
    """Handle JWT token blacklisting for proper logout"""

    @staticmethod
    def blacklist_token(
        db: Session,
        token: str,
        user_id: int,
        expires_at: datetime,
        reason: str = "User logout"
    ) -> TokenBlacklist:
        """Add token to blacklist"""
        blacklisted = TokenBlacklist(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason
        )
        db.add(blacklisted)
        db.commit()
        db.refresh(blacklisted)
        return blacklisted

    @staticmethod
    def is_token_blacklisted(db: Session, token: str) -> bool:
        """Check if token is blacklisted"""
        blacklisted = db.query(TokenBlacklist).filter(
            and_(
                TokenBlacklist.token == token,
                TokenBlacklist.expires_at > datetime.utcnow()
            )
        ).first()
        return blacklisted is not None

    @staticmethod
    def cleanup_expired_tokens(db: Session):
        """Remove expired tokens from blacklist (maintenance task)"""
        db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at <= datetime.utcnow()
        ).delete()
        db.commit()


class MFAService:
    """Handle Multi-Factor Authentication"""

    @staticmethod
    def setup_totp_for_user(db: Session, user_id: int) -> Tuple[str, str]:
        """
        Setup TOTP for user
        Returns: (secret, qr_code_uri)
        """
        if not PYOTP_AVAILABLE:
            raise ImportError("pyotp is required for MFA. Install with: pip install pyotp")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Generate TOTP secret
        secret = pyotp.random_base32()

        # Get or create MFA config
        mfa_config = db.query(UserMFA).filter(UserMFA.user_id == user_id).first()
        if not mfa_config:
            mfa_config = UserMFA(user_id=user_id)
            db.add(mfa_config)

        mfa_config.totp_secret = secret
        mfa_config.method = MFAMethod.TOTP
        mfa_config.totp_verified = False

        db.commit()

        # Generate QR code URI
        totp = pyotp.TOTP(secret)
        qr_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="TSH ERP System"
        )

        return secret, qr_uri

    @staticmethod
    def verify_totp_code(db: Session, user_id: int, code: str) -> bool:
        """Verify TOTP code"""
        if not PYOTP_AVAILABLE:
            return False

        mfa_config = db.query(UserMFA).filter(UserMFA.user_id == user_id).first()
        if not mfa_config or not mfa_config.totp_secret:
            return False

        totp = pyotp.TOTP(mfa_config.totp_secret)
        is_valid = totp.verify(code, valid_window=1)  # Allow 30 second window

        if is_valid:
            if not mfa_config.totp_verified:
                mfa_config.totp_verified = True
                mfa_config.is_enabled = True
                mfa_config.enabled_at = datetime.utcnow()
            mfa_config.last_used_at = datetime.utcnow()
            db.commit()

        # Record verification attempt
        verification = MFAVerification(
            user_id=user_id,
            method=MFAMethod.TOTP,
            code=hashlib.sha256(code.encode()).hexdigest(),
            success=is_valid
        )
        db.add(verification)
        db.commit()

        return is_valid

    @staticmethod
    def is_mfa_enabled(db: Session, user_id: int) -> bool:
        """Check if MFA is enabled for user"""
        mfa_config = db.query(UserMFA).filter(UserMFA.user_id == user_id).first()
        return mfa_config is not None and mfa_config.is_enabled

    @staticmethod
    def is_mfa_required(user_role: str) -> bool:
        """Check if MFA is required for this role"""
        mfa_required_for_admin = os.getenv("MFA_REQUIRED_FOR_ADMIN", "true").lower() == "true"
        if user_role.lower() == "admin" and mfa_required_for_admin:
            return True
        return False

    @staticmethod
    def generate_backup_codes(db: Session, user_id: int, count: int = 10) -> list:
        """Generate backup recovery codes"""
        from app.services.auth_service import AuthService
        import json

        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        hashed_codes = [AuthService.get_password_hash(code) for code in codes]

        mfa_config = db.query(UserMFA).filter(UserMFA.user_id == user_id).first()
        if mfa_config:
            mfa_config.backup_codes = json.dumps(hashed_codes)
            db.commit()

        return codes


class SessionService:
    """Handle user session management"""

    @staticmethod
    def create_session(
        db: Session,
        user_id: int,
        session_token: str,
        device_info: dict,
        ip_address: str,
        user_agent: str,
        expires_in_minutes: int = SESSION_TIMEOUT_MINUTES
    ) -> UserSession:
        """Create new user session"""
        # Check concurrent session limit
        SessionService.cleanup_old_sessions(db, user_id)
        active_sessions = SessionService.get_active_sessions(db, user_id)

        if len(active_sessions) >= MAX_CONCURRENT_SESSIONS:
            # Terminate oldest session
            oldest = active_sessions[-1]
            SessionService.terminate_session(db, oldest.id, "New session created, limit reached")

        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            device_name=device_info.get('name'),
            device_type=device_info.get('type'),
            device_id=device_info.get('id'),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_active_sessions(db: Session, user_id: int) -> list:
        """Get all active sessions for user"""
        return db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).order_by(UserSession.last_activity.desc()).all()

    @staticmethod
    def update_session_activity(db: Session, session_token: str):
        """Update last activity timestamp"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()

    @staticmethod
    def terminate_session(db: Session, session_id: int, reason: str = "User logout"):
        """Terminate a session"""
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            session.is_active = False
            session.terminated_at = datetime.utcnow()
            session.termination_reason = reason
            db.commit()

    @staticmethod
    def terminate_all_sessions(db: Session, user_id: int, except_session_id: Optional[int] = None):
        """Terminate all sessions for a user (except optionally one)"""
        query = db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )

        if except_session_id:
            query = query.filter(UserSession.id != except_session_id)

        sessions = query.all()
        for session in sessions:
            session.is_active = False
            session.terminated_at = datetime.utcnow()
            session.termination_reason = "All sessions terminated by user"

        db.commit()

    @staticmethod
    def cleanup_old_sessions(db: Session, user_id: int):
        """Remove expired sessions"""
        db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.expires_at <= datetime.utcnow()
            )
        ).delete()
        db.commit()


class PasswordPolicyService:
    """Handle password history and expiration"""

    @staticmethod
    def add_to_password_history(db: Session, user_id: int, password_hash: str):
        """Add password to history"""
        history = PasswordHistory(
            user_id=user_id,
            password_hash=password_hash
        )
        db.add(history)

        # Keep only last N passwords
        old_passwords = db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).order_by(PasswordHistory.created_at.desc()).offset(PASSWORD_HISTORY_COUNT).all()

        for old_pw in old_passwords:
            db.delete(old_pw)

        db.commit()

    @staticmethod
    def is_password_in_history(db: Session, user_id: int, password: str) -> bool:
        """Check if password was used recently"""
        from app.services.auth_service import AuthService

        history = db.query(PasswordHistory).filter(
            PasswordHistory.user_id == user_id
        ).order_by(PasswordHistory.created_at.desc()).limit(PASSWORD_HISTORY_COUNT).all()

        for record in history:
            if AuthService.verify_password(password, record.password_hash):
                return True

        return False


class SecurityEventService:
    """General security utilities"""

    @staticmethod
    def log_security_event(
        db: Session,
        event_type: str,
        severity: str = "info",
        description: str = "",
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> SecurityEvent:
        """Log a security event"""
        import json

        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            event_data=metadata  # JSON column accepts dict directly
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
