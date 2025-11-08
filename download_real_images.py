#!/usr/bin/env python3
"""
Download Real Product Images from Zoho Books
=============================================

Downloads actual product images from Zoho in batches with rate limiting.
Stores images locally and updates database with local URLs.

Author: TSH ERP Team
Date: November 7, 2025
"""

import asyncio
import aiohttp
import asyncpg
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple
import time

# Configuration
ZOHO_CLIENT_ID = "1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ"
ZOHO_CLIENT_SECRET = "0581c245cd951e1453042ff2bcf223768e128fed9f"
ZOHO_REFRESH_TOKEN = "1000.456d43e0209a40ba2d580747be746a54.1aa75b48b965e8a8562dc89d2a15e517"
ZOHO_ORG_ID = "748369814"

# Database
DB_CONFIG = {
    'host': 'tsh_postgres',
    'port': 5432,
    'database': 'tsh_erp',
    'user': 'tsh_admin',
    'password': 'TSH@2025Secure!Production'
}

# Storage
IMAGE_DIR = Path('/var/www/html/images/products')
IMAGE_BASE_URL = 'https://erp.tsh.sale/images/products'

# Batch settings
BATCH_SIZE = 50  # Images per batch
DELAY_BETWEEN_BATCHES = 2.0  # Seconds
DELAY_BETWEEN_IMAGES = 0.2  # Seconds


class ImageDownloadStats:
    def __init__(self):
        self.total = 0
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0
        self.start_time = time.time()

    def print_progress(self, current):
        elapsed = time.time() - self.start_time
        rate = self.downloaded / elapsed if elapsed > 0 else 0
        print(f"\n{'='*70}")
        print(f"Progress: {current}/{self.total}")
        print(f"Downloaded: {self.downloaded} | Skipped: {self.skipped} | Failed: {self.failed}")
        print(f"Rate: {rate:.1f} images/sec | Elapsed: {elapsed/60:.1f} min")
        print(f"{'='*70}\n")


