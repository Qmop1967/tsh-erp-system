#!/usr/bin/env python3
"""
Test Items Data and Models for TSH ERP System
اختبار بيانات ونماذج الأصناف
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.getcwd())

from app.db.database import get_db
from app.models.migration import ItemCategory, MigrationItem


def test_categories_data():
    """Test categories data in database"""
    print("🧪 Testing Categories Data...")
    print("-" * 40)
    
    try:
        db = next(get_db())
        categories = db.query(ItemCategory).all()
        
        print(f"✅ Found {len(categories)} categories in database")
        
        for cat in categories:
            print(f"  • {cat.code}: {cat.name_en} ({cat.name_ar})")
            print(f"    Level: {cat.level}, Sort: {cat.sort_order}, Active: {cat.is_active}")
            
        db.close()
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_items_data():
    """Test items data in database"""
    print("\n🧪 Testing Items Data...")
    print("-" * 40)
    
    try:
        db = next(get_db())
        items = db.query(MigrationItem).all()
        
        print(f"✅ Found {len(items)} items in database")
        
        for item in items:
            category = db.query(ItemCategory).filter(ItemCategory.id == item.category_id).first()
            print(f"  • {item.code}: {item.name_en}")
            print(f"    Category: {category.name_en if category else 'No Category'}")
            print(f"    Cost: ${item.cost_price_usd} | Selling: ${item.selling_price_usd}")
            print(f"    Unit: {item.unit_of_measure} | Brand: {item.brand}")
            print(f"    Active: {item.is_active} | Track Inventory: {item.track_inventory}")
            print()
            
        db.close()
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_relationships():
    """Test database relationships"""
    print("\n🧪 Testing Database Relationships...")
    print("-" * 40)
    
    try:
        db = next(get_db())
        
        # Test category-item relationships
        categories_with_items = []
        for cat in db.query(ItemCategory).all():
            item_count = db.query(MigrationItem).filter(MigrationItem.category_id == cat.id).count()
            if item_count > 0:
                categories_with_items.append((cat, item_count))
        
        print(f"Categories with items: {len(categories_with_items)}")
        for cat, count in categories_with_items:
            print(f"  • {cat.name_en}: {count} items")
            
        # Test data integrity
        orphaned_items = db.query(MigrationItem).filter(MigrationItem.category_id.isnot(None)).filter(
            ~MigrationItem.category_id.in_(db.query(ItemCategory.id))
        ).count()
        
        print(f"\\nData integrity:")
        print(f"  • Orphaned items (invalid category_id): {orphaned_items}")
        
        if orphaned_items == 0:
            print("  ✅ All item categories are valid")
        else:
            print("  ⚠️  Some items have invalid category references")
            
        db.close()
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    """Main test function"""
    print("🚀 Testing Items Management Data and Models")
    print("=" * 60)
    
    test_categories_data()
    test_items_data()
    test_relationships()
    
    print("\n" + "=" * 60)
    print("📊 FINAL STATUS:")
    
    # Database stats
    db = next(get_db())
    
    total_categories = db.query(ItemCategory).count()
    total_items = db.query(MigrationItem).count()
    active_items = db.query(MigrationItem).filter(MigrationItem.is_active == True).count()
    
    print(f"  📂 Categories: {total_categories}")
    print(f"  📦 Total Items: {total_items}")
    print(f"  ✅ Active Items: {active_items}")
    
    # Check if sample data exists
    sample_categories = ['ELECTRONICS', 'COMPUTERS', 'MOBILE', 'ACCESSORIES', 'NETWORKING']
    sample_items = ['LAP-001', 'PHN-001', 'MON-001', 'ACC-001', 'NET-001', 'CBL-001']
    
    existing_categories = db.query(ItemCategory).filter(ItemCategory.code.in_(sample_categories)).count()
    existing_items = db.query(MigrationItem).filter(MigrationItem.code.in_(sample_items)).count()
    
    print(f"  🎯 Sample Categories: {existing_categories}/{len(sample_categories)}")
    print(f"  🎯 Sample Items: {existing_items}/{len(sample_items)}")
    
    if existing_categories == len(sample_categories) and existing_items == len(sample_items):
        print("\n✅ All sample data is ready!")
        print("🎉 Items management system is ready for testing!")
    else:
        print("\n⚠️  Some sample data is missing. Run init_items_data.py")
    
    db.close()


if __name__ == "__main__":
    main()
