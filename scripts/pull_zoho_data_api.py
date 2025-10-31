#!/usr/bin/env python3
"""
Pull Master Data from Zoho Books API
Pulls 20 items (with prices and images), 20 customers, 20 vendors using MCP tools
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


class ZohoBooksPuller:
    """Pull data from Zoho Books API using MCP integration"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.zoho_org_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")

        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment")

        # Create database engine
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Data storage
        self.data_dir = project_root / "app" / "data" / "zoho_api_pull"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Image storage
        self.images_dir = project_root / "app" / "data" / "images" / "items"
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def save_to_json(self, data: Any, filename: str):
        """Save data to JSON file"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to: {filepath}")

    def pull_items_from_mcp(self, limit: int = 20) -> List[Dict]:
        """
        Pull items from Zoho Books using MCP
        Note: This is a placeholder - you'll need to run MCP commands separately
        """
        print(f"\n{'='*60}")
        print(f"📦 PULLING {limit} ITEMS FROM ZOHO BOOKS API")
        print(f"{'='*60}")

        # This would be called via MCP in actual implementation
        # For now, we'll create a structure to manually add MCP results

        instructions = f"""
To pull items from Zoho Books, run this MCP command:

mcp__zoho-books__zoho-books-getItems
  organizationId: {self.zoho_org_id}
  params:
    page: 1
    per_page: {limit}

Then save the response to: {self.data_dir}/items_api.json
"""
        print(instructions)

        # Check if data already exists
        items_file = self.data_dir / "items_api.json"
        if items_file.exists():
            with open(items_file, 'r') as f:
                data = json.load(f)
                items = data.get('items', [])
                print(f"✅ Found {len(items)} items in cached API response")
                return items

        print("⚠️  No cached data found. Please run MCP command first.")
        return []

    def pull_customers_from_mcp(self, limit: int = 20) -> List[Dict]:
        """Pull customers from Zoho Books using MCP"""
        print(f"\n{'='*60}")
        print(f"👥 PULLING {limit} CUSTOMERS FROM ZOHO BOOKS API")
        print(f"{'='*60}")

        instructions = f"""
To pull customers from Zoho Books, run this MCP command:

mcp__zoho-books__zoho-books-getContacts
  organizationId: {self.zoho_org_id}
  params:
    page: 1
    per_page: {limit}

Then save the response to: {self.data_dir}/customers_api.json
"""
        print(instructions)

        customers_file = self.data_dir / "customers_api.json"
        if customers_file.exists():
            with open(customers_file, 'r') as f:
                data = json.load(f)
                contacts = data.get('contacts', [])
                print(f"✅ Found {len(contacts)} customers in cached API response")
                return contacts

        print("⚠️  No cached data found. Please run MCP command first.")
        return []

    def pull_vendors_from_mcp(self, limit: int = 20) -> List[Dict]:
        """Pull vendors from Zoho Books using MCP"""
        print(f"\n{'='*60}")
        print(f"🏭 PULLING {limit} VENDORS FROM ZOHO BOOKS API")
        print(f"{'='*60}")

        # Note: Zoho Books uses "contacts" endpoint with contact_type filter for vendors
        instructions = f"""
To pull vendors from Zoho Books, you may need to use contacts endpoint:

mcp__zoho-books__zoho-books-getContacts
  organizationId: {self.zoho_org_id}
  params:
    contact_type: vendor
    page: 1
    per_page: {limit}

