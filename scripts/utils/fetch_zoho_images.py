#!/usr/bin/env python3
"""
Fetch Item Images from Zoho Inventory API
This script updates the existing Zoho items data with image URLs
"""

import json
import requests
import time
from pathlib import Path

def get_access_token():
    """Get a fresh access token using refresh token"""
    config_file = Path("app/data/settings/zoho_config.json")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    client_id = config['client_id']
    client_secret = config['client_secret']
    refresh_token = config['refresh_token']
    
    print("� Getting fresh access token from Zoho...")
    
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    
    try:
        response = requests.post(token_url, params=params)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            if access_token:
                print("✅ Access token obtained successfully")
                print(f"   Token: {access_token[:20]}...")
                return access_token
            else:
                print("❌ No access token in response")
                print(f"   Response: {data}")
                return None
        else:
            print(f"❌ Failed to get access token: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def fetch_images_from_zoho():
    """Fetch image URLs for all items from Zoho API"""
    
    print("�️  Zoho Image Fetcher")
    print("=" * 70)
    
    # Load configuration
    config_file = Path("app/data/settings/zoho_config.json")
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    ORGANIZATION_ID = config['organization_id']
    
    # Get fresh access token
    ZOHO_ACCESS_TOKEN = get_access_token()
    if not ZOHO_ACCESS_TOKEN:
        print("❌ Could not obtain access token. Exiting.")
        return
    
    # Load existing items
    items_file = Path("all_zoho_inventory_items.json")
    if not items_file.exists():
        print(f"❌ File not found: {items_file}")
        return
    
    print(f"📂 Loading items from: {items_file}")
    with open(items_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"✅ Loaded {len(items)} items")
    print()
    
    # Headers for API calls
    headers = {
        "Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Fetch images for each item
    updated_items = []
    images_found = 0
    errors = 0
    
    print("🔄 Fetching image URLs from Zoho API...")
    print("-" * 70)
    
    for idx, item in enumerate(items, 1):
        item_id = item.get('zoho_item_id')
        item_name = item.get('name_en', 'Unknown')
        
        if not item_id:
            print(f"  ⚠️  Skipping item {idx}: No zoho_item_id")
            updated_items.append(item)
            continue
        
        # Get full item details from Zoho API
        url = f"https://inventory.zoho.com/api/v1/items/{item_id}"
        params = {"organization_id": ORGANIZATION_ID}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                item_details = data.get('item', {})
                
                # Check for image fields
                image_url = item_details.get('image_url')
                image_name = item_details.get('image_name')
                image_id = item_details.get('image_id')
                
                # Add image fields to item
                if image_url:
                    item['image_url'] = image_url
                    images_found += 1
                    status = "✅ Image found"
                else:
                    status = "⚪ No image"
                
                if image_name:
                    item['image_name'] = image_name
                if image_id:
                    item['image_id'] = image_id
                
                # Progress indicator
                if idx % 50 == 0:
                    print(f"  ⏳ Processed {idx}/{len(items)} items... ({images_found} images found)")
                
            elif response.status_code == 401:
                print(f"\n❌ Authentication failed! Check your access token.")
                print("   Your token may have expired.")
                break
            else:
                print(f"  ❌ Item {idx}: API error {response.status_code}")
                errors += 1
            
            updated_items.append(item)
            
            # Rate limiting - be nice to Zoho API
            time.sleep(0.1)  # 100ms delay between requests
            
        except Exception as e:
            print(f"  ❌ Error fetching item {idx}: {str(e)}")
            errors += 1
            updated_items.append(item)
    
    print()
    print("=" * 70)
    print("📊 RESULTS:")
    print(f"   Total Items: {len(items)}")
    print(f"   Images Found: {images_found}")
    print(f"   No Images: {len(items) - images_found}")
    print(f"   Errors: {errors}")
    print()
    
    if images_found > 0:
        # Save updated data
        output_file = "all_zoho_inventory_items_with_images.json"
        print(f"💾 Saving updated data to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_items, f, indent=2, ensure_ascii=False)
        
        print("✅ File saved successfully!")
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Review the updated file")
        print("   2. Replace original file:")
        print(f"      cp {output_file} all_zoho_inventory_items.json")
        print("   3. Re-run the sync:")
        print('      curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/item/execute?sync_images=true"')
        print()
    else:
        print("⚠️  No images found in Zoho items.")
        print("   This could mean:")
        print("   - Items don't have images uploaded in Zoho")
        print("   - Images are stored differently in Zoho")
        print("   - API access doesn't include image fields")
        print()

if __name__ == "__main__":
    fetch_images_from_zoho()
