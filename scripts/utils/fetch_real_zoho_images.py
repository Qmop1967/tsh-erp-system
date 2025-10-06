#!/usr/bin/env python3
"""
Fetch REAL Images from Zoho Inventory API
This script fetches actual product images from Zoho (not placeholders)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import requests
import time
from pathlib import Path
from datetime import datetime

def get_fresh_access_token():
    """Get a fresh access token from Zoho"""
    config_file = Path("app/data/settings/zoho_config.json")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("🔐 Refreshing Zoho access token...")
    
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": config['refresh_token'],
        "client_id": config['client_id'],
        "client_secret": config['client_secret'],
        "grant_type": "refresh_token"
    }
    
    try:
        response = requests.post(token_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            if access_token:
                print(f"✅ Access token obtained: {access_token[:20]}...")
                
                # Update config file with new token
                config['access_token'] = access_token
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                print("✅ Config file updated with new token")
                
                return access_token, config['organization_id']
            else:
                print(f"⚠️  No access_token in response: {data}")
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
    
    return None, None

def fetch_real_images_from_zoho():
    """Fetch real image URLs from Zoho Inventory API"""
    
    print("\n🖼️  ZOHO REAL IMAGE FETCHER")
    print("=" * 70)
    print()
    
    # Get fresh access token
    access_token, org_id = get_fresh_access_token()
    
    if not access_token:
        print("❌ Cannot proceed without valid access token")
        print("\n📋 MANUAL STEPS REQUIRED:")
        print("   1. Go to https://api-console.zoho.com/")
        print("   2. Generate a new access token")
        print("   3. Update app/data/settings/zoho_config.json")
        return None
    
    print()
    print("📦 Fetching items from Zoho Inventory...")
    print("-" * 70)
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    base_url = "https://www.zohoapis.com/inventory/v1"
    all_items = []
    page = 1
    items_with_images = 0
    
    while True:
        url = f"{base_url}/items"
        params = {
            "organization_id": org_id,
            "page": page,
            "per_page": 200
        }
        
        try:
            print(f"  📄 Page {page}...", end=" ", flush=True)
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    print("(no more items)")
                    break
                
                print(f"✅ {len(items)} items")
                
                # Process items
                for item in items:
                    # Check for real images
                    has_real_image = False
                    
                    # Zoho image fields
                    if item.get('image_name') and item.get('image_id'):
                        # Construct real Zoho image URL
                        item_id = item.get('item_id')
                        real_image_url = f"{base_url}/items/{item_id}/image"
                        item['real_image_url'] = real_image_url
                        has_real_image = True
                        items_with_images += 1
                    
                    # Store the item
                    all_items.append({
                        'zoho_item_id': item.get('item_id'),
                        'code': item.get('sku'),
                        'name_en': item.get('name'),
                        'name_ar': item.get('name'),
                        'description_en': item.get('description', ''),
                        'description_ar': item.get('description', ''),
                        'brand': item.get('brand', ''),
                        'model': item.get('product_type', ''),
                        'unit_of_measure': item.get('unit'),
                        'cost_price_usd': str(item.get('purchase_rate', 0)),
                        'selling_price_usd': str(item.get('rate', 0)),
                        'track_inventory': item.get('track_inventory', True),
                        'reorder_level': str(item.get('reorder_level', 0)),
                        'is_active': item.get('status') == 'active',
                        'image_name': item.get('image_name'),
                        'image_id': item.get('image_id'),
                        'image_url': item.get('real_image_url') if has_real_image else None
                    })
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            elif response.status_code == 401:
                print("❌ Authentication failed!")
                print("   Token may have expired. Please regenerate.")
                break
            else:
                print(f"❌ Error {response.status_code}")
                print(f"   {response.text[:200]}")
                break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print()
    print("=" * 70)
    print("📊 FETCH RESULTS:")
    print(f"   Total Items:       {len(all_items)}")
    print(f"   Items with Images: {items_with_images}")
    print(f"   Pages Processed:   {page - 1}")
    print("=" * 70)
    print()
    
    if all_items:
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"zoho_items_with_REAL_images_{timestamp}.json"
        
        print(f"💾 Saving to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_items, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(all_items)} items")
        print()
        
        if items_with_images > 0:
            print(f"🎉 SUCCESS! Found {items_with_images} items with REAL Zoho images!")
            print()
            print("🚀 NEXT STEPS:")
            print("   1. Backup current file:")
            print("      cp all_zoho_inventory_items.json all_zoho_inventory_items_backup.json")
            print()
            print("   2. Replace with new data:")
            print(f"      cp {output_file} all_zoho_inventory_items.json")
            print()
            print("   3. Re-run the sync:")
            print('      curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/item/execute?sync_images=true"')
            print()
        else:
            print("⚠️  No items have images in Zoho Inventory.")
            print("   Your products may not have images uploaded in Zoho.")
            print()
        
        # Show sample
        print("📋 Sample item with image:")
        for item in all_items[:10]:
            if item.get('image_url'):
                print(f"   - {item['name_en'][:50]}")
                print(f"     Image: {item['image_url']}")
                break
    else:
        print("❌ No items fetched. Please check authentication.")
    
    return output_file if all_items else None

if __name__ == "__main__":
    print("\n🚀 Starting Real Zoho Image Fetch Process...")
    print()
    
    result_file = fetch_real_images_from_zoho()
    
    if result_file:
        print("\n✅ Real image fetch completed successfully!")
        print(f"📁 Output file: {result_file}")
    else:
        print("\n❌ Image fetch failed. Please check errors above.")


