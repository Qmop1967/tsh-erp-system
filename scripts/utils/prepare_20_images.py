#!/usr/bin/env python3
"""
Prepare data with only 20 images for testing
"""

import json
from pathlib import Path

def prepare_20_images():
    """Create a subset with 20 images for testing"""
    
    print("🔧 Preparing 20 images for sync test...")
    print("=" * 70)
    
    # Load all items
    with open('all_zoho_inventory_items.json', 'r', encoding='utf-8') as f:
        all_items = json.load(f)
    
    print(f"📦 Total items: {len(all_items)}")
    
    # Find items with images
    items_with_images = [item for item in all_items if item.get('image_url')]
    print(f"📷 Items with images: {len(items_with_images)}")
    
    # Get first 20 with images
    items_to_sync = items_with_images[:20]
    
    # Get items without images
    items_without_images = [item for item in all_items if not item.get('image_url')]
    
    # Combine: 20 with images + rest without images
    test_data = items_to_sync + items_without_images[:100]  # Add 100 more without images
    
    print(f"\n✅ Prepared {len(test_data)} items for sync:")
    print(f"   - {len(items_to_sync)} items WITH images")
    print(f"   - {len(test_data) - len(items_to_sync)} items WITHOUT images")
    print()
    
    # Show the 20 items
    print("📋 Items that will have images downloaded:")
    for i, item in enumerate(items_to_sync, 1):
        name = item.get('name_en', 'N/A')[:50]
        print(f"   {i}. {name}")
    
    # Save to temporary file
    temp_file = 'all_zoho_inventory_items_test.json'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"💾 Saved to: {temp_file}")
    print()
    print("🎯 NEXT STEP: Replace the main file temporarily")
    print(f"   mv all_zoho_inventory_items.json all_zoho_inventory_items_backup.json")
    print(f"   cp {temp_file} all_zoho_inventory_items.json")
    print()
    print("=" * 70)

if __name__ == "__main__":
    prepare_20_images()
