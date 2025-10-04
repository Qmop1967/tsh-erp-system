#!/usr/bin/env python3
"""
Fetch 20 more item images from Zoho Inventory API
Uses updated access token from config
"""

import json
import requests
import time
from pathlib import Path

def fetch_20_more_images():
    """Fetch 20 more images from Zoho"""
    
    print("🖼️  Fetching 20 More Images from Zoho")
    print("=" * 70)
    
    # Load config with updated token
    config_file = Path("app/data/settings/zoho_config.json")
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    ACCESS_TOKEN = config['access_token']
    ORG_ID = config['organization_id']
    
    print(f"✅ Access Token: {ACCESS_TOKEN[:20]}...")
    print(f"✅ Organization ID: {ORG_ID}")
    print()
    
    # Load existing items
    items_file = Path("all_zoho_inventory_items.json")
    with open(items_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"📦 Loaded {len(items)} items from local file")
    
    # Count how many already have images
    items_with_images = sum(1 for item in items if item.get('image_url'))
    print(f"📷 Items with images already: {items_with_images}")
    print()
    
    # Headers for API calls
    headers = {
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Find items without images and fetch details for 20 of them
    items_to_update = []
    for item in items:
        if not item.get('image_url'):
            items_to_update.append(item)
            if len(items_to_update) >= 30:  # Fetch 30 to ensure we get 20 with images
                break
    
    print(f"🔍 Fetching details for {len(items_to_update)} items to find images...")
    print("-" * 70)
    
    updated_count = 0
    images_found = 0
    errors = 0
    
    for idx, item in enumerate(items_to_update, 1):
        item_id = item.get('zoho_item_id')
        item_name = item.get('name_en', 'Unknown')[:50]
        
        if not item_id:
            print(f"  {idx}. ⚠️  Skipped (no ID): {item_name}")
            continue
        
        try:
            # Get item details from Zoho API
            url = f"https://www.zohoapis.com/inventory/v1/items/{item_id}"
            params = {"organization_id": ORG_ID}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                item_details = data.get('item', {})
                
                # Check for image fields
                image_url = item_details.get('image_url') or item_details.get('image_document_path')
                image_name = item_details.get('image_name')
                image_id = item_details.get('image_id')
                
                if image_url:
                    # Update item with image data
                    item['image_url'] = image_url
                    if image_name:
                        item['image_name'] = image_name
                    if image_id:
                        item['image_id'] = image_id
                    
                    images_found += 1
                    print(f"  {idx}. ✅ Found image: {item_name}")
                    print(f"       URL: {image_url[:60]}...")
                    
                    # Stop after finding 20 images
                    if images_found >= 20:
                        print(f"\n🎯 Found 20 images! Stopping...")
                        break
                else:
                    print(f"  {idx}. ⚪ No image: {item_name}")
                
                updated_count += 1
                
            elif response.status_code == 401:
                print(f"\n❌ Authentication failed! Access token may be expired.")
                print("   Please refresh the token and try again.")
                break
            else:
                print(f"  {idx}. ❌ API Error {response.status_code}: {item_name}")
                errors += 1
            
            # Rate limiting - be nice to Zoho API
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  {idx}. ❌ Error: {str(e)}")
            errors += 1
    
    print()
    print("=" * 70)
    print(f"\n📊 RESULTS:")
    print(f"   Items Checked: {updated_count}")
    print(f"   Images Found: {images_found}")
    print(f"   Errors: {errors}")
    print()
    
    if images_found > 0:
        # Save updated data
        output_file = "all_zoho_inventory_items_updated.json"
        print(f"💾 Saving updated data to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        
        print("✅ File saved successfully!")
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Review the updated file")
        print("   2. Replace original file:")
        print(f"      cp {output_file} all_zoho_inventory_items.json")
        print("   3. Run sync to download images:")
        print('      curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/item/execute?sync_images=true"')
        print()
        
        # Show sample items with images
        print("📋 Sample items with images:")
        sample_count = 0
        for item in items:
            if item.get('image_url') and sample_count < 5:
                print(f"   • {item.get('name_en', 'N/A')[:50]}")
                print(f"     {item['image_url'][:70]}...")
                sample_count += 1
        
    else:
        print("⚠️  No images found in checked items.")
        print("   Possible reasons:")
        print("   - Items don't have images in Zoho")
        print("   - Access token expired (check for 401 errors above)")
        print("   - All items with images already synced")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    fetch_20_more_images()
