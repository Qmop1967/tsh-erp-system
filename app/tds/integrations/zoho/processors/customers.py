"""
Customer Processor
==================

Processes Zoho customer/contact data.

Author: TSH ERP Team
Date: November 6, 2025
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CustomerProcessor:
    """Customer data processor"""

    @staticmethod
    def validate(customer_data: Dict[str, Any]) -> bool:
        """Validate customer data"""
        required_fields = ['contact_id', 'contact_name']
        return all(field in customer_data for field in required_fields)

    @staticmethod
    def transform(customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform customer data"""
        return {
            'zoho_contact_id': customer_data.get('contact_id'),
            'name': customer_data.get('contact_name'),
            'company_name': customer_data.get('company_name'),
            'email': customer_data.get('email'),
            'phone': customer_data.get('phone'),
            'mobile': customer_data.get('mobile'),
            'website': customer_data.get('website'),

            # Address
            'billing_address': customer_data.get('billing_address', {}),
            'shipping_address': customer_data.get('shipping_address', {}),

            # Financial
            'currency_code': customer_data.get('currency_code'),
            'outstanding_receivable_amount': customer_data.get('outstanding_receivable_amount', 0),
            'credit_limit': customer_data.get('credit_limit', 0),

            # Owner/Salesperson Assignment
            # Zoho Books uses 'owner_id' to assign a user as the contact owner
            'zoho_owner_id': customer_data.get('owner_id'),  # Will be mapped to local salesperson_id

            # Status
            'status': customer_data.get('status', 'active'),
            'is_active': customer_data.get('status') == 'active',
            'customer_type': customer_data.get('customer_type'),

            # Metadata
            'created_time': customer_data.get('created_time'),
            'last_modified_time': customer_data.get('last_modified_time'),
            'zoho_synced_at': datetime.utcnow().isoformat(),
            'zoho_raw_data': customer_data
        }
