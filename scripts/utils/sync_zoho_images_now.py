#!/usr/bin/env python3
"""
Quick Zoho Image Sync Script
This script syncs images from the existing Zoho data to the TSH ERP database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import requests
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.product import Product
from datetime import datetime

def sync_images_to_database():
    """Sync image URLs from Zoho JSON data to database"""
    
    print("🖼️  Zoho Image Database Sync")
    print("=" * 70)
    
    # Load Zoho items with images
    zoho_file = Path("all_zoho_inventory_items.json")
    
    if not zoho_file.exists():
        print(f"❌ File not found: {zoho_file}")
        return
    
    print(f"📂 Loading items from: {zoho_file}")
    with open(zoho_file, 'r', encoding='utf-8') as f:
        zoho_items = json.load(f)
    
    print(f"✅ Loaded {len(zoho_items)} items from Zoho data")
    print()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Stats
        stats = {
            'total_items': len(zoho_items),
            'updated': 0,
            'images_added': 0,
            'not_found': 0,
            'placeholder_images': 0,
            'real_images': 0
        }
        
        print("🔄 Syncing images to database...")
        print("-" * 70)
        
        for idx, item in enumerate(zoho_items, 1):
            zoho_id = item.get('zoho_item_id')
            sku = item.get('code')
            image_url = item.get('image_url')
            image_name = item.get('image_name')
            
            if not zoho_id:
                continue
            
            # Find product in database by SKU or by checking tags for zoho_item_id
            product = None
            
            # First try by SKU (most common and fastest)
            if sku:
                product = db.query(Product).filter(Product.sku == sku).first()
            
            # If not found by SKU, try to find by tags containing zoho_item_id
            if not product:
                products = db.query(Product).all()
                for p in products:
                    if p.tags and isinstance(p.tags, list):
                        for tag in p.tags:
                            if isinstance(tag, dict) and tag.get('zoho_item_id') == zoho_id:
                                product = p
                                break
                        if product:
                            break
            
            if not product:
                stats['not_found'] += 1
                if idx % 100 == 0:
                    print(f"  ⏳ Processed {idx}/{len(zoho_items)}... (Not found: {stats['not_found']})")
                continue
            
            # Check if image_url exists
            if image_url:
                # Check if it's a placeholder
                is_placeholder = 'placeholder' in image_url.lower()
                
                if is_placeholder:
                    stats['placeholder_images'] += 1
                else:
                    stats['real_images'] += 1
                
                # Update product image
                product.image_url = image_url
                
                # Add to images array if not already there
                if not product.images:
                    product.images = []
                
                # Check if image already exists in array
                image_exists = any(
                    img.get('url') == image_url 
                    for img in product.images 
                    if isinstance(img, dict)
                )
                
                if not image_exists:
                    product.images.append({
                        'url': image_url,
                        'source': 'zoho',
                        'zoho_image_name': image_name,
                        'synced_at': datetime.now().isoformat()
                    })
                    stats['images_added'] += 1
                
                stats['updated'] += 1
            
            # Progress indicator
            if idx % 100 == 0:
                print(f"  ⏳ Processed {idx}/{len(zoho_items)}... ({stats['updated']} updated)")
        
        # Commit all changes
        db.commit()
        
        print()
        print("=" * 70)
        print("📊 SYNC RESULTS:")
        print(f"   Total Items:        {stats['total_items']}")
        print(f"   Products Updated:   {stats['updated']}")
        print(f"   Images Added:       {stats['images_added']}")
        print(f"   Not Found in DB:    {stats['not_found']}")
        print(f"   Real Images:        {stats['real_images']}")
        print(f"   Placeholder Images: {stats['placeholder_images']}")
        print("=" * 70)
        print()
        
        if stats['placeholder_images'] > 0:
            print("⚠️  NOTE: Some images are placeholders.")
            print("   To get real Zoho images, you need to:")
            print("   1. Update Zoho credentials in the system")
            print("   2. Re-fetch items from Zoho API with real images")
            print("   3. Re-run this sync")
            print()
        
        if stats['real_images'] > 0:
            print(f"✅ Successfully synced {stats['real_images']} real images!")
            print()
        
        if stats['updated'] > 0:
            print("✅ Image sync to database completed!")
        else:
            print("⚠️  No products were updated.")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_images_to_database()