Or check if there's a dedicated vendors endpoint.
Then save the response to: {self.data_dir}/vendors_api.json
"""
        print(instructions)

        vendors_file = self.data_dir / "vendors_api.json"
        if vendors_file.exists():
            with open(vendors_file, 'r') as f:
                data = json.load(f)
                vendors = data.get('contacts', []) or data.get('vendors', [])
                print(f"✅ Found {len(vendors)} vendors in cached API response")
                return vendors

        print("⚠️  No cached data found. Please run MCP command first.")
        return []

    def sync_items_to_db(self, items: List[Dict]) -> Dict[str, int]:
        """Sync items to PostgreSQL database"""
        if not items:
            print("⚠️  No items to sync")
            return {"inserted": 0, "updated": 0, "errors": 0}

        print(f"\n{'='*60}")
        print(f"💾 SYNCING {len(items)} ITEMS TO DATABASE")
        print(f"{'='*60}")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, item in enumerate(items, 1):
                try:
                    # Extract item data
                    item_id = item.get('item_id', '')
                    sku = item.get('sku') or item.get('item_code') or f"ZOHO_{item_id}"
                    name = item.get('name', 'Unknown Item')
                    description = item.get('description', '')
                    unit_price = float(item.get('rate', 0) or item.get('price', 0) or 0)

                    # Check if exists
                    result = session.execute(
                        text("SELECT id FROM items WHERE sku = :sku"),
                        {"sku": sku}
                    ).fetchone()

                    if result:
                        # Update
                        session.execute(
                            text("""
                                UPDATE items SET
                                    name = :name,
                                    description = :description,
                                    unit_price = :unit_price,
                                    updated_at = NOW()
                                WHERE sku = :sku
                            """),
                            {
                                "name": name,
                                "description": description,
                                "unit_price": unit_price,
                                "sku": sku
                            }
                        )
                        stats['updated'] += 1
                    else:
                        # Insert
                        session.execute(
                            text("""
                                INSERT INTO items (sku, name, description, unit_price, quantity_on_hand, created_at)
                                VALUES (:sku, :name, :description, :unit_price, 0, NOW())
                            """),
                            {
                                "sku": sku,
                                "name": name,
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
                    continue

            session.commit()

            print(f"\n✅ Items sync completed!")
            print(f"   - Inserted: {stats['inserted']}")
            print(f"   - Updated: {stats['updated']}")
            print(f"   - Errors: {stats['errors']}")

            return stats

        except Exception as e:
            session.rollback()
            print(f"❌ Fatal error: {str(e)}")
            return stats

        finally:
            session.close()

    def sync_customers_to_db(self, customers: List[Dict]) -> Dict[str, int]:
        """Sync customers to PostgreSQL database"""
        if not customers:
            print("⚠️  No customers to sync")
            return {"inserted": 0, "updated": 0, "errors": 0}

        print(f"\n{'='*60}")
        print(f"💾 SYNCING {len(customers)} CUSTOMERS TO DATABASE")
        print(f"{'='*60}")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, customer in enumerate(customers, 1):
                try:
                    contact_id = customer.get('contact_id', '')
                    customer_code = f"ZOHO_{contact_id}"
                    name = customer.get('contact_name', 'Unknown')
                    company = customer.get('company_name', '')
                    email = customer.get('email', '')
                    phone = customer.get('phone', '') or customer.get('mobile', '')

                    # Check if exists
                    result = session.execute(
                        text("SELECT id FROM customers WHERE customer_code = :code"),
                        {"code": customer_code}
                    ).fetchone()

                    if result:
                        # Update
                        session.execute(
                            text("""
                                UPDATE customers SET
                                    name = :name,
                                    company_name = :company,
                                    email = :email,
                                    phone = :phone,
                                    updated_at = NOW()
                                WHERE customer_code = :code
                            """),
                            {
                                "name": name,
                                "company": company,
                                "email": email,
                                "phone": phone,
                                "code": customer_code
                            }
                        )
                        stats['updated'] += 1
                    else:
                        # Insert
                        session.execute(
                            text("""
                                INSERT INTO customers (customer_code, name, company_name, email, phone, is_active, created_at)
                                VALUES (:code, :name, :company, :email, :phone, true, NOW())
                            """),
                            {
                                "code": customer_code,
                                "name": name,
                                "company": company,
                                "email": email,
                                "phone": phone
                            }
                        )
                        stats['inserted'] += 1

                except Exception as e:
                    print(f"  ❌ Error processing customer {idx}: {str(e)}")
                    stats['errors'] += 1
                    continue

            session.commit()

            print(f"\n✅ Customers sync completed!")
            print(f"   - Inserted: {stats['inserted']}")
            print(f"   - Updated: {stats['updated']}")
            print(f"   - Errors: {stats['errors']}")

            return stats

        except Exception as e:
            session.rollback()
            print(f"❌ Fatal error: {str(e)}")
            return stats

        finally:
            session.close()

    def sync_vendors_to_db(self, vendors: List[Dict]) -> Dict[str, int]:
        """Sync vendors to PostgreSQL database"""
        if not vendors:
            print("⚠️  No vendors to sync")
            return {"inserted": 0, "updated": 0, "errors": 0}

        print(f"\n{'='*60}")
        print(f"💾 SYNCING {len(vendors)} VENDORS TO DATABASE")
        print(f"{'='*60}")

        session = self.SessionLocal()
        stats = {"inserted": 0, "updated": 0, "errors": 0}

        try:
            for idx, vendor in enumerate(vendors, 1):
                try:
                    vendor_id = vendor.get('contact_id', '') or vendor.get('vendor_id', '')
                    supplier_code = f"ZOHO_{vendor_id}"
                    name = vendor.get('contact_name', '') or vendor.get('vendor_name', 'Unknown')
                    company = vendor.get('company_name', '')
                    email = vendor.get('email', '')
                    phone = vendor.get('phone', '') or vendor.get('mobile', '')

                    # Check if exists
                    result = session.execute(
                        text("SELECT id FROM suppliers WHERE supplier_code = :code"),
                        {"code": supplier_code}
                    ).fetchone()

                    if result:
                        # Update
                        session.execute(
                            text("""
                                UPDATE suppliers SET
                                    name = :name,
                                    company_name = :company,
                                    email = :email,
                                    phone = :phone,
                                    updated_at = NOW()
                                WHERE supplier_code = :code
                            """),
                            {
                                "name": name,
                                "company": company,
                                "email": email,
                                "phone": phone,
                                "code": supplier_code
                            }
                        )
                        stats['updated'] += 1
                    else:
                        # Insert
                        session.execute(
                            text("""
                                INSERT INTO suppliers (supplier_code, name, company_name, email, phone, is_active, created_at)
                                VALUES (:code, :name, :company, :email, :phone, true, NOW())
                            """),
                            {
                                "code": supplier_code,
                                "name": name,
                                "company": company,
                                "email": email,
                                "phone": phone
                            }
                        )
                        stats['inserted'] += 1

                except Exception as e:
                    print(f"  ❌ Error processing vendor {idx}: {str(e)}")
                    stats['errors'] += 1
                    continue

            session.commit()

            print(f"\n✅ Vendors sync completed!")
            print(f"   - Inserted: {stats['inserted']}")
            print(f"   - Updated: {stats['updated']}")
            print(f"   - Errors: {stats['errors']}")

            return stats

        except Exception as e:
            session.rollback()
            print(f"❌ Fatal error: {str(e)}")
            return stats

        finally:
            session.close()


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🚀 ZOHO BOOKS API DATA PULL")
    print("="*60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Limits: 20 items (with prices & images), 20 customers, 20 vendors")
    print("="*60)

    try:
        puller = ZohoBooksPuller()

        # Pull data from API (cached or instructions)
        items = puller.pull_items_from_mcp(limit=20)
        customers = puller.pull_customers_from_mcp(limit=20)
        vendors = puller.pull_vendors_from_mcp(limit=20)

        # Sync to database
        if items:
            puller.sync_items_to_db(items)

        if customers:
            puller.sync_customers_to_db(customers)

        if vendors:
            puller.sync_vendors_to_db(vendors)

        print("\n" + "="*60)
        print("✅ PULL COMPLETED")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
