"""
Product Processor
=================

Processes and transforms Zoho product/item data.

معالج المنتجات - تحويل والتحقق من بيانات المنتجات

Author: TSH ERP Team
Date: November 6, 2025
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    """Safely convert value to Decimal, handling None, empty strings, and invalid values"""
    if value is None or value == '' or value == 'None':
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


class ProductProcessor:
    """
    Product data processor
    معالج بيانات المنتجات

    Validates, transforms, and prepares Zoho product data for local storage.
    """

    @staticmethod
    def validate(product_data: Dict[str, Any]) -> bool:
        """
        Validate product data

        Args:
            product_data: Zoho product data

        Returns:
            bool: True if valid
        """
        required_fields = ['item_id', 'name']

        for field in required_fields:
            if field not in product_data or not product_data[field]:
                logger.warning(f"Product missing required field: {field}")
                return False

        return True

    @staticmethod
    def transform(product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho product data to local format

        Args:
            product_data: Zoho product data

        Returns:
            dict: Transformed product data
        """
        transformed = {
            # IDs
            'zoho_item_id': product_data.get('item_id'),
            'sku': product_data.get('sku'),
            'product_code': product_data.get('product_code'),

            # Basic info
            'name': product_data.get('name'),
            'name_ar': product_data.get('name_ar'),  # Arabic name if available
            'description': product_data.get('description', ''),
            'description_ar': product_data.get('description_ar', ''),

            # Categorization
            'category': product_data.get('category_name'),
            'brand': product_data.get('brand'),
            'manufacturer': product_data.get('manufacturer'),
            'unit': product_data.get('unit'),

            # Pricing
            'rate': safe_decimal(product_data.get('rate')),
            'purchase_rate': safe_decimal(product_data.get('purchase_rate')),
            'cost_price': safe_decimal(product_data.get('purchase_rate')),
            'selling_price': safe_decimal(product_data.get('rate')),

            # Stock - Zoho returns 'actual_available_stock' and 'available_stock'
            'stock_on_hand': safe_decimal(product_data.get('actual_available_stock')),
            'available_stock': safe_decimal(product_data.get('available_stock')),
            'actual_available_stock': safe_decimal(product_data.get('actual_available_stock')),
            'reorder_level': safe_decimal(product_data.get('reorder_level')),

            # Attributes
            'is_taxable': product_data.get('is_taxable', False),
            'tax_id': product_data.get('tax_id'),
            'tax_percentage': safe_decimal(product_data.get('tax_percentage')),
            'is_returnable': product_data.get('is_returnable', True),

            # Status
            'status': product_data.get('status', 'active'),
            'is_active': product_data.get('status') == 'active',

            # Images
            'image_url': product_data.get('image_url'),
            'image_name': product_data.get('image_name'),
            'image_type': product_data.get('image_type'),

            # Tracking
            'track_inventory': product_data.get('is_combo_product', False) == False,
            'is_combo_product': product_data.get('is_combo_product', False),

            # Metadata
            'created_time': product_data.get('created_time'),
            'last_modified_time': product_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),

            # Raw data for reference
            'zoho_raw_data': product_data
        }

        return transformed

    @staticmethod
    def extract_variants(product_data: Dict[str, Any]) -> list:
        """
        Extract product variants if available

        Args:
            product_data: Zoho product data

        Returns:
            list: List of variant data
        """
        variants = []

        # Check if product has variants
        if 'variants' in product_data and product_data['variants']:
            for variant in product_data['variants']:
                variants.append({
                    'variant_id': variant.get('variant_id'),
                    'sku': variant.get('sku'),
                    'name': variant.get('name'),
                    'rate': Decimal(str(variant.get('rate', 0))),
                    'stock': Decimal(str(variant.get('stock', 0))),
                    'attributes': variant.get('attributes', {})
                })

        return variants

    @staticmethod
    def needs_update(
        existing_product: Dict[str, Any],
        new_product_data: Dict[str, Any]
    ) -> bool:
        """
        Check if product needs to be updated

        Args:
            existing_product: Existing product data in database
            new_product_data: New product data from Zoho

        Returns:
            bool: True if update is needed
        """
        # Compare last modified times
        existing_modified = existing_product.get('last_modified_time')
        new_modified = new_product_data.get('last_modified_time')

        if not existing_modified or not new_modified:
            return True

        return new_modified > existing_modified
