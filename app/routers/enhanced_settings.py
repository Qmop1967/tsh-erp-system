# Enhanced Settings Router with Advanced Security Features
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
from pathlib import Path

from app.db.database import get_db
from app.services.permission_service import PermissionService, require_permission
from app.services.security_service import SecurityService, EnhancedBackupService
from app.services.tenant_service import TenantService, TenantContext
from app.schemas.settings import (
    BackupCreateRequest, BackupScheduleRequest, BackupRestoreRequest,
    GrantPermissionRequest, RevokePermissionRequest, SystemHealthResponse
)

router = APIRouter(prefix="/api/settings", tags=["settings"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                          db: Session = Depends(get_db)) -> dict:
    """Enhanced authentication with tenant context"""
    # This would typically decode JWT token and validate
    # For now, returning mock user data
    # In production, implement proper JWT validation
    
    user_data = {
        "user_id": 1,
        "tenant_id": 1,
        "branch_id": 1,
        "role": "admin"
    }
    
    # Set tenant context
    TenantContext.set_context(
        tenant_id=user_data["tenant_id"],
        user_id=user_data["user_id"],
        branch_id=user_data["branch_id"]
    )
    
    return user_data

# Enhanced backup endpoints with encryption and scheduling
@router.post("/backups/create")
@require_permission("create_backup")
async def create_encrypted_backup(
    backup_request: BackupCreateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create encrypted backup with verification"""
    backup_service = EnhancedBackupService(db)
    
    try:
        if backup_request.schedule_for_later:
            # Schedule backup for later
            background_tasks.add_task(
                backup_service.create_encrypted_backup,
                current_user["user_id"],
                backup_request.backup_type,
                backup_request.include_files
            )
            return {"status": "scheduled", "message": "Backup scheduled successfully"}
        else:
            # Create backup immediately
            result = await backup_service.create_encrypted_backup(
                current_user["user_id"],
                backup_request.backup_type,
                backup_request.include_files
            )
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")

@router.post("/backups/schedule")
@require_permission("schedule_backup")
async def schedule_automatic_backup(
    schedule_request: BackupScheduleRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule automatic backups"""
    backup_service = EnhancedBackupService(db)
    
    schedule_config = {
        "frequency": schedule_request.frequency,
        "time": schedule_request.time,
        "days_of_week": schedule_request.days_of_week,
        "backup_type": schedule_request.backup_type,
        "include_files": schedule_request.include_files,
        "retention_days": schedule_request.retention_days
    }
    
    success = await backup_service.schedule_backup(current_user["user_id"], schedule_config)
    
    if success:
        return {"status": "scheduled", "config": schedule_config}
    else:
        raise HTTPException(status_code=500, detail="Failed to schedule backup")

@router.post("/backups/restore/{backup_name}")
@require_permission("initiate_restore")
async def initiate_backup_restore(
    backup_name: str,
    restore_request: BackupRestoreRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate backup restore with multi-person approval"""
    backup_service = EnhancedBackupService(db)
    
    try:
        result = await backup_service.restore_backup(
            current_user["user_id"],
            backup_name,
            restore_request.approver_ids
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Security monitoring endpoints
@router.get("/security/audit-logs")
@require_permission("view_audit_logs")
async def get_audit_logs(
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with filters"""
    permission_service = PermissionService(db)
    
    logs = permission_service.get_audit_logs(
        user_id=user_id,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "timestamp": log.timestamp,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent
            }
            for log in logs
        ],
        "total": len(logs)
    }

@router.get("/security/suspicious-activity")
@require_permission("view_security_alerts")
async def check_suspicious_activity(
    user_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check for suspicious activities"""
    security_service = SecurityService(db)
    
    check_user_id = user_id or current_user["user_id"]
    
    result = security_service.detect_suspicious_activity(
        check_user_id,
        "security_check",
        "127.0.0.1"  # This would come from request
    )
    
    return result

# Permission management endpoints
@router.get("/permissions/user/{user_id}")
@require_permission("view_user_permissions")
async def get_user_permissions(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions for a user"""
    permission_service = PermissionService(db)
    permissions = permission_service.get_user_permissions(user_id)
    return {"user_id": user_id, "permissions": permissions}

@router.post("/permissions/grant")
@require_permission("grant_permissions")
async def grant_user_permission(
    permission_request: GrantPermissionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Grant permission to user"""
    permission_service = PermissionService(db)
    
    success = permission_service.grant_permission(
        granter_id=current_user["user_id"],
        user_id=permission_request.user_id,
        permission_name=permission_request.permission_name,
        conditions=permission_request.conditions,
        expires_at=permission_request.expires_at
    )
    
    if success:
        return {"status": "granted", "message": "Permission granted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to grant permission")

@router.post("/permissions/revoke")
@require_permission("revoke_permissions")
async def revoke_user_permission(
    permission_request: RevokePermissionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke permission from user"""
    permission_service = PermissionService(db)
    
    success = permission_service.revoke_permission(
        revoker_id=current_user["user_id"],
        user_id=permission_request.user_id,
        permission_name=permission_request.permission_name
    )
    
    if success:
        return {"status": "revoked", "message": "Permission revoked successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to revoke permission")

# Tenant management endpoints
@router.get("/tenant/info")
@require_permission("view_tenant_info")
async def get_tenant_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current tenant information"""
    tenant_service = TenantService(db)
    
    tenant_id = current_user["tenant_id"]
    stats = tenant_service.get_tenant_stats(tenant_id)
    limits = tenant_service.check_tenant_limits(tenant_id)
    
    return {
        "tenant_id": tenant_id,
        "stats": stats,
        "limits": limits
    }

@router.get("/tenant/usage")
@require_permission("view_usage_stats")
async def get_tenant_usage(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tenant usage statistics"""
    tenant_service = TenantService(db)
    
    usage_data = tenant_service.get_tenant_stats(current_user["tenant_id"])
    limits_check = tenant_service.check_tenant_limits(current_user["tenant_id"])
    
    return {
        "usage": usage_data,
        "limits_check": limits_check,
        "last_updated": datetime.utcnow().isoformat()
    }

# System health and monitoring
@router.get("/system/health")
@require_permission("view_system_health")
async def get_system_health(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive system health status"""
    try:
        # Database health
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check disk space
    backup_dir = Path("backups")
    if backup_dir.exists():
        disk_usage = os.statvfs(backup_dir)
        free_space_gb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**3)
    else:
        free_space_gb = 0
    
    # Memory usage (simplified - using basic system info)
    try:
        # Try to get basic memory info without psutil
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        
        lines = meminfo.split('\n')
        mem_total = 0
        mem_available = 0
        
        for line in lines:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            elif line.startswith('MemAvailable:'):
                mem_available = int(line.split()[1])
        
        memory_usage_percent = ((mem_total - mem_available) / mem_total) * 100 if mem_total > 0 else 0
    except Exception:
        memory_usage_percent = 0
    
    return {
        "database": db_status,
        "disk_space_gb": round(free_space_gb, 2),
        "memory_usage_percent": memory_usage_percent,
        "system_load": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system/performance")
@require_permission("view_performance_metrics")
async def get_performance_metrics(
    hours: int = 24,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system performance metrics"""
    permission_service = PermissionService(db)
    
    # Get recent audit log activity as a proxy for system activity
    start_time = datetime.utcnow() - timedelta(hours=hours)
    recent_logs = permission_service.get_audit_logs(
        start_date=start_time,
        limit=1000
    )
    
    # Calculate activity metrics
    activity_by_hour = {}
    for log in recent_logs:
        hour = log.timestamp.replace(minute=0, second=0, microsecond=0)
        activity_by_hour[hour] = activity_by_hour.get(hour, 0) + 1
    
    return {
        "total_requests": len(recent_logs),
        "activity_by_hour": {
            hour.isoformat(): count 
            for hour, count in activity_by_hour.items()
        },
        "avg_requests_per_hour": len(recent_logs) / max(hours, 1),
        "period_hours": hours,
        "generated_at": datetime.utcnow().isoformat()
    }
