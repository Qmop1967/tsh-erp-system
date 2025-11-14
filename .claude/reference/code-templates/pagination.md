# Pagination Templates

**Purpose:** Production-ready pagination patterns for web and mobile for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/pagination.md

---

## 📄 Template 5.1: Mobile-Optimized Pagination Response

**Reasoning Context:**
- 8 Flutter mobile apps are primary interface for TSH ERP
- Mobile networks can be slow in Iraq
- Smaller page sizes for mobile (25-50 items vs 100 for web)
- Mobile needs: prev/next URLs, progress indicator data
- Infinite scroll UX pattern common on mobile

**When to Use:**
- Mobile app API endpoints
- Slow network scenarios
- Image-heavy content
- Infinite scroll implementations

**Code Template:**

```python
# app/schemas/pagination.py
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class MobilePaginationMetadata(BaseModel):
    """Mobile-optimized pagination metadata."""

    # Basic pagination
    page: int
    per_page: int
    total_items: int
    total_pages: int

    # Mobile-specific
    has_next: bool
    has_previous: bool
    next_page: Optional[int]
    prev_page: Optional[int]

    # URLs for easy navigation
    next_url: Optional[str]
    prev_url: Optional[str]

    # Progress indicator data
    items_shown: int  # Cumulative items shown so far
    percent_complete: float  # 0.0 to 100.0

class MobilePaginatedResponse(BaseModel, Generic[T]):
    """Mobile-optimized paginated response."""
    items: List[T]
    pagination: MobilePaginationMetadata

    # Optional: Prefetch hint for next page
    prefetch_next: bool = False

# Mobile endpoint example
@router.get("/mobile/products", response_model=MobilePaginatedResponse[ProductResponse])
async def list_products_mobile(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=50, description="Max 50 for mobile"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    List products optimized for mobile apps.

    Smaller page size (25 default vs 100 for web).
    Includes navigation URLs for easy implementation.
    Progress indicator for infinite scroll.
    """
    # Query products
    offset = (page - 1) * per_page
    total_items = db.query(Product).filter(Product.is_active == True).count()
    products = db.query(Product).filter(
        Product.is_active == True
    ).offset(offset).limit(per_page).all()

    # Calculate pagination
    total_pages = (total_items + per_page - 1) // per_page
    has_next = page < total_pages
    has_previous = page > 1
    items_shown = min(page * per_page, total_items)
    percent_complete = (items_shown / total_items * 100) if total_items > 0 else 100

    # Build URLs
    base_url = str(request.url).split('?')[0] if request else ""
    next_url = f"{base_url}?page={page + 1}&per_page={per_page}" if has_next else None
    prev_url = f"{base_url}?page={page - 1}&per_page={per_page}" if has_previous else None

    return {
        "items": products,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
            "next_page": page + 1 if has_next else None,
            "prev_page": page - 1 if has_previous else None,
            "next_url": next_url,
            "prev_url": prev_url,
            "items_shown": items_shown,
            "percent_complete": round(percent_complete, 1)
        },
        "prefetch_next": has_next and (total_pages - page) <= 2  # Prefetch if near end
    }
```

**Flutter Implementation Example:**

```dart
// Mobile app infinite scroll implementation
class ProductListState extends State<ProductListWidget> {
  List<Product> products = [];
  int currentPage = 1;
  bool isLoading = false;
  bool hasMore = true;

  Future<void> loadMore() async {
    if (isLoading || !hasMore) return;

    setState(() => isLoading = true);

    final response = await api.get(
      '/mobile/products?page=$currentPage&per_page=25'
    );

    setState(() {
      products.addAll(response.items);
      currentPage = response.pagination.nextPage ?? currentPage;
      hasMore = response.pagination.hasNext;
      isLoading = false;
    });

    // Prefetch next page if suggested
    if (response.prefetchNext && hasMore) {
      _prefetchNextPage();
    }
  }
}
```

**Web Pagination (Standard):**

```python
# app/schemas/pagination.py
class PaginationMetadata(BaseModel):
    """Standard web pagination metadata."""
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response for web."""
    items: List[T]
    pagination: PaginationMetadata

# Web endpoint
@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100, description="Max 100 for web"),
    db: Session = Depends(get_db)
):
    """
    List products with standard pagination.

    Max 100 items per page.
    For web applications.
    """
    offset = (page - 1) * limit
    total_items = db.query(Product).filter(Product.is_active == True).count()
    products = db.query(Product).filter(
        Product.is_active == True
    ).offset(offset).limit(limit).all()

    total_pages = (total_items + limit - 1) // limit

    return {
        "items": products,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }
```

**Related Patterns:**
- CRUD operations: @docs/reference/code-templates/crud-operations.md
- Database optimization: @docs/reference/code-templates/database-optimization.md

---

## ⚡ Pagination Performance Tips

```yaml
Best Practices:
✅ Always use OFFSET and LIMIT in SQL
✅ Add indexes on sorted columns
✅ Count queries can be expensive - consider caching
✅ Use smaller page sizes for mobile (25-50)
✅ Use larger page sizes for web (100)
✅ Provide prefetch hints for better UX

Avoid:
❌ Loading all records then slicing in Python
❌ No upper limit on page size
❌ Counting on every request (cache when possible)
❌ Same page size for mobile and web
```

---

**Related Documentation:**
- CRUD operations: @docs/reference/code-templates/crud-operations.md
- Mobile optimization: @docs/MOBILE_OPTIMIZATION.md (future)
