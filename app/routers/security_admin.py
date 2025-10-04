"""
Security Administration API Router
Comprehensive admin interface for managing the advanced security system
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from app.db.database import get_db
from app.models.advanced_security import (
    SecurityPolicy, RestrictionGroup, RLSRule, FLSRule,
    MFADevice, UserSession, AuditLog, SecurityIncident
)
from app.services.advanced_security_service import AdvancedSecurityService
from app.services.mfa_mobile_service import MFAMobileService
from app.schemas.security_schemas import (
    SecurityPolicyCreate, SecurityPolicyUpdate, SecurityPolicyResponse,
    RestrictionGroupCreate, RestrictionGroupUpdate, RestrictionGroupResponse,
    RLSRuleCreate, RLSRuleUpdate, RLSRuleResponse,
    FLSRuleCreate, FLSRuleUpdate, FLSRuleResponse,
    SecurityIncidentResponse, AuditLogResponse,
    SecurityDashboardResponse, RiskAssessmentResponse
)
from app.dependencies.auth import get_current_admin_user
from app.models.user import User

router = APIRouter(
    prefix="/admin/security",
    tags=["Security Administration"],
    dependencies=[Depends(get_current_admin_user)]
)

# === SECURITY DASHBOARD ===

@router.get("/dashboard", response_model=SecurityDashboardResponse)
async def get_security_dashboard(
    db: Session = Depends(get_db),
    security_service: AdvancedSecurityService = Depends()
):
    """Get comprehensive security dashboard data"""
    
    # Get recent activity stats
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    # Active sessions
    active_sessions = db.query(UserSession).filter(
        UserSession.is_active == True,
        UserSession.expires_at > now
    ).count()
    
    # Recent failed logins
    failed_logins_24h = db.query(AuditLog).filter(
        AuditLog.action == "login_failed",
        AuditLog.timestamp >= last_24h
    ).count()
    
    # Security incidents
    open_incidents = db.query(SecurityIncident).filter(
        SecurityIncident.status.in_(["open", "investigating"])
    ).count()
    
    # MFA devices
    mfa_devices = db.query(MFADevice).filter(
        MFADevice.is_active == True
    ).count()
    
    # Recent audit logs
    recent_audits = db.query(AuditLog).filter(
        AuditLog.timestamp >= last_24h
    ).order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    # Risk assessment
    high_risk_sessions = db.query(UserSession).filter(
        UserSession.is_active == True,
        UserSession.risk_score >= 0.7
    ).count()
    
    # Policy violations
    policy_violations_7d = db.query(AuditLog).filter(
        AuditLog.action == "policy_violation",
        AuditLog.timestamp >= last_7d
    ).count()
    
    return SecurityDashboardResponse(
        active_sessions=active_sessions,
        failed_logins_24h=failed_logins_24h,
        open_incidents=open_incidents,
        mfa_devices=mfa_devices,
        high_risk_sessions=high_risk_sessions,
        policy_violations_7d=policy_violations_7d,
        recent_audits=[AuditLogResponse.from_orm(audit) for audit in recent_audits[:20]],
        system_health="healthy" if open_incidents == 0 and high_risk_sessions < 5 else "warning"
    )

# === SECURITY POLICIES ===

@router.get("/policies", response_model=List[SecurityPolicyResponse])
async def list_security_policies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List all security policies"""
    query = db.query(SecurityPolicy)
    
    if active_only:
        query = query.filter(SecurityPolicy.is_active == True)
    
    policies = query.order_by(SecurityPolicy.priority.desc()).offset(skip).limit(limit).all()
    return [SecurityPolicyResponse.from_orm(policy) for policy in policies]

