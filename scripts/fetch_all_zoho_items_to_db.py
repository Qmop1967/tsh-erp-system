#!/usr/bin/env python3
"""
Fetch All Zoho Items to TSH ERP Database
========================================

Fetches all items from Zoho using MCP and syncs them to PostgreSQL database.
Avoids duplicates by checking zoho_item_id.

Author: TSH ERP Team
Date: November 8, 2025
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from urllib.parse import urlparse, unquote

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, URL
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def parse_database_url(url: str) -> URL:
    """Parse DATABASE_URL and properly decode URL-encoded components."""
    parsed = urlparse(url)
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    
    return URL.create(
        drivername=parsed.scheme,
        username=username,
        password=password,
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/')
    )


class ZohoItemsFetcher:
    """Fetches all items from Zoho using MCP functions"""
    
    def __init__(self, organization_id: str):
        self.organization_id = organization_id
    
    async def fetch_all_items(self) -> List[Dict[str, Any]]:
        """
        Fetch all items from Zoho Inventory using MCP
        Note: This simulates MCP calls - in actual implementation,
        you would call MCP functions directly from Cursor/Claude
        """
        # For now, we'll use the existing Zoho client infrastructure
        # In production, this could be replaced with direct MCP calls
        from app.tds.integrations.zoho.auth import ZohoAuthManager, ZohoCredentials
        from app.tds.integrations.zoho.client import UnifiedZohoClient, ZohoAPI
        from app.core.events.event_bus import EventBus
        
        # Load credentials
        credentials = ZohoCredentials(
            client_id=os.getenv('ZOHO_CLIENT_ID'),
            client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
            refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
            organization_id=self.organization_id
        )
        
        if not all([credentials.client_id, credentials.client_secret,
                    credentials.refresh_token, credentials.organization_id]):
            raise ValueError("Missing Zoho credentials")
        
        # Initialize client
        event_bus = EventBus()
        auth_manager = ZohoAuthManager(credentials, auto_refresh=True, event_bus=event_bus)
        await auth_manager.start()
        
        zoho_client = UnifiedZohoClient(
            auth_manager=auth_manager,
            organization_id=self.organization_id,
            rate_limit=100,
            event_bus=event_bus
        )
        await zoho_client.start_session()
        
        try:
            all_items = []
            page = 1
            per_page = 200
            
            print(f"  📥 Fetching items from Zoho Inventory...")
            
            while True:
                try:
                    response = await zoho_client.get(
                        ZohoAPI.INVENTORY,
                        "items",
                        params={
                            "page": page,
                            "per_page": per_page
                        }
                    )
                    
                    items = response.get("items", [])
                    
                    if not items:
                        break
                    
                    all_items.extend(items)
                    print(f"     ✅ Page {page}: Fetched {len(items)} items (total: {len(all_items)})")
                    
                    # Check if there are more pages
                    page_context = response.get("page_context", {})
                    has_more = page_context.get("has_more_page", False)
                    
                    if not has_more:
                        break
                    
                    page += 1
                    
                    # Rate limiting - small delay between pages
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ❌ Error fetching page {page}: {e}")
                    break
            
            return all_items
        
        finally:
            await zoho_client.close_session()
            if auth_manager._refresh_task:
                auth_manager._refresh_task.cancel()


class DatabaseSyncer:
    """Syncs items to PostgreSQL database, avoiding duplicates"""
    
    def __init__(self, db_url: str, organization_id: str):
        db_url_parsed = parse_database_url(db_url)
        self.engine = create_engine(db_url_parsed)
        self.organization_id = organization_id
    
    def get_existing_zoho_ids(self) -> Set[str]:
        """Get set of all existing Zoho item IDs in database"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT zoho_item_id
                FROM products
                WHERE zoho_item_id IS NOT NULL
            """))
            return {str(row[0]) for row in result}
    
    def get_or_create_category(self, category_name: Optional[str], conn) -> int:
        """Get or create category and return its ID"""
        if not category_name or category_name.strip() == "":
            category_name = "Uncategorized"
        
        # Check if category exists
        result = conn.execute(
            text("SELECT id FROM categories WHERE name = :name LIMIT 1"),
            {"name": category_name}
        ).fetchone()
        
        if result:
            return result[0]
        
        # Create new category
        result = conn.execute(
            text("""
                INSERT INTO categories (name, is_active, created_at)
                VALUES (:name, true, NOW())
                RETURNING id
            """),
            {"name": category_name}
        ).fetchone()
        conn.commit()
        
        return result[0]
    
    def sync_item(self, zoho_item: Dict[str, Any], existing_ids: Set[str]) -> Dict[str, Any]:
        """Sync a single item to database"""
        item_id = str(zoho_item.get("item_id", ""))
        if not item_id:
            return {"status": "error", "message": "Missing item_id"}
        
        try:
            with self.engine.connect() as conn:
                # Extract item data
                sku = zoho_item.get("sku") or zoho_item.get("code") or f"ZOHO_{item_id}"
                name = zoho_item.get("name") or "Unknown Item"
                description = zoho_item.get("description") or ""
                rate = float(zoho_item.get("rate", 0) or 0)
                purchase_rate = float(zoho_item.get("purchase_rate", 0) or 0)
                stock_on_hand = float(zoho_item.get("available_stock", 0) or 
                                     zoho_item.get("actual_available_stock", 0) or 0)
                image_name = zoho_item.get("image_name")
                category_name = zoho_item.get("category_name") or ""
                status = zoho_item.get("status", "active")
                is_active = status.lower() == "active"
                
                # Get or create category
                category_id = self.get_or_create_category(category_name, conn)
                
                # Build image URL if image_name exists
                image_url = None
                if image_name:
                    # Zoho image URL format
                    image_url = f"https://www.zohoapis.com/inventory/v1/items/{item_id}/image?organization_id={self.organization_id}"
                
                # Check if item exists
                is_new = item_id not in existing_ids
                
                if is_new:
                    # Insert new item
                    conn.execute(
                        text("""
                            INSERT INTO products (
                                zoho_item_id, sku, name, description,
                                category_id, price, cost_price,
                                actual_available_stock, image_url,
                                is_active, created_at, updated_at
                            )
                            VALUES (
                                :zoho_id, :sku, :name, :description,
                                :category_id, :price, :cost_price,
                                :stock, :image_url, :is_active, NOW(), NOW()
                            )
                        """),
                        {
                            "zoho_id": item_id,
                            "sku": sku,
                            "name": name,
                            "description": description,
                            "category_id": category_id,
                            "price": rate,
                            "cost_price": purchase_rate if purchase_rate > 0 else None,
                            "stock": stock_on_hand,
                            "image_url": image_url,
                            "is_active": is_active
                        }
                    )
                    conn.commit()
                    return {"status": "inserted", "item_id": item_id, "sku": sku}
                else:
                    # Update existing item
                    conn.execute(
                        text("""
                            UPDATE products SET
                                sku = :sku,
                                name = :name,
                                description = :description,
                                category_id = :category_id,
                                price = :price,
                                cost_price = :cost_price,
                                actual_available_stock = :stock,
                                image_url = COALESCE(:image_url, image_url),
                                is_active = :is_active,
                                updated_at = NOW()
                            WHERE zoho_item_id = :zoho_id
                        """),
                        {
                            "zoho_id": item_id,
                            "sku": sku,
                            "name": name,
                            "description": description,
                            "category_id": category_id,
                            "price": rate,
                            "cost_price": purchase_rate if purchase_rate > 0 else None,
                            "stock": stock_on_hand,
                            "image_url": image_url,
                            "is_active": is_active
                        }
                    )
                    conn.commit()
                    return {"status": "updated", "item_id": item_id, "sku": sku}
        
        except Exception as e:
            return {"status": "error", "item_id": item_id, "error": str(e)}
    
    def sync_all_items(self, zoho_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync all items to database"""
        print("\n" + "-"*70)
        print("STEP 2: Syncing Items to Database")
        print("-"*70)
        
        # Get existing Zoho item IDs
        print("  🔍 Checking existing items in database...")
        existing_ids = self.get_existing_zoho_ids()
        print(f"     ✅ Found {len(existing_ids)} existing items")
        
        # Statistics
        stats = {
            "total": len(zoho_items),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "errors_list": []
        }
        
        print(f"\n  🔄 Syncing {stats['total']} items...")
        
        for idx, zoho_item in enumerate(zoho_items, 1):
            try:
                result = self.sync_item(zoho_item, existing_ids)
                
                if result["status"] == "inserted":
                    stats["inserted"] += 1
                    if idx % 50 == 0 or idx <= 10:
                        print(f"     ✅ [{idx}/{stats['total']}] Inserted: {result.get('sku', 'N/A')}")
                elif result["status"] == "updated":
                    stats["updated"] += 1
                    if idx % 50 == 0 or idx <= 10:
                        print(f"     🔄 [{idx}/{stats['total']}] Updated: {result.get('sku', 'N/A')}")
                elif result["status"] == "error":
                    stats["errors"] += 1
                    stats["errors_list"].append({
                        "item_id": result.get("item_id"),
                        "error": result.get("error")
                    })
                    if idx <= 10 or stats["errors"] <= 5:
                        print(f"     ❌ [{idx}/{stats['total']}] Error: {result.get('error', 'Unknown')}")
                else:
                    stats["skipped"] += 1
                
            except Exception as e:
                stats["errors"] += 1
                stats["errors_list"].append({
                    "item_id": zoho_item.get("item_id"),
                    "error": str(e)
                })
                if stats["errors"] <= 5:
                    print(f"     ❌ [{idx}/{stats['total']}] Exception: {e}")
        
        return stats


