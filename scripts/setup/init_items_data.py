#!/usr/bin/env python3
"""
Initialize Items Data for TSH ERP System
إعداد بيانات الأصناف لنظام TSH ERP
"""

import sys
import os
from decimal import Decimal
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.getcwd())

from app.db.database import get_db
from app.models.migration import ItemCategory, MigrationItem
from sqlalchemy.orm import Session


def create_item_categories(db: Session):
    """إنشاء فئات الأصناف"""
    
    categories = [
        {
            'code': 'ELECTRONICS',
            'name_ar': 'الإلكترونيات',
            'name_en': 'Electronics',
            'description_ar': 'الأجهزة الإلكترونية والكهربائية',
            'description_en': 'Electronic and electrical devices',
            'parent_id': None,
            'level': 1,
            'sort_order': 10
        },
        {
            'code': 'COMPUTERS',
            'name_ar': 'أجهزة الكمبيوتر',
            'name_en': 'Computers',
            'description_ar': 'أجهزة الكمبيوتر المحمولة والمكتبية',
            'description_en': 'Laptops, desktops and computer systems',
            'parent_id': 1,  # Electronics
            'level': 2,
            'sort_order': 11
        },
        {
            'code': 'MOBILE',
            'name_ar': 'الهواتف المحمولة',
            'name_en': 'Mobile Phones',
            'description_ar': 'الهواتف الذكية والأجهزة اللوحية',
            'description_en': 'Smartphones and tablets',
            'parent_id': 1,  # Electronics
            'level': 2,
            'sort_order': 12
        },
        {
            'code': 'ACCESSORIES',
            'name_ar': 'الإكسسوارات',
            'name_en': 'Accessories',
            'description_ar': 'إكسسوارات الكمبيوتر والهواتف',
            'description_en': 'Computer and phone accessories',
            'parent_id': None,
            'level': 1,
            'sort_order': 20
        },
        {
            'code': 'NETWORKING',
            'name_ar': 'الشبكات',
            'name_en': 'Networking',
            'description_ar': 'معدات الشبكات والاتصالات',
            'description_en': 'Network and communication equipment',
            'parent_id': None,
            'level': 1,
            'sort_order': 30
        }
    ]
    
    created_categories = []
    
    for cat_data in categories:
        # Check if category already exists
        existing = db.query(ItemCategory).filter(ItemCategory.code == cat_data['code']).first()
        if existing:
            print(f"📂 Category already exists: {cat_data['name_en']}")
            created_categories.append(existing)
            continue
            
        category = ItemCategory(**cat_data)
        db.add(category)
        created_categories.append(category)
        print(f"✅ Created category: {cat_data['name_en']}")
    
    db.commit()
    return created_categories


