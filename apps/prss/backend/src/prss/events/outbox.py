"""Outbox pattern implementation"""
from sqlalchemy.orm import Session
from prss.models.all_models import OutboxEvent
from prss.models.base import OutboxStatus
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OutboxProcessor:
    """Process pending outbox events"""

    def __init__(self, db: Session):
        self.db = db

    def process_pending_events(self, batch_size: int = 10):
        """Process pending events"""
        events = self.db.query(OutboxEvent).filter(
            OutboxEvent.status == OutboxStatus.PENDING,
            OutboxEvent.retries < OutboxEvent.max_retries
        ).limit(batch_size).all()

        for event in events:
            try:
                self._send_event(event)
                event.status = OutboxStatus.SENT
                event.sent_at = datetime.utcnow()
                logger.info(f"Event {event.id} sent successfully")
            except Exception as e:
                event.retries += 1
                event.last_error = str(e)
                event.next_retry_at = datetime.utcnow() + timedelta(minutes=5 * event.retries)
                if event.retries >= event.max_retries:
                    event.status = OutboxStatus.FAILED
                logger.error(f"Failed to send event {event.id}: {e}")

        self.db.commit()

    def _send_event(self, event: OutboxEvent):
        """Send event to subscribers"""
        # Implementation depends on message broker (RabbitMQ, Kafka, etc.)
        # For now, just log
        logger.info(f"Sending event {event.topic}: {event.payload}")
