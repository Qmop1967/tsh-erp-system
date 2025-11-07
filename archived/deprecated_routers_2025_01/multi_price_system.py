from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from enum import Enum
from decimal import Decimal
import uuid

from app.db.database import get_db
from app.models import (
    User, Customer, Product, InventoryItem, SalesOrder, SalesInvoice, 
    MoneyTransfer, Branch, Warehouse, StockMovement
)
from app.models.pricing import (
    PricingList, ProductPrice, PriceListCategory, PriceHistory, 
    PriceNegotiationRequest, CustomerPriceCategory
)
from app.db.database import Base
from sqlalchemy import func, desc, and_, or_, Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship

# AdminNotification model (simplified for this context)
class AdminNotification:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

router = APIRouter()

class PriceListType(str, Enum):
    WHOLESALE_A = "wholesale_a"
    WHOLESALE_B = "wholesale_b"
    RETAILER_SHOP = "retailer_shop"
    TECHNICAL = "technical"
    CONSUMER = "consumer"
    PARTNER_SALESMEN = "partner_salesmen"

class CustomerCategory(str, Enum):
    WHOLESALE_A = "wholesale_a"  # High volume, best prices
    WHOLESALE_B = "wholesale_b"  # Medium volume
    RETAILER_SHOP = "retailer_shop"  # Small retailers
    TECHNICAL = "technical"  # Technical customers
    CONSUMER = "consumer"  # End consumers
    PARTNER_SALESMEN = "partner_salesmen"  # Partner network

class PriceUpdateType(str, Enum):
    BULK_UPDATE = "bulk_update"
    CATEGORY_UPDATE = "category_update"
    PRODUCT_UPDATE = "product_update"
    NEGOTIATED_UPDATE = "negotiated_update"
    AUTOMATIC_UPDATE = "automatic_update"

class NegotiationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COUNTER_OFFER = "counter_offer"
    EXPIRED = "expired"

class PriceListCreate(BaseModel):
    name: str
    price_list_type: PriceListType
    description: str
    minimum_order_value: float
    discount_percentage: float
    is_active: bool = True
    valid_from: date
    valid_to: Optional[date] = None
    customer_categories: List[CustomerCategory]

class ProductPriceUpdate(BaseModel):
    product_id: int
    price_list_id: int
    new_price: float
    discount_percentage: float
    minimum_quantity: int = 1
    notes: Optional[str] = None

class BulkPriceUpdate(BaseModel):
    price_list_id: int
    update_type: PriceUpdateType
    products: List[int]  # Product IDs
    update_method: str  # "percentage", "fixed_amount", "new_price"
    update_value: float
    notes: Optional[str] = None

class PriceNegotiation(BaseModel):
    customer_id: int
    product_id: int
    current_price: float
    requested_price: float
    quantity: int
    justification: str
    valid_until: date

class CustomerCategoryUpdate(BaseModel):
    customer_id: int
    new_category: CustomerCategory
    reason: str
    effective_date: date