async def main():
    """Main function to fetch and sync all items"""
    print("\n" + "="*70)
    print("🔄 FETCH ALL ZOHO ITEMS TO TSH ERP DATABASE")
    print("="*70)
    
    # Configuration
    db_url = os.getenv("DATABASE_URL")
    zoho_org_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")
    
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    print(f"\n📋 Configuration:")
    print(f"   Organization ID: {zoho_org_id}")
    print(f"   Database: Connected")
    
    # Step 1: Fetch all items from Zoho
    print("\n" + "-"*70)
    print("STEP 1: Fetching All Items from Zoho")
    print("-"*70)
    
    fetcher = ZohoItemsFetcher(zoho_org_id)
    zoho_items = await fetcher.fetch_all_items()
    
    if not zoho_items:
        print("⚠️  No items found in Zoho")
        return
    
    print(f"\n✅ Fetched {len(zoho_items)} items from Zoho")
    
    # Step 2: Sync to database
    syncer = DatabaseSyncer(db_url, zoho_org_id)
    stats = syncer.sync_all_items(zoho_items)
    
    # Final summary
    print("\n" + "="*70)
    print("📊 SYNC SUMMARY")
    print("="*70)
    print(f"   Total Items Fetched: {stats['total']}")
    print(f"   ✅ Inserted (New): {stats['inserted']}")
    print(f"   🔄 Updated (Existing): {stats['updated']}")
    print(f"   ⏭️  Skipped: {stats['skipped']}")
    print(f"   ❌ Errors: {stats['errors']}")
    
    if stats['errors'] > 0 and stats['errors_list']:
        print(f"\n   ⚠️  Error Details (first 5):")
        for error in stats['errors_list'][:5]:
            print(f"      - Item {error.get('item_id')}: {error.get('error')}")
    
    # Verify final count
    final_count = syncer.get_existing_zoho_ids()
    print(f"\n   📊 Final Database Count: {len(final_count)} items")
    print(f"   📈 Success Rate: {((stats['inserted'] + stats['updated']) / stats['total'] * 100):.1f}%")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

