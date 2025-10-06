#!/usr/bin/env python3
"""
Create inventory items for all products that don't have them yet
"""
import os
import sys

# Add project root to path
sys.path.insert(0, '/Users/khaleelal-mulla/TSH_ERP_System_Local')

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.product import Product
from app.models.inventory_item import InventoryItem
from decimal import Decimal

def create_inventory_items():
    db = SessionLocal()

    try:
        # Get default warehouse ID (assuming warehouse 1 exists)
        warehouse_id = 1

        # Get all products
        products = db.query(Product).all()
        print(f"📦 Found {len(products)} products in database")

        # Get existing inventory items
        existing_items = db.query(InventoryItem).all()
        existing_product_ids = {item.product_id for item in existing_items}
        print(f"📊 Found {len(existing_items)} existing inventory items")

        # Create inventory items for products that don't have them
        created_count = 0
        for product in products:
            if product.id not in existing_product_ids:
                inventory_item = InventoryItem(
                    product_id=product.id,
                    warehouse_id=warehouse_id,
                    quantity_on_hand=Decimal('0'),  # Start with 0, can be updated later
                    quantity_reserved=Decimal('0'),
                    quantity_ordered=Decimal('0'),
                    last_cost=product.unit_price if product.unit_price else Decimal('0'),
                    average_cost=product.unit_price if product.unit_price else Decimal('0')
                )
                db.add(inventory_item)
                created_count += 1

                # Commit every 100 items
                if created_count % 100 == 0:
                    db.commit()
                    print(f"✅ Created {created_count} inventory items...")

        # Final commit
        db.commit()

        print(f"\n{'='*60}")
        print(f"✅ Successfully created {created_count} new inventory items!")
        print(f"📊 Total inventory items now: {len(existing_items) + created_count}")
        print(f"{'='*60}")

        return created_count

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating inventory items for all products...\n")
    create_inventory_items()
    print("\n✅ Done!")
