#!/usr/bin/env python3
"""
TDS Zoho Synchronization Script
================================

Organized Zoho sync using TDS (Tronix Delivery System) architecture.
This uses the proper TDS infrastructure instead of standalone scripts.

Usage:
    python3 run_tds_zoho_sync.py

Author: TSH ERP Team
Date: November 8, 2025
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# TDS Zoho Service
from app.tds.zoho import ZohoService, ZohoCredentials
from app.tds.integrations.zoho import (
    SyncMode, EntityType, SyncConfig
)

# Load environment
load_dotenv()


async def main():
    """
    Main synchronization process using TDS architecture
    """
    print("="*70)
    print("🔄 TDS ZOHO SYNCHRONIZATION")
    print("="*70)
    print()

    # Configuration
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found")
        return

    # Convert to async URL and use localhost for local execution
    if db_url.startswith("postgresql://"):
        async_db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        # Replace Docker hostname with localhost for local script execution
        async_db_url = async_db_url.replace("tsh_postgres:", "localhost:")
    else:
        async_db_url = db_url
        async_db_url = async_db_url.replace("tsh_postgres:", "localhost:")

    # Create Zoho credentials
    credentials = ZohoCredentials(
        client_id=os.getenv('ZOHO_CLIENT_ID'),
        client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
        refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
        organization_id=os.getenv('ZOHO_ORGANIZATION_ID', '748369814')
    )

    # Validate credentials
    if not all([credentials.client_id, credentials.client_secret,
                credentials.refresh_token, credentials.organization_id]):
        print("❌ Missing Zoho credentials in environment variables")
        print("   Required: ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN")
        return

    print(f"📋 Configuration:")
    print(f"   Organization ID: {credentials.organization_id}")
    print(f"   Database: Connected")
    print()

    # Create database session
    engine = create_async_engine(async_db_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as db:
        # Initialize TDS Zoho Service
        print("🚀 Initializing TDS Zoho Service...")
        zoho = ZohoService(credentials=credentials, db=db)

        try:
            # Start service
            await zoho.start()
            print("✅ TDS Zoho Service started")
            print()

            # Step 1: Sync Products (Items)
            print("━"*70)
            print("STEP 1: Syncing Products/Items from Zoho")
            print("━"*70)

            sync_config = SyncConfig(
                entity_type=EntityType.PRODUCTS,
                mode=SyncMode.INCREMENTAL,
                batch_size=200
            )

            products_result = await zoho.sync.sync_entity(config=sync_config)

            print(f"\n✅ Products Sync Results:")
            print(f"   Total Processed: {products_result.total_processed}")
            print(f"   Successful: {products_result.total_success}")
            print(f"   Failed: {products_result.total_failed}")
            print(f"   Duration: {products_result.duration}")
            print()

            # Step 2: Sync Stock Levels
            print("━"*70)
            print("STEP 2: Syncing Stock Levels")
            print("━"*70)

            stock_result = await zoho.stock_sync.sync_all_stock()

            print(f"\n✅ Stock Sync Results:")
            print(f"   Total Processed: {stock_result.total_processed}")
            print(f"   Successful: {stock_result.total_success}")
            print(f"   Failed: {stock_result.total_failed}")
            print(f"   Duration: {stock_result.duration}")
            print()

            # Step 3: Sync Price Lists
            print("━"*70)
            print("STEP 3: Syncing Price Lists")
            print("━"*70)

            # Get Consumer IQD price list
            consumer_pricelist = await zoho.client.get(
                'books',
                'pricelists',
                params={'pricelist_name': 'Consumer IQD'}
            )

            if consumer_pricelist:
                print(f"✅ Found Consumer IQD price list")
                # Sync price list items
                pricelist_id = consumer_pricelist.get('pricelists', [{}])[0].get('pricelist_id')
                if pricelist_id:
                    pricelist_items = await zoho.client.get(
                        'books',
                        f'pricelists/{pricelist_id}/items',
                        params={'per_page': 200}
                    )
                    print(f"   Items in price list: {len(pricelist_items.get('items', []))}")
            print()

            # Step 4: Download Product Images
            print("━"*70)
            print("STEP 4: Downloading Product Images")
            print("━"*70)

            # Get products with missing images
            from sqlalchemy import select, text
            result = await db.execute(text("""
                SELECT zoho_item_id, name
                FROM products
                WHERE zoho_item_id IS NOT NULL
                AND (image_url IS NULL OR image_url = '')
                LIMIT 100
            """))
            products_missing_images = result.fetchall()

            print(f"   Products missing images: {len(products_missing_images)}")

            # Download images for products
            image_count = 0
            for product in products_missing_images[:20]:  # Limit to 20 for now
                zoho_id = product[0]
                try:
                    item_data = await zoho.client.get(
                        'inventory',
                        f'items/{zoho_id}'
                    )

                    item = item_data.get('item', {})
                    image_url = item.get('image_url') or item.get('image_name')

                    if image_url:
                        # Update product with image URL
                        await db.execute(text("""
                            UPDATE products
                            SET image_url = :image_url, updated_at = NOW()
                            WHERE zoho_item_id = :zoho_id
                        """), {"image_url": image_url, "zoho_id": zoho_id})
                        image_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error fetching image for {zoho_id}: {e}")

            await db.commit()
            print(f"   ✅ Updated {image_count} product images")
            print()

            # Final Summary
            print("="*70)
            print("📊 SYNCHRONIZATION SUMMARY")
            print("="*70)
            print(f"✅ Products synced: {products_result.total_success}")
            print(f"✅ Stock levels updated: {stock_result.total_success}")
            print(f"✅ Images downloaded: {image_count}")
            print("="*70)
            print()

        finally:
            # Cleanup
            await zoho.stop()
            print("🔒 TDS Zoho Service stopped")

    await engine.dispose()
    print("\n✅ Synchronization complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
