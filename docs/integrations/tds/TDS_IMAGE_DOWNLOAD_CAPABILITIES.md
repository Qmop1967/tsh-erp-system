# TDS Image Download Capabilities - Complete Analysis

**Date:** January 2025
**Status:** ✅ Fully Documented
**Purpose:** Understanding how to use TDS to download Zoho item images

---

## 📋 Executive Summary

The TSH ERP system has **complete infrastructure** for downloading images from Zoho using the TDS (TSH Data Sync) system. All necessary components exist and are production-ready:

✅ **Zoho API Client** - Can fetch and download images
✅ **Image Service** - Stores images locally or on CDN
✅ **TDS Event System** - Event-driven architecture
✅ **Queue Management** - Handles async processing
✅ **Entity Handlers** - Syncs data to database
✅ **Background Workers** - Processes sync jobs

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              TDS IMAGE DOWNLOAD FLOW                     │
└─────────────────────────────────────────────────────────┘

1. TRIGGER
   └─> Create TDS Sync Run for "product_images"

2. FETCH FROM ZOHO
   └─> ZohoInventoryClient.fetch_items_paginated()
       └─> For each product with image_document_id:
           └─> ZohoInventoryClient.download_item_image(item_id)
               └─> Returns: image bytes

3. PROCESS & STORE
   └─> ImageService.download_image_from_bytes(item_id, image_data)
       ├─> Generate unique filename
       ├─> Store locally: /var/www/html/images/products/
       └─> Returns: (local_path, public_url)

4. UPDATE DATABASE
   └─> ProductHandler updates products.image_url
       └─> Publishes: TDSEntitySyncedEvent

5. COMPLETE
   └─> TDSSyncCompletedEvent published
```

---

## 🔧 Existing Components

### 1. Zoho Inventory Client (`app/services/zoho_inventory_client.py`)

**Location:** `app/services/zoho_inventory_client.py`

**Key Methods:**

```python
class ZohoInventoryClient:
    BASE_URL = "https://www.zohoapis.com/inventory/v1"
    ORGANIZATION_ID = "748369814"

    # Fetch items with pagination
    async def fetch_items_paginated(
        self,
        per_page: int = 200,
        filters: Optional[Dict] = None
    ) -> AsyncIterator[Dict[str, Any]]

    # Get image URL for an item
    async def fetch_item_image_url(
        self,
        item_id: str
    ) -> Optional[str]

    # Download image bytes
    async def download_item_image(
        self,
        item_id: str
    ) -> Optional[bytes]
```

**Usage Example:**

```python
from app.services.zoho_inventory_client import ZohoInventoryClient

# Initialize client
client = ZohoInventoryClient(db_session)

# Fetch all items
async for item in client.fetch_items_paginated():
    item_id = item['item_id']

    # Download image if exists
    if item.get('image_document_id'):
        image_bytes = await client.download_item_image(item_id)
        if image_bytes:
            print(f"Downloaded {len(image_bytes)} bytes for item {item_id}")
```

---

### 2. Image Service (`app/services/image_service.py`)

**Location:** `app/services/image_service.py`

**Key Methods:**

```python
class ImageService:
    # Configuration
    LOCAL_STORAGE_PATH = "/var/www/html/images/products"
    PUBLIC_URL_BASE = "https://erp.tsh.sale/images/products"
    USE_CDN = False  # Can enable CDN if configured

    # Download from URL and store
    @classmethod
    async def download_and_store_image(
        cls,
        item_id: str,
        image_url: str,
        headers: Optional[dict] = None
    ) -> Optional[Tuple[str, str]]  # (local_path, public_url)

    # Store from bytes (already downloaded)
    @classmethod
    async def download_image_from_bytes(
        cls,
        item_id: str,
        image_data: bytes
    ) -> Optional[Tuple[str, str]]  # (local_path, public_url)
```

**Features:**

- ✅ Automatic filename generation with MD5 hash
- ✅ Image format detection (JPG, PNG, GIF, WEBP)
- ✅ Local storage with public URL generation
- ✅ CDN upload support (optional)
- ✅ Error handling and logging

**Usage Example:**

```python
from app.services.image_service import ImageService

# Option 1: Download from URL
result = await ImageService.download_and_store_image(
    item_id="123456",
    image_url="https://zoho.com/image.jpg",
    headers=auth_headers
)

