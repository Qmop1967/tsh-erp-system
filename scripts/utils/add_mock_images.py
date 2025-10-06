#!/usr/bin/env python3
"""
Add Mock Image URLs for Testing
This adds placeholder image URLs so we can test the image sync functionality
"""

import json
from pathlib import Path

print("🖼️  Adding Mock Image URLs for Testing")
print("=" * 70)
print()

# Load existing items
items_file = Path("all_zoho_inventory_items.json")
with open(items_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"📦 Loaded {len(items)} items")
print()

# Add mock image URLs (placeholder images from public CDN)
# Using placeholder.com which provides free test images
print("🎨 Adding mock image URLs for testing...")

for idx, item in enumerate(items):
    item_id = item.get('zoho_item_id', f'item_{idx}')
    # Use a placeholder image service - these are real URLs that work
    item['image_url'] = f"https://via.placeholder.com/400x400/4F46E5/FFFFFF?text=Item+{item.get('code', idx)}"
    item['image_name'] = f"item_{item_id}.jpg"
    item['image_source'] = "placeholder_for_testing"

print(f"✅ Added image URLs to all {len(items)} items")
print()

# Save updated file
output_file = "all_zoho_inventory_items_with_mock_images.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

print(f"💾 Saved to: {output_file}")
print()

# Show sample
print("📋 Sample Item with Image URL:")
print("-" * 70)
sample = items[0]
print(json.dumps({
    "zoho_item_id": sample.get("zoho_item_id"),
    "code": sample.get("code"),
    "name_en": sample.get("name_en"),
    "image_url": sample.get("image_url"),
    "image_name": sample.get("image_name")
}, indent=2))
print()

print("=" * 70)
print("🚀 NEXT STEPS:")
print()
print("1. ✅ Mock image URLs have been added")
print("2. 📋 Replace the main file:")
print(f"   cp {output_file} all_zoho_inventory_items.json")
print()
print("3. 🔄 Re-run the sync to test image downloads:")
print('   curl -X POST "http://localhost:8000/api/settings/integrations/zoho/sync/item/execute?sync_images=true"')
print()
print("4. ✅ Check downloaded images:")
print("   ls -lh /Users/khaleelal-mulla/TSH_ERP_System_Local/app/data/images/item/")
print()
print("5. 🔄 Later, replace mock URLs with real Zoho image URLs")
print()
print("=" * 70)
print()
print("💡 NOTE: These are placeholder images for TESTING the sync system.")
print("   Once you verify the sync works, replace with real Zoho image URLs.")
