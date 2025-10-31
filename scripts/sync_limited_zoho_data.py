#!/usr/bin/env python3
"""
Sync Limited Zoho Data to PostgreSQL
Syncs 20 items (with prices & images prioritized), 20 customers, 20 vendors
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LimitedZohoSync:
    """Sync limited Zoho data from existing JSON files"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment")

        # Create database engine
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Data directory
        self.data_dir = project_root / "app" / "data"

    def load_items(self, limit: int = 20) -> List[Dict]:
        """Load items, prioritizing those with images and prices"""
        print(f"\n{'='*60}")
        print(f"📦 LOADING {limit} ITEMS (Images & Prices Prioritized)")
        print(f"{'='*60}")

        items_file = self.data_dir / "tsh_item_records.json"
        if not items_file.exists():
            print("❌ Items file not found!")
            return []

        with open(items_file, 'r', encoding='utf-8') as f:
            all_items = json.load(f)

        print(f"📂 Found {len(all_items)} total items in JSON")

        # Separate items with/without images
        items_with_images = [item for item in all_items if item.get('image_path')]
        items_with_price = [item for item in all_items if float(item.get('selling_price', 0)) > 0]

        # Prioritize items with both images and prices
        items_with_both = [
            item for item in all_items
            if item.get('image_path') and float(item.get('selling_price', 0)) > 0
        ]

        # Build final list
        selected = []

        # First, add items with both
        selected.extend(items_with_both[:limit])

        # Then add items with just images
        if len(selected) < limit:
            remaining = limit - len(selected)
            for item in items_with_images:
                if item not in selected and len(selected) < limit:
                    selected.append(item)

        # Then add items with just prices
        if len(selected) < limit:
            for item in items_with_price:
                if item not in selected and len(selected) < limit:
                    selected.append(item)

        # Finally, add any remaining items
        if len(selected) < limit:
            for item in all_items:
                if item not in selected and len(selected) < limit:
                    selected.append(item)

        selected = selected[:limit]

        print(f"✅ Selected {len(selected)} items:")
        print(f"   - With images: {len([i for i in selected if i.get('image_path')])}")
        print(f"   - With prices: {len([i for i in selected if float(i.get('selling_price', 0)) > 0])}")

        return selected

    def create_sample_customers(self, limit: int = 20) -> List[Dict]:
        """Create sample customers from items data (generate from scratch)"""
        print(f"\n{'='*60}")
        print(f"👥 CREATING {limit} SAMPLE CUSTOMERS")
        print(f"{'='*60}")

        customers = []
        for i in range(1, limit + 1):
            customers.append({
                "zoho_contact_id": f"CUST{i:05d}",
                "name": f"Customer {i}",
                "name_en": f"Customer {i}",
                "company_name": f"Company {i} Ltd.",
                "email": f"customer{i}@example.com",
                "phone": f"+964770{i:07d}",
                "address": f"{i} Business Street, Baghdad, Iraq",
                "is_active": True
            })

        print(f"✅ Created {len(customers)} sample customers")
        return customers

    def create_sample_vendors(self, limit: int = 20) -> List[Dict]:
        """Create sample vendors"""
        print(f"\n{'='*60}")
        print(f"🏭 CREATING {limit} SAMPLE VENDORS")
        print(f"{'='*60}")

        vendors = []
        vendor_names = [
            "Tech Supplies Co.", "Electronics Hub", "Global Import LLC",
            "Prime Distributors", "Smart Electronics", "Digital World Trading",
            "Innovation Supply", "Future Tech Partners", "Elite Wholesale",
            "Universal Trading", "Mega Electronics", "Pro Tech Supply",
            "Advanced Systems", "Quality Components", "First Choice Supplies",
            "Best Value Imports", "Premier Electronics", "Top Grade Supply",
            "Reliable Vendors Inc.", "Express Distributors"
        ]

        for i in range(limit):
            vendors.append({
                "zoho_vendor_id": f"VEND{i+1:05d}",
                "name": vendor_names[i] if i < len(vendor_names) else f"Vendor {i+1}",
                "name_en": vendor_names[i] if i < len(vendor_names) else f"Vendor {i+1}",
                "company_name": vendor_names[i] if i < len(vendor_names) else f"Vendor {i+1} LLC",
                "email": f"vendor{i+1}@supplier{i+1}.com",
                "phone": f"+971{i+1:09d}",
                "address": f"Suite {i+1}, Trading Center, Dubai, UAE",
                "is_active": True
            })

        print(f"✅ Created {len(vendors)} sample vendors")
        return vendors

    def sync_items_to_db(self, items: List[Dict]) -> Dict[str, int]:
        """Sync items to database"""
        if not items:
            return {"inserted": 0, "updated": 0, "errors": 0}

        print(f"\n{'='*60}")
        print(f"💾 SYNCING {len(items)} ITEMS TO DATABASE")
        print(f"{'='*60}")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, item in enumerate(items, 1):
                try:
                    sku = item.get('code') or f"ITEM_{idx}"
                    name = item.get('name', 'Unknown Item')
                    description = item.get('description') or name
                    unit_price = float(item.get('selling_price', 0))
                    category = item.get('specifications', {}).get('category', 'General')

                    # Check if exists
                    result = session.execute(
                        text("SELECT id FROM items WHERE sku = :sku"),
                        {"sku": sku}
                    ).fetchone()

                    if result:
                        session.execute(
                            text("""
                                UPDATE items SET
                                    name = :name,
                                    category = :category,
                                    description = :description,
                                    unit_price = :unit_price,
                                    updated_at = NOW()
                                WHERE sku = :sku
                            """),
                            {
                                "name": name,
                                "category": category,
                                "description": description,
                                "unit_price": unit_price,
                                "sku": sku
                            }
                        )
                        stats['updated'] += 1
                    else:
                        session.execute(
                            text("""
                                INSERT INTO items (sku, name, category, description, unit_price, quantity_on_hand, created_at)
                                VALUES (:sku, :name, :category, :description, :unit_price, 0, NOW())
                            """),
                            {
                                "sku": sku,
                                "name": name,
                                "category": category,
                                "description": description,
                                "unit_price": unit_price
                            }
                        )
                        stats['inserted'] += 1

                    if idx % 10 == 0:
                        print(f"  ⏳ Processed {idx}/{len(items)} items...")

                except Exception as e:
                    print(f"  ❌ Error processing item {idx}: {str(e)}")
                    stats['errors'] += 1

            session.commit()

            print(f"\n✅ Items sync completed!")
            print(f"   - Inserted: {stats['inserted']}")
            print(f"   - Updated: {stats['updated']}")
            print(f"   - Errors: {stats['errors']}")

            return stats

        finally:
            session.close()

    def sync_customers_to_db(self, customers: List[Dict]) -> Dict[str, int]:
        """Sync customers to database"""
        if not customers:
            return {"inserted": 0, "updated": 0, "errors": 0}

        print(f"\n{'='*60}")
        print(f"💾 SYNCING {len(customers)} CUSTOMERS TO DATABASE")
        print(f"{'='*60}")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, customer in enumerate(customers, 1):
                try:
                    customer_code = customer.get('zoho_contact_id', f"CUST{idx:05d}")
                    name = customer.get('name', 'Unknown')
                    company = customer.get('company_name', '')
                    email = customer.get('email', '')
                    phone = customer.get('phone', '')
                    address = customer.get('address', '')

                    result = session.execute(
                        text("SELECT id FROM customers WHERE customer_code = :code"),
                        {"code": customer_code}
                    ).fetchone()

                    if result:
                        session.execute(
                            text("""
                                UPDATE customers SET
                                    name = :name,
                                    company_name = :company,
                                    email = :email,
                                    phone = :phone,
                                    address = :address,
                                    updated_at = NOW()
                                WHERE customer_code = :code
                            """),
                            {"name": name, "company": company, "email": email, "phone": phone, "address": address, "code": customer_code}
                        )
                        stats['updated'] += 1
                    else:
                        session.execute(
                            text("""
                                INSERT INTO customers (customer_code, name, company_name, email, phone, address, is_active, created_at)
                                VALUES (:code, :name, :company, :email, :phone, :address, true, NOW())
                            """),
                            {"code": customer_code, "name": name, "company": company, "email": email, "phone": phone, "address": address}
                        )
                        stats['inserted'] += 1

                except Exception as e:
                    print(f"  ❌ Error processing customer {idx}: {str(e)}")
                    stats['errors'] += 1

            session.commit()

            print(f"\n✅ Customers sync completed!")
            print(f"   - Inserted: {stats['inserted']}")
            print(f"   - Updated: {stats['updated']}")

            return stats

        finally:
            session.close()

    def sync_vendors_to_db(self, vendors: List[Dict]) -> Dict[str, int]:
        """Sync vendors to database"""
        if not vendors:
            return {"inserted": 0, "updated": 0, "errors": 0}

        print(f"\n{'='*60}")
        print(f"💾 SYNCING {len(vendors)} VENDORS TO DATABASE")
        print(f"{'='*60}")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, vendor in enumerate(vendors, 1):
                try:
                    supplier_code = vendor.get('zoho_vendor_id', f"VEND{idx:05d}")
                    name = vendor.get('name', 'Unknown')
                    company = vendor.get('company_name', '')
                    email = vendor.get('email', '')
                    phone = vendor.get('phone', '')
                    address = vendor.get('address', '')

                    result = session.execute(
                        text("SELECT id FROM suppliers WHERE supplier_code = :code"),
                        {"code": supplier_code}
                    ).fetchone()

                    if result:
                        session.execute(
                            text("""
                                UPDATE suppliers SET
                                    name = :name,
                                    company_name = :company,
                                    email = :email,
                                    phone = :phone,
                                    address = :address,
                                    updated_at = NOW()
                                WHERE supplier_code = :code
                            """),
                            {"name": name, "company": company, "email": email, "phone": phone, "address": address, "code": supplier_code}
                        )
                        stats['updated'] += 1
                    else:
                        session.execute(
                            text("""
                                INSERT INTO suppliers (supplier_code, name, company_name, email, phone, address, is_active, created_at)
                                VALUES (:code, :name, :company, :email, :phone, :address, true, NOW())
                            """),
                            {"code": supplier_code, "name": name, "company": company, "email": email, "phone": phone, "address": address}
                        )
                        stats['inserted'] += 1

                except Exception as e:
                    print(f"  ❌ Error processing vendor {idx}: {str(e)}")
                    stats['errors'] += 1

            session.commit()

            print(f"\n✅ Vendors sync completed!")
            print(f"   - Inserted: {stats['inserted']}")
            print(f"   - Updated: {stats['updated']}")

            return stats

        finally:
            session.close()

    def verify_sync(self):
        """Verify synced data"""
        print(f"\n{'='*60}")
        print("🔍 VERIFYING SYNCED DATA")
        print(f"{'='*60}")

        session = self.SessionLocal()
        try:
            # Count totals
            items_count = session.execute(text("SELECT COUNT(*) FROM items")).scalar()
            customers_count = session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
            suppliers_count = session.execute(text("SELECT COUNT(*) FROM suppliers")).scalar()

            print(f"📦 Total Items: {items_count}")
            print(f"👥 Total Customers: {customers_count}")
            print(f"🏭 Total Suppliers: {suppliers_count}")

            # Sample items
            print(f"\n📋 Sample Items (Zoho):")
            items = session.execute(
                text("SELECT sku, name, unit_price FROM items WHERE sku LIKE 'tsh%' ORDER BY id DESC LIMIT 5")
            ).fetchall()

            for item in items:
                print(f"   - {item[0]}: {item[1]} (${item[2]})")

        finally:
            session.close()


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🚀 LIMITED ZOHO DATA SYNC")
    print("="*60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Targets: 20 items (prices & images), 20 customers, 20 vendors")

    try:
        syncer = LimitedZohoSync()

        # Load/create data
        items = syncer.load_items(limit=20)
        customers = syncer.create_sample_customers(limit=20)
        vendors = syncer.create_sample_vendors(limit=20)

        # Sync to database
        syncer.sync_items_to_db(items)
        syncer.sync_customers_to_db(customers)
        syncer.sync_vendors_to_db(vendors)

        # Verify
        syncer.verify_sync()

        print("\n" + "="*60)
        print("✅ SYNC COMPLETED SUCCESSFULLY!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
