"""
Dashboard API Router
Provides dashboard statistics and metrics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from datetime import datetime, timedelta
from typing import Dict, Any

from app.db.database import get_db
from app.models.user import User
from app.routers.auth_enhanced import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard statistics
    Returns counts for:
    - Total users
    - Active sessions
    - Security alerts
    - Failed logins (last 24 hours)
    """
    try:
        # Total users count
        total_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0

        # Active sessions count - using is_active boolean column
        active_sessions_result = db.execute(text(
            "SELECT COUNT(*) FROM user_sessions WHERE is_active = true AND expires_at > NOW()"
        )).scalar()
        active_sessions = active_sessions_result if active_sessions_result else 0

        # Security alerts count (last 7 days) - using raw SQL
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        security_alerts_result = db.execute(text(
            "SELECT COUNT(*) FROM security_events WHERE created_at >= :seven_days_ago AND severity IN ('medium', 'high', 'critical')"
        ), {"seven_days_ago": seven_days_ago}).scalar()
        security_alerts = security_alerts_result if security_alerts_result else 0

        # Failed logins count (last 24 hours) - using raw SQL
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        failed_logins_result = db.execute(text(
            "SELECT COUNT(*) FROM audit_logs WHERE action = 'login_failed' AND timestamp >= :twenty_four_hours_ago"
        ), {"twenty_four_hours_ago": twenty_four_hours_ago}).scalar()
        failed_logins = failed_logins_result if failed_logins_result else 0

        return {
            "total_users": total_users,
            "active_sessions": active_sessions,
            "security_alerts": security_alerts,
            "failed_logins": failed_logins,
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"❌ Dashboard stats error: {e}")
        # Return zeros if tables don't exist yet
        return {
            "total_users": db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0,
            "active_sessions": 0,
            "security_alerts": 0,
            "failed_logins": 0,
            "last_updated": datetime.utcnow().isoformat()
        }


@router.get("/users/count")
async def get_users_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, int]:
    """Get total active users count"""
    try:
        count = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users count: {str(e)}")


@router.get("/sessions/active/count")
async def get_active_sessions_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, int]:
    """Get active sessions count"""
    try:
        result = db.execute(text(
            "SELECT COUNT(*) FROM user_sessions WHERE is_active = true AND expires_at > NOW()"
        )).scalar()
        count = result if result else 0
        return {"count": count}
    except Exception as e:
        print(f"❌ Active sessions count error: {e}")
        return {"count": 0}


@router.get("/security/alerts/count")
async def get_security_alerts_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, int]:
    """Get security alerts count (last 7 days)"""
    try:
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = db.execute(text(
            "SELECT COUNT(*) FROM security_events WHERE created_at >= :seven_days_ago AND severity IN ('medium', 'high', 'critical')"
        ), {"seven_days_ago": seven_days_ago}).scalar()
        count = result if result else 0
        return {"count": count}
    except Exception as e:
        print(f"❌ Security alerts count error: {e}")
        return {"count": 0}


@router.get("/auth/failed-logins/count")
async def get_failed_logins_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, int]:
    """Get failed logins count (last 24 hours)"""
    try:
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        result = db.execute(text(
            "SELECT COUNT(*) FROM audit_logs WHERE action = 'login_failed' AND timestamp >= :twenty_four_hours_ago"
        ), {"twenty_four_hours_ago": twenty_four_hours_ago}).scalar()
        count = result if result else 0
        return {"count": count}
    except Exception as e:
        print(f"❌ Failed logins count error: {e}")
        return {"count": 0}
