"""
Owner Approvals Router

Handles secure approval workflows for sensitive operations
requiring Owner/Director authorization.

Security:
- ALL endpoints require authentication
- Owner-only endpoints check for 'owner' or 'admin' role
- Complete audit trail for all actions
- QR payloads signed with JWT
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from jose import jwt
import json

from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import RoleChecker
from app.models.user import User
from app.models.owner_approval import (
    OwnerApproval, ApprovalAuditLog, OwnerSecuritySettings,
    ApprovalStatus, ApprovalMethod, ApprovalType, RiskLevel
)
from app.schemas.owner_approval import (
    CreateApprovalRequest, ApproveRequest, DenyRequest, QRScanRequest,
    ApprovalResponse, ApprovalListResponse, ApprovalCreatedResponse,
    ApprovalActionResponse, QRCodeResponse, ApprovalStatsResponse,
    RequesterInfo, OwnerSecuritySettingsResponse, UpdateSecuritySettingsRequest
)
from app.services.auth_service import SECRET_KEY, ALGORITHM
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth/owner", tags=["Owner Approvals"])

# Helper to check if user is owner
def require_owner_role(user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user has owner or admin role"""
    if not user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no role assigned"
        )

    role_name = user.role.name.lower()
    if role_name not in ['owner', 'admin', 'director']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires Owner or Admin privileges"
        )
    return user


def log_approval_action(
    db: Session,
    approval_id: str,
    action: str,
    actor_id: Optional[int],
    request: Optional[Request] = None,
    old_status: Optional[ApprovalStatus] = None,
    new_status: Optional[ApprovalStatus] = None,
    notes: Optional[str] = None
):
    """Log an action to the approval audit log"""
    audit_entry = ApprovalAuditLog(
        approval_id=approval_id,
        action=action,
        actor_id=actor_id,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent", "") if request else None,
        old_status=old_status,
        new_status=new_status,
        notes=notes
    )
    db.add(audit_entry)
    db.commit()


