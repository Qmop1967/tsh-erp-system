#!/usr/bin/env python3
"""
Complete Zoho Data Extraction - All Items with Pagination
استخراج كامل لبيانات Zoho - جميع الأصناف مع التصفح
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

async def pull_all_zoho_data():
    """Pull all data from Zoho APIs with pagination"""
    print("🔄 Complete Zoho Data Extraction...")
    print("=" * 60)
    
    # Load credentials
    config_service = SecureConfigService()
    credentials = config_service.get_zoho_credentials()
    
    if not credentials:
        print("❌ No Zoho credentials found!")
        return
    
    print("✅ Zoho credentials loaded")
    print(f"   Organization: Tech Spider Hand Company")
    print(f"   Organization ID: {credentials.organization_id}")
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
        print("🔍 Testing connection...")
        try:
            connection_results = await service.test_connection()
            if not (connection_results.get('books_api') or connection_results.get('inventory_api')):
                print("❌ Cannot connect to Zoho APIs!")
                return
            print("✅ Connection successful!")
            print()
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return
        
        # === INVENTORY ITEMS ===
        print("📦 Extracting ALL Inventory Items...")
        all_inventory_items = []
        page = 1
        
        while True:
            try:
                print(f"   📄 Loading page {page}...")
                items, has_more = await service.extract_items(page=page, per_page=200)
                
                if not items:
                    break
                
                all_inventory_items.extend(items)
                print(f"   ✅ Page {page}: {len(items)} items (Total: {len(all_inventory_items)})")
                
                if not has_more:
                    break
                    
                page += 1
                
                # Safety limit to avoid infinite loops
                if page > 50:
                    print("   ⚠️ Reached page limit (50). Stopping.")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        print(f"✅ Total inventory items extracted: {len(all_inventory_items)}")
        
        if all_inventory_items:
            with open('all_zoho_inventory_items.json', 'w', encoding='utf-8') as f:
                json.dump(all_inventory_items, f, ensure_ascii=False, indent=2, default=str)
            print(f"   📁 Saved to: all_zoho_inventory_items.json")
        
        # === CUSTOMERS ===
        print("\n👥 Extracting Customers...")
        all_customers = []
        page = 1
        
        while True:
            try:
                print(f"   📄 Loading page {page}...")
                customers, has_more = await service.extract_customers(page=page, per_page=200)
                
                if not customers:
                    break
                
                all_customers.extend(customers)
                print(f"   ✅ Page {page}: {len(customers)} customers (Total: {len(all_customers)})")
                
                if not has_more:
                    break
                    
                page += 1
                
                if page > 20:  # Customers usually fewer
                    print("   ⚠️ Reached page limit (20). Stopping.")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        print(f"✅ Total customers extracted: {len(all_customers)}")
        
        if all_customers:
            with open('all_zoho_customers.json', 'w', encoding='utf-8') as f:
                json.dump(all_customers, f, ensure_ascii=False, indent=2, default=str)
            print(f"   📁 Saved to: all_zoho_customers.json")
        
        # === VENDORS ===
        print("\n🏭 Extracting Vendors...")
        all_vendors = []
        page = 1
        
        while True:
            try:
                print(f"   📄 Loading page {page}...")
                vendors, has_more = await service.extract_vendors(page=page, per_page=200)
                
                if not vendors:
                    break
                
                all_vendors.extend(vendors)
                print(f"   ✅ Page {page}: {len(vendors)} vendors (Total: {len(all_vendors)})")
                
                if not has_more:
                    break
                    
                page += 1
                
                if page > 20:
                    print("   ⚠️ Reached page limit (20). Stopping.")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        print(f"✅ Total vendors extracted: {len(all_vendors)}")
        
        if all_vendors:
            with open('all_zoho_vendors.json', 'w', encoding='utf-8') as f:
                json.dump(all_vendors, f, ensure_ascii=False, indent=2, default=str)
            print(f"   📁 Saved to: all_zoho_vendors.json")
        
        # === SALES ORDERS ===
        print("\n📋 Extracting Sales Orders...")
        all_sales_orders = []
        page = 1
        
        while True:
            try:
                print(f"   📄 Loading page {page}...")
                orders, has_more = await service.extract_sales_orders(page=page, per_page=200)
                
                if not orders:
                    break
                
                all_sales_orders.extend(orders)
                print(f"   ✅ Page {page}: {len(orders)} orders (Total: {len(all_sales_orders)})")
                
                if not has_more:
                    break
                    
                page += 1
                
                if page > 30:
                    print("   ⚠️ Reached page limit (30). Stopping.")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        print(f"✅ Total sales orders extracted: {len(all_sales_orders)}")
        
        if all_sales_orders:
            with open('all_zoho_sales_orders.json', 'w', encoding='utf-8') as f:
                json.dump(all_sales_orders, f, ensure_ascii=False, indent=2, default=str)
            print(f"   📁 Saved to: all_zoho_sales_orders.json")
        
        # === SUMMARY ===
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        
        summary = {
            "extraction_date": datetime.now().isoformat(),
            "organization": "Tech Spider Hand Company For General Trading Ltd",
            "organization_id": credentials.organization_id,
            "totals": {
                "inventory_items": len(all_inventory_items),
                "customers": len(all_customers),
                "vendors": len(all_vendors),
                "sales_orders": len(all_sales_orders)
            }
        }
        
        # Save summary
        with open('zoho_extraction_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("✅ Data successfully extracted:")
        print(f"   📦 Items: {len(all_inventory_items):,}")
        print(f"   👥 Customers: {len(all_customers):,}")
        print(f"   🏭 Vendors: {len(all_vendors):,}")
        print(f"   📋 Sales Orders: {len(all_sales_orders):,}")
        
        print(f"\n📁 Files created:")
        files = [
            'all_zoho_inventory_items.json',
            'all_zoho_customers.json', 
            'all_zoho_vendors.json',
            'all_zoho_sales_orders.json',
            'zoho_extraction_summary.json'
        ]
        
        for filename in files:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"   📁 {filename} ({size:,} bytes)")
        
        print(f"\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🚀 Complete Zoho Data Extraction Tool")
    print("أداة الاستخراج الكامل لبيانات Zoho")
    print("=" * 60)
    
    asyncio.run(pull_all_zoho_data())
    
    print("\n" + "=" * 60)
    print("✅ Complete extraction finished!")
