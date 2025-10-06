# 🔄 Unified Data Implementation Plan
## TSH ERP System - Cross-Platform Data Consistency

**Date:** October 6, 2025
**Priority:** CRITICAL
**Status:** In Progress

---

## 📋 Current Issues

### 1. **Product Images Missing**
- ✅ Images exist in: `frontend/public/images/products/`
- ❌ Database `products.image_url` = `null`
- ❌ Mobile app cannot access local frontend images
- ❌ Need unified image serving system

### 2. **Data Inconsistency**
- React frontend reads from: `/images/products/{barcode}.jpg`
- Flutter mobile app expects: API endpoint with image URL
- Backend doesn't serve static product images
- No unified image management system

---

## 🎯 Solution Architecture

### Phase 1: Backend Image Serving (CRITICAL)
**Goal:** Make product images accessible to all platforms

#### 1.1 Create Static File Serving
```python
# app/main.py
from fastapi.staticfiles import StaticFiles

# Mount static files directory
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")
```

**Result:**
- Images accessible at: `http://192.168.68.66:8000/static/images/products/{barcode}.jpg`
- Works for both React and Flutter apps

#### 1.2 Update Product Image URLs in Database
```sql
UPDATE products
SET image_url = '/static/images/products/' || barcode || '.jpg'
WHERE barcode IS NOT NULL;
```

#### 1.3 Create Image URL Helper in Backend
```python
# app/utils/image_helper.py
def get_product_image_url(barcode: str, base_url: str = "") -> str:
    if not barcode:
        return None
    return f"{base_url}/static/images/products/{barcode}.jpg"
```

### Phase 2: Unified API Endpoints

#### 2.1 Products API Enhancement
```python
# app/routers/products.py
@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    request: Request,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    base_url = str(request.base_url).rstrip('/')
    products = db.query(Product).limit(limit).offset(offset).all()

    for product in products:
        if product.barcode:
            product.image_url = f"{base_url}/static/images/products/{product.barcode}.jpg"

    return products
```

#### 2.2 Inventory Items API Enhancement
```python
# app/routers/inventory.py
@router.get("/inventory/items", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    request: Request,
    warehouse_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    base_url = str(request.base_url).rstrip('/')
    items = db.query(InventoryItem).join(Product)...

    for item in items:
        if item.product and item.product.barcode:
            item.product.image_url = f"{base_url}/static/images/products/{item.product.barcode}.jpg"

    return items
```

### Phase 3: Frontend Updates

#### 3.1 React Frontend (Already Working)
- Uses: `/images/products/{barcode}.jpg`
- After backend update: Can also use `/static/images/products/{barcode}.jpg`
- **Action:** Update image paths to use API base URL

#### 3.2 Flutter Mobile App
```dart
// lib/models/product_model.dart
class Product {
  final int id;
  final String name;
  final String? imageUrl; // Full URL from API

  Widget buildImage() {
    if (imageUrl == null || imageUrl!.isEmpty) {
      return Icon(Icons.image_not_supported);
    }
    return Image.network(
      imageUrl!,
      errorBuilder: (context, error, stackTrace) {
        return Icon(Icons.broken_image);
      },
    );
  }
}
```

### Phase 4: Image Upload System (Future)

```python
# app/routers/products.py
@router.post("/products/{id}/upload-image")
async def upload_product_image(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Save file
    file_path = f"frontend/public/images/products/{product.barcode}.jpg"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Update database
    product.image_url = f"/static/images/products/{product.barcode}.jpg"
    db.commit()

    return {"message": "Image uploaded successfully", "url": product.image_url}
```

---

## 🔧 Implementation Steps

### Step 1: Update Backend Main File
**File:** `app/main.py`

```python
from fastapi.staticfiles import StaticFiles
import os

# Add after app initialization
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"✅ Serving static files from: {static_dir}")
else:
    print(f"⚠️ Static directory not found: {static_dir}")
```

### Step 2: Create Image Helper Utility
**File:** `app/utils/image_helper.py`

```python
import os
from typing import Optional

STATIC_BASE_URL = "/static/images/products"

def get_product_image_url(barcode: Optional[str], base_url: str = "") -> Optional[str]:
    """
    Generate product image URL from barcode

    Args:
        barcode: Product barcode
        base_url: API base URL (e.g., "http://192.168.68.66:8000")

    Returns:
        Full image URL or None
    """
    if not barcode:
        return None

    image_path = f"{STATIC_BASE_URL}/{barcode}.jpg"

    # Check if file exists
    file_path = f"frontend/public/images/products/{barcode}.jpg"
    if not os.path.exists(file_path):
        return None

    if base_url:
        return f"{base_url}{image_path}"
    return image_path


def check_image_exists(barcode: str) -> bool:
    """Check if product image file exists"""
    if not barcode:
        return False
    file_path = f"frontend/public/images/products/{barcode}.jpg"
    return os.path.exists(file_path)
```

