"""
TSH NeuroLink - Push Notification Delivery Service
Uses Firebase Cloud Messaging (FCM) for mobile push notifications
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

import firebase_admin
from firebase_admin import credentials, messaging

from app.models import NeurolinkNotification, NeurolinkDeliveryLog
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        # Load Firebase credentials from environment or file
        if settings.FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        else:
            logger.warning("Firebase credentials not configured")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")


class PushNotificationService:
    """
    Handles push notification delivery using Firebase Cloud Messaging
    """

    async def send_notification_push(
        self,
        notification: NeurolinkNotification,
        fcm_tokens: List[str],
        db: AsyncSession
    ) -> Dict:
        """
        Send a notification as push notification to FCM tokens

        Args:
            notification: The notification object
            fcm_tokens: List of FCM device tokens
            db: Database session for logging

        Returns:
            Dict with status and results
        """
        if not fcm_tokens:
            logger.warning(f"No FCM tokens provided for notification {notification.id}")
            return {
                "success": False,
                "error": "No FCM tokens provided",
                "status": "failed"
            }

        results = {
            "success_count": 0,
            "failure_count": 0,
            "results": []
        }

        for token in fcm_tokens:
            try:
                # Create FCM message
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=notification.title,
                        body=notification.body[:200]  # Limit body length
                    ),
                    data={
                        "notification_id": str(notification.id),
                        "severity": notification.severity,
                        "action_url": notification.action_url or "",
                        "created_at": notification.created_at.isoformat()
                    },
                    token=token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            icon='notification_icon',
                            color='#3b82f6',
                            sound='default',
                            channel_id='tsh_erp_notifications'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                alert=messaging.ApsAlert(
                                    title=notification.title,
                                    body=notification.body[:200]
                                ),
                                badge=1,
                                sound='default'
                            )
                        )
                    )
                )

                # Send message
                response = messaging.send(message)

                # Log successful delivery
                await self._log_delivery(
                    db=db,
                    notification_id=notification.id,
                    recipient=token,
                    status="sent",
                    provider="fcm",
                    provider_message_id=response
                )

                results["success_count"] += 1
                results["results"].append({
                    "token": token[:10] + "...",  # Truncate for privacy
                    "status": "sent",
                    "message_id": response
                })

                logger.info(
                    f"Push notification sent successfully to token {token[:10]}... "
                    f"for notification {notification.id}"
                )

            except messaging.UnregisteredError:
                # Token is no longer valid
                logger.warning(f"FCM token {token[:10]}... is unregistered")
                await self._log_delivery(
                    db=db,
                    notification_id=notification.id,
                    recipient=token,
                    status="failed",
                    provider="fcm",
                    error_message="Token unregistered"
                )
                results["failure_count"] += 1
                results["results"].append({
                    "token": token[:10] + "...",
                    "status": "failed",
                    "error": "Token unregistered"
                })

            except messaging.InvalidArgumentError as e:
                logger.error(f"Invalid FCM token or message: {str(e)}")
                await self._log_delivery(
                    db=db,
                    notification_id=notification.id,
                    recipient=token,
                    status="failed",
                    provider="fcm",
                    error_message=f"Invalid argument: {str(e)}"
                )
                results["failure_count"] += 1
                results["results"].append({
                    "token": token[:10] + "...",
                    "status": "failed",
                    "error": str(e)
                })

            except Exception as e:
                logger.error(f"Failed to send push to token {token[:10]}...: {str(e)}")
                await self._log_delivery(
                    db=db,
                    notification_id=notification.id,
                    recipient=token,
                    status="failed",
                    provider="fcm",
                    error_message=str(e)
                )
                results["failure_count"] += 1
                results["results"].append({
                    "token": token[:10] + "...",
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "success": results["success_count"] > 0,
            "success_count": results["success_count"],
            "failure_count": results["failure_count"],
            "results": results["results"]
        }

    async def send_multicast_push(
        self,
        title: str,
        body: str,
        tokens: List[str],
        data: Optional[Dict] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """
        Send push notification to multiple tokens at once (more efficient)

        Args:
            title: Notification title
            body: Notification body
            tokens: List of FCM tokens
            data: Additional data payload
            db: Database session for logging

        Returns:
            Dict with results
        """
        if not tokens:
            return {
                "success": False,
                "error": "No tokens provided"
            }

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body[:200]
                ),
                data=data or {},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='notification_icon',
                        color='#3b82f6',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body[:200]
                            ),
                            badge=1,
                            sound='default'
                        )
                    )
                )
            )

            # Send multicast message
            response = messaging.send_multicast(message)

            logger.info(
                f"Multicast push sent: {response.success_count} successful, "
                f"{response.failure_count} failed out of {len(tokens)} total"
            )

            return {
                "success": response.success_count > 0,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [
                    {
                        "success": resp.success,
                        "message_id": resp.message_id if resp.success else None,
                        "error": str(resp.exception) if not resp.success else None
                    }
                    for resp in response.responses
                ]
            }

        except Exception as e:
            logger.error(f"Failed to send multicast push: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "success_count": 0,
                "failure_count": len(tokens)
            }

    async def send_announcement_push(
        self,
        announcement: Dict,
        fcm_tokens: List[str],
        db: AsyncSession
    ) -> Dict:
        """
        Send announcement as push notification

        Args:
            announcement: Announcement data
            fcm_tokens: List of FCM tokens
            db: Database session

        Returns:
            Dict with results
        """
        severity_icons = {
            "info": "📢",
            "warning": "⚠️",
            "urgent": "🚨",
            "critical": "🔴"
        }

        icon = severity_icons.get(announcement.get('severity', 'info'), "📢")

        return await self.send_multicast_push(
            title=f"{icon} {announcement['title']}",
            body=announcement.get('summary') or announcement['content'][:200],
            tokens=fcm_tokens,
            data={
                "type": "announcement",
                "announcement_id": str(announcement['id']),
                "severity": announcement.get('severity', 'info')
            },
            db=db
        )

    async def send_emergency_broadcast_push(
        self,
        broadcast: Dict,
        fcm_tokens: List[str],
        db: AsyncSession
    ) -> Dict:
        """
        Send emergency broadcast as push notification

        Args:
            broadcast: Emergency broadcast data
            fcm_tokens: List of FCM tokens
            db: Database session

        Returns:
            Dict with results
        """
        return await self.send_multicast_push(
            title=f"🚨 URGENT: {broadcast['title']}",
            body=broadcast['message'],
            tokens=fcm_tokens,
            data={
                "type": "emergency_broadcast",
                "broadcast_id": str(broadcast['id']),
                "requires_acknowledgment": "true"
            },
            db=db
        )

    async def send_topic_notification(
        self,
        title: str,
        body: str,
        topic: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Send notification to a topic (all users subscribed to the topic)

        Args:
            title: Notification title
            body: Notification body
            topic: Topic name
            data: Additional data

        Returns:
            Dict with result
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body[:200]
                ),
                data=data or {},
                topic=topic
            )

            response = messaging.send(message)

            logger.info(f"Topic notification sent to '{topic}': {response}")

            return {
                "success": True,
                "message_id": response
            }

        except Exception as e:
            logger.error(f"Failed to send topic notification to '{topic}': {str(e)}")
            return {
                "success": False,
                "error": str(e)
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
        """Log delivery attempt to database"""
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
            logger.error(f"Failed to log delivery: {str(e)}")
            await db.rollback()

    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict:
        """
        Subscribe tokens to a topic

        Args:
            tokens: List of FCM tokens
            topic: Topic name

        Returns:
            Dict with result
        """
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            logger.info(f"Subscribed {response.success_count} tokens to topic '{topic}'")
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            logger.error(f"Failed to subscribe to topic '{topic}': {str(e)}")
            return {"success": False, "error": str(e)}

    async def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> Dict:
        """
        Unsubscribe tokens from a topic

        Args:
            tokens: List of FCM tokens
            topic: Topic name

        Returns:
            Dict with result
        """
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            logger.info(f"Unsubscribed {response.success_count} tokens from topic '{topic}'")
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic '{topic}': {str(e)}")
            return {"success": False, "error": str(e)}