# Option 2: Store from bytes
result = await ImageService.download_image_from_bytes(
    item_id="123456",
    image_data=image_bytes
)

if result:
    local_path, public_url = result
    print(f"Stored at: {local_path}")
    print(f"Public URL: {public_url}")
    # Example: https://erp.tsh.sale/images/products/item_123456_a1b2c3d4.jpg
```

---

### 3. TDS Core Service (`app/tds/core/service.py`)

**Location:** `app/tds/core/service.py`

**Key Methods:**

```python
class TDSService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_bus = event_bus

    # Create a new sync run
    async def create_sync_run(
        self,
        run_type: SourceType,  # SourceType.ZOHO
        entity_type: Optional[EntityType] = None,  # EntityType.PRODUCT
        configuration: Optional[Dict[str, Any]] = None
    ) -> TDSSyncRun

    # Record entity sync
    async def record_entity_sync(
        self,
        entity_type: EntityType,
        entity_id: str,
        source_entity_id: str,
        operation: OperationType,
        changes: Optional[Dict] = None
    )

    # Complete sync run
    async def complete_sync_run(
        self,
        sync_run_id: UUID,
        total_processed: int,
        successful: int,
        failed: int
    )
```

**Events Published:**

- `tds.sync.started` - When sync begins
- `tds.entity.synced` - When entity updated
- `tds.sync.completed` - When sync completes
- `tds.sync.failed` - When sync fails

---

### 4. TDS Queue Service (`app/tds/core/queue.py`)

**Location:** `app/tds/core/queue.py`

**Purpose:** Manages async processing queue

```python
class TDSQueueService:
    # Add item to queue
    async def enqueue(
        self,
        inbox_event_id: UUID,
        entity_type: EntityType,
        source_entity_id: str,
        operation_type: OperationType,
        validated_payload: Dict[str, Any],
        priority: int = 5
    ) -> TDSSyncQueue

    # Get pending items
    async def get_pending_events(
        self,
        limit: int = 100
    ) -> List[TDSSyncQueue]

    # Mark as completed
    async def mark_as_completed(
        self,
        queue_id: UUID,
        target_entity_id: Optional[str] = None
    )
```

---

### 5. Product Handler (`app/background/zoho_entity_handlers.py`)

**Location:** `app/background/zoho_entity_handlers.py`

**Purpose:** Syncs product data to database

```python
class ProductHandler(BaseEntityHandler):
    async def sync(
        self,
        payload: Dict[str, Any],
        operation: str
    ) -> Dict[str, Any]:
        """
        Sync product to products table

        Expected payload:
        - item_id (required)
        - name
        - sku
        - description
        - rate (price)
        - stock_on_hand
        - image_url (NEW - add this!)
        """
```

**Current Implementation:** Syncs basic product fields
**Enhancement Needed:** Add image_url field to sync

---

### 6. Zoho Bulk Sync Service (`app/services/zoho_bulk_sync.py`)

**Location:** `app/services/zoho_bulk_sync.py`

**Key Method:**

```python
class ZohoBulkSyncService:
    async def sync_products(
        self,
        incremental: bool = False,
        modified_since: Optional[str] = None,
        batch_size: int = 100,
        active_only: bool = True,
        with_stock_only: bool = True,
        sync_images: bool = True  # ✅ Already supports image sync!
    ) -> Dict[str, Any]
```

**Features:**

- ✅ Pagination support
- ✅ Filters (active only, with stock)
- ✅ Batch processing
- ✅ Image sync flag **already exists**!
- ✅ Error handling and retry

---

## 📊 Database Schema

### Products Table

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    zoho_item_id VARCHAR(100) UNIQUE,  -- Zoho item ID
    name VARCHAR(200) NOT NULL,
    sku VARCHAR(50) UNIQUE,
    description TEXT,
    price NUMERIC(10, 2),
    stock_quantity INTEGER,
    image_url VARCHAR(500),            -- ✅ Image URL field exists!
    images JSON,                        -- ✅ Multiple images support
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Image Fields:**

- `image_url` - Primary product image URL
- `images` - JSON array for multiple images

---

## 🎯 How to Download Images Using TDS

### Method 1: Use Existing Bulk Sync Service

**This is the EASIEST method - it already has image download support!**

```python
from app.services.zoho_bulk_sync import ZohoBulkSyncService
from app.db.database import get_async_db