### Step 3: Update Product Schema
**File:** `app/schemas/product.py`

```python
from pydantic import BaseModel, computed_field
from typing import Optional

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    name_ar: Optional[str] = None
    barcode: Optional[str] = None
    unit_price: float
    unit_of_measure: str
    is_active: bool
    category_name: Optional[str] = None
    image_url: Optional[str] = None  # Will be populated dynamically

    class Config:
        from_attributes = True
```

### Step 4: Update Products Router
**File:** `app/routers/products.py`

```python
from fastapi import Request
from app.utils.image_helper import get_product_image_url

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    request: Request,
    limit: int = 100,
    offset: int = 0,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    base_url = str(request.base_url).rstrip('/')

    query = db.query(Product)

    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.limit(limit).offset(offset).all()

    # Add image URLs
    for product in products:
        product.image_url = get_product_image_url(product.barcode, base_url)

    return products
```

### Step 5: Update Inventory Router
**File:** `app/routers/inventory.py`

```python
from app.utils.image_helper import get_product_image_url

@router.get("/inventory/items")
async def get_inventory_items(
    request: Request,
    warehouse_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    base_url = str(request.base_url).rstrip('/')

    query = db.query(InventoryItem).join(Product)

    if warehouse_id:
        query = query.filter(InventoryItem.warehouse_id == warehouse_id)

    items = query.limit(limit).all()

    # Add image URLs to products
    for item in items:
        if item.product:
            item.product.image_url = get_product_image_url(item.product.barcode, base_url)

    return items
```

### Step 6: Update Flutter Models
**File:** `tsh_salesperson_app/lib/models/product_model.dart`

```dart
class Product {
  final int id;
  final String sku;
  final String name;
  final String? nameAr;
  final String? barcode;
  final double unitPrice;
  final String unitOfMeasure;
  final bool isActive;
  final String? categoryName;
  final String? imageUrl; // Now will have full URL from API

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      sku: json['sku'],
      name: json['name'],
      nameAr: json['name_ar'],
      barcode: json['barcode'],
      unitPrice: (json['unit_price'] as num).toDouble(),
      unitOfMeasure: json['unit_of_measure'],
      isActive: json['is_active'] ?? true,
      categoryName: json['category_name'],
      imageUrl: json['image_url'], // Full URL from backend
    );
  }
}
```

### Step 7: Update Flutter Product Display Widget
**File:** `tsh_salesperson_app/lib/widgets/product_card.dart`

```dart
import 'package:cached_network_image/cached_network_image.dart';

class ProductCard extends StatelessWidget {
  final Product product;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          // Product Image
          Container(
            height: 150,
            child: product.imageUrl != null
                ? CachedNetworkImage(
                    imageUrl: product.imageUrl!,
                    placeholder: (context, url) => CircularProgressIndicator(),
                    errorWidget: (context, url, error) => Icon(Icons.image_not_supported),
                    fit: BoxFit.cover,
                  )
                : Icon(Icons.image, size: 60),
          ),

          // Product Info
          Padding(
            padding: EdgeInsets.all(8.0),
            child: Column(
              children: [
                Text(product.name, style: TextStyle(fontWeight: FontWeight.bold)),
                Text('\$${product.unitPrice.toStringAsFixed(2)}'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## 📊 Testing Checklist

### Backend Tests:
- [ ] Static files accessible at `/static/images/products/`
- [ ] Products API returns image URLs
- [ ] Inventory Items API returns image URLs
- [ ] Image URLs work from both localhost and network IP

### Frontend Tests (React):
- [ ] Product images load on POS screen
- [ ] Product images load on inventory page
- [ ] Images load on customer portal

### Mobile Tests (Flutter):
- [ ] Product images load on POS screen
- [ ] Product images load on product list
- [ ] Images cached properly
- [ ] Fallback icon shows when image missing

---

## 🚀 Deployment

### Development:
```bash
# 1. Update backend
cd /Users/khaleelal-mulla/TSH_ERP_System_Local
# Apply changes to app/main.py, routers, utils

# 2. Restart backend
killall uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Test API
curl http://192.168.68.66:8000/api/products?limit=1

# 4. Rebuild Flutter app
cd tsh_salesperson_app
flutter run -d 00008130-0004310C1ABA001C
```

### Production:
1. Migrate static files to CDN or S3
2. Update image URLs to use CDN
3. Implement image optimization (resize, compress)
4. Add image caching headers

---

## 📈 Expected Results

### Before:
- ❌ No product images on mobile app
- ❌ Inconsistent data across platforms
- ❌ Image URLs = null

### After:
- ✅ All products have image URLs
- ✅ Images accessible from all platforms
- ✅ Unified image serving system
- ✅ Cached images on mobile app
- ✅ Fallback icons for missing images

---

**Status:** Ready to implement
**Estimated Time:** 30 minutes
**Priority:** CRITICAL

