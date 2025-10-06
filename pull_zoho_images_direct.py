#!/usr/bin/env python3
"""
Pull item images directly from Zoho Inventory API
Downloads actual image files and updates database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import requests
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product

# Load Zoho config
with open('app/data/settings/zoho_config.json', 'r') as f:
    zoho_config = json.load(f)

def refresh_zoho_token():
    """Refresh Zoho OAuth token"""
    print("🔄 Refreshing Zoho access token...")

    token_url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        'refresh_token': zoho_config['refresh_token'],
        'client_id': zoho_config['client_id'],
        'client_secret': zoho_config['client_secret'],
        'grant_type': 'refresh_token'
    }

    response = requests.post(token_url, params=params)

    if response.status_code == 200:
        token_data = response.json()
        zoho_config['access_token'] = token_data['access_token']

        # Save updated token
        with open('app/data/settings/zoho_config.json', 'w') as f:
            json.dump(zoho_config, f, indent=2)

        print("✅ Token refreshed successfully")
        return token_data['access_token']
    else:
        print(f"❌ Failed to refresh token: {response.text}")
        return None

def download_image(item_id, access_token, save_path):
    """Download image from Zoho API"""

    image_url = f"https://www.zohoapis.com/inventory/v1/items/{item_id}/image"
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}'
    }
    params = {
        'organization_id': zoho_config['organization_id']
    }

    try:
        response = requests.get(image_url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            # Save image file
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False

    except Exception as e:
        print(f"      ⚠️  Download error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("🖼️  Zoho Images Direct Download")
    print("=" * 70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Refresh token
    access_token = refresh_zoho_token()
    if not access_token:
        print("❌ Failed to get access token. Exiting.")
        return

    # Get database session
    db = next(get_db())

    try:
        # Get all products that have Zoho item IDs
        print("\n📊 Fetching products with Zoho item IDs...")
        products = db.query(Product).all()

        products_with_images = []
        for product in products:
            if product.tags and isinstance(product.tags, list):
                for tag in product.tags:
                    if isinstance(tag, dict) and tag.get('zoho_item_id'):
                        products_with_images.append({
                            'product': product,
                            'zoho_item_id': tag['zoho_item_id']
                        })
                        break

        print(f"✅ Found {len(products_with_images)} products with Zoho item IDs\n")

        # Create images directory
        images_dir = Path('frontend/public/images/products')
        images_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Images will be saved to: {images_dir}\n")
        print("🔄 Downloading images...")
        print("-" * 70)

        stats = {
            'total': len(products_with_images),
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'updated': 0
        }

        for idx, item in enumerate(products_with_images, 1):
            product = item['product']
            zoho_item_id = item['zoho_item_id']

            # Generate filename
            filename = f"{product.sku.replace('/', '-')}.jpg"
            save_path = images_dir / filename
            relative_path = f"/images/products/{filename}"

            # Skip if already downloaded
            if save_path.exists():
                stats['skipped'] += 1
                if idx % 100 == 0:
                    print(f"   ⏳ Progress: {idx}/{stats['total']} (Downloaded: {stats['downloaded']}, Skipped: {stats['skipped']})")
                continue

            # Download image
            print(f"   📥 [{idx}/{stats['total']}] Downloading: {product.sku} ({product.name[:50]})")

            if download_image(zoho_item_id, access_token, save_path):
                stats['downloaded'] += 1

                # Update product image URL in database
                product.image_url = relative_path

                # Add to images array
                if not product.images:
                    product.images = []

                # Check if image already in array
                image_exists = any(
                    img.get('url') == relative_path
                    for img in product.images
                    if isinstance(img, dict)
                )

                if not image_exists:
                    product.images.append({
                        'url': relative_path,
                        'source': 'zoho',
                        'zoho_item_id': zoho_item_id,
                        'downloaded_at': datetime.now().isoformat()
                    })

                stats['updated'] += 1

                # Commit every 50 items
                if stats['downloaded'] % 50 == 0:
                    db.commit()
                    print(f"      ✅ Committed {stats['downloaded']} images to database")

            else:
                stats['failed'] += 1
                # Remove failed download file if exists
                if save_path.exists():
                    save_path.unlink()

        # Final commit
        db.commit()

        print("\n" + "=" * 70)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 70)
        print(f"   📦 Total products:          {stats['total']}")
        print(f"   ✅ Images downloaded:       {stats['downloaded']}")
        print(f"   ⏭️  Already existed:         {stats['skipped']}")
        print(f"   ❌ Failed downloads:        {stats['failed']}")
        print(f"   🔄 Database updated:        {stats['updated']}")
        print("=" * 70)

        print(f"\n✅ Images saved to: {images_dir.absolute()}")
        print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    main()
