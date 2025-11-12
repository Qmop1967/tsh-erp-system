"""
TSH NeuroLink - Notifications API
Endpoints for managing user notifications
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import NeurolinkNotification
from app.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationMarkAllReadResponse,
    User
)
from app.middleware.auth import get_current_user


router = APIRouter(prefix="/v1/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Get user notifications",
    description="""
    Retrieve paginated list of notifications for the current user.

    Features:
    - Auto-filtered to current user
    - Pagination support
    - Status filtering (unread, read, all)
    - Severity filtering
    - Branch filtering (for branch managers)
    """
)
async def get_notifications(
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, delivered, read, dismissed"),
    severity: Optional[str] = Query(None, description="Filter by severity: info, warning, error, critical"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NotificationListResponse:
    """Get notifications for current user with filtering and pagination"""

    # Base query - always filtered to current user
    query = select(NeurolinkNotification).where(
        NeurolinkNotification.user_id == current_user.id
    )

    # Apply filters
    filters = [NeurolinkNotification.user_id == current_user.id]

    if status_filter:
        filters.append(NeurolinkNotification.status == status_filter)

    if severity:
        filters.append(NeurolinkNotification.severity == severity)

    if unread_only:
        filters.append(NeurolinkNotification.read_at.is_(None))

    query = query.where(and_(*filters))

    # Get total count
    count_query = select(func.count()).select_from(NeurolinkNotification).where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get unread count
    unread_query = select(func.count()).select_from(NeurolinkNotification).where(
        and_(
            NeurolinkNotification.user_id == current_user.id,
            NeurolinkNotification.read_at.is_(None)
        )
    )
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar()

    # Order by most recent first
    query = query.order_by(NeurolinkNotification.created_at.desc())

    # Pagination
    offset = (page - 1) * page_size
    query = query.limit(page_size).offset(offset)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size
    )


@router.get(
    "/unread/count",
    summary="Get unread notification count",
    description="Get the count of unread notifications for the current user"
)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get unread notification count for current user"""

    # Use the database function we created
    query = text("SELECT neurolink_get_unread_count(:user_id)")
    result = await db.execute(query, {"user_id": current_user.id})
    count = result.scalar()

    return {"unread_count": count}


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification by ID",
    description="Retrieve a specific notification by its UUID"
)
async def get_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Get a specific notification by ID"""

    query = select(NeurolinkNotification).where(
        and_(
            NeurolinkNotification.id == notification_id,
            NeurolinkNotification.user_id == current_user.id  # Security: user can only see their own
        )
    )

    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found"
        )

    return NotificationResponse.from_orm(notification)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
    description="Mark a specific notification as read"
)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Mark a notification as read"""

    query = select(NeurolinkNotification).where(
        and_(
            NeurolinkNotification.id == notification_id,
            NeurolinkNotification.user_id == current_user.id
        )
    )

    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found"
        )

    # Update status
    if notification.status in ('pending', 'delivered'):
        notification.status = 'read'
    notification.read_at = datetime.utcnow()

    await db.commit()
    await db.refresh(notification)

    return NotificationResponse.from_orm(notification)


@router.post(
    "/mark-read",
    response_model=dict,
    summary="Mark multiple notifications as read",
    description="Mark multiple notifications as read in a single request"
)
async def mark_multiple_read(
    request: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Mark multiple notifications as read"""

    # Update notifications
    query = select(NeurolinkNotification).where(
        and_(
            NeurolinkNotification.id.in_(request.notification_ids),
            NeurolinkNotification.user_id == current_user.id
        )
    )

    result = await db.execute(query)
    notifications = result.scalars().all()

    marked_count = 0
    for notification in notifications:
        if notification.status in ('pending', 'delivered'):
            notification.status = 'read'
        notification.read_at = datetime.utcnow()
        marked_count += 1

    await db.commit()

    return {"marked_count": marked_count}


@router.post(
    "/mark-all-read",
    response_model=NotificationMarkAllReadResponse,
    summary="Mark all notifications as read",
    description="Mark all unread notifications for the current user as read"
)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NotificationMarkAllReadResponse:
    """Mark all notifications as read for current user"""

    # Use the database function we created
    query = text("SELECT neurolink_mark_all_read(:user_id)")
    result = await db.execute(query, {"user_id": current_user.id})
    marked_count = result.scalar()

    await db.commit()

    return NotificationMarkAllReadResponse(marked_count=marked_count)


@router.patch(
    "/{notification_id}/dismiss",
    response_model=NotificationResponse,
    summary="Dismiss notification",
    description="Dismiss a notification (remove from inbox)"
)
async def dismiss_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Dismiss a notification"""

    query = select(NeurolinkNotification).where(
        and_(
            NeurolinkNotification.id == notification_id,
            NeurolinkNotification.user_id == current_user.id
        )
    )

    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found"
        )

    # Update status
    notification.status = 'dismissed'
    notification.dismissed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(notification)

    return NotificationResponse.from_orm(notification)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification",
    description="Permanently delete a notification (admin only or own notifications)"
)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""

    query = select(NeurolinkNotification).where(
        and_(
            NeurolinkNotification.id == notification_id,
            NeurolinkNotification.user_id == current_user.id
        )
    )

    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found"
        )

    await db.delete(notification)
    await db.commit()

    return None
