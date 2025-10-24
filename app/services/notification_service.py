"""
TSH ERP Notification Service
Handles notification creation, delivery, and management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    NotificationLog,
    NotificationType,
    NotificationPriority,
    NotificationChannel
)
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationFromTemplate,
    NotificationListResponse,
    NotificationStats
)


class NotificationService:
    """Service for managing notifications"""

    @staticmethod
    def create_notification(
        db: Session,
        notification_data: NotificationCreate
    ) -> Notification:
        """Create a new notification"""

        # Check user preferences
        preference = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == notification_data.user_id
        ).first()

        # Apply user preferences
        if preference and not preference.enabled:
            return None  # User has disabled notifications

        # Filter by priority
        if preference and notification_data.priority.value < preference.min_priority.value:
            return None  # Below user's minimum priority

        # Check quiet hours
        if preference and preference.quiet_hours_enabled:
            now = datetime.now().time()
            if NotificationService._is_quiet_hours(
                now,
                preference.quiet_hours_start,
                preference.quiet_hours_end
            ):
                # Queue for later delivery
                pass

        # Create notification
        notification = Notification(
            **notification_data.model_dump()
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Trigger delivery based on channels
        NotificationService._deliver_notification(db, notification, preference)

        return notification

    @staticmethod
    def create_bulk_notifications(
        db: Session,
        user_ids: List[int],
        notification_data: Dict[str, Any]
    ) -> List[Notification]:
        """Create notifications for multiple users"""
        notifications = []

        for user_id in user_ids:
            notif_data = NotificationCreate(
                user_id=user_id,
                **notification_data
            )
            notification = NotificationService.create_notification(db, notif_data)
            if notification:
                notifications.append(notification)

        return notifications

    @staticmethod
    def create_from_template(
        db: Session,
        template_code: str,
        user_id: int,
        variables: Dict[str, Any],
        tenant_id: Optional[int] = None,
        channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Notification]:
        """Create notification from template"""

        # Get template
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.code == template_code,
            NotificationTemplate.is_active == True
        ).first()

        if not template:
            raise ValueError(f"Template '{template_code}' not found")

        # Render template with variables
        title = template.title_template.format(**variables)
        message = template.message_template.format(**variables)

        # Create notification
        notification_data = NotificationCreate(
            user_id=user_id,
            tenant_id=tenant_id,
            type=template.type,
            priority=template.priority,
            title=title,
            message=message,
            icon=template.icon,
            color=template.color,
            action_url=template.default_action_url,
            action_label=template.default_action_label,
            channels=channels or template.default_channels,
            meta_data=metadata
        )

        return NotificationService.create_notification(db, notification_data)

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None,
        priority: Optional[NotificationPriority] = None
    ) -> NotificationListResponse:
        """Get user's notifications with filters"""

        # Build query
        query = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_archived == False
        )

        if unread_only:
            query = query.filter(Notification.is_read == False)

        if notification_type:
            query = query.filter(Notification.type == notification_type)

        if priority:
            query = query.filter(Notification.priority == priority)

        # Get total count
        total = query.count()

        # Get unread count
        unread_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_archived == False
        ).count()

        # Get notifications
        notifications = query.order_by(desc(Notification.created_at))\
            .offset(skip).limit(limit).all()

        return NotificationListResponse(
            notifications=notifications,
            total=total,
            unread_count=unread_count,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=skip + limit < total
        )

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """Mark notification as read"""

        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """Mark all notifications as read for user"""

        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })

        db.commit()
        return count

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Delete a notification"""

        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return False

        db.delete(notification)
        db.commit()

        return True

    @staticmethod
    def archive_notification(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """Archive a notification"""

        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return None

        notification.is_archived = True
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def get_notification_stats(db: Session, user_id: int) -> NotificationStats:
        """Get notification statistics for user"""

        # Total notifications
        total = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_archived == False
        ).count()

        # Unread count
        unread = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_archived == False
        ).count()

        # Read count
        read = total - unread

        # Archived count
        archived = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_archived == True
        ).count()

        # By priority
        by_priority = {}
        priority_stats = db.query(
            Notification.priority,
            func.count(Notification.id)
        ).filter(
            Notification.user_id == user_id,
            Notification.is_archived == False
        ).group_by(Notification.priority).all()

        for priority, count in priority_stats:
            by_priority[priority.value] = count

        # By type
        by_type = {}
        type_stats = db.query(
            Notification.type,
            func.count(Notification.id)
        ).filter(
            Notification.user_id == user_id,
            Notification.is_archived == False
        ).group_by(Notification.type).all()

        for notif_type, count in type_stats:
            by_type[notif_type.value] = count

        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.created_at >= seven_days_ago
        ).order_by(desc(Notification.created_at)).limit(10).all()

        recent_activity = [
            {
                "id": n.id,
                "type": n.type.value,
                "title": n.title,
                "created_at": n.created_at.isoformat()
            }
            for n in recent
        ]

        return NotificationStats(
            total_notifications=total,
            unread_count=unread,
            read_count=read,
            archived_count=archived,
            by_priority=by_priority,
            by_type=by_type,
            recent_activity=recent_activity
        )

    # Private helper methods

    @staticmethod
    def _is_quiet_hours(now_time, start_str: str, end_str: str) -> bool:
        """Check if current time is within quiet hours"""
        if not start_str or not end_str:
            return False

        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()

        if start < end:
            return start <= now_time <= end
        else:  # Quiet hours span midnight
            return now_time >= start or now_time <= end

    @staticmethod
    def _deliver_notification(
        db: Session,
        notification: Notification,
        preference: Optional[NotificationPreference]
    ):
        """Deliver notification through configured channels"""

        sent_via = []
        delivery_status = {}

        # In-app notifications are always delivered
        sent_via.append("in_app")
        delivery_status["in_app"] = "delivered"

        # Push notifications
        if "push" in notification.channels:
            if preference and preference.enable_push and preference.fcm_tokens:
                # Send push notification (implement FCM integration)
                success = NotificationService._send_push_notification(
                    notification,
                    preference.fcm_tokens
                )
                sent_via.append("push")
                delivery_status["push"] = "sent" if success else "failed"

        # Email notifications
        if "email" in notification.channels:
            if preference and preference.enable_email and preference.email_address:
                # Send email (implement email integration)
                success = NotificationService._send_email_notification(
                    notification,
                    preference.email_address
                )
                sent_via.append("email")
                delivery_status["email"] = "sent" if success else "failed"

        # Update notification with delivery info
        notification.sent_via = sent_via
        notification.delivery_status = delivery_status
        db.commit()

    @staticmethod
    def _send_push_notification(notification: Notification, tokens: List[str]) -> bool:
        """Send push notification via FCM (placeholder - implement with firebase-admin)"""
        # TODO: Implement Firebase Cloud Messaging integration
        return True

    @staticmethod
    def _send_email_notification(notification: Notification, email: str) -> bool:
        """Send email notification (placeholder - implement with email service)"""
        # TODO: Implement email service integration
        return True