async def download_all_product_images():
    """Download images for all products using existing bulk sync"""

    async with get_async_db() as db:
        sync_service = ZohoBulkSyncService(db)

        # Sync products with images enabled
        result = await sync_service.sync_products(
            active_only=True,      # Only active products
            with_stock_only=True,  # Only products with stock
            sync_images=True,      # ✅ ENABLE IMAGE SYNC
            batch_size=100
        )

        print(f"✅ Sync completed!")
        print(f"   Total: {result['stats']['total_processed']}")
        print(f"   Successful: {result['stats']['successful']}")
        print(f"   Failed: {result['stats']['failed']}")
```

**What it does:**

1. Fetches products from Zoho (paginated)
2. For each product with `image_document_id`:
   - Constructs image URL
   - Stores URL in `products.image_url`
3. Updates database with UPSERT
4. Publishes TDS events

---

### Method 2: Create Custom TDS Image Download Handler

**For more control and actual image file downloads:**

```python
"""
Custom TDS handler for downloading Zoho product images
Location: app/tds/handlers/image_download_handler.py
"""
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import Product
from app.services.zoho_inventory_client import ZohoInventoryClient
from app.services.image_service import ImageService
from app.tds.core.service import TDSService
from app.tds.core.events import TDSEntitySyncedEvent
from app.models.zoho_sync import EntityType, OperationType, SourceType

logger = logging.getLogger(__name__)


class ImageDownloadHandler:
    """Handler for downloading product images from Zoho"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.zoho_client = ZohoInventoryClient(db)
        self.tds_service = TDSService(db)

    async def download_all_images(
        self,
        active_only: bool = True,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Download images for all products

        Args:
            active_only: Only download for active products
            limit: Maximum number of images to download (for testing)

        Returns:
            Statistics dict
        """
        stats = {
            "total": 0,
            "downloaded": 0,
            "skipped": 0,
            "failed": 0
        }

        # Create TDS sync run
        sync_run = await self.tds_service.create_sync_run(
            run_type=SourceType.ZOHO,
            entity_type=EntityType.PRODUCT,
            configuration={"task": "image_download"}
        )

        try:
            # Get products without images
            query = select(Product).where(
                Product.zoho_item_id.isnot(None)
            )

            if active_only:
                query = query.where(Product.is_active == True)

            if limit:
                query = query.limit(limit)

            result = await self.db.execute(query)
            products = result.scalars().all()

            logger.info(f"Found {len(products)} products to process")

            # Process each product
            for product in products:
                stats["total"] += 1

                # Skip if already has image
                if product.image_url:
                    stats["skipped"] += 1
                    continue

                # Download image
                success = await self._download_product_image(product)

                if success:
                    stats["downloaded"] += 1
                else:
                    stats["failed"] += 1

            # Complete sync run
            await self.tds_service.complete_sync_run(
                sync_run_id=sync_run.id,
                total_processed=stats["total"],
                successful=stats["downloaded"],
                failed=stats["failed"]
            )

            return stats

        except Exception as e:
            logger.error(f"Image download failed: {e}", exc_info=True)
            await self.tds_service.fail_sync_run(
                sync_run_id=sync_run.id,
                error_message=str(e)
            )
            raise

    async def _download_product_image(self, product: Product) -> bool:
        """
        Download and store image for a single product

        Args:
            product: Product model instance

        Returns:
            True if successful
        """
        try:
            zoho_item_id = product.zoho_item_id

            # Download image from Zoho
            image_bytes = await self.zoho_client.download_item_image(zoho_item_id)

            if not image_bytes:
                logger.debug(f"No image found for product {product.id} (Zoho ID: {zoho_item_id})")
                return False

            # Store image
            result = await ImageService.download_image_from_bytes(
                item_id=zoho_item_id,
                image_data=image_bytes
            )

            if not result:
                logger.error(f"Failed to store image for product {product.id}")
                return False

            local_path, public_url = result

            # Update product
            product.image_url = public_url
            await self.db.commit()

            # Publish event
            await self.tds_service.record_entity_sync(
                entity_type=EntityType.PRODUCT,
                entity_id=str(product.id),
                source_entity_id=zoho_item_id,
                operation=OperationType.UPDATE,
                changes={"image_url": public_url}
            )

            logger.info(f"✅ Downloaded image for product {product.id}: {public_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to download image for product {product.id}: {e}")
            return False
