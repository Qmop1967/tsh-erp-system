# Zoho Sync Operation Templates

**Purpose:** Production-ready Zoho sync patterns via TDS Core for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/zoho-sync.md

---

## 🔄 Template 3.1: Sync Products from Zoho (via TDS Core)

**Reasoning Context:**
- NEVER access Zoho Books/Inventory APIs directly
- TDS Core orchestrates ALL Zoho operations (rate limiting, error handling, retry logic)
- Zoho data comes from BOTH Books AND Inventory
- Current phase: Migration Phase 1 (read-only from Zoho)
- Sync operations must be idempotent (safe to run multiple times)

**When to Use:**
- Scheduled product sync (every 15 minutes)
- Manual sync trigger
- Initial data import
- Sync after Zoho changes

**Code Template:**

```python
# tds_core/services/zoho_product_sync.py
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from tds_core.clients.zoho_client import ZohoInventoryClient
from app.models.product import Product
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class ZohoProductSyncService:
    """
    Service to sync products from Zoho Inventory to TSH ERP.

    CRITICAL: Always use TDS Core's ZohoClient (never direct API calls).
    Phase 1: Read-only (pull data from Zoho, don't write back).
    """

    def __init__(self):
        self.zoho_client = ZohoInventoryClient()  # 👈 TDS Core client
        self.db = SessionLocal()

    def sync_products(self) -> Dict[str, int]:
        """
        Sync all products from Zoho Inventory.

        Returns:
            Dict with counts: {created: X, updated: Y, errors: Z}
        """
        stats = {"created": 0, "updated": 0, "errors": 0, "skipped": 0}

        try:
            # Fetch products from Zoho Inventory via TDS Core
            logger.info("Fetching products from Zoho Inventory...")
            zoho_products = self.zoho_client.get_all_items()  # Handles pagination

            logger.info(f"Found {len(zoho_products)} products in Zoho")

            for zoho_product in zoho_products:
                try:
                    self._sync_single_product(zoho_product, stats)
                except Exception as e:
                    logger.error(f"Error syncing product {zoho_product.get('item_id')}: {e}")
                    stats["errors"] += 1

            self.db.commit()
            logger.info(f"Sync complete: {stats}")

        except Exception as e:
            logger.error(f"Zoho product sync failed: {e}")
            self.db.rollback()
            stats["errors"] = -1  # Indicates full sync failure

        finally:
            self.db.close()

        return stats

    def _sync_single_product(self, zoho_product: Dict, stats: Dict):
        """Sync a single product (idempotent operation)."""

        zoho_item_id = zoho_product.get("item_id")

        if not zoho_item_id:
            logger.warning("Product missing item_id, skipping")
            stats["skipped"] += 1
            return

        # Find existing product by Zoho ID
        product = self.db.query(Product).filter(
            Product.zoho_item_id == zoho_item_id
        ).first()

        # Map Zoho fields to TSH ERP fields
        product_data = {
            "zoho_item_id": zoho_item_id,
            "name": zoho_product.get("name", ""),
            "name_ar": zoho_product.get("name"),  # Default to English if Arabic missing
            "description": zoho_product.get("description", ""),
            "description_ar": zoho_product.get("description", ""),
            "sku": zoho_product.get("sku"),
            "unit_price": float(zoho_product.get("rate", 0)),
            "cost_price": float(zoho_product.get("purchase_rate", 0)),
            "stock_quantity": int(zoho_product.get("stock_on_hand", 0)),
            "is_active": zoho_product.get("status") == "active",
            "zoho_last_synced_at": datetime.utcnow()
        }

        if product:
            # Update existing product
            for key, value in product_data.items():
                setattr(product, key, value)
            stats["updated"] += 1
            logger.debug(f"Updated product: {product.name}")
        else:
            # Create new product
            product = Product(**product_data)
            self.db.add(product)
            stats["created"] += 1
            logger.debug(f"Created product: {product_data['name']}")
```

**Database Model Update:**

```python
# app/models/product.py
# Add Zoho sync tracking fields:

zoho_item_id = Column(String(100), unique=True, index=True, nullable=True)
zoho_last_synced_at = Column(DateTime(timezone=True), nullable=True)
```

**Scheduled Sync Job:**

```python
# tds_core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from tds_core.services.zoho_product_sync import ZohoProductSyncService

scheduler = BackgroundScheduler()

def sync_products_job():
    """Scheduled job to sync products every 15 minutes."""
    sync_service = ZohoProductSyncService()
    stats = sync_service.sync_products()

    if stats["errors"] > 0:
        logger.warning(f"Product sync completed with {stats['errors']} errors")
    else:
        logger.info(f"Product sync successful: {stats}")

# Schedule: Every 15 minutes
scheduler.add_job(
    sync_products_job,
    trigger="interval",
    minutes=15,
    id="zoho_product_sync",
    replace_existing=True
)

scheduler.start()
```

**Customization Points:**
- Adjust sync frequency (15 minutes is current setting)
- Add error notifications (email/SMS on sync failure)
- Implement incremental sync (only changed products)
- Add conflict resolution logic (what if both systems changed same product)

**Related Patterns:**
- Error handling: @docs/reference/code-templates/error-handling.md
- TDS Core architecture: @docs/TDS_MASTER_ARCHITECTURE.md
- Database optimization: @docs/reference/code-templates/database-optimization.md

---

## 🚨 Critical Rules for Zoho Operations

```yaml
NEVER:
❌ Access Zoho APIs directly (use TDS Core)
❌ Write to Zoho in Phase 1 (read-only)
❌ Skip error handling for Zoho operations
❌ Forget to log sync results

ALWAYS:
✅ Route through TDS Core
✅ Implement idempotent operations
✅ Log all sync activities
✅ Handle Zoho API errors gracefully
✅ Track sync timestamps
✅ Use transactions for data integrity
```

---

**Related Documentation:**
- TDS Core architecture: @docs/TDS_MASTER_ARCHITECTURE.md
- Zoho migration phases: @docs/core/project-context.md
- Error handling: @docs/reference/code-templates/error-handling.md
