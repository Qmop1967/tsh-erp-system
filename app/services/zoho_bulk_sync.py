"""
Zoho Bulk Sync Service
Handles bulk data migration from Zoho Books to TSH ERP
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, text, column
from sqlalchemy.dialects.postgresql import insert

from app.models import (
    Product, Customer, CustomerAddress,
    PriceList, ProductPrice, Branch, Currency
)
from app.services.zoho_books_client import ZohoBooksClient
from app.db.database import get_async_db

logger = logging.getLogger(__name__)


class ZohoBulkSyncService:
    """
    Service for bulk synchronization of data from Zoho Books to TSH ERP
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize bulk sync service

        Args:
            db: Database session
        """
        self.db = db
        self.zoho_client = ZohoBooksClient(db)
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }

    # ============================================================================
    # PRODUCTS BULK SYNC
    # ============================================================================

    async def sync_products(
        self,
        incremental: bool = False,
        modified_since: Optional[str] = None,
        batch_size: int = 100,
        active_only: bool = True,
        with_stock_only: bool = True,
        sync_images: bool = True
    ) -> Dict[str, Any]:
        """
        Bulk sync products from Zoho Books

        Args:
            incremental: If True, only sync modified items
            modified_since: ISO date string for incremental sync
            batch_size: Number of items to process in each batch
            active_only: If True, only sync active items (default: True)
            with_stock_only: If True, only sync items with stock (default: True)
            sync_images: If True, download and sync product images (default: True)

        Returns:
            Statistics dictionary with counts and errors
        """
        logger.info("🔄 Starting products bulk sync from Zoho Books")
        logger.info(f"   Filters: active_only={active_only}, with_stock_only={with_stock_only}, sync_images={sync_images}")
        start_time = datetime.now()

        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }

        try:
            # Build filters for Zoho API
            filters = {}
            if incremental and modified_since:
                filters["last_modified_time"] = modified_since

            # Filter for active items only
            if active_only:
                filters["filter_by"] = "Status.Active"

            # Fetch products from Zoho Books with pagination
            batch = []
            async for zoho_item in self.zoho_client.fetch_items_paginated(filters=filters):
                # Additional filtering for items with stock (if enabled)
                if with_stock_only:
                    stock_on_hand = zoho_item.get("stock_on_hand", 0)
                    if stock_on_hand <= 0:
                        self.stats["skipped"] += 1
                        continue

                batch.append(zoho_item)
                self.stats["total_processed"] += 1

                # Process in batches
                if len(batch) >= batch_size:
                    await self._process_product_batch(batch, sync_images=sync_images)
                    batch = []

                # Rate limiting - avoid overwhelming database
                if self.stats["total_processed"] % 500 == 0:
                    logger.info(f"  Progress: {self.stats['total_processed']} products processed, {self.stats['skipped']} skipped")
                    await asyncio.sleep(0.5)  # Brief pause every 500 items

            # Process remaining items
            if batch:
                await self._process_product_batch(batch, sync_images=sync_images)

            duration = (datetime.now() - start_time).total_seconds()

            logger.info(f"✅ Products bulk sync completed!")
            logger.info(f"   Total: {self.stats['total_processed']}")
            logger.info(f"   Successful: {self.stats['successful']}")
            logger.info(f"   Failed: {self.stats['failed']}")
            logger.info(f"   Skipped: {self.stats['skipped']}")
            logger.info(f"   Duration: {duration:.2f} seconds")

            return {
                "success": True,
                "stats": self.stats,
                "duration_seconds": duration
            }

        except Exception as e:
            logger.error(f"❌ Products bulk sync failed: {e}", exc_info=True)
            self.stats["errors"].append(str(e))
            return {
                "success": False,
                "stats": self.stats,
                "error": str(e)
            }

    async def _process_product_batch(self, batch: List[Dict], sync_images: bool = True) -> None:
        """
        Process a batch of products - each item commits individually

        Args:
            batch: List of Zoho items to process
            sync_images: Whether to download and sync product images
        """
        for zoho_item in batch:
            try:
                await self._upsert_product(zoho_item, sync_images=sync_images)
                await self.db.commit()  # Commit after each item
                self.stats["successful"] += 1
            except Exception as e:
                await self.db.rollback()  # Rollback failed item
                logger.error(f"Failed to process product {zoho_item.get('item_id')}: {e}")
                self.stats["failed"] += 1
                self.stats["errors"].append({
                    "item_id": zoho_item.get("item_id"),
                    "error": str(e)
                })

    async def _upsert_product(self, zoho_item: Dict, sync_images: bool = True) -> None:
        """
        Insert or update a single product

        Args:
            zoho_item: Zoho item dictionary
            sync_images: Whether to download and sync product image
        """
        zoho_item_id = zoho_item.get("item_id")
        if not zoho_item_id:
            raise ValueError("Missing item_id in Zoho data")

        # Transform Zoho item to TSH ERP product format
        product_data = self._transform_zoho_item(zoho_item)

        # Get image URL from Zoho if available
        image_url = ""
        if sync_images and zoho_item.get("image_document_id"):
            # Build Zoho image URL
            org_id = ZohoBooksClient.ORGANIZATION_ID
            doc_id = zoho_item.get("image_document_id")
            image_url = f"https://www.zohoapis.com/inventory/v1/items/{zoho_item_id}/image?organization_id={org_id}"
            logger.debug(f"Product {zoho_item_id} has image: {doc_id}")

        # Use raw SQL for upsert since Product model doesn't define zoho_item_id
        # But the database table has it
        query = text("""
            INSERT INTO products (
                zoho_item_id, sku, name, description, category,
                price, stock_quantity, image_url, is_active,
                last_synced, created_at, updated_at
            )
            VALUES (
                :zoho_item_id, :sku, :name, :description, :category,
                :price, :stock_quantity, :image_url, :is_active,
                :last_synced, :created_at, :updated_at
            )
            ON CONFLICT (zoho_item_id)
            DO UPDATE SET
                sku = EXCLUDED.sku,
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                category = EXCLUDED.category,
                price = EXCLUDED.price,
                stock_quantity = EXCLUDED.stock_quantity,
                image_url = EXCLUDED.image_url,
                is_active = EXCLUDED.is_active,
                last_synced = EXCLUDED.last_synced,
                updated_at = EXCLUDED.updated_at
        """)

        await self.db.execute(query, {
            "zoho_item_id": zoho_item_id,
            "sku": product_data.get("sku"),
            "name": product_data.get("name"),
            "description": product_data.get("description", ""),
            "category": product_data.get("category_name", ""),
            "price": float(product_data.get("unit_price", 0)),
            "stock_quantity": float(product_data.get("stock_quantity", 0)),
            "image_url": image_url,  # Use the Zoho image URL
            "is_active": product_data.get("is_active", True),
            "last_synced": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })

        logger.debug(f"Upserted product: {zoho_item_id}")

    def _transform_zoho_item(self, zoho_item: Dict) -> Dict:
        """
        Transform Zoho item format to TSH ERP product format

        Args:
            zoho_item: Zoho item dictionary

        Returns:
            Product data dictionary
        """
        return {
            "zoho_item_id": zoho_item.get("item_id"),
            "name": zoho_item.get("name", ""),
            "sku": zoho_item.get("sku") or f"AUTO-{zoho_item.get('item_id')}",
            "description": zoho_item.get("description", ""),
            "unit_price": Decimal(str(zoho_item.get("rate", 0))),
            "cost_price": Decimal(str(zoho_item.get("purchase_rate", 0))),
            "stock_quantity": zoho_item.get("stock_on_hand", 0),
            "min_stock_level": zoho_item.get("reorder_level", 0),
            "is_active": zoho_item.get("status") == "active",
            "tax_rate": Decimal(str(zoho_item.get("tax_percentage", 0))),
            "category_name": zoho_item.get("category_name", ""),
            "brand": zoho_item.get("brand", ""),
            "barcode": zoho_item.get("upc", "") or zoho_item.get("ean", ""),
            "unit_of_measure": zoho_item.get("unit", ""),
            "zoho_metadata": zoho_item,  # Store full Zoho JSON
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

    # ============================================================================
    # CUSTOMERS BULK SYNC
    # ============================================================================

    async def sync_customers(
        self,
        incremental: bool = False,
        modified_since: Optional[str] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Bulk sync all customers from Zoho Books

        Args:
            incremental: If True, only sync modified contacts
            modified_since: ISO date string for incremental sync
            batch_size: Number of customers to process in each batch

        Returns:
            Statistics dictionary with counts and errors
        """
        logger.info("🔄 Starting customers bulk sync from Zoho Books")
        start_time = datetime.now()

        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }

        try:
            batch = []
            async for zoho_contact in self.zoho_client.fetch_customers_paginated():
                # Filter by modification date if incremental
                if incremental and modified_since:
                    last_modified = zoho_contact.get("last_modified_time", "")
                    if last_modified < modified_since:
                        self.stats["skipped"] += 1
                        continue

                batch.append(zoho_contact)
                self.stats["total_processed"] += 1

                if len(batch) >= batch_size:
                    await self._process_customer_batch(batch)
                    batch = []

                if self.stats["total_processed"] % 200 == 0:
                    logger.info(f"  Progress: {self.stats['total_processed']} customers processed")

            if batch:
                await self._process_customer_batch(batch)

            duration = (datetime.now() - start_time).total_seconds()

            logger.info(f"✅ Customers bulk sync completed!")
            logger.info(f"   Total: {self.stats['total_processed']}")
            logger.info(f"   Successful: {self.stats['successful']}")
            logger.info(f"   Failed: {self.stats['failed']}")
            logger.info(f"   Duration: {duration:.2f} seconds")

            return {
                "success": True,
                "stats": self.stats,
                "duration_seconds": duration
            }

        except Exception as e:
            logger.error(f"❌ Customers bulk sync failed: {e}", exc_info=True)
            self.stats["errors"].append(str(e))
            return {
                "success": False,
                "stats": self.stats,
                "error": str(e)
            }

    async def _process_customer_batch(self, batch: List[Dict]) -> None:
        """Process a batch of customers - each item commits individually"""
        for zoho_contact in batch:
            try:
                await self._upsert_customer(zoho_contact)
                await self.db.commit()  # Commit after each item
                self.stats["successful"] += 1
            except Exception as e:
                await self.db.rollback()  # Rollback failed item
                logger.error(f"Failed to process customer {zoho_contact.get('contact_id')}: {e}")
                self.stats["failed"] += 1
                self.stats["errors"].append({
                    "contact_id": zoho_contact.get("contact_id"),
                    "error": str(e)
                })

    async def _upsert_customer(self, zoho_contact: Dict) -> None:
        """
        Insert or update a single customer

        Args:
            zoho_contact: Zoho contact dictionary
        """
        zoho_contact_id = zoho_contact.get("contact_id")
        if not zoho_contact_id:
            raise ValueError("Missing contact_id in Zoho data")

        # Transform Zoho contact to TSH ERP customer format
        customer_data = self._transform_zoho_contact(zoho_contact)

        # Use raw SQL for upsert
        query = text("""
            INSERT INTO customers (
                zoho_contact_id, contact_name, email, phone,
                company_name, status, created_at, updated_at
            )
            VALUES (
                :zoho_contact_id, :contact_name, :email, :phone,
                :company_name, :status, :created_at, :updated_at
            )
            ON CONFLICT (zoho_contact_id)
            DO UPDATE SET
                contact_name = EXCLUDED.contact_name,
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                company_name = EXCLUDED.company_name,
                status = EXCLUDED.status,
                updated_at = EXCLUDED.updated_at
            RETURNING id
        """)

        result = await self.db.execute(query, {
            "zoho_contact_id": zoho_contact_id,
            "contact_name": customer_data.get("name", "")[:200],  # Limit length
            "email": customer_data.get("email", "")[:200],
            "phone": customer_data.get("phone", "")[:50],
            "company_name": customer_data.get("company_name", "")[:200],
            "status": "active" if customer_data.get("is_active", True) else "inactive",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })

        customer_id = result.scalar_one()
        logger.debug(f"Upserted customer: {zoho_contact_id}")

    def _transform_zoho_contact(self, zoho_contact: Dict) -> Dict:
        """
        Transform Zoho contact format to TSH ERP customer format

        Args:
            zoho_contact: Zoho contact dictionary

        Returns:
            Customer data dictionary
        """
        return {
            "zoho_contact_id": zoho_contact.get("contact_id"),
            "name": zoho_contact.get("contact_name", ""),
            "full_name": f"{zoho_contact.get('first_name', '')} {zoho_contact.get('last_name', '')}".strip(),
            "email": zoho_contact.get("email", ""),
            "phone": zoho_contact.get("phone", ""),
            "mobile": zoho_contact.get("mobile", ""),
            "company_name": zoho_contact.get("company_name", ""),
            "customer_type": "business" if zoho_contact.get("contact_type") == "business" else "individual",
            "is_active": zoho_contact.get("status") == "active",
            "credit_limit": Decimal(str(zoho_contact.get("credit_limit", 0))),
            "payment_terms": zoho_contact.get("payment_terms_label", ""),
            "tax_number": zoho_contact.get("tax_id", ""),
            "website": zoho_contact.get("website", ""),
            "notes": zoho_contact.get("notes", ""),
            "zoho_metadata": zoho_contact,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

    async def _sync_customer_addresses(self, customer: Customer, zoho_contact: Dict) -> None:
        """
        Sync customer addresses from Zoho contact

        Args:
            customer: TSH ERP customer object
            zoho_contact: Zoho contact dictionary
        """
        # Delete existing addresses
        await self.db.execute(
            CustomerAddress.__table__.delete().where(CustomerAddress.customer_id == customer.id)
        )

        # Add billing address
        billing_address = zoho_contact.get("billing_address", {})
        if billing_address:
            address = CustomerAddress(
                customer_id=customer.id,
                address_type="billing",
                address_line1=billing_address.get("address", ""),
                city=billing_address.get("city", ""),
                state=billing_address.get("state", ""),
                postal_code=billing_address.get("zip", ""),
                country=billing_address.get("country", ""),
                is_default=True
            )
            self.db.add(address)

        # Add shipping address
        shipping_address = zoho_contact.get("shipping_address", {})
        if shipping_address:
            address = CustomerAddress(
                customer_id=customer.id,
                address_type="shipping",
                address_line1=shipping_address.get("address", ""),
                city=shipping_address.get("city", ""),
                state=shipping_address.get("state", ""),
                postal_code=shipping_address.get("zip", ""),
                country=shipping_address.get("country", ""),
                is_default=False
            )
            self.db.add(address)

    # ============================================================================
    # NOTE: Invoice sync removed - invoices are handled by webhook sync
    # ============================================================================

    # ============================================================================
    # PRICE LISTS BULK SYNC
    # ============================================================================

    async def sync_pricelists(self) -> Dict[str, Any]:
        """
        Bulk sync all price lists from Zoho Books

        Returns:
            Statistics dictionary with counts and errors
        """
        logger.info("🔄 Starting price lists bulk sync from Zoho Books")
        start_time = datetime.now()

        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Fetch all price lists
            zoho_pricelists = await self.zoho_client.fetch_pricelists()

            for zoho_pricelist in zoho_pricelists:
                try:
                    # Fetch detailed pricelist with item prices
                    pricelist_id = zoho_pricelist.get("pricelist_id")
                    pricelist_details = await self.zoho_client.fetch_pricelist_details(pricelist_id)

                    await self._upsert_pricelist(pricelist_details)

                    self.stats["total_processed"] += 1
                    self.stats["successful"] += 1

                except Exception as e:
                    logger.error(f"Failed to process pricelist {zoho_pricelist.get('pricelist_id')}: {e}")
                    self.stats["failed"] += 1
                    self.stats["errors"].append({
                        "pricelist_id": zoho_pricelist.get("pricelist_id"),
                        "error": str(e)
                    })

            await self.db.commit()

            duration = (datetime.now() - start_time).total_seconds()

            logger.info(f"✅ Price lists bulk sync completed!")
            logger.info(f"   Total: {self.stats['total_processed']}")
            logger.info(f"   Successful: {self.stats['successful']}")
            logger.info(f"   Failed: {self.stats['failed']}")
            logger.info(f"   Duration: {duration:.2f} seconds")

            return {
                "success": True,
                "stats": self.stats,
                "duration_seconds": duration
            }

        except Exception as e:
            logger.error(f"❌ Price lists bulk sync failed: {e}", exc_info=True)
            await self.db.rollback()
            return {
                "success": False,
                "stats": self.stats,
                "error": str(e)
            }

    async def _upsert_pricelist(self, zoho_pricelist: Dict) -> None:
        """
        Insert or update a price list with item prices

        Args:
            zoho_pricelist: Zoho pricelist dictionary with items
        """
        zoho_pricelist_id = zoho_pricelist.get("pricelist_id")
        if not zoho_pricelist_id:
            raise ValueError("Missing pricelist_id in Zoho data")

        # Use raw SQL for upsert - pricelist
        query = text("""
            INSERT INTO pricelists (
                zoho_pricelist_id, name, currency, is_active,
                created_at, updated_at
            )
            VALUES (
                :zoho_pricelist_id, :name, :currency, :is_active,
                :created_at, :updated_at
            )
            ON CONFLICT (zoho_pricelist_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                currency = EXCLUDED.currency,
                is_active = EXCLUDED.is_active,
                updated_at = EXCLUDED.updated_at
            RETURNING id
        """)

        result = await self.db.execute(query, {
            "zoho_pricelist_id": zoho_pricelist_id,
            "name": zoho_pricelist.get("name", "")[:200],
            "currency": zoho_pricelist.get("currency_code", "USD")[:10],
            "is_active": zoho_pricelist.get("status") == "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })

        pricelist_id = result.scalar_one()

        # Delete existing product prices for this pricelist
        await self.db.execute(
            text("DELETE FROM product_prices WHERE pricelist_id = :pricelist_id"),
            {"pricelist_id": pricelist_id}
        )

        # Add product prices
        for item in zoho_pricelist.get("items", []):
            zoho_item_id = item.get("item_id")

            # Find product by zoho_item_id using raw SQL
            product_query = text("SELECT id FROM products WHERE zoho_item_id = :zoho_item_id")
            product_result = await self.db.execute(product_query, {"zoho_item_id": zoho_item_id})
            product_row = product_result.fetchone()

            if product_row:
                product_id = product_row[0]
                # Insert product price
                price_query = text("""
                    INSERT INTO product_prices (pricelist_id, product_id, price, is_active)
                    VALUES (:pricelist_id, :product_id, :price, :is_active)
                    ON CONFLICT (pricelist_id, product_id)
                    DO UPDATE SET price = EXCLUDED.price, is_active = EXCLUDED.is_active
                """)
                await self.db.execute(price_query, {
                    "pricelist_id": pricelist_id,
                    "product_id": product_id,
                    "price": float(item.get("rate", 0)),
                    "is_active": True
                })

        logger.debug(f"Upserted pricelist: {zoho_pricelist_id}")
