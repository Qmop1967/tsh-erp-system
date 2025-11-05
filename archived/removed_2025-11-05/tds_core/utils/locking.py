"""
TDS Core - Distributed Locking Utilities
Database-backed distributed locks for concurrent processing
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.tds_models import TDSSyncQueue

logger = logging.getLogger(__name__)


async def acquire_lock(
    db: AsyncSession,
    queue_id: str,
    worker_id: str,
    lock_duration_seconds: int = 300
) -> bool:
    """
    Acquire distributed lock on sync queue item

    Args:
        db: Database session
        queue_id: Queue item UUID
        worker_id: Unique worker identifier
        lock_duration_seconds: Lock timeout (default: 5 minutes)

    Returns:
        True if lock acquired successfully

    Example:
        >>> async with get_db_context() as db:
        >>>     worker_id = f"worker-{uuid4()}"
        >>>     if await acquire_lock(db, queue_id, worker_id):
        >>>         try:
        >>>             # Process event
        >>>             await process_event(queue_id)
        >>>         finally:
        >>>             await release_lock(db, queue_id, worker_id)
    """
    lock_expires_at = datetime.utcnow() + timedelta(seconds=lock_duration_seconds)

    try:
        # Attempt to acquire lock using UPDATE with WHERE condition
        # Only updates if: (1) not locked, OR (2) lock expired
        result = await db.execute(
            update(TDSSyncQueue)
            .where(
                TDSSyncQueue.id == queue_id,
                (
                    (TDSSyncQueue.locked_by == None) |
                    (TDSSyncQueue.lock_expires_at < datetime.utcnow())
                )
            )
            .values(
                locked_by=worker_id,
                lock_expires_at=lock_expires_at
            )
        )

        await db.commit()

        # Check if lock was acquired (row was updated)
        if result.rowcount > 0:
            logger.debug(f"Lock acquired: queue_id={queue_id}, worker={worker_id}")
            return True
        else:
            logger.debug(f"Lock already held: queue_id={queue_id}")
            return False

    except Exception as e:
        logger.error(f"Failed to acquire lock: {e}")
        await db.rollback()
        return False


async def release_lock(
    db: AsyncSession,
    queue_id: str,
    worker_id: str
) -> bool:
    """
    Release distributed lock

    Args:
        db: Database session
        queue_id: Queue item UUID
        worker_id: Worker identifier (must match lock owner)

    Returns:
        True if lock released successfully

    Note:
        Only the worker that acquired the lock can release it
    """
    try:
        result = await db.execute(
            update(TDSSyncQueue)
            .where(
                TDSSyncQueue.id == queue_id,
                TDSSyncQueue.locked_by == worker_id
            )
            .values(
                locked_by=None,
                lock_expires_at=None
            )
        )

        await db.commit()

        if result.rowcount > 0:
            logger.debug(f"Lock released: queue_id={queue_id}, worker={worker_id}")
            return True
        else:
            logger.warning(f"Lock not held by worker: queue_id={queue_id}, worker={worker_id}")
            return False

    except Exception as e:
        logger.error(f"Failed to release lock: {e}")
        await db.rollback()
        return False


async def is_lock_valid(
    db: AsyncSession,
    queue_id: str,
    worker_id: str
) -> bool:
    """
    Check if lock is still valid for worker

    Args:
        db: Database session
        queue_id: Queue item UUID
        worker_id: Worker identifier

    Returns:
        True if lock is valid and not expired
    """
    try:
        result = await db.execute(
            select(TDSSyncQueue)
            .where(
                TDSSyncQueue.id == queue_id,
                TDSSyncQueue.locked_by == worker_id,
                TDSSyncQueue.lock_expires_at > datetime.utcnow()
            )
        )

        queue_item = result.scalar_one_or_none()
        return queue_item is not None

    except Exception as e:
        logger.error(f"Failed to check lock validity: {e}")
        return False


async def extend_lock(
    db: AsyncSession,
    queue_id: str,
    worker_id: str,
    extension_seconds: int = 300
) -> bool:
    """
    Extend lock duration for long-running operations

    Args:
        db: Database session
        queue_id: Queue item UUID
        worker_id: Worker identifier
        extension_seconds: Additional time to add

    Returns:
        True if lock extended successfully
    """
    new_expires_at = datetime.utcnow() + timedelta(seconds=extension_seconds)

    try:
        result = await db.execute(
            update(TDSSyncQueue)
            .where(
                TDSSyncQueue.id == queue_id,
                TDSSyncQueue.locked_by == worker_id,
                TDSSyncQueue.lock_expires_at > datetime.utcnow()
            )
            .values(lock_expires_at=new_expires_at)
        )

        await db.commit()

        if result.rowcount > 0:
            logger.debug(f"Lock extended: queue_id={queue_id}, worker={worker_id}")
            return True
        else:
            logger.warning(f"Cannot extend expired/invalid lock: queue_id={queue_id}")
            return False

    except Exception as e:
        logger.error(f"Failed to extend lock: {e}")
        await db.rollback()
        return False


async def cleanup_expired_locks(db: AsyncSession) -> int:
    """
    Clean up expired locks (maintenance task)

    Args:
        db: Database session

    Returns:
        Number of locks cleaned up
    """
    try:
        result = await db.execute(
            update(TDSSyncQueue)
            .where(
                TDSSyncQueue.locked_by != None,
                TDSSyncQueue.lock_expires_at < datetime.utcnow()
            )
            .values(
                locked_by=None,
                lock_expires_at=None
            )
        )

        await db.commit()

        cleaned = result.rowcount
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired locks")

        return cleaned

    except Exception as e:
        logger.error(f"Failed to cleanup expired locks: {e}")
        await db.rollback()
        return 0
