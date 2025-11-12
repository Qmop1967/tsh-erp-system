"""
TSH NeuroLink - Background Worker
Handles automated notification triggers, scheduled notifications, and monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, or_, update

from app.config import settings
from app.models import (
    NeurolinkEvent,
    NeurolinkNotification,
    NeurolinkScheduledNotifications,
    NeurolinkAnnouncement,
    NeurolinkEmergencyBroadcast
)
from app.services.email_delivery import EmailDeliveryService
from app.services.push_delivery import PushNotificationService

logger = logging.getLogger(__name__)


class BackgroundWorker:
    """
    Background worker for automated notification triggers and scheduled tasks
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.email_service = EmailDeliveryService()
        self.push_service = PushNotificationService()

        # Create async database engine
        self.engine = create_async_engine(
            settings.database_url,
            pool_size=5,
            max_overflow=10,
            echo=False
        )

        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def start(self):
        """Start the background worker"""
        logger.info("Starting NeuroLink Background Worker...")

        # Schedule periodic tasks
        self._schedule_tasks()

        # Start scheduler
        self.scheduler.start()
        logger.info("Background Worker started successfully")

    async def stop(self):
        """Stop the background worker"""
        logger.info("Stopping Background Worker...")
        self.scheduler.shutdown()
        await self.engine.dispose()
        logger.info("Background Worker stopped")

    def _schedule_tasks(self):
        """Schedule all periodic tasks"""

        # Check for low stock every 5 minutes
        self.scheduler.add_job(
            self.check_low_stock_alerts,
            trigger=IntervalTrigger(minutes=5),
            id='check_low_stock',
            name='Check Low Stock Alerts',
            replace_existing=True
        )

        # Check for overdue invoices every hour
        self.scheduler.add_job(
            self.check_overdue_invoices,
            trigger=IntervalTrigger(hours=1),
            id='check_overdue_invoices',
            name='Check Overdue Invoices',
            replace_existing=True
        )

        # Process scheduled notifications every minute
        self.scheduler.add_job(
            self.process_scheduled_notifications,
            trigger=IntervalTrigger(minutes=1),
            id='process_scheduled_notifications',
            name='Process Scheduled Notifications',
            replace_existing=True
        )

        # Publish scheduled announcements every minute
        self.scheduler.add_job(
            self.publish_scheduled_announcements,
            trigger=IntervalTrigger(minutes=1),
            id='publish_scheduled_announcements',
            name='Publish Scheduled Announcements',
            replace_existing=True
        )

        # Check for pending emergency broadcast acknowledgments every 5 minutes
        self.scheduler.add_job(
            self.check_emergency_broadcast_acknowledgments,
            trigger=IntervalTrigger(minutes=5),
            id='check_emergency_acks',
            name='Check Emergency Broadcast Acknowledgments',
            replace_existing=True
        )

        # Clean up old events and notifications (daily at 2 AM)
        self.scheduler.add_job(
            self.cleanup_old_data,
            trigger=CronTrigger(hour=2, minute=0),
            id='cleanup_old_data',
            name='Clean Up Old Data',
            replace_existing=True
        )

        logger.info("All background tasks scheduled successfully")

    async def check_low_stock_alerts(self):
        """
        Check inventory for products below minimum stock levels
        Create notifications for warehouse managers
        """
        try:
            async with self.async_session() as db:
                # Query for low stock products
                # Assuming products table has: id, name, sku, actual_available_stock, min_quantity, warehouse_id
                query = """
                    SELECT
                        p.id as product_id,
                        p.name as product_name,
                        p.sku,
                        p.actual_available_stock as current_stock,
                        p.min_quantity,
                        w.id as warehouse_id,
                        w.name as warehouse_name
                    FROM products p
                    LEFT JOIN warehouses w ON p.warehouse_id = w.id
                    WHERE p.is_active = true
                    AND p.actual_available_stock <= p.min_quantity
                    AND p.actual_available_stock > 0  -- Not completely out of stock
                    AND p.min_quantity IS NOT NULL
                    AND p.min_quantity > 0
                """

                result = await db.execute(query)
                low_stock_products = result.fetchall()

                if low_stock_products:
                    logger.info(f"Found {len(low_stock_products)} low stock products")

                    # Create event for low stock
                    for product in low_stock_products:
                        await self._create_low_stock_event(db, product)

                    await db.commit()

        except Exception as e:
            logger.error(f"Error checking low stock: {str(e)}")

    async def check_overdue_invoices(self):
        """
        Check for overdue invoices
        Create notifications for accountants and finance managers
        """
        try:
            async with self.async_session() as db:
                # Query for overdue invoices
                query = """
                    SELECT
                        i.id as invoice_id,
                        i.invoice_number,
                        i.customer_id,
                        c.name as customer_name,
                        i.total_amount,
                        i.currency,
                        i.due_date,
                        EXTRACT(DAY FROM CURRENT_DATE - i.due_date) as days_overdue,
                        i.branch_id
                    FROM invoices i
                    LEFT JOIN customers c ON i.customer_id = c.id
                    WHERE i.status = 'unpaid'
                    AND i.due_date < CURRENT_DATE
                    AND i.is_active = true
                """

                result = await db.execute(query)
                overdue_invoices = result.fetchall()

                if overdue_invoices:
                    logger.info(f"Found {len(overdue_invoices)} overdue invoices")

                    for invoice in overdue_invoices:
                        await self._create_overdue_invoice_event(db, invoice)

                    await db.commit()

        except Exception as e:
            logger.error(f"Error checking overdue invoices: {str(e)}")

    async def process_scheduled_notifications(self):
        """
        Process scheduled notifications that are due to be sent
        """
        try:
            async with self.async_session() as db:
                # Get scheduled notifications that are due
                stmt = select(NeurolinkScheduledNotifications).where(
                    and_(
                        NeurolinkScheduledNotifications.is_active == True,
                        NeurolinkScheduledNotifications.next_run_at <= datetime.utcnow()
                    )
                )

                result = await db.execute(stmt)
                scheduled_notifications = result.scalars().all()

                for scheduled in scheduled_notifications:
                    try:
                        # Create notifications for targeted users
                        await self._create_notifications_from_schedule(db, scheduled)

                        # Update next run time
                        next_run = self._calculate_next_run(scheduled)
                        scheduled.last_run_at = datetime.utcnow()
                        scheduled.next_run_at = next_run
                        scheduled.run_count += 1

                        await db.commit()

                        logger.info(
                            f"Processed scheduled notification: {scheduled.name}, "
                            f"next run: {next_run}"
                        )

                    except Exception as e:
                        logger.error(
                            f"Error processing scheduled notification {scheduled.id}: {str(e)}"
                        )
                        await db.rollback()

        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {str(e)}")

    async def publish_scheduled_announcements(self):
        """
        Publish announcements that are scheduled for current time
        """
        try:
            async with self.async_session() as db:
                # Get announcements scheduled for now
                stmt = select(NeurolinkAnnouncement).where(
                    and_(
                        NeurolinkAnnouncement.status == 'scheduled',
                        NeurolinkAnnouncement.publish_at <= datetime.utcnow()
                    )
                )

                result = await db.execute(stmt)
                announcements = result.scalars().all()

                for announcement in announcements:
                    try:
                        # Update status to published
                        announcement.status = 'published'
                        announcement.published_at = datetime.utcnow()

                        # Create notifications for targeted users if configured
                        if 'in_app' in announcement.delivery_channels:
                            await self._create_notifications_from_announcement(
                                db,
                                announcement
                            )

                        await db.commit()

                        logger.info(f"Published announcement: {announcement.title}")

                    except Exception as e:
                        logger.error(
                            f"Error publishing announcement {announcement.id}: {str(e)}"
                        )
                        await db.rollback()

        except Exception as e:
            logger.error(f"Error publishing scheduled announcements: {str(e)}")

    async def check_emergency_broadcast_acknowledgments(self):
        """
        Check emergency broadcasts for missing acknowledgments
        Resend to users who haven't acknowledged
        """
        try:
            async with self.async_session() as db:
                # Get active emergency broadcasts
                stmt = select(NeurolinkEmergencyBroadcast).where(
                    NeurolinkEmergencyBroadcast.status == 'active'
                )

                result = await db.execute(stmt)
                broadcasts = result.scalars().all()

                for broadcast in broadcasts:
                    # Check if we should resend
                    if broadcast.auto_resend_interval and broadcast.max_resend_attempts:
                        # Get pending acknowledgments count
                        pending_query = """
                            SELECT COUNT(*)
                            FROM users u
                            LEFT JOIN neurolink_emergency_broadcast_acknowledgments eba
                                ON eba.user_id = u.id
                                AND eba.broadcast_id = :broadcast_id
                            WHERE u.is_active = true
                            AND eba.id IS NULL
                        """

                        result = await db.execute(
                            pending_query,
                            {"broadcast_id": broadcast.id}
                        )
                        pending_count = result.scalar()

                        if pending_count > 0:
                            logger.warning(
                                f"Emergency broadcast {broadcast.id} has "
                                f"{pending_count} pending acknowledgments"
                            )
                            # In production, implement resend logic here

        except Exception as e:
            logger.error(f"Error checking emergency acknowledgments: {str(e)}")

    async def cleanup_old_data(self):
        """
        Clean up old events and notifications based on retention policy
        """
        try:
            async with self.async_session() as db:
                retention_date = datetime.utcnow() - timedelta(
                    days=settings.event_retention_days
                )

                # Delete old processed events
                delete_events_query = """
                    DELETE FROM neurolink_events
                    WHERE ingested_at < :retention_date
                    AND processed_at IS NOT NULL
                """

                result = await db.execute(
                    delete_events_query,
                    {"retention_date": retention_date}
                )

                deleted_events = result.rowcount

                # Delete old read notifications
                delete_notifications_query = """
                    DELETE FROM neurolink_notifications
                    WHERE created_at < :retention_date
                    AND status = 'read'
                """

                result = await db.execute(
                    delete_notifications_query,
                    {"retention_date": retention_date}
                )

                deleted_notifications = result.rowcount

                await db.commit()

                logger.info(
                    f"Cleanup completed: {deleted_events} events, "
                    f"{deleted_notifications} notifications deleted"
                )

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def _create_low_stock_event(self, db: AsyncSession, product: Dict):
        """Create low stock event in database"""
        try:
            event_data = {
                "source_module": "inventory",
                "event_type": "stock.low",
                "severity": "warning",
                "occurred_at": datetime.utcnow(),
                "payload": {
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "sku": product.sku,
                    "current_stock": product.current_stock,
                    "min_quantity": product.min_quantity,
                    "warehouse_id": product.warehouse_id,
                    "warehouse_name": product.warehouse_name
                },
                "producer_idempotency_key": f"low_stock_{product.product_id}_{datetime.utcnow().date()}"
            }

            # Insert event (will be processed by rule engine)
            event = NeurolinkEvent(**event_data)
            db.add(event)

            logger.info(f"Created low stock event for product: {product.product_name}")

        except Exception as e:
            logger.error(f"Error creating low stock event: {str(e)}")

    async def _create_overdue_invoice_event(self, db: AsyncSession, invoice: Dict):
        """Create overdue invoice event"""
        try:
            event_data = {
                "source_module": "invoicing",
                "event_type": "invoice.overdue",
                "severity": "warning",
                "occurred_at": datetime.utcnow(),
                "payload": {
                    "invoice_id": invoice.invoice_id,
                    "invoice_number": invoice.invoice_number,
                    "customer_name": invoice.customer_name,
                    "amount": float(invoice.total_amount),
                    "currency": invoice.currency,
                    "days_overdue": int(invoice.days_overdue)
                },
                "branch_id": invoice.branch_id,
                "producer_idempotency_key": f"invoice_overdue_{invoice.invoice_id}_{datetime.utcnow().date()}"
            }

            event = NeurolinkEvent(**event_data)
            db.add(event)

            logger.info(
                f"Created overdue invoice event: {invoice.invoice_number} "
                f"({invoice.days_overdue} days overdue)"
            )

        except Exception as e:
            logger.error(f"Error creating overdue invoice event: {str(e)}")

    async def _create_notifications_from_schedule(
        self,
        db: AsyncSession,
        scheduled: NeurolinkScheduledNotifications
    ):
        """Create notifications from scheduled notification"""
        # Get target users based on roles, branches, or specific users
        # This is a simplified version - implement full targeting logic

        logger.info(f"Creating notifications from schedule: {scheduled.name}")
        # Implementation would query users and create notifications

    async def _create_notifications_from_announcement(
        self,
        db: AsyncSession,
        announcement: NeurolinkAnnouncement
    ):
        """Create notifications from announcement"""
        logger.info(f"Creating notifications from announcement: {announcement.title}")
        # Implementation would query users and create notifications

    def _calculate_next_run(
        self,
        scheduled: NeurolinkScheduledNotifications
    ) -> Optional[datetime]:
        """Calculate next run time for scheduled notification"""
        if scheduled.schedule_type == 'once':
            return None  # One-time notification

        now = datetime.utcnow()

        if scheduled.schedule_type == 'daily':
            next_run = now.replace(
                hour=scheduled.schedule_time.hour,
                minute=scheduled.schedule_time.minute,
                second=0,
                microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif scheduled.schedule_type == 'weekly':
            # Calculate next week's run time
            # Simplified - implement full logic
            return now + timedelta(weeks=1)

        elif scheduled.schedule_type == 'monthly':
            # Calculate next month's run time
            # Simplified - implement full logic
            return now + timedelta(days=30)

        return None


# Global worker instance
worker = None


async def start_background_worker():
    """Start the background worker"""
    global worker
    worker = BackgroundWorker()
    await worker.start()


async def stop_background_worker():
    """Stop the background worker"""
    global worker
    if worker:
        await worker.stop()
