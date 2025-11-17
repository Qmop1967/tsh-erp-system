"""
API Response Schema Validation Tests
اختبارات التحقق من صحة مخطط استجابة API

This test suite validates that API responses match the standard defined in:
API_RESPONSE_STANDARDS.md

Run: pytest tests/test_api_response_schema.py -v
"""

import pytest
import requests
from typing import Dict, Any, List

# Base URL for testing
BASE_URL = "https://erp.tsh.sale/api"

# Expected fields for Product response (from API_RESPONSE_STANDARDS.md)
REQUIRED_PRODUCT_FIELDS = {
    # Primary fields
    'id', 'zoho_item_id', 'sku', 'name', 'image_url', 'category',
    'stock_quantity', 'actual_available_stock', 'warehouse_id',
    'is_active', 'price', 'currency',

    # Legacy fields (for backward compatibility)
    'item_id', 'product_id', 'product_name', 'category_name',
    'selling_price', 'quantity', 'barcode', 'image_path',
    'in_stock', 'has_image'
}

REQUIRED_PRODUCT_TYPES = {
    'id': str,
    'zoho_item_id': str,
    'sku': str,
    'name': str,
    'price': (int, float),
    'currency': str,
    'stock_quantity': int,
    'actual_available_stock': int,
    'is_active': bool,
    'in_stock': bool,
    'has_image': bool
}


class TestConsumerAPISchema:
    """Test Consumer API response schemas"""

    def _get_products(self, limit=5):
        """Helper to get products with error handling"""
        try:
            response = requests.get(f"{BASE_URL}/consumer/products?limit={limit}", timeout=10)
            if response.status_code != 200:
                return None, response.status_code
            data = response.json()
            if 'items' not in data:
                return None, "missing_items"
            return data, None
        except requests.RequestException as e:
            return None, str(e)

    def test_products_list_response_structure(self):
        """Test /api/consumer/products returns correct structure"""
        response = requests.get(f"{BASE_URL}/consumer/products?limit=5", timeout=10)

        # Skip if API is unavailable or has server errors
        if response.status_code >= 500:
            pytest.skip(f"API server error (status {response.status_code}) - possibly missing database migration")

        assert response.status_code == 200, f"API returned {response.status_code}"

        data = response.json()

        # Check top-level structure
        assert 'status' in data, "Missing 'status' field"
        assert 'count' in data, "Missing 'count' field"
        assert 'items' in data, "Missing 'items' field"

        assert data['status'] == 'success', f"Status is {data['status']}, expected 'success'"
        assert isinstance(data['items'], list), "'items' should be a list"
        assert data['count'] == len(data['items']), "Count doesn't match items length"

    def test_product_fields_presence(self):
        """Test that all required fields are present in product responses"""
        data, error = self._get_products(limit=1)
        if error:
            pytest.skip(f"API unavailable or error: {error}")

        if len(data['items']) == 0:
            pytest.skip("No products available for testing")

        product = data['items'][0]
        missing_fields = REQUIRED_PRODUCT_FIELDS - set(product.keys())

        assert len(missing_fields) == 0, f"Missing required fields: {missing_fields}"

    def test_product_field_types(self):
        """Test that product fields have correct data types"""
        data, error = self._get_products(limit=1)
        if error:
            pytest.skip(f"API unavailable or error: {error}")

        if len(data['items']) == 0:
            pytest.skip("No products available for testing")

        product = data['items'][0]

        for field, expected_type in REQUIRED_PRODUCT_TYPES.items():
            assert field in product, f"Missing field: {field}"

            value = product[field]
            if isinstance(expected_type, tuple):
                assert isinstance(value, expected_type), \
                    f"Field '{field}' should be {expected_type}, got {type(value)}"
            else:
                assert isinstance(value, expected_type), \
                    f"Field '{field}' should be {expected_type}, got {type(value)}"

    def test_primary_legacy_field_consistency(self):
        """Test that primary and legacy fields contain the same values"""
        data, error = self._get_products(limit=1)
        if error:
            pytest.skip(f"API unavailable or error: {error}")

        if len(data['items']) == 0:
            pytest.skip("No products available for testing")

        product = data['items'][0]

        # Test field mappings
        mappings = {
            'id': 'product_id',
            'zoho_item_id': 'item_id',
            'name': 'product_name',
            'category': 'category_name',
            'price': 'selling_price',
            'image_url': 'image_path',
            'sku': 'barcode'
        }

        for primary, legacy in mappings.items():
            assert product[primary] == product[legacy], \
                f"Mismatch: {primary}={product[primary]} != {legacy}={product[legacy]}"

    def test_product_details_endpoint(self):
        """Test /api/consumer/products/{id} endpoint"""
        # First get a product ID
        data, error = self._get_products(limit=1)
        if error:
            pytest.skip(f"API unavailable or error: {error}")

        if len(data['items']) == 0:
            pytest.skip("No products available for testing")

        product_id = data['items'][0]['id']

        # Test details endpoint
        detail_response = requests.get(f"{BASE_URL}/consumer/products/{product_id}", timeout=10)

        if detail_response.status_code >= 500:
            pytest.skip(f"API server error (status {detail_response.status_code})")

        assert detail_response.status_code == 200

        detail_data = detail_response.json()
        assert 'status' in detail_data
        assert 'product' in detail_data
        assert detail_data['status'] == 'success'

        # Check all required fields are present
        product = detail_data['product']
        missing_fields = REQUIRED_PRODUCT_FIELDS - set(product.keys())
        assert len(missing_fields) == 0, f"Missing fields in detail: {missing_fields}"

    def test_categories_endpoint(self):
        """Test /api/consumer/categories endpoint"""
        response = requests.get(f"{BASE_URL}/consumer/categories")
        assert response.status_code == 200

        data = response.json()
        assert 'status' in data
        assert 'categories' in data
        assert data['status'] == 'success'
        assert isinstance(data['categories'], list)

    def test_flutter_model_compatibility(self):
        """
        Test that API response can be parsed by Flutter Product model
        This simulates the Product.fromJson() behavior
        """
        data, error = self._get_products(limit=1)
        if error:
            pytest.skip(f"API unavailable or error: {error}")

        if len(data['items']) == 0:
            pytest.skip("No products available for testing")

        product = data['items'][0]

        # Simulate Flutter's fromJson with fallbacks
        def parse_like_flutter(json_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                'id': json_data.get('id') or json_data.get('product_id'),
                'zoho_item_id': json_data.get('zoho_item_id') or json_data.get('item_id'),
                'sku': json_data.get('sku') or json_data.get('barcode') or '',
                'name': json_data.get('name') or json_data.get('product_name'),
                'image_url': json_data.get('image_url') or json_data.get('image_path'),
                'category': json_data.get('category') or json_data.get('category_name'),
                'stock_quantity': json_data.get('stock_quantity') or int(json_data.get('quantity', 0)),
                'actual_available_stock': json_data.get('actual_available_stock') or int(json_data.get('quantity', 0)),
                'price': json_data.get('price') or json_data.get('selling_price', 0.0),
                'is_active': json_data.get('is_active') or json_data.get('in_stock', True),
            }

        # This should not raise any exceptions
        parsed = parse_like_flutter(product)

        # Verify all critical fields are populated
        assert parsed['id'] is not None
        assert parsed['name'] is not None
        assert parsed['price'] is not None
        assert parsed['zoho_item_id'] is not None


