#!/usr/bin/env python3
"""
Zoho Books to PostgreSQL Sync Script
Pulls master data from Zoho Books and inserts into local PostgreSQL database
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ZohoToPostgresSync:
    """Sync Zoho Books data to PostgreSQL"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.zoho_org_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")

        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment")

        # Create database engine
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Load existing synced data from JSON
        self.data_dir = project_root / "app" / "data"
        self.items_file = self.data_dir / "tsh_item_records.json"

    def load_json_data(self, entity_type: str, limit: Optional[int] = None) -> List[Dict]:
        """Load data from JSON files with optional limit"""
        file_map = {
            "items": self.data_dir / "tsh_item_records.json",
            "customers": self.data_dir / "tsh_customer_records.json",
            "vendors": self.data_dir / "tsh_vendor_records.json"
        }

        file_path = file_map.get(entity_type)
        if file_path and file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Apply limit if specified
                if limit and len(data) > limit:
                    print(f"  ℹ️  Limiting {entity_type} from {len(data)} to {limit} records")
                    return data[:limit]
                return data
        return []

    def sync_items(self, limit: int = 100) -> Dict[str, Any]:
        """Sync items from JSON to PostgreSQL (limited to 100 items with images)"""
        print("\n" + "="*60)
        print(f"🔄 SYNCING ITEMS TO POSTGRESQL (Limit: {limit})")
        print("="*60)

        # Load limited items - prioritize those with images
        all_items = self.load_json_data("items", limit=None)

        # Filter items with images first
        items_with_images = [item for item in all_items if item.get('image_path')]
        items_without_images = [item for item in all_items if not item.get('image_path')]

        # Take up to limit, prioritizing items with images
        items = items_with_images[:limit] + items_without_images[:max(0, limit - len(items_with_images))]
        items = items[:limit]

        print(f"  📷 Items with images: {len([i for i in items if i.get('image_path')])}")
        print(f"  📦 Total items to sync: {len(items)}")

        if not items:
            print("⚠️  No items found in JSON data")
            return {"status": "skipped", "count": 0}

        print(f"📦 Found {len(items)} items in JSON data")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0, "skipped": 0}

        try:
            for idx, item in enumerate(items, 1):
                try:
                    # Check if item exists by SKU/code
                    code = item.get('code') or f"ITEM_{idx}"

                    # Check existing
                    result = session.execute(
                        text("SELECT id FROM items WHERE sku = :sku"),
                        {"sku": code}
                    ).fetchone()

                    if result:
                        # Update existing
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
                                "name": item.get('name', 'Unknown Item'),
                                "category": item.get('specifications', {}).get('category', 'General'),
                                "description": item.get('description') or item.get('name', 'No description'),
                                "unit_price": float(item.get('selling_price', 0)),
                                "sku": code
                            }
                        )
                        stats['updated'] += 1
                    else:
                        # Insert new
                        session.execute(
                            text("""
                                INSERT INTO items (sku, name, category, description, unit_price, quantity_on_hand, created_at)
                                VALUES (:sku, :name, :category, :description, :unit_price, :quantity, NOW())
                            """),
                            {
                                "sku": code,
                                "name": item.get('name', 'Unknown Item'),
                                "category": item.get('specifications', {}).get('category', 'General'),
                                "description": item.get('description') or item.get('name', 'No description'),
                                "unit_price": float(item.get('selling_price', 0)),
                                "quantity": 0
                            }
                        )
                        stats['inserted'] += 1

                    # Progress indicator
                    if idx % 100 == 0:
                        print(f"  ⏳ Processed {idx}/{len(items)} items...")

                except Exception as e:
                    print(f"  ❌ Error processing item {idx}: {str(e)}")
                    stats['errors'] += 1
                    continue

            # Commit all changes
            session.commit()

            print(f"\n✅ Items sync completed!")
            print(f"   📊 Statistics:")
            print(f"      - Inserted: {stats['inserted']}")
            print(f"      - Updated: {stats['updated']}")
            print(f"      - Errors: {stats['errors']}")

            return {"status": "success", "statistics": stats}

        except Exception as e:
            session.rollback()
            print(f"❌ Fatal error: {str(e)}")
            return {"status": "failed", "error": str(e)}

        finally:
            session.close()

    def sync_customers(self, limit: int = 100) -> Dict[str, Any]:
        """Sync customers from JSON to PostgreSQL (limited to 100 customers)"""
        print("\n" + "="*60)
        print(f"🔄 SYNCING CUSTOMERS TO POSTGRESQL (Limit: {limit})")
        print("="*60)

        customers = self.load_json_data("customers", limit=limit)

        if not customers:
            print("⚠️  No customers found in JSON data")
            return {"status": "skipped", "count": 0}

        print(f"👥 Found {len(customers)} customers in JSON data")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, customer in enumerate(customers, 1):
                try:
                    # Generate customer code
                    customer_code = customer.get('zoho_contact_id') or f"CUST_{idx:05d}"

                    # Check existing
                    result = session.execute(
                        text("SELECT id FROM customers WHERE customer_code = :code"),
                        {"code": customer_code}
                    ).fetchone()

                    if result:
                        # Update existing
                        session.execute(
                            text("""
                                UPDATE customers SET
                                    name = :name,
                                    company_name = :company,
                                    phone = :phone,
                                    email = :email,
                                    address = :address,
                                    updated_at = NOW()
                                WHERE customer_code = :code
                            """),
                            {
                                "name": customer.get('name') or customer.get('name_en', 'Unknown'),
                                "company": customer.get('company_name', ''),
                                "phone": customer.get('phone', ''),
                                "email": customer.get('email', ''),
                                "address": customer.get('address', ''),
                                "code": customer_code
                            }
                        )
                        stats['updated'] += 1
                    else:
                        # Insert new
                        session.execute(
                            text("""
                                INSERT INTO customers (
                                    customer_code, name, company_name, phone, email,
                                    address, is_active, created_at
                                )
                                VALUES (:code, :name, :company, :phone, :email, :address, true, NOW())
                            """),
                            {
                                "code": customer_code,
                                "name": customer.get('name') or customer.get('name_en', 'Unknown'),
                                "company": customer.get('company_name', ''),
                                "phone": customer.get('phone', ''),
                                "email": customer.get('email', ''),
                                "address": customer.get('address', '')
                            }
                        )
                        stats['inserted'] += 1

                    if idx % 50 == 0:
                        print(f"  ⏳ Processed {idx}/{len(customers)} customers...")

                except Exception as e:
                    print(f"  ❌ Error processing customer {idx}: {str(e)}")
                    stats['errors'] += 1
                    continue

            session.commit()

            print(f"\n✅ Customers sync completed!")
            print(f"   📊 Statistics:")
            print(f"      - Inserted: {stats['inserted']}")
            print(f"      - Updated: {stats['updated']}")
            print(f"      - Errors: {stats['errors']}")

            return {"status": "success", "statistics": stats}

        except Exception as e:
            session.rollback()
            print(f"❌ Fatal error: {str(e)}")
            return {"status": "failed", "error": str(e)}

        finally:
            session.close()

    def sync_vendors(self, limit: int = 100) -> Dict[str, Any]:
        """Sync vendors from JSON to PostgreSQL (limited to 100 vendors)"""
        print("\n" + "="*60)
        print(f"🔄 SYNCING VENDORS TO POSTGRESQL (Limit: {limit})")
        print("="*60)

        vendors = self.load_json_data("vendors", limit=limit)

        if not vendors:
            print("⚠️  No vendors found in JSON data")
            return {"status": "skipped", "count": 0}

        print(f"🏭 Found {len(vendors)} vendors in JSON data")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, vendor in enumerate(vendors, 1):
                try:
                    # Generate supplier code
                    supplier_code = vendor.get('zoho_vendor_id') or f"SUPP_{idx:05d}"

                    # Check existing
                    result = session.execute(
                        text("SELECT id FROM suppliers WHERE supplier_code = :code"),
                        {"code": supplier_code}
                    ).fetchone()

                    if result:
                        # Update existing
                        session.execute(
                            text("""
                                UPDATE suppliers SET
                                    name = :name,
                                    company_name = :company,
                                    phone = :phone,
                                    email = :email,
                                    address = :address,
                                    updated_at = NOW()
                                WHERE supplier_code = :code
                            """),
                            {
                                "name": vendor.get('name') or vendor.get('name_en', 'Unknown'),
                                "company": vendor.get('company_name', ''),
                                "phone": vendor.get('phone', ''),
                                "email": vendor.get('email', ''),
                                "address": vendor.get('address', ''),
                                "code": supplier_code
                            }
                        )
                        stats['updated'] += 1
                    else:
                        # Insert new
                        session.execute(
                            text("""
                                INSERT INTO suppliers (
                                    supplier_code, name, company_name, phone, email,
                                    address, is_active, created_at
                                )
                                VALUES (:code, :name, :company, :phone, :email, :address, true, NOW())
                            """),
                            {
                                "code": supplier_code,
                                "name": vendor.get('name') or vendor.get('name_en', 'Unknown'),
                                "company": vendor.get('company_name', ''),
                                "phone": vendor.get('phone', ''),
                                "email": vendor.get('email', ''),
                                "address": vendor.get('address', '')
                            }
                        )
                        stats['inserted'] += 1

                    if idx % 50 == 0:
                        print(f"  ⏳ Processed {idx}/{len(vendors)} vendors...")

                except Exception as e:
                    print(f"  ❌ Error processing vendor {idx}: {str(e)}")
                    stats['errors'] += 1
                    continue

            session.commit()

            print(f"\n✅ Vendors sync completed!")
            print(f"   📊 Statistics:")
            print(f"      - Inserted: {stats['inserted']}")
            print(f"      - Updated: {stats['updated']}")
            print(f"      - Errors: {stats['errors']}")

            return {"status": "success", "statistics": stats}

        except Exception as e:
            session.rollback()
            print(f"❌ Fatal error: {str(e)}")
            return {"status": "failed", "error": str(e)}

        finally:
            session.close()

    def verify_sync(self):
        """Verify synced data in database"""
        print("\n" + "="*60)
        print("🔍 VERIFYING SYNCED DATA")
        print("="*60)

        session = self.SessionLocal()

        try:
            # Count items
            items_count = session.execute(text("SELECT COUNT(*) FROM items")).scalar()
            print(f"📦 Items in database: {items_count}")

            # Count customers
            customers_count = session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
            print(f"👥 Customers in database: {customers_count}")

            # Count suppliers
            suppliers_count = session.execute(text("SELECT COUNT(*) FROM suppliers")).scalar()
            print(f"🏭 Suppliers in database: {suppliers_count}")

            # Show sample items
            print(f"\n📋 Sample Items:")
            items = session.execute(
                text("SELECT sku, name, unit_price FROM items LIMIT 5")
            ).fetchall()

            for item in items:
                print(f"   - {item[0]}: {item[1]} (${item[2]})")

        finally:
            session.close()


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("🚀 ZOHO BOOKS TO POSTGRESQL SYNC")
    print("="*60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Limits: 100 items (with images prioritized), 100 customers, 100 vendors")

    try:
        syncer = ZohoToPostgresSync()

        # Sync 100 items (prioritizing those with images)
        items_result = syncer.sync_items(limit=100)

        # Sync 100 customers
        customers_result = syncer.sync_customers(limit=100)

        # Sync 100 vendors
        vendors_result = syncer.sync_vendors(limit=100)

        # Verify
        syncer.verify_sync()

        print("\n" + "="*60)
        print("✅ SYNC COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
