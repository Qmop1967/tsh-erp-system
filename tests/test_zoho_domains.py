#!/usr/bin/env python3
"""
Test different Zoho API domains
اختبار نطاقات Zoho API المختلفة
"""

import asyncio
import aiohttp
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService

async def test_domains():
    """Test different Zoho API domains"""
    print("🔄 Testing Zoho API Domains...")
    
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
    
    # Different domain combinations to test
    domain_combinations = [
        # Original domains
        ('https://books.zoho.com/api/v3', 'https://inventory.zoho.com/api/v1'),
        # API domains  
        ('https://books.zohoapis.com/api/v3', 'https://inventory.zohoapis.com/api/v1'),
        # EU domains
        ('https://books.zoho.eu/api/v3', 'https://inventory.zoho.eu/api/v1'),
        # US domains
        ('https://books.zoho.com/api/v3', 'https://inventory.zoho.com/api/v1'),
        # IN domains
        ('https://books.zoho.in/api/v3', 'https://inventory.zoho.in/api/v1'),
        # AU domains
        ('https://books.zoho.com.au/api/v3', 'https://inventory.zoho.com.au/api/v1'),
    ]
    
    for books_base, inventory_base in domain_combinations:
        print(f"\n🔄 Testing domains:")
        print(f"   Books: {books_base}")
        print(f"   Inventory: {inventory_base}")
        
        # Test Books API
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                # Test simple organization endpoint
                async with session.get(
                    f"{books_base}/organizations/{credentials.organization_id}",
                    headers=headers
                ) as response:
                    print(f"   Books Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        org_name = data.get('organization', {}).get('name', 'Unknown')
                        print(f"   ✅ Books API Working! Organization: {org_name}")
                        
                        # Test Inventory API with this domain pattern
                        try:
                            async with session.get(
                                f"{inventory_base}/organizations/{credentials.organization_id}",
                                headers=headers
                            ) as inv_response:
                                print(f"   Inventory Status: {inv_response.status}")
                                
                                if inv_response.status == 200:
                                    inv_data = await inv_response.json()
                                    inv_org_name = inv_data.get('organization', {}).get('name', 'Unknown')
                                    print(f"   ✅ Inventory API Working! Organization: {inv_org_name}")
                                    
                                    print(f"\n🎉 WORKING DOMAINS FOUND:")
                                    print(f"   Books: {books_base}")
                                    print(f"   Inventory: {inventory_base}")
                                    return books_base, inventory_base
                                    
                                else:
                                    inv_error = await inv_response.text()
                                    print(f"   ❌ Inventory failed: {inv_error[:100]}...")
                        except Exception as e:
                            print(f"   ❌ Inventory error: {str(e)}")
                            
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Books failed: {error_text[:100]}...")
                        
        except Exception as e:
            print(f"   ❌ Connection error: {str(e)}")
    
    print("\n❌ No working domains found!")
    return None, None

if __name__ == "__main__":
    print("🌐 Zoho API Domain Test")
    print("=" * 50)
    
    working_books, working_inventory = asyncio.run(test_domains())
    
    if working_books and working_inventory:
        print(f"\n✅ Use these domains:")
        print(f"Books: {working_books}")
        print(f"Inventory: {working_inventory}")
    
    print("=" * 50)
    print("✅ Test completed!")
