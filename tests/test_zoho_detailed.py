#!/usr/bin/env python3
"""
Detailed Zoho API test
اختبار تفصيلي لـ Zoho API
"""

import asyncio
import sys
import os
import aiohttp
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService

async def detailed_api_test():
    """Detailed API testing with full error responses"""
    print("🔄 Detailed Zoho API Test...")
    
    # Load credentials
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No credentials found!")
        return
    
    print(f"✅ Testing with Organization ID: {credentials.organization_id}")
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {credentials.access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test different endpoints
    test_endpoints = [
        {
            'name': 'Books Organizations',
            'url': f"{credentials.books_api_base}/organizations"
        },
        {
            'name': 'Books Organization Info',
            'url': f"{credentials.books_api_base}/organizations/{credentials.organization_id}"
        },
        {
            'name': 'Books Items',
            'url': f"{credentials.books_api_base}/items",
            'params': {'organization_id': credentials.organization_id}
        },
        {
            'name': 'Inventory Organizations', 
            'url': f"{credentials.inventory_api_base}/organizations"
        },
        {
            'name': 'Inventory Organization Info',
            'url': f"{credentials.inventory_api_base}/organizations/{credentials.organization_id}"
        },
        {
            'name': 'Inventory Items',
            'url': f"{credentials.inventory_api_base}/items",
            'params': {'organization_id': credentials.organization_id}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in test_endpoints:
            print(f"\n🔄 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            try:
                params = endpoint.get('params', {})
                if params:
                    print(f"   Params: {params}")
                
                async with session.get(
                    endpoint['url'],
                    headers=headers,
                    params=params
                ) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success!")
                        
                        # Show sample of response structure
                        if isinstance(data, dict):
                            print(f"   Response keys: {list(data.keys())}")
                            if 'organization' in data:
                                org = data['organization']
                                print(f"   Organization: {org.get('name', 'N/A')}")
                            elif 'organizations' in data:
                                orgs = data['organizations']
                                print(f"   Found {len(orgs)} organizations")
                                if orgs:
                                    print(f"   First org: {orgs[0].get('name', 'N/A')}")
                            elif 'items' in data:
                                items = data['items']
                                print(f"   Found {len(items)} items")
                                if items:
                                    print(f"   First item: {items[0].get('name', 'N/A')}")
                        
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error: {response.status}")
                        print(f"   Response: {error_text}")
                        
                        # Try to parse JSON error
                        try:
                            error_json = json.loads(error_text)
                            if 'message' in error_json:
                                print(f"   Error Message: {error_json['message']}")
                        except:
                            pass
                            
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 Detailed Zoho API Test")
    print("=" * 50)
    
    asyncio.run(detailed_api_test())
    
    print("=" * 50)
    print("✅ Test completed!")
