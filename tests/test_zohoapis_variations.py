#!/usr/bin/env python3
"""
Test zohoapis domain variations
اختبار تنويعات نطاق zohoapis
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
async def test_zohoapis_variations():
    """Test zohoapis domain variations"""
    print("🔄 Testing Zoho APIs Domain Variations...")
    
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
    
    # Try different variations of zohoapis domains
    zohoapis_variations = [
        # Standard format
        'https://www.zohoapis.com/books/v3',
        'https://www.zohoapis.com/inventory/v1', 
        # Regional variations
        'https://www.zohoapis.eu/books/v3',
        'https://www.zohoapis.eu/inventory/v1',
        'https://www.zohoapis.in/books/v3',
        'https://www.zohoapis.in/inventory/v1',
        'https://www.zohoapis.com.au/books/v3',
        'https://www.zohoapis.com.au/inventory/v1',
        # Without www
        'https://zohoapis.com/books/v3',
        'https://zohoapis.com/inventory/v1',
        # US specific
        'https://books.zohoapis.us/api/v3',
        'https://inventory.zohoapis.us/api/v1',
    ]
    
    for api_base in zohoapis_variations:
        print(f"\n🔄 Testing: {api_base}")
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                # Test organization endpoint
                test_url = f"{api_base}/organizations/{credentials.organization_id}"
                if 'inventory' in api_base:
                    test_url = f"{api_base}/organizations/{credentials.organization_id}"
                elif 'books' in api_base:
                    test_url = f"{api_base}/organizations/{credentials.organization_id}"
                
                print(f"   Testing URL: {test_url}")
                
                async with session.get(test_url, headers=headers) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        org_name = data.get('organization', {}).get('name', 'Unknown')
                        print(f"   ✅ SUCCESS! Organization: {org_name}")
                        print(f"   🎉 WORKING API BASE: {api_base}")
                        return api_base
                        
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error: {error_text[:100]}...")
                        
        except Exception as e:
            print(f"   ❌ Connection error: {str(e)}")
    
    print("\n❌ No working zohoapis domains found!")
    
    # Try one more approach - test the original domain with correct params
    print("\n🔄 Testing original domain with organization_id as parameter...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test Books with org_id as parameter
            books_url = "https://books.zoho.com/api/v3/items"
            params = {'organization_id': credentials.organization_id}
            
            async with session.get(books_url, headers=headers, params=params) as response:
                print(f"Books Status: {response.status}")
                error_text = await response.text()
                print(f"Books Response: {error_text[:200]}...")
                
                if response.status == 200:
                    print("✅ Books API working with original domain!")
                
    except Exception as e:
        print(f"❌ Original domain test failed: {str(e)}")

if __name__ == "__main__":
    print("🔧 Zoho APIs Domain Variations Test")
    print("=" * 50)
    
    asyncio.run(test_zohoapis_variations())
    
    print("=" * 50)
    print("✅ Test completed!")
