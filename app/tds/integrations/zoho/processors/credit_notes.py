"""
Credit Note Processor
=====================

Processes and transforms Zoho credit note data.

معالج الإشعارات الدائنة - تحويل والتحقق من بيانات الإشعارات الدائنة

Author: TSH ERP Team
Date: November 15, 2025
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class CreditNoteProcessor:
    """
    Credit Note data processor
    معالج بيانات الإشعارات الدائنة

    Validates, transforms, and prepares Zoho credit note data for local storage.
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
    def validate(credit_note_data: Dict[str, Any]) -> bool:
        """
        Validate credit note data

        Args:
            credit_note_data: Zoho credit note data

        Returns:
            bool: True if valid
        """
        required_fields = ['creditnote_id', 'customer_id', 'creditnote_number']

        for field in required_fields:
            if field not in credit_note_data or not credit_note_data[field]:
                logger.warning(f"Credit note missing required field: {field}")
                return False

        return True

    @staticmethod
    def transform(credit_note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho credit note data to local format

        Args:
            credit_note_data: Zoho credit note data

        Returns:
            dict: Transformed credit note data
        """
        transformed = {
            # IDs
            'zoho_creditnote_id': credit_note_data.get('creditnote_id'),
            'zoho_customer_id': credit_note_data.get('customer_id'),
            'creditnote_number': credit_note_data.get('creditnote_number'),
            'reference_number': credit_note_data.get('reference_number'),

            # Customer info
            'customer_name': credit_note_data.get('customer_name'),
            'customer_id': credit_note_data.get('customer_id'),

            # Dates
            'creditnote_date': credit_note_data.get('date'),

            # Amounts
            'sub_total': CreditNoteProcessor._safe_decimal(credit_note_data.get('sub_total', 0)),
            'tax_total': CreditNoteProcessor._safe_decimal(credit_note_data.get('tax_total', 0)),
            'total': CreditNoteProcessor._safe_decimal(credit_note_data.get('total', 0)),
            'balance': CreditNoteProcessor._safe_decimal(credit_note_data.get('balance', 0)),
            'credits_applied': CreditNoteProcessor._safe_decimal(credit_note_data.get('credits_applied', 0)),
            'refunded_amount': CreditNoteProcessor._safe_decimal(credit_note_data.get('refunded_amount', 0)),

            # Discount
            'discount': CreditNoteProcessor._safe_decimal(credit_note_data.get('discount', 0)),
            'discount_type': credit_note_data.get('discount_type'),
            'is_discount_before_tax': credit_note_data.get('is_discount_before_tax', False),

            # Adjustment
            'adjustment': CreditNoteProcessor._safe_decimal(credit_note_data.get('adjustment', 0)),
            'adjustment_description': credit_note_data.get('adjustment_description'),

            # Currency
            'currency_id': credit_note_data.get('currency_id'),
            'currency_code': credit_note_data.get('currency_code'),
            'currency_symbol': credit_note_data.get('currency_symbol'),
            'exchange_rate': CreditNoteProcessor._safe_decimal(credit_note_data.get('exchange_rate', 1)),

            # Status
            'status': credit_note_data.get('status', 'draft'),
            'is_emailed': credit_note_data.get('is_emailed', False),

            # Reason
            'reason': credit_note_data.get('reason'),
            'notes': credit_note_data.get('notes'),

            # Related documents
            'invoice_id': credit_note_data.get('invoice_id'),
            'invoice_number': credit_note_data.get('invoice_number'),

            # Line items
            'line_items': credit_note_data.get('line_items', []),

            # Metadata
            'created_time': credit_note_data.get('created_time'),
            'last_modified_time': credit_note_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),

            # Raw data for reference
            'zoho_raw_data': credit_note_data
        }

        return transformed

    @staticmethod
    def needs_update(
        existing_credit_note: Dict[str, Any],
        new_credit_note_data: Dict[str, Any]
    ) -> bool:
        """
        Check if credit note needs to be updated

        Args:
            existing_credit_note: Existing credit note data in database
            new_credit_note_data: New credit note data from Zoho

        Returns:
            bool: True if update is needed
        """
        # Compare last modified times
        existing_modified = existing_credit_note.get('last_modified_time')
        new_modified = new_credit_note_data.get('last_modified_time')

        if not existing_modified or not new_modified:
            return True

        return new_modified > existing_modified

    @staticmethod
    def extract_line_items(credit_note_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and transform credit note line items

        Args:
            credit_note_data: Zoho credit note data

        Returns:
            list: List of transformed line items
        """
        line_items = []

        for item in credit_note_data.get('line_items', []):
            line_items.append({
                'line_item_id': item.get('line_item_id'),
                'item_id': item.get('item_id'),
                'item_name': item.get('name'),
                'description': item.get('description'),
                'quantity': CreditNoteProcessor._safe_decimal(item.get('quantity', 0)),
                'rate': CreditNoteProcessor._safe_decimal(item.get('rate', 0)),
                'unit': item.get('unit'),
                'tax_id': item.get('tax_id'),
                'tax_name': item.get('tax_name'),
                'tax_percentage': CreditNoteProcessor._safe_decimal(item.get('tax_percentage', 0)),
                'item_total': CreditNoteProcessor._safe_decimal(item.get('item_total', 0)),
            })

        return line_items
