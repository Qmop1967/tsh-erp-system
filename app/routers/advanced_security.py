"""
Advanced Security API Router for TSH ERP System
Provides endpoints for advanced security features including:
- Multi-factor authentication
- Device management
- Session control
- Security policies
- Audit logging
- Passless authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.db.database import get_db
from app.models.user import User
from app.models.advanced_security import *
from app.services.advanced_security_service import AdvancedSecurityService, AccessContext, AccessDecision
from app.services.mfa_mobile_service import MFAMobileService, DeviceInfo
from app.dependencies.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/security", tags=["Advanced Security"])

# === PYDANTIC MODELS ===

class AccessCheckRequest(BaseModel):
    resource_type: str
    resource_id: Optional[str] = None
    action: str = "read"

class DeviceRegistrationRequest(BaseModel):
    name: str
    type: str
    platform: str
    version: str
    model: str
    manufacturer: str
    app_version: str
    push_token: str

class MFASetupRequest(BaseModel):
    factor_type: str  # "totp", "push", "sms"
    phone_number: Optional[str] = None

class MFAVerificationRequest(BaseModel):
    challenge_id: str
    code: str

class MFAResponseRequest(BaseModel):
    request_id: str
    approved: bool
    device_id: str

class SecurityPolicyRequest(BaseModel):
    name: str
    display_name: str
    description: str
    policy_document: Dict[str, Any]
    effect: str = "allow"
    priority: int = 100
    applies_to_resources: Optional[List[str]] = None
    applies_to_actions: Optional[List[str]] = None
    applies_to_subjects: Optional[Dict[str, List[int]]] = None
    conditions: Optional[Dict[str, Any]] = None

class PasslessTokenRequest(BaseModel):
    email: str
    token_type: str  # "magic_link", "qr_code"

class SessionTerminationRequest(BaseModel):
    session_id: str

# === HELPER FUNCTIONS ===

def get_access_context(request: Request, current_user: User) -> AccessContext:
    """Create access context from request"""
    return AccessContext(
        user_id=current_user.id,
        resource_type="api",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        branch_id=current_user.branch_id,
        tenant_id=getattr(current_user, 'tenant_id', None)
    )

# === ACCESS CONTROL ENDPOINTS ===

@router.post("/check-access")
async def check_access(
    request_data: AccessCheckRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if user has access to specific resource/action"""
    
    security_service = AdvancedSecurityService(db)
    
    context = AccessContext(
        user_id=current_user.id,
        resource_type=request_data.resource_type,
        resource_id=request_data.resource_id,
        action=request_data.action,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        branch_id=current_user.branch_id,
        tenant_id=getattr(current_user, 'tenant_id', None)
    )
    
    decision = security_service.check_access(context)
    
    return {
        "granted": decision.granted,
        "reason": decision.reason,
        "requires_mfa": decision.requires_mfa,
        "risk_score": decision.risk_score,
        "applicable_policies": decision.applicable_policies
    }

# === DEVICE MANAGEMENT ENDPOINTS ===

