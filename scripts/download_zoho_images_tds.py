#!/usr/bin/env python3
"""
Download product images from Zoho using TDS Image Sync Handler
================================================================

✅ UPDATED: Now uses TDS architecture for centralized monitoring and event tracking

This script replaces the old download_zoho_images_paginated.py and uses
the TDS ImageSyncHandler for proper integration with the TSH ERP ecosystem.

Usage:
    python3 scripts/download_zoho_images_tds.py                    # Download all images
    python3 scripts/download_zoho_images_tds.py --active-only      # Only active products
    python3 scripts/download_zoho_images_tds.py --force            # Force re-download
    python3 scripts/download_zoho_images_tds.py --limit 50         # Limit to 50 images (testing)

Author: TSH ERP Team
Date: January 2025
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env')

from app.db.database import AsyncSessionLocal
from app.tds.integrations.zoho.image_sync import TDSImageSyncHandler
from app.tds.integrations.zoho import ZohoCredentials

# Configuration
ORGANIZATION_ID = os.getenv('ZOHO_ORGANIZATION_ID', '748369814')
BATCH_SIZE = int(os.getenv('IMAGE_SYNC_BATCH_SIZE', '100'))
DELAY_BETWEEN_BATCHES = float(os.getenv('IMAGE_SYNC_DELAY_BATCHES', '2.0'))
DELAY_BETWEEN_IMAGES = float(os.getenv('IMAGE_SYNC_DELAY_IMAGES', '0.1'))


async def download_images_tds(
    active_only: bool = True,
    with_stock_only: bool = False,
    force_redownload: bool = False,
    limit: int = None
):
    """
    Download product images using TDS Image Sync Handler

    Args:
        active_only: Only process active products
        with_stock_only: Only process products with stock
        force_redownload: Re-download even if image exists
        limit: Maximum images to download (for testing)
    """
    print("=" * 70)
    print("🖼️  Zoho Product Images Download (TDS)")
    print("=" * 70)
    print()
    print("✅ Using TDS Image Sync Handler")
    print(f"   Organization ID: {ORGANIZATION_ID}")
    print(f"   Batch Size: {BATCH_SIZE}")
    print(f"   Active Only: {active_only}")
    print(f"   With Stock Only: {with_stock_only}")
    print(f"   Force Re-download: {force_redownload}")
    if limit:
        print(f"   Limit: {limit} images")
    print()

    # Create async database session
    async with AsyncSessionLocal() as db_session:
        try:
            # Initialize TDS Image Sync Handler
            handler = TDSImageSyncHandler(
                db_session=db_session,
                organization_id=ORGANIZATION_ID,
                batch_size=BATCH_SIZE,
                delay_between_batches=DELAY_BETWEEN_BATCHES,
                delay_between_images=DELAY_BETWEEN_IMAGES
            )

            print("🚀 Starting image download...")
            print()

            # Sync images using TDS handler
            stats = await handler.sync_images(
                active_only=active_only,
                with_stock_only=with_stock_only,
                force_redownload=force_redownload,
                limit=limit
            )

            # Print summary
            print()
            print("=" * 70)
            print("✅ Download Complete!")
            print("=" * 70)
            print(f"   Total: {stats['total']}")
            print(f"   Downloaded: {stats['downloaded']}")
            print(f"   Skipped: {stats['skipped']}")
            print(f"   Failed: {stats['failed']}")
            print(f"   Success Rate: {stats['success_rate']}")
            print(f"   Elapsed Time: {stats['elapsed_seconds']:.1f} seconds")
            print(f"   Downloads/Min: {stats['downloads_per_minute']:.1f}")
            print("=" * 70)
            print()

            if stats['failed'] > 0:
                print(f"⚠️  Warning: {stats['failed']} images failed to download")
                print("   Check logs for details")
                print()

            print("✅ All images synced via TDS!")
            print("   Events tracked and logged for monitoring")
            print()

        except Exception as e:
            print()
            print("=" * 70)
            print("❌ Error during image download")
            print("=" * 70)
            print(f"Error: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Download product images from Zoho using TDS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all images for active products
  python3 scripts/download_zoho_images_tds.py

  # Only products with stock
  python3 scripts/download_zoho_images_tds.py --with-stock

  # Force re-download all images
  python3 scripts/download_zoho_images_tds.py --force

  # Test with limited images
  python3 scripts/download_zoho_images_tds.py --limit 10
        """
    )

    parser.add_argument(
        '--active-only',
        action='store_true',
        default=True,
        help='Only process active products (default: True)'
    )
    parser.add_argument(
        '--all-products',
        action='store_true',
        help='Process all products (including inactive)'
    )
    parser.add_argument(
        '--with-stock',
        action='store_true',
        help='Only process products with available stock'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-download even if image already exists'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of images to download (for testing)'
    )

    args = parser.parse_args()

    # Determine active_only flag
    active_only = not args.all_products if args.all_products else args.active_only

    # Run async function
    asyncio.run(download_images_tds(
        active_only=active_only,
        with_stock_only=args.with_stock,
        force_redownload=args.force,
        limit=args.limit
    ))


if __name__ == '__main__':
    main()