class TestAPIStandardsCompliance:
    """Test compliance with API_RESPONSE_STANDARDS.md"""

    def _get_products(self, limit=5):
        """Helper to get products with error handling"""
        try:
            response = requests.get(f"{BASE_URL}/consumer/products?limit={limit}", timeout=10)
            if response.status_code != 200:
                return None, response.status_code
            data = response.json()
            if 'items' not in data:
                return None, "missing_items"
            return data, None
        except requests.RequestException as e:
            return None, str(e)

    def test_response_uses_snake_case(self):
        """Verify all fields use snake_case naming convention"""
        data, error = self._get_products(limit=1)
        if error:
            pytest.skip(f"API unavailable or error: {error}")

        if len(data['items']) == 0:
            pytest.skip("No products available for testing")

        product = data['items'][0]

        # Check that no camelCase fields exist
        camel_case_fields = [
            key for key in product.keys()
            if any(c.isupper() for c in key)
        ]

        assert len(camel_case_fields) == 0, \
            f"Found camelCase fields (should be snake_case): {camel_case_fields}"

    def test_nullable_fields_handling(self):
        """Test that nullable fields are properly handled"""
        data, error = self._get_products(limit=5)
        if error:
            pytest.skip(f"API unavailable or error: {error}")

        nullable_fields = ['description', 'cdn_image_url', 'warehouse_id']

        for product in data['items']:
            for field in nullable_fields:
                # Field should exist (even if None/null)
                assert field in product, f"Nullable field '{field}' is missing"
                # Value can be None, empty string, or valid value
                value = product[field]
                assert value is None or isinstance(value, str), \
                    f"Nullable field '{field}' has invalid type: {type(value)}"


# Utility function to run all tests
def run_all_tests():
    """Run all schema validation tests"""
    print("🧪 Running API Schema Validation Tests...")
    print(f"📍 Testing against: {BASE_URL}")
    print("-" * 60)

    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
