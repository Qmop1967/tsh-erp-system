#!/usr/bin/env python3
"""
Download product images from Zoho Books with pagination and monitoring
This script downloads images in batches to reduce API calls and memory usage
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

# Add parent directory to path to import app modules
sys.path.insert(0, '/home/deploy/TSH_ERP_Ecosystem')
from app.services.zoho_token_manager import get_token_manager

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

# Image storage configuration
IMAGE_DIR = Path('/var/www/product-images')
IMAGE_BASE_URL = 'https://erp.tsh.sale/product-images'

# Pagination settings
BATCH_SIZE = 100  # Download 100 images per batch
DELAY_BETWEEN_BATCHES = 2  # Seconds to wait between batches
DELAY_BETWEEN_IMAGES = 0.1  # Seconds to wait between individual image downloads


async def download_images_batch(products, batch_num, total_batches, headers):
    """Download a batch of product images"""

    success_count = 0
    failed_count = 0
    skipped_count = 0

    print(f"\n{'='*60}")
    print(f"Processing Batch {batch_num}/{total_batches}")
    print(f"Products in this batch: {len(products)}")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for idx, product in enumerate(products, 1):
            product_id = product.id
            zoho_item_id = product.zoho_item_id
            sku = product.sku or f"product_{product_id}"
            name = product.name

            # Calculate overall progress
            overall_idx = ((batch_num - 1) * BATCH_SIZE) + idx

            print(f"[{overall_idx}] {name}")
            print(f"  SKU: {sku}")
            print(f"  Zoho Item ID: {zoho_item_id}")

            # Check if image already exists
            existing_images = list(IMAGE_DIR.glob(f"{sku}.*"))
            if existing_images:
                print(f"  ⏭️  Image already exists: {existing_images[0].name}")
                skipped_count += 1
                print()
                continue

            try:
                # Fetch image from Zoho
                image_url = f"{INVENTORY_API_BASE}/items/{zoho_item_id}/image"
                params = {"organization_id": ORGANIZATION_ID}

                response = await client.get(image_url, params=params, headers=headers)

                if response.status_code == 200:
                    # Check content type to determine extension
                    content_type = response.headers.get('content-type', 'image/jpeg')

                    if 'png' in content_type.lower():
                        ext = 'png'
                    elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
                        ext = 'jpg'
                    elif 'webp' in content_type.lower():
                        ext = 'webp'
                    else:
                        ext = 'jpg'  # default

                    final_filename = f"{sku}.{ext}"
                    final_path = IMAGE_DIR / final_filename

                    # Save image
                    with open(final_path, 'wb') as f:
                        f.write(response.content)

                    image_size = len(response.content) / 1024  # KB
                    print(f"  ✅ Downloaded: {final_filename} ({image_size:.1f} KB)")

                    # Update database with local image URL
                    local_image_url = f"{IMAGE_BASE_URL}/{final_filename}"
                    engine = create_engine(DATABASE_URL)
                    with engine.connect() as conn:
                        update_query = text("""
                            UPDATE products
                            SET image_url = :image_url,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = :product_id
                        """)
                        conn.execute(update_query, {
                            'image_url': local_image_url,
                            'product_id': product_id
                        })
                        conn.commit()

                    print(f"  ✅ Database updated: {local_image_url}")
                    success_count += 1

                elif response.status_code == 404:
                    print(f"  ⚠️  No image available in Zoho")
                    skipped_count += 1

                else:
                    print(f"  ❌ Failed: HTTP {response.status_code}")
                    print(f"     Response: {response.text[:100]}")
                    failed_count += 1

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                failed_count += 1

            print()

            # Small delay between images to avoid rate limiting
            await asyncio.sleep(DELAY_BETWEEN_IMAGES)

    return success_count, failed_count, skipped_count


async def download_product_images_paginated():
    """Download all product images from Zoho with pagination"""

    print("=" * 60)
    print("Zoho Product Images Download Script (Paginated)")
    print("=" * 60)
    print()

    # Create image directory if it doesn't exist
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Image directory: {IMAGE_DIR}")
    print()

    # Get database engine
    engine = create_engine(DATABASE_URL)

    # Get token manager
    token_manager = get_token_manager()
    headers = await token_manager.get_auth_headers()

    if not headers:
        print("❌ ERROR: Unable to obtain Zoho OAuth token")
        return

    print("✅ Zoho OAuth token obtained")
    print()

    # Count total products
    with engine.connect() as conn:
        count_query = text("""
            SELECT COUNT(*) as total
            FROM products
            WHERE zoho_item_id IS NOT NULL
            AND is_active = true
        """)
        total_count = conn.execute(count_query).scalar()

    print(f"📊 Total products to process: {total_count}")

    # Calculate number of batches
    total_batches = (total_count + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"📦 Total batches: {total_batches} (batch size: {BATCH_SIZE})")
    print()

    # Track overall statistics
    total_success = 0
    total_failed = 0
    total_skipped = 0

    start_time = time.time()

    # Process in batches
    for batch_num in range(1, total_batches + 1):
        offset = (batch_num - 1) * BATCH_SIZE

        # Fetch batch of products
        with engine.connect() as conn:
            query = text("""
                SELECT id, zoho_item_id, sku, name, image_url
                FROM products
                WHERE zoho_item_id IS NOT NULL
                AND is_active = true
                ORDER BY name
                LIMIT :limit OFFSET :offset
            """)
            result = conn.execute(query, {"limit": BATCH_SIZE, "offset": offset})
            products = result.fetchall()

        if not products:
            break

        # Download images for this batch
        success, failed, skipped = await download_images_batch(
            products, batch_num, total_batches, headers
        )

        total_success += success
        total_failed += failed
        total_skipped += skipped

        # Print batch summary
        elapsed_time = time.time() - start_time
        avg_time_per_batch = elapsed_time / batch_num
        remaining_batches = total_batches - batch_num
        estimated_remaining = remaining_batches * avg_time_per_batch

        print(f"{'='*60}")
        print(f"Batch {batch_num}/{total_batches} Complete")
        print(f"  ✅ Downloaded: {success}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏭️  Skipped: {skipped}")
        print(f"  ⏱️  Elapsed: {elapsed_time/60:.1f} minutes")
        print(f"  ⏳ Estimated remaining: {estimated_remaining/60:.1f} minutes")
        print(f"{'='*60}\n")

        # Delay between batches (except after last batch)
        if batch_num < total_batches:
            print(f"⏸️  Waiting {DELAY_BETWEEN_BATCHES} seconds before next batch...\n")
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)

    # Final summary
    total_time = time.time() - start_time

    print("=" * 60)
    print("Download Complete!")
    print("=" * 60)
    print(f"✅ Successfully downloaded: {total_success}")
    print(f"❌ Failed: {total_failed}")
    print(f"⏭️  Skipped (already exist or no image): {total_skipped}")
    print(f"📊 Total processed: {total_count}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print()
    print(f"Images saved to: {IMAGE_DIR}")
    print(f"Image URL pattern: {IMAGE_BASE_URL}/{{sku}}.{{ext}}")
    print()

    # Set proper permissions
    print("Setting file permissions...")
    os.system(f"chmod -R 755 {IMAGE_DIR}")
    print("✅ Permissions set")
    print()

    print("🎉 Done! Product images are now stored locally.")
    print()
    print("Next steps:")
    print("1. Clear Flutter cache: https://consumer.tsh.sale/force-reload.html?auto=1")
    print("2. Visit consumer app: https://consumer.tsh.sale")


if __name__ == '__main__':
    asyncio.run(download_product_images_paginated())
