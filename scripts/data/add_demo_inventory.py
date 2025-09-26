#!/usr/bin/env python3
"""
Demo Inventory Data Creation Script
إنشاء بيانات وهمية للمخزون
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.inventory import InventoryItem, StockMovement
from app.models.product import Product
from app.models.migration import PriceList, PriceListItem, MigrationItem
from app.models.warehouse import Warehouse
from app.models.user import User
from datetime import datetime
import random

def create_demo_inventory_data():
    """إنشاء بيانات وهمية للمخزون"""
    
    db = SessionLocal()
    
    try:
        # التحقق من وجود المنتجات والمستودعات
        products = db.query(Product).limit(10).all()
        warehouses = db.query(Warehouse).limit(3).all()
        users = db.query(User).limit(1).all()
        
        if not products:
            print("❌ لا توجد منتجات، يجب إنشاء منتجات أولاً")
            return False
            
        print(f"📦 وجدت {len(products)} منتج في جدول products")
            
        if not warehouses:
            print("❌ لا توجد مستودعات، يجب إنشاء مستودعات أولاً")
            return False
            
        if not users:
            print("❌ لا يوجد مستخدمون، يجب إنشاء مستخدمين أولاً")
            return False
            
        user_id = users[0].id
        
        print("📦 إنشاء عناصر المخزون...")
        
        # إنشاء عناصر المخزون لكل منتج في كل مستودع
        inventory_items = []
        for item in products:
            for warehouse in warehouses:
                # التحقق من عدم وجود العنصر مسبقاً
                # استخدام معرف العنصر سواء كان product أو migration_item
                item_id = item.id
                existing = db.query(InventoryItem).filter(
                    InventoryItem.product_id == item_id,
                    InventoryItem.warehouse_id == warehouse.id
                ).first()
                
                if not existing:
                    inventory_item = InventoryItem(
                        product_id=item_id,
                        warehouse_id=warehouse.id,
                        quantity_on_hand=random.randint(50, 500),
                        quantity_reserved=random.randint(0, 50),
                        quantity_ordered=random.randint(0, 100),
                        last_cost=round(random.uniform(10.0, 200.0), 2),
                        average_cost=round(random.uniform(10.0, 200.0), 2)
                    )
                    
                    db.add(inventory_item)
                    inventory_items.append(inventory_item)
        
        db.commit()
        
        # تحديث معرفات العناصر
        for item in inventory_items:
            db.refresh(item)
        
        print(f"✅ تم إنشاء {len(inventory_items)} عنصر مخزون")
        
        # إنشاء حركات المخزون التوضيحية
        print("📊 إنشاء حركات المخزون...")
        
        movement_types = ['IN', 'OUT', 'ADJUSTMENT']
        reference_types = ['PURCHASE', 'SALE', 'ADJUSTMENT', 'TRANSFER']
        
        stock_movements = []
        for _ in range(50):  # إنشاء 50 حركة عشوائية
            if inventory_items:
                inventory_item = random.choice(inventory_items)
                movement_type = random.choice(movement_types)
                
                # تحديد الكمية بناءً على نوع الحركة
                if movement_type == 'IN':
                    quantity = random.randint(10, 100)
                elif movement_type == 'OUT':
                    quantity = -random.randint(5, 50)
                else:  # ADJUSTMENT
                    quantity = random.randint(-20, 20)
                
                stock_movement = StockMovement(
                    inventory_item_id=inventory_item.id,
                    movement_type=movement_type,
                    reference_type=random.choice(reference_types),
                    reference_id=random.randint(1, 100),
                    quantity=quantity,
                    unit_cost=round(random.uniform(10.0, 200.0), 2),
                    notes=f"حركة {movement_type} توضيحية",
                    created_by=user_id
                )
                
                db.add(stock_movement)
                stock_movements.append(stock_movement)
        
        db.commit()
        print(f"✅ تم إنشاء {len(stock_movements)} حركة مخزون")
        
        # إنشاء قوائم أسعار
        print("💰 إنشاء قوائم الأسعار...")
        
        price_lists_data = [
            {
                "code": "RETAIL",
                "name_ar": "قائمة أسعار التجزئة",
                "name_en": "Retail Price List", 
                "description_ar": "قائمة الأسعار الأساسية للعملاء",
                "description_en": "Basic price list for customers",
                "currency": "USD",
                "is_active": True
            },
            {
                "code": "WHOLESALE", 
                "name_ar": "قائمة أسعار الجملة",
                "name_en": "Wholesale Price List",
                "description_ar": "قائمة أسعار خاصة لعملاء الجملة",
                "description_en": "Special price list for wholesale customers", 
                "currency": "USD",
                "is_active": True
            },
            {
                "code": "PREMIUM",
                "name_ar": "قائمة الأسعار المميزة",
                "name_en": "Premium Price List",
                "description_ar": "قائمة أسعار للعملاء المميزين",
                "description_en": "Price list for premium customers",
                "currency": "USD", 
                "is_active": True
            }
        ]
        
        created_price_lists = []
        for price_list_data in price_lists_data:
            # التحقق من عدم وجود القائمة مسبقاً
            existing = db.query(PriceList).filter(
                PriceList.code == price_list_data["code"]
            ).first()
            
            if not existing:
                price_list = PriceList(**price_list_data)
                db.add(price_list)
                created_price_lists.append(price_list)
        
        db.commit()
        
        # تحديث معرفات قوائم الأسعار
        for price_list in created_price_lists:
            db.refresh(price_list)
        
        # إضافة عناصر لقوائم الأسعار
        price_list_items = []
        for price_list in created_price_lists:
            for item in products[:5]:  # إضافة أول 5 منتجات فقط
                # تحديد الأسعار بناءً على نوع القائمة
                if price_list.code == "RETAIL":
                    price = round(random.uniform(20.0, 300.0), 2)
                elif price_list.code == "WHOLESALE":
                    price = round(random.uniform(15.0, 250.0), 2)
                else:  # PREMIUM
                    price = round(random.uniform(25.0, 350.0), 2)
                
                price_list_item = PriceListItem(
                    price_list_id=price_list.id,
                    item_id=item.id,  # PriceListItem uses item_id, not product_id
                    unit_price=price,
                    minimum_quantity=random.randint(1, 10),
                    is_active=True
                )
                
                db.add(price_list_item)
                price_list_items.append(price_list_item)
        
        db.commit()
        
        print(f"✅ تم إنشاء {len(created_price_lists)} قائمة أسعار")
        print(f"✅ تم إنشاء {len(price_list_items)} عنصر في قوائم الأسعار")
        
        print("🎉 تم إنشاء جميع البيانات التوضيحية للمخزون بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 بدء إنشاء البيانات التوضيحية للمخزون...")
    success = create_demo_inventory_data()
    
    if success:
        print("✅ تم إنشاء البيانات بنجاح!")
    else:
        print("❌ فشل في إنشاء البيانات!")
        sys.exit(1) 