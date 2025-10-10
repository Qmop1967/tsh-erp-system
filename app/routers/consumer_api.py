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
from ..models.inventory import InventoryItem
from ..models.product import Product, Category
from ..services.zoho_service import ZohoAsyncService, ZohoAPIError
from ..utils.image_helper import get_product_image_url

logger = logging.getLogger(__name__)

router = APIRouter()


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

        # Query with eager loading of product and category
        query = db.query(InventoryItem).options(
            joinedload(InventoryItem.product).joinedload(Product.category)
        )

        # Filter by category
        if category and category != 'All':
            query = query.join(InventoryItem.product).join(Product.category).filter(
                Category.name == category
            )

        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.join(InventoryItem.product).filter(
                Product.name.ilike(search_term) |
                Product.barcode.ilike(search_term) |
                Product.sku.ilike(search_term)
            )

        # Get items
        items = query.offset(skip).limit(limit).all()

        # Format response
        products = []
        for item in items:
            product = item.product
            category = product.category if product else None

            # Generate image URL with fallback to placeholder
            image_url = get_product_image_url(
                barcode=product.barcode if product else None,
                sku=product.sku if product else None,
                base_url=base_url
            )

            # Use placeholder if no image
            if not image_url or image_url == '':
                image_url = f"{base_url}/static/placeholder-product.png"

            products.append({
                'id': item.id,
                'item_id': item.id,
                'product_id': item.product_id,
                'product_name': product.name if product else 'Unknown',
                'category_name': category.name if category else 'Unknown',
                'selling_price': float(product.unit_price) if product else 0,
                'quantity': float(item.quantity_on_hand) if item.quantity_on_hand else 0,
                'barcode': product.barcode if product else None,
                'sku': product.sku if product else None,
                'image_path': image_url,
                'in_stock': (item.quantity_on_hand or 0) > 0,
                'has_image': bool(image_url and image_url != f"{base_url}/static/placeholder-product.png")
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
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific product"""
    try:
        base_url = str(request.base_url).rstrip('/')

        item = db.query(InventoryItem).options(
            joinedload(InventoryItem.product).joinedload(Product.category)
        ).filter(InventoryItem.id == product_id).first()

        if not item:
            raise HTTPException(status_code=404, detail="Product not found")

        product = item.product
        category = product.category if product else None

        image_url = get_product_image_url(
            barcode=product.barcode if product else None,
            sku=product.sku if product else None,
            base_url=base_url
        )

        return {
            'status': 'success',
            'product': {
                'id': item.id,
                'product_id': item.product_id,
                'product_name': product.name if product else 'Unknown',
                'category_name': category.name if category else 'Unknown',
                'selling_price': float(product.unit_price) if product else 0,
                'cost_price': float(item.average_cost) if item.average_cost else 0,
                'quantity': float(item.quantity_on_hand) if item.quantity_on_hand else 0,
                'barcode': product.barcode if product else None,
                'sku': product.sku if product else None,
                'image_path': image_url,
                'in_stock': (item.quantity_on_hand or 0) > 0,
                'created_at': item.created_at.isoformat() if item.created_at else None
            }
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
        categories = db.query(Category.name).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]

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
    try:
        logger.info(f"Creating order for customer: {order_data.customer_email}")

        # Initialize Zoho service
        async with ZohoAsyncService() as zoho:
            # Prepare order data for Zoho
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

            # Create sales order in Zoho
            try:
                zoho_response = await zoho.create_salesorder(zoho_order_data)

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


def update_inventory_after_order(line_items: List[OrderLineItem], db: Session):
    """Background task to update inventory quantities after order"""
    try:
        for item in line_items:
            db_item = db.query(InventoryItem).filter(
                InventoryItem.id == int(item.item_id)
            ).first()

            if db_item and db_item.quantity_on_hand:
                db_item.quantity_on_hand -= item.quantity
                logger.info(f"Updated inventory for {item.product_name}: {db_item.quantity_on_hand}")

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
    try:
        async with ZohoAsyncService() as zoho:
            # Fetch items from Zoho
            items = await zoho.get_all_items()

            if not items:
                return {
                    'status': 'error',
                    'message': 'No items fetched from Zoho'
                }

            # Update database
            updated_count = 0
            for zoho_item in items:
                # Find product by SKU/barcode
                product = db.query(Product).filter(
                    (Product.sku == zoho_item.get('sku')) |
                    (Product.barcode == zoho_item.get('sku'))
                ).first()

                if product:
                    # Find inventory item for this product
                    inventory_item = db.query(InventoryItem).filter(
                        InventoryItem.product_id == product.id
                    ).first()

                    if inventory_item:
                        # Update existing inventory
                        inventory_item.quantity_on_hand = zoho_item.get('stock_on_hand', 0)
                        product.unit_price = zoho_item.get('rate', 0)
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


@router.get("/sync/status", summary="Get sync status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Get the current sync status and last sync time"""
    try:
        total_products = db.query(InventoryItem).count()
        in_stock_products = db.query(InventoryItem).filter(
            InventoryItem.quantity_on_hand > 0
        ).count()

        return {
            'status': 'success',
            'total_products': total_products,
            'in_stock_products': in_stock_products,
            'out_of_stock_products': total_products - in_stock_products,
            'last_sync': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
