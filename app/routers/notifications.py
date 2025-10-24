"""
TSH ERP Notification API Router
Provides REST endpoints for notification management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.notification import NotificationType, NotificationPriority
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
    NotificationFromTemplate,
    NotificationListResponse,
    NotificationBulkCreate,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationStats,
    NotificationSettingsResponse,
    DeviceTokenRequest,
    BulkMarkAsRead,
    BulkDelete,
    BulkArchive
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ===============================================
# Notification CRUD Operations
# ===============================================

@router.post("", response_model=NotificationResponse, status_code=201)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification"""
    created_notification = NotificationService.create_notification(db, notification)

    if not created_notification:
        raise HTTPException(
            status_code=400,
            detail="Notification not created - user preferences may have blocked it"
        )

    return created_notification


@router.post("/bulk", status_code=201)
def create_bulk_notifications(
    bulk_data: NotificationBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notifications for multiple users"""
    notifications = NotificationService.create_bulk_notifications(
        db,
        bulk_data.user_ids,
        bulk_data.notification.model_dump()
    )

    return {
        "created_count": len(notifications),
        "notifications": notifications
    }


@router.post("/template", response_model=NotificationResponse, status_code=201)
def create_notification_from_template(
    template_data: NotificationFromTemplate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notification from template"""
    try:
        notification = NotificationService.create_from_template(
            db,
            template_code=template_data.template_code,
            user_id=template_data.user_id,
            variables=template_data.variables,
            tenant_id=template_data.tenant_id,
            channels=template_data.channels,
            metadata=template_data.meta_data
        )

        if not notification:
            raise HTTPException(
                status_code=400,
                detail="Notification not created - user preferences may have blocked it"
            )

        return notification

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=NotificationListResponse)
def get_user_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    notification_type: Optional[NotificationType] = None,
    priority: Optional[NotificationPriority] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's notifications with filters"""
    return NotificationService.get_user_notifications(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        notification_type=notification_type,
        priority=priority
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single notification"""
    from app.models.notification import Notification

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    notification = NotificationService.mark_as_read(
        db,
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.put("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for current user"""
    count = NotificationService.mark_all_as_read(db, current_user.id)

    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    success = NotificationService.delete_notification(
        db,
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return None


@router.put("/{notification_id}/archive", response_model=NotificationResponse)
def archive_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a notification"""
    notification = NotificationService.archive_notification(
        db,
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


# ===============================================
# Bulk Operations
# ===============================================

@router.post("/bulk/mark-read")
def bulk_mark_as_read(
    bulk_data: BulkMarkAsRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark multiple notifications as read"""
    from app.models.notification import Notification

    count = db.query(Notification).filter(
        Notification.id.in_(bulk_data.notification_ids),
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update(
        {"is_read": True, "read_at": datetime.utcnow()},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.post("/bulk/delete")
def bulk_delete_notifications(
    bulk_data: BulkDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete multiple notifications"""
    from app.models.notification import Notification

    count = db.query(Notification).filter(
        Notification.id.in_(bulk_data.notification_ids),
        Notification.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.commit()

    return {
        "message": f"Deleted {count} notifications",
        "count": count
    }


@router.post("/bulk/archive")
def bulk_archive_notifications(
    bulk_data: BulkArchive,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive multiple notifications"""
    from app.models.notification import Notification

    count = db.query(Notification).filter(
        Notification.id.in_(bulk_data.notification_ids),
        Notification.user_id == current_user.id,
        Notification.is_archived == False
    ).update(
        {"is_archived": True},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": f"Archived {count} notifications",
        "count": count
    }


# ===============================================
# Statistics and Analytics
# ===============================================

@router.get("/stats", response_model=NotificationStats)
def get_notification_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for current user"""
    return NotificationService.get_notification_stats(db, current_user.id)


# ===============================================
# User Preferences
# ===============================================

@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's notification preferences"""
    from app.models.notification import NotificationPreference

    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()

    # Create default preferences if not exists
    if not preference:
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)

    return preference


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_notification_preferences(
    preferences_update: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's notification preferences"""
    from app.models.notification import NotificationPreference

    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()

    # Create if not exists
    if not preference:
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)

    # Update fields
    update_data = preferences_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preference, field, value)

    db.commit()
    db.refresh(preference)

    return preference


@router.post("/device-token")
def register_device_token(
    device_data: DeviceTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register device token for push notifications"""
    from app.models.notification import NotificationPreference

    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()

    # Create if not exists
    if not preference:
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
        db.flush()

    # Add token based on platform
    if device_data.platform in ['android', 'web']:
        # FCM token
        if not preference.fcm_tokens:
            preference.fcm_tokens = []

        if device_data.token not in preference.fcm_tokens:
            preference.fcm_tokens.append(device_data.token)
            preference.fcm_tokens = list(set(preference.fcm_tokens))  # Deduplicate

    elif device_data.platform == 'ios':
        # APNS token
        if not preference.apns_tokens:
            preference.apns_tokens = []

        if device_data.token not in preference.apns_tokens:
            preference.apns_tokens.append(device_data.token)
            preference.apns_tokens = list(set(preference.apns_tokens))  # Deduplicate

    db.commit()

    return {
        "message": "Device token registered successfully",
        "platform": device_data.platform,
        "token_count": len(preference.fcm_tokens or []) + len(preference.apns_tokens or [])
    }


@router.delete("/device-token/{token}")
def unregister_device_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unregister device token"""
    from app.models.notification import NotificationPreference

    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()

    if not preference:
        raise HTTPException(status_code=404, detail="Preferences not found")

    removed = False

    # Remove from FCM tokens
    if preference.fcm_tokens and token in preference.fcm_tokens:
        preference.fcm_tokens.remove(token)
        removed = True

    # Remove from APNS tokens
    if preference.apns_tokens and token in preference.apns_tokens:
        preference.apns_tokens.remove(token)
        removed = True

    if removed:
        db.commit()
        return {"message": "Device token unregistered successfully"}
    else:
        raise HTTPException(status_code=404, detail="Token not found")


# ===============================================
# Settings and Configuration
# ===============================================

@router.get("/settings", response_model=NotificationSettingsResponse)
def get_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete notification settings including preferences and stats"""

    # Get preferences
    from app.models.notification import NotificationPreference
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()

    if not preference:
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)

    # Get stats
    stats = NotificationService.get_notification_stats(db, current_user.id)

    # Get available types and priorities
    available_types = [
        {"value": t.value, "label": t.value.replace('_', ' ').title()}
        for t in NotificationType
    ]

    available_priorities = [p.value for p in NotificationPriority]

    return NotificationSettingsResponse(
        preferences=preference,
        stats=stats,
        available_types=available_types,
        available_priorities=available_priorities
    )


# ===============================================
# WebSocket for Real-time Notifications
# ===============================================

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""

    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_to_user(self, user_id: int, message: dict):
        """Send notification to all connected clients for a user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn, user_id)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications

    Connect to: ws://localhost:8000/api/notifications/ws/{user_id}

    Messages received:
    - {"type": "notification", "data": {...notification object...}}
    - {"type": "unread_count", "count": 5}
    - {"type": "ping", "timestamp": "..."}
    """
    await manager.connect(websocket, user_id)

    try:
        # Send initial unread count
        from app.models.notification import Notification
        unread_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_archived == False
        ).count()

        await websocket.send_json({
            "type": "unread_count",
            "count": unread_count
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()

            # Handle ping/pong
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


# Helper function to broadcast notifications (used by notification service)
async def broadcast_notification(user_id: int, notification: dict):
    """Broadcast notification to user's connected WebSocket clients"""
    await manager.send_to_user(user_id, {
        "type": "notification",
        "data": notification
    })