@router.post("/devices/register")
async def register_device(
    device_data: DeviceRegistrationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new device for the user"""
    
    mfa_service = MFAMobileService(db)
    
    device_info = DeviceInfo(
        name=device_data.name,
        type=device_data.type,
        platform=device_data.platform,
        version=device_data.version,
        model=device_data.model,
        manufacturer=device_data.manufacturer,
        app_version=device_data.app_version
    )
    
    context = get_access_context(request, current_user)
    
    result = mfa_service.register_mobile_device(
        current_user.id,
        device_info,
        device_data.push_token,
        context
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/devices")
async def get_user_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all devices for the current user"""
    
    devices = db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    
    result = []
    for device in devices:
        result.append({
            "device_id": device.id,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "platform": device.platform,
            "status": device.status.value,
            "is_trusted": device.is_trusted,
            "first_seen": device.first_seen.isoformat(),
            "last_seen": device.last_seen.isoformat(),
            "last_ip_address": device.last_ip_address,
            "last_location": device.last_location
        })
    
    return result

@router.get("/devices/pending")
async def get_pending_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get devices pending approval (admin only)"""
    
    # Check if user is admin
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    mfa_service = MFAMobileService(db)
    return mfa_service.get_pending_devices()

@router.post("/devices/{device_id}/approve")
async def approve_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a device (admin only)"""
    
    # Check if user is admin
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    mfa_service = MFAMobileService(db)
    result = mfa_service.approve_mobile_device(device_id, current_user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.delete("/devices/{device_id}")
async def revoke_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke/block a device"""
    
    device = db.query(UserDevice).filter(
        and_(
            UserDevice.id == device_id,
            UserDevice.user_id == current_user.id
        )
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.status = DeviceStatus.BLOCKED
    db.commit()
    
    return {"message": "Device revoked successfully"}

# === MFA ENDPOINTS ===

@router.post("/mfa/setup")
async def setup_mfa(
    setup_data: MFASetupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Setup MFA for user"""
    
    mfa_service = MFAMobileService(db)
    
    if setup_data.factor_type == "totp":
        result = mfa_service.setup_totp(current_user.id)
    elif setup_data.factor_type == "push":
        # Need device_id for push notifications
        raise HTTPException(status_code=400, detail="Device ID required for push notifications")
    else:
        raise HTTPException(status_code=400, detail="Unsupported MFA type")
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/mfa/verify-setup")
async def verify_mfa_setup(
    verification_data: MFAVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify MFA setup"""
    
    mfa_service = MFAMobileService(db)
    result = mfa_service.verify_totp_setup(
        int(verification_data.challenge_id),
        verification_data.code
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/mfa/challenge")
async def create_mfa_challenge(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create MFA challenge"""
    
    security_service = AdvancedSecurityService(db)
    context = get_access_context(request, current_user)
    
    challenge_id = security_service.create_mfa_challenge(
        current_user.id,
        AuthFactor.TOTP,  # Default to TOTP for now
        context
    )
    
    return {"challenge_id": challenge_id}

@router.post("/mfa/verify")
async def verify_mfa_challenge(
    verification_data: MFAVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify MFA challenge"""
    
    security_service = AdvancedSecurityService(db)
    is_valid = security_service.verify_mfa_challenge(
        verification_data.challenge_id,
        verification_data.code
    )
    
    return {"valid": is_valid}

@router.get("/mfa/methods")
async def get_mfa_methods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's MFA methods"""
    
    methods = db.query(MFAMethod).filter(
        and_(
            MFAMethod.user_id == current_user.id,
            MFAMethod.is_enabled == True
        )
    ).all()
    
    result = []
    for method in methods:
        result.append({
            "id": method.id,
            "factor_type": method.factor_type.value,
            "is_primary": method.is_primary,
            "created_at": method.created_at.isoformat(),
            "last_used": method.last_used.isoformat() if method.last_used else None,
            "use_count": method.use_count
        })
    
    return result

@router.get("/mfa/requests")
async def get_mfa_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending MFA requests for mobile app"""
    
    mfa_service = MFAMobileService(db)
    return mfa_service.get_pending_mfa_requests(current_user.id)

@router.post("/mfa/respond")
async def respond_to_mfa_request(
    response_data: MFAResponseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Respond to MFA request from mobile app"""
    
    mfa_service = MFAMobileService(db)
    result = mfa_service.handle_mfa_response(
        response_data.request_id,
        current_user.id,
        response_data.approved,
        response_data.device_id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# === SESSION MANAGEMENT ENDPOINTS ===

@router.get("/sessions")
async def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active sessions for user"""
    
    mfa_service = MFAMobileService(db)
    return mfa_service.get_user_sessions(current_user.id)

@router.post("/sessions/terminate")
async def terminate_session(
    termination_data: SessionTerminationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Terminate a specific session"""
    
    mfa_service = MFAMobileService(db)
    result = mfa_service.terminate_session(
        termination_data.session_id,
        current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/sessions/terminate-all")
async def terminate_all_other_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Terminate all other sessions for user"""
    
    # Get current session ID from headers or token
    current_session_id = request.headers.get("x-session-id", "unknown")
    
    mfa_service = MFAMobileService(db)
    result = mfa_service.terminate_all_other_sessions(
        current_user.id,
        current_session_id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# === SECURITY POLICIES ENDPOINTS ===

@router.get("/policies")
async def get_security_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all security policies (admin only)"""
    
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    policies = db.query(SecurityPolicy).filter(SecurityPolicy.is_active == True).all()
    
    result = []
    for policy in policies:
        result.append({
            "id": policy.id,
            "name": policy.name,
            "display_name": policy.display_name,
            "description": policy.description,
            "effect": policy.effect.value,
            "priority": policy.priority,
            "applies_to_resources": policy.applies_to_resources,
            "applies_to_actions": policy.applies_to_actions,
            "applies_to_subjects": policy.applies_to_subjects,
            "conditions": policy.conditions,
            "created_at": policy.created_at.isoformat()
        })
    
    return result

@router.post("/policies")
async def create_security_policy(
    policy_data: SecurityPolicyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create security policy (admin only)"""
    
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if policy name already exists
    existing = db.query(SecurityPolicy).filter(SecurityPolicy.name == policy_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Policy name already exists")
    
    policy = SecurityPolicy(
        name=policy_data.name,
        display_name=policy_data.display_name,
        description=policy_data.description,
        policy_document=policy_data.policy_document,
        effect=PolicyEffect.ALLOW if policy_data.effect.lower() == "allow" else PolicyEffect.DENY,
        priority=policy_data.priority,
        applies_to_resources=policy_data.applies_to_resources,
        applies_to_actions=policy_data.applies_to_actions,
        applies_to_subjects=policy_data.applies_to_subjects,
        conditions=policy_data.conditions,
        created_by=current_user.id
    )
    
    db.add(policy)
    db.commit()
    
    return {"message": "Security policy created successfully", "policy_id": policy.id}

# === AUDIT LOGGING ENDPOINTS ===

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs (admin only)"""
    
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "description": log.description,
            "timestamp": log.timestamp.isoformat(),
            "ip_address": log.ip_address,
            "location": log.location,
            "risk_score": log.risk_score,
            "is_suspicious": log.is_suspicious
        })
    
    return result

@router.get("/security-events")
async def get_security_events(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    unresolved_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get security events (admin only)"""
    
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(SecurityEvent)
    
    if severity:
        severity_enum = RiskLevel(severity.lower())
        query = query.filter(SecurityEvent.severity == severity_enum)
    
    if unresolved_only:
        query = query.filter(SecurityEvent.is_resolved == False)
    
    events = query.order_by(SecurityEvent.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for event in events:
        result.append({
            "id": event.id,
            "event_type": event.event_type,
            "severity": event.severity.value,
            "title": event.title,
            "description": event.description,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "location": event.location,
            "event_data": event.event_data,
            "is_resolved": event.is_resolved,
            "created_at": event.created_at.isoformat(),
            "resolved_at": event.resolved_at.isoformat() if event.resolved_at else None
        })
    
    return result

# === PASSLESS AUTHENTICATION ENDPOINTS ===

@router.post("/passless/create-token")
async def create_passless_token(
    token_data: PasslessTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create passless authentication token"""
    
    mfa_service = MFAMobileService(db)
    
    context = AccessContext(
        user_id=0,  # Unknown user at this point
        resource_type="authentication",
        action="create_passless_token",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    result = mfa_service.create_passless_token(
        token_data.email,
        token_data.token_type,
        context
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/passless/verify-token")
async def verify_passless_token(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify passless authentication token"""
    
    mfa_service = MFAMobileService(db)
    
    context = AccessContext(
        user_id=0,
        resource_type="authentication",
        action="verify_passless_token",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    result = mfa_service.verify_passless_token(token, context)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# === SECURITY DASHBOARD ENDPOINTS ===

@router.get("/dashboard/stats")
async def get_security_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get security dashboard statistics (admin only)"""
    
    if not current_user.role or current_user.role.name.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get various security statistics
    active_sessions = db.query(UserSession).filter(
        and_(
            UserSession.status == SessionStatus.ACTIVE,
            UserSession.expires_at > datetime.utcnow()
        )
    ).count()
    
    pending_devices = db.query(UserDevice).filter(
        UserDevice.status == DeviceStatus.PENDING
    ).count()
    
    recent_security_events = db.query(SecurityEvent).filter(
        and_(
            SecurityEvent.created_at >= datetime.utcnow() - timedelta(days=7),
            SecurityEvent.is_resolved == False
        )
    ).count()
    
    high_risk_sessions = db.query(UserSession).filter(
        and_(
            UserSession.status == SessionStatus.ACTIVE,
            UserSession.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        )
    ).count()
    
    return {
        "active_sessions": active_sessions,
        "pending_devices": pending_devices,
        "recent_security_events": recent_security_events,
        "high_risk_sessions": high_risk_sessions,
        "generated_at": datetime.utcnow().isoformat()
    }