```

---

### Method 3: Script to Trigger Image Download

```python
#!/usr/bin/env python3
"""
Script to download Zoho product images using TDS
Location: scripts/download_zoho_images.py
"""
import asyncio
import sys
sys.path.insert(0, '/Users/khaleelal-mulla/TSH_ERP_Ecosystem')

from app.db.database import AsyncSessionLocal
from app.tds.handlers.image_download_handler import ImageDownloadHandler


async def main():
    """Main entry point"""
    print("=" * 60)
    print("ZOHO PRODUCT IMAGE DOWNLOAD")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        handler = ImageDownloadHandler(db)

        # Download all images
        stats = await handler.download_all_images(
            active_only=True,
            limit=None  # No limit - download all
        )

        print("\n" + "=" * 60)
        print("DOWNLOAD COMPLETE")
        print("=" * 60)
        print(f"Total Products:    {stats['total']}")
        print(f"Downloaded:        {stats['downloaded']}")
        print(f"Skipped:           {stats['skipped']}")
        print(f"Failed:            {stats['failed']}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 Implementation Steps

### Step 1: Verify Zoho Credentials

```bash
# Check if credentials are configured
python3 -c "from app.config.zoho_config import zoho_config_manager; print(zoho_config_manager.get_credentials())"
```

### Step 2: Test Image Download (Single Product)

```python
# Test script
from app.services.zoho_inventory_client import ZohoInventoryClient
from app.services.image_service import ImageService

async def test_download():
    client = ZohoInventoryClient()

    # Test with one item
    item_id = "2646610000067014381"  # Example Zoho item ID

    # Download
    image_bytes = await client.download_item_image(item_id)

    if image_bytes:
        print(f"✅ Downloaded {len(image_bytes)} bytes")

        # Store
        result = await ImageService.download_image_from_bytes(item_id, image_bytes)
        if result:
            local_path, public_url = result
            print(f"✅ Stored at: {public_url}")
    else:
        print("❌ No image found")

# Run test
import asyncio
asyncio.run(test_download())
```

### Step 3: Create the Image Download Handler

```bash
# Create handler file
touch app/tds/handlers/image_download_handler.py

# Copy the handler code from Method 2 above
```

### Step 4: Create Download Script

```bash
# Create script
touch scripts/download_zoho_images.py
chmod +x scripts/download_zoho_images.py

# Copy the script code from Method 3 above
```

### Step 5: Run Image Download

```bash
# Run the script
python3 scripts/download_zoho_images.py
```

---

## 📋 Summary

### What Exists (✅ Ready to Use)

1. ✅ **Zoho API Client** - fetch_item_image_url(), download_item_image()
2. ✅ **Image Service** - download_and_store_image(), download_image_from_bytes()
3. ✅ **TDS Core** - Event system, queue management
4. ✅ **Database Schema** - products.image_url field
5. ✅ **Bulk Sync** - sync_images=True flag already exists

### What Needs to be Created (⚡ Quick Implementation)

1. ⚡ **Image Download Handler** - Custom TDS handler (30 minutes)
2. ⚡ **Download Script** - CLI script to trigger download (15 minutes)
3. ⚡ **Testing** - Verify with sample products (30 minutes)

### Recommended Approach

**🎯 EASIEST: Use existing bulk sync**

```python
await ZohoBulkSyncService(db).sync_products(sync_images=True)
```

**🎯 BEST: Create custom handler for actual file downloads**

Implement Method 2 & 3 above for complete control over image downloads with TDS events.

---

## 📚 References

- TDS Enhanced Architecture: `TDS_ENHANCED_ARCHITECTURE.md`
- Zoho Integration: `ZOHO_INTEGRATION_ANALYSIS_AND_IMPROVEMENTS.md`
- Event Bus: `EVENT_BUS_EXAMPLES.md`
- BFF Architecture: `BFF_PROJECT_COMPLETE.md`

---

**Status:** ✅ Complete - Ready for Implementation
**Estimated Time:** 1-2 hours for full implementation
**Complexity:** Low to Medium (all infrastructure exists)
