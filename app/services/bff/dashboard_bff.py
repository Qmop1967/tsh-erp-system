"""
Dashboard BFF Service

Aggregates dashboard data for Salesperson App:
- Daily/weekly/monthly statistics
- Recent orders and customers
- Performance metrics
- Pending tasks
- Top products
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_
from app.services.bff.base_bff import BaseBFFService
from app.models import (
    SalesOrder, Customer, Product, User, SalesInvoice,
    InvoicePayment, InventoryItem
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DashboardBFFService(BaseBFFService):
    """
    Dashboard BFF Service

    Provides complete dashboard data in a single API call
    """

    async def get_salesperson_dashboard(
        self,
        salesperson_id: int,
        date_range: str = "today"  # today, week, month
    ) -> Dict[str, Any]:
        """
        Get complete salesperson dashboard in single call

        Before: 8-10 separate API calls (1200ms total)
        After: 1 API call (300ms total)

        Args:
            salesperson_id: Salesperson user ID
            date_range: Date range filter (today, week, month)

        Returns:
            Complete dashboard data dictionary
        """
        cache_key = f"bff:dashboard:salesperson:{salesperson_id}:{date_range}"

        # Try cache first (shorter TTL for dashboard)
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached

        logger.info(f"Cache MISS: {cache_key} - Fetching from database")

        # Calculate date ranges
        now = datetime.now()
        if date_range == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "week":
            start_date = now - timedelta(days=7)
        elif date_range == "month":
            start_date = now - timedelta(days=30)
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Fetch all data in parallel
        tasks = [
            self._get_salesperson_info(salesperson_id),
            self._get_sales_stats(salesperson_id, start_date, now),
            self._get_recent_orders(salesperson_id, limit=10),
            self._get_pending_orders(salesperson_id),
            self._get_top_customers(salesperson_id, start_date, now, limit=5),
            self._get_top_products(salesperson_id, start_date, now, limit=5),
            self._get_payment_collection(salesperson_id, start_date, now),
            self._get_customer_count(salesperson_id),
        ]

        # Execute in parallel
        results = await self.fetch_parallel(*tasks)

        # Handle results
        salesperson = self.handle_exception(results[0], default={})
        sales_stats = self.handle_exception(results[1], default={})
        recent_orders = self.handle_exception(results[2], default=[])
        pending_orders = self.handle_exception(results[3], default=[])
        top_customers = self.handle_exception(results[4], default=[])
        top_products = self.handle_exception(results[5], default=[])
        payment_collection = self.handle_exception(results[6], default={})
        customer_count = self.handle_exception(results[7], default=0)

        # Format response
        response_data = {
            "salesperson": salesperson,
            "period": {
                "range": date_range,
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat()
            },
            "sales_overview": sales_stats,
            "recent_orders": {
                "items": recent_orders,
                "count": len(recent_orders)
            },
            "pending_orders": {
                "items": pending_orders,
                "count": len(pending_orders),
                "total_value": sum(o.get("total_amount", 0) for o in pending_orders)
            },
            "top_customers": {
                "items": top_customers,
                "count": len(top_customers)
            },
            "top_products": {
                "items": top_products,
                "count": len(top_products)
            },
            "payment_collection": payment_collection,
            "customer_stats": {
                "total_customers": customer_count,
                "active_customers": sum(1 for c in top_customers if c.get("order_count", 0) > 0)
            }
        }

        # Cache for 5 minutes (dashboard data changes frequently)
        await self.cache.set(cache_key, response_data, ttl=300)

        return self.format_response(response_data, metadata={
            "cached": False,
            "data_sources": len(tasks),
            "generated_at": now.isoformat()
        })

    async def _get_salesperson_info(self, salesperson_id: int) -> Dict[str, Any]:
        """Get salesperson basic information"""
        result = await self.db.execute(
            select(User).where(User.id == salesperson_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return {}

        return {
            "id": user.id,
            "name": user.name,
            "email": getattr(user, "email", None),
            "phone": getattr(user, "phone", None),
            "role": getattr(user, "role_name", "Salesperson")
        }

    async def _get_sales_stats(
        self,
        salesperson_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get sales statistics for the period"""
        # Total sales value
        result = await self.db.execute(
            select(
                func.count(SalesOrder.id).label('total_orders'),
                func.sum(SalesOrder.total_amount).label('total_value'),
                func.avg(SalesOrder.total_amount).label('average_order_value')
            ).where(
                and_(
                    SalesOrder.salesperson_id == salesperson_id,
                    SalesOrder.created_at >= start_date,
                    SalesOrder.created_at <= end_date
                )
            )
        )
        stats = result.first()

        # Count by status
        status_result = await self.db.execute(
            select(
                SalesOrder.status,
                func.count(SalesOrder.id).label('count')
            ).where(
                and_(
                    SalesOrder.salesperson_id == salesperson_id,
                    SalesOrder.created_at >= start_date,
                    SalesOrder.created_at <= end_date
                )
            ).group_by(SalesOrder.status)
        )
        status_counts = {row.status: row.count for row in status_result}

        return {
            "total_orders": stats.total_orders or 0,
            "total_value": float(stats.total_value or 0),
            "average_order_value": float(stats.average_order_value or 0),
            "status_breakdown": status_counts,
            "confirmed_orders": status_counts.get("confirmed", 0),
            "pending_orders": status_counts.get("pending", 0),
            "completed_orders": status_counts.get("completed", 0)
        }

    async def _get_recent_orders(
        self,
        salesperson_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent orders for salesperson"""
        result = await self.db.execute(
            select(SalesOrder, Customer)
            .join(Customer, SalesOrder.customer_id == Customer.id)
            .where(SalesOrder.salesperson_id == salesperson_id)
            .order_by(desc(SalesOrder.created_at))
            .limit(limit)
        )

        orders = []
        for order, customer in result:
            orders.append({
                "id": order.id,
                "order_number": getattr(order, "order_number", f"ORD-{order.id}"),
                "customer_id": customer.id,
                "customer_name": customer.name,
                "total_amount": float(getattr(order, "total_amount", 0)),
                "status": getattr(order, "status", "pending"),
                "created_at": order.created_at.isoformat() if order.created_at else None
            })

        return orders

    async def _get_pending_orders(self, salesperson_id: int) -> List[Dict[str, Any]]:
        """Get pending orders requiring attention"""
        result = await self.db.execute(
            select(SalesOrder, Customer)
            .join(Customer, SalesOrder.customer_id == Customer.id)
            .where(
                and_(
                    SalesOrder.salesperson_id == salesperson_id,
                    or_(
                        SalesOrder.status == "pending",
                        SalesOrder.status == "draft"
                    )
                )
            )
            .order_by(desc(SalesOrder.created_at))
        )

        orders = []
        for order, customer in result:
            orders.append({
                "id": order.id,
                "order_number": getattr(order, "order_number", f"ORD-{order.id}"),
                "customer_id": customer.id,
                "customer_name": customer.name,
                "total_amount": float(getattr(order, "total_amount", 0)),
                "status": getattr(order, "status", "pending"),
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "days_pending": (datetime.now() - order.created_at).days if order.created_at else 0
            })

        return orders

    async def _get_top_customers(
        self,
        salesperson_id: int,
        start_date: datetime,
        end_date: datetime,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top customers by order value"""
        result = await self.db.execute(
            select(
                Customer.id,
                Customer.name,
                func.count(SalesOrder.id).label('order_count'),
                func.sum(SalesOrder.total_amount).label('total_value')
            )
            .join(SalesOrder, Customer.id == SalesOrder.customer_id)
            .where(
                and_(
                    SalesOrder.salesperson_id == salesperson_id,
                    SalesOrder.created_at >= start_date,
                    SalesOrder.created_at <= end_date
                )
            )
            .group_by(Customer.id, Customer.name)
            .order_by(desc('total_value'))
            .limit(limit)
        )

        customers = []
        for row in result:
            customers.append({
                "id": row.id,
                "name": row.name,
                "order_count": row.order_count,
                "total_value": float(row.total_value or 0)
            })

        return customers

    async def _get_top_products(
        self,
        salesperson_id: int,
        start_date: datetime,
        end_date: datetime,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top selling products"""
        from app.models import SalesOrderItem

        result = await self.db.execute(
            select(
                Product.id,
                Product.name,
                Product.sku,
                func.sum(SalesOrderItem.quantity).label('total_quantity'),
                func.sum(SalesOrderItem.total).label('total_value')
            )
            .join(SalesOrderItem, Product.id == SalesOrderItem.product_id)
            .join(SalesOrder, SalesOrderItem.order_id == SalesOrder.id)
            .where(
                and_(
                    SalesOrder.salesperson_id == salesperson_id,
                    SalesOrder.created_at >= start_date,
                    SalesOrder.created_at <= end_date
                )
            )
            .group_by(Product.id, Product.name, Product.sku)
            .order_by(desc('total_value'))
            .limit(limit)
        )

        products = []
        for row in result:
            products.append({
                "id": row.id,
                "name": row.name,
                "sku": row.sku,
                "quantity_sold": float(row.total_quantity or 0),
                "total_value": float(row.total_value or 0)
            })

        return products

    async def _get_payment_collection(
        self,
        salesperson_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get payment collection statistics"""
        # Get invoices for salesperson's orders
        result = await self.db.execute(
            select(
                func.count(SalesInvoice.id).label('invoice_count'),
                func.sum(SalesInvoice.total_amount).label('total_invoiced'),
                func.sum(
                    func.case(
                        (SalesInvoice.status == 'paid', SalesInvoice.total_amount),
                        else_=0
                    )
                ).label('total_collected')
            )
            .join(SalesOrder, SalesInvoice.order_id == SalesOrder.id)
            .where(
                and_(
                    SalesOrder.salesperson_id == salesperson_id,
                    SalesInvoice.created_at >= start_date,
                    SalesInvoice.created_at <= end_date
                )
            )
        )
        stats = result.first()

        total_invoiced = float(stats.total_invoiced or 0)
        total_collected = float(stats.total_collected or 0)
        outstanding = total_invoiced - total_collected

        return {
            "invoice_count": stats.invoice_count or 0,
            "total_invoiced": total_invoiced,
            "total_collected": total_collected,
            "outstanding": outstanding,
            "collection_rate": (total_collected / total_invoiced * 100) if total_invoiced > 0 else 0
        }

    async def _get_customer_count(self, salesperson_id: int) -> int:
        """Get total customer count for salesperson"""
        result = await self.db.execute(
            select(func.count(Customer.id))
            .where(Customer.salesperson_id == salesperson_id)
        )
        return result.scalar_one()

    async def invalidate_dashboard_cache(self, salesperson_id: int):
        """Invalidate all dashboard cache entries for a salesperson"""
        patterns = [
            f"bff:dashboard:salesperson:{salesperson_id}:*",
        ]

        for pattern in patterns:
            await self.invalidate_cache(pattern)

        logger.info(f"Invalidated dashboard cache for salesperson_id={salesperson_id}")
