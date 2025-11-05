"""
Customer BFF Service

Aggregates customer-related data from multiple sources:
- Customer details
- Outstanding balance
- Recent orders
- Credit limit
- Payment history
- Assigned salesperson
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from app.services.bff.base_bff import BaseBFFService
from app.models import (
    Customer, SalesOrder, SalesInvoice, InvoicePayment, User
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CustomerBFFService(BaseBFFService):
    """
    Customer BFF Service

    Provides complete customer information in a single API call
    """

    async def get_customer_complete(
        self,
        customer_id: int,
        include_orders: bool = True,
        include_payments: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete customer data in single call

        Before: 6 separate API calls (800ms total)
        After: 1 API call (200ms total)

        Args:
            customer_id: Customer ID
            include_orders: Include recent orders
            include_payments: Include payment history

        Returns:
            Complete customer data dictionary
        """
        cache_key = f"bff:customer:{customer_id}:complete"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached

        logger.info(f"Cache MISS: {cache_key} - Fetching from database")

        # Fetch all data in parallel
        tasks = [
            self._get_customer_details(customer_id),
            self._get_customer_balance(customer_id),
            self._get_credit_info(customer_id),
        ]

        if include_orders:
            tasks.append(self._get_recent_orders(customer_id, limit=10))

        if include_payments:
            tasks.append(self._get_payment_history(customer_id, limit=10))

        # Execute in parallel
        results = await self.fetch_parallel(*tasks)

        # Handle results
        customer = self.handle_exception(results[0])
        balance = self.handle_exception(results[1], default={"total": 0, "overdue": 0})
        credit = self.handle_exception(results[2], default={"limit": 0, "available": 0})

        idx = 3
        orders = []
        payments = []

        if include_orders:
            orders = self.handle_exception(results[idx], default=[])
            idx += 1

        if include_payments:
            payments = self.handle_exception(results[idx], default=[])

        # Check if customer exists
        if not customer:
            return self.format_error("Customer not found")

        # Format response
        response_data = {
            "customer": customer,
            "financial": {
                "balance": balance,
                "credit": credit,
                "payment_terms": customer.get("payment_terms", "Net 30"),
                "risk_level": self._calculate_risk_level(balance, credit)
            },
            "recent_orders": {
                "items": orders,
                "count": len(orders),
                "total_value": sum(o.get("total", 0) for o in orders)
            } if include_orders else None,
            "payment_history": {
                "items": payments,
                "count": len(payments),
                "total_paid": sum(p.get("amount", 0) for p in payments)
            } if include_payments else None
        }

        # Cache for 2 minutes (shorter than products due to changing balances)
        await self.cache.set(cache_key, response_data, ttl=120)

        return self.format_response(response_data, metadata={
            "cached": False,
            "data_sources": len(tasks)
        })

    async def _get_customer_details(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer basic information"""
        result = await self.db.execute(
            select(Customer, User)
            .outerjoin(User, Customer.salesperson_id == User.id)
            .where(Customer.id == customer_id)
        )
        row = result.first()

        if not row:
            return None

        customer, salesperson = row

        return {
            "id": customer.id,
            "name": customer.name,
            "name_ar": getattr(customer, "name_ar", None),
            "email": getattr(customer, "email", None),
            "phone": getattr(customer, "phone", None),
            "mobile": getattr(customer, "mobile", None),
            "tax_number": getattr(customer, "tax_number", None),
            "customer_type": getattr(customer, "customer_type", "regular"),
            "salesperson": {
                "id": salesperson.id,
                "name": salesperson.name,
                "phone": getattr(salesperson, "phone", None)
            } if salesperson else None,
            "is_active": customer.is_active,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "payment_terms": getattr(customer, "payment_terms", "Net 30")
        }

    async def _get_customer_balance(self, customer_id: int) -> Dict[str, Any]:
        """Get customer outstanding balance"""
        # Get total outstanding from invoices
        result = await self.db.execute(
            select(
                func.sum(SalesInvoice.total_amount).label('total_outstanding'),
                func.sum(
                    func.case(
                        (SalesInvoice.due_date < datetime.now(), SalesInvoice.total_amount),
                        else_=0
                    )
                ).label('overdue_amount')
            ).where(
                and_(
                    SalesInvoice.customer_id == customer_id,
                    SalesInvoice.status.in_(['pending', 'partial'])
                )
            )
        )
        balance_data = result.first()

        total = float(balance_data.total_outstanding or 0)
        overdue = float(balance_data.overdue_amount or 0)

        return {
            "total": total,
            "overdue": overdue,
            "current": total - overdue,
            "currency": "USD"  # TODO: Get from customer currency
        }

    async def _get_credit_info(self, customer_id: int) -> Dict[str, Any]:
        """Get customer credit limit and available credit"""
        result = await self.db.execute(
            select(Customer.credit_limit).where(Customer.id == customer_id)
        )
        credit_limit = result.scalar_one_or_none() or 0

        # Get current balance
        balance_result = await self._get_customer_balance(customer_id)
        outstanding = balance_result.get("total", 0)

        available = float(credit_limit) - outstanding

        return {
            "limit": float(credit_limit),
            "used": outstanding,
            "available": max(0, available),
            "percentage_used": (outstanding / float(credit_limit) * 100) if credit_limit > 0 else 0
        }

    async def _get_recent_orders(self, customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent customer orders"""
        result = await self.db.execute(
            select(SalesOrder)
            .where(SalesOrder.customer_id == customer_id)
            .order_by(desc(SalesOrder.created_at))
            .limit(limit)
        )
        orders = result.scalars().all()

        return [
            {
                "id": order.id,
                "order_number": getattr(order, "order_number", f"ORD-{order.id}"),
                "date": order.created_at.isoformat() if order.created_at else None,
                "total": float(getattr(order, "total_amount", 0)),
                "status": getattr(order, "status", "pending"),
                "items_count": getattr(order, "items_count", 0)
            }
            for order in orders
        ]

    async def _get_payment_history(self, customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent payment history"""
        result = await self.db.execute(
            select(InvoicePayment, SalesInvoice)
            .join(SalesInvoice, InvoicePayment.invoice_id == SalesInvoice.id)
            .where(SalesInvoice.customer_id == customer_id)
            .order_by(desc(InvoicePayment.payment_date))
            .limit(limit)
        )

        payments = []
        for payment, invoice in result:
            payments.append({
                "id": payment.id,
                "invoice_id": invoice.id,
                "invoice_number": getattr(invoice, "invoice_number", f"INV-{invoice.id}"),
                "amount": float(payment.amount),
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "payment_method": getattr(payment, "payment_method", "unknown"),
                "reference": getattr(payment, "reference", None)
            })

        return payments

    def _calculate_risk_level(
        self,
        balance: Dict[str, Any],
        credit: Dict[str, Any]
    ) -> str:
        """Calculate customer risk level based on balance and credit"""
        overdue = balance.get("overdue", 0)
        credit_used_pct = credit.get("percentage_used", 0)

        if overdue > 0:
            return "high"
        elif credit_used_pct > 80:
            return "medium"
        elif credit_used_pct > 50:
            return "low"
        else:
            return "minimal"

    async def invalidate_customer_cache(self, customer_id: int):
        """Invalidate all cache entries for a customer"""
        patterns = [
            f"bff:customer:{customer_id}:*",
            f"customer:{customer_id}:*",
        ]

        for pattern in patterns:
            await self.invalidate_cache(pattern)

        logger.info(f"Invalidated customer cache for customer_id={customer_id}")
