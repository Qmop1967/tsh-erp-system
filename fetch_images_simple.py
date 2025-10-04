#!/usr/bin/env python3
"""
Fetch Item Images from Zoho Inventory API - Simple Version
Uses existing Zoho service with proper authentication
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.zoho_service import ZohoAsyncService
from app.services.config_service import SecureConfigService

async def fetch_item_details_with_images():
    """Fetch detailed item information including images from Zoho"""
    
    print("🖼️  Zoho Image Fetcher (Using TSH Zoho Service)")
    print("=" * 70)
    print()
    
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
    
    # Initialize Zoho service
    print("🔐 Initializing Zoho service...")
    try:
        async with ZohoAsyncService() as zoho_service:
            print("✅ Zoho service initialized")
            print()
            
            # Test with first 10 items to see if they have images
            print("🔍 Testing first 10 items for image data...")
            print("-" * 70)
            
            images_found = 0
            updated_items = []
            
            for idx, item in enumerate(items[:10], 1):
                item_id = item.get('zoho_item_id')
                item_name = item.get('name_en', 'Unknown')
                
                if not item_id:
                    print(f"  {idx}. ⚠️  No ID: {item_name}")
                    updated_items.append(item)
                    continue
                
                try:
                    # Make direct API call to get item details
                    url = f"{zoho_service.config.inventory_api_base}/items/{item_id}"
                    params = {"organization_id": zoho_service.config.organization_id}
                    
                    async with zoho_service.session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            item_details = data.get('item', {})
                            
                            # Check all possible image fields
                            image_fields = {}
                            for key in item_details.keys():
                                if 'image' in key.lower():
                                    image_fields[key] = item_details[key]
                            
                            if image_fields:
                                print(f"  {idx}. ✅ {item_name[:40]}")
                                print(f"       Image fields: {list(image_fields.keys())}")
                                # Add image fields to item
                                for key, value in image_fields.items():
                                    item[key] = value
                                images_found += 1
                            else:
                                print(f"  {idx}. ⚪ {item_name[:40]} (no image)")
                            
                            updated_items.append(item)
                        else:
                            print(f"  {idx}. ❌ API error {response.status}: {item_name[:40]}")
                            updated_items.append(item)
                    
                    # Rate limiting
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    print(f"  {idx}. ❌ Error: {str(e)}")
                    updated_items.append(item)
            
            print()
            print("=" * 70)
            print(f"\n📊 TEST RESULTS (First 10 items):")
            print(f"   Images Found: {images_found}/10")
            print()
            
            if images_found > 0:
                print("✅ Some items have images!")
                print("\n💡 Would you like to fetch all 2,204 items? (y/n)")
                # For now, just show results
                print("\n📋 To fetch all items, uncomment the full processing code in the script.")
            else:
                print("⚠️  No images found in the first 10 items.")
                print("   Possible reasons:")
                print("   1. Items don't have images uploaded in Zoho")
                print("   2. Images might be in a different field")
                print("   3. API might not include image data")
                print()
                print("📋 Sample item structure:")
                if updated_items:
                    sample = updated_items[0]
                    print(json.dumps({k: str(v)[:50] if v else None for k, v in list(sample.items())[:10]}, indent=2))
            
    except Exception as e:
        print(f"❌ Error initializing Zoho service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fetch_item_details_with_images())
