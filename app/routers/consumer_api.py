"""
Consumer App API Routes - Modern E-commerce Endpoints
توجيهات API لتطبيق المستهلك - نقاط نهاية التجارة الإلكترونية الحديثة

Provides endpoints for the TSH Consumer mobile app with Zoho integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from ..db.database import get_db
# Removed InventoryItem - using products table directly
from ..models.product import Product, Category
# ✅ UPDATED: Using TDS unified Zoho integration
from ..tds.integrations.zoho import (
    UnifiedZohoClient, ZohoAuthManager, ZohoCredentials,
    ZohoAPIError
)
from ..utils.image_helper import get_product_image_url
from sqlalchemy import text
import os

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_zoho_client() -> UnifiedZohoClient:
    """
    Initialize and return TDS unified Zoho client

    Returns:
        UnifiedZohoClient instance
    """
    # Load credentials from environment
    credentials = ZohoCredentials(
        client_id=os.getenv('ZOHO_CLIENT_ID'),
        client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
        refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
        organization_id=os.getenv('ZOHO_ORGANIZATION_ID')
    )

    # Create auth manager
    auth_manager = ZohoAuthManager(credentials, auto_refresh=True)
    await auth_manager.start()

    # Create and return Zoho client
    client = UnifiedZohoClient(
        auth_manager=auth_manager,
        organization_id=credentials.organization_id,
        rate_limit=100
    )
    await client.start_session()

    return client


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class OrderLineItem(BaseModel):
    item_id: str
    product_name: str
    quantity: int
    rate: float
    amount: float


class CreateOrderRequest(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    line_items: List[OrderLineItem]
    total_amount: float
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    success: bool
    order_id: Optional[str] = None
    salesorder_number: Optional[str] = None
    message: str
    zoho_response: Optional[Dict[str, Any]] = None


# ============================================
# INVENTORY ENDPOINTS
# ============================================

@router.get("/products", summary="Get all products with Zoho sync")
async def get_products(
    request: Request,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get products from database (synced from Zoho)
    جلب المنتجات من قاعدة البيانات (متزامنة من Zoho)
    """
    try:
        base_url = str(request.base_url).rstrip('/')

        # Query products directly with Consumer pricelist
        query_params = {"limit": limit, "skip": skip}

        # Build WHERE clause based on filters
        where_conditions = ["p.is_active = true", "p.actual_available_stock > 0"]

        if category and category != 'All':
            where_conditions.append("p.category = :category")
            query_params["category"] = category

        if search:
            where_conditions.append("(p.name ILIKE :search OR p.sku ILIKE :search)")
            query_params["search"] = f"%{search}%"

        where_clause = " AND ".join(where_conditions)

        # Use subquery to get ONLY Consumer pricelist price
        query = text(f"""
            SELECT DISTINCT ON (p.id)
                p.id,
                p.zoho_item_id,
                p.sku,
                p.name,
                p.description,
                COALESCE(p.cdn_image_url, p.image_url) as image_url,
                p.category,
                p.actual_available_stock,
                p.is_active,
                COALESCE(consumer_price.price, p.price, 0) as price,
                COALESCE(consumer_price.currency, 'IQD') as currency
            FROM products p
            LEFT JOIN LATERAL (
                SELECT pp.price, pp.currency
                FROM product_prices pp
                JOIN pricelists pl ON pp.pricelist_id = pl.id
                WHERE pp.product_id = p.id
                  AND pl.name = 'Consumer'
                  AND pp.currency = 'IQD'
                LIMIT 1
            ) consumer_price ON true
            WHERE {where_clause}
            ORDER BY p.id, p.name
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(query, query_params)
        products = []

        for row in result:
            # Use local product images (already downloaded from Zoho)
            image_url = f"{base_url}/static/placeholder-product.png"  # default fallback

            if row.zoho_item_id:
                # Use local product images stored on server
                image_url = f"{base_url}/product-images/{row.zoho_item_id}.jpg"
            elif row.image_url and 'zohoapis.com' not in row.image_url:
                # Use CDN or other non-Zoho image URL as-is
                image_url = row.image_url

            # STANDARDIZED RESPONSE FORMAT - matches Flutter Product model
            products.append({
                # Primary fields (Flutter model expects these)
                'id': str(row.id),
                'zoho_item_id': str(row.zoho_item_id),
                'sku': row.sku,
                'name': row.name,
                'description': row.description,
                'image_url': image_url,
                'cdn_image_url': row.image_url if row.image_url else None,
                'category': row.category or 'Uncategorized',
                'stock_quantity': int(row.actual_available_stock) if row.actual_available_stock else 0,
                'actual_available_stock': int(row.actual_available_stock) if row.actual_available_stock else 0,
                'warehouse_id': None,
                'is_active': True,
                'price': float(row.price) if row.price else 0,
                'currency': 'IQD',

                # Legacy fields for backward compatibility (can be removed later)
                'item_id': str(row.zoho_item_id),
                'product_id': str(row.id),
                'product_name': row.name,
                'category_name': row.category or 'Uncategorized',
                'selling_price': float(row.price) if row.price else 0,
                'quantity': float(row.actual_available_stock) if row.actual_available_stock else 0,
                'barcode': row.sku,
                'image_path': image_url,
                'in_stock': (row.actual_available_stock or 0) > 0,
                'has_image': bool(row.image_url)
            })

        return {
            'status': 'success',
            'count': len(products),
            'items': products
        }

    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", summary="Get product details")
async def get_product_details(
    product_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific product"""
    try:
        base_url = str(request.base_url).rstrip('/')

        # Query product directly with Consumer price
        query = text("""
            SELECT
                p.id,
                p.zoho_item_id,
                p.sku,
                p.name,
                p.description,
                COALESCE(p.cdn_image_url, p.image_url) as image_url,
                p.category,
                p.actual_available_stock,
                p.is_active,
                COALESCE(consumer_price.price, p.price, 0) as price,
                COALESCE(consumer_price.currency, 'IQD') as currency,
                p.created_at
            FROM products p
            LEFT JOIN LATERAL (
                SELECT pp.price, pp.currency
                FROM product_prices pp
                JOIN pricelists pl ON pp.pricelist_id = pl.id
                WHERE pp.product_id = p.id
                  AND pl.name = 'Consumer'
                  AND pp.currency = 'IQD'
                LIMIT 1
            ) consumer_price ON true
            WHERE p.id = :product_id::uuid
        """)

        result = db.execute(query, {"product_id": product_id}).first()

        if not result:
            raise HTTPException(status_code=404, detail="Product not found")

        # Use local product images (already downloaded from Zoho)
        image_url = f"{base_url}/static/placeholder-product.png"  # default fallback

        if result.zoho_item_id:
            # Use local product images stored on server
            image_url = f"{base_url}/product-images/{result.zoho_item_id}.jpg"
        elif result.image_url and 'zohoapis.com' not in result.image_url:
            # Use CDN or other non-Zoho image URL as-is
            image_url = result.image_url

        # STANDARDIZED RESPONSE FORMAT - matches Flutter Product model
        product_data = {
            # Primary fields (Flutter model expects these)
            'id': str(result.id),
            'zoho_item_id': str(result.zoho_item_id),
            'sku': result.sku,
            'name': result.name,
            'description': result.description,
            'image_url': image_url,
            'cdn_image_url': result.image_url if result.image_url else None,
            'category': result.category or 'Uncategorized',
            'stock_quantity': int(result.actual_available_stock) if result.actual_available_stock else 0,
            'actual_available_stock': int(result.actual_available_stock) if result.actual_available_stock else 0,
            'warehouse_id': None,
            'is_active': result.is_active,
            'price': float(result.price) if result.price else 0,
            'currency': 'IQD',
            'created_at': result.created_at.isoformat() if result.created_at else None,

            # Legacy fields for backward compatibility
            'product_id': str(result.id),
            'product_name': result.name,
            'category_name': result.category or 'Uncategorized',
            'selling_price': float(result.price) if result.price else 0,
            'cost_price': 0,
            'quantity': float(result.actual_available_stock) if result.actual_available_stock else 0,
            'barcode': result.sku,
            'image_path': image_url,
            'in_stock': (result.actual_available_stock or 0) > 0
        }

        return {
            'status': 'success',
            'product': product_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", summary="Get all product categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of all product categories"""
    try:
        # Get distinct categories from products table
        query = text("""
            SELECT DISTINCT category
            FROM products
            WHERE category IS NOT NULL AND category != ''
            ORDER BY category
        """)
        result = db.execute(query)
        category_list = [row.category for row in result]

        return {
            'status': 'success',
            'categories': category_list
        }

    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ORDER ENDPOINTS WITH ZOHO INTEGRATION
# ============================================

@router.post("/orders", response_model=OrderResponse, summary="Create order in Zoho")
async def create_order(
    order_data: CreateOrderRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a sales order in Zoho Books and update inventory
    إنشاء طلب مبيعات في Zoho Books وتحديث المخزون
    """
    zoho_client = None
    try:
        logger.info(f"Creating order for customer: {order_data.customer_email}")

        # Initialize TDS Zoho client
        zoho_client = await get_zoho_client()

        # Prepare order data for Zoho Books API
        zoho_order_data = {
            "customer_name": order_data.customer_name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "line_items": [
                {
                    "item_id": item.item_id,
                    "name": item.product_name,
                    "quantity": item.quantity,
                    "rate": item.rate,
                    "amount": item.amount
                }
                for item in order_data.line_items
            ],
            "notes": order_data.notes or f"Order from TSH Consumer App - {order_data.customer_email}",
            "custom_fields": [
                {"label": "Customer Email", "value": order_data.customer_email},
                {"label": "Customer Phone", "value": order_data.customer_phone}
            ]
        }

        # Create sales order in Zoho Books via TDS client
        try:
            from ..tds.integrations.zoho.client import ZohoAPI

            zoho_response = await zoho_client.post(
                endpoint="/salesorders",
                data=zoho_order_data,
                api_type=ZohoAPI.BOOKS
            )

            if zoho_response and 'salesorder' in zoho_response:
                salesorder = zoho_response['salesorder']

                # Update local inventory quantities
                background_tasks.add_task(
                    update_inventory_after_order,
                    order_data.line_items,
                    db
                )

                return OrderResponse(
                    success=True,
                    order_id=salesorder.get('salesorder_id'),
                    salesorder_number=salesorder.get('salesorder_number'),
                    message="Order created successfully in Zoho",
                    zoho_response=zoho_response
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create order in Zoho"
                )

        except ZohoAPIError as e:
            logger.error(f"Zoho API Error: {e.message}")
            raise HTTPException(
                status_code=500,
                detail=f"Zoho API Error: {e.message}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()


def update_inventory_after_order(line_items: List[OrderLineItem], db: Session):
    """Background task to update inventory quantities after order"""
    try:
        for item in line_items:
            # Update product stock directly
            update_query = text("""
                UPDATE products
                SET actual_available_stock = actual_available_stock - :quantity,
                    stock_quantity = stock_quantity - :quantity,
                    updated_at = NOW()
                WHERE zoho_item_id = :item_id
                  AND actual_available_stock >= :quantity
            """)
            result = db.execute(update_query, {
                "quantity": item.quantity,
                "item_id": item.item_id
            })

            if result.rowcount > 0:
                logger.info(f"Updated inventory for {item.product_name}: reduced by {item.quantity}")
            else:
                logger.warning(f"Could not update inventory for {item.product_name}: insufficient stock or not found")

        db.commit()

    except Exception as e:
        logger.error(f"Error updating inventory: {e}")
        db.rollback()


# ============================================
# ZOHO SYNC ENDPOINTS
# ============================================

@router.post("/sync/inventory", summary="Sync inventory from Zoho")
async def sync_inventory_from_zoho(db: Session = Depends(get_db)):
    """
    Manually trigger inventory sync from Zoho
    تشغيل مزامنة المخزون من Zoho يدوياً
    """
    zoho_client = None
    try:
        # Initialize TDS Zoho client
        zoho_client = await get_zoho_client()

        # Fetch items from Zoho Books/Inventory API
        from ..tds.integrations.zoho.client import ZohoAPI

        items_response = await zoho_client.paginated_fetch(
            endpoint="/items",
            api_type=ZohoAPI.BOOKS,
            params={"filter_by": "Status.Active"}
        )

        items = items_response.get('items', [])

        if not items:
            return {
                'status': 'error',
                'message': 'No items fetched from Zoho'
            }

        # Update database
        updated_count = 0
        for zoho_item in items:
            # Update products directly by zoho_item_id
            update_query = text("""
                UPDATE products
                SET actual_available_stock = :stock,
                    stock_quantity = :stock,
                    price = :price,
                    last_zoho_sync = NOW(),
                    updated_at = NOW()
                WHERE zoho_item_id = :item_id
            """)
            result = db.execute(update_query, {
                "stock": zoho_item.get('stock_on_hand', 0),
                "price": zoho_item.get('rate', 0),
                "item_id": zoho_item.get('item_id')
            })

            if result.rowcount > 0:
                updated_count += 1

        db.commit()

        return {
            'status': 'success',
            'message': f'Synced {updated_count} items from Zoho',
            'total_items': len(items),
            'updated_items': updated_count
        }

    except Exception as e:
        logger.error(f"Error syncing inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()


@router.get("/sync/status", summary="Get sync status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Get the current sync status and last sync time"""
    try:
        # Get product counts from products table
        count_query = text("""
            SELECT
                COUNT(*) as total_products,
                SUM(CASE WHEN actual_available_stock > 0 THEN 1 ELSE 0 END) as in_stock_products,
                SUM(CASE WHEN actual_available_stock = 0 THEN 1 ELSE 0 END) as out_of_stock_products,
                MAX(last_zoho_sync) as last_sync
            FROM products
            WHERE is_active = true
        """)
        result = db.execute(count_query).first()

        return {
            'status': 'success',
            'total_products': int(result.total_products) if result.total_products else 0,
            'in_stock_products': int(result.in_stock_products) if result.in_stock_products else 0,
            'out_of_stock_products': int(result.out_of_stock_products) if result.out_of_stock_products else 0,
            'last_sync': result.last_sync.isoformat() if result.last_sync else None
        }

    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
