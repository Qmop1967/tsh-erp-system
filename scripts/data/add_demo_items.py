#!/usr/bin/env python3
"""
Add Demo Items Script for TSH ERP System
إضافة عناصر تجريبية لنظام TSH ERP

This script adds sample items to the database for testing purposes.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.migration import MigrationItem, ItemCategory
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/erp_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_demo_items():
    """Add demo items to the database"""
    db = SessionLocal()
    
    try:
        print("🏷️ Adding demo items to TSH ERP System...")
        
        # Get categories for reference
        electronics_cat = db.query(ItemCategory).filter(ItemCategory.code == "ELECTRONICS").first()
        computers_cat = db.query(ItemCategory).filter(ItemCategory.code == "COMPUTERS").first()
        mobile_cat = db.query(ItemCategory).filter(ItemCategory.code == "MOBILE").first()
        accessories_cat = db.query(ItemCategory).filter(ItemCategory.code == "ACCESSORIES").first()
        networking_cat = db.query(ItemCategory).filter(ItemCategory.code == "NETWORKING").first()
        
        # Demo items to add
        demo_items = [
            {
                "code": "SPH-S23-128GB-BLK",
                "name_ar": "هاتف سامسونغ جالاكسي اس 23 - 128 جيجا - أسود",
                "name_en": "Samsung Galaxy S23 - 128GB - Black",
                "description_ar": "هاتف ذكي متطور مع كاميرا عالية الدقة وأداء ممتاز",
                "description_en": "Advanced smartphone with high-resolution camera and excellent performance",
                "category_id": mobile_cat.id if mobile_cat else None,
                "brand": "Samsung",
                "model": "Galaxy S23",
                "specifications": '{"storage": "128GB", "color": "Black", "camera": "50MP", "battery": "3900mAh", "display": "6.1 inch"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 650.00,
                "cost_price_iqd": 850000.00,
                "selling_price_usd": 799.00,
                "selling_price_iqd": 1045000.00,
                "track_inventory": True,
                "reorder_level": 5.0,
                "reorder_quantity": 20.0,
                "weight": 0.168,
                "dimensions": "146.3 x 70.9 x 7.6 mm",
                "is_active": True,
                "is_serialized": True,
                "is_batch_tracked": False
            },
            {
                "code": "LTP-XPS13-512GB-SLV",
                "name_ar": "لابتوب ديل اكس بي اس 13 - 512 جيجا - فضي",
                "name_en": "Dell XPS 13 Laptop - 512GB - Silver",
                "description_ar": "لابتوب عالي الأداء مع معالج Intel Core i7 وذاكرة SSD",
                "description_en": "High-performance laptop with Intel Core i7 processor and SSD storage",
                "category_id": computers_cat.id if computers_cat else None,
                "brand": "Dell",
                "model": "XPS 13",
                "specifications": '{"processor": "Intel Core i7", "ram": "16GB", "storage": "512GB SSD", "display": "13.3 inch 4K", "color": "Silver"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 1200.00,
                "cost_price_iqd": 1560000.00,
                "selling_price_usd": 1499.00,
                "selling_price_iqd": 1950000.00,
                "track_inventory": True,
                "reorder_level": 3.0,
                "reorder_quantity": 10.0,
                "weight": 1.2,
                "dimensions": "295.7 x 199.2 x 14.8 mm",
                "is_active": True,
                "is_serialized": True,
                "is_batch_tracked": False
            },
            {
                "code": "HDP-SONY-WH1000XM5",
                "name_ar": "سماعات سوني اللاسلكية مع خاصية إلغاء الضوضاء",
                "name_en": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
                "description_ar": "سماعات لاسلكية متطورة مع خاصية إلغاء الضوضاء الذكية",
                "description_en": "Premium wireless headphones with intelligent noise canceling",
                "category_id": accessories_cat.id if accessories_cat else None,
                "brand": "Sony",
                "model": "WH-1000XM5",
                "specifications": '{"type": "Over-ear", "connectivity": "Bluetooth 5.2", "battery": "30 hours", "noise_canceling": "Yes"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 280.00,
                "cost_price_iqd": 365000.00,
                "selling_price_usd": 349.00,
                "selling_price_iqd": 455000.00,
                "track_inventory": True,
                "reorder_level": 10.0,
                "reorder_quantity": 30.0,
                "weight": 0.25,
                "dimensions": "Foldable design",
                "is_active": True,
                "is_serialized": False,
                "is_batch_tracked": False
            },
            {
                "code": "RTR-CISCO-RV340",
                "name_ar": "راوتر سيسكو للشركات الصغيرة",
                "name_en": "Cisco RV340 Small Business Router",
                "description_ar": "راوتر عالي الأداء للشركات الصغيرة مع خاصية VPN",
                "description_en": "High-performance small business router with VPN capabilities",
                "category_id": networking_cat.id if networking_cat else None,
                "brand": "Cisco",
                "model": "RV340",
                "specifications": '{"ports": "4x Gigabit Ethernet", "vpn": "IPSec/SSL VPN", "throughput": "900 Mbps", "security": "Firewall"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 320.00,
                "cost_price_iqd": 416000.00,
                "selling_price_usd": 399.00,
                "selling_price_iqd": 520000.00,
                "track_inventory": True,
                "reorder_level": 5.0,
                "reorder_quantity": 15.0,
                "weight": 1.5,
                "dimensions": "200 x 180 x 44 mm",
                "is_active": True,
                "is_serialized": True,
                "is_batch_tracked": False
            },
            {
                "code": "MON-LG-27UP850",
                "name_ar": "شاشة إل جي 27 بوصة 4K للتصميم",
                "name_en": "LG 27UP850 27-inch 4K Monitor for Design",
                "description_ar": "شاشة احترافية للتصميم مع دقة 4K ودعم HDR",
                "description_en": "Professional design monitor with 4K resolution and HDR support",
                "category_id": computers_cat.id if computers_cat else None,
                "brand": "LG",
                "model": "27UP850",
                "specifications": '{"size": "27 inch", "resolution": "3840x2160", "panel": "IPS", "color_gamut": "99% sRGB", "hdr": "HDR10"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 380.00,
                "cost_price_iqd": 495000.00,
                "selling_price_usd": 479.00,
                "selling_price_iqd": 625000.00,
                "track_inventory": True,
                "reorder_level": 3.0,
                "reorder_quantity": 12.0,
                "weight": 5.7,
                "dimensions": "611.4 x 362.8 x 55.1 mm",
                "is_active": True,
                "is_serialized": True,
                "is_batch_tracked": False
            },
            {
                "code": "KBD-LOGITECH-MX",
                "name_ar": "كيبورد لوجيتك اللاسلكي للمبرمجين",
                "name_en": "Logitech MX Keys Wireless Keyboard for Programmers",
                "description_ar": "كيبورد لاسلكي متطور مع إضاءة خلفية ذكية",
                "description_en": "Advanced wireless keyboard with smart backlighting",
                "category_id": accessories_cat.id if accessories_cat else None,
                "brand": "Logitech",
                "model": "MX Keys",
                "specifications": '{"connectivity": "Bluetooth/USB", "backlight": "Smart illumination", "battery": "10 days", "layout": "Full-size"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 75.00,
                "cost_price_iqd": 97500.00,
                "selling_price_usd": 99.00,
                "selling_price_iqd": 129000.00,
                "track_inventory": True,
                "reorder_level": 15.0,
                "reorder_quantity": 50.0,
                "weight": 0.81,
                "dimensions": "430 x 131 x 20.5 mm",
                "is_active": True,
                "is_serialized": False,
                "is_batch_tracked": False
            },
            {
                "code": "SSD-SAMSUNG-980PRO-1TB",
                "name_ar": "قرص تخزين SSD سامسونغ 980 برو - 1 تيرا",
                "name_en": "Samsung 980 PRO SSD - 1TB NVMe",
                "description_ar": "قرص تخزين SSD عالي السرعة للألعاب والتطبيقات الاحترافية",
                "description_en": "High-speed SSD for gaming and professional applications",
                "category_id": computers_cat.id if computers_cat else None,
                "brand": "Samsung",
                "model": "980 PRO",
                "specifications": '{"capacity": "1TB", "interface": "NVMe PCIe 4.0", "read_speed": "7000 MB/s", "write_speed": "5000 MB/s"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 120.00,
                "cost_price_iqd": 156000.00,
                "selling_price_usd": 149.00,
                "selling_price_iqd": 194000.00,
                "track_inventory": True,
                "reorder_level": 20.0,
                "reorder_quantity": 50.0,
                "weight": 0.008,
                "dimensions": "80.15 x 22.15 x 2.38 mm",
                "is_active": True,
                "is_serialized": False,
                "is_batch_tracked": True
            },
            {
                "code": "CAM-LOGITECH-C920S",
                "name_ar": "كاميرا ويب لوجيتك بدقة Full HD",
                "name_en": "Logitech C920S HD Pro Webcam",
                "description_ar": "كاميرا ويب احترافية للاجتماعات والبث المباشر",
                "description_en": "Professional webcam for meetings and streaming",
                "category_id": accessories_cat.id if accessories_cat else None,
                "brand": "Logitech",
                "model": "C920S",
                "specifications": '{"resolution": "1080p", "frame_rate": "30fps", "field_of_view": "78°", "autofocus": "Yes", "microphone": "Dual stereo"}',
                "unit_of_measure": "PCS",
                "cost_price_usd": 55.00,
                "cost_price_iqd": 71500.00,
                "selling_price_usd": 69.00,
                "selling_price_iqd": 90000.00,
                "track_inventory": True,
                "reorder_level": 25.0,
                "reorder_quantity": 100.0,
                "weight": 0.162,
                "dimensions": "94 x 71 x 43.3 mm",
                "is_active": True,
                "is_serialized": False,
                "is_batch_tracked": False
            }
        ]
        
        # Add items to database
        added_count = 0
        for item_data in demo_items:
            # Check if item already exists
            existing_item = db.query(MigrationItem).filter(MigrationItem.code == item_data["code"]).first()
            if existing_item:
                print(f"   ⚠️  Item {item_data['code']} already exists, skipping...")
                continue
            
            # Create new item
            new_item = MigrationItem(**item_data)
            db.add(new_item)
            added_count += 1
            print(f"   ✅ Added: {item_data['name_en']} ({item_data['code']})")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Successfully added {added_count} demo items!")
        print(f"📊 Total items now in database: {db.query(MigrationItem).count()}")
        
        # Display summary by category
        print("\n📊 Items by Category:")
        for category in [electronics_cat, computers_cat, mobile_cat, accessories_cat, networking_cat]:
            if category:
                count = db.query(MigrationItem).filter(MigrationItem.category_id == category.id).count()
                print(f"   🏷️  {category.name_en}: {count} items")
        
    except Exception as e:
        print(f"❌ Error adding demo items: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_demo_items()
