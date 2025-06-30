#!/usr/bin/env python3
"""
Direct API test with current token
اختبار مباشر للAPI بالرمز الحالي
"""

import asyncio
import aiohttp
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService

async def direct_api_test():
    """Direct API test with current token"""
    print("🔄 Direct API Test...")
    
    # Load current credentials
    config_service = SecureConfigService()
    creds = config_service.get_zoho_credentials()
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {creds.access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"🔄 Testing with:")
    print(f"   Books API: {creds.books_api_base}")
    print(f"   Inventory API: {creds.inventory_api_base}")
    print(f"   Token: {creds.access_token[:30]}...")
    
    async with aiohttp.ClientSession() as session:
        # Test Books API - Organization
        print(f"\n🔄 Testing Books API...")
        books_url = f"{creds.books_api_base}/organizations/{creds.organization_id}"
        print(f"   URL: {books_url}")
        
        try:
            async with session.get(books_url, headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    org_name = data.get('organization', {}).get('name', 'Unknown')
                    print(f"   ✅ Success! Organization: {org_name}")
                else:
                    error_data = await response.text()
                    print(f"   ❌ Error: {error_data}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        # Test Inventory API - Organization  
        print(f"\n🔄 Testing Inventory API...")
        inventory_url = f"{creds.inventory_api_base}/organizations/{creds.organization_id}"
        print(f"   URL: {inventory_url}")
        
        try:
            async with session.get(inventory_url, headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    org_name = data.get('organization', {}).get('name', 'Unknown')
                    print(f"   ✅ Success! Organization: {org_name}")
                else:
                    error_data = await response.text()
                    print(f"   ❌ Error: {error_data}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        # Test Items API
        print(f"\n🔄 Testing Items API...")
        items_url = f"{creds.inventory_api_base}/items"
        params = {'organization_id': creds.organization_id, 'per_page': 5}
        print(f"   URL: {items_url}")
        print(f"   Params: {params}")
        
        try:
            async with session.get(items_url, headers=headers, params=params) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    print(f"   ✅ Success! Found {len(items)} items")
                    if items:
                        print(f"   Sample: {items[0].get('name', 'N/A')}")
                else:
                    error_data = await response.text()
                    print(f"   ❌ Error: {error_data}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🧪 Direct API Test")
    print("=" * 50)
    
    asyncio.run(direct_api_test())
    
    print("=" * 50)
    print("✅ Test completed!")
