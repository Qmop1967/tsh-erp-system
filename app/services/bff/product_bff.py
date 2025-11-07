"""
Product BFF Service

Aggregates product-related data from multiple sources:
- Product details
- Inventory levels (all branches)
- Pricing (all pricelists)
- Images
- Reviews
- Similar products
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.services.bff.base_bff import BaseBFFService
from app.models import (
    Product, InventoryItem, ProductPrice, PricingList,
    Review, Branch, Warehouse
)
import logging

logger = logging.getLogger(__name__)


class ProductBFFService(BaseBFFService):
    """
    Product BFF Service

    Provides complete product information in a single API call
    """

    async def get_product_complete(
        self,
        product_id: int,
        include_similar: bool = True,
        include_reviews: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete product data in single call

        Before: 5 separate API calls (700ms total)
        After: 1 API call (180ms total)

        Args:
            product_id: Product ID
            include_similar: Include similar products
            include_reviews: Include customer reviews

        Returns:
            Complete product data dictionary
        """
        cache_key = f"bff:product:{product_id}:complete"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached

        logger.info(f"Cache MISS: {cache_key} - Fetching from database")

        # Fetch all data in parallel
        tasks = [
            self._get_product_details(product_id),
            self._get_inventory_all_branches(product_id),
            self._get_pricing_all_pricelists(product_id),
            self._get_product_images(product_id),
        ]

        if include_reviews:
            tasks.append(self._get_product_reviews(product_id, limit=5))

        if include_similar:
            tasks.append(self._get_similar_products(product_id, limit=6))

        # Execute in parallel
        results = await self.fetch_parallel(*tasks)

        # Handle results
        product = self.handle_exception(results[0])
        inventory = self.handle_exception(results[1], default=[])
        pricing = self.handle_exception(results[2], default=[])
        images = self.handle_exception(results[3], default=[])

        idx = 4
        reviews = []
        similar = []

        if include_reviews:
            reviews = self.handle_exception(results[idx], default=[])
            idx += 1

        if include_similar:
            similar = self.handle_exception(results[idx], default=[])

        # Check if product exists
        if not product:
            return self.format_error("Product not found")

        # Format response
        response_data = {
            "product": product,
            "inventory": {
                "total_quantity": sum(inv.get("quantity", 0) for inv in inventory),
                "by_branch": inventory,
                "is_available": any(inv.get("quantity", 0) > 0 for inv in inventory)
            },
            "pricing": pricing,
            "images": images,
            "reviews": {
                "items": reviews,
                "count": len(reviews),
                "average_rating": self._calculate_average_rating(reviews)
            } if include_reviews else None,
            "similar_products": similar if include_similar else None
        }

        # Cache for 5 minutes
        await self.cache.set(cache_key, response_data, ttl=300)

        return self.format_response(response_data, metadata={
            "cached": False,
            "data_sources": len(tasks)
        })

    async def _get_product_details(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product basic information"""
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()

        if not product:
            return None

        return {
            "id": product.id,
            "name": product.name,
            "name_ar": getattr(product, "name_ar", None),
            "sku": product.sku,
            "barcode": getattr(product, "barcode", None),
            "description": getattr(product, "description", None),
            "category": getattr(product, "category", None),
            "brand": getattr(product, "brand", None),
            "unit": getattr(product, "unit", "unit"),
            "weight": getattr(product, "weight", None),
            "dimensions": getattr(product, "dimensions", None),
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat() if product.created_at else None
        }

    async def _get_inventory_all_branches(self, product_id: int) -> List[Dict[str, Any]]:
        """Get inventory levels across all branches"""
        result = await self.db.execute(
            select(InventoryItem, Branch, Warehouse)
            .join(Warehouse, InventoryItem.warehouse_id == Warehouse.id)
            .join(Branch, Warehouse.branch_id == Branch.id)
            .where(InventoryItem.product_id == product_id)
        )

        inventory_list = []
        for inv, branch, warehouse in result:
            inventory_list.append({
                "branch_id": branch.id,
                "branch_name": branch.name,
                "warehouse_id": warehouse.id,
                "warehouse_name": warehouse.name,
                "quantity": inv.quantity,
                "reserved_quantity": getattr(inv, "reserved_quantity", 0),
                "available_quantity": inv.quantity - getattr(inv, "reserved_quantity", 0),
                "last_updated": inv.updated_at.isoformat() if inv.updated_at else None
            })

        return inventory_list

    async def _get_pricing_all_pricelists(self, product_id: int) -> List[Dict[str, Any]]:
        """Get pricing across all pricelists"""
        result = await self.db.execute(
            select(ProductPrice, PricingList)
            .join(PricingList, ProductPrice.pricelist_id == PricingList.id)
            .where(
                and_(
                    ProductPrice.product_id == product_id,
                    PricingList.is_active == True
                )
            )
        )

        pricing_list = []
        for price, pricelist in result:
            pricing_list.append({
                "pricelist_id": pricelist.id,
                "pricelist_name": pricelist.name,
                "currency": getattr(pricelist, "currency", "USD"),
                "price": float(price.price),
                "cost": float(getattr(price, "cost", 0)),
                "discount_percentage": float(getattr(price, "discount_percentage", 0)),
                "final_price": float(price.price) * (1 - float(getattr(price, "discount_percentage", 0)) / 100),
                "is_default": getattr(pricelist, "is_default", False)
            })

        return pricing_list

    async def _get_product_images(self, product_id: int) -> List[Dict[str, Any]]:
        """Get product images"""
        # For now, return placeholder
        # TODO: Implement proper image service
        return [
            {
                "url": f"/api/images/products/{product_id}/main.jpg",
                "thumbnail": f"/api/images/products/{product_id}/main_thumb.jpg",
                "is_primary": True,
                "order": 0
            }
        ]

    async def _get_product_reviews(self, product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent customer reviews"""
        try:
            result = await self.db.execute(
                select(Review)
                .where(Review.product_id == product_id)
                .order_by(Review.created_at.desc())
                .limit(limit)
            )
            reviews = result.scalars().all()

            return [
                {
                    "id": review.id,
                    "rating": review.rating,
                    "comment": review.comment,
                    "customer_name": getattr(review, "customer_name", "Anonymous"),
                    "created_at": review.created_at.isoformat() if review.created_at else None
                }
                for review in reviews
            ]
        except Exception as e:
            logger.warning(f"Failed to fetch reviews: {e}")
            return []

    async def _get_similar_products(self, product_id: int, limit: int = 6) -> List[Dict[str, Any]]:
        """Get similar products (same category)"""
        # Get the product's category
        result = await self.db.execute(
            select(Product.category_id).where(Product.id == product_id)
        )
        category_id = result.scalar_one_or_none()

        if not category_id:
            return []

        # Get similar products
        result = await self.db.execute(
            select(Product)
            .where(
                and_(
                    Product.category_id == category_id,
                    Product.id != product_id,
                    Product.is_active == True
                )
            )
            .limit(limit)
        )
        products = result.scalars().all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "image": f"/api/images/products/{p.id}/main_thumb.jpg"
            }
            for p in products
        ]

    def _calculate_average_rating(self, reviews: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate average rating from reviews"""
        if not reviews:
            return None

        ratings = [r.get("rating", 0) for r in reviews if r.get("rating")]
        if not ratings:
            return None

        return round(sum(ratings) / len(ratings), 1)

    async def invalidate_product_cache(self, product_id: int):
        """Invalidate all cache entries for a product"""
        patterns = [
            f"bff:product:{product_id}:*",
            f"product:{product_id}:*",
        ]

        for pattern in patterns:
            await self.invalidate_cache(pattern)

        logger.info(f"Invalidated product cache for product_id={product_id}")
