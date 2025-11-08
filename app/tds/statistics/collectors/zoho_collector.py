"""
Zoho Data Collector
===================

Collects statistics from Zoho APIs (Books, Inventory, CRM).

جامع بيانات Zoho
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from app.tds.integrations.zoho import (
    UnifiedZohoClient,
    ZohoAPI,
    ZohoAuthManager,
    ZohoCredentials,
)
from app.tds.statistics.models import (
    ItemStatistics,
    CustomerStatistics,
    VendorStatistics,
    PriceListStatistics,
    StockStatistics,
    ImageStatistics,
    ZohoStatistics,
)

logger = logging.getLogger(__name__)


class ZohoDataCollector:
    """
    Collects comprehensive statistics from Zoho systems

    جامع إحصائيات شامل من أنظمة Zoho

    Features:
    - Fetches data from Zoho Books, Inventory, and CRM
    - Aggregates statistics across all entity types
    - Handles pagination and rate limiting
    - Provides detailed breakdowns by category, brand, country, etc.
    """

    def __init__(
        self,
        client: Optional[UnifiedZohoClient] = None,
        credentials: Optional[ZohoCredentials] = None
    ):
        """
        Initialize Zoho data collector

        Args:
            client: Existing UnifiedZohoClient instance
            credentials: Zoho credentials (if client not provided)
        """
        if client:
            self.client = client
            self._owns_client = False
        else:
            if not credentials:
                credentials = self._load_credentials_from_env()

            auth = ZohoAuthManager(credentials, auto_refresh=True)
            self.client = UnifiedZohoClient(auth, credentials.organization_id)
            self._owns_client = True

    def _load_credentials_from_env(self) -> ZohoCredentials:
        """Load Zoho credentials from environment variables"""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        return ZohoCredentials(
            client_id=os.getenv("ZOHO_CLIENT_ID", ""),
            client_secret=os.getenv("ZOHO_CLIENT_SECRET", ""),
            refresh_token=os.getenv("ZOHO_REFRESH_TOKEN", ""),
            organization_id=os.getenv("ZOHO_ORGANIZATION_ID", "")
        )

    async def collect_all_stats(self) -> ZohoStatistics:
        """
        Collect all statistics from Zoho

        Returns:
            Complete ZohoStatistics object with all entity statistics

        جمع جميع الإحصائيات من Zoho
        """
        logger.info("Starting Zoho statistics collection...")

        try:
            # Ensure client is started
            if self._owns_client:
                await self.client.start_session()

            # Collect statistics for all entity types
            items_stats = await self.collect_items_stats()
            customers_stats = await self.collect_customer_stats()
            vendors_stats = await self.collect_vendor_stats()
            price_lists_stats = await self.collect_pricelist_stats()
            stock_stats = await self.collect_stock_stats()
            images_stats = await self.collect_image_stats()

            logger.info("✅ Zoho statistics collection completed")

            return ZohoStatistics(
                items=items_stats,
                customers=customers_stats,
                vendors=vendors_stats,
                price_lists=price_lists_stats,
                stock=stock_stats,
                images=images_stats,
                collected_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Failed to collect Zoho statistics: {e}", exc_info=True)
            raise
        finally:
            if self._owns_client:
                await self.client.close_session()

    async def collect_items_stats(self) -> ItemStatistics:
        """
        Collect item/product statistics from Zoho Inventory

        Returns:
            ItemStatistics with counts, breakdowns, and aggregates

        جمع إحصائيات المنتجات
        """
        logger.info("Collecting Zoho items statistics...")

        # Fetch all items
        items = await self.client.paginated_fetch(
            api_type=ZohoAPI.INVENTORY,
            endpoint="items",
            page_size=200
        )

        # Initialize counters
        total_count = len(items)
        active_count = 0
        inactive_count = 0
        with_images_count = 0
        without_images_count = 0
        low_stock_count = 0
        out_of_stock_count = 0

        by_category: Dict[str, int] = defaultdict(int)
        by_brand: Dict[str, int] = defaultdict(int)

        total_price = 0.0
        total_stock_value = 0.0

        # Analyze each item
        for item in items:
            # Status
            if item.get("status") == "active":
                active_count += 1
            else:
                inactive_count += 1

            # Images
            if item.get("image_name") or item.get("image_document_id"):
                with_images_count += 1
            else:
                without_images_count += 1

            # Category
            category = item.get("category_name", "Uncategorized")
            by_category[category] += 1

            # Brand
            brand = item.get("brand", "No Brand")
            by_brand[brand] += 1

            # Price
            rate = float(item.get("rate", 0) or 0)
            total_price += rate

            # Stock
            stock = float(item.get("actual_available_stock", 0) or 0)
            reorder_level = float(item.get("reorder_level", 0) or 0)

            if stock <= 0:
                out_of_stock_count += 1
            elif stock <= reorder_level:
                low_stock_count += 1

            # Stock value
            total_stock_value += stock * rate

        # Calculate averages
        average_price = total_price / total_count if total_count > 0 else 0.0

        logger.info(
            f"✅ Zoho items: {total_count} total, {active_count} active, "
            f"{with_images_count} with images"
        )

        return ItemStatistics(
            total_count=total_count,
            active_count=active_count,
            inactive_count=inactive_count,
            with_images_count=with_images_count,
            without_images_count=without_images_count,
            by_category=dict(by_category),
            by_brand=dict(by_brand),
            average_price=round(average_price, 2),
            total_stock_value=round(total_stock_value, 2),
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count
        )

    async def collect_customer_stats(self) -> CustomerStatistics:
        """
        Collect customer statistics from Zoho Books

        Returns:
            CustomerStatistics with counts and breakdowns

        جمع إحصائيات العملاء
        """
        logger.info("Collecting Zoho customer statistics...")

        # Fetch all contacts (customers)
        contacts = await self.client.paginated_fetch(
            api_type=ZohoAPI.BOOKS,
            endpoint="contacts",
            params={"contact_type": "customer"},
            page_size=200
        )

        # Initialize counters
        total_count = len(contacts)
        active_count = 0
        inactive_count = 0
        with_outstanding = 0

        by_type: Dict[str, int] = defaultdict(int)
        by_country: Dict[str, int] = defaultdict(int)
        by_price_list: Dict[str, int] = defaultdict(int)

        total_credit_limit = 0.0
        total_credit_limits = 0

        # Analyze each customer
        for contact in contacts:
            # Status
            if contact.get("status") == "active":
                active_count += 1
            else:
                inactive_count += 1

            # Outstanding balance
            outstanding = float(contact.get("outstanding_receivable_amount", 0) or 0)
            if outstanding > 0:
                with_outstanding += 1

            # Customer type
            customer_type = contact.get("customer_type", "regular")
            by_type[customer_type] += 1

            # Country
            country = contact.get("billing_address", {}).get("country", "Unknown")
            by_country[country] += 1

            # Price list
            price_list = contact.get("price_list_name", "Default")
            by_price_list[price_list] += 1

            # Credit limit
            credit_limit = float(contact.get("credit_limit", 0) or 0)
            if credit_limit > 0:
                total_credit_limit += credit_limit
                total_credit_limits += 1

        # Calculate averages
        avg_credit_limit = (
            total_credit_limit / total_credit_limits
            if total_credit_limits > 0
            else 0.0
        )

        logger.info(
            f"✅ Zoho customers: {total_count} total, {active_count} active"
        )

        return CustomerStatistics(
            total_count=total_count,
            active_count=active_count,
            inactive_count=inactive_count,
            by_type=dict(by_type),
            by_country=dict(by_country),
            by_price_list=dict(by_price_list),
            total_credit_limit=round(total_credit_limit, 2),
            with_outstanding_balance=with_outstanding,
            average_credit_limit=round(avg_credit_limit, 2)
        )

    async def collect_vendor_stats(self) -> VendorStatistics:
        """
        Collect vendor/supplier statistics from Zoho Books

        Returns:
            VendorStatistics with counts and breakdowns

        جمع إحصائيات الموردين
        """
        logger.info("Collecting Zoho vendor statistics...")

        # Fetch all vendors
        vendors = await self.client.paginated_fetch(
            api_type=ZohoAPI.BOOKS,
            endpoint="contacts",
            params={"contact_type": "vendor"},
            page_size=200
        )

        # Initialize counters
        total_count = len(vendors)
        active_count = 0
        inactive_count = 0
        with_payables = 0

        by_country: Dict[str, int] = defaultdict(int)

        total_payables = 0.0

        # Analyze each vendor
        for vendor in vendors:
            # Status
            if vendor.get("status") == "active":
                active_count += 1
            else:
                inactive_count += 1

            # Outstanding payables
            payable = float(vendor.get("outstanding_payable_amount", 0) or 0)
            if payable > 0:
                with_payables += 1
                total_payables += payable

            # Country
            country = vendor.get("billing_address", {}).get("country", "Unknown")
            by_country[country] += 1

        logger.info(
            f"✅ Zoho vendors: {total_count} total, {active_count} active"
        )

        return VendorStatistics(
            total_count=total_count,
            active_count=active_count,
            inactive_count=inactive_count,
            by_country=dict(by_country),
            total_payables=round(total_payables, 2),
            with_outstanding_payables=with_payables
        )

    async def collect_pricelist_stats(self) -> PriceListStatistics:
        """
        Collect price list statistics from Zoho Books

        Returns:
            PriceListStatistics with counts and coverage

        جمع إحصائيات قوائم الأسعار
        """
        logger.info("Collecting Zoho price list statistics...")

        # Fetch all price books
        price_books = await self.client.paginated_fetch(
            api_type=ZohoAPI.BOOKS,
            endpoint="pricebooks",
            page_size=200
        )

        # Initialize counters
        total_lists = len(price_books)
        active_lists = 0
        inactive_lists = 0
        total_items_mapped = 0

        lists_by_currency: Dict[str, int] = defaultdict(int)
        items_per_list: Dict[str, int] = {}

        # Analyze each price list
        for price_book in price_books:
            # Status
            if price_book.get("status") == "active":
                active_lists += 1
            else:
                inactive_lists += 1

            # Currency
            currency = price_book.get("currency_code", "USD")
            lists_by_currency[currency] += 1

            # Items count
            item_count = len(price_book.get("pricebook_items", []))
            total_items_mapped += item_count
            items_per_list[price_book.get("name", "Unknown")] = item_count

        # Calculate coverage (would need total items count)
        # For now, use a placeholder
        coverage_percentage = 0.0

        logger.info(
            f"✅ Zoho price lists: {total_lists} total, {total_items_mapped} items mapped"
        )

        return PriceListStatistics(
            total_lists=total_lists,
            active_lists=active_lists,
            inactive_lists=inactive_lists,
            total_items_mapped=total_items_mapped,
            lists_by_currency=dict(lists_by_currency),
            coverage_percentage=coverage_percentage,
            items_per_list=items_per_list
        )

    async def collect_stock_stats(self) -> StockStatistics:
        """
        Collect stock/inventory statistics from Zoho Inventory

        Returns:
            StockStatistics with stock levels and values

        جمع إحصائيات المخزون
        """
        logger.info("Collecting Zoho stock statistics...")

        # Fetch all items with stock information
        items = await self.client.paginated_fetch(
            api_type=ZohoAPI.INVENTORY,
            endpoint="items",
            page_size=200
        )

        # Initialize counters
        total_items_in_stock = 0
        out_of_stock_count = 0
        low_stock_count = 0
        total_stock_value = 0.0
        total_stock_quantity = 0.0
        items_with_negative_stock = 0
        total_reserved_stock = 0.0

        by_warehouse: Dict[str, int] = defaultdict(int)

        # Analyze stock for each item
        for item in items:
            stock = float(item.get("actual_available_stock", 0) or 0)
            rate = float(item.get("rate", 0) or 0)
            reorder_level = float(item.get("reorder_level", 0) or 0)

            # Stock status
            if stock > 0:
                total_items_in_stock += 1
                total_stock_quantity += stock
            elif stock == 0:
                out_of_stock_count += 1
            elif stock < 0:
                items_with_negative_stock += 1

            # Low stock
            if 0 < stock <= reorder_level:
                low_stock_count += 1

            # Stock value
            total_stock_value += stock * rate

            # Reserved stock (if available)
            reserved = float(item.get("reserved_stock", 0) or 0)
            total_reserved_stock += reserved

            # Warehouse breakdown (simplified - Zoho has warehouse-specific data)
            warehouse = item.get("warehouse_name", "Default")
            by_warehouse[warehouse] += 1

        # Calculate averages
        avg_stock = (
            total_stock_quantity / total_items_in_stock
            if total_items_in_stock > 0
            else 0.0
        )

        logger.info(
            f"✅ Zoho stock: {total_items_in_stock} items in stock, "
            f"{out_of_stock_count} out of stock"
        )

        return StockStatistics(
            total_items_in_stock=total_items_in_stock,
            out_of_stock_count=out_of_stock_count,
            low_stock_count=low_stock_count,
            total_stock_value=round(total_stock_value, 2),
            average_stock_per_item=round(avg_stock, 2),
            by_warehouse=dict(by_warehouse),
            items_with_negative_stock=items_with_negative_stock,
            total_reserved_stock=int(total_reserved_stock)
        )

    async def collect_image_stats(self) -> ImageStatistics:
        """
        Collect image statistics from Zoho Inventory

        Returns:
            ImageStatistics with image coverage

        جمع إحصائيات الصور
        """
        logger.info("Collecting Zoho image statistics...")

        # Fetch all items
        items = await self.client.paginated_fetch(
            api_type=ZohoAPI.INVENTORY,
            endpoint="items",
            page_size=200
        )

        # Initialize counters
        total_items = len(items)
        with_images = 0
        without_images = 0
        total_images_count = 0
        broken_links = 0

        # Analyze images for each item
        for item in items:
            # Check if item has images
            has_image = False

            # Check image fields
            if item.get("image_name") or item.get("image_document_id"):
                has_image = True
                with_images += 1
                total_images_count += 1

                # Check if image URL is accessible (simplified)
                image_url = item.get("image_url", "")
                if not image_url or image_url == "":
                    broken_links += 1

            if not has_image:
                without_images += 1

        # Calculate averages
        avg_images = (
            total_images_count / total_items
            if total_items > 0
            else 0.0
        )

        logger.info(
            f"✅ Zoho images: {with_images}/{total_items} items with images "
            f"({(with_images/total_items*100) if total_items > 0 else 0:.1f}%)"
        )

        return ImageStatistics(
            total_items=total_items,
            with_images=with_images,
            without_images=without_images,
            total_images_count=total_images_count,
            average_images_per_item=round(avg_images, 2),
            broken_image_links=broken_links
        )