async def get_access_token():
    """Get Zoho OAuth access token"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://accounts.zoho.com/oauth/v2/token',
            data={
                'refresh_token': ZOHO_REFRESH_TOKEN,
                'client_id': ZOHO_CLIENT_ID,
                'client_secret': ZOHO_CLIENT_SECRET,
                'grant_type': 'refresh_token'
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data['access_token']
            raise Exception(f"Failed to get token: {await response.text()}")


def detect_image_extension(image_data: bytes) -> str:
    """Detect image format from binary data"""
    if image_data.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    elif image_data.startswith(b'\x89PNG'):
        return 'png'
    elif image_data.startswith(b'GIF'):
        return 'gif'
    elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
        return 'webp'
    return 'jpg'  # default


async def download_image_from_zoho(
    session: aiohttp.ClientSession,
    zoho_item_id: str,
    access_token: str
) -> Optional[bytes]:
    """Download image bytes from Zoho Books"""
    try:
        url = f"https://www.zohoapis.com/books/v3/items/{zoho_item_id}/image"
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        params = {'organization_id': ZOHO_ORG_ID}

        async with session.get(url, headers=headers, params=params, timeout=30) as response:
            if response.status == 200:
                return await response.read()
            elif response.status == 404:
                return None  # No image available
            else:
                print(f"    ⚠️  HTTP {response.status}")
                return None
    except Exception as e:
        print(f"    ❌ Download error: {e}")
        return None


def save_image_locally(zoho_item_id: str, image_data: bytes) -> Tuple[str, str]:
    """Save image to local filesystem"""
    # Generate filename
    image_hash = hashlib.md5(image_data).hexdigest()[:8]
    extension = detect_image_extension(image_data)
    filename = f"item_{zoho_item_id}_{image_hash}.{extension}"

    # Save file
    file_path = IMAGE_DIR / filename
    with open(file_path, 'wb') as f:
        f.write(image_data)

    # Generate public URL
    public_url = f"{IMAGE_BASE_URL}/{filename}"

    return str(file_path), public_url


async def process_batch(
    products: list,
    batch_num: int,
    total_batches: int,
    access_token: str,
    stats: ImageDownloadStats
):
    """Process a batch of products"""

    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        async with aiohttp.ClientSession() as session:
            for idx, product in enumerate(products, 1):
                product_id = product['id']
                zoho_item_id = product['zoho_item_id']
                name = product['name']

                overall_idx = ((batch_num - 1) * BATCH_SIZE) + idx

                print(f"[{overall_idx}/{stats.total}] {name}")
                print(f"  Zoho ID: {zoho_item_id}")

                # Check if already has local image
                if product['image_url'] and not 'placeholder' in product['image_url']:
                    print(f"  ⏭️  Already has image")
                    stats.skipped += 1
                    await asyncio.sleep(0.1)
                    continue

                # Download from Zoho
                image_data = await download_image_from_zoho(session, zoho_item_id, access_token)

                if not image_data:
                    print(f"  ⏭️  No image available in Zoho")
                    stats.skipped += 1
                    await asyncio.sleep(0.1)
                    continue

                try:
                    # Save locally
                    local_path, public_url = save_image_locally(zoho_item_id, image_data)

                    # Update database
                    await conn.execute("""
                        UPDATE products
                        SET image_url = $1, updated_at = NOW()
                        WHERE id = $2
                    """, public_url, product_id)

                    image_size = len(image_data) / 1024
                    print(f"  ✅ Downloaded: {image_size:.1f} KB")
                    print(f"  💾 URL: {public_url}")

                    stats.downloaded += 1

                except Exception as e:
                    print(f"  ❌ Save failed: {e}")
                    stats.failed += 1

                # Rate limiting
                await asyncio.sleep(DELAY_BETWEEN_IMAGES)

        # Print batch summary
        if batch_num % 5 == 0 or batch_num == total_batches:
            stats.print_progress(batch_num * BATCH_SIZE)

    finally:
        await conn.close()


async def main():
    """Main download function"""

    print("="*70)
    print("🚀 TSH ERP - Real Image Download from Zoho Books")
    print("="*70)
    print()

    # Create image directory
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Image directory: {IMAGE_DIR}")
    print()

    # Get OAuth token
    print("🔑 Getting Zoho access token...")
    access_token = await get_access_token()
    print("✅ Token obtained")
    print()

    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)

    # Get products that need images
    print("📊 Fetching products from database...")
    products = await conn.fetch("""
        SELECT id, zoho_item_id, name, image_url
        FROM products
        WHERE zoho_item_id IS NOT NULL
        AND is_active = true
        AND actual_available_stock > 0
        ORDER BY name
    """)

    await conn.close()

    stats = ImageDownloadStats()
    stats.total = len(products)

    print(f"✅ Found {stats.total} products")
    print()

    # Calculate batches
    total_batches = (stats.total + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"📦 Processing in {total_batches} batches (batch size: {BATCH_SIZE})")
    print()

    # Process in batches
    for batch_num in range(1, total_batches + 1):
        start_idx = (batch_num - 1) * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, stats.total)
        batch_products = products[start_idx:end_idx]

        print(f"\n{'='*70}")
        print(f"Batch {batch_num}/{total_batches} - Products {start_idx+1} to {end_idx}")
        print(f"{'='*70}\n")

        await process_batch(batch_products, batch_num, total_batches, access_token, stats)

        # Delay between batches
        if batch_num < total_batches:
            print(f"\n⏸️  Waiting {DELAY_BETWEEN_BATCHES}s before next batch...")
            await asyncio.sleep(DELAY_BETWEEN_BATCHES)

    # Final summary
    elapsed = time.time() - stats.start_time

    print("\n" + "="*70)
    print("✅ DOWNLOAD COMPLETE!")
    print("="*70)
    print(f"Total Products:     {stats.total}")
    print(f"Downloaded:         {stats.downloaded}")
    print(f"Skipped:            {stats.skipped}")
    print(f"Failed:             {stats.failed}")
    print(f"Success Rate:       {(stats.downloaded/stats.total*100):.1f}%")
    print(f"Total Time:         {elapsed/60:.1f} minutes")
    print(f"Average Rate:       {stats.downloaded/elapsed:.1f} images/sec")
    print("="*70)
    print()
    print(f"📁 Images saved to: {IMAGE_DIR}")
    print(f"🌐 Base URL: {IMAGE_BASE_URL}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