def generate_qr_jwt(approval: OwnerApproval) -> str:
    """Generate a signed JWT payload for QR code scanning"""
    payload = {
        "approval_id": approval.id,
        "approval_type": approval.approval_type.value,
        "requester_id": approval.requester_id,
        "created_at": approval.created_at.isoformat(),
        "expires_at": approval.expires_at.isoformat(),
        "iat": datetime.utcnow().timestamp(),
        "exp": approval.expires_at.timestamp()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_qr_jwt(token: str) -> dict:
    """Verify and decode a QR JWT payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        logger.error(f"QR JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired QR code"
        )


def approval_to_response(approval: OwnerApproval) -> ApprovalResponse:
    """Convert approval model to response schema"""
    # Calculate time remaining
    time_remaining = None
    if approval.status == ApprovalStatus.PENDING and not approval.is_expired():
        remaining = (approval.expires_at - datetime.utcnow()).total_seconds()
        time_remaining = max(0, int(remaining))

    requester_info = RequesterInfo(
        id=approval.requester.id,
        name=approval.requester.name,
        email=approval.requester.email,
        role=approval.requester.role.name if approval.requester.role else None
    )

    return ApprovalResponse(
        id=approval.id,
        requester=requester_info,
        approval_type=approval.approval_type.value,
        risk_level=approval.risk_level.value,
        status=approval.status.value,
        method=approval.method.value,
        request_description=approval.request_description,
        request_description_ar=approval.request_description_ar,
        app_id=approval.app_id,
        device_info=approval.device_info,
        ip_address=approval.ip_address,
        geolocation=approval.geolocation,
        created_at=approval.created_at,
        expires_at=approval.expires_at,
        resolved_at=approval.resolved_at,
        resolved_by=approval.resolved_by,
        resolution_reason=approval.resolution_reason,
        resolution_reason_ar=approval.resolution_reason_ar,
        is_expired=approval.is_expired(),
        time_remaining_seconds=time_remaining
    )


# ============================================================================
# REQUEST APPROVAL (For any authenticated user)
# ============================================================================

@router.post(
    "/request-approval",
    response_model=ApprovalCreatedResponse,
    summary="Request Owner approval",
    description="""
    Create a new approval request for Owner/Director authorization.

    Any authenticated user can request approval for sensitive operations.
    The Owner will receive a notification via TSH NeuroLink.

    **Returns:**
    - Approval ID and 6-digit code
    - Expiration time
    - Notification status
    """
)
async def request_approval(
    request_data: CreateApprovalRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request owner approval for sensitive operation"""

    # Create approval request
    approval_code = OwnerApproval.generate_approval_code()
    expires_at = datetime.utcnow() + timedelta(minutes=request_data.expiration_minutes or 10)

    approval = OwnerApproval(
        requester_id=current_user.id,
        approval_type=ApprovalType(request_data.approval_type.value),
        risk_level=RiskLevel(request_data.risk_level.value),
        approval_code=approval_code,
        method=ApprovalMethod(request_data.method.value),
        status=ApprovalStatus.PENDING,
        app_id=request_data.app_id,
        request_description=request_data.request_description,
        request_description_ar=request_data.request_description_ar,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", ""),
        expires_at=expires_at,
        request_metadata=request_data.metadata
    )

    # Generate QR payload
    db.add(approval)
    db.flush()  # Get the ID
    approval.qr_payload = generate_qr_jwt(approval)

    db.commit()
    db.refresh(approval)

    # Log the action
    log_approval_action(
        db, approval.id, "created", current_user.id, request,
        new_status=ApprovalStatus.PENDING,
        notes=f"Approval request created for {request_data.approval_type.value}"
    )

    # Send notification via TSH NeuroLink (APNS for iOS)
    notification_sent = False
    notification_channels = {}
    try:
        from app.services.owner_notification_service import owner_notification_service

        # Get location info from request
        location_str = None
        if approval.geolocation:
            loc = approval.geolocation
            location_str = f"{loc.get('city', 'Unknown')}, {loc.get('country', 'Unknown')}"

        # Send push notification to Owner
        notification_result = await owner_notification_service.notify_approval_request(
            db=db,
            approval_id=approval.id,
            requester=current_user,
            app_name=request_data.app_id,
            approval_code=approval_code,
            location=location_str,
            risk_level=request_data.risk_level.value
        )

        notification_sent = notification_result.get("overall_success", False)
        notification_channels = notification_result.get("channels", {})

        # Update approval with notification status
        approval.notification_sent = notification_sent
        approval.notification_sent_at = datetime.utcnow() if notification_sent else None
        db.commit()

        logger.info(
            f"Notification sent for approval {approval.id}: {notification_result}"
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        notification_channels = {"error": str(e)}

    logger.info(
        "owner_approval_requested",
        approval_id=approval.id,
        requester_id=current_user.id,
        approval_type=request_data.approval_type.value,
        risk_level=request_data.risk_level.value,
        notification_sent=notification_sent
    )

    return ApprovalCreatedResponse(
        success=True,
        message="Approval request created successfully",
        message_ar="تم إنشاء طلب الموافقة بنجاح",
        approval_id=approval.id,
        approval_code=approval_code,
        expires_at=expires_at,
        notification_sent=notification_sent
    )


# ============================================================================
# OWNER-ONLY ENDPOINTS
# ============================================================================

@router.get(
    "/pending",
    response_model=ApprovalListResponse,
    summary="Get pending approvals",
    description="Get list of pending approval requests (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def get_pending_approvals(
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    approval_type: Optional[str] = Query(None, description="Filter by type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pending approval requests"""

    # Build query
    query = db.query(OwnerApproval).filter(
        OwnerApproval.status == ApprovalStatus.PENDING,
        OwnerApproval.expires_at > datetime.utcnow()
    )

    # Apply filters
    if risk_level:
        try:
            query = query.filter(OwnerApproval.risk_level == RiskLevel(risk_level))
        except ValueError:
            pass

    if approval_type:
        try:
            query = query.filter(OwnerApproval.approval_type == ApprovalType(approval_type))
        except ValueError:
            pass

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    approvals = query.order_by(
        OwnerApproval.risk_level.desc(),
        OwnerApproval.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    # Convert to response
    approval_responses = [approval_to_response(a) for a in approvals]

    return ApprovalListResponse(
        approvals=approval_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get(
    "/all",
    response_model=ApprovalListResponse,
    summary="Get all approvals",
    description="Get all approval requests with filters (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def get_all_approvals(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    risk_level: Optional[str] = Query(None),
    approval_type: Optional[str] = Query(None),
    requester_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all approval requests with filtering"""

    query = db.query(OwnerApproval)

    # Apply filters
    if status_filter:
        try:
            query = query.filter(OwnerApproval.status == ApprovalStatus(status_filter))
        except ValueError:
            pass

    if risk_level:
        try:
            query = query.filter(OwnerApproval.risk_level == RiskLevel(risk_level))
        except ValueError:
            pass

    if approval_type:
        try:
            query = query.filter(OwnerApproval.approval_type == ApprovalType(approval_type))
        except ValueError:
            pass

    if requester_id:
        query = query.filter(OwnerApproval.requester_id == requester_id)

    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(OwnerApproval.created_at >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(OwnerApproval.created_at <= to_date)
        except ValueError:
            pass

    total = query.count()

    approvals = query.order_by(
        OwnerApproval.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    approval_responses = [approval_to_response(a) for a in approvals]

    return ApprovalListResponse(
        approvals=approval_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
    summary="Get approval details",
    description="Get details of a specific approval request"
)
async def get_approval_details(
    approval_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific approval"""

    approval = db.query(OwnerApproval).filter(
        OwnerApproval.id == approval_id
    ).first()

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )

    # Check permissions: requester can see their own, owner can see all
    role_name = current_user.role.name.lower() if current_user.role else ""
    if approval.requester_id != current_user.id and role_name not in ['owner', 'admin', 'director']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this approval"
        )

    return approval_to_response(approval)


@router.post(
    "/approve",
    response_model=ApprovalActionResponse,
    summary="Approve request",
    description="Approve a pending request using 6-digit code (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def approve_request(
    approval_data: ApproveRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a pending approval request"""

    # Find the approval by code
    approval = db.query(OwnerApproval).filter(
        OwnerApproval.approval_code == approval_data.approval_code,
        OwnerApproval.status == ApprovalStatus.PENDING
    ).first()

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid approval code or request already resolved"
        )

    # Check expiration
    if approval.is_expired():
        approval.status = ApprovalStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval request has expired"
        )

    # Update approval
    old_status = approval.status
    approval.status = ApprovalStatus.APPROVED
    approval.resolved_at = datetime.utcnow()
    approval.resolved_by = current_user.id
    approval.resolution_reason = approval_data.resolution_reason
    approval.resolution_reason_ar = approval_data.resolution_reason_ar
    approval.owner_ip_address = request.client.host if request.client else None
    approval.owner_device_info = {
        "user_agent": request.headers.get("user-agent", ""),
        "biometric_verified": approval_data.biometric_verified
    }

    db.commit()

    # Log action
    log_approval_action(
        db, approval.id, "approved", current_user.id, request,
        old_status=old_status, new_status=ApprovalStatus.APPROVED,
        notes=approval_data.resolution_reason
    )

    logger.info(
        "owner_approval_approved",
        approval_id=approval.id,
        approved_by=current_user.id,
        requester_id=approval.requester_id
    )

    return ApprovalActionResponse(
        success=True,
        message="Request approved successfully",
        message_ar="تمت الموافقة على الطلب بنجاح",
        approval_id=approval.id,
        new_status=ApprovalStatus.APPROVED.value,
        resolved_at=approval.resolved_at
    )


@router.post(
    "/{approval_id}/deny",
    response_model=ApprovalActionResponse,
    summary="Deny request",
    description="Deny a pending approval request (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def deny_request(
    approval_id: str,
    denial_data: DenyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deny a pending approval request"""

    approval = db.query(OwnerApproval).filter(
        OwnerApproval.id == approval_id,
        OwnerApproval.status == ApprovalStatus.PENDING
    ).first()

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found or already resolved"
        )

    old_status = approval.status
    approval.status = ApprovalStatus.DENIED
    approval.resolved_at = datetime.utcnow()
    approval.resolved_by = current_user.id
    approval.resolution_reason = denial_data.resolution_reason
    approval.resolution_reason_ar = denial_data.resolution_reason_ar
    approval.owner_ip_address = request.client.host if request.client else None

    db.commit()

    log_approval_action(
        db, approval.id, "denied", current_user.id, request,
        old_status=old_status, new_status=ApprovalStatus.DENIED,
        notes=denial_data.resolution_reason
    )

    logger.info(
        "owner_approval_denied",
        approval_id=approval.id,
        denied_by=current_user.id,
        requester_id=approval.requester_id
    )

    return ApprovalActionResponse(
        success=True,
        message="Request denied",
        message_ar="تم رفض الطلب",
        approval_id=approval.id,
        new_status=ApprovalStatus.DENIED.value,
        resolved_at=approval.resolved_at
    )


@router.post(
    "/{approval_id}/qr/generate",
    response_model=QRCodeResponse,
    summary="Generate QR code",
    description="Generate QR code for approval (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def generate_qr_code(
    approval_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate QR code for approval scanning"""

    approval = db.query(OwnerApproval).filter(
        OwnerApproval.id == approval_id
    ).first()

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only generate QR for pending approvals"
        )

    # Regenerate QR payload if needed
    if not approval.qr_payload:
        approval.qr_payload = generate_qr_jwt(approval)
        db.commit()

    return QRCodeResponse(
        success=True,
        approval_id=approval.id,
        qr_payload=approval.qr_payload,
        expires_at=approval.expires_at
    )


@router.post(
    "/qr/scan",
    response_model=ApprovalActionResponse,
    summary="Scan QR to approve",
    description="Approve request by scanning QR code (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def scan_qr_approve(
    scan_data: QRScanRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve request by scanning QR code"""

    # Verify QR payload
    payload = verify_qr_jwt(scan_data.qr_payload)
    approval_id = payload.get("approval_id")

    if not approval_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid QR code payload"
        )

    # Get the approval
    approval = db.query(OwnerApproval).filter(
        OwnerApproval.id == approval_id,
        OwnerApproval.status == ApprovalStatus.PENDING
    ).first()

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found or already resolved"
        )

    if approval.is_expired():
        approval.status = ApprovalStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval request has expired"
        )

    # Verify QR payload matches
    if approval.qr_payload != scan_data.qr_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="QR code does not match this approval"
        )

    # Approve
    old_status = approval.status
    approval.status = ApprovalStatus.APPROVED
    approval.resolved_at = datetime.utcnow()
    approval.resolved_by = current_user.id
    approval.resolution_reason = "Approved via QR scan"
    approval.owner_ip_address = request.client.host if request.client else None
    approval.owner_device_info = {
        "method": "qr_scan",
        "biometric_verified": scan_data.biometric_verified
    }

    db.commit()

    log_approval_action(
        db, approval.id, "approved_via_qr", current_user.id, request,
        old_status=old_status, new_status=ApprovalStatus.APPROVED
    )

    logger.info(
        "owner_approval_qr_scan",
        approval_id=approval.id,
        approved_by=current_user.id
    )

    return ApprovalActionResponse(
        success=True,
        message="Request approved via QR scan",
        message_ar="تمت الموافقة على الطلب عبر مسح QR",
        approval_id=approval.id,
        new_status=ApprovalStatus.APPROVED.value,
        resolved_at=approval.resolved_at
    )


@router.get(
    "/stats/summary",
    response_model=ApprovalStatsResponse,
    summary="Get approval statistics",
    description="Get summary statistics of approvals (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def get_approval_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get approval statistics"""

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Count pending
    pending = db.query(OwnerApproval).filter(
        OwnerApproval.status == ApprovalStatus.PENDING,
        OwnerApproval.expires_at > datetime.utcnow()
    ).count()

    # Count today's resolutions
    approved_today = db.query(OwnerApproval).filter(
        OwnerApproval.status == ApprovalStatus.APPROVED,
        OwnerApproval.resolved_at >= today_start
    ).count()

    denied_today = db.query(OwnerApproval).filter(
        OwnerApproval.status == ApprovalStatus.DENIED,
        OwnerApproval.resolved_at >= today_start
    ).count()

    expired_today = db.query(OwnerApproval).filter(
        OwnerApproval.status == ApprovalStatus.EXPIRED,
        OwnerApproval.expires_at >= today_start
    ).count()

    # Average resolution time (for approved/denied today)
    resolved = db.query(OwnerApproval).filter(
        OwnerApproval.resolved_at >= today_start,
        OwnerApproval.status.in_([ApprovalStatus.APPROVED, ApprovalStatus.DENIED])
    ).all()

    avg_time = None
    if resolved:
        total_seconds = sum(
            (a.resolved_at - a.created_at).total_seconds() for a in resolved
        )
        avg_time = total_seconds / len(resolved)

    # Count by risk level (all time)
    by_risk = {}
    for level in RiskLevel:
        count = db.query(OwnerApproval).filter(
            OwnerApproval.risk_level == level
        ).count()
        by_risk[level.value] = count

    # Count by type (all time)
    by_type = {}
    for atype in ApprovalType:
        count = db.query(OwnerApproval).filter(
            OwnerApproval.approval_type == atype
        ).count()
        if count > 0:
            by_type[atype.value] = count

    return ApprovalStatsResponse(
        pending=pending,
        approved_today=approved_today,
        denied_today=denied_today,
        expired_today=expired_today,
        average_resolution_time_seconds=avg_time,
        by_risk_level=by_risk,
        by_type=by_type
    )


# ============================================================================
# SECURITY SETTINGS
# ============================================================================

@router.get(
    "/settings/security",
    response_model=OwnerSecuritySettingsResponse,
    summary="Get security settings",
    description="Get Owner security settings (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def get_security_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get owner security settings"""

    settings = db.query(OwnerSecuritySettings).filter(
        OwnerSecuritySettings.user_id == current_user.id
    ).first()

    if not settings:
        # Create default settings
        settings = OwnerSecuritySettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put(
    "/settings/security",
    response_model=OwnerSecuritySettingsResponse,
    summary="Update security settings",
    description="Update Owner security settings (Owner only)",
    dependencies=[Depends(require_owner_role)]
)
async def update_security_settings(
    update_data: UpdateSecuritySettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update owner security settings"""

    settings = db.query(OwnerSecuritySettings).filter(
        OwnerSecuritySettings.user_id == current_user.id
    ).first()

    if not settings:
        settings = OwnerSecuritySettings(user_id=current_user.id)
        db.add(settings)

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(settings, key, value)

    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)

    logger.info(
        "owner_security_settings_updated",
        user_id=current_user.id,
        updated_fields=list(update_dict.keys())
    )

    return settings
