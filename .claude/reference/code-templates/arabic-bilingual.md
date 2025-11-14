# Arabic Bilingual Support Templates

**Purpose:** Production-ready Arabic/English bilingual patterns for TSH ERP
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/code-templates/arabic-bilingual.md

---

## 🌍 Template 4.1: Bilingual Model Mixin

**Reasoning Context:**
- Arabic is PRIMARY language for TSH ERP (most users don't speak English)
- Every user-facing model needs name_ar, description_ar
- Mixin provides reusable bilingual fields
- Reduces code duplication across models
- Ensures consistency in Arabic field naming

**When to Use:**
- Products, categories, clients, orders
- Any model displayed in UI
- Reports and exports

**Code Template:**

```python
# app/models/mixins.py
from sqlalchemy import Column, String, Text

class BilingualMixin:
    """
    Mixin for models that need bilingual (English + Arabic) fields.

    Provides:
    - name / name_ar
    - description / description_ar

    Usage:
    class Product(BilingualMixin, Base):
        __tablename__ = "products"
        # Automatically gets name, name_ar, description, description_ar
    """

    # English fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Arabic fields (PRIMARY language for TSH ERP)
    name_ar = Column(String(255), nullable=False, index=True)
    description_ar = Column(Text, nullable=True)

    def get_name(self, lang: str = 'ar') -> str:
        """Get name in specified language (default Arabic)."""
        return self.name_ar if lang == 'ar' else self.name

    def get_description(self, lang: str = 'ar') -> str:
        """Get description in specified language (default Arabic)."""
        return self.description_ar if lang == 'ar' else self.description
```

**Usage in Models:**

```python
# app/models/product.py
from app.models.mixins import BilingualMixin
from app.database import Base

class Product(BilingualMixin, Base):
    """Product model with automatic bilingual support."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String(100), unique=True)
    # name, name_ar, description, description_ar inherited from BilingualMixin
    # ...rest of fields

# app/models/category.py
class Category(BilingualMixin, Base):
    """Category model with automatic bilingual support."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    # name, name_ar, description, description_ar inherited from BilingualMixin
    # ...rest of fields
```

**Pydantic Schema with Bilingual Support:**

```python
# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    """Base product schema with bilingual fields."""

    # English fields
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    # Arabic fields (MANDATORY)
    name_ar: str = Field(..., min_length=1, max_length=255)
    description_ar: Optional[str] = Field(None, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop Dell XPS 15",
                "name_ar": "لابتوب ديل اكس بي اس 15",
                "description": "High-performance laptop",
                "description_ar": "لابتوب عالي الأداء"
            }
        }
```

**Database Migration for Bilingual Fields:**

```python
# alembic/versions/xxxx_add_arabic_fields.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add Arabic fields to existing table."""

    op.add_column('products',
        sa.Column('name_ar', sa.String(255), nullable=False, server_default=''))
    op.add_column('products',
        sa.Column('description_ar', sa.Text, nullable=True))

    # Add indexes for Arabic fields (for search)
    op.create_index('idx_products_name_ar', 'products', ['name_ar'])

def downgrade():
    """Remove Arabic fields."""
    op.drop_index('idx_products_name_ar', 'products')
    op.drop_column('products', 'description_ar')
    op.drop_column('products', 'name_ar')
```

**Frontend Integration (React/Flutter):**

```dart
// Flutter example - RTL support
class ProductCard extends StatelessWidget {
  final Product product;
  final String language;

  @override
  Widget build(BuildContext context) {
    // Get name in appropriate language
    final name = language == 'ar' ? product.nameAr : product.name;
    final description = language == 'ar' ? product.descriptionAr : product.description;

    return Card(
      child: Directionality(
        textDirection: language == 'ar' ? TextDirection.rtl : TextDirection.ltr,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(name, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text(description ?? ''),
          ],
        ),
      ),
    );
  }
}
```

**API Response with Language Selection:**

```python
# app/routers/products.py
from fastapi import APIRouter, Query
from typing import Literal

@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    lang: Literal['en', 'ar'] = Query('ar', description="Response language"),
    db: Session = Depends(get_db)
):
    """
    Get product with language-specific fields.

    Returns name/description in requested language.
    Defaults to Arabic (primary language).
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "name": product.get_name(lang),
        "description": product.get_description(lang),
        # Include both languages for flexibility
        "name_en": product.name,
        "name_ar": product.name_ar,
        "description_en": product.description,
        "description_ar": product.description_ar
    }
```

**Related Patterns:**
- CRUD operations: @docs/reference/code-templates/crud-operations.md
- Error messages: @docs/reference/code-templates/error-handling.md

---

## ✅ Arabic Support Checklist

```yaml
For Every User-Facing Model:
□ name_ar field (mandatory, indexed)
□ description_ar field (optional)
□ Database indexes on Arabic fields
□ Pydantic schemas include Arabic validation
□ API responses support language selection
□ Frontend implements RTL support
□ Search includes Arabic fields
□ Error messages available in Arabic

Common Mistakes to Avoid:
❌ Forgetting name_ar field
❌ Not indexing Arabic fields
❌ Missing RTL support in UI
❌ Search only on English fields
❌ English-only error messages
```

---

**Related Documentation:**
- Architecture: @docs/core/architecture.md
- CRUD operations: @docs/reference/code-templates/crud-operations.md
- Localization guide: @docs/LOCALIZATION.md (future)
