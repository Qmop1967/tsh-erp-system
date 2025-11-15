"""
Invoice Processor
=================

Processes and transforms Zoho invoice data.

معالج الفواتير - تحويل والتحقق من بيانات الفواتير

Author: TSH ERP Team
Date: November 15, 2025
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """
    Invoice data processor
    معالج بيانات الفواتير

    Validates, transforms, and prepares Zoho invoice data for local storage.
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
    def validate(invoice_data: Dict[str, Any]) -> bool:
        """
        Validate invoice data

        Args:
            invoice_data: Zoho invoice data

        Returns:
            bool: True if valid
        """
        required_fields = ['invoice_id', 'customer_id', 'invoice_number']

        for field in required_fields:
            if field not in invoice_data or not invoice_data[field]:
                logger.warning(f"Invoice missing required field: {field}")
                return False

        # Validate line items exist
        if 'line_items' not in invoice_data or not invoice_data['line_items']:
            logger.warning("Invoice must have at least one line item")
            return False

        return True

    @staticmethod
    def transform(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho invoice data to local format

        Args:
            invoice_data: Zoho invoice data

        Returns:
            dict: Transformed invoice data
        """
        transformed = {
            # IDs
            'zoho_invoice_id': invoice_data.get('invoice_id'),
            'zoho_customer_id': invoice_data.get('customer_id'),
            'invoice_number': invoice_data.get('invoice_number'),
            'reference_number': invoice_data.get('reference_number'),

            # Customer info
            'customer_name': invoice_data.get('customer_name'),
            'customer_id': invoice_data.get('customer_id'),

            # Dates
            'invoice_date': invoice_data.get('date'),
            'due_date': invoice_data.get('due_date'),
            'payment_expected_date': invoice_data.get('payment_expected_date'),

            # Amounts
            'sub_total': InvoiceProcessor._safe_decimal(invoice_data.get('sub_total', 0)),
            'tax_total': InvoiceProcessor._safe_decimal(invoice_data.get('tax_total', 0)),
            'total': InvoiceProcessor._safe_decimal(invoice_data.get('total', 0)),
            'balance': InvoiceProcessor._safe_decimal(invoice_data.get('balance', 0)),
            'credits_applied': InvoiceProcessor._safe_decimal(invoice_data.get('credits_applied', 0)),
            'payment_made': InvoiceProcessor._safe_decimal(invoice_data.get('payment_made', 0)),
            'write_off_amount': InvoiceProcessor._safe_decimal(invoice_data.get('write_off_amount', 0)),

            # Discount
            'discount': InvoiceProcessor._safe_decimal(invoice_data.get('discount', 0)),
            'discount_type': invoice_data.get('discount_type'),
            'is_discount_before_tax': invoice_data.get('is_discount_before_tax', False),

            # Adjustment
            'adjustment': InvoiceProcessor._safe_decimal(invoice_data.get('adjustment', 0)),
            'adjustment_description': invoice_data.get('adjustment_description'),

            # Currency
            'currency_id': invoice_data.get('currency_id'),
            'currency_code': invoice_data.get('currency_code'),
            'currency_symbol': invoice_data.get('currency_symbol'),
            'exchange_rate': InvoiceProcessor._safe_decimal(invoice_data.get('exchange_rate', 1)),

            # Status
            'status': invoice_data.get('status', 'draft'),
            'payment_status': invoice_data.get('payment_status', 'unpaid'),
            'is_viewed_by_client': invoice_data.get('is_viewed_by_client', False),
            'is_emailed': invoice_data.get('is_emailed', False),

            # Sales person
            'salesperson_id': invoice_data.get('salesperson_id'),
            'salesperson_name': invoice_data.get('salesperson_name'),

            # Terms and notes
            'terms': invoice_data.get('terms'),
            'notes': invoice_data.get('notes'),
            'customer_notes': invoice_data.get('customer_notes'),

            # Shipping
            'shipping_charge': InvoiceProcessor._safe_decimal(invoice_data.get('shipping_charge', 0)),

            # Line items
            'line_items': invoice_data.get('line_items', []),

            # Metadata
            'created_time': invoice_data.get('created_time'),
            'last_modified_time': invoice_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),

            # Raw data for reference
            'zoho_raw_data': invoice_data
        }

        return transformed

    @staticmethod
    def needs_update(
        existing_invoice: Dict[str, Any],
        new_invoice_data: Dict[str, Any]
    ) -> bool:
        """
        Check if invoice needs to be updated

        Args:
            existing_invoice: Existing invoice data in database
            new_invoice_data: New invoice data from Zoho

        Returns:
            bool: True if update is needed
        """
        # Compare last modified times
        existing_modified = existing_invoice.get('last_modified_time')
        new_modified = new_invoice_data.get('last_modified_time')

        if not existing_modified or not new_modified:
            return True

        return new_modified > existing_modified

    @staticmethod
    def extract_line_items(invoice_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and transform invoice line items

        Args:
            invoice_data: Zoho invoice data

        Returns:
            list: List of transformed line items
        """
        line_items = []

        for item in invoice_data.get('line_items', []):
            line_items.append({
                'line_item_id': item.get('line_item_id'),
                'item_id': item.get('item_id'),
                'item_name': item.get('name'),
                'description': item.get('description'),
                'quantity': InvoiceProcessor._safe_decimal(item.get('quantity', 0)),
                'rate': InvoiceProcessor._safe_decimal(item.get('rate', 0)),
                'unit': item.get('unit'),
                'discount': InvoiceProcessor._safe_decimal(item.get('discount', 0)),
                'tax_id': item.get('tax_id'),
                'tax_name': item.get('tax_name'),
                'tax_type': item.get('tax_type'),
                'tax_percentage': InvoiceProcessor._safe_decimal(item.get('tax_percentage', 0)),
                'item_total': InvoiceProcessor._safe_decimal(item.get('item_total', 0)),
            })

        return line_items
