"""
Local Data Collector
====================

Collects statistics from TSH ERP local database (PostgreSQL).

جامع البيانات المحلية
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.migration_items import MigrationItem, ItemCategory
from app.models.migration_customers import MigrationCustomer
from app.models.migration_vendors import MigrationVendor
from app.models.price_lists import PriceList, PriceListItem
from app.models.migration_stock import MigrationStock
from app.tds.statistics.models import (
    ItemStatistics,
    CustomerStatistics,
    VendorStatistics,
    PriceListStatistics,
    StockStatistics,
    ImageStatistics,
    LocalStatistics,
)

logger = logging.getLogger(__name__)


class LocalDataCollector:
    """
    Collects comprehensive statistics from TSH ERP local database

    جامع إحصائيات شامل من قاعدة بيانات TSH ERP المحلية

    Features:
    - Queries PostgreSQL database directly
    - Aggregates statistics across all tables
    - Provides detailed breakdowns matching Zoho structure
    - Optimized queries for performance
    """

    def __init__(self, db: Session):
        """
        Initialize local data collector

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    async def collect_all_stats(self) -> LocalStatistics:
        """
        Collect all statistics from local database

        Returns:
            Complete LocalStatistics object with all entity statistics

        جمع جميع الإحصائيات من قاعدة البيانات المحلية
        """
        logger.info("Starting local statistics collection...")

        try:
            # Collect statistics for all entity types
            items_stats = await self.collect_items_stats()
            customers_stats = await self.collect_customer_stats()
            vendors_stats = await self.collect_vendor_stats()
            price_lists_stats = await self.collect_pricelist_stats()
            stock_stats = await self.collect_stock_stats()
            images_stats = await self.collect_image_stats()

            logger.info("✅ Local statistics collection completed")

            return LocalStatistics(
                items=items_stats,
                customers=customers_stats,
                vendors=vendors_stats,
                price_lists=price_lists_stats,
                stock=stock_stats,
                images=images_stats,
                collected_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Failed to collect local statistics: {e}", exc_info=True)
            raise

    async def collect_items_stats(self) -> ItemStatistics:
        """
        Collect item/product statistics from migration_items table

        Returns:
            ItemStatistics with counts, breakdowns, and aggregates

        جمع إحصائيات المنتجات
        """
        logger.info("Collecting local items statistics...")

        # Total counts
        total_count = self.db.query(func.count(MigrationItem.id)).scalar() or 0
        active_count = self.db.query(func.count(MigrationItem.id)).filter(
            MigrationItem.is_active == True
        ).scalar() or 0
        inactive_count = total_count - active_count

        # Images
        with_images_count = self.db.query(func.count(MigrationItem.id)).filter(
            MigrationItem.image_url.isnot(None),
            MigrationItem.image_url != ''
        ).scalar() or 0
        without_images_count = total_count - with_images_count

        # By category
        category_counts = self.db.query(
            ItemCategory.name_en,
            func.count(MigrationItem.id)
        ).join(
            ItemCategory,
            MigrationItem.category_id == ItemCategory.id
        ).group_by(ItemCategory.name_en).all()

        by_category = {name: count for name, count in category_counts}
        if not by_category:
            by_category = {"Uncategorized": total_count}

        # By brand (if you have brand field)
        by_brand: Dict[str, int] = {"No Brand": total_count}  # Placeholder

        # Price aggregates
        price_stats = self.db.query(
            func.avg(MigrationItem.selling_price_usd).label('avg_price'),
            func.sum(MigrationItem.selling_price_usd).label('total_price')
        ).first()

        average_price = float(price_stats.avg_price or 0) if price_stats else 0.0

        # Stock value (calculate from stock table if available)
        # For now, using placeholder
        total_stock_value = 0.0
        low_stock_count = 0
        out_of_stock_count = 0

        logger.info(
            f"✅ Local items: {total_count} total, {active_count} active, "
            f"{with_images_count} with images"
        )

        return ItemStatistics(
            total_count=total_count,
            active_count=active_count,
            inactive_count=inactive_count,
            with_images_count=with_images_count,
            without_images_count=without_images_count,
            by_category=by_category,
            by_brand=by_brand,
            average_price=round(average_price, 2),
            total_stock_value=round(total_stock_value, 2),
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count
        )

    async def collect_customer_stats(self) -> CustomerStatistics:
        """
        Collect customer statistics from migration_customers table

        Returns:
            CustomerStatistics with counts and breakdowns

        جمع إحصائيات العملاء
        """
        logger.info("Collecting local customer statistics...")

        # Total counts
        total_count = self.db.query(func.count(MigrationCustomer.id)).scalar() or 0
        active_count = self.db.query(func.count(MigrationCustomer.id)).filter(
            MigrationCustomer.is_active == True
        ).scalar() or 0
        inactive_count = total_count - active_count

        # By type (if you have customer type field)
        by_type: Dict[str, int] = {"regular": total_count}  # Placeholder

        # By country
        country_counts = self.db.query(
            MigrationCustomer.country,
            func.count(MigrationCustomer.id)
        ).group_by(MigrationCustomer.country).all()

        by_country = {country or "Unknown": count for country, count in country_counts}

        # By price list
        pricelist_counts = self.db.query(
            PriceList.name_en,
            func.count(MigrationCustomer.id)
        ).join(
            PriceList,
            MigrationCustomer.price_list_id == PriceList.id,
            isouter=True
        ).group_by(PriceList.name_en).all()

        by_price_list = {name or "Default": count for name, count in pricelist_counts}

        # Credit limit aggregates
        credit_stats = self.db.query(
            func.sum(MigrationCustomer.credit_limit_usd).label('total'),
            func.avg(MigrationCustomer.credit_limit_usd).label('average'),
            func.count(MigrationCustomer.id).filter(
                MigrationCustomer.credit_limit_usd > 0
            ).label('count')
        ).first()

        total_credit_limit = float(credit_stats.total or 0) if credit_stats else 0.0
        average_credit_limit = float(credit_stats.average or 0) if credit_stats else 0.0

        # Outstanding balance (placeholder - need to join with invoices table)
        with_outstanding_balance = 0

        logger.info(
            f"✅ Local customers: {total_count} total, {active_count} active"
        )

        return CustomerStatistics(
            total_count=total_count,
            active_count=active_count,
            inactive_count=inactive_count,
            by_type=by_type,
            by_country=by_country,
            by_price_list=by_price_list,
            total_credit_limit=round(total_credit_limit, 2),
            with_outstanding_balance=with_outstanding_balance,
            average_credit_limit=round(average_credit_limit, 2)
        )

    async def collect_vendor_stats(self) -> VendorStatistics:
        """
        Collect vendor/supplier statistics from migration_vendors table

        Returns:
            VendorStatistics with counts and breakdowns

        جمع إحصائيات الموردين
        """
        logger.info("Collecting local vendor statistics...")

        # Total counts
        total_count = self.db.query(func.count(MigrationVendor.id)).scalar() or 0
        active_count = self.db.query(func.count(MigrationVendor.id)).filter(
            MigrationVendor.is_active == True
        ).scalar() or 0
        inactive_count = total_count - active_count

        # By country
        country_counts = self.db.query(
            MigrationVendor.country,
            func.count(MigrationVendor.id)
        ).group_by(MigrationVendor.country).all()

        by_country = {country or "Unknown": count for country, count in country_counts}

        # Payables (placeholder - need bills/payables table)
        total_payables = 0.0
        with_outstanding_payables = 0

        logger.info(
            f"✅ Local vendors: {total_count} total, {active_count} active"
        )

        return VendorStatistics(
            total_count=total_count,
            active_count=active_count,
            inactive_count=inactive_count,
            by_country=by_country,
            total_payables=round(total_payables, 2),
            with_outstanding_payables=with_outstanding_payables
        )

    async def collect_pricelist_stats(self) -> PriceListStatistics:
        """
        Collect price list statistics from price_lists table

        Returns:
            PriceListStatistics with counts and coverage

        جمع إحصائيات قوائم الأسعار
        """
        logger.info("Collecting local price list statistics...")

        # Total counts
        total_lists = self.db.query(func.count(PriceList.id)).scalar() or 0
        active_lists = self.db.query(func.count(PriceList.id)).filter(
            PriceList.is_active == True
        ).scalar() or 0
        inactive_lists = total_lists - active_lists

        # Total items mapped
        total_items_mapped = self.db.query(
            func.count(PriceListItem.id)
        ).scalar() or 0

        # By currency
        currency_counts = self.db.query(
            PriceList.currency,
            func.count(PriceList.id)
        ).group_by(PriceList.currency).all()

        lists_by_currency = {currency or "USD": count for currency, count in currency_counts}

        # Items per list
        items_per_list_data = self.db.query(
            PriceList.name_en,
            func.count(PriceListItem.id)
        ).join(
            PriceListItem,
            PriceList.id == PriceListItem.price_list_id,
            isouter=True
        ).group_by(PriceList.name_en).all()

        items_per_list = {name: count for name, count in items_per_list_data}

        # Calculate coverage
        total_items = self.db.query(func.count(MigrationItem.id)).scalar() or 0
        coverage_percentage = (
            (total_items_mapped / total_items * 100)
            if total_items > 0
            else 0.0
        )

        logger.info(
            f"✅ Local price lists: {total_lists} total, {total_items_mapped} items mapped"
        )

        return PriceListStatistics(
            total_lists=total_lists,
            active_lists=active_lists,
            inactive_lists=inactive_lists,
            total_items_mapped=total_items_mapped,
            lists_by_currency=lists_by_currency,
            coverage_percentage=round(coverage_percentage, 2),
            items_per_list=items_per_list
        )

    async def collect_stock_stats(self) -> StockStatistics:
        """
        Collect stock/inventory statistics from migration_stock table

        Returns:
            StockStatistics with stock levels and values

        جمع إحصائيات المخزون
        """
        logger.info("Collecting local stock statistics...")

        # Total items in stock
        total_items_in_stock = self.db.query(
            func.count(MigrationStock.id)
        ).filter(
            MigrationStock.quantity_available > 0
        ).scalar() or 0

        # Out of stock
        out_of_stock_count = self.db.query(
            func.count(MigrationStock.id)
        ).filter(
            MigrationStock.quantity_available == 0
        ).scalar() or 0

        # Low stock (where available < reorder_level)
        low_stock_count = self.db.query(
            func.count(MigrationStock.id)
        ).filter(
            and_(
                MigrationStock.quantity_available > 0,
                MigrationStock.quantity_available <= MigrationStock.reorder_level
            )
        ).scalar() or 0

        # Stock value (need to join with items for prices)
        # Placeholder for now
        total_stock_value = 0.0

        # Average stock per item
        avg_stock_query = self.db.query(
            func.avg(MigrationStock.quantity_available)
        ).filter(
            MigrationStock.quantity_available > 0
        ).scalar()

        average_stock_per_item = float(avg_stock_query or 0)

        # By warehouse (if you have warehouse field)
        by_warehouse: Dict[str, int] = {"Default": total_items_in_stock}

        # Negative stock
        items_with_negative_stock = self.db.query(
            func.count(MigrationStock.id)
        ).filter(
            MigrationStock.quantity_available < 0
        ).scalar() or 0

        # Reserved stock
        total_reserved_query = self.db.query(
            func.sum(MigrationStock.quantity_reserved)
        ).scalar()

        total_reserved_stock = int(total_reserved_query or 0)

        logger.info(
            f"✅ Local stock: {total_items_in_stock} items in stock, "
            f"{out_of_stock_count} out of stock"
        )

        return StockStatistics(
            total_items_in_stock=total_items_in_stock,
            out_of_stock_count=out_of_stock_count,
            low_stock_count=low_stock_count,
            total_stock_value=round(total_stock_value, 2),
            average_stock_per_item=round(average_stock_per_item, 2),
            by_warehouse=by_warehouse,
            items_with_negative_stock=items_with_negative_stock,
            total_reserved_stock=total_reserved_stock
        )

    async def collect_image_stats(self) -> ImageStatistics:
        """
        Collect image statistics from migration_items table

        Returns:
            ImageStatistics with image coverage

        جمع إحصائيات الصور
        """
        logger.info("Collecting local image statistics...")

        # Total items
        total_items = self.db.query(func.count(MigrationItem.id)).scalar() or 0

        # With images
        with_images = self.db.query(func.count(MigrationItem.id)).filter(
            MigrationItem.image_url.isnot(None),
            MigrationItem.image_url != ''
        ).scalar() or 0

        # Without images
        without_images = total_items - with_images

        # Total images count (if you store multiple images per item)
        # For now, assuming 1 image per item
        total_images_count = with_images

        # Average images per item
        average_images_per_item = (
            total_images_count / total_items
            if total_items > 0
            else 0.0
        )

        # Broken links (placeholder - would need to verify URLs)
        broken_image_links = 0

        logger.info(
            f"✅ Local images: {with_images}/{total_items} items with images "
            f"({(with_images/total_items*100) if total_items > 0 else 0:.1f}%)"
        )

        return ImageStatistics(
            total_items=total_items,
            with_images=with_images,
            without_images=without_images,
            total_images_count=total_images_count,
            average_images_per_item=round(average_images_per_item, 2),
            broken_image_links=broken_image_links
        )
