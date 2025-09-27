#!/usr/bin/env python3
"""
Import Zoho data into TSH ERP System database
استيراد بيانات Zoho إلى قاعدة بيانات TSH ERP System
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db
from app.models import Product, Customer, Supplier, Category
from sqlalchemy.orm import Session

def import_inventory_items(db: Session):
    """Import inventory items into database"""
    print("📦 Importing Inventory Items...")
    
    try:
        with open('all_zoho_inventory_items.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        imported_count = 0
        updated_count = 0
        error_count = 0
        
        for item_data in items:
            try:
                # Check if item already exists
                existing_item = db.query(Product).filter(
                    Product.code == item_data.get('code')
                ).first()
                
                # Prepare item data
                product_data = {
                    'code': item_data.get('code', ''),
                    'name_en': item_data.get('name_en', ''),
                    'name_ar': item_data.get('name_ar', ''),
                    'description_en': item_data.get('description_en', ''),
                    'description_ar': item_data.get('description_ar', ''),
                    'brand': item_data.get('brand', ''),
                    'model': item_data.get('model', ''),
                    'unit_of_measure': item_data.get('unit_of_measure', 'pcs'),
                    'cost_price': Decimal(str(item_data.get('cost_price_usd', 0) or 0)),
                    'selling_price': Decimal(str(item_data.get('selling_price_usd', 0) or 0)),
                    'is_active': item_data.get('is_active', True),
                    'track_inventory': item_data.get('track_inventory', True),
                    'reorder_level': Decimal(str(item_data.get('reorder_level', 0) or 0)),
                    'zoho_item_id': item_data.get('zoho_item_id'),
                    'weight': Decimal(str(item_data.get('weight', 0) or 0)) if item_data.get('weight') else None
                }
                
                if existing_item:
                    # Update existing item
                    for key, value in product_data.items():
                        setattr(existing_item, key, value)
                    updated_count += 1
                else:
                    # Create new item
                    new_item = Product(**product_data)
                    db.add(new_item)
                    imported_count += 1
                
                # Commit every 100 items
                if (imported_count + updated_count) % 100 == 0:
                    db.commit()
                    print(f"   ✅ Processed {imported_count + updated_count} items...")
                
            except Exception as e:
                error_count += 1
                print(f"   ❌ Error processing item {item_data.get('code', 'Unknown')}: {e}")
                continue
        
        # Final commit
        db.commit()
        
        print(f"✅ Inventory Import Summary:")
        print(f"   📦 New items: {imported_count}")
        print(f"   🔄 Updated items: {updated_count}")
        print(f"   ❌ Errors: {error_count}")
        
    except Exception as e:
        print(f"❌ Error importing inventory: {e}")

def import_customers(db: Session):
    """Import customers into database"""
    print("\n👥 Importing Customers...")
    
    try:
        with open('all_zoho_customers.json', 'r', encoding='utf-8') as f:
            customers = json.load(f)
        
        imported_count = 0
        updated_count = 0
        error_count = 0
        
        for customer_data in customers:
            try:
                # Check if customer already exists
                existing_customer = db.query(Customer).filter(
                    Customer.code == customer_data.get('code')
                ).first()
                
                # Prepare customer data
                customer_info = {
                    'code': customer_data.get('code', ''),
                    'name_en': customer_data.get('name_en', ''),
                    'name_ar': customer_data.get('name_ar', ''),
                    'email': customer_data.get('email', ''),
                    'phone': customer_data.get('phone', ''),
                    'address_en': customer_data.get('address_en', ''),
                    'address_ar': customer_data.get('address_ar', ''),
                    'city': customer_data.get('city', ''),
                    'country': customer_data.get('country', 'Iraq'),
                    'is_active': customer_data.get('is_active', True),
                    'credit_limit': Decimal(str(customer_data.get('credit_limit', 0) or 0)),
                    'currency': customer_data.get('currency', 'USD'),
                    'zoho_customer_id': customer_data.get('zoho_customer_id'),
                    'tax_number': customer_data.get('tax_number', ''),
                    'payment_terms': customer_data.get('payment_terms', '')
                }
                
                if existing_customer:
                    # Update existing customer
                    for key, value in customer_info.items():
                        setattr(existing_customer, key, value)
                    updated_count += 1
                else:
                    # Create new customer
                    new_customer = Customer(**customer_info)
                    db.add(new_customer)
                    imported_count += 1
                
                # Commit every 100 customers
                if (imported_count + updated_count) % 100 == 0:
                    db.commit()
                    print(f"   ✅ Processed {imported_count + updated_count} customers...")
                
            except Exception as e:
                error_count += 1
                print(f"   ❌ Error processing customer {customer_data.get('code', 'Unknown')}: {e}")
                continue
        
        # Final commit
        db.commit()
        
        print(f"✅ Customer Import Summary:")
        print(f"   👥 New customers: {imported_count}")
        print(f"   🔄 Updated customers: {updated_count}")
        print(f"   ❌ Errors: {error_count}")
        
    except Exception as e:
        print(f"❌ Error importing customers: {e}")

def import_vendors(db: Session):
    """Import vendors into database"""
    print("\n🏭 Importing Vendors...")
    
    try:
        with open('all_zoho_vendors.json', 'r', encoding='utf-8') as f:
            vendors = json.load(f)
        
        imported_count = 0
        updated_count = 0
        error_count = 0
        
        for vendor_data in vendors:
            try:
                # Check if vendor already exists
                existing_vendor = db.query(Supplier).filter(
                    Supplier.code == vendor_data.get('code')
                ).first()
                
                # Prepare vendor data
                vendor_info = {
                    'code': vendor_data.get('code', ''),
                    'name_en': vendor_data.get('name_en', ''),
                    'name_ar': vendor_data.get('name_ar', ''),
                    'email': vendor_data.get('email', ''),
                    'phone': vendor_data.get('phone', ''),
                    'address_en': vendor_data.get('address_en', ''),
                    'address_ar': vendor_data.get('address_ar', ''),
                    'city': vendor_data.get('city', ''),
                    'country': vendor_data.get('country', ''),
                    'is_active': vendor_data.get('is_active', True),
                    'currency': vendor_data.get('currency', 'USD'),
                    'tax_number': vendor_data.get('tax_number', ''),
                    'payment_terms': vendor_data.get('payment_terms', ''),
                    'contact_person': vendor_data.get('contact_person', '')
                }
                
                if existing_vendor:
                    # Update existing vendor
                    for key, value in vendor_info.items():
                        if hasattr(existing_vendor, key):
                            setattr(existing_vendor, key, value)
                    updated_count += 1
                else:
                    # Create new vendor
                    new_vendor = Supplier(**vendor_info)
                    db.add(new_vendor)
                    imported_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"   ❌ Error processing vendor {vendor_data.get('code', 'Unknown')}: {e}")
                continue
        
        # Final commit
        db.commit()
        
        print(f"✅ Vendor Import Summary:")
        print(f"   🏭 New vendors: {imported_count}")
        print(f"   🔄 Updated vendors: {updated_count}")
        print(f"   ❌ Errors: {error_count}")
        
    except Exception as e:
        print(f"❌ Error importing vendors: {e}")

def main():
    """Main import function"""
    print("🚀 Zoho Data Import to TSH ERP System")
    print("استيراد بيانات Zoho إلى نظام TSH ERP")
    print("=" * 60)
    
    # Get database session
    db = next(get_db())
    
    try:
        print(f"🔄 Starting import process...")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Import data
        import_inventory_items(db)
        import_customers(db)
        import_vendors(db)
        
        print("\n" + "=" * 60)
        print("📊 IMPORT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Verify imports
        items_count = db.query(Product).count()
        customers_count = db.query(Customer).count()
        vendors_count = db.query(Supplier).count()
        
        print("✅ Database Status:")
        print(f"   📦 Products: {items_count:,}")
        print(f"   👥 Customers: {customers_count:,}")
        print(f"   🏭 Suppliers: {vendors_count:,}")
        
        print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
