"""
TSH NeuroLink - Event Ingestion API
Endpoints for receiving and managing business events
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import redis.asyncio as redis

from app.database import get_db
from app.models import NeurolinkEvent
from app.schemas import EventCreate, EventResponse, User
from app.middleware.auth import get_current_user
from app.config import settings


router = APIRouter(prefix="/v1/events", tags=["Events"])


# Redis client for publishing events to the event bus
async def get_redis():
    """Get Redis client for event bus publishing"""
    client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a new event",
    description="""
    Receive and ingest a new business event into NeuroLink.

    **Idempotency:**
    - Use `producer_idempotency_key` to prevent duplicate events
    - If an event with the same key exists, returns the existing event with 200 OK

    **Event Bus:**
    - Event is immediately published to Redis for async processing
    - Rule engine will evaluate and create notifications

    **Authentication:**
    - Requires valid JWT token
    - User context is automatically added to the event
    """
)
async def ingest_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
) -> EventResponse:
    """
    Ingest a new business event with idempotency protection

    Flow:
    1. Check for existing event with same idempotency key
    2. If exists, return existing event (idempotent)
    3. If new, create event in database
    4. Publish event to Redis event bus
    5. Return created event
    """

    # Check for existing event with same idempotency key (idempotency)
    if event_data.producer_idempotency_key:
        existing_query = select(NeurolinkEvent).where(
            NeurolinkEvent.producer_idempotency_key == event_data.producer_idempotency_key
        )
        result = await db.execute(existing_query)
        existing_event = result.scalar_one_or_none()

        if existing_event:
            # Event already exists - return it (idempotent behavior)
            return EventResponse.from_orm(existing_event)

    # Create new event
    new_event = NeurolinkEvent(
        # Auto-fill TSH ERP context from authenticated user
        branch_id=event_data.branch_id or current_user.branch_id,
        user_id=event_data.user_id or current_user.id,
        company_id=event_data.company_id,
        warehouse_id=event_data.warehouse_id,

        # Event data
        source_module=event_data.source_module,
        event_type=event_data.event_type,
        severity=event_data.severity,
        occurred_at=event_data.occurred_at,
        payload=event_data.payload,

        # Correlation
        correlation_id=event_data.correlation_id,
        producer_idempotency_key=event_data.producer_idempotency_key,

        # Metadata
        tags=event_data.tags,
        ingested_at=datetime.utcnow()
    )

    try:
        db.add(new_event)
        await db.commit()
        await db.refresh(new_event)

        # Publish event to Redis event bus for async processing
        event_message = {
            "event_id": str(new_event.id),
            "source_module": new_event.source_module,
            "event_type": new_event.event_type,
            "occurred_at": new_event.occurred_at.isoformat(),
        }

        # Publish to module-specific channel and global channel
        channel_name = f"{settings.redis_channel_prefix}events:{new_event.source_module}"
        await redis_client.publish(channel_name, str(event_message))

        # Also publish to global events channel
        await redis_client.publish(
            f"{settings.redis_channel_prefix}events:all",
            str(event_message)
        )

        return EventResponse.from_orm(new_event)

    except IntegrityError as e:
        await db.rollback()
        # Likely duplicate idempotency key (race condition)
        # Try to fetch the existing event
        existing_query = select(NeurolinkEvent).where(
            NeurolinkEvent.producer_idempotency_key == event_data.producer_idempotency_key
        )
        result = await db.execute(existing_query)
        existing_event = result.scalar_one_or_none()

        if existing_event:
            return EventResponse.from_orm(existing_event)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create event: {str(e)}"
            )


@router.get(
    "",
    response_model=List[EventResponse],
    summary="List events",
    description="Retrieve events with filtering and pagination"
)
async def list_events(
    source_module: Optional[str] = Query(None, description="Filter by source module"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    limit: int = Query(100, le=1000, description="Max events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[EventResponse]:
    """List events with filters"""

    # Build query with filters
    query = select(NeurolinkEvent)

    filters = []

    if source_module:
        filters.append(NeurolinkEvent.source_module == source_module)

    if event_type:
        filters.append(NeurolinkEvent.event_type == event_type)

    if severity:
        filters.append(NeurolinkEvent.severity == severity)

    if branch_id:
        filters.append(NeurolinkEvent.branch_id == branch_id)

    # Non-admin users only see events from their branch
    if current_user.role != "admin" and current_user.branch_id:
        filters.append(NeurolinkEvent.branch_id == current_user.branch_id)

    if filters:
        query = query.where(and_(*filters))

    # Order by most recent first
    query = query.order_by(NeurolinkEvent.occurred_at.desc())

    # Pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    events = result.scalars().all()

    return [EventResponse.from_orm(event) for event in events]


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event by ID",
    description="Retrieve a specific event by its UUID"
)
async def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EventResponse:
    """Get a specific event by ID"""

    query = select(NeurolinkEvent).where(NeurolinkEvent.id == event_id)

    # Non-admin users can only see events from their branch
    if current_user.role != "admin" and current_user.branch_id:
        query = query.where(NeurolinkEvent.branch_id == current_user.branch_id)

    result = await db.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )

    return EventResponse.from_orm(event)


@router.get(
    "/stats/summary",
    summary="Get event statistics",
    description="Retrieve event statistics and metrics"
)
async def get_event_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get event statistics"""

    # Total events
    total_query = select(func.count(NeurolinkEvent.id))
    if current_user.role != "admin" and current_user.branch_id:
        total_query = total_query.where(NeurolinkEvent.branch_id == current_user.branch_id)

    total_result = await db.execute(total_query)
    total_events = total_result.scalar()

    # Events by module
    module_query = select(
        NeurolinkEvent.source_module,
        func.count(NeurolinkEvent.id).label("count")
    ).group_by(NeurolinkEvent.source_module)

    if current_user.role != "admin" and current_user.branch_id:
        module_query = module_query.where(NeurolinkEvent.branch_id == current_user.branch_id)

    module_result = await db.execute(module_query)
    events_by_module = {row.source_module: row.count for row in module_result}

    # Events by severity
    severity_query = select(
        NeurolinkEvent.severity,
        func.count(NeurolinkEvent.id).label("count")
    ).group_by(NeurolinkEvent.severity)

    if current_user.role != "admin" and current_user.branch_id:
        severity_query = severity_query.where(NeurolinkEvent.branch_id == current_user.branch_id)

    severity_result = await db.execute(severity_query)
    events_by_severity = {row.severity: row.count for row in severity_result}

    return {
        "total_events": total_events,
        "events_by_module": events_by_module,
        "events_by_severity": events_by_severity
    }
