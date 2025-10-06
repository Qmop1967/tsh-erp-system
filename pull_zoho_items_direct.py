#!/usr/bin/env python3
"""
Pull items directly from Zoho Inventory API and import to TSH ERP System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import requests
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product, Category

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

def fetch_all_zoho_items(access_token):
    """Fetch all items from Zoho Inventory API with pagination"""
    print("\n📡 Fetching items from Zoho Inventory API...")

    base_url = "https://www.zohoapis.com/inventory/v1/items"
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}'
    }
    params = {
        'organization_id': zoho_config['organization_id'],
        'per_page': 200  # Max items per page
    }

    all_items = []
    page = 1

    while True:
        params['page'] = page
        print(f"   📄 Fetching page {page}...")

        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            if not items:
                break

            all_items.extend(items)
            print(f"   ✅ Retrieved {len(items)} items (Total: {len(all_items)})")

            # Check if there are more pages
            page_context = data.get('page_context', {})
            if not page_context.get('has_more_page', False):
                break

            page += 1
        else:
            print(f"   ❌ Error fetching page {page}: {response.text}")
            break

    print(f"\n✅ Total items fetched: {len(all_items)}")
    return all_items

def import_item_to_database(item, db: Session):
    """Import a single item to database"""

    # Extract SKU
    sku = item.get('sku', '').strip()
    if not sku:
        # Generate SKU from item_id if missing
        sku = f"ZOHO-{item.get('item_id', '')}"

    # Truncate SKU if too long
    if len(sku) > 50:
        sku = sku[:50]

    # Check if item exists
    existing_item = db.query(Product).filter(Product.sku == sku).first()

    # Get or create category
    category_name = item.get('category_name', 'General')
    category = db.query(Category).filter(Category.name == category_name).first()
    if not category:
        category = Category(name=category_name, name_ar=category_name, is_active=True)
        db.add(category)
        db.flush()

    # Get image URL
    image_url = None
    if item.get('image_document_id'):
        image_url = f"https://www.zohoapis.com/inventory/v1/items/{item['item_id']}/image?organization_id={zoho_config['organization_id']}"

    # Prepare product data
    product_data = {
        'sku': sku,
        'name': item.get('name', 'Unnamed Product')[:200],  # Limit name length
        'name_ar': item.get('name', '')[:200],
        'description': item.get('description', ''),
        'description_ar': '',
        'brand': item.get('brand', '')[:100] if item.get('brand') else '',
        'model': item.get('product_type', 'goods')[:100] if item.get('product_type') else 'goods',
        'category_id': category.id,
        'unit_of_measure': item.get('unit', 'pcs') or 'pcs',
        'cost_price': Decimal(str(item.get('purchase_rate', 0) or 0)),
        'unit_price': Decimal(str(item.get('rate', 0) or 0)),
        'is_active': item.get('status') == 'active',
        'is_trackable': item.get('track_inventory', True),
        'reorder_point': int(float(item.get('reorder_level', 0) or 0)),
        'min_stock_level': int(float(item.get('minimum_order_quantity', 0) or 0)),
        'weight': Decimal(str(item.get('weight', 0) or 0)) if item.get('weight') else None,
        'image_url': image_url,
        'barcode': item.get('barcode', '')[:100] if item.get('barcode') else None,
        'tags': [{'zoho_item_id': item.get('item_id')}] if item.get('item_id') else []
    }

    if existing_item:
        # Update existing item
        for key, value in product_data.items():
            setattr(existing_item, key, value)
        return 'updated'
    else:
        # Create new item
        new_item = Product(**product_data)
        db.add(new_item)
        return 'created'

def main():
    """Main function"""
    print("=" * 70)
    print("🚀 Zoho Direct Import to TSH ERP System")
    print("=" * 70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Refresh token
    access_token = refresh_zoho_token()
    if not access_token:
        print("❌ Failed to get access token. Exiting.")
        return

    # Fetch all items from Zoho
    zoho_items = fetch_all_zoho_items(access_token)

    if not zoho_items:
        print("⚠️  No items fetched from Zoho. Exiting.")
        return

    # Get database session
    db = next(get_db())

    try:
        print("\n📦 Importing items to database...")
        print("-" * 70)

        created_count = 0
        updated_count = 0
        error_count = 0

        for idx, item in enumerate(zoho_items, 1):
            try:
                result = import_item_to_database(item, db)

                if result == 'created':
                    created_count += 1
                elif result == 'updated':
                    updated_count += 1

                # Commit every 100 items
                if (created_count + updated_count) % 100 == 0:
                    db.commit()
                    print(f"   ✅ Processed {created_count + updated_count}/{len(zoho_items)} items...")

            except Exception as e:
                error_count += 1
                print(f"   ❌ Error importing item {item.get('sku', 'Unknown')}: {e}")
                db.rollback()
                continue

        # Final commit
        db.commit()

        print("\n" + "=" * 70)
        print("📊 IMPORT SUMMARY")
        print("=" * 70)
        print(f"   📥 Items fetched from Zoho: {len(zoho_items)}")
        print(f"   ✅ New items created:       {created_count}")
        print(f"   🔄 Existing items updated:  {updated_count}")
        print(f"   ❌ Errors:                  {error_count}")
        print("=" * 70)

        # Verify final count
        total_products = db.query(Product).count()
        print(f"\n✅ Total products in database: {total_products:,}")

        print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    main()
