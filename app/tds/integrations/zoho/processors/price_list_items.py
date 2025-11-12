"""
Price List Items Processor
===========================

Processes and transforms Zoho Books price list items (product-specific prices).

معالج عناصر قوائم الأسعار - يربط المنتجات بقوائم الأسعار مع الأسعار المحددة

This processor syncs individual product prices for each price list from Zoho Books.

Zoho Books API Structure:
- GET /pricebooks/{pricebook_id}
- Response contains 'pricebook_items' array with product prices

Database Structure:
- price_list_items table links migration_items to price_lists with specific prices

Author: Claude Code (Senior Software Engineer AI)
Date: November 7, 2025
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal, InvalidOperation
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_decimal(value, default=0):
    """
    Safely convert value to Decimal, handling invalid inputs.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Decimal: Converted value or default
    """
    try:
        if value is None or value == '' or value == 'None':
            return Decimal(str(default))
        # Handle various number formats
        str_value = str(value).strip().replace(',', '')
        if not str_value:
            return Decimal(str(default))
        return Decimal(str_value)
    except (ValueError, TypeError, InvalidOperation) as e:
        logger.warning(f"Invalid decimal value: {value}, using {default}. Error: {e}")
        return Decimal(str(default))


def parse_discount_percentage(discount_str: str) -> Decimal:
    """
    Parse discount percentage from string.

    Handles formats like: "10%", "10", 10, 10.5

    Args:
        discount_str: Discount string from Zoho

    Returns:
        Decimal: Discount percentage (e.g., 10.0 for 10%)
    """
    if not discount_str or discount_str == '':
        return Decimal('0')

    try:
        # Remove % sign if present
        str_val = str(discount_str).strip().replace('%', '')
        return safe_decimal(str_val, 0)
    except Exception as e:
        logger.warning(f"Failed to parse discount: {discount_str}, error: {e}")
        return Decimal('0')


class PriceListItemsProcessor:
    """
    Price List Items data processor
    معالج بيانات عناصر قوائم الأسعار

    Validates, transforms, and prepares Zoho Books price list item data for local storage.
    Links products to price lists with specific prices.
    """

    @staticmethod
    def validate(item_data: Dict[str, Any]) -> bool:
        """
        Validate price list item data from Zoho Books.

        Args:
            item_data: Zoho Books price list item data (pricebook_item)

        Returns:
            bool: True if valid, False otherwise
        """
        # Required fields from Zoho Books pricebook_items
        required_fields = ['item_id', 'pricebook_rate']

        for field in required_fields:
            if field not in item_data or item_data[field] is None:
                logger.warning(f"Price list item missing required field: {field}")
                return False

        # Validate price is numeric and > 0
        try:
            price = safe_decimal(item_data.get('pricebook_rate', 0))
            if price < 0:
                logger.warning(f"Invalid price: {price} (must be >= 0)")
                return False
        except Exception as e:
            logger.warning(f"Invalid price value: {item_data.get('pricebook_rate')}, error: {e}")
            return False

        return True

    @staticmethod
    def transform(
        item_data: Dict[str, Any],
        price_list_local_id: int,
        migration_item_local_id: int
    ) -> Dict[str, Any]:
        """
        Transform Zoho Books price list item to local format.

        Zoho Books API Structure (pricebook_item):
        {
            "pricebook_item_id": "2646610000054858555",
            "item_id": "2646610000000113286",
            "name": "Product Name",
            "pricebook_rate": 55000.0,
            "pricebook_discount": "10",  # Can be percentage string like "10%" or number
            "price_brackets": []  # Quantity-based pricing (may be empty)
        }

        Local Database Structure (price_list_items):
        - price_list_id: FK to price_lists.id
        - item_id: FK to migration_items.id
        - unit_price: The price for this item
        - discount_percentage: Optional discount
        - minimum_quantity: Minimum quantity (default 1)
        - is_active: Whether this price is active

        Args:
            item_data: Zoho Books price list item data
            price_list_local_id: Local price_lists.id (looked up from zoho_price_list_id)
            migration_item_local_id: Local migration_items.id (looked up from zoho_item_id)

        Returns:
            dict: Transformed price list item data for local database
        """
        # Extract discount percentage
        discount = parse_discount_percentage(item_data.get('pricebook_discount', ''))

        transformed = {
            # Foreign Keys
            'price_list_id': price_list_local_id,
            'item_id': migration_item_local_id,

            # Price Data
            'unit_price': safe_decimal(item_data.get('pricebook_rate', 0)),
            'discount_percentage': discount,

            # Quantity (default to 1, price_brackets may have higher quantities)
            'minimum_quantity': safe_decimal(1, 1),

            # Status
            'is_active': True,

            # Timestamps
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        logger.debug(
            f"✅ Transformed price list item: "
            f"item_id={migration_item_local_id}, "
            f"price_list_id={price_list_local_id}, "
            f"price={transformed['unit_price']}"
        )

        return transformed

    @staticmethod
    def extract_pricebook_items(pricebook_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract pricebook_items array from Zoho pricebook details response.

        Args:
            pricebook_details: Full Zoho pricebook details response

        Returns:
            list: Array of pricebook_items
        """
        # Zoho Books API returns pricebook object with pricebook_items array
        pricebook = pricebook_details.get('pricebook', {})
        items = pricebook.get('pricebook_items', [])

        logger.info(f"📦 Extracted {len(items)} pricebook items from Zoho response")
        return items

    @staticmethod
    def process_price_brackets(
        item_data: Dict[str, Any],
        price_list_local_id: int,
        migration_item_local_id: int
    ) -> List[Dict[str, Any]]:
        """
        Process price brackets (quantity-based pricing) if present.

        Zoho Books supports tiered pricing based on quantity.
        Example:
        price_brackets: [
            {"minimum_quantity": 10, "rate": 50.0},
            {"minimum_quantity": 50, "rate": 45.0},
            {"minimum_quantity": 100, "rate": 40.0}
        ]

        Args:
            item_data: Zoho Books price list item data
            price_list_local_id: Local price list ID
            migration_item_local_id: Local item ID

        Returns:
            list: Multiple price_list_items records for different quantities
        """
        price_brackets = item_data.get('price_brackets', [])

        if not price_brackets or len(price_brackets) == 0:
            # No quantity-based pricing, return single record
            return [PriceListItemsProcessor.transform(
                item_data,
                price_list_local_id,
                migration_item_local_id
            )]

        # Process each price bracket as separate record
        records = []
        for bracket in price_brackets:
            # Create a modified item_data with bracket-specific price and quantity
            bracket_item = {
                **item_data,
                'pricebook_rate': bracket.get('rate', item_data.get('pricebook_rate')),
            }

            transformed = PriceListItemsProcessor.transform(
                bracket_item,
                price_list_local_id,
                migration_item_local_id
            )

            # Override minimum_quantity from bracket
            transformed['minimum_quantity'] = safe_decimal(
                bracket.get('minimum_quantity', 1),
                1
            )

            records.append(transformed)

        logger.info(
            f"📊 Processed {len(records)} price brackets for item "
            f"{migration_item_local_id} in price list {price_list_local_id}"
        )

        return records


