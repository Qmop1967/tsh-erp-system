"""
Event Store - Event Persistence
Stores events for audit trail, replay, and debugging
"""
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.database import Base
from .base_event import BaseEvent

logger = logging.getLogger(__name__)


class StoredEvent(Base):
    """
    Persisted event model

    Stores all published events for audit trail and event sourcing
    """
    __tablename__ = "event_store"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(PG_UUID(as_uuid=True), unique=True, nullable=False, index=True)
    event_type = Column(String(255), nullable=False, index=True)
    module = Column(String(100), nullable=False, index=True)
    aggregate_id = Column(String(255), nullable=True, index=True)
    aggregate_type = Column(String(100), nullable=True, index=True)
    data = Column(JSONB, nullable=False)
    event_metadata = Column(JSONB, default={})  # Renamed from 'metadata' to avoid SQLAlchemy reserved name
    correlation_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    causation_id = Column(PG_UUID(as_uuid=True), nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    version = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_domain_event(self) -> BaseEvent:
        """Convert stored event back to domain event"""
        return BaseEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            timestamp=self.timestamp,
            module=self.module,
            data=self.data,
            metadata=self.event_metadata,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            user_id=self.user_id,
            version=self.version
        )


class EventStore:
    """
    Event Store Service

    Provides methods to persist and retrieve events
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def save(self, event: BaseEvent) -> StoredEvent:
        """
        Save an event to the store

        Args:
            event: Event to save

        Returns:
            Stored event record
        """
        if not self.db:
            logger.warning("No database session provided, event not persisted")
            return None

        stored_event = StoredEvent(
            event_id=event.event_id,
            event_type=event.event_type,
            module=event.module,
            aggregate_id=getattr(event, 'aggregate_id', None),
            aggregate_type=getattr(event, 'aggregate_type', None),
            data=event.data,
            event_metadata=event.metadata,  # Use event_metadata column name
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            user_id=event.user_id,
            version=event.version,
            timestamp=event.timestamp
        )

        self.db.add(stored_event)
        await self.db.commit()
        await self.db.refresh(stored_event)

        logger.info(f"Event persisted: {event.event_type} (id={event.event_id})")
        return stored_event

    async def get_by_id(self, event_id: UUID) -> Optional[StoredEvent]:
        """
        Get an event by ID

        Args:
            event_id: Event UUID

        Returns:
            Stored event or None
        """
        if not self.db:
            return None

        result = await self.db.execute(
            select(StoredEvent).where(StoredEvent.event_id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_by_aggregate(
        self,
        aggregate_id: str,
        aggregate_type: Optional[str] = None
    ) -> List[StoredEvent]:
        """
        Get all events for a specific aggregate

        Args:
            aggregate_id: Aggregate ID
            aggregate_type: Aggregate type (optional)

        Returns:
            List of events
        """
        if not self.db:
            return []

        query = select(StoredEvent).where(StoredEvent.aggregate_id == aggregate_id)

        if aggregate_type:
            query = query.where(StoredEvent.aggregate_type == aggregate_type)

        query = query.order_by(StoredEvent.timestamp.asc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_correlation(self, correlation_id: UUID) -> List[StoredEvent]:
        """
        Get all events in a correlation chain

        Args:
            correlation_id: Correlation ID

        Returns:
            List of correlated events
        """
        if not self.db:
            return []

        result = await self.db.execute(
            select(StoredEvent)
            .where(StoredEvent.correlation_id == correlation_id)
            .order_by(StoredEvent.timestamp.asc())
        )
        return result.scalars().all()

    async def get_by_type(
        self,
        event_type: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredEvent]:
        """
        Get events by type

        Args:
            event_type: Event type
            limit: Maximum number of events
            offset: Number of events to skip

        Returns:
            List of events
        """
        if not self.db:
            return []

        result = await self.db.execute(
            select(StoredEvent)
            .where(StoredEvent.event_type == event_type)
            .order_by(StoredEvent.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_by_module(
        self,
        module: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredEvent]:
        """
        Get events from a specific module

        Args:
            module: Module name
            limit: Maximum number of events
            offset: Number of events to skip

        Returns:
            List of events
        """
        if not self.db:
            return []

        result = await self.db.execute(
            select(StoredEvent)
            .where(StoredEvent.module == module)
            .order_by(StoredEvent.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_recent(self, limit: int = 100) -> List[StoredEvent]:
        """
        Get most recent events

        Args:
            limit: Maximum number of events

        Returns:
            List of recent events
        """
        if not self.db:
            return []

        result = await self.db.execute(
            select(StoredEvent)
            .order_by(StoredEvent.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def replay_events(
        self,
        aggregate_id: str,
        aggregate_type: Optional[str] = None
    ) -> List[BaseEvent]:
        """
        Replay all events for an aggregate

        Useful for event sourcing and rebuilding state

        Args:
            aggregate_id: Aggregate ID
            aggregate_type: Aggregate type (optional)

        Returns:
            List of domain events in order
        """
        stored_events = await self.get_by_aggregate(aggregate_id, aggregate_type)
        return [event.to_domain_event() for event in stored_events]

    async def count_by_type(self, event_type: str) -> int:
        """
        Count events by type

        Args:
            event_type: Event type

        Returns:
            Number of events
        """
        if not self.db:
            return 0

        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(StoredEvent.id)).where(StoredEvent.event_type == event_type)
        )
        return result.scalar()

    async def get_stats(self) -> dict:
        """
        Get event store statistics

        Returns:
            Dictionary with statistics
        """
        if not self.db:
            return {}

        from sqlalchemy import func

        # Total events
        total_result = await self.db.execute(select(func.count(StoredEvent.id)))
        total = total_result.scalar()

        # Events by module
        module_result = await self.db.execute(
            select(StoredEvent.module, func.count(StoredEvent.id))
            .group_by(StoredEvent.module)
        )
        by_module = dict(module_result.all())

        # Events by type (top 10)
        type_result = await self.db.execute(
            select(StoredEvent.event_type, func.count(StoredEvent.id))
            .group_by(StoredEvent.event_type)
            .order_by(func.count(StoredEvent.id).desc())
            .limit(10)
        )
        by_type = dict(type_result.all())

        return {
            'total_events': total,
            'by_module': by_module,
            'by_type': by_type
        }


# Global event store instance (will be initialized with DB session)
event_store: Optional[EventStore] = None


def init_event_store(db: AsyncSession):
    """
    Initialize global event store with database session

    Call this during application startup

    Args:
        db: Database session
    """
    global event_store
    event_store = EventStore(db)
    logger.info("Event store initialized")
