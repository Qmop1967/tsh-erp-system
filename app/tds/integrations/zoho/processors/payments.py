"""
Payment Processor
=================

Processes and transforms Zoho customer payment data.

معالج المدفوعات - تحويل والتحقق من بيانات المدفوعات

Author: TSH ERP Team
Date: November 15, 2025
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """
    Customer Payment data processor
    معالج بيانات المدفوعات

    Validates, transforms, and prepares Zoho customer payment data for local storage.
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
    def validate(payment_data: Dict[str, Any]) -> bool:
        """
        Validate payment data

        Args:
            payment_data: Zoho payment data

        Returns:
            bool: True if valid
        """
        required_fields = ['payment_id', 'customer_id', 'amount']

        for field in required_fields:
            if field not in payment_data:
                logger.warning(f"Payment missing required field: {field}")
                return False

        # Validate amount is positive
        amount = PaymentProcessor._safe_decimal(payment_data.get('amount', 0))
        if amount <= 0:
            logger.warning(f"Payment has invalid amount: {amount}")
            return False

        return True

    @staticmethod
    def transform(payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho payment data to local format

        Args:
            payment_data: Zoho payment data

        Returns:
            dict: Transformed payment data
        """
        transformed = {
            # IDs
            'zoho_payment_id': payment_data.get('payment_id'),
            'zoho_customer_id': payment_data.get('customer_id'),
            'payment_number': payment_data.get('payment_number'),
            'reference_number': payment_data.get('reference_number'),

            # Customer info
            'customer_name': payment_data.get('customer_name'),
            'customer_id': payment_data.get('customer_id'),

            # Payment details
            'payment_date': payment_data.get('date'),
            'payment_mode': payment_data.get('payment_mode'),
            'account_id': payment_data.get('account_id'),
            'account_name': payment_data.get('account_name'),

            # Amount
            'amount': PaymentProcessor._safe_decimal(payment_data.get('amount', 0)),
            'amount_applied': PaymentProcessor._safe_decimal(payment_data.get('amount_applied', 0)),
            'unused_amount': PaymentProcessor._safe_decimal(payment_data.get('unused_amount', 0)),

            # Currency
            'currency_id': payment_data.get('currency_id'),
            'currency_code': payment_data.get('currency_code'),
            'currency_symbol': payment_data.get('currency_symbol'),
            'exchange_rate': PaymentProcessor._safe_decimal(payment_data.get('exchange_rate', 1)),

            # Bank details
            'bank_charges': PaymentProcessor._safe_decimal(payment_data.get('bank_charges', 0)),
            'tax_amount_withheld': PaymentProcessor._safe_decimal(payment_data.get('tax_amount_withheld', 0)),

            # Notes
            'notes': payment_data.get('notes'),
            'description': payment_data.get('description'),

            # Applied invoices
            'invoices': payment_data.get('invoices', []),

            # Metadata
            'created_time': payment_data.get('created_time'),
            'last_modified_time': payment_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),

            # Raw data for reference
            'zoho_raw_data': payment_data
        }

        return transformed

    @staticmethod
    def needs_update(
        existing_payment: Dict[str, Any],
        new_payment_data: Dict[str, Any]
    ) -> bool:
        """
        Check if payment needs to be updated

        Args:
            existing_payment: Existing payment data in database
            new_payment_data: New payment data from Zoho

        Returns:
            bool: True if update is needed
        """
        # Compare last modified times
        existing_modified = existing_payment.get('last_modified_time')
        new_modified = new_payment_data.get('last_modified_time')

        if not existing_modified or not new_modified:
            return True

        return new_modified > existing_modified

    @staticmethod
    def extract_applied_invoices(payment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract invoices this payment was applied to

        Args:
            payment_data: Zoho payment data

        Returns:
            list: List of applied invoices
        """
        applied_invoices = []

        for invoice in payment_data.get('invoices', []):
            applied_invoices.append({
                'invoice_id': invoice.get('invoice_id'),
                'invoice_number': invoice.get('invoice_number'),
                'amount_applied': PaymentProcessor._safe_decimal(invoice.get('amount_applied', 0)),
                'tax_amount_withheld': PaymentProcessor._safe_decimal(invoice.get('tax_amount_withheld', 0)),
                'discount_amount': PaymentProcessor._safe_decimal(invoice.get('discount_amount', 0)),
            })

        return applied_invoices
