#!/usr/bin/env python3
"""
Sync stock quantities from Zoho Inventory with pagination
Uses Zoho Inventory API with optimized pagination to reduce API calls
"""

import os
import sys
import asyncio
import httpx
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/home/deploy/TSH_ERP_Ecosystem')
from app.services.zoho_token_manager import get_token_manager
from app.services.zoho_rate_limiter import get_rate_limiter

# Load environment variables
load_dotenv('/home/deploy/TSH_ERP_Ecosystem/.env')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

# Zoho configuration
ORGANIZATION_ID = os.getenv('ZOHO_ORGANIZATION_ID', '748369814')
INVENTORY_API_BASE = 'https://www.zohoapis.com/inventory/v1'

# Pagination settings
PAGE_SIZE = 200  # Zoho Inventory allows up to 200 items per page
DELAY_BETWEEN_PAGES = 0.5  # Half second between pages


async def sync_stock_paginated():
    """Sync stock quantities from Zoho Inventory with pagination"""

    print("=" * 60)
    print("Zoho Inventory Stock Sync (Paginated)")
    print("=" * 60)
    print()

    # Get database engine
    engine = create_engine(DATABASE_URL)

    # Get token manager and rate limiter
    token_manager = get_token_manager()
    rate_limiter = get_rate_limiter()

    headers = await token_manager.get_auth_headers()
    if not headers:
        print("❌ ERROR: Unable to obtain Zoho OAuth token")
        return

    print("✅ Zoho OAuth token obtained")
    print()

    # Statistics
    total_updated = 0
    total_skipped = 0
    total_errors = 0
    start_time = time.time()

    page = 1
    has_more_pages = True

    async with httpx.AsyncClient(timeout=30.0) as client:
        while has_more_pages:
            print(f"\n{'='*60}")
            print(f"Processing Page {page}")
            print(f"{'='*60}\n")

            try:
                # Use rate limiter
                await rate_limiter.acquire(f"items?page={page}")

                # Fetch items from Zoho Inventory
                url = f"{INVENTORY_API_BASE}/items"
                params = {
                    'organization_id': ORGANIZATION_ID,
                    'page': page,
                    'per_page': PAGE_SIZE
                }

                response = await client.get(url, params=params, headers=headers)
                rate_limiter.release()

                if response.status_code != 200:
                    print(f"❌ API Error: HTTP {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    rate_limiter.throttle_on_error(response.status_code)
                    break

                data = response.json()

                # Check if we have items
                if 'items' not in data or not data['items']:
                    print(f"✅ No more items on page {page}")
                    has_more_pages = False
                    break

                items = data['items']
                page_info = data.get('page_context', {})

                print(f"📦 Retrieved {len(items)} items from Zoho Inventory")

                # Update stock in database
                updated_count = 0
                skipped_count = 0
                error_count = 0

                with engine.connect() as conn:
                    for idx, item in enumerate(items, 1):
                        zoho_item_id = item.get('item_id')
                        stock_quantity = item.get('stock_on_hand', 0)
                        item_name = item.get('name', 'Unknown')

                        if not zoho_item_id:
                            skipped_count += 1
                            continue

                        try:
                            # Update stock quantity in database
                            update_query = text("""
                                UPDATE products
                                SET stock_quantity = :stock_quantity,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE zoho_item_id = :zoho_item_id
                            """)

                            result = conn.execute(update_query, {
                                'stock_quantity': stock_quantity,
                                'zoho_item_id': zoho_item_id
                            })
                            conn.commit()

                            if result.rowcount > 0:
                                updated_count += 1
                                if stock_quantity > 0:
                                    print(f"  [{idx}] ✅ {item_name}: {stock_quantity} units")
                            else:
                                skipped_count += 1

                        except Exception as e:
                            error_count += 1
                            print(f"  [{idx}] ❌ Error updating {item_name}: {str(e)}")

                total_updated += updated_count
                total_skipped += skipped_count
                total_errors += error_count

                # Print page summary
                print(f"\n{'='*60}")
                print(f"Page {page} Complete")
                print(f"  ✅ Updated: {updated_count}")
                print(f"  ⏭️  Skipped: {skipped_count}")
                print(f"  ❌ Errors: {error_count}")
                print(f"{'='*60}")

                # Check if there are more pages
                has_more_page = page_info.get('has_more_page', False)
                if not has_more_page:
                    print(f"\n✅ No more pages available")
                    has_more_pages = False
                else:
                    page += 1
                    print(f"\n⏸️  Waiting {DELAY_BETWEEN_PAGES}s before next page...")
                    await asyncio.sleep(DELAY_BETWEEN_PAGES)

            except Exception as e:
                print(f"\n❌ Error processing page {page}: {str(e)}")
                rate_limiter.release()
                break

    # Final summary
    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("Stock Sync Complete!")
    print("=" * 60)
    print(f"✅ Successfully updated: {total_updated}")
    print(f"⏭️  Skipped: {total_skipped}")
    print(f"❌ Errors: {total_errors}")
    print(f"📊 Total processed: {total_updated + total_skipped + total_errors}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"📄 Pages processed: {page}")
    print()

    # Show stock statistics
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) as total_products,
                   COUNT(CASE WHEN stock_quantity > 0 THEN 1 END) as with_stock,
                   COUNT(CASE WHEN stock_quantity = 0 THEN 1 END) as no_stock,
                   SUM(stock_quantity) as total_stock
            FROM products
            WHERE zoho_item_id IS NOT NULL AND is_active = true
        """))
        stats = result.fetchone()

        print("📊 Stock Statistics:")
        print(f"  Total products: {stats.total_products}")
        print(f"  With stock (>0): {stats.with_stock}")
        print(f"  No stock (=0): {stats.no_stock}")
        print(f"  Total stock units: {stats.total_stock}")

    print()
    print("🎉 Stock sync completed successfully!")
    print()
    print("Rate Limiter Statistics:")
    rate_stats = rate_limiter.get_stats()
    print(f"  API calls this minute: {rate_stats['requests_this_minute']}/{rate_stats['max_per_minute']}")
    print(f"  API calls today: {rate_stats['requests_today']}/{rate_stats['max_per_day']}")
    print(f"  Total throttles: {rate_stats['total_throttles']}")
    print()


if __name__ == '__main__':
    asyncio.run(sync_stock_paginated())
