"""
Product Service

Business logic layer for product operations using repository pattern.
"""

from typing import List, Optional
from app.application.interfaces.repositories.product_repository import IProductRepository
from app.application.dtos.product_dto import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
    ProductListResponseDTO,
    ProductSearchDTO,
    ProductSummaryDTO,
    StockUpdateDTO,
    ProductStockStatusDTO,
)
from app.models import Product


class ProductService:
    """
    Service class for product business logic.

    This service class handles all product-related business logic
    using the repository pattern for data access.
    """

    def __init__(self, product_repository: IProductRepository):
        """
        Initialize the service with a product repository.

        Args:
            product_repository: Product repository implementation
        """
        self.repository = product_repository

    async def get_product_by_id(self, product_id: int) -> Optional[ProductResponseDTO]:
        """
        Get a product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product response DTO if found, None otherwise
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            return None
        return ProductResponseDTO.model_validate(product)

    async def get_all_products(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> ProductListResponseDTO:
        """
        Get all products with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status

        Returns:
            Product list response DTO
        """
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active

        products = await self.repository.get_all(skip=skip, limit=limit, **filters)
        total = await self.repository.count(**filters)

        return ProductListResponseDTO(
            items=[ProductResponseDTO.model_validate(p) for p in products],
            total=total,
            skip=skip,
            limit=limit
        )

    async def create_product(self, dto: ProductCreateDTO) -> ProductResponseDTO:
        """
        Create a new product.

        Args:
            dto: Product creation DTO

        Returns:
            Created product response DTO

        Raises:
            ValueError: If SKU or barcode already exists
        """
        # Check for duplicate SKU
        if dto.sku:
            existing = await self.repository.get_by_sku(dto.sku)
            if existing:
                raise ValueError(f"Product with SKU {dto.sku} already exists")

        # Check for duplicate barcode
        if dto.barcode:
            existing = await self.repository.get_by_barcode(dto.barcode)
            if existing:
                raise ValueError(f"Product with barcode {dto.barcode} already exists")

        # Create product entity
        product = Product(**dto.model_dump())
        created_product = await self.repository.create(product)

        return ProductResponseDTO.model_validate(created_product)

    async def update_product(
        self,
        product_id: int,
        dto: ProductUpdateDTO
    ) -> Optional[ProductResponseDTO]:
        """
        Update an existing product.

        Args:
            product_id: Product ID
            dto: Product update DTO

        Returns:
            Updated product response DTO if found, None otherwise

        Raises:
            ValueError: If SKU or barcode conflicts with another product
        """
        existing_product = await self.repository.get_by_id(product_id)
        if not existing_product:
            return None

        # Check for duplicate SKU (if changing)
        if dto.sku and dto.sku != existing_product.sku:
            sku_exists = await self.repository.get_by_sku(dto.sku)
            if sku_exists:
                raise ValueError(f"Product with SKU {dto.sku} already exists")

        # Check for duplicate barcode (if changing)
        if dto.barcode and dto.barcode != existing_product.barcode:
            barcode_exists = await self.repository.get_by_barcode(dto.barcode)
            if barcode_exists:
                raise ValueError(f"Product with barcode {dto.barcode} already exists")

        # Update only provided fields
        update_data = dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_product, key, value)

        updated_product = await self.repository.update(product_id, existing_product)
        return ProductResponseDTO.model_validate(updated_product)

    async def delete_product(self, product_id: int) -> bool:
        """
        Delete a product (soft delete by setting is_active=False).

        Args:
            product_id: Product ID

        Returns:
            True if deleted, False if not found
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            return False

        # Soft delete
        product.is_active = False
        await self.repository.update(product_id, product)
        return True

    async def search_products(self, dto: ProductSearchDTO) -> ProductListResponseDTO:
        """
        Search products with filters.

        Args:
            dto: Product search DTO

        Returns:
            Product list response DTO
        """
        products = []
        total = 0

        if dto.low_stock:
            # Low stock filter
            products = await self.repository.get_low_stock_products(
                skip=dto.skip,
                limit=dto.limit
            )
            all_low_stock = await self.repository.get_low_stock_products(skip=0, limit=10000)
            total = len(all_low_stock)
        elif dto.out_of_stock:
            # Out of stock filter
            products = await self.repository.get_out_of_stock_products(
                skip=dto.skip,
                limit=dto.limit
            )
            all_out_of_stock = await self.repository.get_out_of_stock_products(skip=0, limit=10000)
            total = len(all_out_of_stock)
        elif dto.query:
            # Text search
            products = await self.repository.search(
                query=dto.query,
                skip=dto.skip,
                limit=dto.limit,
                is_active=dto.is_active
            )
            all_results = await self.repository.search(
                query=dto.query,
                skip=0,
                limit=10000,
                is_active=dto.is_active
            )
            total = len(all_results)
        elif dto.category_id:
            # Category filter
            products = await self.repository.get_by_category(
                category_id=dto.category_id,
                skip=dto.skip,
                limit=dto.limit,
                is_active=dto.is_active
            )
            total = await self.repository.count_by_category(
                category_id=dto.category_id,
                is_active=dto.is_active
            )
        elif dto.supplier_id:
            # Supplier filter
            products = await self.repository.get_products_by_supplier(
                supplier_id=dto.supplier_id,
                skip=dto.skip,
                limit=dto.limit
            )
            filters = {'supplier_id': dto.supplier_id}
            if dto.is_active is not None:
                filters['is_active'] = dto.is_active
            total = await self.repository.count(**filters)
        elif dto.min_price is not None or dto.max_price is not None:
            # Price range filter
            products = await self.repository.get_products_by_price_range(
                min_price=dto.min_price,
                max_price=dto.max_price,
                skip=dto.skip,
                limit=dto.limit
            )
            all_products = await self.repository.get_products_by_price_range(
                min_price=dto.min_price,
                max_price=dto.max_price,
                skip=0,
                limit=10000
            )
            total = len(all_products)
        elif dto.is_featured:
            # Featured products
            products = await self.repository.get_featured_products(
                skip=dto.skip,
                limit=dto.limit
            )
            all_featured = await self.repository.get_featured_products(skip=0, limit=10000)
            total = len(all_featured)
        else:
            # Default: get all with is_active filter
            filters = {}
            if dto.is_active is not None:
                filters['is_active'] = dto.is_active
            products = await self.repository.get_all(
                skip=dto.skip,
                limit=dto.limit,
                **filters
            )
            total = await self.repository.count(**filters)

        return ProductListResponseDTO(
            items=[ProductResponseDTO.model_validate(p) for p in products],
            total=total,
            skip=dto.skip,
            limit=dto.limit
        )

    async def get_product_by_sku(self, sku: str) -> Optional[ProductResponseDTO]:
        """
        Get a product by SKU.

        Args:
            sku: Product SKU

        Returns:
            Product response DTO if found, None otherwise
        """
        product = await self.repository.get_by_sku(sku)
        if not product:
            return None
        return ProductResponseDTO.model_validate(product)

    async def get_product_by_barcode(self, barcode: str) -> Optional[ProductResponseDTO]:
        """
        Get a product by barcode.

        Args:
            barcode: Product barcode

        Returns:
            Product response DTO if found, None otherwise
        """
        product = await self.repository.get_by_barcode(barcode)
        if not product:
            return None
        return ProductResponseDTO.model_validate(product)

    async def get_products_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> ProductListResponseDTO:
        """
        Get products in a category.

        Args:
            category_id: Category ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status

        Returns:
            Product list response DTO
        """
        products = await self.repository.get_by_category(
            category_id=category_id,
            skip=skip,
            limit=limit,
            is_active=is_active
        )
        total = await self.repository.count_by_category(
            category_id=category_id,
            is_active=is_active
        )

        return ProductListResponseDTO(
            items=[ProductResponseDTO.model_validate(p) for p in products],
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_active_products_summary(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductSummaryDTO]:
        """
        Get summary of active products.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of product summary DTOs
        """
        products = await self.repository.get_active_products(skip=skip, limit=limit)
        return [ProductSummaryDTO.model_validate(p) for p in products]

    async def get_low_stock_products(
        self,
        threshold: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductStockStatusDTO]:
        """
        Get products with low stock levels.

        Args:
            threshold: Stock threshold
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of product stock status DTOs
        """
        products = await self.repository.get_low_stock_products(
            threshold=threshold,
            skip=skip,
            limit=limit
        )

        return [
            ProductStockStatusDTO(
                product_id=p.id,
                name=p.name,
                sku=p.sku,
                stock_quantity=p.stock_quantity,
                reorder_level=p.reorder_level,
                status="low_stock",
                needs_reorder=True
            )
            for p in products
        ]

    async def get_out_of_stock_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductStockStatusDTO]:
        """
        Get out of stock products.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of product stock status DTOs
        """
        products = await self.repository.get_out_of_stock_products(
            skip=skip,
            limit=limit
        )

        return [
            ProductStockStatusDTO(
                product_id=p.id,
                name=p.name,
                sku=p.sku,
                stock_quantity=p.stock_quantity,
                reorder_level=p.reorder_level,
                status="out_of_stock",
                needs_reorder=True
            )
            for p in products
        ]

    async def update_stock(self, dto: StockUpdateDTO) -> Optional[ProductResponseDTO]:
        """
        Update product stock quantity.

        Args:
            dto: Stock update DTO

        Returns:
            Updated product response DTO if found, None otherwise

        Raises:
            ValueError: If stock quantity would become negative
        """
        product = await self.repository.get_by_id(dto.product_id)
        if not product:
            return None

        new_quantity = product.stock_quantity + dto.quantity_change
        if new_quantity < 0:
            raise ValueError(
                f"Stock quantity cannot be negative. "
                f"Current: {product.stock_quantity}, Change: {dto.quantity_change}"
            )

        updated_product = await self.repository.update_stock_quantity(
            dto.product_id,
            dto.quantity_change
        )

        return ProductResponseDTO.model_validate(updated_product)

    async def get_product_stock_status(self, product_id: int) -> Optional[ProductStockStatusDTO]:
        """
        Get product stock status.

        Args:
            product_id: Product ID

        Returns:
            Product stock status DTO if found, None otherwise
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            return None

        # Determine stock status
        if product.stock_quantity <= 0:
            status = "out_of_stock"
            needs_reorder = True
        elif product.reorder_level and product.stock_quantity <= product.reorder_level:
            status = "low_stock"
            needs_reorder = True
        else:
            status = "in_stock"
            needs_reorder = False

        return ProductStockStatusDTO(
            product_id=product.id,
            name=product.name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            reorder_level=product.reorder_level,
            status=status,
            needs_reorder=needs_reorder
        )

    async def get_featured_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> ProductListResponseDTO:
        """
        Get featured products (for e-commerce).

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Product list response DTO
        """
        products = await self.repository.get_featured_products(skip=skip, limit=limit)
        all_featured = await self.repository.get_featured_products(skip=0, limit=10000)
        total = len(all_featured)

        return ProductListResponseDTO(
            items=[ProductResponseDTO.model_validate(p) for p in products],
            total=total,
            skip=skip,
            limit=limit
        )
