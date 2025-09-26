#!/usr/bin/env python3
"""
Migrate Items to Products Script
نقل العناصر من جدول migration_items إلى جدول products
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.migration import MigrationItem
from app.models.product import Product, Category
from app.models.warehouse import Warehouse
import random

def migrate_items_to_products():
    """نقل العناصر من migration_items إلى products"""
    
    db = SessionLocal()
    
    try:
        # جلب العناصر من migration_items
        migration_items = db.query(MigrationItem).all()
        
        if not migration_items:
            print("❌ لا توجد عناصر في migration_items")
            return False
            
        print(f"📦 وجدت {len(migration_items)} عنصر في migration_items")
        
        # التأكد من وجود فئة افتراضية
        default_category = db.query(Category).first()
        if not default_category:
            # إنشاء فئة افتراضية
            default_category = Category(
                name="منتجات عامة",
                description="فئة افتراضية للمنتجات",
                is_active=True
            )
            db.add(default_category)
            db.commit()
            db.refresh(default_category)
            print("✅ تم إنشاء فئة افتراضية")
        
        # نقل العناصر
        created_products = []
        for item in migration_items:
            # التحقق من عدم وجود المنتج مسبقاً
            existing = db.query(Product).filter(Product.sku == item.code).first()
            
            if not existing:
                product = Product(
                    sku=item.code,
                    name=item.name_en or item.name_ar,
                    description=item.description_en or item.description_ar or f"منتج {item.name_en or item.name_ar}",
                    category_id=default_category.id,
                    unit_price=float(item.selling_price_usd) if item.selling_price_usd else 0.0,
                    cost_price=float(item.cost_price_usd) if item.cost_price_usd else 0.0,
                    unit_of_measure=item.unit_of_measure or "قطعة",
                    min_stock_level=0,
                    reorder_point=int(float(item.reorder_level)) if item.reorder_level else 10,
                    is_active=item.is_active,
                    is_trackable=item.track_inventory
                )
                
                db.add(product)
                created_products.append(product)
                
        db.commit()
        
        # تحديث معرفات المنتجات
        for product in created_products:
            db.refresh(product)
            
        print(f"✅ تم نقل {len(created_products)} منتج إلى جدول products")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في النقل: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 بدء نقل العناصر من migration_items إلى products...")
    success = migrate_items_to_products()
    
    if success:
        print("✅ تم النقل بنجاح!")
    else:
        print("❌ فشل في النقل!")
        sys.exit(1) 