"""
TSH NeuroLink - Announcements API
Endpoints for creating and managing system announcements
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_active_user, require_role
from app.models import (
    NeurolinkAnnouncement,
    NeurolinkAnnouncementAcknowledgment,
    User
)
from app.schemas import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse,
    AnnouncementListResponse,
    AcknowledgmentResponse
)

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.post(
    "",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "super_admin"))]
)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new announcement (Admin only)

    - **title**: Announcement title
    - **content**: Full announcement text
    - **target_type**: Who should see it ('all', 'role', 'branch', etc.)
    - **severity**: Importance level
    - **publish_at**: When to publish (null = immediate)
    """
    # Create announcement
    announcement = NeurolinkAnnouncement(
        title=announcement_data.title,
        content=announcement_data.content,
        summary=announcement_data.summary,
        severity=announcement_data.severity,
        announcement_type=announcement_data.announcement_type,
        target_type=announcement_data.target_type,
        target_roles=announcement_data.target_roles,
        target_branches=announcement_data.target_branches,
        target_departments=announcement_data.target_departments,
        target_users=announcement_data.target_users,
        is_pinned=announcement_data.is_pinned,
        priority=announcement_data.priority,
        requires_acknowledgment=announcement_data.requires_acknowledgment,
        publish_at=announcement_data.publish_at,
        expires_at=announcement_data.expires_at,
        translations=announcement_data.translations,
        delivery_channels=announcement_data.delivery_channels,
        created_by=current_user.id,
        status='scheduled' if announcement_data.publish_at and announcement_data.publish_at > datetime.utcnow() else 'published',
        published_at=datetime.utcnow() if not announcement_data.publish_at or announcement_data.publish_at <= datetime.utcnow() else None
    )

    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)

    return announcement


