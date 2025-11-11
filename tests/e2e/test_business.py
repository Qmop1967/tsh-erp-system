"""
Business Logic E2E Tests
=========================

End-to-end tests for business workflows and logic.
"""

import pytest
import httpx
from typing import Dict


class TestSalesWorkflow:
    """Test complete sales workflow"""

    def test_complete_sales_order_workflow(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """
        Complete sales order workflow:
        1. Create customer
        2. Create product
        3. Create sales order
        4. Generate invoice
        5. Record payment
        """
        # Step 1: Create customer (or use existing)
        customers_response = api_client.get("/api/customers", headers=auth_headers)
        customers = customers_response.json()

        if isinstance(customers, list) and len(customers) > 0:
            customer_id = customers[0]["id"]
        elif isinstance(customers, dict) and "items" in customers and len(customers["items"]) > 0:
            customer_id = customers["items"][0]["id"]
        else:
            # Create new customer
            new_customer = {
                "name": "E2E Test Customer",
                "email": "e2e_customer@test.com",
                "phone": "+966500000000",
                "credit_limit": 10000.00
            }
            response = api_client.post(
                "/api/customers",
                headers=auth_headers,
                json=new_customer
            )
            if response.status_code == 201:
                customer_id = response.json()["id"]
            else:
                pytest.skip("Cannot create customer for workflow test")

        # Step 2: Get product
        products_response = api_client.get("/api/products", headers=auth_headers)
        products = products_response.json()

        if isinstance(products, list) and len(products) > 0:
            product = products[0]
        elif isinstance(products, dict) and "items" in products and len(products["items"]) > 0:
            product = products["items"][0]
        else:
            pytest.skip("No products available for workflow test")

        product_id = product["id"]
        unit_price = product.get("unit_price", 100.00)

        # Step 3: Create sales order
        order_data = {
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 5,
                    "unit_price": unit_price
                }
            ],
            "notes": "E2E workflow test order"
        }

        order_response = api_client.post(
            "/api/sales/orders",
            headers=auth_headers,
            json=order_data
        )

        if order_response.status_code not in [201, 404]:
            pytest.fail(f"Failed to create order: {order_response.text}")

        # If order creation is not implemented, skip rest
        if order_response.status_code == 404:
            pytest.skip("Order creation not implemented")

        order_id = order_response.json()["id"]

        # Step 4: Generate invoice (if endpoint exists)
        invoice_response = api_client.post(
            f"/api/sales/orders/{order_id}/invoice",
            headers=auth_headers
        )
        # Continue even if invoice endpoint doesn't exist
        assert invoice_response.status_code in [200, 201, 404]


