#!/usr/bin/env python3
"""
Resume Zoho Product Images Sync
================================

Continues downloading remaining product images from Zoho Books.

Usage:
    python3 sync_zoho_images_resume.py

Author: TSH ERP Team
Date: November 9, 2025
"""

import asyncio
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/image_sync_resume.log')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main image sync resume process"""
    from app.tds.zoho import ZohoService
    from app.tds.integrations.zoho.client import ZohoAPI
    from app.tds.integrations.zoho.image_sync import ZohoImageSyncService
    from app.db.database import get_db, get_async_db
    from sqlalchemy import text

    print("=" * 80)
    print("🖼️  ZOHO PRODUCT IMAGES SYNC (RESUME)")
    print("=" * 80)
    print()

    start_time = datetime.utcnow()

    try:
        # Get database session
        db = next(get_db())

        # Check current status
        print("📊 Checking current image status...")
        async for db_async in get_async_db():
            try:
                query = text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(image_url) FILTER (WHERE image_url LIKE '/static/images/products/%') as synced,
                        COUNT(*) - COUNT(image_url) FILTER (WHERE image_url LIKE '/static/images/products/%') as remaining
                    FROM products
                    WHERE zoho_item_id IS NOT NULL
                """)
                result = await db_async.execute(query)
                stats = result.fetchone()
                print(f"  Total products: {stats[0]}")
                print(f"  Images synced: {stats[1]}")
                print(f"  Remaining: {stats[2]}")
                print()
                break
            finally:
                break

        # Initialize Zoho service
        print("📡 Initializing Zoho service...")
        zoho = ZohoService(db=db)
        await zoho.start()
        print("✅ Zoho service ready")
        print()

        # Fetch all items
        print("📦 Fetching all items from Zoho...")
        items = await zoho.client.paginated_fetch(
            api_type=ZohoAPI.INVENTORY,
            endpoint="items",
            page_size=200
        )
        print(f"✅ Fetched {len(items)} items from Zoho")
        print()

        # Filter items that have images in Zoho
        items_with_images = [
            item for item in items
            if item.get('image_name') or item.get('image_document_id')
        ]
        
        # Get list of items already synced
        async for db_async in get_async_db():
            try:
                query = text("""
                    SELECT zoho_item_id 
                    FROM products 
                    WHERE image_url LIKE '/static/images/products/%'
                """)
                result = await db_async.execute(query)
                synced_ids = {row[0] for row in result.fetchall()}
                break
            finally:
                break

        # Filter to only items that need syncing
        items_to_sync = [
            item for item in items_with_images
            if item.get('item_id') not in synced_ids
        ]

        print(f"📊 Analysis:")
        print(f"  Total items with images in Zoho: {len(items_with_images)}")
        print(f"  Already synced: {len(synced_ids)}")
        print(f"  Need to download: {len(items_to_sync)}")
        print()

        if not items_to_sync:
            print("✅ All images already synced!")
            await zoho.stop()
            db.close()
            return

        # Initialize image sync service
        print("🖼️  Initializing image download service...")
        image_service = ZohoImageSyncService(auth_manager=zoho.auth)
        print("✅ Image service ready")
        print()

        # Download remaining images
        print("=" * 80)
        print("⬇️  DOWNLOADING REMAINING IMAGES")
        print("=" * 80)
        print(f"Items to download: {len(items_to_sync)}")
        print(f"Batch size: 2 concurrent downloads")
        print(f"Delay between batches: 3 seconds")
        print(f"Estimated time: {(len(items_to_sync) * 3) / 60:.1f} minutes")
        print()
        print("⚠️  This will take a while due to Zoho rate limits")
        print("   Progress updates every 10 images...")
        print()

        # Create a modified items list with only items to sync
        items_filtered = [item for item in items if item.get('item_id') in {i['item_id'] for i in items_to_sync}]
        
        stats = await image_service.sync_all_images(items_filtered, batch_size=2)

        print()
        print("=" * 80)
        print("✅ DOWNLOAD COMPLETE")
        print("=" * 80)
        print(f"Attempted:  {len(items_to_sync)}")
        print(f"Downloaded: {stats['downloaded']}")
        print(f"Skipped:    {stats['skipped']}")
        print(f"Failed:     {stats['failed']}")
        print(f"Duration:   {stats['duration']:.1f}s ({stats['duration']/60:.1f} min)")
        print()

        # Show errors if any
        if stats['errors']:
            print("⚠️  ERRORS (first 20):")
            for error in stats['errors'][:20]:
                print(f"  - {error['name'][:50]}: {error['error']}")
            if len(stats['errors']) > 20:
                print(f"  ... and {len(stats['errors']) - 20} more errors")
            print()

        # Update database
        print("=" * 80)
        print("💾 UPDATING DATABASE")
        print("=" * 80)
        print("Updating product records with local image paths...")
        print()

        async for db_async in get_async_db():
            try:
                updated = await image_service.update_database_image_paths(items_filtered, db_async)
                print(f"✅ Updated {updated} product records")
                break
            except Exception as e:
                logger.error(f"Database update failed: {str(e)}")
                print(f"❌ Database update failed: {str(e)}")
            finally:
                break

        # Final status check
        print()
        print("=" * 80)
        print("📊 FINAL STATUS")
        print("=" * 80)
        async for db_async in get_async_db():
            try:
                query = text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(image_url) FILTER (WHERE image_url LIKE '/static/images/products/%') as synced
                    FROM products
                    WHERE zoho_item_id IS NOT NULL
                """)
                result = await db_async.execute(query)
                final_stats = result.fetchone()
                print(f"  Total products: {final_stats[0]}")
                print(f"  Images synced: {final_stats[1]}")
                print(f"  Completion: {final_stats[1]/final_stats[0]*100:.1f}%")
                break
            finally:
                break

        # Cleanup
        await zoho.stop()
        db.close()

        end_time = datetime.utcnow()
        total_duration = (end_time - start_time).total_seconds()

        print()
        print("=" * 80)
        print("✅ IMAGE SYNC COMPLETE")
        print("=" * 80)
        print(f"Total execution time: {total_duration:.1f}s ({total_duration/60:.1f} min)")
        print()

    except KeyboardInterrupt:
        print()
        print("⚠️  Sync interrupted by user")
        print("   Progress has been saved. Run this script again to resume.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Image sync failed: {str(e)}", exc_info=True)
        print()
        print(f"❌ Image sync failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
