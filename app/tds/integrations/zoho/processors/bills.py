"""
Bill Processor
==============

Processes and transforms Zoho purchase bill data.

معالج الفواتير الشرائية - تحويل والتحقق من بيانات فواتير المشتريات

Author: TSH ERP Team
Date: November 15, 2025
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class BillProcessor:
    """
    Purchase Bill data processor
    معالج بيانات فواتير المشتريات

    Validates, transforms, and prepares Zoho bill data for local storage.
    """

    @staticmethod
    def _safe_decimal(value: Any) -> Decimal:
        """
        Safely convert value to Decimal, handling empty strings and None

        Args:
            value: Value to convert

        Returns:
            Decimal: Converted value or Decimal('0') if invalid
        """
        if value is None or value == '' or value == 'None':
            return Decimal('0')
        try:
            return Decimal(str(value))
        except (ValueError, TypeError, Exception):
            logger.warning(f"Invalid decimal value: {value}, using 0")
            return Decimal('0')

    @staticmethod
    def validate(bill_data: Dict[str, Any]) -> bool:
        """
        Validate bill data

        Args:
            bill_data: Zoho bill data

        Returns:
            bool: True if valid
        """
        required_fields = ['bill_id', 'vendor_id', 'bill_number']

        for field in required_fields:
            if field not in bill_data or not bill_data[field]:
                logger.warning(f"Bill missing required field: {field}")
                return False

        # Validate line items exist
        if 'line_items' not in bill_data or not bill_data['line_items']:
            logger.warning("Bill must have at least one line item")
            return False

        return True

    @staticmethod
    def transform(bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho bill data to local format

        Args:
            bill_data: Zoho bill data

        Returns:
            dict: Transformed bill data
        """
        transformed = {
            # IDs
            'zoho_bill_id': bill_data.get('bill_id'),
            'zoho_vendor_id': bill_data.get('vendor_id'),
            'bill_number': bill_data.get('bill_number'),
            'reference_number': bill_data.get('reference_number'),

            # Vendor info
            'vendor_name': bill_data.get('vendor_name'),
            'vendor_id': bill_data.get('vendor_id'),

            # Purchase Order reference
            'purchaseorder_ids': bill_data.get('purchaseorder_ids', []),

            # Dates
            'bill_date': bill_data.get('date'),
            'due_date': bill_data.get('due_date'),

            # Amounts
            'sub_total': BillProcessor._safe_decimal(bill_data.get('sub_total', 0)),
            'tax_total': BillProcessor._safe_decimal(bill_data.get('tax_total', 0)),
            'total': BillProcessor._safe_decimal(bill_data.get('total', 0)),
            'balance': BillProcessor._safe_decimal(bill_data.get('balance', 0)),
            'payment_made': BillProcessor._safe_decimal(bill_data.get('payment_made', 0)),
            'vendor_credits_applied': BillProcessor._safe_decimal(bill_data.get('vendor_credits_applied', 0)),

            # Discount
            'discount': BillProcessor._safe_decimal(bill_data.get('discount', 0)),
            'discount_type': bill_data.get('discount_type'),
            'is_discount_before_tax': bill_data.get('is_discount_before_tax', False),

            # Adjustment
            'adjustment': BillProcessor._safe_decimal(bill_data.get('adjustment', 0)),
            'adjustment_description': bill_data.get('adjustment_description'),

            # Currency
            'currency_id': bill_data.get('currency_id'),
            'currency_code': bill_data.get('currency_code'),
            'currency_symbol': bill_data.get('currency_symbol'),
            'exchange_rate': BillProcessor._safe_decimal(bill_data.get('exchange_rate', 1)),

            # Status
            'status': bill_data.get('status', 'draft'),
            'payment_status': bill_data.get('payment_status', 'unpaid'),

            # Notes
            'notes': bill_data.get('notes'),

            # Line items
            'line_items': bill_data.get('line_items', []),

            # Metadata
            'created_time': bill_data.get('created_time'),
            'last_modified_time': bill_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),

            # Raw data for reference
            'zoho_raw_data': bill_data
        }

        return transformed

    @staticmethod
    def needs_update(
        existing_bill: Dict[str, Any],
        new_bill_data: Dict[str, Any]
    ) -> bool:
        """
        Check if bill needs to be updated

        Args:
            existing_bill: Existing bill data in database
            new_bill_data: New bill data from Zoho

        Returns:
            bool: True if update is needed
        """
        # Compare last modified times
        existing_modified = existing_bill.get('last_modified_time')
        new_modified = new_bill_data.get('last_modified_time')

        if not existing_modified or not new_modified:
            return True

        return new_modified > existing_modified

    @staticmethod
    def extract_line_items(bill_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and transform bill line items

        Args:
            bill_data: Zoho bill data

        Returns:
            list: List of transformed line items
        """
        line_items = []

        for item in bill_data.get('line_items', []):
            line_items.append({
                'line_item_id': item.get('line_item_id'),
                'item_id': item.get('item_id'),
                'item_name': item.get('name'),
                'description': item.get('description'),
                'account_id': item.get('account_id'),
                'account_name': item.get('account_name'),
                'quantity': BillProcessor._safe_decimal(item.get('quantity', 0)),
                'rate': BillProcessor._safe_decimal(item.get('rate', 0)),
                'unit': item.get('unit'),
                'tax_id': item.get('tax_id'),
                'tax_name': item.get('tax_name'),
                'tax_percentage': BillProcessor._safe_decimal(item.get('tax_percentage', 0)),
                'item_total': BillProcessor._safe_decimal(item.get('item_total', 0)),
            })

        return line_items
