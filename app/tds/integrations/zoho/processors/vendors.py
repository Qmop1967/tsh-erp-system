"""
Vendor Processor
================

Processes and transforms Zoho vendor/supplier data.

معالج الموردين - تحويل والتحقق من بيانات الموردين

Author: TSH ERP Team
Date: November 15, 2025
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class VendorProcessor:
    """
    Vendor data processor
    معالج بيانات الموردين

    Validates, transforms, and prepares Zoho vendor data for local storage.
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
    def validate(vendor_data: Dict[str, Any]) -> bool:
        """
        Validate vendor data

        Args:
            vendor_data: Zoho vendor data

        Returns:
            bool: True if valid
        """
        required_fields = ['contact_id', 'contact_name']

        for field in required_fields:
            if field not in vendor_data or not vendor_data[field]:
                logger.warning(f"Vendor missing required field: {field}")
                return False

        return True

    @staticmethod
    def transform(vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho vendor data to local format

        Args:
            vendor_data: Zoho vendor data

        Returns:
            dict: Transformed vendor data
        """
        transformed = {
            # IDs
            'zoho_vendor_id': vendor_data.get('contact_id'),
            'vendor_name': vendor_data.get('contact_name'),
            'company_name': vendor_data.get('company_name'),

            # Contact information
            'email': vendor_data.get('email'),
            'phone': vendor_data.get('phone'),
            'mobile': vendor_data.get('mobile'),
            'website': vendor_data.get('website'),

            # Contact persons
            'contact_persons': vendor_data.get('contact_persons', []),

            # Address
            'billing_address': vendor_data.get('billing_address', {}),
            'shipping_address': vendor_data.get('shipping_address', {}),

            # Financial
            'currency_id': vendor_data.get('currency_id'),
            'currency_code': vendor_data.get('currency_code'),
            'outstanding_payable_amount': VendorProcessor._safe_decimal(
                vendor_data.get('outstanding_payable_amount', 0)
            ),
            'unused_credits': VendorProcessor._safe_decimal(
                vendor_data.get('unused_credits', 0)
            ),

            # Payment terms
            'payment_terms': vendor_data.get('payment_terms'),
            'payment_terms_label': vendor_data.get('payment_terms_label'),

            # Tax
            'tax_id_type': vendor_data.get('tax_id_type'),
            'tax_id_value': vendor_data.get('tax_id_value'),
            'tds_tax_id': vendor_data.get('tds_tax_id'),

            # Status
            'status': vendor_data.get('status', 'active'),
            'is_active': vendor_data.get('status') == 'active',
            'vendor_type': vendor_data.get('vendor_type'),

            # Notes
            'notes': vendor_data.get('notes'),

            # Custom fields
            'custom_fields': vendor_data.get('custom_fields', []),

            # Metadata
            'created_time': vendor_data.get('created_time'),
            'last_modified_time': vendor_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),

            # Raw data for reference
            'zoho_raw_data': vendor_data
        }

        return transformed

    @staticmethod
    def needs_update(
        existing_vendor: Dict[str, Any],
        new_vendor_data: Dict[str, Any]
    ) -> bool:
        """
        Check if vendor needs to be updated

        Args:
            existing_vendor: Existing vendor data in database
            new_vendor_data: New vendor data from Zoho

        Returns:
            bool: True if update is needed
        """
        # Compare last modified times
        existing_modified = existing_vendor.get('last_modified_time')
        new_modified = new_vendor_data.get('last_modified_time')

        if not existing_modified or not new_modified:
            return True

        return new_modified > existing_modified
