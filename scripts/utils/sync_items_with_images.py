#!/usr/bin/env python3
"""
Pull Zoho Items WITH Images
Attempts to sync images by fetching items with image data from Zoho API
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService

async def main():
    print("🖼️  Zoho Items + Images Sync")
    print("=" * 70)
    print()
    
    # Load config
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No Zoho credentials found!")
        print("   Please configure Zoho credentials first.")
        return
    
    print("✅ Credentials loaded")
    print(f"   Organization: {credentials.organization_id}")
    print()
    
    # Try to get fresh access token
    print("🔐 Attempting to refresh access token...")
    import requests
    
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    token_params = {
        "refresh_token": credentials.refresh_token,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "grant_type": "refresh_token"
    }
    
    try:
        token_response = requests.post(token_url, params=token_params, timeout=10)
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            if access_token:
                print("✅ Got fresh access token!")
                print(f"   Token: {access_token[:20]}...")
            else:
                print("⚠️  Token refresh succeeded but no access_token in response")
                print(f"   Using stored token instead")
                access_token = credentials.access_token
        else:
            print(f"⚠️  Token refresh failed: {token_response.status_code}")
            print(f"   Response: {token_response.text[:200]}")
            print(f"   Using stored access token...")
            access_token = credentials.access_token
    except Exception as e:
        print(f"⚠️  Token refresh error: {e}")
        print(f"   Using stored access token...")
        access_token = credentials.access_token
    
    print()
    print("📦 Fetching items from Zoho Inventory API...")
    print("-" * 70)
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    all_items = []
    items_with_images = 0
    page = 1
    max_pages = 3  # Start with first 3 pages for testing
    
    while page <= max_pages:
        url = f"{credentials.inventory_api_base}/items"
        params = {
            "organization_id": credentials.organization_id,
            "page": page,
            "per_page": 200
        }
        
        try:
            print(f"  📄 Fetching page {page}...", end=" ", flush=True)
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    print("(no more items)")
                    break
                
                print(f"✅ Got {len(items)} items")
                
                # Check each item for images
                for item in items:
                    # Look for image-related fields
                    has_image = False
                    image_fields = {}
                    
                    for key in item.keys():
                        if 'image' in key.lower():
                            image_fields[key] = item[key]
                            if item[key]:  # Has value
                                has_image = True
                    
                    if has_image:
                        items_with_images += 1
                    
                    # Transform to our format
                    item_data = {
                        "zoho_item_id": item.get('item_id'),
                        "code": item.get('sku'),
                        "name_en": item.get('name'),
                        "name_ar": item.get('name'),  # May need translation
                        "description_en": item.get('description', ''),
                        "description_ar": item.get('description', ''),
                        "brand": item.get('brand', ''),
                        "model": item.get('product_type', ''),
                        "unit_of_measure": item.get('unit'),
                        "cost_price_usd": str(item.get('purchase_rate', 0)),
                        "selling_price_usd": str(item.get('rate', 0)),
                        "track_inventory": item.get('track_inventory', True),
                        "reorder_level": str(item.get('reorder_level', 0)),
                        "weight": item.get('weight'),
                        "dimensions": item.get('dimensions'),
                        "is_active": item.get('status') == 'active',
                        "specifications": {
                            "category": item.get('category_name', ''),
                            "tax_id": item.get('tax_id', ''),
                            "hsn_or_sac": item.get('hsn_or_sac'),
                            "item_type": item.get('item_type', 'inventory'),
                            "source": "zoho_api_direct"
                        }
                    }
                    
                    # Add ALL image-related fields we find
                    for img_key, img_value in image_fields.items():
                        item_data[img_key] = img_value
                    
                    all_items.append(item_data)
                
                page += 1
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            elif response.status_code == 401:
                print("❌ Authentication failed!")
                print("   Your access token may have expired.")
                print("   Please get a fresh token from Zoho API Console:")
                print("   https://api-console.zoho.com/")
                break
            else:
                print(f"❌ Error {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print()
    print("=" * 70)
    print(f"📊 RESULTS:")
    print(f"   Total Items Fetched: {len(all_items)}")
    print(f"   Items with Images: {items_with_images}")
    print(f"   Pages Fetched: {page - 1}")
    print()
    
    if all_items:
        # Save to file
        output_file = "all_zoho_inventory_items_with_images.json"
        print(f"💾 Saving to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_items, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(all_items)} items")
        print()
        
        # Show sample item with image fields
        print("🔍 Sample Item Structure:")
        print("-" * 70)
        if all_items:
            sample = all_items[0]
            image_related = {k: v for k, v in sample.items() if 'image' in k.lower() or k in ['name_en', 'code', 'zoho_item_id']}
            print(json.dumps(image_related, indent=2))
        print()
        
        if items_with_images > 0:
            print("🎉 SUCCESS! Found items with images!")
            print()
            print("🚀 NEXT STEPS:")
            print("   1. Review the output file")
            print("   2. If satisfied, replace the main file:")
            print(f"      cp {output_file} all_zoho_inventory_items.json")
            print("   3. Re-run the sync:")
            print('      curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/item/execute?sync_images=true"')
            print()
        else:
            print("⚠️  No images found in fetched items.")
            print()
            print("💡 This could mean:")
            print("   1. Items don't have images in Zoho")
            print("   2. Images are in a different field/endpoint")
            print("   3. Need to fetch individual item details for images")
            print()
            print("📋 Recommendation:")
            print("   Check a few items in Zoho Inventory web interface")
            print("   to see if they actually have images.")
    else:
        print("❌ No items fetched. Check authentication and try again.")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
