"""
Order Processor
================

Processes Zoho sales order data for creation and synchronization.

معالج الطلبات - معالجة بيانات طلبات المبيعات من Zoho

Author: TSH ERP Team
Date: January 2025
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


def safe_decimal(value, default=0):
    """Safely convert value to Decimal"""
    try:
        if value is None or value == '' or value == 'None':
            return Decimal(str(default))
        str_value = str(value).strip().replace(',', '')
        if not str_value:
            return Decimal(str(default))
        return Decimal(str_value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid decimal value: {value}, using {default}. Error: {e}")
        return Decimal(str(default))


class OrderProcessor:
    """
    Order data processor
    معالج بيانات الطلبات

    Validates, transforms, and prepares Zoho sales order data.
    """

    @staticmethod
    def validate(order_data: Dict[str, Any]) -> bool:
        """
        Validate order data before sending to Zoho

        Args:
            order_data: Order data dictionary

        Returns:
            bool: True if valid
        """
        # Required fields for creating an order
        required_fields = ['customer_name', 'line_items']
        
        for field in required_fields:
            if field not in order_data:
                logger.warning(f"Order missing required field: {field}")
                return False

        # Validate line items
        line_items = order_data.get('line_items', [])
        if not line_items or len(line_items) == 0:
            logger.warning("Order must have at least one line item")
            return False

        # Validate each line item
        for idx, item in enumerate(line_items):
            if 'item_id' not in item:
                logger.warning(f"Line item {idx} missing item_id")
                return False
            if 'quantity' not in item or item['quantity'] <= 0:
                logger.warning(f"Line item {idx} has invalid quantity")
                return False

        return True

    @staticmethod
    def prepare_for_zoho(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare order data for Zoho Books API

        Args:
            order_data: Order data from consumer API

        Returns:
            dict: Formatted order data for Zoho API
        """
        # Format date
        order_date = order_data.get('date')
        if not order_date:
            order_date = datetime.now().strftime("%Y-%m-%d")
        elif isinstance(order_date, datetime):
            order_date = order_date.strftime("%Y-%m-%d")

        # Prepare line items
        line_items = []
        for item in order_data.get('line_items', []):
            line_item = {
                "item_id": item.get('item_id'),
                "name": item.get('product_name') or item.get('name'),
                "quantity": item.get('quantity'),
                "rate": float(safe_decimal(item.get('rate', 0))),
                "amount": float(safe_decimal(item.get('amount', 0)))
            }
            line_items.append(line_item)

        # Build Zoho order payload
        zoho_order = {
            "customer_name": order_data.get('customer_name'),
            "date": order_date,
            "line_items": line_items,
            "notes": order_data.get('notes', ''),
        }

        # Add custom fields if provided
        if 'custom_fields' in order_data:
            zoho_order['custom_fields'] = order_data['custom_fields']

        # Add customer email and phone as custom fields if not already present
        if 'customer_email' in order_data:
            if 'custom_fields' not in zoho_order:
                zoho_order['custom_fields'] = []
            zoho_order['custom_fields'].append({
                "label": "Customer Email",
                "value": order_data['customer_email']
            })

        if 'customer_phone' in order_data:
            if 'custom_fields' not in zoho_order:
                zoho_order['custom_fields'] = []
            zoho_order['custom_fields'].append({
                "label": "Customer Phone",
                "value": order_data['customer_phone']
            })

        return zoho_order

    @staticmethod
    def transform_zoho_response(zoho_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Zoho order response to local format

        Args:
            zoho_response: Response from Zoho API

        Returns:
            dict: Transformed order data
        """
        if 'salesorder' not in zoho_response:
            return {}

        salesorder = zoho_response['salesorder']

        return {
            'order_id': salesorder.get('salesorder_id'),
            'order_number': salesorder.get('salesorder_number'),
            'customer_id': salesorder.get('customer_id'),
            'customer_name': salesorder.get('customer_name'),
            'date': salesorder.get('date'),
            'status': salesorder.get('status'),
            'total': float(safe_decimal(salesorder.get('total', 0))),
            'sub_total': float(safe_decimal(salesorder.get('sub_total', 0))),
            'tax_total': float(safe_decimal(salesorder.get('tax_total', 0))),
            'line_items': salesorder.get('line_items', []),
            'created_time': salesorder.get('created_time'),
            'last_modified_time': salesorder.get('last_modified_time'),
            'zoho_raw_data': salesorder
        }

