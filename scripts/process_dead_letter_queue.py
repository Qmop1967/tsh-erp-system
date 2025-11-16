#!/usr/bin/env python3
"""
Process Dead Letter Queue Script
=================================

Processes all items in the dead letter queue by resetting them to PENDING status.
The background workers will then automatically pick them up and process them.

This script should be run AFTER verifying the webhook fix works with test_webhook_fix.py

Run: python3 scripts/process_dead_letter_queue.py
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.zoho_sync import TDSSyncQueue, EventStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_dlq():
    """Process all items in dead letter queue"""

    print("=" * 80)
    print("🔄 Processing Dead Letter Queue")
    print("=" * 80)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")

    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Count DLQ items
            print("\n📊 Step 1: Counting dead letter queue items...")

            dlq_count_result = await db.execute(
                select(func.count(TDSSyncQueue.id))
                .where(TDSSyncQueue.status == EventStatus.DEAD_LETTER)
            )
            dlq_count = dlq_count_result.scalar()

            print(f"✅ Found {dlq_count} items in dead letter queue")

            if dlq_count == 0:
                print("\n🎉 Dead letter queue is empty! All webhooks have been processed.")
                print("\n📊 Check overall queue status:")
                print("   SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;")
                return

            # Step 2: Get all DLQ items
            print(f"\n📋 Step 2: Retrieving all {dlq_count} items...")

            result = await db.execute(
                select(TDSSyncQueue)
                .where(TDSSyncQueue.status == EventStatus.DEAD_LETTER)
            )
            dlq_items = result.scalars().all()

            print(f"✅ Retrieved {len(dlq_items)} items")

            # Show breakdown by entity type
            entity_counts = {}
            for item in dlq_items:
                entity_type = str(item.entity_type)
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

            print("\n📊 Breakdown by entity type:")
            for entity_type, count in sorted(entity_counts.items()):
                print(f"   {entity_type}: {count} items")

            # Step 3: Reset all to PENDING
            print(f"\n🔄 Step 3: Resetting all {len(dlq_items)} items to PENDING...")

            for i, item in enumerate(dlq_items, 1):
                item.status = EventStatus.PENDING
                item.attempt_count = 0  # Reset attempts
                item.error_message = None
                item.locked_by = None
                item.dead_letter_at = None

                if i % 10 == 0:
                    print(f"   Progress: {i}/{len(dlq_items)} items reset...")

            await db.commit()
            print(f"✅ All {len(dlq_items)} items reset to PENDING")

            # Step 4: Verify
            print("\n✅ Step 4: Verifying reset...")

            verification = await db.execute(
                select(func.count(TDSSyncQueue.id))
                .where(TDSSyncQueue.status == EventStatus.PENDING)
            )
            pending_count = verification.scalar()

            print(f"✅ Verification complete: {pending_count} items now in PENDING status")

            # Show current queue status
            print("\n📊 Current Queue Status:")
            for status in [EventStatus.PENDING, EventStatus.PROCESSING, EventStatus.COMPLETED, EventStatus.FAILED, EventStatus.DEAD_LETTER]:
                count_result = await db.execute(
                    select(func.count(TDSSyncQueue.id))
                    .where(TDSSyncQueue.status == status)
                )
                count = count_result.scalar()
                if count > 0:
                    print(f"   {str(status):15s}: {count:4d} items")

            print("\n" + "=" * 80)
            print("✅ DEAD LETTER QUEUE PROCESSING COMPLETE")
            print("=" * 80)

            print("\n🎯 Next steps:")
            print("   1. Background workers will automatically process the queue")
            print("   2. Monitor progress with:")
            print("      SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;")
            print("   3. Check for successful completion:")
            print("      SELECT COUNT(*) FROM tds_sync_queue WHERE status = 'COMPLETED';")
            print("   4. Monitor logs for any errors:")
            print("      tail -f /var/log/tsh-erp/backend.log | grep -i webhook")

            print("\n⏱️  Expected processing time:")
            print(f"   - {len(dlq_items)} items")
            print(f"   - 2 workers processing")
            print(f"   - ~100 items/minute")
            print(f"   - Estimated: {len(dlq_items) / 100:.1f} minutes")

            print("\n📈 Monitor progress:")
            print("   watch -n 5 'psql -c \"SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;\"'")

        except Exception as e:
            print("\n" + "=" * 80)
            print("❌ PROCESSING FAILED")
            print("=" * 80)
            print(f"\nError: {e}")
            logger.exception("DLQ processing failed")
            sys.exit(1)


async def main():
    """Main function"""
    try:
        await process_dlq()
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
