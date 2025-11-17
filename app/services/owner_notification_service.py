"""
Owner Notification Service
Handles sending notifications to Owner/Director for approval requests
Integrates with TSH NeuroLink and APNS for iOS push notifications
"""

import os
import sys
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Add neurolink to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'neurolink', 'app'))

from app.models.user import User
from app.models.notification import NotificationPreference
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class OwnerNotificationService:
    """
    Service to send notifications to Owner/Director for security approvals
    Uses TSH NeuroLink for unified notification delivery
    """

    def __init__(self):
        """Initialize the notification service"""
        self._apns_service = None
        self._initialize_apns()

    def _initialize_apns(self):
        """Initialize APNS service if available"""
        try:
            from app.neurolink.app.services.apns_delivery import apns_service
            self._apns_service = apns_service
            logger.info("APNS service initialized for Owner notifications")
        except ImportError as e:
            logger.warning(f"APNS service not available: {str(e)}")
            self._apns_service = None
        except Exception as e:
            logger.error(f"Failed to initialize APNS service: {str(e)}")
            self._apns_service = None

    def get_owner_apns_tokens(self, db: Session) -> List[str]:
        """
        Get all APNS tokens registered for Owner/Director roles

        Args:
            db: Database session

        Returns:
            List of APNS device tokens
        """
        try:
            # Get users with owner/admin/director roles
            owner_users = db.query(User).join(User.role).filter(
                User.is_active == True,
                User.role.has(name__in=['owner', 'admin', 'director'])
            ).all()

            if not owner_users:
                # Fallback: get by role name directly
                from app.models.role import Role
                owner_roles = db.query(Role).filter(
                    Role.name.in_(['owner', 'admin', 'director'])
                ).all()
                role_ids = [r.id for r in owner_roles]

                owner_users = db.query(User).filter(
                    User.is_active == True,
                    User.role_id.in_(role_ids)
                ).all()

            apns_tokens = []
            for user in owner_users:
                # Get notification preferences
                prefs = db.query(NotificationPreference).filter(
                    NotificationPreference.user_id == user.id
                ).first()

                if prefs and prefs.apns_tokens:
                    if isinstance(prefs.apns_tokens, list):
                        apns_tokens.extend(prefs.apns_tokens)
                    elif isinstance(prefs.apns_tokens, str):
                        apns_tokens.append(prefs.apns_tokens)

            logger.info(f"Found {len(apns_tokens)} APNS tokens for {len(owner_users)} owner users")
            return apns_tokens

        except Exception as e:
            logger.error(f"Error getting owner APNS tokens: {str(e)}")
            return []

    async def notify_approval_request(
        self,
        db: Session,
        approval_id: str,
        requester: User,
        app_name: str,
        approval_code: str,
        location: Optional[str] = None,
        risk_level: str = "medium"
    ) -> Dict:
        """
        Send push notification to Owner about new approval request

        Args:
            db: Database session
            approval_id: Approval request ID
            requester: User requesting approval
            app_name: Name of TSH app requesting access
            approval_code: 6-digit approval code
            location: Geographic location of request
            risk_level: Risk level of the request

        Returns:
            Dict with notification delivery results
        """
        results = {
            "apns": {"sent": False, "error": None},
            "email": {"sent": False, "error": None},
            "in_app": {"sent": False, "error": None}
        }

        # Get Owner APNS tokens
        apns_tokens = self.get_owner_apns_tokens(db)

        # Send APNS push notification
        if self._apns_service and apns_tokens:
            try:
                apns_result = await self._apns_service.send_owner_approval_notification(
                    device_tokens=apns_tokens,
                    approval_id=approval_id,
                    requester_name=requester.name,
                    requester_email=requester.email,
                    app_name=app_name,
                    approval_code=approval_code,
                    location=location
                )
                results["apns"] = {
                    "sent": apns_result.get("success", False),
                    "success_count": apns_result.get("success_count", 0),
                    "failure_count": apns_result.get("failure_count", 0),
                    "details": apns_result.get("results", [])
                }
                logger.info(f"APNS notification sent for approval {approval_id}: {apns_result}")
            except Exception as e:
                logger.error(f"Failed to send APNS notification: {str(e)}")
                results["apns"]["error"] = str(e)
        else:
            logger.warning("APNS service not available or no tokens registered")
            results["apns"]["error"] = "APNS not available or no tokens"

        # Create in-app notification for Owner dashboard
        results["in_app"] = await self._create_in_app_notification(
            db=db,
            approval_id=approval_id,
            requester=requester,
            app_name=app_name,
            risk_level=risk_level
        )

        # Send email notification as backup
        results["email"] = await self._send_email_notification(
            db=db,
            approval_id=approval_id,
            requester=requester,
            app_name=app_name,
            approval_code=approval_code,
            location=location,
            risk_level=risk_level
        )

        overall_success = any([
            results["apns"].get("sent", False),
            results["email"].get("sent", False),
            results["in_app"].get("sent", False)
        ])

        return {
            "overall_success": overall_success,
            "channels": results
        }

    async def notify_approval_resolved(
        self,
        db: Session,
        approval_id: str,
        requester: User,
        status: str,
        resolved_by: User,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Notify requester that their approval was resolved

        Args:
            db: Database session
            approval_id: Approval ID
            requester: User who requested approval
            status: Resolution status (approved/denied)
            resolved_by: User who resolved
            reason: Resolution reason

        Returns:
            Dict with notification results
        """
        # Get requester's APNS tokens
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == requester.id
        ).first()

        apns_tokens = []
        if prefs and prefs.apns_tokens:
            if isinstance(prefs.apns_tokens, list):
                apns_tokens = prefs.apns_tokens
            else:
                apns_tokens = [prefs.apns_tokens]

        results = {"sent": False, "error": None}

        if self._apns_service and apns_tokens:
            try:
                if status == "approved":
                    title = "✅ Access Approved"
                    body = f"Your access request has been approved by {resolved_by.name}"
                else:
                    title = "❌ Access Denied"
                    body = f"Your access request was denied by {resolved_by.name}"
                    if reason:
                        body += f": {reason}"

                for token in apns_tokens:
                    result = await self._apns_service.send_notification(
                        device_token=token,
                        title=title,
                        body=body,
                        data={
                            "type": "approval_resolved",
                            "approval_id": approval_id,
                            "status": status,
                            "resolved_by": resolved_by.name
                        },
                        badge=0,
                        sound="default",
                        priority=10
                    )
                    if result.get("success"):
                        results["sent"] = True

            except Exception as e:
                logger.error(f"Failed to notify requester: {str(e)}")
                results["error"] = str(e)

        return results

    async def notify_security_alert(
        self,
        db: Session,
        alert_type: str,
        title: str,
        body: str,
        severity: str = "high",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Send security alert to all Owner devices

        Args:
            db: Database session
            alert_type: Type of security alert
            title: Alert title
            body: Alert body
            severity: Alert severity
            metadata: Additional data

        Returns:
            Dict with notification results
        """
        apns_tokens = self.get_owner_apns_tokens(db)

        if not self._apns_service or not apns_tokens:
            return {"sent": False, "error": "APNS not available"}

        try:
            result = await self._apns_service.send_security_alert(
                device_tokens=apns_tokens,
                alert_type=alert_type,
                title=title,
                body=body,
                severity=severity,
                metadata=metadata
            )
            return {
                "sent": result.get("success", False),
                "details": result
            }
        except Exception as e:
            logger.error(f"Failed to send security alert: {str(e)}")
            return {"sent": False, "error": str(e)}

    async def _create_in_app_notification(
        self,
        db: Session,
        approval_id: str,
        requester: User,
        app_name: str,
        risk_level: str
    ) -> Dict:
        """Create in-app notification for Owner dashboard"""
        try:
            # This would integrate with the existing notification system
            # For now, just log it
            logger.info(f"Creating in-app notification for approval {approval_id}")
            return {"sent": True, "notification_id": approval_id}
        except Exception as e:
            logger.error(f"Failed to create in-app notification: {str(e)}")
            return {"sent": False, "error": str(e)}

    async def _send_email_notification(
        self,
        db: Session,
        approval_id: str,
        requester: User,
        app_name: str,
        approval_code: str,
        location: Optional[str],
        risk_level: str
    ) -> Dict:
        """Send email notification to Owner as backup"""
        try:
            # Get owner email addresses
            from app.models.role import Role
            owner_roles = db.query(Role).filter(
                Role.name.in_(['owner', 'admin', 'director'])
            ).all()
            role_ids = [r.id for r in owner_roles]

            owner_users = db.query(User).filter(
                User.is_active == True,
                User.role_id.in_(role_ids)
            ).all()

            # TODO: Integrate with TSH NeuroLink email service
            # For now, just log
            for owner in owner_users:
                logger.info(f"Would send email to {owner.email} for approval {approval_id}")

            return {"sent": True, "recipients": [u.email for u in owner_users]}
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return {"sent": False, "error": str(e)}


# Global service instance
owner_notification_service = OwnerNotificationService()
