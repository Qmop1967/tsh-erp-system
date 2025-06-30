#!/usr/bin/env python3
"""
Test script for Zoho integration
اختبار تكامل Zoho
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.zoho_service import ZohoAsyncService
from app.schemas.migration import ZohoConfigCreate
from app.services.config_service import SecureConfigService

async def test_zoho_integration():
    """Test the Zoho integration"""
    print("🔄 Starting Zoho Integration Test...")
    
    # Load credentials from secure config
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No Zoho credentials found!")
        return
    
    print("✅ Loaded Zoho credentials")
    print(f"   Organization ID: {credentials.organization_id}")
    print(f"   Client ID: {credentials.client_id}")
    
    # Create config
    config = ZohoConfigCreate(
        organization_id=credentials.organization_id,
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret
    )
    
    print("\n🔄 Testing Zoho API Connection...")
    
    # Test connection
    async with ZohoAsyncService(config) as service:
        try:
            # Test basic connection
            test_results = await service.test_connection()
            print("📋 Connection Test Results:")
            for key, value in test_results.items():
                if key.endswith('_error'):
                    print(f"   ❌ {key}: {value}")
                else:
                    print(f"   ✅ {key}: {value}")
            
            # Try to extract a small sample of items
            print("\n🔄 Testing Items Extraction...")
            try:
                items, has_more = await service.extract_items(page=1, per_page=5)
                print(f"✅ Successfully extracted {len(items)} items (has_more: {has_more})")
                
                if items:
                    sample_item = items[0]
                    print(f"   Sample item: {sample_item.get('name_en', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Items extraction failed: {str(e)}")
            
            # Try to extract customers
            print("\n🔄 Testing Customers Extraction...")
            try:
                customers, has_more = await service.extract_customers(page=1, per_page=5)
                print(f"✅ Successfully extracted {len(customers)} customers (has_more: {has_more})")
                
                if customers:
                    sample_customer = customers[0]
                    print(f"   Sample customer: {sample_customer.get('name_en', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Customers extraction failed: {str(e)}")
                
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Zoho Integration Test Script")
    print("=" * 50)
    
    asyncio.run(test_zoho_integration())
    
    print("=" * 50)
    print("✅ Test completed!")
