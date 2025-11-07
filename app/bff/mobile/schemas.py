"""
Mobile BFF Schemas
Pydantic models optimized for mobile responses
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Product Schemas (Mobile Optimized)
# ============================================================================

class MobileProductMinimal(BaseModel):
    """Minimal product info for lists (home, search, etc.)"""
    id: int
    name: str
    price: float
    image: Optional[str] = None
    in_stock: bool
    discount: Optional[float] = None

    class Config:
        from_attributes = True


class MobileProductDetail(BaseModel):
    """Detailed product info for product screen"""
    id: int
    name: str
    description: str
    price: float
    original_price: Optional[float] = None
    discount: Optional[float] = None
    images: List[str] = []
    in_stock: bool
    stock_quantity: int
    branch_name: Optional[str] = None
    rating: Optional[float] = None
    review_count: int = 0
    specifications: dict = {}

    class Config:
        from_attributes = True


# ============================================================================
# Promotion Schemas
# ============================================================================

class MobilePromotion(BaseModel):
    """Mobile-optimized promotion"""
    id: int
    title: str
    description: str
    banner_url: Optional[str] = None
    discount_percentage: Optional[float] = None
    valid_until: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Customer Schemas
# ============================================================================

class MobileCustomerInfo(BaseModel):
    """Minimal customer info for mobile"""
    id: int
    name: str
    avatar: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Cart Schemas
# ============================================================================

class MobileCartSummary(BaseModel):
    """Cart summary for header/badge"""
    items_count: int = 0
    total: float = 0.0
    currency: str = "IQD"

    class Config:
        from_attributes = True


class MobileCartItem(BaseModel):
    """Cart item for cart screen"""
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    quantity: int
    price: float
    subtotal: float

    class Config:
        from_attributes = True


class MobileCart(BaseModel):
    """Full cart for checkout"""
    items: List[MobileCartItem]
    subtotal: float
    discount: float = 0.0
    delivery_fee: float = 0.0
    total: float
    currency: str = "IQD"

    class Config:
        from_attributes = True


# ============================================================================
# Home Screen Schema (Aggregated)
# ============================================================================

class MobileHomeResponse(BaseModel):
    """
    Complete home screen data in ONE call

    This aggregates data from multiple modules:
    - Products (featured, best sellers, new)
    - Promotions
    - Customer info
    - Cart summary
    """
    featured_products: List[MobileProductMinimal] = []
    best_sellers: List[MobileProductMinimal] = []
    new_arrivals: List[MobileProductMinimal] = []
    promotions: List[MobilePromotion] = []
    customer: Optional[MobileCustomerInfo] = None
    cart: MobileCartSummary = Field(default_factory=MobileCartSummary)

    class Config:
        from_attributes = True


# ============================================================================
# Search Schema
# ============================================================================

class MobileSearchResponse(BaseModel):
    """Search results for mobile"""
    query: str
    results: List[MobileProductMinimal]
    total_count: int
    page: int = 1
    page_size: int = 20
    has_more: bool = False

    class Config:
        from_attributes = True


# ============================================================================
# Category Schema
# ============================================================================

class MobileCategory(BaseModel):
    """Category for mobile"""
    id: int
    name: str
    icon: Optional[str] = None
    product_count: int = 0

    class Config:
        from_attributes = True


class MobileCategoryProductsResponse(BaseModel):
    """Category with products"""
    category: MobileCategory
    products: List[MobileProductMinimal]
    total_count: int
    page: int = 1
    has_more: bool = False

    class Config:
        from_attributes = True


# ============================================================================
# Order Schemas
# ============================================================================

class MobileOrderItem(BaseModel):
    """Order item for mobile"""
    product_name: str
    quantity: int
    price: float
    subtotal: float

    class Config:
        from_attributes = True


class MobileOrderMinimal(BaseModel):
    """Minimal order info for list"""
    id: int
    order_number: str
    status: str
    total: float
    currency: str = "IQD"
    created_at: str

    class Config:
        from_attributes = True


class MobileOrderDetail(BaseModel):
    """Detailed order for order screen"""
    id: int
    order_number: str
    status: str
    items: List[MobileOrderItem]
    subtotal: float
    discount: float
    delivery_fee: float
    total: float
    currency: str = "IQD"
    created_at: str
    delivery_address: Optional[str] = None
    estimated_delivery: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Checkout Schema (Aggregated)
# ============================================================================

class MobileAddress(BaseModel):
    """Delivery address"""
    id: int
    label: str
    address: str
    is_default: bool = False

    class Config:
        from_attributes = True


class MobilePaymentMethod(BaseModel):
    """Payment method"""
    id: str
    name: str
    icon: Optional[str] = None
    is_default: bool = False

    class Config:
        from_attributes = True


class MobileDeliveryOption(BaseModel):
    """Delivery option"""
    id: str
    name: str
    fee: float
    estimated_days: int
    is_default: bool = False

    class Config:
        from_attributes = True


class MobileCheckoutResponse(BaseModel):
    """
    Complete checkout data in ONE call

    Aggregates:
    - Cart items
    - Addresses
    - Payment methods
    - Delivery options
    - Price calculation
    """
    cart: MobileCart
    addresses: List[MobileAddress] = []
    payment_methods: List[MobilePaymentMethod] = []
    delivery_options: List[MobileDeliveryOption] = []
    promotions: List[MobilePromotion] = []
    summary: dict  # subtotal, discount, delivery_fee, total

    class Config:
        from_attributes = True


# ============================================================================
# Profile Schema
# ============================================================================

class MobileProfile(BaseModel):
    """User profile for mobile"""
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    addresses_count: int = 0
    orders_count: int = 0
    favorites_count: int = 0

    class Config:
        from_attributes = True