@router.post("/policies", response_model=SecurityPolicyResponse)
async def create_security_policy(
    policy_data: SecurityPolicyCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new security policy"""
    
    # Validate policy document structure
    try:
        json.loads(json.dumps(policy_data.policy_document))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid policy document format")
    
    policy = SecurityPolicy(
        name=policy_data.name,
        display_name=policy_data.display_name,
        description=policy_data.description,
        policy_document=policy_data.policy_document,
        effect=policy_data.effect,
        priority=policy_data.priority,
        applies_to_roles=policy_data.applies_to_roles,
        applies_to_users=policy_data.applies_to_users,
        conditions=policy_data.conditions,
        is_active=policy_data.is_active,
        created_by=current_user.id
    )
    
    db.add(policy)
    db.commit()
    db.refresh(policy)
    
    return SecurityPolicyResponse.from_orm(policy)

@router.put("/policies/{policy_id}", response_model=SecurityPolicyResponse)
async def update_security_policy(
    policy_id: int = Path(...),
    policy_data: SecurityPolicyUpdate = ...,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update an existing security policy"""
    
    policy = db.query(SecurityPolicy).filter(SecurityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Update fields
    for field, value in policy_data.dict(exclude_unset=True).items():
        setattr(policy, field, value)
    
    policy.updated_at = datetime.utcnow()
    policy.updated_by = current_user.id
    
    db.commit()
    db.refresh(policy)
    
    return SecurityPolicyResponse.from_orm(policy)

@router.delete("/policies/{policy_id}")
async def deactivate_security_policy(
    policy_id: int = Path(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a security policy (soft delete)"""
    
    policy = db.query(SecurityPolicy).filter(SecurityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policy.is_active = False
    policy.updated_at = datetime.utcnow()
    policy.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Security policy deactivated successfully"}

@router.post("/policies/{policy_id}/test")
async def test_security_policy(
    policy_id: int = Path(...),
    test_context: Dict[str, Any] = ...,
    security_service: AdvancedSecurityService = Depends(),
    db: Session = Depends(get_db)
):
    """Test a security policy against a given context"""
    
    policy = db.query(SecurityPolicy).filter(SecurityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Evaluate policy
    result = await security_service.evaluate_single_policy(policy, test_context)
    
    return {
        "policy_name": policy.name,
        "test_context": test_context,
        "evaluation_result": result,
        "timestamp": datetime.utcnow().isoformat()
    }

# === RESTRICTION GROUPS ===

@router.get("/restriction-groups", response_model=List[RestrictionGroupResponse])
async def list_restriction_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List all restriction groups"""
    query = db.query(RestrictionGroup)
    
    if active_only:
        query = query.filter(RestrictionGroup.is_active == True)
    
    groups = query.order_by(RestrictionGroup.name).offset(skip).limit(limit).all()
    return [RestrictionGroupResponse.from_orm(group) for group in groups]

@router.post("/restriction-groups", response_model=RestrictionGroupResponse)
async def create_restriction_group(
    group_data: RestrictionGroupCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new restriction group"""
    
    group = RestrictionGroup(
        name=group_data.name,
        description=group_data.description,
        restrictions=group_data.restrictions,
        is_active=group_data.is_active,
        created_by=current_user.id
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    return RestrictionGroupResponse.from_orm(group)

# === RLS RULES ===

@router.get("/rls-rules", response_model=List[RLSRuleResponse])
async def list_rls_rules(
    table_name: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List Row-Level Security rules"""
    query = db.query(RLSRule)
    
    if active_only:
        query = query.filter(RLSRule.is_active == True)
    
    if table_name:
        query = query.filter(RLSRule.table_name == table_name)
    
    rules = query.order_by(RLSRule.table_name, RLSRule.name).all()
    return [RLSRuleResponse.from_orm(rule) for rule in rules]

@router.post("/rls-rules", response_model=RLSRuleResponse)
async def create_rls_rule(
    rule_data: RLSRuleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new RLS rule"""
    
    rule = RLSRule(
        name=rule_data.name,
        description=rule_data.description,
        table_name=rule_data.table_name,
        rule_expression=rule_data.rule_expression,
        applies_to_actions=rule_data.applies_to_actions,
        applies_to_roles=rule_data.applies_to_roles,
        applies_to_users=rule_data.applies_to_users,
        conditions=rule_data.conditions,
        is_active=rule_data.is_active,
        created_by=current_user.id
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return RLSRuleResponse.from_orm(rule)

# === FLS RULES ===

@router.get("/fls-rules", response_model=List[FLSRuleResponse])
async def list_fls_rules(
    table_name: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List Field-Level Security rules"""
    query = db.query(FLSRule)
    
    if active_only:
        query = query.filter(FLSRule.is_active == True)
    
    if table_name:
        query = query.filter(FLSRule.table_name == table_name)
    
    rules = query.order_by(FLSRule.table_name, FLSRule.column_name).all()
    return [FLSRuleResponse.from_orm(rule) for rule in rules]

@router.post("/fls-rules", response_model=FLSRuleResponse)
async def create_fls_rule(
    rule_data: FLSRuleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new FLS rule"""
    
    rule = FLSRule(
        name=rule_data.name,
        description=rule_data.description,
        table_name=rule_data.table_name,
        column_name=rule_data.column_name,
        is_visible=rule_data.is_visible,
        is_readable=rule_data.is_readable,
        is_writable=rule_data.is_writable,
        masking_pattern=rule_data.masking_pattern,
        requires_encryption=rule_data.requires_encryption,
        applies_to_roles=rule_data.applies_to_roles,
        applies_to_users=rule_data.applies_to_users,
        conditions=rule_data.conditions,
        is_active=rule_data.is_active,
        created_by=current_user.id
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return FLSRuleResponse.from_orm(rule)

# === AUDIT LOGS ===

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    risk_level: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering"""
    
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    if risk_level:
        query = query.filter(AuditLog.risk_level == risk_level)
    
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return [AuditLogResponse.from_orm(log) for log in logs]

@router.get("/audit-logs/export")
async def export_audit_logs(
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    security_service: AdvancedSecurityService = Depends(),
    db: Session = Depends(get_db)
):
    """Export audit logs in various formats"""
    
    # Build query
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    logs = query.order_by(AuditLog.timestamp.desc()).all()
    
    # Export based on format
    export_result = await security_service.export_audit_logs(logs, format)
    
    return {
        "export_url": export_result["url"],
        "filename": export_result["filename"],
        "record_count": len(logs),
        "export_timestamp": datetime.utcnow().isoformat()
    }

# === SECURITY INCIDENTS ===

@router.get("/incidents", response_model=List[SecurityIncidentResponse])
async def list_security_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List security incidents"""
    
    query = db.query(SecurityIncident)
    
    if status:
        query = query.filter(SecurityIncident.status == status)
    
    if severity:
        query = query.filter(SecurityIncident.severity == severity)
    
    incidents = query.order_by(SecurityIncident.created_at.desc()).offset(skip).limit(limit).all()
    return [SecurityIncidentResponse.from_orm(incident) for incident in incidents]

@router.put("/incidents/{incident_id}/status")
async def update_incident_status(
    incident_id: int = Path(...),
    status: str = ...,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update security incident status"""
    
    incident = db.query(SecurityIncident).filter(SecurityIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = status
    incident.updated_at = datetime.utcnow()
    incident.assigned_to = current_user.id
    
    if notes:
        if incident.investigation_notes:
            incident.investigation_notes += f"\n\n[{datetime.utcnow()}] {notes}"
        else:
            incident.investigation_notes = f"[{datetime.utcnow()}] {notes}"
    
    db.commit()
    
    return {"message": "Incident status updated successfully"}

# === USER SESSIONS ===

@router.get("/sessions")
async def list_active_sessions(
    user_id: Optional[int] = Query(None),
    high_risk_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List active user sessions"""
    
    query = db.query(UserSession).filter(
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    )
    
    if user_id:
        query = query.filter(UserSession.user_id == user_id)
    
    if high_risk_only:
        query = query.filter(UserSession.risk_score >= 0.7)
    
    sessions = query.order_by(UserSession.last_activity.desc()).all()
    
    return [
        {
            "id": session.id,
            "user_id": session.user_id,
            "user_email": session.user.email if session.user else None,
            "device_info": session.device_info,
            "location_info": session.location_info,
            "risk_score": session.risk_score,
            "last_activity": session.last_activity,
            "created_at": session.created_at,
            "expires_at": session.expires_at
        }
        for session in sessions
    ]

@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: str = Path(...),
    reason: str = "Terminated by admin",
    current_user: User = Depends(get_current_admin_user),
    security_service: AdvancedSecurityService = Depends(),
    db: Session = Depends(get_db)
):
    """Terminate a user session"""
    
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Terminate session
    await security_service.terminate_session(session_id, reason, current_user.id)
    
    return {"message": "Session terminated successfully"}

# === RISK ASSESSMENT ===

@router.get("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    security_service: AdvancedSecurityService = Depends(),
    db: Session = Depends(get_db)
):
    """Get comprehensive risk assessment"""
    
    assessment = await security_service.generate_risk_assessment()
    
    return RiskAssessmentResponse(
        overall_risk_score=assessment["overall_risk_score"],
        risk_level=assessment["risk_level"],
        active_threats=assessment["active_threats"],
        risk_factors=assessment["risk_factors"],
        recommendations=assessment["recommendations"],
        assessment_timestamp=datetime.utcnow()
    )

# === SYSTEM HEALTH ===

@router.get("/health")
async def get_security_system_health(
    security_service: AdvancedSecurityService = Depends(),
    db: Session = Depends(get_db)
):
    """Get security system health status"""
    
    health_status = await security_service.check_system_health()
    
    return {
        "status": health_status["status"],
        "components": health_status["components"],
        "last_check": datetime.utcnow(),
        "uptime": health_status["uptime"]
    }
