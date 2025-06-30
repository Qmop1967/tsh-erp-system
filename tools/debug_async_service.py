#!/usr/bin/env python3
"""
Debug the async Zoho service
تحليل خدمة Zoho غير المتزامنة
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.zoho_service import ZohoAsyncService
from app.schemas.migration import ZohoConfigCreate
from app.services.config_service import SecureConfigService

async def debug_async_service():
    """Debug the async service"""
    print("🔍 Debugging Async Zoho Service...")
    
    # Load credentials
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    print(f"✅ Loaded credentials:")
    print(f"   Books API: {credentials.books_api_base}")
    print(f"   Inventory API: {credentials.inventory_api_base}")
    print(f"   Token: {credentials.access_token[:30]}...")
    
    # Create config
    config = ZohoConfigCreate(
        organization_id=credentials.organization_id,
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        books_api_base=credentials.books_api_base,
        inventory_api_base=credentials.inventory_api_base
    )
    
    print(f"\n✅ Created config:")
    print(f"   Books API: {config.books_api_base}")
    print(f"   Inventory API: {config.inventory_api_base}")
    
    # Test the async service step by step
    async with ZohoAsyncService(config) as service:
        print(f"\n✅ Service config:")
        print(f"   Books API: {service.config.books_api_base}")
        print(f"   Inventory API: {service.config.inventory_api_base}")
        
        # Test books URL construction
        books_url = f"{service.config.books_api_base}/organizations/{service.config.organization_id}"
        print(f"\n🔄 Testing Books URL: {books_url}")
        
        try:
            books_response = await service._make_request(books_url)
            print("✅ Books API request successful!")
            print(f"   Organization: {books_response.get('organization', {}).get('name', 'Unknown')}")
        except Exception as e:
            print(f"❌ Books API failed: {str(e)}")
        
        # Test inventory URL construction
        inventory_url = f"{service.config.inventory_api_base}/organizations/{service.config.organization_id}"
        print(f"\n🔄 Testing Inventory URL: {inventory_url}")
        
        try:
            inventory_response = await service._make_request(inventory_url)
            print("✅ Inventory API request successful!")
            print(f"   Organization: {inventory_response.get('organization', {}).get('name', 'Unknown')}")
        except Exception as e:
            print(f"❌ Inventory API failed: {str(e)}")
        
        # Test items extraction URL
        items_url = f"{service.config.inventory_api_base}/items"
        print(f"\n🔄 Testing Items URL: {items_url}")
        print(f"   With params: organization_id={service.config.organization_id}")
        
        try:
            params = {
                'organization_id': service.config.organization_id,
                'page': 1,
                'per_page': 5
            }
            items_response = await service._make_request(items_url, params=params)
            items = items_response.get('items', [])
            print(f"✅ Items API request successful! Found {len(items)} items")
            if items:
                print(f"   Sample: {items[0].get('name', 'N/A')}")
        except Exception as e:
            print(f"❌ Items API failed: {str(e)}")

if __name__ == "__main__":
    print("🔍 Async Service Debug")
    print("=" * 50)
    
    asyncio.run(debug_async_service())
    
    print("=" * 50)
    print("✅ Debug completed!")
