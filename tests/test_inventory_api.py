#!/usr/bin/env python3
"""
Test inventory API with working domain pattern
اختبار inventory API بالنطاق الصحيح
"""

import asyncio
import aiohttp
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService
import pytest

@pytest.mark.asyncio
async def test_inventory_api():
    """Test inventory API with correct domain"""
    print("🔄 Testing Inventory API with working domain pattern...")
    
    # Load credentials
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No credentials found!")
        return
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {credentials.access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test inventory API variations
    inventory_bases = [
        'https://www.zohoapis.com/inventory/v1',
        'https://inventory.zohoapis.com/api/v1',
        'https://www.zohoapis.com/inventory/api/v1'
    ]
    
    for inventory_base in inventory_bases:
        print(f"\n🔄 Testing: {inventory_base}")
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                # Test organization endpoint
                test_url = f"{inventory_base}/organizations/{credentials.organization_id}"
                print(f"   Testing URL: {test_url}")
                
                async with session.get(test_url, headers=headers) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        org_name = data.get('organization', {}).get('name', 'Unknown')
                        print(f"   ✅ SUCCESS! Organization: {org_name}")
                        
                        # Test items endpoint
                        items_url = f"{inventory_base}/items"
                        params = {'organization_id': credentials.organization_id, 'per_page': 5}
                        
                        async with session.get(items_url, headers=headers, params=params) as items_response:
                            print(f"   Items Status: {items_response.status}")
                            
                            if items_response.status == 200:
                                items_data = await items_response.json()
                                items = items_data.get('items', [])
                                print(f"   ✅ Items API working! Found {len(items)} items")
                                
                                if items:
                                    print(f"   Sample item: {items[0].get('name', 'N/A')}")
                                
                                print(f"\n🎉 WORKING INVENTORY API: {inventory_base}")
                                return inventory_base
                            else:
                                items_error = await items_response.text()
                                print(f"   ❌ Items API failed: {items_error[:100]}...")
                        
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error: {error_text[:100]}...")
                        
        except Exception as e:
            print(f"   ❌ Connection error: {str(e)}")
    
    print("\n❌ No working inventory API found!")
    return None

if __name__ == "__main__":
    print("📦 Inventory API Test")
    print("=" * 50)
    
    working_inventory = asyncio.run(test_inventory_api())
    
    if working_inventory:
        print(f"\n✅ Working APIs found:")
        print(f"Books: https://www.zohoapis.com/books/v3")
        print(f"Inventory: {working_inventory}")
    
    print("=" * 50)
    print("✅ Test completed!")
