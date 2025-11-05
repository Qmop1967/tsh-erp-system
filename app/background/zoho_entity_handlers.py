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

            # Map Zoho fields to local database fields (only fields that exist in the schema)
            product_data = {
                "zoho_item_id": zoho_item_id,
                "name": payload.get("name", ""),
                "sku": payload.get("sku", ""),
                "description": payload.get("description", ""),
                "price": float(payload.get("rate", 0)),
                "stock_quantity": int(payload.get("stock_on_hand", 0)),
                "is_active": payload.get("is_active", True),
            }

            # Execute upsert (assuming products table has zoho_item_id unique constraint)
            # Note: This is a simplified example - real implementation would use actual SQLAlchemy models
            from sqlalchemy import text

            # Perform upsert using raw SQL for now
            # TODO: Replace with proper SQLAlchemy model when available
            result = await self.db.execute(
                text("""
                    INSERT INTO products (zoho_item_id, name, sku, description, price, stock_quantity, is_active, updated_at)
                    VALUES (:zoho_item_id, :name, :sku, :description, :price, :stock_quantity, :is_active, NOW())
                    ON CONFLICT (zoho_item_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        sku = EXCLUDED.sku,
                        description = EXCLUDED.description,
                        price = EXCLUDED.price,
                        stock_quantity = EXCLUDED.stock_quantity,
                        is_active = EXCLUDED.is_active,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_item_id": product_data["zoho_item_id"],
                    "name": product_data["name"],
                    "sku": product_data["sku"],
                    "description": product_data["description"],
                    "price": product_data["price"],
                    "stock_quantity": product_data["stock_quantity"],
                    "is_active": product_data["is_active"],
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

            # Extract billing and shipping addresses
            billing_address = payload.get("billing_address", {})
            shipping_address = payload.get("shipping_address", {})

            from sqlalchemy import text
            import json

            result = await self.db.execute(
                text("""
                    INSERT INTO customers (zoho_contact_id, contact_name, company_name, email, phone, billing_address, shipping_address, updated_at)
                    VALUES (:zoho_contact_id, :contact_name, :company_name, :email, :phone, :billing_address, :shipping_address, NOW())
                    ON CONFLICT (zoho_contact_id)
                    DO UPDATE SET
                        contact_name = EXCLUDED.contact_name,
                        company_name = EXCLUDED.company_name,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        billing_address = EXCLUDED.billing_address,
                        shipping_address = EXCLUDED.shipping_address,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_contact_id": zoho_contact_id,
                    "contact_name": payload.get("contact_name", ""),
                    "company_name": payload.get("company_name", ""),
                    "email": payload.get("email", ""),
                    "phone": payload.get("phone", ""),
                    "billing_address": json.dumps(billing_address) if billing_address else None,
                    "shipping_address": json.dumps(shipping_address) if shipping_address else None,
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
            from datetime import datetime
            import json

            # Helper function to parse date strings
            def parse_date(date_value):
                """Convert date string to date object, handling various formats"""
                if date_value is None:
                    return None
                if isinstance(date_value, str):
                    try:
                        # Try ISO format (YYYY-MM-DD)
                        return datetime.strptime(date_value, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            # Try alternate format (DD-MM-YYYY)
                            return datetime.strptime(date_value, '%d-%m-%Y').date()
                        except ValueError:
                            logger.warning(f"Could not parse date: {date_value}, using NULL")
                            return None
                return date_value  # Already a date object

            # Parse date fields
            invoice_date = parse_date(payload.get("date"))
            due_date = parse_date(payload.get("due_date"))

            result = await self.db.execute(
                text("""
                    INSERT INTO invoices (zoho_invoice_id, invoice_number, customer_id, invoice_date, due_date, total, status, zoho_data, updated_at)
                    VALUES (:zoho_invoice_id, :invoice_number, :customer_id, :invoice_date, :due_date, :total, :status, :zoho_data, NOW())
                    ON CONFLICT (zoho_invoice_id)
                    DO UPDATE SET
                        invoice_number = EXCLUDED.invoice_number,
                        customer_id = EXCLUDED.customer_id,
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
                    "customer_id": payload.get("customer_id", ""),
                    "invoice_date": invoice_date,
                    "due_date": due_date,
                    "total": float(payload.get("total", 0)),
                    "status": payload.get("status", "draft"),
                    "zoho_data": json.dumps(payload)
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

        NOTE: Bills table not yet implemented in database schema
        """
        logger.warning("BillHandler called but bills table does not exist in database")
        raise NotImplementedError("Bills table not yet implemented. Please create the bills table first.")


class CreditNoteHandler(BaseEntityHandler):
    """Handler for credit note synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync credit note to local credit_notes table

        NOTE: Credit notes table not yet implemented in database schema
        """
        logger.warning("CreditNoteHandler called but credit_notes table does not exist in database")
        raise NotImplementedError("Credit notes table not yet implemented. Please create the credit_notes table first.")


class StockAdjustmentHandler(BaseEntityHandler):
    """Handler for stock adjustment synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync stock adjustment to local stock_adjustments table

        NOTE: Stock adjustments table not yet implemented in database schema
        """
        logger.warning("StockAdjustmentHandler called but stock_adjustments table does not exist in database")
        raise NotImplementedError("Stock adjustments table not yet implemented. Please create the stock_adjustments table first.")


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
                    INSERT INTO pricelists (zoho_pricelist_id, name, currency, is_active, updated_at)
                    VALUES (:zoho_pricelist_id, :name, :currency, :is_active, NOW())
                    ON CONFLICT (zoho_pricelist_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        currency = EXCLUDED.currency,
                        is_active = EXCLUDED.is_active,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_pricelist_id": zoho_pricelist_id,
                    "name": payload.get("name", ""),
                    "currency": payload.get("currency_code", "IQD"),
                    "is_active": payload.get("is_active", True),
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
        # Handle both "invoice" and "EntityType.INVOICE" formats
        entity_key = entity_type.lower()
        if "." in entity_key:
            # Extract value from enum string (e.g., "EntityType.INVOICE" -> "invoice")
            entity_key = entity_key.split(".")[-1]

        handler_class = cls._handlers.get(entity_key)
        if not handler_class:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        return handler_class(db)

    @classmethod
    def is_supported(cls, entity_type: str) -> bool:
        """Check if entity type is supported"""
        return entity_type.lower() in cls._handlers
