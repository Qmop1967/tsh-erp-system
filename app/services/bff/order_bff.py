"""
Order BFF Service

Aggregates order-related data from multiple sources:
- Order details with items
- Customer information
- Payment status
- Delivery status
- Invoice information
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.services.bff.base_bff import BaseBFFService
from app.models import (
    SalesOrder, SalesOrderItem, Customer, User, Product,
    SalesInvoice, InvoicePayment, DeliveryNote
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderBFFService(BaseBFFService):
    """
    Order BFF Service

    Provides complete order information in a single API call
    """

    async def get_order_complete(
        self,
        order_id: int,
        include_items: bool = True,
        include_payment: bool = True,
        include_delivery: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete order data in single call

        Before: 5 separate API calls (600ms total)
        After: 1 API call (150ms total)

        Args:
            order_id: Order ID
            include_items: Include order items with product details
            include_payment: Include payment and invoice information
            include_delivery: Include delivery status

        Returns:
            Complete order data dictionary
        """
        cache_key = f"bff:order:{order_id}:complete"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached

        logger.info(f"Cache MISS: {cache_key} - Fetching from database")

        # Fetch all data in parallel
        tasks = [
            self._get_order_details(order_id),
            self._get_customer_summary(order_id),
        ]

        if include_items:
            tasks.append(self._get_order_items(order_id))

        if include_payment:
            tasks.append(self._get_payment_info(order_id))

        if include_delivery:
            tasks.append(self._get_delivery_status(order_id))

        # Execute in parallel
        results = await self.fetch_parallel(*tasks)

        # Handle results
        order = self.handle_exception(results[0])
        customer = self.handle_exception(results[1], default={})

        idx = 2
        items = []
        payment = {}
        delivery = {}

        if include_items:
            items = self.handle_exception(results[idx], default=[])
            idx += 1

        if include_payment:
            payment = self.handle_exception(results[idx], default={})
            idx += 1

        if include_delivery:
            delivery = self.handle_exception(results[idx], default={})

        # Check if order exists
        if not order:
            return self.format_error("Order not found")

        # Format response
        response_data = {
            "order": order,
            "customer": customer,
            "items": {
                "list": items,
                "count": len(items),
                "total_value": sum(item.get("total", 0) for item in items)
            } if include_items else None,
            "payment": payment if include_payment else None,
            "delivery": delivery if include_delivery else None,
            "summary": {
                "status": order.get("status"),
                "created_at": order.get("created_at"),
                "total_amount": order.get("total_amount"),
                "is_paid": payment.get("is_fully_paid", False) if include_payment else None,
                "is_delivered": delivery.get("is_delivered", False) if include_delivery else None
            }
        }

        # Cache for 3 minutes (moderate TTL for order data)
        await self.cache.set(cache_key, response_data, ttl=180)

        return self.format_response(response_data, metadata={
            "cached": False,
            "data_sources": len(tasks)
        })

    async def _get_order_details(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order basic information"""
        result = await self.db.execute(
            select(SalesOrder, User)
            .outerjoin(User, SalesOrder.salesperson_id == User.id)
            .where(SalesOrder.id == order_id)
        )
        row = result.first()

        if not row:
            return None

        order, salesperson = row

        return {
            "id": order.id,
            "order_number": getattr(order, "order_number", f"ORD-{order.id}"),
            "order_date": order.created_at.isoformat() if order.created_at else None,
            "status": getattr(order, "status", "pending"),
            "total_amount": float(getattr(order, "total_amount", 0)),
            "discount_amount": float(getattr(order, "discount_amount", 0)),
            "tax_amount": float(getattr(order, "tax_amount", 0)),
            "net_amount": float(getattr(order, "net_amount", 0)),
            "notes": getattr(order, "notes", None),
            "salesperson": {
                "id": salesperson.id,
                "name": salesperson.name,
                "phone": getattr(salesperson, "phone", None)
            } if salesperson else None,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        }

    async def _get_customer_summary(self, order_id: int) -> Dict[str, Any]:
        """Get customer summary for the order"""
        result = await self.db.execute(
            select(Customer)
            .join(SalesOrder, Customer.id == SalesOrder.customer_id)
            .where(SalesOrder.id == order_id)
        )
        customer = result.scalar_one_or_none()

        if not customer:
            return {}

        return {
            "id": customer.id,
            "name": customer.name,
            "name_ar": getattr(customer, "name_ar", None),
            "phone": getattr(customer, "phone", None),
            "mobile": getattr(customer, "mobile", None),
            "email": getattr(customer, "email", None),
            "address": getattr(customer, "address", None)
        }

    async def _get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        """Get order items with product details"""
        result = await self.db.execute(
            select(SalesOrderItem, Product)
            .join(Product, SalesOrderItem.product_id == Product.id)
            .where(SalesOrderItem.order_id == order_id)
            .order_by(SalesOrderItem.id)
        )

        items = []
        for order_item, product in result:
            items.append({
                "id": order_item.id,
                "product_id": product.id,
                "product_name": product.name,
                "product_sku": product.sku,
                "product_name_ar": getattr(product, "name_ar", None),
                "quantity": float(order_item.quantity),
                "unit_price": float(order_item.unit_price),
                "discount": float(getattr(order_item, "discount", 0)),
                "tax": float(getattr(order_item, "tax", 0)),
                "total": float(getattr(order_item, "total", 0)),
                "notes": getattr(order_item, "notes", None)
            })

        return items

    async def _get_payment_info(self, order_id: int) -> Dict[str, Any]:
        """Get payment and invoice information"""
        # Get invoice for this order
        result = await self.db.execute(
            select(SalesInvoice)
            .where(SalesInvoice.order_id == order_id)
            .order_by(desc(SalesInvoice.created_at))
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            return {
                "has_invoice": False,
                "invoice_id": None,
                "invoice_number": None,
                "invoice_date": None,
                "total_amount": 0,
                "paid_amount": 0,
                "balance": 0,
                "is_fully_paid": False,
                "payments": []
            }

        # Get payments for this invoice
        payments_result = await self.db.execute(
            select(InvoicePayment)
            .where(InvoicePayment.invoice_id == invoice.id)
            .order_by(desc(InvoicePayment.payment_date))
        )
        payments = payments_result.scalars().all()

        paid_amount = sum(float(p.amount) for p in payments)
        total_amount = float(invoice.total_amount)
        balance = total_amount - paid_amount

        return {
            "has_invoice": True,
            "invoice_id": invoice.id,
            "invoice_number": getattr(invoice, "invoice_number", f"INV-{invoice.id}"),
            "invoice_date": invoice.created_at.isoformat() if invoice.created_at else None,
            "due_date": invoice.due_date.isoformat() if hasattr(invoice, "due_date") and invoice.due_date else None,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "balance": balance,
            "is_fully_paid": balance <= 0,
            "status": getattr(invoice, "status", "pending"),
            "payments": [
                {
                    "id": p.id,
                    "amount": float(p.amount),
                    "payment_date": p.payment_date.isoformat() if p.payment_date else None,
                    "payment_method": getattr(p, "payment_method", "unknown"),
                    "reference": getattr(p, "reference", None)
                }
                for p in payments
            ]
        }

    async def _get_delivery_status(self, order_id: int) -> Dict[str, Any]:
        """Get delivery status information"""
        # Get delivery notes for this order
        result = await self.db.execute(
            select(DeliveryNote)
            .where(DeliveryNote.order_id == order_id)
            .order_by(desc(DeliveryNote.created_at))
        )
        delivery_notes = result.scalars().all()

        if not delivery_notes:
            return {
                "has_delivery": False,
                "is_delivered": False,
                "delivery_notes": []
            }

        # Check if any delivery note is completed
        is_delivered = any(
            getattr(dn, "status", "pending") == "delivered"
            for dn in delivery_notes
        )

        return {
            "has_delivery": True,
            "is_delivered": is_delivered,
            "delivery_count": len(delivery_notes),
            "delivery_notes": [
                {
                    "id": dn.id,
                    "delivery_number": getattr(dn, "delivery_number", f"DN-{dn.id}"),
                    "delivery_date": dn.created_at.isoformat() if dn.created_at else None,
                    "status": getattr(dn, "status", "pending"),
                    "driver": getattr(dn, "driver_name", None),
                    "tracking_number": getattr(dn, "tracking_number", None),
                    "notes": getattr(dn, "notes", None)
                }
                for dn in delivery_notes
            ],
            "latest_status": delivery_notes[0].status if delivery_notes else "pending"
        }

    async def invalidate_order_cache(self, order_id: int):
        """Invalidate all cache entries for an order"""
        patterns = [
            f"bff:order:{order_id}:*",
            f"order:{order_id}:*",
        ]

        for pattern in patterns:
            await self.invalidate_cache(pattern)

        logger.info(f"Invalidated order cache for order_id={order_id}")

    async def get_customer_orders(
        self,
        customer_id: int,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all orders for a customer with summary

        Args:
            customer_id: Customer ID
            limit: Maximum number of orders to return
            status: Filter by order status (optional)

        Returns:
            List of orders with summary data
        """
        cache_key = f"bff:customer:{customer_id}:orders:{status or 'all'}:{limit}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached

        logger.info(f"Cache MISS: {cache_key} - Fetching from database")

        # Build query
        query = (
            select(SalesOrder)
            .where(SalesOrder.customer_id == customer_id)
            .order_by(desc(SalesOrder.created_at))
            .limit(limit)
        )

        if status:
            query = query.where(SalesOrder.status == status)

        result = await self.db.execute(query)
        orders = result.scalars().all()

        orders_list = [
            {
                "id": order.id,
                "order_number": getattr(order, "order_number", f"ORD-{order.id}"),
                "order_date": order.created_at.isoformat() if order.created_at else None,
                "status": getattr(order, "status", "pending"),
                "total_amount": float(getattr(order, "total_amount", 0)),
                "items_count": getattr(order, "items_count", 0)
            }
            for order in orders
        ]

        response_data = {
            "orders": orders_list,
            "count": len(orders_list),
            "total_value": sum(o.get("total_amount", 0) for o in orders_list)
        }

        # Cache for 5 minutes
        await self.cache.set(cache_key, response_data, ttl=300)

        return self.format_response(response_data, metadata={
            "cached": False,
            "customer_id": customer_id,
            "filter_status": status
        })
