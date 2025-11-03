"""
Zoho Entity Handlers (Unified from TDS Core)
Handlers for syncing different entity types to local database
"""
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

logger = logging.getLogger(__name__)


# ============================================================================
# BASE HANDLER
# ============================================================================

class BaseEntityHandler(ABC):
    """Base class for entity-specific sync handlers"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync entity to local database

        Args:
            payload: Entity data from Zoho
            operation: Operation type (create, update, delete, upsert)

        Returns:
            Dictionary with sync result

        Raises:
            Exception: If sync fails
        """
        pass

    async def upsert(self, table, values: Dict, conflict_column: str):
        """
        Perform PostgreSQL upsert (INSERT ... ON CONFLICT ... DO UPDATE)

        Args:
            table: SQLAlchemy table model
            values: Dictionary of column values
            conflict_column: Column to check for conflicts

        Returns:
            Result of upsert operation
        """
        stmt = pg_insert(table).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[conflict_column],
            set_=values
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result


# ============================================================================
# PRODUCT HANDLER
# ============================================================================

class ProductHandler(BaseEntityHandler):
    """Handler for product/item synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync product to local products table

        Expected payload fields:
        - item_id (required)
        - name (required)
        - sku
        - description
        - rate (price)
        - purchase_rate
        - stock_on_hand
        - is_active
        """
        try:
            # Extract required fields
            zoho_item_id = payload.get("item_id")
            if not zoho_item_id:
                raise ValueError("Missing required field: item_id")

            # Map Zoho fields to local database fields
            product_data = {
                "zoho_item_id": zoho_item_id,
                "name": payload.get("name", ""),
                "sku": payload.get("sku", ""),
                "description": payload.get("description", ""),
                "price": float(payload.get("rate", 0)),
                "cost": float(payload.get("purchase_rate", 0)),
                "stock_quantity": int(payload.get("stock_on_hand", 0)),
                "is_active": payload.get("is_active", True),
                "zoho_data": payload  # Store full payload as JSONB
            }

            # Execute upsert (assuming products table has zoho_item_id unique constraint)
            # Note: This is a simplified example - real implementation would use actual SQLAlchemy models
            from sqlalchemy import text

            # Perform upsert using raw SQL for now
            # TODO: Replace with proper SQLAlchemy model when available
            result = await self.db.execute(
                text("""
                    INSERT INTO products (zoho_item_id, name, sku, description, price, cost, stock_quantity, is_active, zoho_data, updated_at)
                    VALUES (:zoho_item_id, :name, :sku, :description, :price, :cost, :stock_quantity, :is_active, :zoho_data::jsonb, NOW())
                    ON CONFLICT (zoho_item_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        sku = EXCLUDED.sku,
                        description = EXCLUDED.description,
                        price = EXCLUDED.price,
                        cost = EXCLUDED.cost,
                        stock_quantity = EXCLUDED.stock_quantity,
                        is_active = EXCLUDED.is_active,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_item_id": product_data["zoho_item_id"],
                    "name": product_data["name"],
                    "sku": product_data["sku"],
                    "description": product_data["description"],
                    "price": product_data["price"],
                    "cost": product_data["cost"],
                    "stock_quantity": product_data["stock_quantity"],
                    "is_active": product_data["is_active"],
                    "zoho_data": str(product_data["zoho_data"])
                }
            )

            await self.db.commit()

            # Get the product ID
            row = result.fetchone()
            product_id = row[0] if row else None

            logger.info(f"Product synced successfully: {zoho_item_id} -> local ID {product_id}")

            return {
                "success": True,
                "local_entity_id": str(product_id),
                "operation_performed": "upsert",
                "records_affected": 1
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Product sync failed: {e}", exc_info=True)
            raise


# ============================================================================
# CUSTOMER HANDLER
# ============================================================================

class CustomerHandler(BaseEntityHandler):
    """Handler for customer/contact synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync customer to local customers table

        Expected payload fields:
        - contact_id (required)
        - contact_name (required)
        - email
        - phone
        - billing_address
        - shipping_address
        """
        try:
            zoho_contact_id = payload.get("contact_id")
            if not zoho_contact_id:
                raise ValueError("Missing required field: contact_id")

            # Extract billing address
            billing_address = payload.get("billing_address", {})

            from sqlalchemy import text

            result = await self.db.execute(
                text("""
                    INSERT INTO customers (zoho_contact_id, name, email, phone, address, city, country, zoho_data, updated_at)
                    VALUES (:zoho_contact_id, :name, :email, :phone, :address, :city, :country, :zoho_data::jsonb, NOW())
                    ON CONFLICT (zoho_contact_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        address = EXCLUDED.address,
                        city = EXCLUDED.city,
                        country = EXCLUDED.country,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_contact_id": zoho_contact_id,
                    "name": payload.get("contact_name", ""),
                    "email": payload.get("email", ""),
                    "phone": payload.get("phone", ""),
                    "address": billing_address.get("street", ""),
                    "city": billing_address.get("city", ""),
                    "country": billing_address.get("country", ""),
                    "zoho_data": str(payload)
                }
            )

            await self.db.commit()

            row = result.fetchone()
            customer_id = row[0] if row else None

            logger.info(f"Customer synced successfully: {zoho_contact_id} -> local ID {customer_id}")

            return {
                "success": True,
                "local_entity_id": str(customer_id),
                "operation_performed": "upsert",
                "records_affected": 1
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Customer sync failed: {e}", exc_info=True)
            raise


# ============================================================================
# INVOICE HANDLER
# ============================================================================

class InvoiceHandler(BaseEntityHandler):
    """Handler for invoice synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync invoice to local invoices table

        Expected payload fields:
        - invoice_id (required)
        - invoice_number (required)
        - customer_id (required)
        - date
        - due_date
        - total
        - status
        - line_items[]
        """
        try:
            zoho_invoice_id = payload.get("invoice_id")
            if not zoho_invoice_id:
                raise ValueError("Missing required field: invoice_id")

            from sqlalchemy import text

            result = await self.db.execute(
                text("""
                    INSERT INTO invoices (zoho_invoice_id, invoice_number, zoho_customer_id, invoice_date, due_date, total, status, zoho_data, updated_at)
                    VALUES (:zoho_invoice_id, :invoice_number, :zoho_customer_id, :invoice_date, :due_date, :total, :status, :zoho_data::jsonb, NOW())
                    ON CONFLICT (zoho_invoice_id)
                    DO UPDATE SET
                        invoice_number = EXCLUDED.invoice_number,
                        invoice_date = EXCLUDED.invoice_date,
                        due_date = EXCLUDED.due_date,
                        total = EXCLUDED.total,
                        status = EXCLUDED.status,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_invoice_id": zoho_invoice_id,
                    "invoice_number": payload.get("invoice_number", ""),
                    "zoho_customer_id": payload.get("customer_id", ""),
                    "invoice_date": payload.get("date"),
                    "due_date": payload.get("due_date"),
                    "total": float(payload.get("total", 0)),
                    "status": payload.get("status", "draft"),
                    "zoho_data": str(payload)
                }
            )

            await self.db.commit()

            row = result.fetchone()
            invoice_id = row[0] if row else None

            logger.info(f"Invoice synced successfully: {zoho_invoice_id} -> local ID {invoice_id}")

            return {
                "success": True,
                "local_entity_id": str(invoice_id),
                "operation_performed": "upsert",
                "records_affected": 1
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Invoice sync failed: {e}", exc_info=True)
            raise


# ============================================================================
# STUB HANDLERS (For other entity types)
# ============================================================================

class BillHandler(BaseEntityHandler):
    """Handler for bill synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync bill to local bills table

        Expected payload fields:
        - bill_id (required)
        - bill_number (required)
        - vendor_id (required)
        - date
        - due_date
        - total
        - status
        """
        try:
            zoho_bill_id = payload.get("bill_id")
            if not zoho_bill_id:
                raise ValueError("Missing required field: bill_id")

            from sqlalchemy import text

            result = await self.db.execute(
                text("""
                    INSERT INTO bills (zoho_bill_id, bill_number, zoho_vendor_id, bill_date, due_date, total, status, zoho_data, updated_at)
                    VALUES (:zoho_bill_id, :bill_number, :zoho_vendor_id, :bill_date, :due_date, :total, :status, :zoho_data::jsonb, NOW())
                    ON CONFLICT (zoho_bill_id)
                    DO UPDATE SET
                        bill_number = EXCLUDED.bill_number,
                        bill_date = EXCLUDED.bill_date,
                        due_date = EXCLUDED.due_date,
                        total = EXCLUDED.total,
                        status = EXCLUDED.status,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_bill_id": zoho_bill_id,
                    "bill_number": payload.get("bill_number", ""),
                    "zoho_vendor_id": payload.get("vendor_id", ""),
                    "bill_date": payload.get("date"),
                    "due_date": payload.get("due_date"),
                    "total": float(payload.get("total", 0)),
                    "status": payload.get("status", "draft"),
                    "zoho_data": str(payload)
                }
            )

            await self.db.commit()

            row = result.fetchone()
            bill_id = row[0] if row else None

            logger.info(f"Bill synced successfully: {zoho_bill_id} -> local ID {bill_id}")

            return {
                "success": True,
                "local_entity_id": str(bill_id),
                "operation_performed": "upsert",
                "records_affected": 1
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Bill sync failed: {e}", exc_info=True)
            raise


class CreditNoteHandler(BaseEntityHandler):
    """Handler for credit note synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync credit note to local credit_notes table

        Expected payload fields:
        - creditnote_id (required)
        - creditnote_number (required)
        - customer_id
        - date
        - total
        - status
        """
        try:
            zoho_creditnote_id = payload.get("creditnote_id")
            if not zoho_creditnote_id:
                raise ValueError("Missing required field: creditnote_id")

            from sqlalchemy import text

            result = await self.db.execute(
                text("""
                    INSERT INTO credit_notes (zoho_creditnote_id, creditnote_number, zoho_customer_id, creditnote_date, total, status, zoho_data, updated_at)
                    VALUES (:zoho_creditnote_id, :creditnote_number, :zoho_customer_id, :creditnote_date, :total, :status, :zoho_data::jsonb, NOW())
                    ON CONFLICT (zoho_creditnote_id)
                    DO UPDATE SET
                        creditnote_number = EXCLUDED.creditnote_number,
                        creditnote_date = EXCLUDED.creditnote_date,
                        total = EXCLUDED.total,
                        status = EXCLUDED.status,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_creditnote_id": zoho_creditnote_id,
                    "creditnote_number": payload.get("creditnote_number", ""),
                    "zoho_customer_id": payload.get("customer_id", ""),
                    "creditnote_date": payload.get("date"),
                    "total": float(payload.get("total", 0)),
                    "status": payload.get("status", "draft"),
                    "zoho_data": str(payload)
                }
            )

            await self.db.commit()

            row = result.fetchone()
            creditnote_id = row[0] if row else None

            logger.info(f"Credit note synced successfully: {zoho_creditnote_id} -> local ID {creditnote_id}")

            return {
                "success": True,
                "local_entity_id": str(creditnote_id),
                "operation_performed": "upsert",
                "records_affected": 1
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Credit note sync failed: {e}", exc_info=True)
            raise


class StockAdjustmentHandler(BaseEntityHandler):
    """Handler for stock adjustment synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync stock adjustment to local stock_adjustments table
        Also updates product stock quantity

        Expected payload fields:
        - adjustment_id (required)
        - item_id (required)
        - quantity_adjusted (required)
        - adjustment_type
        - reason
        - date
        """
        try:
            zoho_adjustment_id = payload.get("adjustment_id")
            zoho_item_id = payload.get("item_id")

            if not zoho_adjustment_id:
                raise ValueError("Missing required field: adjustment_id")
            if not zoho_item_id:
                raise ValueError("Missing required field: item_id")

            from sqlalchemy import text

            # Store stock adjustment record
            result = await self.db.execute(
                text("""
                    INSERT INTO stock_adjustments (zoho_adjustment_id, zoho_item_id, quantity_adjusted, adjustment_type, reason, adjustment_date, zoho_data, updated_at)
                    VALUES (:zoho_adjustment_id, :zoho_item_id, :quantity_adjusted, :adjustment_type, :reason, :adjustment_date, :zoho_data::jsonb, NOW())
                    ON CONFLICT (zoho_adjustment_id)
                    DO UPDATE SET
                        quantity_adjusted = EXCLUDED.quantity_adjusted,
                        adjustment_type = EXCLUDED.adjustment_type,
                        reason = EXCLUDED.reason,
                        adjustment_date = EXCLUDED.adjustment_date,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_adjustment_id": zoho_adjustment_id,
                    "zoho_item_id": zoho_item_id,
                    "quantity_adjusted": int(payload.get("quantity_adjusted", 0)),
                    "adjustment_type": payload.get("adjustment_type", "quantity"),
                    "reason": payload.get("reason", ""),
                    "adjustment_date": payload.get("date"),
                    "zoho_data": str(payload)
                }
            )

            row = result.fetchone()
            adjustment_id = row[0] if row else None

            # Update product stock quantity
            # Find product by zoho_item_id and update stock
            await self.db.execute(
                text("""
                    UPDATE products
                    SET stock_quantity = stock_quantity + :quantity_adjusted,
                        updated_at = NOW()
                    WHERE zoho_item_id = :zoho_item_id
                """),
                {
                    "zoho_item_id": zoho_item_id,
                    "quantity_adjusted": int(payload.get("quantity_adjusted", 0))
                }
            )

            await self.db.commit()

            logger.info(f"Stock adjustment synced successfully: {zoho_adjustment_id} -> local ID {adjustment_id}")

            return {
                "success": True,
                "local_entity_id": str(adjustment_id),
                "operation_performed": "upsert+update_stock",
                "records_affected": 2  # adjustment + product
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Stock adjustment sync failed: {e}", exc_info=True)
            raise


class PriceListHandler(BaseEntityHandler):
    """Handler for price list synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync price list to local pricelists and product_prices tables

        Expected payload fields:
        - pricelist_id (required)
        - name (required)
        - currency_code
        - is_active
        - items[] (optional - array of item prices)
          - item_id
          - rate
          - discount_percentage
        """
        try:
            zoho_pricelist_id = payload.get("pricelist_id")
            if not zoho_pricelist_id:
                raise ValueError("Missing required field: pricelist_id")

            from sqlalchemy import text

            # Step 1: Sync pricelist header
            result = await self.db.execute(
                text("""
                    INSERT INTO pricelists (zoho_pricelist_id, name, currency, is_active, zoho_data, updated_at)
                    VALUES (:zoho_pricelist_id, :name, :currency, :is_active, :zoho_data::jsonb, NOW())
                    ON CONFLICT (zoho_pricelist_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        currency = EXCLUDED.currency,
                        is_active = EXCLUDED.is_active,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_pricelist_id": zoho_pricelist_id,
                    "name": payload.get("name", ""),
                    "currency": payload.get("currency_code", "USD"),
                    "is_active": payload.get("is_active", True),
                    "zoho_data": str(payload)
                }
            )

            row = result.fetchone()
            pricelist_id = row[0] if row else None

            records_affected = 1  # Pricelist itself

            # Step 2: Sync price list items (if provided)
            items = payload.get("items", [])
            if items and pricelist_id:
                for item in items:
                    zoho_item_id = item.get("item_id")
                    if not zoho_item_id:
                        continue

                    # Get local product ID from zoho_item_id
                    product_result = await self.db.execute(
                        text("SELECT id FROM products WHERE zoho_item_id = :zoho_item_id"),
                        {"zoho_item_id": zoho_item_id}
                    )
                    product_row = product_result.fetchone()

                    if not product_row:
                        logger.warning(f"Product not found for item_id: {zoho_item_id}, skipping price")
                        continue

                    product_id = product_row[0]

                    # Upsert product price
                    await self.db.execute(
                        text("""
                            INSERT INTO product_prices (product_id, pricelist_id, price, discount_percentage, currency, updated_at)
                            VALUES (:product_id, :pricelist_id, :price, :discount_percentage, :currency, NOW())
                            ON CONFLICT (product_id, pricelist_id)
                            DO UPDATE SET
                                price = EXCLUDED.price,
                                discount_percentage = EXCLUDED.discount_percentage,
                                updated_at = NOW()
                        """),
                        {
                            "product_id": product_id,
                            "pricelist_id": pricelist_id,
                            "price": float(item.get("rate", 0)),
                            "discount_percentage": float(item.get("discount_percentage", 0)),
                            "currency": payload.get("currency_code", "USD")
                        }
                    )

                    records_affected += 1

            await self.db.commit()

            logger.info(
                f"Price list synced successfully: {zoho_pricelist_id} -> local ID {pricelist_id} "
                f"({len(items)} items)"
            )

            return {
                "success": True,
                "local_entity_id": str(pricelist_id),
                "operation_performed": "upsert_pricelist_and_items",
                "records_affected": records_affected
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Price list sync failed: {e}", exc_info=True)
            raise


# ============================================================================
# ENTITY HANDLER FACTORY
# ============================================================================

class EntityHandlerFactory:
    """Factory for creating entity-specific handlers"""

    _handlers = {
        "product": ProductHandler,
        "customer": CustomerHandler,
        "invoice": InvoiceHandler,
        "bill": BillHandler,
        "credit_note": CreditNoteHandler,
        "stock_adjustment": StockAdjustmentHandler,
        "price_list": PriceListHandler,
    }

    @classmethod
    def get_handler(cls, entity_type: str, db: AsyncSession) -> BaseEntityHandler:
        """
        Get handler for entity type

        Args:
            entity_type: Entity type (product, customer, etc.)
            db: Database session

        Returns:
            Entity handler instance

        Raises:
            ValueError: If entity type not supported
        """
        handler_class = cls._handlers.get(entity_type.lower())
        if not handler_class:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        return handler_class(db)

    @classmethod
    def is_supported(cls, entity_type: str) -> bool:
        """Check if entity type is supported"""
        return entity_type.lower() in cls._handlers