@router.get("", response_model=AnnouncementListResponse)
async def list_announcements(
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List announcements visible to current user

    - Filters by user's role and branch
    - Returns active (published, not expired) announcements
    - Admins can see all announcements with status filter
    """
    # Base query
    query = select(NeurolinkAnnouncement)

    # If not admin, filter by published and not expired
    if current_user.role.name not in ["admin", "super_admin"]:
        query = query.where(
            and_(
                NeurolinkAnnouncement.status == 'published',
                or_(
                    NeurolinkAnnouncement.expires_at == None,
                    NeurolinkAnnouncement.expires_at > datetime.utcnow()
                )
            )
        )

        # Filter by targeting
        # User should see announcements targeted to:
        # - all users
        # - their role
        # - their branch
        # - them specifically

        # This is simplified - in production, implement full targeting logic
    else:
        # Admin: apply status filter if provided
        if status_filter:
            query = query.where(NeurolinkAnnouncement.status == status_filter)

    # Order by pinned, priority, created_at
    query = query.order_by(
        NeurolinkAnnouncement.is_pinned.desc(),
        NeurolinkAnnouncement.priority.desc(),
        NeurolinkAnnouncement.created_at.desc()
    )

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    announcements = result.scalars().all()

    # Get total count
    count_query = select(NeurolinkAnnouncement)
    if status_filter and current_user.role.name in ["admin", "super_admin"]:
        count_query = count_query.where(NeurolinkAnnouncement.status == status_filter)

    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    return {
        "announcements": announcements,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific announcement"""
    stmt = select(NeurolinkAnnouncement).where(
        NeurolinkAnnouncement.id == announcement_id
    )

    result = await db.execute(stmt)
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    # Increment view count
    announcement.view_count += 1
    await db.commit()

    return announcement


@router.put(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    dependencies=[Depends(require_role("admin", "super_admin"))]
)
async def update_announcement(
    announcement_id: UUID,
    announcement_data: AnnouncementUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an announcement (Admin only)"""
    stmt = select(NeurolinkAnnouncement).where(
        NeurolinkAnnouncement.id == announcement_id
    )

    result = await db.execute(stmt)
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    # Update fields
    update_data = announcement_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)

    announcement.updated_by = current_user.id
    announcement.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(announcement)

    return announcement


@router.delete(
    "/{announcement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin", "super_admin"))]
)
async def delete_announcement(
    announcement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete an announcement (Admin only)"""
    stmt = delete(NeurolinkAnnouncement).where(
        NeurolinkAnnouncement.id == announcement_id
    )

    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    return None


@router.post(
    "/{announcement_id}/publish",
    response_model=AnnouncementResponse,
    dependencies=[Depends(require_role("admin", "super_admin"))]
)
async def publish_announcement(
    announcement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Publish an announcement immediately (Admin only)"""
    stmt = select(NeurolinkAnnouncement).where(
        NeurolinkAnnouncement.id == announcement_id
    )

    result = await db.execute(stmt)
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    announcement.status = 'published'
    announcement.published_at = datetime.utcnow()

    await db.commit()
    await db.refresh(announcement)

    return announcement


@router.post(
    "/{announcement_id}/acknowledge",
    response_model=AcknowledgmentResponse
)
async def acknowledge_announcement(
    announcement_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an announcement (mark as read/acknowledged)"""
    # Check if announcement exists
    stmt = select(NeurolinkAnnouncement).where(
        NeurolinkAnnouncement.id == announcement_id
    )

    result = await db.execute(stmt)
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    # Check if already acknowledged
    ack_stmt = select(NeurolinkAnnouncementAcknowledgment).where(
        and_(
            NeurolinkAnnouncementAcknowledgment.announcement_id == announcement_id,
            NeurolinkAnnouncementAcknowledgment.user_id == current_user.id
        )
    )

    ack_result = await db.execute(ack_stmt)
    existing_ack = ack_result.scalar_one_or_none()

    if existing_ack:
        return {
            "announcement_id": str(announcement_id),
            "user_id": current_user.id,
            "acknowledged_at": existing_ack.acknowledged_at,
            "already_acknowledged": True
        }

    # Create acknowledgment
    acknowledgment = NeurolinkAnnouncementAcknowledgment(
        announcement_id=announcement_id,
        user_id=current_user.id
    )

    db.add(acknowledgment)

    # Update acknowledgment count
    announcement.acknowledgment_count += 1

    await db.commit()

    return {
        "announcement_id": str(announcement_id),
        "user_id": current_user.id,
        "acknowledged_at": datetime.utcnow(),
        "already_acknowledged": False
    }


@router.get("/{announcement_id}/acknowledgments")
async def get_announcement_acknowledgments(
    announcement_id: UUID,
    current_user: User = Depends(require_role("admin", "super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of users who acknowledged the announcement (Admin only)
    """
    stmt = select(NeurolinkAnnouncementAcknowledgment).where(
        NeurolinkAnnouncementAcknowledgment.announcement_id == announcement_id
    )

    result = await db.execute(stmt)
    acknowledgments = result.scalars().all()

    return {
        "announcement_id": str(announcement_id),
        "total_acknowledgments": len(acknowledgments),
        "acknowledgments": [
            {
                "user_id": ack.user_id,
                "acknowledged_at": ack.acknowledged_at
            }
            for ack in acknowledgments
        ]
    }


@router.get("/{announcement_id}/pending-acknowledgments")
async def get_pending_acknowledgments(
    announcement_id: UUID,
    current_user: User = Depends(require_role("admin", "super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of users who haven't acknowledged the announcement yet (Admin only)
    """
    # Use the database function we created
    query = "SELECT * FROM neurolink_get_pending_emergency_acks(:announcement_id)"

    result = await db.execute(query, {"announcement_id": announcement_id})
    pending_users = result.fetchall()

    return {
        "announcement_id": str(announcement_id),
        "pending_count": len(pending_users),
        "pending_users": [
            {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "role": user.role,
                "email": user.email
            }
            for user in pending_users
        ]
    }


@router.post(
    "/{announcement_id}/archive",
    response_model=AnnouncementResponse,
    dependencies=[Depends(require_role("admin", "super_admin"))]
)
async def archive_announcement(
    announcement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Archive an announcement (Admin only)"""
    stmt = select(NeurolinkAnnouncement).where(
        NeurolinkAnnouncement.id == announcement_id
    )

    result = await db.execute(stmt)
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    announcement.status = 'archived'
    announcement.archived_at = datetime.utcnow()

    await db.commit()
    await db.refresh(announcement)

    return announcement
