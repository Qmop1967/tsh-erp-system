#!/usr/bin/env python3
"""
Zoho Items Comparison and Sync Script using Zoho MCP
====================================================

Compares Zoho items count with TSH ERP Ecosystem items count
and syncs missing items through Zoho MCP.

Author: TSH ERP Team
Date: November 8, 2025
"""

import os
import sys
import json
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

# Import Zoho infrastructure
from app.tds.integrations.zoho.auth import ZohoAuthManager, ZohoCredentials
from app.tds.integrations.zoho.client import UnifiedZohoClient, ZohoAPI
from app.core.events.event_bus import EventBus

# Load environment variables
load_dotenv()


def parse_database_url(url: str) -> URL:
    """
    Parse DATABASE_URL and properly decode URL-encoded components.
    """
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


class ZohoMCPClient:
    """Client for interacting with Zoho using UnifiedZohoClient (MCP-ready)"""
    
    def __init__(self, zoho_client: UnifiedZohoClient):
        self.zoho_client = zoho_client
    
    async def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items from Zoho with pagination"""
        all_items = []
        page = 1
        per_page = 200
        
        print(f"  📥 Fetching items from Zoho (page {page})...")
        
        while True:
            try:
                response = await self.zoho_client.get(
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
                print(f"     ✅ Fetched {len(items)} items (total: {len(all_items)})")
                
                # Check if there are more pages
                page_context = response.get("page_context", {})
                has_more = page_context.get("has_more_page", False)
                
                if not has_more:
                    break
                
                page += 1
                
            except Exception as e:
                print(f"  ❌ Error fetching page {page}: {e}")
                break
        
        return all_items
    
    async def get_item_details(self, item_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific item"""
        try:
            response = await self.zoho_client.get(
                ZohoAPI.INVENTORY,
                f"items/{item_id}"
            )
            return response.get("item", {})
        except Exception as e:
            raise Exception(f"Zoho API error getting item {item_id}: {e}")


