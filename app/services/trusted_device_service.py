"""
Trusted Device Service - Device Trust Management

Provides business logic for trusted device management:
- Mark devices as trusted for automatic login
- Check device trust status
- List user's trusted devices
- Revoke device trust
- Auto-login for trusted devices

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P3 Batch 3 - Trusted Devices Router Migration
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Depends

from app.db.database import get_db
from app.models.security import TrustedDevice
from app.models.user import User
from app.exceptions import EntityNotFoundError


class TrustedDeviceService:
    """Service for trusted device management"""

    def __init__(self, db: Session):
        """
        Initialize trusted device service.

        Args:
            db: Database session
        """
        self.db = db

    def trust_device(
        self,
        user_id: int,
        device_id: str,
        device_name: str,
        device_type: str,
        device_fingerprint: Optional[str],
        trust_duration_days: int
    ) -> TrustedDevice:
        """
        Mark device as trusted for automatic login.

        Args:
            user_id: User ID
            device_id: Unique device identifier
            device_name: Human-readable device name
            device_type: Device type (ios, android, web)
            device_fingerprint: Optional device fingerprint
            trust_duration_days: How long to trust (default 30 days)

        Returns:
            Trusted device record
        """
        # Check if device already exists
        existing_device = self.db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_id == device_id
        ).first()

        if existing_device:
            # Update existing device
            existing_device.is_trusted = True
            existing_device.trust_expires_at = datetime.utcnow() + timedelta(days=trust_duration_days)
            existing_device.last_seen_at = datetime.utcnow()
            existing_device.device_name = device_name
            existing_device.device_type = device_type
            if device_fingerprint:
                existing_device.device_fingerprint = device_fingerprint
            existing_device.revoked_at = None  # Un-revoke if previously revoked

            self.db.commit()
            self.db.refresh(existing_device)
            return existing_device

        # Create new trusted device
        new_device = TrustedDevice(
            user_id=user_id,
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            device_fingerprint=device_fingerprint,
            is_trusted=True,
            trust_expires_at=datetime.utcnow() + timedelta(days=trust_duration_days),
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow()
        )

        self.db.add(new_device)
        self.db.commit()
        self.db.refresh(new_device)
        return new_device

    def check_device_trust(self, device_id: str) -> Dict[str, Any]:
        """
        Check if device is trusted for any user.

        Args:
            device_id: Device identifier

        Returns:
            Dictionary with trust status and details
        """
        # Find device
        device = self.db.query(TrustedDevice).filter(
            TrustedDevice.device_id == device_id,
            TrustedDevice.is_trusted == True,
            TrustedDevice.revoked_at.is_(None)
        ).first()

        if not device:
            return {
                "is_trusted": False,
                "device_id": device_id,
                "user_id": None,
                "can_auto_login": False
            }

        # Check if trust has expired
        if device.trust_expires_at and device.trust_expires_at < datetime.utcnow():
            return {
                "is_trusted": False,
                "device_id": device_id,
                "user_id": device.user_id,
                "can_auto_login": False
            }

        # Update last seen
        device.last_seen_at = datetime.utcnow()
        self.db.commit()

        return {
            "is_trusted": True,
            "device_id": device_id,
            "user_id": device.user_id,
            "can_auto_login": True
        }

    def get_user_devices(self, user_id: int) -> List[TrustedDevice]:
        """
        Get all trusted devices for a user.

        Args:
            user_id: User ID

        Returns:
            List of trusted devices
        """
        return self.db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user_id
        ).order_by(TrustedDevice.last_seen_at.desc()).all()

    def revoke_device(self, user_id: int, device_id: str) -> bool:
        """
        Revoke trust for a device.

        Args:
            user_id: User ID
            device_id: Device identifier

        Returns:
            True if revoked

        Raises:
            EntityNotFoundError: If device not found
        """
        device = self.db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_id == device_id
        ).first()

        if not device:
            raise EntityNotFoundError("Trusted device", device_id)

        device.is_trusted = False
        device.revoked_at = datetime.utcnow()

        self.db.commit()
        return True

    def auto_login(self, device_id: str) -> Dict[str, Any]:
        """
        Attempt automatic login for trusted device.

        Args:
            device_id: Device identifier

        Returns:
            Dictionary with login status and user info
        """
        trust_check = self.check_device_trust(device_id)

        if not trust_check["can_auto_login"]:
            return {
                "success": False,
                "message": "Device is not trusted or trust has expired",
                "requires_manual_login": True
            }

        # Get user
        user = self.db.query(User).filter(
            User.id == trust_check["user_id"]
        ).first()

        if not user or not user.is_active:
            return {
                "success": False,
                "message": "User not found or inactive",
                "requires_manual_login": True
            }

        # Import here to avoid circular dependency
        from app.services.auth_service import AuthService

        # Generate access token
        access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )

        return {
            "success": True,
            "message": "Auto-login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }


# ============================================================================
# Dependency for FastAPI
# ============================================================================

def get_trusted_device_service(db: Session = Depends(get_db)) -> TrustedDeviceService:
    """
    Dependency to get TrustedDeviceService instance.

    Usage in routers:
        @router.post("/trust")
        def trust_device(
            service: TrustedDeviceService = Depends(get_trusted_device_service)
        ):
            device = service.trust_device(...)
            return device
    """
    return TrustedDeviceService(db)