# ============================================================================
# Batch Processing Utilities
# ============================================================================

def batch_transform_price_list_items(
    items: List[Dict[str, Any]],
    price_list_local_id: int,
    zoho_to_local_item_map: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Transform multiple price list items in batch.

    Args:
        items: List of Zoho Books pricebook_items
        price_list_local_id: Local price list ID
        zoho_to_local_item_map: Map of zoho_item_id -> migration_items.id

    Returns:
        list: List of transformed price list items (flattened, including price brackets)
    """
    processor = PriceListItemsProcessor()
    transformed = []
    skipped = 0

    for item in items:
        try:
            # Validate item
            if not processor.validate(item):
                logger.warning(f"⏭️  Skipping invalid item: {item.get('name', 'Unknown')}")
                skipped += 1
                continue

            # Lookup local item_id from zoho_item_id
            zoho_item_id = item.get('item_id')
            migration_item_local_id = zoho_to_local_item_map.get(zoho_item_id)

            if not migration_item_local_id:
                logger.warning(
                    f"⏭️  Skipping item with unknown zoho_item_id: {zoho_item_id} "
                    f"({item.get('name', 'Unknown')})"
                )
                skipped += 1
                continue

            # Process item (including price brackets)
            records = processor.process_price_brackets(
                item,
                price_list_local_id,
                migration_item_local_id
            )

            transformed.extend(records)

        except Exception as e:
            logger.error(
                f"❌ Error transforming price list item {item.get('name', 'Unknown')}: {e}",
                exc_info=True
            )
            skipped += 1

    logger.info(
        f"✅ Batch transformed {len(transformed)} price list items "
        f"({skipped} skipped) for price list {price_list_local_id}"
    )

    return transformed
