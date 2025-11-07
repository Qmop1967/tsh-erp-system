"""
Dashboard Service - Business Logic for Dashboard Statistics

Created for Phase 5 P3 Batch 1 using Phase 4 patterns:
- Instance methods for better dependency injection
- Separation of concerns (statistics logic out of router)
- Error handling with graceful fallbacks

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P3 Batch 1 - Dashboard Router Migration
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import Depends

from app.models.user import User


class DashboardService:
    """
    Service for dashboard statistics and metrics.

    Handles all dashboard-related queries and calculations,
    replacing direct database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize dashboard service.

        Args:
            db: Database session
        """
        self.db = db

    # ========================================================================
    # Dashboard Statistics
    # ========================================================================

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard statistics.

        Returns:
            Dictionary with:
            - total_users: Active users count
            - active_sessions: Active session count
            - security_alerts: Security alerts (last 7 days)
            - failed_logins: Failed logins (last 24 hours)
            - last_updated: Timestamp
        """
        try:
            # Total users count
            total_users = self.get_users_count()

            # Active sessions count
            active_sessions = self.get_active_sessions_count()

            # Security alerts count (last 7 days)
            security_alerts = self.get_security_alerts_count()

            # Failed logins count (last 24 hours)
            failed_logins = self.get_failed_logins_count()

            return {
                "total_users": total_users,
                "active_sessions": active_sessions,
                "security_alerts": security_alerts,
                "failed_logins": failed_logins,
                "last_updated": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print(f"❌ Dashboard stats error: {e}")
            # Return zeros if tables don't exist yet, except for users which should always work
            return {
                "total_users": self.get_users_count(),
                "active_sessions": 0,
                "security_alerts": 0,
                "failed_logins": 0,
                "last_updated": datetime.utcnow().isoformat()
            }

    def get_users_count(self) -> int:
        """
        Get total active users count.

        Returns:
            Count of active users
        """
        try:
            count = self.db.query(func.count(User.id)).filter(
                User.is_active == True
            ).scalar()
            return count or 0
        except Exception as e:
            print(f"❌ Users count error: {e}")
            return 0

    def get_active_sessions_count(self) -> int:
        """
        Get active sessions count.

        Queries user_sessions table for active sessions.

        Returns:
            Count of active sessions
        """
        try:
            result = self.db.execute(text(
                "SELECT COUNT(*) FROM user_sessions WHERE is_active = true AND expires_at > NOW()"
            )).scalar()
            return result if result else 0
        except Exception as e:
            print(f"❌ Active sessions count error: {e}")
            return 0

    def get_security_alerts_count(self) -> int:
        """
        Get security alerts count (last 7 days).

        Queries security_events table for medium/high/critical alerts.

        Returns:
            Count of security alerts
        """
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            result = self.db.execute(text(
                "SELECT COUNT(*) FROM security_events WHERE created_at >= :seven_days_ago AND severity IN ('medium', 'high', 'critical')"
            ), {"seven_days_ago": seven_days_ago}).scalar()
            return result if result else 0
        except Exception as e:
            print(f"❌ Security alerts count error: {e}")
            return 0

    def get_failed_logins_count(self) -> int:
        """
        Get failed logins count (last 24 hours).

        Queries audit_logs table for login_failed actions.

        Returns:
            Count of failed logins
        """
        try:
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            result = self.db.execute(text(
                "SELECT COUNT(*) FROM audit_logs WHERE action = 'login_failed' AND timestamp >= :twenty_four_hours_ago"
            ), {"twenty_four_hours_ago": twenty_four_hours_ago}).scalar()
            return result if result else 0
        except Exception as e:
            print(f"❌ Failed logins count error: {e}")
            return 0


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """
    Dependency to get DashboardService instance.

    Usage in routers:
        @router.get("/stats")
        def get_stats(
            service: DashboardService = Depends(get_dashboard_service)
        ):
            return service.get_dashboard_stats()
    """
    return DashboardService(db)
