"""
Product Repository SQLAlchemy Implementation

Concrete implementation of the product repository using SQLAlchemy.
"""

from typing import List, Optional
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.repositories.product_repository import IProductRepository
from app.models import Product


class ProductRepository(IProductRepository):
    """
    SQLAlchemy implementation of the product repository.

    This class provides concrete implementations of all product
    data access operations using SQLAlchemy ORM.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get_by_id(self, id: int) -> Optional[Product]:
        """Get a product by ID."""
        result = await self.db.execute(
            select(Product).where(Product.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Product]:
        """Get all products with optional pagination and filtering."""
        query = select(Product)

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(Product, key):
                    conditions.append(getattr(Product, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: Product) -> Product:
        """Create a new product."""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: int, entity: Product) -> Optional[Product]:
        """Update an existing product."""
        existing = await self.get_by_id(id)
        if not existing:
            return None

        # Update fields
        for key, value in entity.__dict__.items():
            if not key.startswith('_') and key != 'id':
                setattr(existing, key, value)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing

    async def delete(self, id: int) -> bool:
        """Delete a product."""
        product = await self.get_by_id(id)
        if not product:
            return False

        await self.db.delete(product)
        await self.db.commit()
        return True

    async def exists(self, id: int) -> bool:
        """Check if a product exists."""
        result = await self.db.execute(
            select(Product.id).where(Product.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def count(self, **filters) -> int:
        """Count products with optional filtering."""
        query = select(func.count(Product.id))

        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(Product, key):
                    conditions.append(getattr(Product, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def find_one(self, **filters) -> Optional[Product]:
        """Find a single product by filters."""
        query = select(Product)

        conditions = []
        for key, value in filters.items():
            if hasattr(Product, key):
                conditions.append(getattr(Product, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Product]:
        """Find multiple products by filters."""
        return await self.get_all(skip=skip, limit=limit, **filters)

    # Product-specific methods

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU."""
        result = await self.db.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get a product by barcode."""
        result = await self.db.execute(
            select(Product).where(Product.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def get_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """Get products in a specific category."""
        query = select(Product).where(Product.category_id == category_id)

        if is_active is not None:
            query = query.where(Product.is_active == is_active)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """Search products by name, SKU, or barcode."""
        search_pattern = f"%{query}%"

        sql_query = select(Product).where(
            or_(
                Product.name.ilike(search_pattern),
                Product.sku.ilike(search_pattern),
                Product.barcode.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )

        if is_active is not None:
            sql_query = sql_query.where(Product.is_active == is_active)

        sql_query = sql_query.offset(skip).limit(limit)
        result = await self.db.execute(sql_query)
        return list(result.scalars().all())

    async def get_active_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get all active products."""
        query = select(Product).where(Product.is_active == True)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_low_stock_products(
        self,
        threshold: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products with low stock levels."""
        if threshold is not None:
            # Use provided threshold
            query = select(Product).where(
                and_(
                    Product.stock_quantity <= threshold,
                    Product.stock_quantity > 0
                )
            )
        else:
            # Use reorder_level if available
            query = select(Product).where(
                and_(
                    Product.stock_quantity <= Product.reorder_level,
                    Product.stock_quantity > 0
                )
            )

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_out_of_stock_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get out of stock products."""
        query = select(Product).where(Product.stock_quantity <= 0)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_products_by_price_range(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products filtered by price range."""
        query = select(Product)

        conditions = []
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_zoho_item_id(self, zoho_item_id: str) -> Optional[Product]:
        """Get a product by Zoho item ID."""
        result = await self.db.execute(
            select(Product).where(Product.zoho_item_id == zoho_item_id)
        )
        return result.scalar_one_or_none()

    async def count_by_category(
        self,
        category_id: int,
        is_active: Optional[bool] = None
    ) -> int:
        """Count products in a category."""
        query = select(func.count(Product.id)).where(
            Product.category_id == category_id
        )

        if is_active is not None:
            query = query.where(Product.is_active == is_active)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update_stock_quantity(
        self,
        product_id: int,
        quantity_change: int
    ) -> Optional[Product]:
        """Update product stock quantity."""
        product = await self.get_by_id(product_id)
        if not product:
            return None

        product.stock_quantity += quantity_change
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_products_by_supplier(
        self,
        supplier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products from a specific supplier."""
        query = select(Product).where(Product.supplier_id == supplier_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_featured_products(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get featured products (for e-commerce display)."""
        # Assuming there's an is_featured field, otherwise use is_active and sort by popularity
        query = select(Product).where(Product.is_active == True)

        # If there's an is_featured field, filter by it
        if hasattr(Product, 'is_featured'):
            query = query.where(Product.is_featured == True)

        # Order by created_at descending to show newest first
        query = query.order_by(Product.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