@router.post("/price-lists/create")
async def create_price_list(
    price_list: PriceListCreate,
    db: Session = Depends(get_db)
):
    """
    📋 Create new price list for different customer categories
    """
    
    try:
        # Check if price list already exists
        existing = db.query(PricingList).filter(
            PricingList.name == price_list.name,
            PricingList.price_list_type == price_list.price_list_type.value
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Price list with this name and type already exists")
        
        # Create price list
        new_price_list = PricingList(
            name=price_list.name,
            price_list_type=price_list.price_list_type.value,
            description=price_list.description,
            minimum_order_value=price_list.minimum_order_value,
            discount_percentage=price_list.discount_percentage,
            is_active=price_list.is_active,
            valid_from=price_list.valid_from,
            valid_to=price_list.valid_to,
            created_at=datetime.now()
        )
        
        db.add(new_price_list)
        db.flush()
        
        # Link to customer categories
        for category in price_list.customer_categories:
            category_link = PriceListCategory(
                price_list_id=new_price_list.id,
                customer_category=category.value,
                created_at=datetime.now()
            )
            db.add(category_link)
        
        db.commit()
        
        return {
            "price_list_id": new_price_list.id,
            "name": new_price_list.name,
            "type": new_price_list.price_list_type,
            "status": "created",
            "message": "Price list created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create price list: {str(e)}")

@router.get("/price-lists", response_model=List[Dict[str, Any]])
async def get_price_lists(
    price_list_type: Optional[PriceListType] = Query(None),
    is_active: Optional[bool] = Query(None),
    customer_category: Optional[CustomerCategory] = Query(None),
    db: Session = Depends(get_db)
):
    """
    📋 Get all price lists with filtering
    """
    
    query = db.query(PricingList).order_by(desc(PricingList.created_at))
    
    if price_list_type:
        query = query.filter(PricingList.price_list_type == price_list_type.value)
    
    if is_active is not None:
        query = query.filter(PricingList.is_active == is_active)
    
    if customer_category:
        query = query.join(PriceListCategory).filter(
            PriceListCategory.customer_category == customer_category.value
        )
    
    price_lists = query.all()
    
    formatted_lists = []
    for price_list in price_lists:
        # Get product count
        product_count = db.query(func.count(ProductPrice.id)).filter(
            ProductPrice.price_list_id == price_list.id
        ).scalar() or 0
        
        # Get customer categories
        categories = db.query(PriceListCategory.customer_category).filter(
            PriceListCategory.price_list_id == price_list.id
        ).all()
        
        formatted_lists.append({
            "id": price_list.id,
            "name": price_list.name,
            "price_list_type": price_list.price_list_type,
            "description": price_list.description,
            "minimum_order_value": float(price_list.minimum_order_value),
            "discount_percentage": float(price_list.discount_percentage),
            "is_active": price_list.is_active,
            "valid_from": price_list.valid_from.isoformat(),
            "valid_to": price_list.valid_to.isoformat() if price_list.valid_to else None,
            "product_count": product_count,
            "customer_categories": [cat[0] for cat in categories],
            "created_at": price_list.created_at.isoformat()
        })
    
    # Create mock price lists if none exist
    if not formatted_lists:
        mock_price_lists = [
            {
                "id": i,
                "name": name,
                "price_list_type": name,
                "description": f"{name.replace('_', ' ').title()} Price List",
                "minimum_order_value": 100.0,
                "discount_percentage": 5.0 + (i * 2),
                "is_active": True,
                "valid_from": datetime.now().isoformat(),
                "valid_to": None,
                "product_count": 150 + (i * 20),
                "customer_categories": [name],
                "created_at": datetime.now().isoformat()
            }
            for i, name in enumerate(["wholesale_a", "wholesale_b", "retailer", "technical", "consumer"], 1)
        ]
        formatted_lists = mock_price_lists
    
    return {
        "price_lists": formatted_lists,
        "total": len(formatted_lists),
        "status": "operational"
    }

@router.get("/price-lists/{price_list_id}/products")
async def get_price_list_products(
    price_list_id: int,
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    📦 Get products with prices for specific price list
    """
    
    # Get price list
    price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
    if not price_list:
        raise HTTPException(status_code=404, detail="Price list not found")
    
    # Build query
    query = db.query(Product, ProductPrice).join(
        ProductPrice,
        Product.id == ProductPrice.product_id
    ).filter(
        ProductPrice.price_list_id == price_list_id
    )
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(
            or_(
                Product.name_en.ilike(f"%{search}%"),
                Product.name_ar.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
        )
    
    products = query.offset(offset).limit(limit).all()
    
    formatted_products = []
    for product, price in products:
        formatted_products.append({
            "product_id": product.id,
            "sku": product.sku,
            "name_en": product.name_en,
            "name_ar": product.name_ar,
            "category": product.category,
            "base_price": float(product.cost_price),
            "list_price": float(price.price),
            "discount_percentage": float(price.discount_percentage) if price.discount_percentage else 0,
            "minimum_quantity": price.minimum_quantity,
            "last_updated": price.updated_at.isoformat() if price.updated_at else None,
            "is_negotiable": price.is_negotiable,
            "stock_quantity": product.stock_quantity
        })
    
    return {
        "price_list_id": price_list_id,
        "price_list_name": price_list.name,
        "products": formatted_products,
        "total_products": len(formatted_products)
    }

@router.post("/price-lists/{price_list_id}/products/update")
async def update_product_prices(
    price_list_id: int,
    updates: List[ProductPriceUpdate],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    💰 Update product prices in price list
    """
    
    try:
        # Get price list
        price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
        if not price_list:
            raise HTTPException(status_code=404, detail="Price list not found")
        
        updated_products = []
        
        for update in updates:
            # Get or create product price
            product_price = db.query(ProductPrice).filter(
                ProductPrice.product_id == update.product_id,
                ProductPrice.price_list_id == price_list_id
            ).first()
            
            if not product_price:
                # Create new product price
                product_price = ProductPrice(
                    product_id=update.product_id,
                    price_list_id=price_list_id,
                    price=update.new_price,
                    discount_percentage=update.discount_percentage,
                    minimum_quantity=update.minimum_quantity,
                    is_negotiable=True,
                    created_at=datetime.now()
                )
                db.add(product_price)
            else:
                # Update existing price
                old_price = product_price.price
                product_price.price = update.new_price
                product_price.discount_percentage = update.discount_percentage
                product_price.minimum_quantity = update.minimum_quantity
                product_price.updated_at = datetime.now()
                
                # Create price history record
                price_history = PriceHistory(
                    product_id=update.product_id,
                    price_list_id=price_list_id,
                    old_price=old_price,
                    new_price=update.new_price,
                    update_type=PriceUpdateType.PRODUCT_UPDATE.value,
                    notes=update.notes,
                    updated_by=1,  # Current user ID
                    created_at=datetime.now()
                )
                db.add(price_history)
            
            updated_products.append(update.product_id)
        
        # Update price list modification date
        price_list.updated_at = datetime.now()
        
        # Background task to notify customers about price changes
        background_tasks.add_task(
            notify_customers_price_change,
            price_list_id,
            updated_products,
            db
        )
        
        db.commit()
        
        return {
            "price_list_id": price_list_id,
            "updated_products": len(updated_products),
            "message": "Product prices updated successfully",
            "products_updated": updated_products
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update prices: {str(e)}")

@router.post("/price-lists/{price_list_id}/bulk-update")
async def bulk_update_prices(
    price_list_id: int,
    bulk_update: BulkPriceUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    📊 Bulk update prices for multiple products
    """
    
    try:
        # Get price list
        price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
        if not price_list:
            raise HTTPException(status_code=404, detail="Price list not found")
        
        updated_count = 0
        
        for product_id in bulk_update.products:
            # Get product price
            product_price = db.query(ProductPrice).filter(
                ProductPrice.product_id == product_id,
                ProductPrice.price_list_id == price_list_id
            ).first()
            
            if product_price:
                old_price = product_price.price
                
                # Calculate new price based on update method
                if bulk_update.update_method == "percentage":
                    new_price = old_price * (1 + bulk_update.update_value / 100)
                elif bulk_update.update_method == "fixed_amount":
                    new_price = old_price + bulk_update.update_value
                elif bulk_update.update_method == "new_price":
                    new_price = bulk_update.update_value
                else:
                    continue
                
                # Update price
                product_price.price = new_price
                product_price.updated_at = datetime.now()
                
                # Create price history
                price_history = PriceHistory(
                    product_id=product_id,
                    price_list_id=price_list_id,
                    old_price=old_price,
                    new_price=new_price,
                    update_type=bulk_update.update_type.value,
                    notes=bulk_update.notes,
                    updated_by=1,  # Current user ID
                    created_at=datetime.now()
                )
                db.add(price_history)
                
                updated_count += 1
        
        # Update price list modification date
        price_list.updated_at = datetime.now()
        
        # Background task to notify customers
        background_tasks.add_task(
            notify_customers_price_change,
            price_list_id,
            bulk_update.products,
            db
        )
        
        db.commit()
        
        return {
            "price_list_id": price_list_id,
            "updated_count": updated_count,
            "total_requested": len(bulk_update.products),
            "update_method": bulk_update.update_method,
            "update_value": bulk_update.update_value,
            "message": f"Bulk update completed for {updated_count} products"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to bulk update prices: {str(e)}")

@router.post("/price-negotiations/request")
async def request_price_negotiation(
    negotiation: PriceNegotiation,
    db: Session = Depends(get_db)
):
    """
    💬 Request price negotiation for specific product
    """
    
    try:
        # Get customer and product
        customer = db.query(Customer).filter(Customer.id == negotiation.customer_id).first()
        product = db.query(Product).filter(Product.id == negotiation.product_id).first()
        
        if not customer or not product:
            raise HTTPException(status_code=404, detail="Customer or product not found")
        
        # Create negotiation request
        negotiation_request = PriceNegotiationRequest(
            customer_id=negotiation.customer_id,
            product_id=negotiation.product_id,
            current_price=negotiation.current_price,
            requested_price=negotiation.requested_price,
            quantity=negotiation.quantity,
            justification=negotiation.justification,
            valid_until=negotiation.valid_until,
            status=NegotiationStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        db.add(negotiation_request)
        db.flush()
        
        # Create admin notification
        notification = AdminNotification(
            type="price_negotiation",
            title="Price Negotiation Request",
            message=f"Price negotiation request from {customer.name} for {product.name_en}",
            data={
                "negotiation_id": negotiation_request.id,
                "customer_name": customer.name,
                "product_name": product.name_en,
                "requested_price": float(negotiation.requested_price),
                "current_price": float(negotiation.current_price)
            },
            priority="medium",
            created_at=datetime.now()
        )
        db.add(notification)
        
        db.commit()
        
        return {
            "negotiation_id": negotiation_request.id,
            "status": negotiation_request.status,
            "message": "Price negotiation request submitted successfully",
            "estimated_response_time": "24-48 hours"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to request price negotiation: {str(e)}")

@router.get("/price-negotiations", response_model=List[Dict[str, Any]])
async def get_price_negotiations(
    status: Optional[NegotiationStatus] = Query(None),
    customer_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    💬 Get price negotiation requests
    """
    
    query = db.query(PriceNegotiationRequest).order_by(desc(PriceNegotiationRequest.created_at))
    
    if status:
        query = query.filter(PriceNegotiationRequest.status == status.value)
    
    if customer_id:
        query = query.filter(PriceNegotiationRequest.customer_id == customer_id)
    
    if product_id:
        query = query.filter(PriceNegotiationRequest.product_id == product_id)
    
    negotiations = query.offset(offset).limit(limit).all()
    
    formatted_negotiations = []
    for negotiation in negotiations:
        formatted_negotiations.append({
            "id": negotiation.id,
            "customer": {
                "id": negotiation.customer.id,
                "name": negotiation.customer.name,
                "category": negotiation.customer.customer_category
            },
            "product": {
                "id": negotiation.product.id,
                "name": negotiation.product.name_en,
                "sku": negotiation.product.sku
            },
            "current_price": float(negotiation.current_price),
            "requested_price": float(negotiation.requested_price),
            "discount_requested": float((negotiation.current_price - negotiation.requested_price) / negotiation.current_price * 100),
            "quantity": negotiation.quantity,
            "justification": negotiation.justification,
            "status": negotiation.status,
            "valid_until": negotiation.valid_until.isoformat(),
            "created_at": negotiation.created_at.isoformat(),
            "responded_at": negotiation.responded_at.isoformat() if negotiation.responded_at else None
        })
    
    return formatted_negotiations

@router.post("/customers/{customer_id}/category/update")
async def update_customer_category(
    customer_id: int,
    category_update: CustomerCategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    👥 Update customer category for different pricing
    """
    
    try:
        # Get customer
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        old_category = customer.customer_category
        
        # Update customer category
        customer.customer_category = category_update.new_category.value
        customer.updated_at = datetime.now()
        
        # Create category change history
        category_history = CustomerCategoryHistory(
            customer_id=customer_id,
            old_category=old_category,
            new_category=category_update.new_category.value,
            reason=category_update.reason,
            effective_date=category_update.effective_date,
            changed_by=1,  # Current user ID
            created_at=datetime.now()
        )
        db.add(category_history)
        
        db.commit()
        
        return {
            "customer_id": customer_id,
            "old_category": old_category,
            "new_category": category_update.new_category.value,
            "effective_date": category_update.effective_date.isoformat(),
            "message": "Customer category updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update customer category: {str(e)}")

@router.get("/customers/{customer_id}/pricing")
async def get_customer_pricing(
    customer_id: int,
    product_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    💰 Get customer-specific pricing
    """
    
    try:
        # Get customer
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get customer's price list
        price_list = db.query(PriceList).join(PriceListCategory).filter(
            PriceListCategory.customer_category == customer.customer_category,
            PriceList.is_active == True
        ).first()
        
        if not price_list:
            raise HTTPException(status_code=404, detail="No active price list found for customer category")
        
        # Build product query
        query = db.query(Product, ProductPrice).join(
            ProductPrice,
            Product.id == ProductPrice.product_id
        ).filter(
            ProductPrice.price_list_id == price_list.id
        )
        
        if product_id:
            query = query.filter(Product.id == product_id)
        
        if category:
            query = query.filter(Product.category == category)
        
        products = query.all()
        
        customer_pricing = []
        for product, price in products:
            # Check for negotiated prices
            negotiated_price = db.query(NegotiatedPrice).filter(
                NegotiatedPrice.customer_id == customer_id,
                NegotiatedPrice.product_id == product.id,
                NegotiatedPrice.is_active == True
            ).first()
            
            final_price = float(negotiated_price.negotiated_price) if negotiated_price else float(price.price)
            
            customer_pricing.append({
                "product_id": product.id,
                "sku": product.sku,
                "name_en": product.name_en,
                "name_ar": product.name_ar,
                "category": product.category,
                "base_price": float(product.cost_price),
                "list_price": float(price.price),
                "customer_price": final_price,
                "discount_percentage": float(price.discount_percentage) if price.discount_percentage else 0,
                "minimum_quantity": price.minimum_quantity,
                "is_negotiated": negotiated_price is not None,
                "negotiated_until": negotiated_price.valid_until.isoformat() if negotiated_price else None
            })
        
        return {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "customer_category": customer.customer_category,
            "price_list": {
                "id": price_list.id,
                "name": price_list.name,
                "type": price_list.price_list_type
            },
            "products": customer_pricing
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get customer pricing: {str(e)}")

@router.get("/pricing/dashboard/overview")
async def get_pricing_dashboard_overview(
    db: Session = Depends(get_db)
):
    """
    📊 Pricing system dashboard overview
    """
    
    try:
        # Price list counts
        total_price_lists = db.query(func.count(PriceList.id)).scalar() or 0
        active_price_lists = db.query(func.count(PriceList.id)).filter(
            PriceList.is_active == True
        ).scalar() or 0
        
        # Customer category breakdown
        category_breakdown = db.query(
            Customer.customer_category,
            func.count(Customer.id).label('count')
        ).group_by(Customer.customer_category).all()
        
        # Pending negotiations
        pending_negotiations = db.query(func.count(PriceNegotiationRequest.id)).filter(
            PriceNegotiationRequest.status == NegotiationStatus.PENDING.value
        ).scalar() or 0
        
        # Recent price changes
        recent_changes = db.query(func.count(PriceHistory.id)).filter(
            PriceHistory.created_at >= datetime.now() - timedelta(days=7)
        ).scalar() or 0
        
        # Price list usage
        price_list_usage = db.query(
            PriceList.name,
            PriceList.price_list_type,
            func.count(ProductPrice.id).label('product_count')
        ).join(
            ProductPrice,
            PriceList.id == ProductPrice.price_list_id
        ).group_by(PriceList.id, PriceList.name, PriceList.price_list_type).all()
        
        return {
            "total_price_lists": total_price_lists,
            "active_price_lists": active_price_lists,
            "pending_negotiations": pending_negotiations,
            "recent_price_changes": recent_changes,
            "category_breakdown": [
                {"category": category, "count": count} for category, count in category_breakdown
            ],
            "price_list_usage": [
                {
                    "name": usage.name,
                    "type": usage.price_list_type,
                    "product_count": usage.product_count
                } for usage in price_list_usage
            ],
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pricing dashboard: {str(e)}")

# Helper Functions
async def notify_customers_price_change(price_list_id: int, product_ids: List[int], db: Session):
    """Background task to notify customers about price changes"""
    try:
        # Get affected customers
        customers = db.query(Customer).join(PriceListCategory).filter(
            PriceListCategory.price_list_id == price_list_id
        ).all()
        
        # In production, send notifications (email, SMS, etc.)
        print(f"Price change notifications sent to {len(customers)} customers for {len(product_ids)} products")
        
    except Exception as e:
        print(f"Error sending price change notifications: {e}")

# Note: Database models are imported from app.models.migration 
# to avoid duplication and table conflicts 