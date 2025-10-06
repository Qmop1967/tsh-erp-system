#!/usr/bin/env python3
"""
Pull items from Zoho Inventory and Books APIs
استخراج الأصناف من Zoho Inventory و Books APIs
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.config_service import SecureConfigService
from app.services.zoho_service import ZohoAsyncService
from app.schemas.migration import ZohoConfigCreate

async def pull_items_from_zoho():
    """Pull all items from Zoho APIs"""
    print("🔄 Starting Zoho Items Extraction...")
    print("=" * 60)
    
    # Load credentials
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No Zoho credentials found!")
        return
    
    print("✅ Zoho credentials loaded")
    print(f"   Organization ID: {credentials.organization_id}")
    print(f"   Books API: {credentials.books_api_base}")
    print(f"   Inventory API: {credentials.inventory_api_base}")
    print()
    
    # Create config for async service
    config = ZohoConfigCreate(
        organization_id=credentials.organization_id,
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        books_api_base=credentials.books_api_base,
        inventory_api_base=credentials.inventory_api_base
    )
    
    # Initialize async service
    async with ZohoAsyncService(config) as service:
        print("🔍 Testing connection to Zoho APIs...")
        
        # Test connection first
        try:
            connection_results = await service.test_connection()
            print("📋 Connection Test Results:")
            print(f"   Books API: {'✅ Connected' if connection_results.get('books_api') else '❌ Failed'}")
            print(f"   Inventory API: {'✅ Connected' if connection_results.get('inventory_api') else '❌ Failed'}")
            
            if connection_results.get('books_organization'):
                print(f"   Organization: {connection_results['books_organization']}")
            print()
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return
        
        # Extract items from Zoho Inventory
        print("📦 Extracting Items from Zoho Inventory...")
        try:
            inventory_items, has_more = await service.extract_items(page=1, per_page=100)
            print(f"✅ Retrieved {len(inventory_items)} items from Zoho Inventory")
            
            # Save to file
            with open('zoho_inventory_items.json', 'w', encoding='utf-8') as f:
                json.dump(inventory_items, f, ensure_ascii=False, indent=2, default=str)
            
            # Display sample items
            if inventory_items:
                print("\n📋 Sample Items from Inventory:")
                for i, item in enumerate(inventory_items[:3]):
                    print(f"   {i+1}. {item.get('name', 'N/A')} (SKU: {item.get('sku', 'N/A')})")
                    print(f"      Rate: {item.get('rate', 'N/A')} {item.get('currency_code', '')}")
                    print(f"      Stock: {item.get('stock_on_hand', 'N/A')}")
                    print()
            
            if has_more:
                print("ℹ️  More items available. Use pagination to get all items.")
            
        except Exception as e:
            print(f"❌ Failed to extract inventory items: {e}")
        
        # Extract items from Zoho Books (if different)
        print("\n📚 Extracting Items from Zoho Books...")
        try:
            books_items, has_more = await service.extract_books_items(page=1, per_page=100)
            print(f"✅ Retrieved {len(books_items)} items from Zoho Books")
            
            # Save to file
            with open('zoho_books_items.json', 'w', encoding='utf-8') as f:
                json.dump(books_items, f, ensure_ascii=False, indent=2, default=str)
            
            # Display sample items
            if books_items:
                print("\n📋 Sample Items from Books:")
                for i, item in enumerate(books_items[:3]):
                    print(f"   {i+1}. {item.get('name', 'N/A')} (Item ID: {item.get('item_id', 'N/A')})")
                    print(f"      Selling Price: {item.get('rate', 'N/A')}")
                    print(f"      Tax: {item.get('tax_name', 'N/A')}")
                    print()
            
        except Exception as e:
            print(f"❌ Failed to extract books items: {e}")
        
        # Extract categories
        print("\n📂 Extracting Categories...")
        try:
            categories, has_more = await service.extract_categories(page=1, per_page=100)
            print(f"✅ Retrieved {len(categories)} categories")
            
            # Save to file
            with open('zoho_categories.json', 'w', encoding='utf-8') as f:
                json.dump(categories, f, ensure_ascii=False, indent=2, default=str)
            
            if categories:
                print("\n📂 Available Categories:")
                for category in categories[:5]:
                    print(f"   • {category.get('category_name', 'N/A')} (ID: {category.get('category_id', 'N/A')})")
            
        except Exception as e:
            print(f"❌ Failed to extract categories: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        
        # Check files
        files_created = []
        for filename in ['zoho_inventory_items.json', 'zoho_books_items.json', 'zoho_categories.json']:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                files_created.append(f"{filename} ({size:,} bytes)")
        
        if files_created:
            print("✅ Files created:")
            for file_info in files_created:
                print(f"   📁 {file_info}")
        
        print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🚀 Zoho Items Extraction Tool")
    print("أداة استخراج الأصناف من Zoho")
    print("=" * 60)
    
    asyncio.run(pull_items_from_zoho())
    
    print("\n" + "=" * 60)
    print("✅ Extraction completed!")
