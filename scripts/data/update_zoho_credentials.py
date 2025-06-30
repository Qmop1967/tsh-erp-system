#!/usr/bin/env python3
"""
Update Zoho credentials with correct API base URLs
تحديث بيانات اعتماد Zoho بعناوين API الصحيحة
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService, ZohoCredentials

def update_credentials():
    """Update stored credentials with correct API URLs"""
    print("🔄 Updating Zoho credentials with correct API URLs...")
    
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No credentials found!")
        return
    
    print("✅ Current credentials loaded")
    print(f"   Books API Base: {credentials.books_api_base}")
    print(f"   Inventory API Base: {credentials.inventory_api_base}")
    
    # Update with correct URLs
    updated_credentials = ZohoCredentials(
        organization_id=credentials.organization_id,
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        books_api_base="https://books.zohoapis.com/api/v3",
        inventory_api_base="https://inventory.zohoapis.com/api/v1"
    )
    
    # Save updated credentials
    success = config_service.save_zoho_credentials(updated_credentials)
    
    if success:
        print("✅ Credentials updated successfully!")
        print(f"   New Books API Base: {updated_credentials.books_api_base}")
        print(f"   New Inventory API Base: {updated_credentials.inventory_api_base}")
    else:
        print("❌ Failed to update credentials!")

if __name__ == "__main__":
    print("🔧 Zoho Credentials Update")
    print("=" * 50)
    
    update_credentials()
    
    print("=" * 50)
    print("✅ Update completed!")
