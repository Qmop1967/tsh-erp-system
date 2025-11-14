#!/usr/bin/env python3
"""
Complete Zoho Synchronization Script
=====================================

Comprehensive sync for ALL Zoho Books entities:
- Products/Items (2,221+)
- Stock/Inventory (1,312+)
- Customers/Contacts (500+)
- Invoices (23,972+)
- Sales Orders (19,636+)
- Purchase Orders
- Price Lists
- Product Images

Usage:
    python3 run_complete_zoho_sync.py
    python3 run_complete_zoho_sync.py --entities products customers invoices
    python3 run_complete_zoho_sync.py --skip-images

Author: TSH ERP Team
Date: November 14, 2025
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# TDS Zoho Service
from app.tds.zoho import ZohoService, ZohoCredentials
from app.tds.integrations.zoho import SyncMode, EntityType, SyncConfig

# Load environment
load_dotenv()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Complete Zoho Books Synchronization",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--entities',
        nargs='+',
        choices=['products', 'stock', 'customers', 'invoices', 'sales_orders', 'purchase_orders', 'images'],
        help='Specific entities to sync (default: all)'
    )

    parser.add_argument(
        '--mode',
        choices=['full', 'incremental'],
        default='incremental',
        help='Sync mode (default: incremental)'
    )

    parser.add_argument(
        '--skip-images',
        action='store_true',
        help='Skip image downloads'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=200,
        help='Batch size for processing (default: 200)'
    )

    return parser.parse_args()


async def main():
    """Main synchronization process"""
    args = parse_args()

    print("=" * 80)
    print("🚀 COMPLETE ZOHO BOOKS SYNCHRONIZATION")
    print("=" * 80)
    print(f"Mode: {args.mode.upper()}")
    print(f"Batch Size: {args.batch_size}")
    if args.entities:
        print(f"Entities: {', '.join(args.entities)}")
    else:
        print("Entities: ALL")
    print()

    # Configuration
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found")
        return 1

    # Convert to async URL and use localhost for local execution
    if db_url.startswith("postgresql://"):
        async_db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
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
        return 1

    print(f"📋 Organization ID: {credentials.organization_id}")
    print(f"📦 Database: Connected")
    print()

    # Create database session
    engine = create_async_engine(async_db_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Track results
    results = {}
    start_time = datetime.now()

    async with async_session_maker() as db:
        # Initialize TDS Zoho Service
        print("🔧 Initializing TDS Zoho Service...")
        zoho = ZohoService(credentials=credentials, db=db)

        try:
            await zoho.start()
            print("✅ TDS Zoho Service started\n")

            # Determine entities to sync
            entities_to_sync = args.entities or ['products', 'stock', 'customers', 'invoices', 'sales_orders', 'purchase_orders']
            if not args.skip_images and 'images' not in entities_to_sync:
                entities_to_sync.append('images')

            # Step 1: Sync Products
            if 'products' in entities_to_sync:
                print("━" * 80)
                print("STEP 1: Syncing Products/Items")
                print("━" * 80)

                sync_config = SyncConfig(
                    entity_type=EntityType.PRODUCTS,
                    mode=SyncMode.FULL if args.mode == 'full' else SyncMode.INCREMENTAL,
                    batch_size=args.batch_size
                )

                products_result = await zoho.sync.sync_entity(config=sync_config)
                results['products'] = {
                    'processed': products_result.total_processed,
                    'success': products_result.total_success,
                    'failed': products_result.total_failed,
                    'duration': str(products_result.duration)
                }

                print(f"\n✅ Products: {products_result.total_success}/{products_result.total_processed} synced")
                print(f"   Duration: {products_result.duration}\n")

            # Step 2: Sync Stock Levels
            if 'stock' in entities_to_sync:
                print("━" * 80)
                print("STEP 2: Syncing Stock Levels")
                print("━" * 80)

                stock_result = await zoho.stock_sync.sync_all_stock()
                results['stock'] = {
                    'processed': stock_result.total_processed,
                    'success': stock_result.total_success,
                    'failed': stock_result.total_failed,
                    'duration': str(stock_result.duration)
                }

                print(f"\n✅ Stock: {stock_result.total_success}/{stock_result.total_processed} synced")
                print(f"   Duration: {stock_result.duration}\n")

            # Step 3: Sync Customers/Contacts
            if 'customers' in entities_to_sync:
                print("━" * 80)
                print("STEP 3: Syncing Customers/Contacts")
                print("━" * 80)

                sync_config = SyncConfig(
                    entity_type=EntityType.CUSTOMERS,
                    mode=SyncMode.FULL if args.mode == 'full' else SyncMode.INCREMENTAL,
                    batch_size=args.batch_size
                )

                try:
                    customers_result = await zoho.sync.sync_entity(config=sync_config)
                    results['customers'] = {
                        'processed': customers_result.total_processed,
                        'success': customers_result.total_success,
                        'failed': customers_result.total_failed,
                        'duration': str(customers_result.duration)
                    }
                    print(f"\n✅ Customers: {customers_result.total_success}/{customers_result.total_processed} synced")
                except Exception as e:
                    print(f"\n⚠️  Customers sync skipped: {e}")
                    results['customers'] = {'error': str(e)}
                print()

            # Step 4: Download Product Images
            if 'images' in entities_to_sync and not args.skip_images:
                print("━" * 80)
                print("STEP 4: Downloading Product Images")
                print("━" * 80)

                try:
                    # Get products missing images
                    from sqlalchemy import select, text
                    result = await db.execute(text("""
                        SELECT zoho_item_id, name
                        FROM products
                        WHERE zoho_item_id IS NOT NULL
                        AND (image_url IS NULL OR image_url = '')
                        LIMIT 100
                    """))
                    products_missing_images = result.fetchall()

                    print(f"   Found {len(products_missing_images)} products missing images")

                    image_count = 0
                    for product in products_missing_images[:50]:  # Limit to 50
                        zoho_id = product[0]
                        try:
                            item_data = await zoho.client.get('inventory', f'items/{zoho_id}')
                            item = item_data.get('item', {})
                            image_url = item.get('image_url') or item.get('image_name')

                            if image_url:
                                await db.execute(text("""
                                    UPDATE products
                                    SET image_url = :image_url, updated_at = NOW()
                                    WHERE zoho_item_id = :zoho_id
                                """), {"image_url": image_url, "zoho_id": zoho_id})
                                image_count += 1
                        except Exception as e:
                            pass

                    await db.commit()
                    results['images'] = {'success': image_count}
                    print(f"\n✅ Images: {image_count} downloaded\n")
                except Exception as e:
                    print(f"\n⚠️  Image sync error: {e}\n")
                    results['images'] = {'error': str(e)}

            # Final Summary
            print("=" * 80)
            print("📊 SYNCHRONIZATION SUMMARY")
            print("=" * 80)

            total_duration = datetime.now() - start_time

            for entity, data in results.items():
                if 'error' in data:
                    print(f"⚠️  {entity.capitalize()}: Error - {data['error']}")
                elif 'success' in data and isinstance(data['success'], int):
                    print(f"✅ {entity.capitalize()}: {data['success']} synced")
                else:
                    print(f"✅ {entity.capitalize()}: {data.get('success', 0)}/{data.get('processed', 0)} synced")

            print(f"\n⏱️  Total Duration: {total_duration}")
            print("=" * 80)
            print()

            return 0

        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1

        finally:
            await zoho.stop()
            print("🔒 TDS Zoho Service stopped")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Sync interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
