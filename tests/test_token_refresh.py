#!/usr/bin/env python3
"""
Test script for Zoho token refresh
اختبار تحديث رمز Zoho
"""

import asyncio
import sys
import os
import aiohttp
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService, ZohoCredentials
import pytest

@pytest.mark.asyncio
async def test_token_refresh():
    """Test token refresh functionality"""
    print("🔄 Testing Zoho Token Refresh...")
    
    # Load current credentials
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No credentials found!")
        return
    
    print(f"✅ Current credentials loaded")
    print(f"   Organization ID: {credentials.organization_id}")
    print(f"   Access Token (first 20 chars): {credentials.access_token[:20]}...")
    print(f"   Refresh Token (first 20 chars): {credentials.refresh_token[:20]}...")
    
    # Try to refresh the token
    print("\n🔄 Attempting token refresh...")
    
    refresh_data = {
        'refresh_token': credentials.refresh_token,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'grant_type': 'refresh_token'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://accounts.zoho.com/oauth/v2/token",
                data=refresh_data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    new_access_token = token_data.get('access_token')
                    
                    print("✅ Token refresh successful!")
                    print(f"   New Access Token (first 20 chars): {new_access_token[:20]}...")
                    
                    # Update and save credentials
                    updated_credentials = ZohoCredentials(
                        organization_id=credentials.organization_id,
                        access_token=new_access_token,
                        refresh_token=credentials.refresh_token,
                        client_id=credentials.client_id,
                        client_secret=credentials.client_secret,
                        books_api_base=credentials.books_api_base,
                        inventory_api_base=credentials.inventory_api_base
                    )
                    
                    config_service.save_zoho_credentials(updated_credentials)
                    print("✅ Updated credentials saved!")
                    
                    # Test the new token
                    print("\n🔄 Testing new token...")
                    await test_api_with_token(new_access_token, credentials.organization_id)
                    
                else:
                    response_text = await response.text()
                    print(f"❌ Token refresh failed: {response.status}")
                    print(f"   Response: {response_text}")
                    
    except Exception as e:
        print(f"❌ Token refresh error: {str(e)}")

@pytest.mark.asyncio
async def test_api_with_token(access_token: str, org_id: str):
    """Test API calls with the new token"""
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test Books API
    print("🔄 Testing Books API...")
    try:
        async with aiohttp.ClientSession() as session:
            # Test organization endpoint
            async with session.get(
                f"https://www.zohoapis.com/books/v3/organizations/{org_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    print("✅ Books API: Organization endpoint working!")
                    data = await response.json()
                    org_name = data.get('organization', {}).get('name', 'Unknown')
                    print(f"   Organization: {org_name}")
                else:
                    print(f"❌ Books API failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
    except Exception as e:
        print(f"❌ Books API error: {str(e)}")
    
    # Test Inventory API
    print("\n🔄 Testing Inventory API...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://www.zohoapis.com/inventory/v1/organizations/{org_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    print("✅ Inventory API: Organization endpoint working!")
                    data = await response.json()
                    org_name = data.get('organization', {}).get('name', 'Unknown')
                    print(f"   Organization: {org_name}")
                else:
                    print(f"❌ Inventory API failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
    except Exception as e:
        print(f"❌ Inventory API error: {str(e)}")

if __name__ == "__main__":
    print("🔄 Zoho Token Refresh Test")
    print("=" * 50)
    
    asyncio.run(test_token_refresh())
    
    print("=" * 50)
    print("✅ Test completed!")