class TSHERPItemsCounter:
    """Counter for TSH ERP Ecosystem items"""
    
    def __init__(self, db_url: str):
        db_url_parsed = parse_database_url(db_url)
        self.engine = create_engine(db_url_parsed)
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items from TSH ERP database"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    id,
                    zoho_item_id,
                    sku,
                    name,
                    is_active,
                    actual_available_stock
                FROM products
                WHERE zoho_item_id IS NOT NULL
                ORDER BY id
            """))
            
            items = []
            for row in result:
                items.append({
                    "id": row.id,
                    "zoho_item_id": row.zoho_item_id,
                    "sku": row.sku,
                    "name": row.name,
                    "is_active": row.is_active,
                    "stock": row.actual_available_stock or 0
                })
            
            return items
    
    def get_count(self) -> int:
        """Get total count of items synced from Zoho"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM products
                WHERE zoho_item_id IS NOT NULL
            """))
            row = result.fetchone()
            return row[0] if row else 0
    
    def get_zoho_item_ids(self) -> Set[str]:
        """Get set of all Zoho item IDs in database"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT zoho_item_id
                FROM products
                WHERE zoho_item_id IS NOT NULL
            """))
            return {str(row[0]) for row in result}


class ZohoItemSyncer:
    """Sync missing items from Zoho to TSH ERP"""
    
    def __init__(self, db_url: str, zoho_client: ZohoMCPClient):
        db_url_parsed = parse_database_url(db_url)
        self.engine = create_engine(db_url_parsed)
        self.zoho_client = zoho_client
    
    async def sync_item(self, zoho_item: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a single item from Zoho to TSH ERP"""
        item_id = zoho_item.get("item_id")
        if not item_id:
            return {"status": "error", "message": "Missing item_id"}
        
        try:
            # Get detailed item information
            item_details = await self.zoho_client.get_item_details(item_id)
            
            # Extract item data
            sku = item_details.get("sku") or item_details.get("code") or f"ZOHO_{item_id}"
            name = item_details.get("name") or "Unknown Item"
            description = item_details.get("description") or ""
            rate = float(item_details.get("rate", 0) or 0)
            stock_on_hand = float(item_details.get("stock_on_hand", 0) or 0)
            image_url = item_details.get("image_url") or item_details.get("image_name")
            
            # Check if item already exists
            with self.engine.connect() as conn:
                # Check by zoho_item_id
                existing = conn.execute(
                    text("SELECT id FROM products WHERE zoho_item_id = :zoho_id"),
                    {"zoho_id": str(item_id)}
                ).fetchone()
                
                if existing:
                    # Update existing item
                    conn.execute(
                        text("""
                            UPDATE products SET
                                sku = :sku,
                                name = :name,
                                description = :description,
                                price = :price,
                                actual_available_stock = :stock,
                                image_url = COALESCE(:image_url, image_url),
                                updated_at = NOW()
                            WHERE zoho_item_id = :zoho_id
                        """),
                        {
                            "zoho_id": str(item_id),
                            "sku": sku,
                            "name": name,
                            "description": description,
                            "price": rate,
                            "stock": stock_on_hand,
                            "image_url": image_url
                        }
                    )
                    conn.commit()
                    return {"status": "updated", "item_id": item_id, "sku": sku}
                else:
                    # Insert new item
                    # First, get or create a default category
                    category_result = conn.execute(
                        text("SELECT id FROM categories WHERE name = 'Uncategorized' LIMIT 1")
                    ).fetchone()
                    
                    if not category_result:
                        # Create default category
                        category_result = conn.execute(
                            text("""
                                INSERT INTO categories (name, is_active, created_at)
                                VALUES ('Uncategorized', true, NOW())
                                RETURNING id
                            """)
                        ).fetchone()
                        conn.commit()
                    
                    category_id = category_result[0]
                    
                    # Insert new product
                    conn.execute(
                        text("""
                            INSERT INTO products (
                                zoho_item_id, sku, name, description,
                                category_id, price, actual_available_stock,
                                image_url, is_active, created_at, updated_at
                            )
                            VALUES (
                                :zoho_id, :sku, :name, :description,
                                :category_id, :price, :stock,
                                :image_url, true, NOW(), NOW()
                            )
                        """),
                        {
                            "zoho_id": str(item_id),
                            "sku": sku,
                            "name": name,
                            "description": description,
                            "category_id": category_id,
                            "price": rate,
                            "stock": stock_on_hand,
                            "image_url": image_url
                        }
                    )
                    conn.commit()
                    return {"status": "inserted", "item_id": item_id, "sku": sku}
        
        except Exception as e:
            return {"status": "error", "item_id": item_id, "error": str(e)}