def create_sample_items(db: Session):
    """إنشاء أصناف تجريبية"""
    
    # Get categories
    electronics = db.query(ItemCategory).filter(ItemCategory.code == 'ELECTRONICS').first()
    computers = db.query(ItemCategory).filter(ItemCategory.code == 'COMPUTERS').first()
    mobile = db.query(ItemCategory).filter(ItemCategory.code == 'MOBILE').first()
    accessories = db.query(ItemCategory).filter(ItemCategory.code == 'ACCESSORIES').first()
    networking = db.query(ItemCategory).filter(ItemCategory.code == 'NETWORKING').first()
    
    items = [
        {
            'code': 'LAP-001',
            'name_ar': 'لاب توب ديل XPS 13',
            'name_en': 'Dell XPS 13 Laptop',
            'description_ar': 'لاب توب ديل عالي الأداء بمعالج Intel Core i7',
            'description_en': 'High-performance Dell laptop with Intel Core i7 processor',
            'category_id': computers.id if computers else None,
            'brand': 'Dell',
            'model': 'XPS 13',
            'unit_of_measure': 'PCS',
            'cost_price_usd': Decimal('800.00'),
            'cost_price_iqd': Decimal('1056000.00'),  # 800 * 1320
            'selling_price_usd': Decimal('1200.00'),
            'selling_price_iqd': Decimal('1584000.00'),  # 1200 * 1320
            'track_inventory': True,
            'reorder_level': Decimal('5.00'),
            'reorder_quantity': Decimal('10.00'),
            'weight': Decimal('1.2'),
            'dimensions': '30.2 x 19.9 x 1.4 cm',
            'is_active': True
        },
        {
            'code': 'PHN-001',
            'name_ar': 'آيفون 15 برو',
            'name_en': 'iPhone 15 Pro',
            'description_ar': 'هاتف آبل الذكي الجديد بتقنية A17 Pro',
            'description_en': 'Latest Apple smartphone with A17 Pro chip',
            'category_id': mobile.id if mobile else None,
            'brand': 'Apple',
            'model': 'iPhone 15 Pro',
            'unit_of_measure': 'PCS',
            'cost_price_usd': Decimal('900.00'),
            'cost_price_iqd': Decimal('1188000.00'),
            'selling_price_usd': Decimal('1399.00'),
            'selling_price_iqd': Decimal('1846680.00'),
            'track_inventory': True,
            'reorder_level': Decimal('3.00'),
            'reorder_quantity': Decimal('5.00'),
            'weight': Decimal('0.187'),
            'dimensions': '14.67 x 7.09 x 0.83 cm',
            'is_active': True
        },
        {
            'code': 'MON-001',
            'name_ar': 'شاشة سامسونج 27 بوصة',
            'name_en': 'Samsung 27" Monitor',
            'description_ar': 'شاشة سامسونج عالية الدقة 4K',
            'description_en': 'Samsung 4K high-resolution monitor',
            'category_id': electronics.id if electronics else None,
            'brand': 'Samsung',
            'model': 'M7 27"',
            'unit_of_measure': 'PCS',
            'cost_price_usd': Decimal('250.00'),
            'cost_price_iqd': Decimal('330000.00'),
            'selling_price_usd': Decimal('399.00'),
            'selling_price_iqd': Decimal('526680.00'),
            'track_inventory': True,
            'reorder_level': Decimal('2.00'),
            'reorder_quantity': Decimal('5.00'),
            'weight': Decimal('4.5'),
            'dimensions': '61.2 x 36.3 x 20.6 cm',
            'is_active': True
        },
        {
            'code': 'ACC-001',
            'name_ar': 'ماوس لاسلكي لوجيتك',
            'name_en': 'Logitech Wireless Mouse',
            'description_ar': 'ماوس لاسلكي عالي الدقة من لوجيتك',
            'description_en': 'High-precision wireless mouse from Logitech',
            'category_id': accessories.id if accessories else None,
            'brand': 'Logitech',
            'model': 'MX Master 3S',
            'unit_of_measure': 'PCS',
            'cost_price_usd': Decimal('15.00'),
            'cost_price_iqd': Decimal('19800.00'),
            'selling_price_usd': Decimal('29.99'),
            'selling_price_iqd': Decimal('39587.00'),
            'track_inventory': True,
            'reorder_level': Decimal('10.00'),
            'reorder_quantity': Decimal('20.00'),
            'weight': Decimal('0.141'),
            'dimensions': '12.4 x 8.4 x 5.1 cm',
            'is_active': True
        },
        {
            'code': 'NET-001',
            'name_ar': 'راوتر TP-Link',
            'name_en': 'TP-Link Router',
            'description_ar': 'راوتر لاسلكي عالي السرعة',
            'description_en': 'High-speed wireless router',
            'category_id': networking.id if networking else None,
            'brand': 'TP-Link',
            'model': 'Archer AX50',
            'unit_of_measure': 'PCS',
            'cost_price_usd': Decimal('75.00'),
            'cost_price_iqd': Decimal('99000.00'),
            'selling_price_usd': Decimal('129.00'),
            'selling_price_iqd': Decimal('170280.00'),
            'track_inventory': True,
            'reorder_level': Decimal('5.00'),
            'reorder_quantity': Decimal('10.00'),
            'weight': Decimal('0.68'),
            'dimensions': '26.0 x 13.5 x 3.8 cm',
            'is_active': True
        },
        {
            'code': 'CBL-001',
            'name_ar': 'كابل USB-C',
            'name_en': 'USB-C Cable',
            'description_ar': 'كابل USB-C عالي الجودة طول متر واحد',
            'description_en': 'High-quality USB-C cable 1 meter length',
            'category_id': accessories.id if accessories else None,
            'brand': 'Anker',
            'model': 'PowerLine III',
            'unit_of_measure': 'PCS',
            'cost_price_usd': Decimal('5.00'),
            'cost_price_iqd': Decimal('6600.00'),
            'selling_price_usd': Decimal('12.99'),
            'selling_price_iqd': Decimal('17147.00'),
            'track_inventory': True,
            'reorder_level': Decimal('20.00'),
            'reorder_quantity': Decimal('50.00'),
            'weight': Decimal('0.05'),
            'dimensions': '100 cm length',
            'is_active': True
        }
    ]
    
    created_items = []
    
    for item_data in items:
        # Check if item already exists
        existing = db.query(MigrationItem).filter(MigrationItem.code == item_data['code']).first()
        if existing:
            print(f"📦 Item already exists: {item_data['name_en']}")
            created_items.append(existing)
            continue
            
        item = MigrationItem(**item_data)
        db.add(item)
        created_items.append(item)
        print(f"✅ Created item: {item_data['name_en']} ({item_data['code']})")
    
    db.commit()
    return created_items


def main():
    """الدالة الرئيسية"""
    print("🚀 Initializing Items Data for TSH ERP System...")
    print("=" * 60)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create categories
        print("\n📂 Creating Item Categories...")
        categories = create_item_categories(db)
        print(f"✅ Created/Found {len(categories)} categories")
        
        # Create sample items
        print("\n📦 Creating Sample Items...")
        items = create_sample_items(db)
        print(f"✅ Created/Found {len(items)} items")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY:")
        
        total_categories = db.query(ItemCategory).count()
        total_items = db.query(MigrationItem).count()
        active_items = db.query(MigrationItem).filter(MigrationItem.is_active == True).count()
        
        print(f"  📂 Total Categories: {total_categories}")
        print(f"  📦 Total Items: {total_items}")
        print(f"  ✅ Active Items: {active_items}")
        
        # Calculate total inventory value
        from sqlalchemy import func
        total_cost_usd = db.query(func.sum(MigrationItem.cost_price_usd)).scalar() or 0
        total_selling_usd = db.query(func.sum(MigrationItem.selling_price_usd)).scalar() or 0
        
        print(f"  💰 Total Cost Value: ${total_cost_usd:,.2f}")
        print(f"  💵 Total Selling Value: ${total_selling_usd:,.2f}")
        print(f"  📈 Potential Margin: ${total_selling_usd - total_cost_usd:,.2f}")
        
        print("\n🎉 Items data initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
