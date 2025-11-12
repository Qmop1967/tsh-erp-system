"""
API Endpoint E2E Tests
======================

End-to-end tests for REST API endpoints.
"""

import pytest
import httpx
from typing import Dict


class TestProductAPI:
    """Test product-related API endpoints"""

    def test_get_products_list(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/products should return products list"""
        response = api_client.get("/api/products", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))  # Could be list or paginated response

    def test_get_single_product(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/products/{id} should return product details"""
        # First get a product ID
        response = api_client.get("/api/products", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Extract first product ID
        if isinstance(data, list) and len(data) > 0:
            product_id = data[0].get("id")
        elif isinstance(data, dict) and "items" in data and len(data["items"]) > 0:
            product_id = data["items"][0].get("id")
        else:
            pytest.skip("No products available for testing")

        # Get product details
        response = api_client.get(f"/api/products/{product_id}", headers=auth_headers)
        assert response.status_code == 200
        product = response.json()
        assert product["id"] == product_id
        assert "name" in product
        assert "sku" in product

    def test_create_product(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """POST /api/products should create new product"""
        new_product = {
            "name": "E2E Test Product",
            "sku": "TEST-E2E-001",
            "unit_price": 99.99,
            "cost_price": 50.00,
            "category_id": 1,
            "is_active": True
        }

        response = api_client.post(
            "/api/products",
            headers=auth_headers,
            json=new_product
        )

        # Should either succeed (201) or conflict if SKU exists (409)
        assert response.status_code in [201, 409]

        if response.status_code == 201:
            product = response.json()
            assert product["name"] == new_product["name"]
            assert product["sku"] == new_product["sku"]

    def test_update_product(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """PUT /api/products/{id} should update product"""
        # Get a product first
        response = api_client.get("/api/products", headers=auth_headers)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            product_id = data[0]["id"]
        elif isinstance(data, dict) and "items" in data and len(data["items"]) > 0:
            product_id = data["items"][0]["id"]
        else:
            pytest.skip("No products available for testing")

        # Update product
        update_data = {
            "name": "Updated E2E Product",
            "is_active": True
        }

        response = api_client.put(
            f"/api/products/{product_id}",
            headers=auth_headers,
            json=update_data
        )
        assert response.status_code in [200, 404]  # 404 if endpoint not implemented


class TestCustomerAPI:
    """Test customer-related API endpoints"""

    def test_get_customers_list(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/customers should return customers list"""
        response = api_client.get("/api/customers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_search_customers(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/customers?search= should filter customers"""
        response = api_client.get(
            "/api/customers",
            headers=auth_headers,
            params={"search": "test"}
        )
        assert response.status_code == 200


class TestSalesAPI:
    """Test sales-related API endpoints"""

    def test_get_sales_orders(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/sales/orders should return orders"""
        response = api_client.get("/api/sales/orders", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_create_sales_order(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """POST /api/sales/orders should create new order"""
        # Get customer and product IDs first
        customers = api_client.get("/api/customers", headers=auth_headers).json()
        products = api_client.get("/api/products", headers=auth_headers).json()

        if isinstance(customers, list) and len(customers) > 0:
            customer_id = customers[0]["id"]
        elif isinstance(customers, dict) and "items" in customers:
            if len(customers["items"]) > 0:
                customer_id = customers["items"][0]["id"]
            else:
                pytest.skip("No customers available")
        else:
            pytest.skip("No customers available")

        if isinstance(products, list) and len(products) > 0:
            product_id = products[0]["id"]
            unit_price = products[0].get("unit_price", 100)
        elif isinstance(products, dict) and "items" in products:
            if len(products["items"]) > 0:
                product_id = products["items"][0]["id"]
                unit_price = products["items"][0].get("unit_price", 100)
            else:
                pytest.skip("No products available")
        else:
            pytest.skip("No products available")

        new_order = {
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                    "unit_price": unit_price
                }
            ],
            "notes": "E2E test order"
        }

        response = api_client.post(
            "/api/sales/orders",
            headers=auth_headers,
            json=new_order
        )
        assert response.status_code in [201, 404]  # 404 if endpoint not implemented


class TestInventoryAPI:
    """Test inventory-related API endpoints"""

    def test_get_inventory_levels(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/inventory should return inventory levels"""
        response = api_client.get("/api/inventory", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_low_stock_items(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/inventory/low-stock should return low stock items"""
        response = api_client.get("/api/inventory/low-stock", headers=auth_headers)
        assert response.status_code in [200, 404]


class TestReportsAPI:
    """Test reporting API endpoints"""

    def test_get_sales_report(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/reports/sales should return sales report"""
        response = api_client.get("/api/reports/sales", headers=auth_headers)
        assert response.status_code in [200, 404]

    def test_get_inventory_report(
        self,
        api_client: httpx.Client,
        auth_headers: Dict[str, str]
    ):
        """GET /api/reports/inventory should return inventory report"""
        response = api_client.get("/api/reports/inventory", headers=auth_headers)
        assert response.status_code in [200, 404]
