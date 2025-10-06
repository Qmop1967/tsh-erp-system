#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/khaleelal-mulla/TSH_ERP_System_Local')

from app.database import SessionLocal
from app.models.product import Product
from app.models.inventory_item import InventoryItem

db = SessionLocal()

# Check products with images
products_with_images = db.query(Product).filter(Product.image_url != None, Product.image_url != '').limit(5).all()

print("📦 Products in Database with Images:")
print("=" * 70)
for p in products_with_images:
    print(f"ID: {p.id} | SKU: {p.sku} | Name: {p.name}")
    print(f"   Image: {p.image_url}")
    print()

# Check total products
total_products = db.query(Product).count()
total_with_images = db.query(Product).filter(Product.image_url != None, Product.image_url != '').count()

print("=" * 70)
print(f"Total Products: {total_products}")
print(f"Products with Images: {total_with_images}")
print("=" * 70)

# Check inventory items
total_inventory = db.query(InventoryItem).count()
print(f"\nTotal Inventory Items: {total_inventory}")

db.close()
