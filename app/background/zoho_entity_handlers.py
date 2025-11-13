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
# SALES ORDER HANDLER
# ============================================================================

class SalesOrderHandler(BaseEntityHandler):
    """Handler for sales order synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync sales order to local sales_orders and sales_items tables

        Expected payload fields:
        - salesorder_id (required)
        - salesorder_number (required)
        - customer_id (required)
        - date
        - shipment_date
        - line_items[] (array of products)
          - item_id
          - quantity
          - rate (unit price)
          - discount
        - subtotal
        - tax_total
        - total
        - status
        """
        try:
            zoho_salesorder_id = payload.get("salesorder_id")
            if not zoho_salesorder_id:
                raise ValueError("Missing required field: salesorder_id")

            from sqlalchemy import text
            from datetime import datetime
            import json

            # Helper function to parse date strings
            def parse_date(date_value):
                """Convert date string to date object"""
                if date_value is None:
                    return None
                if isinstance(date_value, str):
                    try:
                        return datetime.strptime(date_value, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            return datetime.strptime(date_value, '%d-%m-%Y').date()
                        except ValueError:
                            logger.warning(f"Could not parse date: {date_value}, using NULL")
                            return None
                return date_value

            # Parse dates
            order_date = parse_date(payload.get("date"))
            shipment_date = parse_date(payload.get("shipment_date"))
            expected_delivery_date = parse_date(payload.get("delivery_date"))

            # Map Zoho customer_id to local customer
            zoho_customer_id = payload.get("customer_id", "")

            # Get local customer ID from zoho_contact_id
            customer_result = await self.db.execute(
                text("SELECT id FROM customers WHERE zoho_contact_id = :zoho_contact_id LIMIT 1"),
                {"zoho_contact_id": str(zoho_customer_id)}
            )
            customer_row = customer_result.fetchone()
            local_customer_id = customer_row[0] if customer_row else None

            if not local_customer_id:
                logger.warning(f"Customer not found for zoho_contact_id: {zoho_customer_id}, creating placeholder")
                # Create placeholder customer (you may want to sync customer first)
                placeholder_result = await self.db.execute(
                    text("""
                        INSERT INTO customers (zoho_contact_id, contact_name, created_at, updated_at)
                        VALUES (:zoho_contact_id, :contact_name, NOW(), NOW())
                        RETURNING id
                    """),
                    {
                        "zoho_contact_id": str(zoho_customer_id),
                        "contact_name": payload.get("customer_name", f"Customer {zoho_customer_id}")
                    }
                )
                await self.db.commit()
                placeholder_row = placeholder_result.fetchone()
                local_customer_id = placeholder_row[0] if placeholder_row else None

            # Step 1: Upsert sales order header
            # Note: Assuming zoho_salesorder_id column exists or using order_number as unique
            result = await self.db.execute(
                text("""
                    INSERT INTO sales_orders (
                        order_number,
                        customer_id,
                        branch_id,
                        warehouse_id,
                        order_date,
                        expected_delivery_date,
                        actual_delivery_date,
                        status,
                        payment_status,
                        payment_method,
                        subtotal,
                        discount_percentage,
                        discount_amount,
                        tax_percentage,
                        tax_amount,
                        total_amount,
                        paid_amount,
                        notes,
                        created_by,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :order_number,
                        :customer_id,
                        :branch_id,
                        :warehouse_id,
                        :order_date,
                        :expected_delivery_date,
                        :actual_delivery_date,
                        :status,
                        :payment_status,
                        :payment_method,
                        :subtotal,
                        :discount_percentage,
                        :discount_amount,
                        :tax_percentage,
                        :tax_amount,
                        :total_amount,
                        :paid_amount,
                        :notes,
                        :created_by,
                        NOW(),
                        NOW()
                    )
                    ON CONFLICT (order_number)
                    DO UPDATE SET
                        customer_id = EXCLUDED.customer_id,
                        order_date = EXCLUDED.order_date,
                        expected_delivery_date = EXCLUDED.expected_delivery_date,
                        actual_delivery_date = EXCLUDED.actual_delivery_date,
                        status = EXCLUDED.status,
                        payment_status = EXCLUDED.payment_status,
                        payment_method = EXCLUDED.payment_method,
                        subtotal = EXCLUDED.subtotal,
                        discount_percentage = EXCLUDED.discount_percentage,
                        discount_amount = EXCLUDED.discount_amount,
                        tax_percentage = EXCLUDED.tax_percentage,
                        tax_amount = EXCLUDED.tax_amount,
                        total_amount = EXCLUDED.total_amount,
                        paid_amount = EXCLUDED.paid_amount,
                        notes = EXCLUDED.notes,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "order_number": payload.get("salesorder_number", f"SO-{zoho_salesorder_id}"),
                    "customer_id": local_customer_id,
                    "branch_id": 1,  # Default branch (TODO: map from Zoho or config)
                    "warehouse_id": 1,  # Default warehouse (TODO: map from Zoho or config)
                    "order_date": order_date or datetime.utcnow().date(),
                    "expected_delivery_date": expected_delivery_date,
                    "actual_delivery_date": shipment_date,
                    "status": payload.get("status", "DRAFT").upper(),
                    "payment_status": "PENDING",  # TODO: derive from payment info
                    "payment_method": None,
                    "subtotal": float(payload.get("sub_total", 0)),
                    "discount_percentage": float(payload.get("discount_percent", 0)),
                    "discount_amount": float(payload.get("discount", 0)),
                    "tax_percentage": 0,  # TODO: calculate from line items
                    "tax_amount": float(payload.get("tax_total", 0)),
                    "total_amount": float(payload.get("total", 0)),
                    "paid_amount": 0,  # TODO: sync from payments
                    "notes": payload.get("notes", ""),
                    "created_by": 1,  # TODO: map from Zoho user or use system user
                }
            )

            row = result.fetchone()
            sales_order_id = row[0] if row else None

            records_affected = 1

            # Step 2: Sync line items
            line_items = payload.get("line_items", [])
            if line_items and sales_order_id:
                # First, delete existing items for this order (to handle updates)
                await self.db.execute(
                    text("DELETE FROM sales_items WHERE sales_order_id = :sales_order_id"),
                    {"sales_order_id": sales_order_id}
                )

                for item in line_items:
                    zoho_item_id = item.get("item_id")
                    if not zoho_item_id:
                        logger.warning(f"Line item missing item_id, skipping")
                        continue

                    # Get local product ID from zoho_item_id
                    product_result = await self.db.execute(
                        text("SELECT id FROM products WHERE zoho_item_id = :zoho_item_id LIMIT 1"),
                        {"zoho_item_id": str(zoho_item_id)}
                    )
                    product_row = product_result.fetchone()

                    if not product_row:
                        logger.warning(f"Product not found for zoho_item_id: {zoho_item_id}, skipping line item")
                        continue

                    product_id = product_row[0]
                    quantity = float(item.get("quantity", 0))
                    unit_price = float(item.get("rate", 0))
                    discount_amount = float(item.get("discount_amount", 0))
                    line_total = float(item.get("item_total", quantity * unit_price - discount_amount))

                    # Insert sales item
                    await self.db.execute(
                        text("""
                            INSERT INTO sales_items (
                                sales_order_id,
                                product_id,
                                quantity,
                                unit_price,
                                discount_percentage,
                                discount_amount,
                                line_total,
                                delivered_quantity,
                                notes
                            )
                            VALUES (
                                :sales_order_id,
                                :product_id,
                                :quantity,
                                :unit_price,
                                :discount_percentage,
                                :discount_amount,
                                :line_total,
                                :delivered_quantity,
                                :notes
                            )
                        """),
                        {
                            "sales_order_id": sales_order_id,
                            "product_id": product_id,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "discount_percentage": float(item.get("discount", 0)),
                            "discount_amount": discount_amount,
                            "line_total": line_total,
                            "delivered_quantity": float(item.get("quantity_invoiced", 0)),
                            "notes": item.get("description", "")
                        }
                    )

                    records_affected += 1

            await self.db.commit()

            logger.info(
                f"Sales order synced successfully: {zoho_salesorder_id} -> local ID {sales_order_id} "
                f"({len(line_items)} items)"
            )

            return {
                "success": True,
                "local_entity_id": str(sales_order_id),
                "operation_performed": "upsert_salesorder_and_items",
                "records_affected": records_affected
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Sales order sync failed: {e}", exc_info=True)
            raise


# ============================================================================
# PAYMENT HANDLER
# ============================================================================

class PaymentHandler(BaseEntityHandler):
    """Handler for customer payment synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync customer payment to local invoice_payments table

        Expected payload fields:
        - payment_id (required)
        - payment_number (required)
        - customer_id
        - date (payment date)
        - amount
        - payment_mode (cash, bank, card, check, etc.)
        - reference_number
        - bank_name / bank_account
        - invoices[] (array of invoices this payment applies to)
          - invoice_id
          - invoice_number
          - amount_applied
        """
        try:
            zoho_payment_id = payload.get("payment_id")
            if not zoho_payment_id:
                raise ValueError("Missing required field: payment_id")

            from sqlalchemy import text
            from datetime import datetime

            # Helper function to parse date strings
            def parse_date(date_value):
                """Convert date string to date object"""
                if date_value is None:
                    return None
                if isinstance(date_value, str):
                    try:
                        return datetime.strptime(date_value, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            return datetime.strptime(date_value, '%d-%m-%Y').date()
                        except ValueError:
                            logger.warning(f"Could not parse date: {date_value}, using today")
                            return datetime.utcnow().date()
                return date_value

            # Parse payment date
            payment_date = parse_date(payload.get("date"))

            # Get invoices this payment applies to
            invoices = payload.get("invoices", [])

            # If there are multiple invoices, create one payment record per invoice
            # If no invoices specified, create one general payment record
            if not invoices:
                invoices = [{"invoice_id": None, "amount_applied": payload.get("amount", 0)}]

            records_affected = 0

            for invoice_payment in invoices:
                zoho_invoice_id = invoice_payment.get("invoice_id")
                amount_applied = float(invoice_payment.get("amount_applied", 0))

                # Get local invoice ID if specified
                local_invoice_id = None
                if zoho_invoice_id:
                    invoice_result = await self.db.execute(
                        text("SELECT id FROM invoices WHERE zoho_invoice_id = :zoho_invoice_id LIMIT 1"),
                        {"zoho_invoice_id": str(zoho_invoice_id)}
                    )
                    invoice_row = invoice_result.fetchone()
                    if invoice_row:
                        local_invoice_id = invoice_row[0]
                    else:
                        logger.warning(f"Invoice not found for zoho_invoice_id: {zoho_invoice_id}, payment will be unlinked")

                # Upsert payment record
                result = await self.db.execute(
                    text("""
                        INSERT INTO invoice_payments (
                            payment_number,
                            sales_invoice_id,
                            purchase_invoice_id,
                            payment_date,
                            amount,
                            currency_id,
                            exchange_rate,
                            payment_method,
                            reference_number,
                            bank_account,
                            check_number,
                            check_date,
                            notes,
                            created_by,
                            created_at,
                            updated_at
                        )
                        VALUES (
                            :payment_number,
                            :sales_invoice_id,
                            :purchase_invoice_id,
                            :payment_date,
                            :amount,
                            :currency_id,
                            :exchange_rate,
                            :payment_method,
                            :reference_number,
                            :bank_account,
                            :check_number,
                            :check_date,
                            :notes,
                            :created_by,
                            NOW(),
                            NOW()
                        )
                        ON CONFLICT (payment_number)
                        DO UPDATE SET
                            sales_invoice_id = EXCLUDED.sales_invoice_id,
                            payment_date = EXCLUDED.payment_date,
                            amount = EXCLUDED.amount,
                            payment_method = EXCLUDED.payment_method,
                            reference_number = EXCLUDED.reference_number,
                            bank_account = EXCLUDED.bank_account,
                            check_number = EXCLUDED.check_number,
                            check_date = EXCLUDED.check_date,
                            notes = EXCLUDED.notes,
                            updated_at = NOW()
                        RETURNING id
                    """),
                    {
                        "payment_number": payload.get("payment_number", f"PAY-{zoho_payment_id}"),
                        "sales_invoice_id": local_invoice_id,  # Link to sales invoice
                        "purchase_invoice_id": None,  # Not applicable for customer payments
                        "payment_date": payment_date or datetime.utcnow().date(),
                        "amount": amount_applied,
                        "currency_id": 1,  # Default currency (TODO: map from Zoho or config)
                        "exchange_rate": float(payload.get("exchange_rate", 1.0)),
                        "payment_method": payload.get("payment_mode", "UNKNOWN").upper(),
                        "reference_number": payload.get("reference_number", ""),
                        "bank_account": payload.get("bank_name", ""),
                        "check_number": payload.get("check_number", ""),
                        "check_date": parse_date(payload.get("check_date")),
                        "notes": payload.get("notes", ""),
                        "created_by": 1,  # TODO: map from Zoho user or use system user
                    }
                )

                row = result.fetchone()
                payment_id = row[0] if row else None
                records_affected += 1

                logger.info(f"Payment synced: {zoho_payment_id} -> invoice: {zoho_invoice_id or 'N/A'}, local ID {payment_id}")

            await self.db.commit()

            logger.info(
                f"Payment synced successfully: {zoho_payment_id} "
                f"({records_affected} payment records created)"
            )

            return {
                "success": True,
                "local_entity_id": str(zoho_payment_id),  # Return Zoho ID since we may have multiple records
                "operation_performed": "upsert_payment",
                "records_affected": records_affected
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Payment sync failed: {e}", exc_info=True)
            raise


# ============================================================================
# VENDOR HANDLER
# ============================================================================

class VendorHandler(BaseEntityHandler):
    """Handler for vendor/supplier synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync vendor to local vendors table

        Expected payload fields:
        - vendor_id (required)
        - vendor_name (required)
        - company_name
        - email
        - phone
        - billing_address
        - shipping_address
        - payment_terms
        - currency_code
        """
        try:
            zoho_vendor_id = payload.get("vendor_id") or payload.get("contact_id")
            if not zoho_vendor_id:
                raise ValueError("Missing required field: vendor_id or contact_id")

            from sqlalchemy import text
            import json

            # Extract addresses
            billing_address = payload.get("billing_address", {})
            shipping_address = payload.get("shipping_address", {})

            # Try to create vendors table if it doesn't exist
            # This is a temporary solution until proper migration is run
            try:
                await self.db.execute(text("""
                    CREATE TABLE IF NOT EXISTS vendors (
                        id SERIAL PRIMARY KEY,
                        zoho_vendor_id VARCHAR NOT NULL UNIQUE,
                        vendor_name VARCHAR NOT NULL,
                        company_name VARCHAR,
                        email VARCHAR,
                        phone VARCHAR,
                        billing_address JSONB,
                        shipping_address JSONB,
                        payment_terms VARCHAR,
                        currency_code VARCHAR DEFAULT 'IQD',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                await self.db.commit()
                logger.info("Vendors table created or already exists")
            except Exception as e:
                logger.warning(f"Could not create vendors table: {e}")
                await self.db.rollback()

            # Upsert vendor
            result = await self.db.execute(
                text("""
                    INSERT INTO vendors (
                        zoho_vendor_id,
                        vendor_name,
                        company_name,
                        email,
                        phone,
                        billing_address,
                        shipping_address,
                        payment_terms,
                        currency_code,
                        is_active,
                        updated_at
                    )
                    VALUES (
                        :zoho_vendor_id,
                        :vendor_name,
                        :company_name,
                        :email,
                        :phone,
                        :billing_address,
                        :shipping_address,
                        :payment_terms,
                        :currency_code,
                        :is_active,
                        NOW()
                    )
                    ON CONFLICT (zoho_vendor_id)
                    DO UPDATE SET
                        vendor_name = EXCLUDED.vendor_name,
                        company_name = EXCLUDED.company_name,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        billing_address = EXCLUDED.billing_address,
                        shipping_address = EXCLUDED.shipping_address,
                        payment_terms = EXCLUDED.payment_terms,
                        currency_code = EXCLUDED.currency_code,
                        is_active = EXCLUDED.is_active,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_vendor_id": str(zoho_vendor_id),
                    "vendor_name": payload.get("vendor_name") or payload.get("contact_name", ""),
                    "company_name": payload.get("company_name", ""),
                    "email": payload.get("email", ""),
                    "phone": payload.get("phone", ""),
                    "billing_address": json.dumps(billing_address) if billing_address else None,
                    "shipping_address": json.dumps(shipping_address) if shipping_address else None,
                    "payment_terms": payload.get("payment_terms", "NET_30"),
                    "currency_code": payload.get("currency_code", "IQD"),
                    "is_active": payload.get("is_active", True),
                }
            )

            await self.db.commit()

            row = result.fetchone()
            vendor_id = row[0] if row else None

            logger.info(f"Vendor synced successfully: {zoho_vendor_id} -> local ID {vendor_id}")

            return {
                "success": True,
                "local_entity_id": str(vendor_id),
                "operation_performed": "upsert",
                "records_affected": 1
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Vendor sync failed: {e}", exc_info=True)
            raise


# ============================================================================
# USER HANDLER
# ============================================================================

class UserHandler(BaseEntityHandler):
    """Handler for Zoho user synchronization"""

    async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """
        Sync Zoho user to local zoho_users table

        Expected payload fields:
        - user_id (required)
        - name (required)
        - email (required)
        - role
        - status
        """
        try:
            zoho_user_id = payload.get("user_id")
            if not zoho_user_id:
                raise ValueError("Missing required field: user_id")

            from sqlalchemy import text
            import json

            # Try to create zoho_users table if it doesn't exist
            try:
                await self.db.execute(text("""
                    CREATE TABLE IF NOT EXISTS zoho_users (
                        id SERIAL PRIMARY KEY,
                        zoho_user_id VARCHAR NOT NULL UNIQUE,
                        name VARCHAR NOT NULL,
                        email VARCHAR NOT NULL,
                        role VARCHAR,
                        status VARCHAR DEFAULT 'active',
                        zoho_data JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                await self.db.commit()
                logger.info("Zoho users table created or already exists")
            except Exception as e:
                logger.warning(f"Could not create zoho_users table: {e}")
                await self.db.rollback()

            # Upsert user
            result = await self.db.execute(
                text("""
                    INSERT INTO zoho_users (
                        zoho_user_id,
                        name,
                        email,
                        role,
                        status,
                        zoho_data,
                        updated_at
                    )
                    VALUES (
                        :zoho_user_id,
                        :name,
                        :email,
                        :role,
                        :status,
                        :zoho_data,
                        NOW()
                    )
                    ON CONFLICT (zoho_user_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        role = EXCLUDED.role,
                        status = EXCLUDED.status,
                        zoho_data = EXCLUDED.zoho_data,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "zoho_user_id": str(zoho_user_id),
                    "name": payload.get("name", ""),
                    "email": payload.get("email", ""),
                    "role": payload.get("role", ""),
                    "status": payload.get("status", "active"),
                    "zoho_data": json.dumps(payload),
                }
            )

            await self.db.commit()

            row = result.fetchone()
            user_id = row[0] if row else None

            logger.info(f"Zoho user synced successfully: {zoho_user_id} -> local ID {user_id}")

            return {
                "success": True,
                "local_entity_id": str(user_id),
                "operation_performed": "upsert",
                "records_affected": 1
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Zoho user sync failed: {e}", exc_info=True)
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
        "order": SalesOrderHandler,  # Sales orders
        "salesorder": SalesOrderHandler,  # Alternate key
        "payment": PaymentHandler,  # Customer payments
        "customerpayment": PaymentHandler,  # Alternate key
        "vendor": VendorHandler,  # Vendors/suppliers
        "supplier": VendorHandler,  # Alternate key
        "user": UserHandler,  # Zoho users
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
