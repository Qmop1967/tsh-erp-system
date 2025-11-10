#!/usr/bin/env python3
"""
Sync Zoho Product Images
=========================

Downloads all product images from Zoho Books and stores them locally.

Usage:
    python3 sync_zoho_images.py

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
        logging.FileHandler('logs/image_sync.log')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main image sync process"""
    from app.tds.zoho import ZohoService
    from app.tds.integrations.zoho.client import ZohoAPI
    from app.tds.integrations.zoho.image_sync import ZohoImageSyncService
    from app.db.database import get_db, get_async_db

    print("=" * 80)
    print("🖼️  ZOHO PRODUCT IMAGES SYNC")
    print("=" * 80)
    print()

    start_time = datetime.utcnow()

    try:
        # Get database session
        db = next(get_db())

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

        # Count items with images
        items_with_images = [
            item for item in items
            if item.get('image_name') or item.get('image_document_id')
        ]
        print(f"📊 {len(items_with_images)} items have images ({len(items_with_images)/len(items)*100:.1f}%)")
        print()

        # Initialize image sync service
        print("🖼️  Initializing image download service...")
        image_service = ZohoImageSyncService(auth_manager=zoho.auth)
        print("✅ Image service ready")
        print()

        # Download all images
        print("=" * 80)
        print("⬇️  DOWNLOADING IMAGES")
        print("=" * 80)
        print(f"Starting download of {len(items_with_images)} images...")
        print(f"Batch size: 10 concurrent downloads")
        print(f"Estimated time: {len(items_with_images) * 0.5 / 60:.1f} minutes")
        print()

        stats = await image_service.sync_all_images(items, batch_size=10)

        print()
        print("=" * 80)
        print("✅ DOWNLOAD COMPLETE")
        print("=" * 80)
        print(f"Total items:       {stats['total']}")
        print(f"Items with images: {stats['items_with_images']}")
        print(f"Downloaded:        {stats['downloaded']}")
        print(f"Skipped:           {stats['skipped']}")
        print(f"Failed:            {stats['failed']}")
        print(f"Duration:          {stats['duration']:.1f}s ({stats['duration']/60:.1f} min)")
        print()

        # Show errors if any
        if stats['errors']:
            print("⚠️  ERRORS:")
            for error in stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error['name']} ({error['item_id']}): {error['error']}")
            if len(stats['errors']) > 10:
                print(f"  ... and {len(stats['errors']) - 10} more errors")
            print()

        # Update database
        print("=" * 80)
        print("💾 UPDATING DATABASE")
        print("=" * 80)
        print("Updating product records with local image paths...")
        print()

        async for db_async in get_async_db():
            try:
                updated = await image_service.update_database_image_paths(items, db_async)
                print(f"✅ Updated {updated} product records")
                break
            except Exception as e:
                logger.error(f"Database update failed: {str(e)}")
                print(f"❌ Database update failed: {str(e)}")
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
        print(f"Images downloaded: {stats['downloaded']}")
        if stats['items_with_images'] > 0:
            print(f"Success rate: {stats['downloaded']/stats['items_with_images']*100:.1f}%")
        print()

    except Exception as e:
        logger.error(f"Image sync failed: {str(e)}", exc_info=True)
        print()
        print(f"❌ Image sync failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