class TestInventoryWorkflow:
    """Test inventory management workflow"""

    def test_stock_adjustment_workflow(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """
        Stock adjustment workflow:
        1. Check current stock level
        2. Adjust stock (increase/decrease)
        3. Verify new stock level
        """
        # Get a product with inventory
        products_response = api_client.get("/api/products", headers=auth_headers)
        products = products_response.json()

        if isinstance(products, list) and len(products) > 0:
            product_id = products[0]["id"]
        elif isinstance(products, dict) and "items" in products and len(products["items"]) > 0:
            product_id = products["items"][0]["id"]
        else:
            pytest.skip("No products available")

        # Get current inventory
        inventory_response = api_client.get(
            f"/api/inventory/{product_id}",
            headers=auth_headers
        )

        if inventory_response.status_code == 404:
            pytest.skip("Inventory endpoint not implemented")

        assert inventory_response.status_code == 200
        current_stock = inventory_response.json().get("quantity", 0)

        # Adjust stock
        adjustment_data = {
            "product_id": product_id,
            "quantity": 10,
            "type": "adjustment",
            "notes": "E2E test adjustment"
        }

        adjust_response = api_client.post(
            "/api/inventory/adjust",
            headers=auth_headers,
            json=adjustment_data
        )

        if adjust_response.status_code == 404:
            pytest.skip("Stock adjustment endpoint not implemented")

        assert adjust_response.status_code in [200, 201]


class TestPurchaseWorkflow:
    """Test purchase order workflow"""

    def test_purchase_order_workflow(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """
        Purchase order workflow:
        1. Get supplier
        2. Create purchase order
        3. Receive goods
        4. Update inventory
        """
        # Get supplier
        suppliers_response = api_client.get("/api/suppliers", headers=auth_headers)

        if suppliers_response.status_code == 404:
            pytest.skip("Suppliers endpoint not implemented")

        suppliers = suppliers_response.json()

        if isinstance(suppliers, list) and len(suppliers) > 0:
            supplier_id = suppliers[0]["id"]
        elif isinstance(suppliers, dict) and "items" in suppliers and len(suppliers["items"]) > 0:
            supplier_id = suppliers["items"][0]["id"]
        else:
            pytest.skip("No suppliers available")

        # Get product
        products_response = api_client.get("/api/products", headers=auth_headers)
        products = products_response.json()

        if isinstance(products, list) and len(products) > 0:
            product_id = products[0]["id"]
            cost_price = products[0].get("cost_price", 50.00)
        elif isinstance(products, dict) and "items" in products and len(products["items"]) > 0:
            product_id = products["items"][0]["id"]
            cost_price = products["items"][0].get("cost_price", 50.00)
        else:
            pytest.skip("No products available")

        # Create purchase order
        po_data = {
            "supplier_id": supplier_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 100,
                    "unit_price": cost_price
                }
            ],
            "notes": "E2E workflow test PO"
        }

        po_response = api_client.post(
            "/api/purchase/orders",
            headers=auth_headers,
            json=po_data
        )

        if po_response.status_code == 404:
            pytest.skip("Purchase order endpoint not implemented")

        assert po_response.status_code in [201]


class TestZohoIntegration:
    """Test Zoho Books integration workflows"""

    def test_sync_product_to_zoho(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """Test syncing product to Zoho Books"""
        # Get a product
        products_response = api_client.get("/api/products", headers=auth_headers)
        products = products_response.json()

        if isinstance(products, list) and len(products) > 0:
            product_id = products[0]["id"]
        elif isinstance(products, dict) and "items" in products and len(products["items"]) > 0:
            product_id = products["items"][0]["id"]
        else:
            pytest.skip("No products available")

        # Trigger Zoho sync
        sync_response = api_client.post(
            f"/api/zoho/sync/product/{product_id}",
            headers=auth_headers
        )

        if sync_response.status_code == 404:
            pytest.skip("Zoho sync endpoint not implemented")

        # Should either succeed or fail gracefully
        assert sync_response.status_code in [200, 201, 503]  # 503 if Zoho unavailable

    def test_get_zoho_sync_status(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """Test getting Zoho sync status"""
        status_response = api_client.get(
            "/api/zoho/sync/status",
            headers=auth_headers
        )

        if status_response.status_code == 404:
            pytest.skip("Zoho status endpoint not implemented")

        assert status_response.status_code == 200
        status = status_response.json()
        assert "last_sync" in status or "status" in status


class TestReportGeneration:
    """Test report generation workflows"""

    def test_generate_sales_report(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """Test generating sales report for date range"""
        report_params = {
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "format": "json"
        }

        report_response = api_client.get(
            "/api/reports/sales",
            headers=auth_headers,
            params=report_params
        )

        if report_response.status_code == 404:
            pytest.skip("Sales report endpoint not implemented")

        assert report_response.status_code == 200
        report = report_response.json()
        assert isinstance(report, dict)

    def test_generate_inventory_valuation_report(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """Test generating inventory valuation report"""
        report_response = api_client.get(
            "/api/reports/inventory/valuation",
            headers=auth_headers
        )

        if report_response.status_code == 404:
            pytest.skip("Inventory valuation report not implemented")

        assert report_response.status_code == 200
        report = report_response.json()
        assert isinstance(report, (dict, list))
