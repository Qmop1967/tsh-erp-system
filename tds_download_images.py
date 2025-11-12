#!/usr/bin/env python3
"""
TDS Image Download Script
==========================

Download product images from Zoho through TDS.
Downloads images in batches with proper rate limiting and monitoring.

This script uses the TDS-integrated image sync handler for:
- Centralized monitoring
- Event tracking
- Unified architecture
- Proper error handling

تنزيل صور المنتجات من Zoho عبر TDS

Author: TSH ERP Team
Date: November 7, 2025
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import get_async_db
from app.tds.integrations.zoho.image_sync import TDSImageSyncHandler


async def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Download product images from Zoho through TDS"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download images for all products (including inactive/out of stock)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of images per batch (default: 100)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of images to download (for testing)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if image_url already exists"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 TDS Image Download Script")
    print("=" * 70)
    print()
    print("Configuration:")
    print(f"  Active products only: {not args.all}")
    print(f"  With stock only: {not args.all}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Force redownload: {args.force}")
    if args.limit:
        print(f"  Limit: {args.limit} images (testing mode)")
    print()
    print("=" * 70)
    print()

    # Get database session
    db_gen = get_async_db()
    db = await anext(db_gen)

    try:
        # Create TDS handler
        handler = TDSImageSyncHandler(
            db_session=db,
            batch_size=args.batch_size
        )

        # Run sync
        stats = await handler.sync_images(
            active_only=not args.all,
            with_stock_only=not args.all,
            force_redownload=args.force,
            limit=args.limit
        )

        # Print final summary
        print()
        print("=" * 70)
        print("📊 Final Statistics")
        print("=" * 70)
        for key, value in stats.items():
            print(f"  {key:25s}: {value}")
        print("=" * 70)
        print()
        print("✅ Image download complete!")
        print()
        print("Next steps:")
        print("  1. Verify images in database:")
        print("     SELECT COUNT(*), COUNT(image_url) FROM products;")
        print()
        print("  2. Check consumer app:")
        print("     https://consumer.tsh.sale")
        print()
    finally:
        # Close database session
        await db.close()
        try:
            await anext(db_gen)
        except StopAsyncIteration:
            pass


if __name__ == "__main__":
    asyncio.run(main())
