"""
Price List Processor
====================

Processes and transforms Zoho Books price list data.

معالج قوائم الأسعار - تحويل والتحقق من بيانات قوائم الأسعار من Zoho Books

TSH Multi-Price System:
- Wholesale A (USD)
- Wholesale B (USD)
- Retailer (USD)
- Technical IQD (IQD)
- Technical USD (USD)
- Consumer IQD (IQD)

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


class PriceListProcessor:
    """
    Price List data processor
    معالج بيانات قوائم الأسعار

    Validates, transforms, and prepares Zoho Books price list data for local storage.
    """

    @staticmethod
    def validate(pricelist_data: Dict[str, Any]) -> bool:
        """
        Validate price list data from Zoho Books.

        Args:
            pricelist_data: Zoho Books price list data

        Returns:
            bool: True if valid, False otherwise
        """
        # Zoho Books API returns 'name' not 'pricebook_name'
        required_fields = ['pricebook_id', 'name']

        for field in required_fields:
            if field not in pricelist_data or not pricelist_data[field]:
                logger.warning(f"Price list missing required field: {field}")
                return False

        return True

    @staticmethod
    def transform(pricelist_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho Books price list data to local format.

        Zoho Books API Structure:
        {
            "pricebook_id": "string",
            "name": "string",  # NOTE: Actual field is 'name' not 'pricebook_name'
            "description": "string",
            "currency_code": "USD",
            "status": "active"  # active or inactive
        }

        Args:
            pricelist_data: Zoho Books price list data

        Returns:
            dict: Transformed price list data for local database
        """
        # Determine price list code from name
        # NOTE: Zoho Books returns 'name' not 'pricebook_name'
        name = pricelist_data.get('name', '').lower()
        code = PriceListProcessor._determine_price_list_code(name)

        transformed = {
            # IDs
            'zoho_price_list_id': pricelist_data.get('pricebook_id'),
            'code': code,

            # Names
            'name': pricelist_data.get('name'),
            'name_en': pricelist_data.get('name'),
            'name_ar': PriceListProcessor._get_arabic_name(name),

            # Descriptions
            'description_en': pricelist_data.get('description', ''),
            'description_ar': PriceListProcessor._get_arabic_description(name),

            # Currency
            'currency': pricelist_data.get('currency_code', 'USD'),

            # Status
            'is_default': pricelist_data.get('is_default', False),
            'is_active': pricelist_data.get('status') == 'active',

            # Sync metadata
            'zoho_last_sync': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        logger.debug(f"✅ Transformed price list: {transformed['name']} ({code})")
        return transformed

    @staticmethod
    def transform_price_item(item_data: Dict[str, Any], pricelist_id: int, product_id: int) -> Dict[str, Any]:
        """
        Transform individual price list item (product price).

        Args:
            item_data: Zoho Books price list item data
            pricelist_id: Local price list ID
            product_id: Local product ID

        Returns:
            dict: Transformed product price data
        """
        transformed = {
            'product_id': product_id,
            'pricing_list_id': pricelist_id,
            'price': safe_decimal(item_data.get('rate', 0)),
            'discount_percentage': safe_decimal(item_data.get('discount_percentage', 0)),
            'minimum_quantity': int(item_data.get('minimum_quantity', 1)),
            'is_negotiable': item_data.get('is_negotiable', True),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        return transformed

    @staticmethod
    def _determine_price_list_code(name: str) -> str:
        """
        Determine price list code from name.

        Args:
            name: Price list name

        Returns:
            str: Price list code (wholesale_a, wholesale_b, etc.)
        """
        name_lower = name.lower()

        if 'wholesale a' in name_lower or 'wholesale_a' in name_lower:
            return 'wholesale_a'
        elif 'wholesale b' in name_lower or 'wholesale_b' in name_lower:
            return 'wholesale_b'
        elif 'retailer' in name_lower or 'retail' in name_lower:
            return 'retailer'
        elif 'technical' in name_lower and ('iqd' in name_lower or 'dinar' in name_lower):
            return 'technical_iqd'
        elif 'technical' in name_lower and ('usd' in name_lower or 'dollar' in name_lower):
            return 'technical_usd'
        elif 'consumer' in name_lower or 'standard' in name_lower:
            return 'consumer_iqd'
        else:
            # Default fallback
            return 'custom'

    @staticmethod
    def _get_arabic_name(name: str) -> str:
        """
        Get Arabic name for price list.

        Args:
            name: English name

        Returns:
            str: Arabic name
        """
        name_lower = name.lower()

        arabic_names = {
            'wholesale_a': 'جملة أ',
            'wholesale_b': 'جملة ب',
            'retailer': 'قطاعي',
            'technical_iqd': 'فني - دينار',
            'technical_usd': 'فني - دولار',
            'consumer_iqd': 'مستهلك - دينار'
        }

        for code, arabic in arabic_names.items():
            if code.replace('_', ' ') in name_lower:
                return arabic

        return name  # Fallback to English

    @staticmethod
    def _get_arabic_description(name: str) -> str:
        """
        Get Arabic description for price list.

        Args:
            name: English name

        Returns:
            str: Arabic description
        """
        name_lower = name.lower()

        descriptions = {
            'wholesale_a': 'أسعار الجملة للعملاء كبار الحجم',
            'wholesale_b': 'أسعار الجملة للعملاء متوسطي الحجم',
            'retailer': 'أسعار القطاعي للمتاجر الصغيرة',
            'technical_iqd': 'أسعار المنتجات الفنية - دينار عراقي',
            'technical_usd': 'أسعار المنتجات الفنية - دولار أمريكي',
            'consumer_iqd': 'أسعار المستهلك النهائي - دينار عراقي'
        }

        for code, description in descriptions.items():
            if code.replace('_', ' ') in name_lower:
                return description

        return ''  # Empty fallback


# ============================================================================
# Batch Processing Utilities
# ============================================================================

def batch_transform_pricelists(pricelists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform multiple price lists in batch.

    Args:
        pricelists: List of Zoho Books price list data

    Returns:
        list: List of transformed price lists
    """
    processor = PriceListProcessor()
    transformed = []

    for pricelist in pricelists:
        try:
            if processor.validate(pricelist):
                transformed_data = processor.transform(pricelist)
                transformed.append(transformed_data)
            else:
                logger.warning(f"Skipping invalid price list: {pricelist.get('pricebook_name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error transforming price list {pricelist.get('pricebook_name', 'Unknown')}: {e}", exc_info=True)

    logger.info(f"✅ Batch transformed {len(transformed)}/{len(pricelists)} price lists")
    return transformed