async def main():
    """Main comparison and sync function"""
    print("\n" + "="*70)
    print("🔄 ZOHO ITEMS COMPARISON AND SYNC")
    print("="*70)
    
    # Configuration
    db_url = os.getenv("DATABASE_URL")
    zoho_org_id = os.getenv("ZOHO_ORGANIZATION_ID", "748369814")
    
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    # Load Zoho credentials
    credentials = ZohoCredentials(
        client_id=os.getenv('ZOHO_CLIENT_ID'),
        client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
        refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
        organization_id=zoho_org_id
    )
    
    if not all([credentials.client_id, credentials.client_secret,
                credentials.refresh_token, credentials.organization_id]):
        print("❌ Missing Zoho credentials in environment variables")
        print("   Required: ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN, ZOHO_ORGANIZATION_ID")
        return
    
    print(f"\n📋 Configuration:")
    print(f"   Organization ID: {zoho_org_id}")
    print(f"   Database: Connected")
    
    # Initialize Zoho client
    event_bus = EventBus()
    auth_manager = ZohoAuthManager(credentials, auto_refresh=True, event_bus=event_bus)
    await auth_manager.start()
    
    zoho_client = UnifiedZohoClient(
        auth_manager=auth_manager,
        organization_id=zoho_org_id,
        rate_limit=100,
        event_bus=event_bus
    )
    await zoho_client.start_session()
    
    # Step 1: Get Zoho items count
    print("\n" + "-"*70)
    print("STEP 1: Fetching items from Zoho")
    print("-"*70)
    
    mcp_client = ZohoMCPClient(zoho_client)
    zoho_items = await mcp_client.get_all_items()
    zoho_count = len(zoho_items)
    zoho_item_ids = {str(item.get("item_id")) for item in zoho_items if item.get("item_id")}
    
    print(f"\n✅ Zoho Items:")
    print(f"   Total Count: {zoho_count}")
    print(f"   Unique Item IDs: {len(zoho_item_ids)}")
    
    # Step 2: Get TSH ERP items count
    print("\n" + "-"*70)
    print("STEP 2: Fetching items from TSH ERP Database")
    print("-"*70)
    
    tsh_counter = TSHERPItemsCounter(db_url)
    tsh_items = tsh_counter.get_all_items()
    tsh_count = len(tsh_items)
    tsh_item_ids = tsh_counter.get_zoho_item_ids()
    
    print(f"\n✅ TSH ERP Items:")
    print(f"   Total Count: {tsh_count}")
    print(f"   Unique Zoho Item IDs: {len(tsh_item_ids)}")
    
    # Step 3: Compare and identify differences
    print("\n" + "-"*70)
    print("STEP 3: Comparing Counts")
    print("-"*70)
    
    missing_in_tsh = zoho_item_ids - tsh_item_ids
    extra_in_tsh = tsh_item_ids - zoho_item_ids
    
    print(f"\n📊 Comparison Results:")
    print(f"   Zoho Items: {zoho_count}")
    print(f"   TSH ERP Items: {tsh_count}")
    print(f"   Difference: {zoho_count - tsh_count}")
    print(f"\n   Missing in TSH ERP: {len(missing_in_tsh)} items")
    print(f"   Extra in TSH ERP: {len(extra_in_tsh)} items")
    
    if missing_in_tsh:
        print(f"\n   Missing Item IDs (first 10): {list(missing_in_tsh)[:10]}")
    
    # Step 4: Sync missing items
    if missing_in_tsh:
        print("\n" + "-"*70)
        print("STEP 4: Syncing Missing Items")
        print("-"*70)
        
        # Create syncer
        syncer = ZohoItemSyncer(db_url, mcp_client)
        
        # Find missing items in Zoho data
        missing_items = [item for item in zoho_items 
                        if str(item.get("item_id")) in missing_in_tsh]
        
        print(f"\n🔄 Syncing {len(missing_items)} missing items...")
        
        stats = {"inserted": 0, "updated": 0, "errors": 0}
        
        for idx, zoho_item in enumerate(missing_items, 1):
            try:
                result = await syncer.sync_item(zoho_item)
                
                if result["status"] == "inserted":
                    stats["inserted"] += 1
                    print(f"   ✅ [{idx}/{len(missing_items)}] Inserted: {result.get('sku', 'N/A')}")
                elif result["status"] == "updated":
                    stats["updated"] += 1
                    print(f"   🔄 [{idx}/{len(missing_items)}] Updated: {result.get('sku', 'N/A')}")
                else:
                    stats["errors"] += 1
                    print(f"   ❌ [{idx}/{len(missing_items)}] Error: {result.get('error', 'Unknown')}")
                
                # Rate limiting - small delay
                if idx % 10 == 0:
                    await asyncio.sleep(1)
            
            except Exception as e:
                stats["errors"] += 1
                print(f"   ❌ [{idx}/{len(missing_items)}] Exception: {e}")
        
        print(f"\n✅ Sync Completed!")
        print(f"   📊 Statistics:")
        print(f"      - Inserted: {stats['inserted']}")
        print(f"      - Updated: {stats['updated']}")
        print(f"      - Errors: {stats['errors']}")
    else:
        print("\n✅ No missing items to sync. Everything is up to date!")
    
    # Cleanup
    await zoho_client.close_session()
    if auth_manager._refresh_task:
        auth_manager._refresh_task.cancel()
    
    # Final summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    print(f"   Zoho Items: {zoho_count}")
    print(f"   TSH ERP Items: {tsh_count}")
    print(f"   Missing Items: {len(missing_in_tsh)}")
    print(f"   Extra Items: {len(extra_in_tsh)}")
    print(f"   Sync Status: {'✅ Complete' if not missing_in_tsh else '⚠️  Partial'}")
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

