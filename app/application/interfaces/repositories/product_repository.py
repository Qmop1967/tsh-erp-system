"""
Product Repository Interface

Defines the contract for product repository implementations.
"""

from abc import abstractmethod
from typing import List, Optional
from app.application.interfaces.repositories.base_repository import IBaseRepository
from app.models import Product


class IProductRepository(IBaseRepository[Product, int]):
    """
    Product repository interface for data access operations.

    This interface extends the base repository with product-specific
    operations for searching, filtering, and managing product data.
    """

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get a product by SKU.

        Args:
            sku: Product SKU (Stock Keeping Unit)

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """
        Get a product by barcode.

        Args:
            barcode: Product barcode

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """
        Get products in a specific category.

        Args:
            category_id: Category ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (optional)

        Returns:
            List of products
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """
        Search products by name, SKU, or barcode.

        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (optional)

        Returns:
            List of matching products
        """
        pass

    @abstractmethod
    async def get_active_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get all active products.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active products
        """
        pass

    @abstractmethod
    async def get_low_stock_products(
        self,
        threshold: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get products with low stock levels.

        Args:
            threshold: Stock threshold (uses reorder_level if not provided)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of low stock products
        """
        pass

    @abstractmethod
    async def get_out_of_stock_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get out of stock products.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of out of stock products
        """
        pass

    @abstractmethod
    async def get_products_by_price_range(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get products filtered by price range.

        Args:
            min_price: Minimum price (optional)
            max_price: Maximum price (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of products within price range
        """
        pass

    @abstractmethod
    async def get_by_zoho_item_id(self, zoho_item_id: str) -> Optional[Product]:
        """
        Get a product by Zoho item ID.

        Args:
            zoho_item_id: Zoho item ID

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    async def count_by_category(
        self,
        category_id: int,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Count products in a category.

        Args:
            category_id: Category ID
            is_active: Filter by active status (optional)

        Returns:
            Number of products
        """
        pass

    @abstractmethod
    async def update_stock_quantity(
        self,
        product_id: int,
        quantity_change: int
    ) -> Optional[Product]:
        """
        Update product stock quantity.

        Args:
            product_id: Product ID
            quantity_change: Change in quantity (positive for increase, negative for decrease)

        Returns:
            Updated product if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_products_by_supplier(
        self,
        supplier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get products from a specific supplier.

        Args:
            supplier_id: Supplier ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of products
        """
        pass

    @abstractmethod
    async def get_featured_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get featured products (for e-commerce display).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of featured products
        """
        pass
