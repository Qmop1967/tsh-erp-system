"""
Trusted Devices API Router
Handles device trust management for automatic login
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.security import TrustedDevice
from app.services.auth_service import AuthService
from app.routers.auth_enhanced import get_current_user

router = APIRouter(prefix="/trusted-devices", tags=["Trusted Devices"])


# Pydantic Schemas
class TrustDeviceRequest(BaseModel):
    device_id: str
    device_name: str
    device_type: str  # "ios", "android", "web"
    device_fingerprint: Optional[str] = None
    trust_duration_days: Optional[int] = 30  # Default 30 days


class TrustedDeviceResponse(BaseModel):
    id: int
    device_id: str
    device_name: str
    device_type: str
    is_trusted: bool
    trust_expires_at: Optional[datetime]
    first_seen_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True


class DeviceTrustCheckRequest(BaseModel):
    device_id: str


class DeviceTrustCheckResponse(BaseModel):
    is_trusted: bool
    device_id: str
    user_id: Optional[int] = None
    can_auto_login: bool


@router.post("/trust", response_model=TrustedDeviceResponse)
async def trust_device(
    trust_request: TrustDeviceRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark current device as trusted for automatic login
    """
    # Check if device already exists
    existing_device = db.query(TrustedDevice).filter(
        TrustedDevice.user_id == current_user.id,
        TrustedDevice.device_id == trust_request.device_id
    ).first()

    if existing_device:
        # Update existing device
        existing_device.is_trusted = True
        existing_device.trust_expires_at = datetime.utcnow() + timedelta(days=trust_request.trust_duration_days)
        existing_device.last_seen_at = datetime.utcnow()
        existing_device.device_name = trust_request.device_name
        existing_device.device_type = trust_request.device_type
        if trust_request.device_fingerprint:
            existing_device.device_fingerprint = trust_request.device_fingerprint
        existing_device.revoked_at = None  # Un-revoke if previously revoked

        db.commit()
        db.refresh(existing_device)
        return existing_device

    # Create new trusted device
    new_device = TrustedDevice(
        user_id=current_user.id,
        device_id=trust_request.device_id,
        device_name=trust_request.device_name,
        device_type=trust_request.device_type,
        device_fingerprint=trust_request.device_fingerprint,
        is_trusted=True,
        trust_expires_at=datetime.utcnow() + timedelta(days=trust_request.trust_duration_days),
        first_seen_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow()
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device


@router.post("/check", response_model=DeviceTrustCheckResponse)
async def check_device_trust(
    check_request: DeviceTrustCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if a device is trusted (public endpoint for login screen)
    """
    trusted_device = db.query(TrustedDevice).filter(
        TrustedDevice.device_id == check_request.device_id,
        TrustedDevice.is_trusted == True,
        TrustedDevice.revoked_at.is_(None)
    ).first()

    if not trusted_device:
        return DeviceTrustCheckResponse(
            is_trusted=False,
            device_id=check_request.device_id,
            can_auto_login=False
        )

    # Check if trust has expired
    if trusted_device.trust_expires_at and trusted_device.trust_expires_at < datetime.utcnow():
        return DeviceTrustCheckResponse(
            is_trusted=False,
            device_id=check_request.device_id,
            user_id=trusted_device.user_id,
            can_auto_login=False
        )

    # Update last seen
    trusted_device.last_seen_at = datetime.utcnow()
    db.commit()

    return DeviceTrustCheckResponse(
        is_trusted=True,
        device_id=check_request.device_id,
        user_id=trusted_device.user_id,
        can_auto_login=True
    )


@router.get("/", response_model=List[TrustedDeviceResponse])
async def list_trusted_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all trusted devices for current user
    """
    devices = db.query(TrustedDevice).filter(
        TrustedDevice.user_id == current_user.id,
        TrustedDevice.revoked_at.is_(None)
    ).order_by(TrustedDevice.last_seen_at.desc()).all()

    return devices


@router.delete("/{device_id}")
async def revoke_device_trust(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke trust for a specific device
    """
    device = db.query(TrustedDevice).filter(
        TrustedDevice.user_id == current_user.id,
        TrustedDevice.device_id == device_id
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trusted device not found"
        )

    device.is_trusted = False
    device.revoked_at = datetime.utcnow()

    db.commit()

    return {"message": "Device trust revoked successfully", "device_id": device_id}


@router.post("/auto-login", response_model=dict)
async def auto_login_with_trusted_device(
    check_request: DeviceTrustCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Automatically login using a trusted device
    Returns access token if device is trusted
    """
    trusted_device = db.query(TrustedDevice).filter(
        TrustedDevice.device_id == check_request.device_id,
        TrustedDevice.is_trusted == True,
        TrustedDevice.revoked_at.is_(None)
    ).first()

    if not trusted_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trusted device not found"
        )

    # Check if trust has expired
    if trusted_device.trust_expires_at and trusted_device.trust_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device trust has expired. Please login again."
        )

    # Get user
    user = db.query(User).filter(User.id == trusted_device.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Update last seen
    trusted_device.last_seen_at = datetime.utcnow()
    db.commit()

    # Generate access token
    access_token = AuthService.create_access_token(data={"sub": user.email})

    # Get user permissions
    from app.routers.auth import get_user_permissions
    permissions = get_user_permissions(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.name if user.role else None,
            "branch_id": user.branch_id,
        },
        "permissions": permissions,
        "auto_login": True
    }
