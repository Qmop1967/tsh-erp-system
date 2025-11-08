"""
TDS Order Synchronization Handler
==================================

Handles creating and syncing sales orders to/from Zoho through TDS.
معالج مزامنة الطلبات - إنشاء ومزامنة طلبات المبيعات من/إلى Zoho

This integrates order creation functionality into TDS for centralized
monitoring, event tracking, and unified architecture.

Author: TSH ERP Team
Date: January 2025
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .client import UnifiedZohoClient, ZohoAPI, ZohoAPIError
from .processors.orders import OrderProcessor
from ...core.events.event_bus import EventBus

logger = logging.getLogger(__name__)


class OrderSyncHandler:
    """
    TDS Handler for Zoho Sales Order Synchronization
    معالج TDS لمزامنة طلبات المبيعات من Zoho

    Features:
    - Create sales orders in Zoho Books
    - Validate order data
    - Transform order data for Zoho API
    - Event publishing for monitoring
    - Comprehensive error handling
    - Integration with TDS event system
    """

    def __init__(
        self,
        zoho_client: UnifiedZohoClient,
        event_bus: Optional[EventBus] = None
    ):
        """
        Initialize order sync handler

        Args:
            zoho_client: Unified Zoho API client
            event_bus: Event bus for publishing events
        """
        self.zoho_client = zoho_client
        self.event_bus = event_bus
        self.processor = OrderProcessor()

    async def create_order(
        self,
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a sales order in Zoho Books

        Args:
            order_data: Order data dictionary containing:
                - customer_name: Customer name
                - customer_email: Customer email (optional)
                - customer_phone: Customer phone (optional)
                - line_items: List of order line items
                - date: Order date (optional, defaults to today)
                - notes: Order notes (optional)

        Returns:
            dict: Order creation result containing:
                - success: bool
                - order_id: Zoho order ID
                - order_number: Order number
                - message: Status message
                - zoho_response: Full Zoho API response

        Raises:
            ZohoAPIError: If Zoho API call fails
            ValueError: If order data is invalid
        """
        try:
            # Validate order data
            if not self.processor.validate(order_data):
                raise ValueError("Invalid order data: validation failed")

            # Prepare order data for Zoho API
            zoho_order_data = self.processor.prepare_for_zoho(order_data)

            # Publish event: Order creation started
            if self.event_bus:
                await self.event_bus.publish('tds.order.create.started', {
                    'customer_name': order_data.get('customer_name'),
                    'line_items_count': len(order_data.get('line_items', [])),
                    'timestamp': datetime.utcnow().isoformat()
                })

            logger.info(
                f"Creating order in Zoho for customer: {order_data.get('customer_name')} "
                f"({len(order_data.get('line_items', []))} items)"
            )

            # Create order in Zoho Books via TDS client
            zoho_response = await self.zoho_client.post(
                endpoint="/salesorders",
                data=zoho_order_data,
                api_type=ZohoAPI.BOOKS
            )

            # Validate response
            if not zoho_response or 'salesorder' not in zoho_response:
                error_msg = "Failed to create order in Zoho: invalid response"
                logger.error(error_msg)
                
                # Publish failure event
                if self.event_bus:
                    await self.event_bus.publish('tds.order.create.failed', {
                        'customer_name': order_data.get('customer_name'),
                        'error': error_msg,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                raise ZohoAPIError(error_msg)

            # Transform response
            salesorder = zoho_response['salesorder']
            order_id = salesorder.get('salesorder_id')
            order_number = salesorder.get('salesorder_number')

            logger.info(
                f"✅ Order created successfully in Zoho: {order_number} (ID: {order_id})"
            )

            # Transform response to local format
            transformed_order = self.processor.transform_zoho_response(zoho_response)

            # Publish success event
            if self.event_bus:
                await self.event_bus.publish('tds.order.create.completed', {
                    'order_id': order_id,
                    'order_number': order_number,
                    'customer_name': order_data.get('customer_name'),
                    'total': transformed_order.get('total', 0),
                    'timestamp': datetime.utcnow().isoformat()
                })

            # Return result
            return {
                'success': True,
                'order_id': order_id,
                'order_number': order_number,
                'message': 'Order created successfully in Zoho',
                'zoho_response': zoho_response,
                'transformed_order': transformed_order
            }

        except ValueError as e:
            logger.error(f"Order validation error: {e}")
            raise
        except ZohoAPIError as e:
            logger.error(f"Zoho API error creating order: {e.message}")
            
            # Publish failure event
            if self.event_bus:
                await self.event_bus.publish('tds.order.create.failed', {
                    'customer_name': order_data.get('customer_name'),
                    'error': e.message,
                    'error_code': getattr(e, 'code', None),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating order: {e}", exc_info=True)
            
            # Publish failure event
            if self.event_bus:
                await self.event_bus.publish('tds.order.create.failed', {
                    'customer_name': order_data.get('customer_name'),
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            raise

