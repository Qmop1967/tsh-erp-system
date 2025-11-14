#!/usr/bin/env python3
"""
Test Webhook Fix Script
========================

Tests that the async context fix resolves the webhook processing error.

This script:
1. Finds a single item from the dead letter queue
2. Resets it to PENDING status
3. Processes it through the worker
4. Verifies successful completion

Run: python3 scripts/test_webhook_fix.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import AsyncSessionLocal
from app.background.zoho_sync_worker import SyncWorker
from sqlalchemy import select
from app.models.zoho_sync import TDSSyncQueue, EventStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_single_webhook():
    """Test webhook processing with fixed async context"""

    print("=" * 80)
    print("🧪 Testing Webhook Fix - Single Item")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Find first item from dead letter queue
            print("\n📋 Step 1: Finding item in dead letter queue...")

            result = await db.execute(
                select(TDSSyncQueue)
                .where(TDSSyncQueue.status == EventStatus.DEAD_LETTER)
                .limit(1)
            )
            queue_item = result.scalar_one_or_none()

            if not queue_item:
                print("❌ No items in dead letter queue!")
                print("   Either:")
                print("   1. All webhooks have already been processed (great!)")
                print("   2. Workers haven't processed any webhooks yet")
                print("\n💡 Check current queue status:")
                print("   SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;")
                return

            print(f"✅ Found item: {queue_item.id}")
            print(f"   Entity: {queue_item.entity_type}/{queue_item.source_entity_id}")
            print(f"   Status: {queue_item.status}")
            print(f"   Attempts: {queue_item.attempt_count}")
            print(f"   Error: {queue_item.error_message[:100] if queue_item.error_message else 'N/A'}...")

            # Step 2: Reset status to pending
            print("\n🔄 Step 2: Resetting to PENDING status...")
            queue_item.status = EventStatus.PENDING
            queue_item.attempt_count = 0
            queue_item.error_message = None
            queue_item.locked_by = None
            await db.commit()
            print("✅ Status reset to PENDING")

            # Step 3: Process with worker
            print("\n⚙️  Step 3: Processing through worker...")
            worker = SyncWorker(worker_id="test-worker-manual")

            try:
                await worker._process_event(str(queue_item.id))
                print("✅ Worker processing completed")
            except Exception as e:
                print(f"❌ Worker processing failed: {e}")
                raise

            # Step 4: Check result
            print("\n📊 Step 4: Checking result...")
            await db.refresh(queue_item)

            print(f"   Final Status: {queue_item.status}")
            print(f"   Local Entity ID: {queue_item.local_entity_id}")
            print(f"   Processing Time: {queue_item.processing_completed_at}")

            if queue_item.status == EventStatus.COMPLETED:
                print("\n" + "=" * 80)
                print("✅ SUCCESS! WEBHOOK PROCESSED SUCCESSFULLY!")
                print("=" * 80)
                print("\n🎉 The async context fix is working!")
                print("\n📝 Next steps:")
                print("   1. Process all dead letter queue items:")
                print("      python3 scripts/process_dead_letter_queue.py")
                print("   2. Monitor workers processing the queue")
                print("   3. Verify all 58 webhooks complete successfully")
                return True
            else:
                print("\n" + "=" * 80)
                print("❌ FAILED - Webhook did not complete successfully")
                print("=" * 80)
                print(f"\nStatus: {queue_item.status}")
                print(f"Error: {queue_item.error_message}")
                print("\n🔍 Troubleshooting:")
                print("   1. Check logs for detailed error")
                print("   2. Verify database schema matches expectations")
                print("   3. Check if all entity handlers have been updated")
                return False

        except Exception as e:
            print("\n" + "=" * 80)
            print("❌ TEST FAILED")
            print("=" * 80)
            print(f"\nError: {e}")
            logger.exception("Test failed with exception")
            return False


async def main():
    """Main test function"""
    try:
        success = await test_single_webhook()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.exception("Fatal error in test")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
