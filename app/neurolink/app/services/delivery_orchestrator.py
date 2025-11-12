"""
TSH NeuroLink - Delivery Orchestrator
Coordinates notification delivery across multiple channels
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import NeurolinkNotification, NeurolinkUserPreferences
from app.services.email_delivery import EmailDeliveryService
from app.services.push_delivery import PushNotificationService
from app.config import settings

logger = logging.getLogger(__name__)


class DeliveryOrchestrator:
    """
    Orchestrates notification delivery across all available channels
    """

    def __init__(self):
        self.email_service = EmailDeliveryService()
        self.push_service = PushNotificationService()

    async def deliver_notification(
        self,
        notification: NeurolinkNotification,
        user: Dict,
        db: AsyncSession,
        bypass_preferences: bool = False
    ) -> Dict:
        """
        Deliver notification through configured channels

        Args:
            notification: Notification to deliver
            user: User object with email, fcm_tokens, etc.
            db: Database session
            bypass_preferences: Bypass user preferences (for emergency broadcasts)

        Returns:
            Dict with delivery results for each channel
        """
        results = {
            "notification_id": str(notification.id),
            "user_id": user['id'],
            "channels": {},
            "overall_success": False
        }

        # Get user preferences
        if not bypass_preferences:
            preferences = await self._get_user_preferences(db, user['id'])

            # Check quiet hours
            if self._is_in_quiet_hours(preferences):
                logger.info(
                    f"Skipping delivery to user {user['id']} - quiet hours active"
                )
                return results
        else:
            preferences = None

        # Determine which channels to use
        channels_to_use = notification.channels or []

        if notification.bypass_preferences:
            bypass_preferences = True

        # Deliver via each channel
        for channel in channels_to_use:
            try:
                if channel == 'email':
                    if bypass_preferences or self._can_use_email(preferences):
                        email_result = await self._deliver_via_email(
                            notification,
                            user,
                            db
                        )
                        results["channels"]["email"] = email_result
                        if email_result.get("success"):
                            results["overall_success"] = True

                elif channel == 'push':
                    if bypass_preferences or self._can_use_push(preferences):
                        push_result = await self._deliver_via_push(
                            notification,
                            user,
                            db
                        )
                        results["channels"]["push"] = push_result
                        if push_result.get("success"):
                            results["overall_success"] = True

                elif channel == 'in_app':
                    # In-app is always delivered (just stored in database)
                    results["channels"]["in_app"] = {"success": True, "status": "stored"}
                    results["overall_success"] = True

                elif channel == 'sms':
                    if settings.sms_enabled and (bypass_preferences or self._can_use_sms(preferences)):
                        sms_result = await self._deliver_via_sms(
                            notification,
                            user,
                            db
                        )
                        results["channels"]["sms"] = sms_result
                        if sms_result.get("success"):
                            results["overall_success"] = True

                elif channel == 'whatsapp':
                    if bypass_preferences or True:  # WhatsApp integration exists
                        whatsapp_result = await self._deliver_via_whatsapp(
                            notification,
                            user,
                            db
                        )
                        results["channels"]["whatsapp"] = whatsapp_result
                        if whatsapp_result.get("success"):
                            results["overall_success"] = True

            except Exception as e:
                logger.error(f"Error delivering via {channel}: {str(e)}")
                results["channels"][channel] = {
                    "success": False,
                    "error": str(e)
                }

        # Update notification delivery status
        if results["overall_success"]:
            notification.status = 'delivered'
            notification.delivered_at = datetime.utcnow()
            await db.commit()

        return results

    async def deliver_announcement(
        self,
        announcement: Dict,
        users: List[Dict],
        db: AsyncSession
    ) -> Dict:
        """
        Deliver announcement to multiple users

        Args:
            announcement: Announcement data
            users: List of user objects
            db: Database session

        Returns:
            Dict with delivery statistics
        """
        results = {
            "total_users": len(users),
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "channels_used": announcement.get('delivery_channels', ['in_app'])
        }

        for user in users:
            try:
                # Deliver via email if configured
                if 'email' in results["channels_used"]:
                    email_result = await self.email_service.send_announcement_email(
                        announcement=announcement,
                        recipient_email=user['email'],
                        recipient_name=user['full_name'],
                        db=db
                    )
                    if email_result.get("success"):
                        results["successful_deliveries"] += 1

                # Deliver via push if configured
                if 'push' in results["channels_used"] and user.get('fcm_tokens'):
                    push_result = await self.push_service.send_announcement_push(
                        announcement=announcement,
                        fcm_tokens=user['fcm_tokens'],
                        db=db
                    )
                    if push_result.get("success"):
                        results["successful_deliveries"] += 1

            except Exception as e:
                logger.error(f"Error delivering announcement to user {user['id']}: {str(e)}")
                results["failed_deliveries"] += 1

        return results

    async def deliver_emergency_broadcast(
        self,
        broadcast: Dict,
        users: List[Dict],
        db: AsyncSession
    ) -> Dict:
        """
        Deliver emergency broadcast to all users via ALL channels

        Args:
            broadcast: Emergency broadcast data
            users: List of user objects
            db: Database session

        Returns:
            Dict with delivery statistics
        """
        results = {
            "total_users": len(users),
            "deliveries": {
                "email": 0,
                "push": 0,
                "sms": 0,
                "whatsapp": 0,
                "in_app": 0
            },
            "failed_users": []
        }

        for user in users:
            user_delivered = False

            try:
                # Email
                if user.get('email'):
                    email_result = await self.email_service.send_emergency_broadcast_email(
                        broadcast=broadcast,
                        recipient_email=user['email'],
                        recipient_name=user['full_name'],
                        db=db
                    )
                    if email_result.get("success"):
                        results["deliveries"]["email"] += 1
                        user_delivered = True

                # Push notifications
                if user.get('fcm_tokens'):
                    push_result = await self.push_service.send_emergency_broadcast_push(
                        broadcast=broadcast,
                        fcm_tokens=user['fcm_tokens'],
                        db=db
                    )
                    if push_result.get("success"):
                        results["deliveries"]["push"] += 1
                        user_delivered = True

                # SMS (if enabled)
                if settings.sms_enabled and user.get('phone'):
                    # SMS delivery implementation
                    results["deliveries"]["sms"] += 1
                    user_delivered = True

                # WhatsApp (if user has WhatsApp)
                if user.get('whatsapp_phone'):
                    # WhatsApp delivery implementation
                    results["deliveries"]["whatsapp"] += 1
                    user_delivered = True

                # In-app (always)
                results["deliveries"]["in_app"] += 1
                user_delivered = True

                if not user_delivered:
                    results["failed_users"].append({
                        "user_id": user['id'],
                        "reason": "No valid delivery channels"
                    })

            except Exception as e:
                logger.error(f"Error delivering emergency broadcast to user {user['id']}: {str(e)}")
                results["failed_users"].append({
                    "user_id": user['id'],
                    "reason": str(e)
                })

        return results

    async def _deliver_via_email(
        self,
        notification: NeurolinkNotification,
        user: Dict,
        db: AsyncSession
    ) -> Dict:
        """Deliver notification via email"""
        if not user.get('email'):
            return {"success": False, "error": "No email address"}

        return await self.email_service.send_notification_email(
            notification=notification,
            recipient_email=user['email'],
            recipient_name=user.get('full_name', 'User'),
            db=db
        )

    async def _deliver_via_push(
        self,
        notification: NeurolinkNotification,
        user: Dict,
        db: AsyncSession
    ) -> Dict:
        """Deliver notification via push notification"""
        fcm_tokens = user.get('fcm_tokens', [])
        if not fcm_tokens:
            return {"success": False, "error": "No FCM tokens registered"}

        return await self.push_service.send_notification_push(
            notification=notification,
            fcm_tokens=fcm_tokens,
            db=db
        )

    async def _deliver_via_sms(
        self,
        notification: NeurolinkNotification,
        user: Dict,
        db: AsyncSession
    ) -> Dict:
        """Deliver notification via SMS (Twilio)"""
        # Placeholder for SMS delivery
        # Implement with Twilio in Phase 4
        return {"success": False, "error": "SMS not implemented yet"}

    async def _deliver_via_whatsapp(
        self,
        notification: NeurolinkNotification,
        user: Dict,
        db: AsyncSession
    ) -> Dict:
        """Deliver notification via WhatsApp"""
        # Integration with existing WhatsApp service
        # Use the existing whatsapp_integration module
        return {"success": False, "error": "WhatsApp integration pending"}

    async def _get_user_preferences(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[NeurolinkUserPreferences]:
        """Get user notification preferences"""
        stmt = select(NeurolinkUserPreferences).where(
            NeurolinkUserPreferences.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def _is_in_quiet_hours(self, preferences: Optional[NeurolinkUserPreferences]) -> bool:
        """Check if current time is in user's quiet hours"""
        if not preferences or not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return False

        now = datetime.utcnow().time()
        start = preferences.quiet_hours_start
        end = preferences.quiet_hours_end

        # Handle overnight quiet hours (e.g., 10 PM to 7 AM)
        if start > end:
            return now >= start or now <= end
        else:
            return start <= now <= end

    def _can_use_email(self, preferences: Optional[NeurolinkUserPreferences]) -> bool:
        """Check if email delivery is allowed"""
        if not preferences:
            return True
        return preferences.email_enabled and 'email' in (preferences.enabled_channels or [])

    def _can_use_push(self, preferences: Optional[NeurolinkUserPreferences]) -> bool:
        """Check if push notification delivery is allowed"""
        if not preferences:
            return True
        return 'push' in (preferences.enabled_channels or [])

    def _can_use_sms(self, preferences: Optional[NeurolinkUserPreferences]) -> bool:
        """Check if SMS delivery is allowed"""
        if not preferences:
            return False
        return preferences.sms_enabled and 'sms' in (preferences.enabled_channels or [])


# Global orchestrator instance
orchestrator = DeliveryOrchestrator()
