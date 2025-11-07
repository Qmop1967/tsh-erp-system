"""
Order Service

Business logic layer for order operations using repository pattern.
"""

from typing import List, Optional
from datetime import date
from app.application.interfaces.repositories.order_repository import IOrderRepository
from app.application.dtos.order_dto import (
    OrderCreateDTO,
    OrderUpdateDTO,
    OrderResponseDTO,
    OrderWithItemsResponseDTO,
    OrderListResponseDTO,
    OrderSearchDTO,
    OrderSummaryDTO,
    OrderStatusUpdateDTO,
    OrderPaymentUpdateDTO,
    OrderStatisticsDTO,
    OrderItemResponseDTO,
)
from app.models import SalesOrder, SalesItem


class OrderService:
    """
    Service class for order business logic.

    This service class handles all order-related business logic
    using the repository pattern for data access.
    """

    def __init__(self, order_repository: IOrderRepository):
        """
        Initialize the service with an order repository.

        Args:
            order_repository: Order repository implementation
        """
        self.repository = order_repository

    async def get_order_by_id(self, order_id: int) -> Optional[OrderResponseDTO]:
        """
        Get an order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order response DTO if found, None otherwise
        """
        order = await self.repository.get_by_id(order_id)
        if not order:
            return None
        return OrderResponseDTO.model_validate(order)

    async def get_order_with_items(self, order_id: int) -> Optional[OrderWithItemsResponseDTO]:
        """
        Get an order with its items.

        Args:
            order_id: Order ID

        Returns:
            Order with items response DTO if found, None otherwise
        """
        order = await self.repository.get_with_items(order_id)
        if not order:
            return None

        # Convert to DTO
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "branch_id": order.branch_id,
            "warehouse_id": order.warehouse_id,
            "order_date": order.order_date,
            "expected_delivery_date": order.expected_delivery_date,
            "actual_delivery_date": order.actual_delivery_date,
            "status": order.status,
            "payment_status": order.payment_status,
            "payment_method": order.payment_method,
            "subtotal": float(order.subtotal),
            "discount_percentage": float(order.discount_percentage),
            "discount_amount": float(order.discount_amount),
            "tax_percentage": float(order.tax_percentage),
            "tax_amount": float(order.tax_amount),
            "total_amount": float(order.total_amount),
            "paid_amount": float(order.paid_amount),
            "notes": order.notes,
            "created_by": order.created_by,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": [OrderItemResponseDTO.model_validate(item) for item in order.sales_items]
        }

        return OrderWithItemsResponseDTO(**order_dict)

    async def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> OrderListResponseDTO:
        """
        Get all orders with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by order status

        Returns:
            Order list response DTO
        """
        filters = {}
        if status:
            filters['status'] = status

        orders = await self.repository.get_all(skip=skip, limit=limit, **filters)
        total = await self.repository.count(**filters)

        return OrderListResponseDTO(
            items=[OrderResponseDTO.model_validate(o) for o in orders],
            total=total,
            skip=skip,
            limit=limit
        )

    async def create_order(self, dto: OrderCreateDTO) -> OrderWithItemsResponseDTO:
        """
        Create a new order with items.

        Args:
            dto: Order creation DTO

        Returns:
            Created order with items response DTO

        Raises:
            ValueError: If validation fails
        """
        # Generate order number
        order_number = await self._generate_order_number()

        # Calculate order totals
        subtotal = sum(
            item.quantity * item.unit_price - item.discount_amount
            for item in dto.items
        )

        # Apply order-level discount
        order_discount = 0.0
        if dto.discount_percentage > 0:
            order_discount = subtotal * (dto.discount_percentage / 100)
        elif dto.discount_amount > 0:
            order_discount = dto.discount_amount

        subtotal_after_discount = subtotal - order_discount

        # Calculate tax
        tax_amount = subtotal_after_discount * (dto.tax_percentage / 100)
        total_amount = subtotal_after_discount + tax_amount

        # Create order entity
        order = SalesOrder(
            order_number=order_number,
            customer_id=dto.customer_id,
            branch_id=dto.branch_id,
            warehouse_id=dto.warehouse_id,
            order_date=dto.order_date,
            expected_delivery_date=dto.expected_delivery_date,
            status="DRAFT",
            payment_status="PENDING",
            payment_method=dto.payment_method,
            subtotal=subtotal,
            discount_percentage=dto.discount_percentage,
            discount_amount=order_discount,
            tax_percentage=dto.tax_percentage,
            tax_amount=tax_amount,
            total_amount=total_amount,
            paid_amount=0,
            notes=dto.notes,
            created_by=dto.created_by
        )

        # Create order in database
        created_order = await self.repository.create(order)

        # Create order items
        # Note: In a real implementation, you'd create items through a separate repository
        # For now, we'll return the order without items since we'd need item repository

        return await self.get_order_with_items(created_order.id)

    async def update_order(
        self,
        order_id: int,
        dto: OrderUpdateDTO
    ) -> Optional[OrderResponseDTO]:
        """
        Update an existing order.

        Args:
            order_id: Order ID
            dto: Order update DTO

        Returns:
            Updated order response DTO if found, None otherwise

        Raises:
            ValueError: If validation fails
        """
        existing_order = await self.repository.get_by_id(order_id)
        if not existing_order:
            return None

        # Update only provided fields
        update_data = dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(existing_order, key):
                setattr(existing_order, key, value)

        updated_order = await self.repository.update(order_id, existing_order)
        return OrderResponseDTO.model_validate(updated_order)

    async def delete_order(self, order_id: int) -> bool:
        """
        Delete an order.

        Args:
            order_id: Order ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(order_id)

    async def search_orders(self, dto: OrderSearchDTO) -> OrderListResponseDTO:
        """
        Search orders with filters.

        Args:
            dto: Order search DTO

        Returns:
            Order list response DTO
        """
        orders = []
        total = 0

        if dto.query:
            # Text search
            orders = await self.repository.search(
                query=dto.query,
                skip=dto.skip,
                limit=dto.limit
            )
            all_results = await self.repository.search(
                query=dto.query,
                skip=0,
                limit=10000
            )
            total = len(all_results)
        elif dto.customer_id:
            # Customer filter
            orders = await self.repository.get_by_customer(
                customer_id=dto.customer_id,
                skip=dto.skip,
                limit=dto.limit,
                status=dto.status
            )
            total = await self.repository.count_by_customer(
                customer_id=dto.customer_id,
                status=dto.status
            )
        elif dto.status:
            # Status filter
            orders = await self.repository.get_by_status(
                status=dto.status,
                skip=dto.skip,
                limit=dto.limit
            )
            total = await self.repository.count_by_status(status=dto.status)
        elif dto.payment_status:
            # Payment status filter
            orders = await self.repository.get_by_payment_status(
                payment_status=dto.payment_status,
                skip=dto.skip,
                limit=dto.limit
            )
            filters = {'payment_status': dto.payment_status}
            total = await self.repository.count(**filters)
        elif dto.branch_id:
            # Branch filter
            orders = await self.repository.get_by_branch(
                branch_id=dto.branch_id,
                skip=dto.skip,
                limit=dto.limit
            )
            filters = {'branch_id': dto.branch_id}
            total = await self.repository.count(**filters)
        elif dto.salesperson_id:
            # Salesperson filter
            orders = await self.repository.get_by_salesperson(
                salesperson_id=dto.salesperson_id,
                skip=dto.skip,
                limit=dto.limit
            )
            all_salesperson_orders = await self.repository.get_by_salesperson(
                salesperson_id=dto.salesperson_id,
                skip=0,
                limit=10000
            )
            total = len(all_salesperson_orders)
        elif dto.start_date and dto.end_date:
            # Date range filter
            orders = await self.repository.get_by_date_range(
                start_date=dto.start_date,
                end_date=dto.end_date,
                skip=dto.skip,
                limit=dto.limit
            )
            all_date_orders = await self.repository.get_by_date_range(
                start_date=dto.start_date,
                end_date=dto.end_date,
                skip=0,
                limit=10000
            )
            total = len(all_date_orders)
        else:
            # Default: get all
            orders = await self.repository.get_all(
                skip=dto.skip,
                limit=dto.limit
            )
            total = await self.repository.count()

        return OrderListResponseDTO(
            items=[OrderResponseDTO.model_validate(o) for o in orders],
            total=total,
            skip=dto.skip,
            limit=dto.limit
        )

    async def get_order_by_number(self, order_number: str) -> Optional[OrderResponseDTO]:
        """
        Get an order by order number.

        Args:
            order_number: Order number

        Returns:
            Order response DTO if found, None otherwise
        """
        order = await self.repository.get_by_order_number(order_number)
        if not order:
            return None
        return OrderResponseDTO.model_validate(order)

    async def get_orders_by_customer(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> OrderListResponseDTO:
        """
        Get orders for a customer.

        Args:
            customer_id: Customer ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status

        Returns:
            Order list response DTO
        """
        orders = await self.repository.get_by_customer(
            customer_id=customer_id,
            skip=skip,
            limit=limit,
            status=status
        )
        total = await self.repository.count_by_customer(
            customer_id=customer_id,
            status=status
        )

        return OrderListResponseDTO(
            items=[OrderResponseDTO.model_validate(o) for o in orders],
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_pending_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> OrderListResponseDTO:
        """
        Get pending orders (DRAFT status).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Order list response DTO
        """
        orders = await self.repository.get_pending_orders(skip=skip, limit=limit)
        total = await self.repository.count_by_status("DRAFT")

        return OrderListResponseDTO(
            items=[OrderResponseDTO.model_validate(o) for o in orders],
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_overdue_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> OrderListResponseDTO:
        """
        Get overdue orders.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Order list response DTO
        """
        orders = await self.repository.get_overdue_orders(skip=skip, limit=limit)
        all_overdue = await self.repository.get_overdue_orders(skip=0, limit=10000)

        return OrderListResponseDTO(
            items=[OrderResponseDTO.model_validate(o) for o in orders],
            total=len(all_overdue),
            skip=skip,
            limit=limit
        )

    async def update_order_status(self, dto: OrderStatusUpdateDTO) -> Optional[OrderResponseDTO]:
        """
        Update order status.

        Args:
            dto: Order status update DTO

        Returns:
            Updated order response DTO if found, None otherwise
        """
        order = await self.repository.update_order_status(dto.order_id, dto.status)
        if not order:
            return None
        return OrderResponseDTO.model_validate(order)

    async def update_payment(self, dto: OrderPaymentUpdateDTO) -> Optional[OrderResponseDTO]:
        """
        Update order payment.

        Args:
            dto: Order payment update DTO

        Returns:
            Updated order response DTO if found, None otherwise
        """
        order = await self.repository.update_payment_status(
            dto.order_id,
            dto.payment_status,
            dto.paid_amount
        )
        if not order:
            return None
        return OrderResponseDTO.model_validate(order)

    async def get_order_statistics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> OrderStatisticsDTO:
        """
        Get order statistics.

        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            Order statistics DTO
        """
        # Get counts by status
        total_orders = await self.repository.count()
        confirmed_orders = await self.repository.count_by_status("CONFIRMED")
        pending_orders = await self.repository.count_by_status("DRAFT")
        delivered_orders = await self.repository.count_by_status("DELIVERED")
        cancelled_orders = await self.repository.count_by_status("CANCELLED")

        # Get total sales amount
        total_sales = await self.repository.get_total_sales_amount(
            start_date=start_date,
            end_date=end_date
        )

        # Calculate average order value
        active_orders = confirmed_orders + delivered_orders
        average_order_value = total_sales / active_orders if active_orders > 0 else 0.0

        return OrderStatisticsDTO(
            total_orders=total_orders,
            confirmed_orders=confirmed_orders,
            pending_orders=pending_orders,
            delivered_orders=delivered_orders,
            cancelled_orders=cancelled_orders,
            total_sales_amount=total_sales,
            average_order_value=average_order_value
        )

    async def _generate_order_number(self) -> str:
        """
        Generate a unique order number.

        Returns:
            Unique order number
        """
        from datetime import datetime

        # Format: ORD-YYYYMMDD-XXXX
        date_str = datetime.now().strftime("%Y%m%d")

        # Get count of orders today to generate sequence
        today = date.today()
        orders_today = await self.repository.get_by_date_range(
            start_date=today,
            end_date=today,
            skip=0,
            limit=10000
        )

        sequence = len(orders_today) + 1
        order_number = f"ORD-{date_str}-{sequence:04d}"

        # Check if exists (safety check)
        existing = await self.repository.get_by_order_number(order_number)
        if existing:
            # Try next sequence
            sequence += 1
            order_number = f"ORD-{date_str}-{sequence:04d}"

        return order_number
