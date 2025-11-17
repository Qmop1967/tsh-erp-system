"""
TSH NeuroLink - Apple Push Notification Service (APNS) Delivery
Native APNS implementation for iOS push notifications
NO Firebase/Twilio dependencies - Direct Apple integration
"""

import os
import json
import jwt
import time
import httpx
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.models import NeurolinkNotification, NeurolinkDeliveryLog
from app.config import settings

logger = logging.getLogger(__name__)


class APNSService:
    """
    Native Apple Push Notification Service delivery
    Uses JWT-based token authentication (recommended for production)
    """

    # APNS endpoints
    APNS_PRODUCTION = "https://api.push.apple.com"
    APNS_SANDBOX = "https://api.sandbox.push.apple.com"

    # Token expiration (60 minutes, Apple requirement)
    TOKEN_EXPIRATION = 3600

    def __init__(self):
        """Initialize APNS service with configuration"""
        self.team_id = getattr(settings, 'APNS_TEAM_ID', os.getenv('APNS_TEAM_ID'))
        self.key_id = getattr(settings, 'APNS_KEY_ID', os.getenv('APNS_KEY_ID'))
        self.bundle_id = getattr(settings, 'APNS_BUNDLE_ID', os.getenv('APNS_BUNDLE_ID', 'com.tsh.securityconsole'))
        self.is_production = getattr(settings, 'APNS_PRODUCTION', os.getenv('APNS_PRODUCTION', 'false').lower() == 'true')

        # Path to .p8 key file
        self.key_path = getattr(settings, 'APNS_KEY_PATH', os.getenv('APNS_KEY_PATH'))
        self.private_key = None

        # JWT token cache
        self._token = None
        self._token_generated_at = 0

        # Load private key
        self._load_private_key()

        # Select endpoint
        self.endpoint = self.APNS_PRODUCTION if self.is_production else self.APNS_SANDBOX

        logger.info(f"APNS Service initialized - {'Production' if self.is_production else 'Sandbox'}")

    def _load_private_key(self):
        """Load APNS private key from .p8 file"""
        if self.key_path and os.path.exists(self.key_path):
            try:
                with open(self.key_path, 'r') as f:
                    self.private_key = f.read()
                logger.info(f"APNS private key loaded from {self.key_path}")
            except Exception as e:
                logger.error(f"Failed to load APNS private key: {str(e)}")
        else:
            # Try environment variable
            self.private_key = getattr(settings, 'APNS_PRIVATE_KEY', os.getenv('APNS_PRIVATE_KEY'))
            if self.private_key:
                logger.info("APNS private key loaded from environment")
            else:
                logger.warning("APNS private key not configured - push notifications disabled")

    def _generate_token(self) -> str:
        """
        Generate JWT token for APNS authentication
        Token is valid for 60 minutes and cached for reuse
        """
        current_time = time.time()

        # Check if cached token is still valid (refresh 5 minutes before expiry)
        if self._token and (current_time - self._token_generated_at) < (self.TOKEN_EXPIRATION - 300):
            return self._token

        if not all([self.team_id, self.key_id, self.private_key]):
            raise ValueError("APNS credentials not configured")

        # Create JWT token
        headers = {
            "alg": "ES256",
            "kid": self.key_id
        }

        payload = {
            "iss": self.team_id,
            "iat": int(current_time)
        }

        self._token = jwt.encode(payload, self.private_key, algorithm="ES256", headers=headers)
        self._token_generated_at = current_time

        logger.debug("Generated new APNS JWT token")
        return self._token

    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        badge: Optional[int] = None,
        sound: str = "default",
        priority: int = 10,  # 10 = immediate, 5 = consider power
        category: Optional[str] = None,
        thread_id: Optional[str] = None,
        collapse_id: Optional[str] = None,
        expiration: Optional[int] = None,
        mutable_content: bool = False,
        content_available: bool = False
    ) -> Dict:
        """
        Send push notification to single iOS device via APNS

        Args:
            device_token: APNS device token (hex string)
            title: Notification title
            body: Notification body
            data: Custom data payload
            badge: Badge number to display
            sound: Sound to play (default, or custom sound name)
            priority: 10 for immediate, 5 for power consideration
            category: Notification category for actions
            thread_id: Thread identifier for grouping
            collapse_id: Collapse identifier for replacing notifications
            expiration: Expiration timestamp (0 = immediate, None = 30 days)
            mutable_content: Allow Notification Service Extension to modify
            content_available: Silent notification for background processing

        Returns:
            Dict with success status and details
        """
        if not self.private_key:
            return {
                "success": False,
                "error": "APNS not configured",
                "status": "failed"
            }

        try:
            # Generate authentication token
            auth_token = self._generate_token()

            # Build APNS payload
            aps = {
                "alert": {
                    "title": title,
                    "body": body[:4096]  # APNS limit
                },
                "sound": sound
            }

            if badge is not None:
                aps["badge"] = badge

            if category:
                aps["category"] = category

            if thread_id:
                aps["thread-id"] = thread_id

            if mutable_content:
                aps["mutable-content"] = 1

            if content_available:
                aps["content-available"] = 1

            payload = {"aps": aps}

            # Add custom data
            if data:
                payload.update(data)

            # Ensure payload size < 4KB
            payload_json = json.dumps(payload)
            if len(payload_json.encode('utf-8')) > 4096:
                # Truncate body if needed
                max_body = 4096 - len(json.dumps({**payload, "aps": {**aps, "alert": {"title": title, "body": ""}}}).encode('utf-8'))
                aps["alert"]["body"] = body[:max_body]
                payload = {"aps": aps}
                if data:
                    payload.update(data)

            # Build request headers
            headers = {
                "authorization": f"bearer {auth_token}",
                "apns-topic": self.bundle_id,
                "apns-push-type": "alert" if not content_available else "background",
                "apns-priority": str(priority)
            }

            if collapse_id:
                headers["apns-collapse-id"] = collapse_id

            if expiration is not None:
                headers["apns-expiration"] = str(expiration)

            # Send request to APNS
            url = f"{self.endpoint}/3/device/{device_token}"

            async with httpx.AsyncClient(http2=True, timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )

            # Check response
            if response.status_code == 200:
                apns_id = response.headers.get("apns-id", "")
                logger.info(f"APNS notification sent successfully: {apns_id}")
                return {
                    "success": True,
                    "apns_id": apns_id,
                    "status": "sent"
                }
            else:
                error_body = response.json() if response.content else {}
                reason = error_body.get("reason", "Unknown error")
                logger.error(f"APNS error: {response.status_code} - {reason}")
                return {
                    "success": False,
                    "error": reason,
                    "status_code": response.status_code,
                    "status": "failed"
                }

        except jwt.exceptions.PyJWTError as e:
            logger.error(f"APNS JWT error: {str(e)}")
            return {"success": False, "error": f"JWT error: {str(e)}", "status": "failed"}
        except httpx.HTTPError as e:
            logger.error(f"APNS HTTP error: {str(e)}")
            return {"success": False, "error": f"HTTP error: {str(e)}", "status": "failed"}
        except Exception as e:
            logger.error(f"APNS delivery error: {str(e)}")
            return {"success": False, "error": str(e), "status": "failed"}

    async def send_owner_approval_notification(
        self,
        device_tokens: List[str],
        approval_id: str,
        requester_name: str,
        requester_email: str,
        app_name: str,
        approval_code: str,
        location: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """
        Send high-priority approval request to Owner's iOS device

        Args:
            device_tokens: Owner's APNS device tokens
            approval_id: Approval request ID
            requester_name: Name of user requesting approval
            requester_email: Email of user requesting approval
            app_name: TSH app requesting access
            approval_code: 6-digit approval code
            location: Location of request
            db: Database session for logging

        Returns:
            Dict with delivery results
        """
        if not device_tokens:
            return {"success": False, "error": "No APNS tokens provided"}

        title = "🔐 Login Approval Required"
        body = f"{requester_name} ({requester_email}) is requesting access to {app_name}"
        if location:
            body += f" from {location}"

        data = {
            "type": "owner_approval",
            "approval_id": approval_id,
            "approval_code": approval_code,
            "requester_name": requester_name,
            "requester_email": requester_email,
            "app_name": app_name,
            "location": location or "",
            "timestamp": datetime.utcnow().isoformat()
        }

        results = {
            "success_count": 0,
            "failure_count": 0,
            "results": []
        }

        for token in device_tokens:
            result = await self.send_notification(
                device_token=token,
                title=title,
                body=body,
                data=data,
                badge=1,
                sound="default",
                priority=10,  # High priority for approvals
                category="OWNER_APPROVAL",  # For actionable notification
                mutable_content=True  # Allow modification by extension
            )

            if result.get("success"):
                results["success_count"] += 1
            else:
                results["failure_count"] += 1

            results["results"].append({
                "token": token[:10] + "...",
                **result
            })

            # Log delivery
            if db:
                await self._log_delivery(
                    db=db,
                    notification_id=approval_id,
                    recipient=token,
                    status="sent" if result.get("success") else "failed",
                    provider="apns",
                    provider_message_id=result.get("apns_id"),
                    error_message=result.get("error")
                )

        return {
            "success": results["success_count"] > 0,
            **results
        }

    async def send_security_alert(
        self,
        device_tokens: List[str],
        alert_type: str,
        title: str,
        body: str,
        severity: str = "high",
        metadata: Optional[Dict] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """
        Send security alert to Owner's iOS device

        Args:
            device_tokens: APNS device tokens
            alert_type: Type of security alert
            title: Alert title
            body: Alert body
            severity: low, medium, high, critical
            metadata: Additional alert data
            db: Database session

        Returns:
            Dict with delivery results
        """
        severity_badges = {
            "low": 1,
            "medium": 5,
            "high": 10,
            "critical": 99
        }

        data = {
            "type": "security_alert",
            "alert_type": alert_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }

        results = {
            "success_count": 0,
            "failure_count": 0,
            "results": []
        }

        for token in device_tokens:
            result = await self.send_notification(
                device_token=token,
                title=f"⚠️ {title}",
                body=body,
                data=data,
                badge=severity_badges.get(severity, 1),
                sound="default",
                priority=10 if severity in ["high", "critical"] else 5,
                category="SECURITY_ALERT"
            )

            if result.get("success"):
                results["success_count"] += 1
            else:
                results["failure_count"] += 1

            results["results"].append({
                "token": token[:10] + "...",
                **result
            })

        return {
            "success": results["success_count"] > 0,
            **results
        }

    async def send_session_kill_notification(
        self,
        device_tokens: List[str],
        session_id: str,
        killed_by: str,
        reason: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """
        Notify device that its session was killed

        Args:
            device_tokens: APNS device tokens
            session_id: Killed session ID
            killed_by: Who killed the session
            reason: Reason for killing
            db: Database session

        Returns:
            Dict with delivery results
        """
        title = "Session Terminated"
        body = f"Your session was terminated by {killed_by}"
        if reason:
            body += f": {reason}"

        data = {
            "type": "session_terminated",
            "session_id": session_id,
            "killed_by": killed_by,
            "reason": reason or "",
            "timestamp": datetime.utcnow().isoformat(),
            "action": "logout"  # iOS app should logout immediately
        }

        results = {
            "success_count": 0,
            "failure_count": 0,
            "results": []
        }

        for token in device_tokens:
            result = await self.send_notification(
                device_token=token,
                title=title,
                body=body,
                data=data,
                badge=0,  # Clear badge
                sound="default",
                priority=10,
                content_available=True  # Trigger background processing
            )

            if result.get("success"):
                results["success_count"] += 1
            else:
                results["failure_count"] += 1

            results["results"].append({
                "token": token[:10] + "...",
                **result
            })

        return {
            "success": results["success_count"] > 0,
            **results
        }

    async def _log_delivery(
        self,
        db: AsyncSession,
        notification_id: str,
        recipient: str,
        status: str,
        provider: str,
        provider_message_id: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log APNS delivery attempt to database"""
        try:
            log_data = {
                "notification_id": notification_id,
                "channel": "push",
                "recipient": recipient,
                "status": status,
                "provider": provider,
                "provider_message_id": provider_message_id,
                "error_message": error_message,
                "sent_at": datetime.utcnow() if status == "sent" else None,
                "failed_at": datetime.utcnow() if status == "failed" else None
            }

            stmt = insert(NeurolinkDeliveryLog).values(**log_data)
            await db.execute(stmt)
            await db.commit()

        except Exception as e:
            logger.error(f"Failed to log APNS delivery: {str(e)}")
            await db.rollback()

    async def validate_device_token(self, device_token: str) -> bool:
        """
        Validate if a device token is properly formatted

        Args:
            device_token: APNS device token

        Returns:
            bool: True if valid format
        """
        # APNS tokens are 64 hex characters
        if not device_token:
            return False

        # Remove any spaces or angle brackets
        token = device_token.replace(" ", "").replace("<", "").replace(">", "")

        # Check length and hex format
        if len(token) != 64:
            return False

        try:
            int(token, 16)
            return True
        except ValueError:
            return False


# Global APNS service instance
apns_service = APNSService()
