# TSH ERP API Response Standards
# معايير استجابة API لنظام TSH ERP

## 📋 Overview / نظرة عامة

This document defines the **STANDARDIZED** response format for all API endpoints.
**NEVER** change field names without updating this document and all related models.

هذا المستند يحدد تنسيق الاستجابة **الموحد** لجميع نقاط النهاية في الـ API.
**لا تقم أبداً** بتغيير أسماء الحقول دون تحديث هذا المستند وجميع النماذج المرتبطة.

---

## 🎯 Core Principles / المبادئ الأساسية

1. **One Source of Truth**: This document is the single source of truth for API responses
2. **Backward Compatibility**: When adding new fields, keep old fields for compatibility
3. **Consistent Naming**: Use snake_case for all field names
4. **Type Safety**: Always specify field types clearly

---

## 📦 Product Response Schema

### Endpoint: `GET /api/consumer/products`

**Response Format:**
```json
{
  "status": "success",
  "count": 5,
  "items": [
    {
      // ============ PRIMARY FIELDS (Required for Flutter Product model) ============
      "id": "uuid-string",                    // Product UUID
      "zoho_item_id": "string",               // Zoho Books item ID
      "sku": "string",                        // Product SKU/barcode
      "name": "string",                       // Product name (Arabic/English)
      "description": "string|null",           // Product description
      "image_url": "string|null",             // Full image URL (CDN or placeholder)
      "cdn_image_url": "string|null",         // Original CDN URL
      "category": "string",                   // Product category
      "stock_quantity": 0,                    // Stock quantity (integer)
      "actual_available_stock": 0,            // Available stock (integer)
      "warehouse_id": "string",               // Warehouse UUID (empty for consumer)
      "is_active": true,                      // Active status (boolean)
      "price": 0.0,                           // Price (float)
      "currency": "IQD",                      // Currency code

      // ============ LEGACY FIELDS (Backward compatibility - DO NOT REMOVE) ============
      "item_id": "string",                    // Same as zoho_item_id
      "product_id": "string",                 // Same as id
      "product_name": "string",               // Same as name
      "category_name": "string",              // Same as category
      "selling_price": 0.0,                   // Same as price
      "quantity": 0.0,                        // Same as actual_available_stock
      "barcode": "string",                    // Same as sku
      "image_path": "string",                 // Same as image_url
      "in_stock": true,                       // Computed from actual_available_stock > 0
      "has_image": true                       // Computed from image_url presence
    }
  ]
}
```

### Endpoint: `GET /api/consumer/products/{id}`

**Response Format:**
```json
{
  "status": "success",
  "product": {
    // Same structure as items in products list
    // Plus additional fields:
    "created_at": "ISO8601 datetime string",
    "updated_at": "ISO8601 datetime string",
    "last_synced": "ISO8601 datetime string"
  }
}
```

### Endpoint: `GET /api/consumer/categories`

**Response Format:**
```json
{
  "status": "success",
  "categories": [
    "Category 1",
    "Category 2",
    "شواحن لابتوب",
    "..."
  ]
}
```

---

## 🔧 Flutter Product Model Mapping

The Flutter `Product` model expects these **exact** field names:

```dart
class Product {
  final String id;                          // ✅ Must match
  final String zohoItemId;                  // ✅ zoho_item_id
  final String sku;                         // ✅ Must match
  final String name;                        // ✅ Must match
  final String? description;                // ✅ Must match
  final String? imageUrl;                   // ✅ image_url
  final String? cdnImageUrl;                // ✅ cdn_image_url
  final String? category;                   // ✅ Must match
  final int stockQuantity;                  // ✅ stock_quantity
  final int actualAvailableStock;           // ✅ actual_available_stock
  final String warehouseId;                 // ✅ warehouse_id
  final bool isActive;                      // ✅ is_active
  final double price;                       // ✅ Must match
  final String currency;                    // ✅ Must match
}
```

**Model Location:**
- File: `mobile/flutter_apps/10_tsh_consumer_app/lib/models/product.dart`
- Factory: `Product.fromJson()`

**Current Implementation:**
- Supports **both** standard and legacy field names
- Uses null-coalescing (`??`) for backward compatibility
- Example: `json['name'] ?? json['product_name']`

---

## 📝 Implementation Checklist

When creating or modifying API endpoints that return products:

- [ ] Use the standardized field names from this document
- [ ] Include **both** primary and legacy fields for compatibility
- [ ] Add comments marking PRIMARY vs LEGACY sections
- [ ] Test response with Flutter app
- [ ] Update this document if adding new fields
- [ ] Run integration tests

---

## 🚨 Breaking Change Prevention

### ⛔ DO NOT:
- Change primary field names without updating Flutter models
- Remove legacy fields without deprecation notice
- Use different naming conventions (e.g., camelCase instead of snake_case)
- Return different data types for the same field

### ✅ DO:
- Add new fields with clear comments
- Mark legacy fields as "// Backward compatibility"
- Update this document when making changes
- Test with mobile app before deployment
- Use type hints in Python (FastAPI)

---

## 🔄 Migration Path for Removing Legacy Fields

When you want to remove legacy fields in the future:

1. **Phase 1 - Deprecation Notice (Current)**
   - Keep both primary and legacy fields
   - Mark legacy fields with "// Deprecated - use {primary_field}"
   - Update documentation

2. **Phase 2 - Warning Period (3-6 months)**
   - Add deprecation warnings in API responses
   - Monitor usage of legacy fields
   - Notify all client developers

3. **Phase 3 - Removal**
   - Remove legacy fields from API
   - Update this document
   - Increment API version (v2)

---

## 📞 Contact / الاتصال

If you need to modify API responses, contact:
- **Backend Team**: Khaleel Al-Mulla
- **Mobile Team**: [Team Contact]
- **Documentation**: This file location

---

## 📚 Related Files / الملفات ذات الصلة

### Backend:
- `/app/routers/consumer_api.py` - Consumer API endpoints
- `/app/models/product.py` - Product database model

### Frontend:
- `/mobile/flutter_apps/10_tsh_consumer_app/lib/models/product.dart` - Flutter Product model
- `/mobile/flutter_apps/10_tsh_consumer_app/lib/services/api_service.dart` - API service

### Documentation:
- `/COMPLETE_ARCHITECTURE_GUIDE.md` - Full system architecture
- `/API_RESPONSE_STANDARDS.md` - This file

---

## 📊 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-10-31 | Initial standardization document | Khaleel Al-Mulla |
| 1.0.1 | 2025-10-31 | Added dual-format support (primary + legacy) | Khaleel Al-Mulla |

---

## ⚠️ CRITICAL NOTES

**READ THIS BEFORE MAKING ANY CHANGES:**

1. The Flutter app's `Product.fromJson()` is now flexible and supports both formats
2. The API returns **both** primary and legacy fields for maximum compatibility
3. This prevents future issues when field names don't match
4. Always test changes with the mobile app running on `consumer.tsh.sale`
5. Never commit API changes without testing on production

---

**Last Updated:** 2025-10-31
**Document Owner:** Khaleel Al-Mulla
**Review Cycle:** Quarterly
