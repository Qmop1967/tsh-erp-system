#!/usr/bin/env python3
"""
Download all product images from Zoho Books and store them locally
This script will:
1. Fetch all products with Zoho item IDs from database
2. Download their images from Zoho API
3. Save images to /var/www/product-images/
4. Update database with local image URLs
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

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


async def download_product_images():
    """Download all product images from Zoho and store locally"""

    print("=" * 60)
    print("Zoho Product Images Download Script")
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

    # Fetch all products with Zoho item IDs
    with engine.connect() as conn:
        query = text("""
            SELECT id, zoho_item_id, sku, name, image_url
            FROM products
            WHERE zoho_item_id IS NOT NULL
            AND is_active = true
            ORDER BY name
        """)
        result = conn.execute(query)
        products = result.fetchall()

    print(f"📊 Found {len(products)} products with Zoho item IDs")
    print()

    # Download images
    success_count = 0
    failed_count = 0
    skipped_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        for idx, product in enumerate(products, 1):
            product_id = product.id
            zoho_item_id = product.zoho_item_id
            sku = product.sku or f"product_{product_id}"
            name = product.name

            print(f"[{idx}/{len(products)}] {name}")
            print(f"  SKU: {sku}")
            print(f"  Zoho Item ID: {zoho_item_id}")

            # Determine file extension (default to jpg)
            # We'll detect the actual format from the response
            temp_filename = f"{sku}.tmp"
            temp_path = IMAGE_DIR / temp_filename

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

            # Small delay to avoid rate limiting
            if idx % 10 == 0:
                await asyncio.sleep(1)

    # Summary
    print("=" * 60)
    print("Download Complete!")
    print("=" * 60)
    print(f"✅ Successfully downloaded: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⚠️  Skipped (no image): {skipped_count}")
    print(f"📊 Total processed: {len(products)}")
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
    print("1. Restart the TSH ERP service: systemctl restart tsh-erp")
    print("2. Clear Flutter cache: https://consumer.tsh.sale/clear-cache.html")
    print("3. Visit consumer app: https://consumer.tsh.sale")


if __name__ == '__main__':
    asyncio.run(download_product_images())
