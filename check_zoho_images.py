#!/usr/bin/env python3
"""Check Zoho image fields"""
import asyncio
import json
from app.tds.integrations.zoho.client import UnifiedZohoClient, ZohoAPI
from app.tds.integrations.zoho.auth import ZohoAuthManager

async def check_images():
    auth = ZohoAuthManager()
    await auth.ensure_valid_token()

    client = UnifiedZohoClient(auth_manager=auth)
    await client.start()

    # Fetch first page of items
    items = await client.paginated_fetch(
        api_type=ZohoAPI.INVENTORY,
        endpoint='items',
        page_size=50
    )

    # Find items with images
    items_with_images = [
        item for item in items
        if item.get('image_name') or item.get('image_document_id')
    ]

    print(f"\nFound {len(items_with_images)} items with images out of {len(items)} total items")

    if items_with_images:
        sample = items_with_images[0]
        print('\n' + '='*80)
        print('Sample item with image:')
        print('='*80)
        print(f"item_id: {sample.get('item_id')}")
        print(f"name: {sample.get('name')}")
        print(f"image_name: {sample.get('image_name')}")
        print(f"image_document_id: {sample.get('image_document_id')}")
        print(f"image_url: {sample.get('image_url')}")
        print(f"image_type: {sample.get('image_type')}")

        # Print all image-related fields
        print('\nAll image-related fields:')
        for key in sample.keys():
            if 'image' in key.lower():
                print(f"  {key}: {sample[key]}")

    await client.stop()
    await auth.stop()

if __name__ == '__main__':
    asyncio.run(check_images())
