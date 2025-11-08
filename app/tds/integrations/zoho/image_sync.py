"""
TDS Image Synchronization Handler
==================================

Handles downloading and syncing product images from Zoho through TDS.
معالج مزامنة الصور للمنتجات من Zoho عبر TDS

This integrates existing standalone image download functionality into TDS
for centralized monitoring, event tracking, and unified architecture.

Author: TSH ERP Team
Date: November 7, 2025
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from ....models.product import Product
from ....services.image_service import ImageService
from ...core.service import TDSService
from ...core.events import TDSEvent
from ....core.events.event_bus import event_bus
from .client import UnifiedZohoClient, ZohoAPI
from .auth import ZohoAuthManager, ZohoCredentials

logger = logging.getLogger(__name__)


class ImageSyncStats:
    """Statistics for image synchronization"""

    def __init__(self):
        self.total = 0
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0
        self.start_time = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "total": self.total,
            "downloaded": self.downloaded,
            "skipped": self.skipped,
            "failed": self.failed,
            "success_rate": f"{(self.downloaded / self.total * 100):.1f}%" if self.total > 0 else "0%",
            "elapsed_seconds": round(elapsed, 2),
            "downloads_per_minute": round((self.downloaded / elapsed) * 60, 2) if elapsed > 0 else 0
        }


class TDSImageSyncHandler:
    """
    TDS Handler for Zoho Product Image Synchronization
    معالج TDS لمزامنة صور المنتجات من Zoho

    Features:
    - Batch processing with pagination
    - Rate limiting (respects Zoho API limits)
    - Event publishing for monitoring
    - Integration with existing ImageService
    - TDS event tracking
    - Comprehensive error handling
    """

    def __init__(
        self,
        db_session: AsyncSession,
        organization_id: str = "748369814",
        batch_size: int = 100,
        delay_between_batches: float = 2.0,
        delay_between_images: float = 0.1
    ):
        """
        Initialize image sync handler

        Args:
            db_session: Database session
            organization_id: Zoho organization ID
            batch_size: Images per batch (default: 100)
            delay_between_batches: Seconds between batches (default: 2.0)
            delay_between_images: Seconds between individual downloads (default: 0.1)
        """
        self.db = db_session
        self.organization_id = organization_id
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.delay_between_images = delay_between_images

        # Initialize TDS service
        self.tds_service = TDSService(db_session)

        # Initialize Zoho client (will be set in sync_images)
        self.zoho_client: Optional[UnifiedZohoClient] = None

        # Statistics
        self.stats = ImageSyncStats()

    async def sync_images(
        self,
        active_only: bool = True,
        with_stock_only: bool = True,
        force_redownload: bool = False,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Download and sync product images from Zoho

        Args:
            active_only: Only process active products
            with_stock_only: Only process products with stock
            force_redownload: Re-download even if image_url exists
            limit: Maximum images to download (for testing)

        Returns:
            Statistics dictionary
        """
        logger.info("🚀 Starting TDS Image Synchronization...")

        # Initialize Zoho client with auth from environment variables
        import os
        credentials = ZohoCredentials(
            client_id=os.getenv('ZOHO_CLIENT_ID'),
            client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
            refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
            organization_id=self.organization_id or os.getenv('ZOHO_ORGANIZATION_ID')
        )
        
        if not all([credentials.client_id, credentials.client_secret, credentials.refresh_token]):
            raise ValueError("Missing Zoho credentials in environment variables")
        
        auth_manager = ZohoAuthManager(credentials)
        await auth_manager.start()
        
        self.zoho_client = UnifiedZohoClient(
            auth_manager=auth_manager,
            organization_id=credentials.organization_id,
            rate_limit=100  # Zoho Books limit
        )
        await self.zoho_client.start_session()

        # Create TDS sync run
        sync_run = await self.tds_service.create_sync_run(
            run_type="zoho",
            entity_type="product",
            configuration={
                "task": "image_download",
                "active_only": active_only,
                "with_stock_only": with_stock_only,
                "force_redownload": force_redownload,
                "batch_size": self.batch_size
            }
        )

        logger.info(f"📋 TDS Sync Run Created: {sync_run.id}")

        try:
            # Get products to process
            products = await self._get_products_to_process(
                active_only, with_stock_only, force_redownload, limit
            )

            self.stats.total = len(products)
            logger.info(f"📊 Found {self.stats.total} products to process")

            # Publish start event
            await event_bus.publish(TDSEvent(
                event_type="zoho.image_sync.started",
                data={
                    "sync_run_id": str(sync_run.id),
                    "total_products": self.stats.total,
                    "batch_size": self.batch_size
                }
            ))

            # Process in batches
            total_batches = (self.stats.total + self.batch_size - 1) // self.batch_size

            for batch_num in range(total_batches):
                start_idx = batch_num * self.batch_size
                end_idx = min(start_idx + self.batch_size, self.stats.total)
                batch_products = products[start_idx:end_idx]

                logger.info(f"\n{'='*60}")
                logger.info(f"Processing Batch {batch_num + 1}/{total_batches}")
                logger.info(f"Products: {len(batch_products)}")
                logger.info(f"{'='*60}\n")

                await self._process_batch(batch_products, batch_num + 1, total_batches)

                # Delay between batches (except last)
                if batch_num < total_batches - 1:
                    logger.info(f"⏸️  Waiting {self.delay_between_batches}s before next batch...\n")
                    await asyncio.sleep(self.delay_between_batches)

            # Complete sync run
            await self.tds_service.complete_sync_run(
                sync_run_id=sync_run.id,
                total_processed=self.stats.total,
                successful=self.stats.downloaded,
                failed=self.stats.failed
            )

            # Publish completion event
            await event_bus.publish(TDSEvent(
                event_type="zoho.image_sync.completed",
                data={
                    "sync_run_id": str(sync_run.id),
                    "statistics": self.stats.to_dict()
                }
            ))

            logger.info("\n" + "="*60)
            logger.info("✅ Image Synchronization Complete!")
            logger.info("="*60)
            for key, value in self.stats.to_dict().items():
                logger.info(f"  {key}: {value}")
            logger.info("="*60 + "\n")

            # Cleanup: Close Zoho client session
            if self.zoho_client:
                await self.zoho_client.close_session()

            return self.stats.to_dict()

        except Exception as e:
            logger.error(f"❌ Image sync failed: {e}", exc_info=True)

            # Cleanup: Close Zoho client session on error
            if self.zoho_client:
                await self.zoho_client.close_session()

            # Fail sync run
            await self.tds_service.fail_sync_run(
                sync_run_id=sync_run.id,
                error_message=str(e)
            )

            # Publish failure event
            await event_bus.publish(TDSEvent(
                event_type="zoho.image_sync.failed",
                data={
                    "sync_run_id": str(sync_run.id),
                    "error": str(e),
                    "statistics": self.stats.to_dict()
                }
            ))

            raise

    async def _get_products_to_process(
        self,
        active_only: bool,
        with_stock_only: bool,
        force_redownload: bool,
        limit: Optional[int]
    ) -> List[Product]:
        """Get products that need image downloads"""

        query = select(Product).where(
            Product.zoho_item_id.isnot(None)
        )

        if active_only:
            query = query.where(Product.is_active == True)

        if with_stock_only:
            query = query.where(Product.actual_available_stock > 0)

        if not force_redownload:
            # Only get products without images
            query = query.where(
                (Product.image_url.is_(None)) |
                (Product.image_url == '')
            )

        query = query.order_by(Product.name)

        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _process_batch(
        self,
        products: List[Product],
        batch_num: int,
        total_batches: int
    ):
        """Process a batch of products"""

        for idx, product in enumerate(products, 1):
            overall_idx = ((batch_num - 1) * self.batch_size) + idx

            logger.info(f"[{overall_idx}] {product.name}")
            logger.info(f"  SKU: {product.sku}")
            logger.info(f"  Zoho Item ID: {product.zoho_item_id}")

            try:
                # Download and store image
                success = await self._download_product_image(product)

                if success:
                    self.stats.downloaded += 1
                    logger.info(f"  ✅ Downloaded and stored successfully\n")
                else:
                    self.stats.skipped += 1
                    logger.info(f"  ⏭️  Skipped (no image available)\n")

            except Exception as e:
                self.stats.failed += 1
                logger.error(f"  ❌ Failed: {e}\n")

            # Small delay between images
            await asyncio.sleep(self.delay_between_images)

    async def _download_product_image(self, product: Product) -> bool:
        """
        Download and store image for a single product

        Returns:
            True if downloaded successfully, False if skipped
        """
        try:
            zoho_item_id = product.zoho_item_id

            # Get image from Zoho Books
            # Zoho Books endpoint: /items/{item_id}/image
            image_url = f"https://www.zohoapis.com/books/v3/items/{zoho_item_id}/image"
            params = {"organization_id": self.organization_id}

            # Get auth headers from Zoho client
            headers = await self.zoho_client.auth_manager.get_auth_headers()

            # Download image using ImageService
            result = await ImageService.download_and_store_image(
                item_id=zoho_item_id,
                image_url=image_url,
                headers=headers
            )

            if not result:
                # No image available
                return False

            local_path, public_url = result

            # Update product in database
            product.image_url = public_url
            product.updated_at = datetime.utcnow()
            await self.db.commit()

            # Record entity sync in TDS
            await self.tds_service.record_entity_sync(
                entity_type="PRODUCT",
                entity_id=str(product.id),
                source_entity_id=zoho_item_id,
                operation="UPDATE",
                changes={"image_url": public_url}
            )

            logger.info(f"  💾 Stored at: {public_url}")

            return True

        except Exception as e:
            logger.error(f"Failed to download image for product {product.id}: {e}")
            raise


# Convenience function for CLI scripts
async def download_images_via_tds(
    db_session: AsyncSession,
    active_only: bool = True,
    with_stock_only: bool = True,
    batch_size: int = 100,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function to download images through TDS

    Args:
        db_session: Database session
        active_only: Only active products
        with_stock_only: Only products with stock
        batch_size: Images per batch
        limit: Maximum images (for testing)

    Returns:
        Statistics dictionary
    """
    handler = TDSImageSyncHandler(
        db_session=db_session,
        batch_size=batch_size
    )

    return await handler.sync_images(
        active_only=active_only,
        with_stock_only=with_stock_only,
        limit=limit
    )
