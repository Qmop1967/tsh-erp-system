# TSH ERP System - Sales and Inventory Module

## نظرة عامة

تم إكمال وحدة المبيعات والمخزون في نظام TSH ERP مع جميع الوظائف الأساسية المطلوبة لإدارة العمليات التجارية.

## النماذج المُضافة

### 1. إدارة المنتجات (`product.py`)
- **Category**: فئات المنتجات مع إمكانية الفئات الفرعية
- **Product**: المنتجات الأساسية مع رموز SKU وباركود

### 2. إدارة العملاء والموردين (`customer.py`)
- **Customer**: بيانات العملاء مع حدود الائتمان وشروط الدفع
- **Supplier**: بيانات الموردين مع شروط الدفع

### 3. إدارة المخزون (`inventory.py`)
- **InventoryItem**: عناصر المخزون لكل منتج في كل مستودع
- **StockMovement**: تتبع جميع حركات دخول وخروج المخزون

### 4. إدارة المبيعات (`sales.py`)
- **SalesOrder**: أوامر البيع مع حالات مختلفة (مسودة، مؤكد، مشحون، إلخ)
- **SalesItem**: عناصر أوامر البيع مع تفاصيل الكميات والأسعار

### 5. إدارة المشتريات (`purchase.py`)
- **PurchaseOrder**: أوامر الشراء من الموردين
- **PurchaseItem**: عناصر أوامر الشراء

## المخططات (Schemas)

تم إنشاء مخططات Pydantic شاملة لكل نموذج تتضمن:
- مخططات الإنشاء (Create)
- مخططات التحديث (Update)
- مخططات الاستجابة (Response)
- مخططات الملخص (Summary) للقوائم

## الخدمات (Services)

### 1. خدمة المنتجات (`ProductService`)
- إنشاء وإدارة فئات المنتجات
- إنشاء وإدارة المنتجات
- البحث والتصفية
- التحقق من صحة البيانات

### 2. خدمة المخزون (`InventoryService`)
- تتبع المخزون الحالي
- تسجيل حركات المخزون
- حجز وإلغاء حجز المخزون
- تعديل المخزون
- تقارير المخزون
- إنذارات المخزون المنخفض

### 3. خدمة المبيعات (`SalesService`)
- إنشاء أوامر البيع
- إدارة دورة حياة الأمر (مسودة → مؤكد → مشحون → مسلم)
- حساب الإجماليات والضرائب
- ربط المبيعات بالمخزون
- إلغاء الأوامر

## نقاط الخدمة (API Endpoints)

### المنتجات (`/products`)
```
POST   /products/categories     - إنشاء فئة
GET    /products/categories     - قائمة الفئات
PUT    /products/categories/{id} - تحديث فئة

POST   /products               - إنشاء منتج
GET    /products               - قائمة المنتجات (مع بحث وتصفية)
GET    /products/{id}          - تفاصيل منتج
GET    /products/sku/{sku}     - البحث برمز المنتج
PUT    /products/{id}          - تحديث منتج
DELETE /products/{id}          - حذف منتج (تعطيل)
```

### المخزون (`/inventory`)
```
GET    /inventory/items        - عناصر المخزون
GET    /inventory/report       - تقرير المخزون
POST   /inventory/movements    - تسجيل حركة مخزون
GET    /inventory/movements    - قائمة حركات المخزون
POST   /inventory/adjust       - تعديل المخزون
```

### المبيعات (`/sales`)
```
POST   /sales/orders           - إنشاء أمر بيع
GET    /sales/orders           - قائمة أوامر البيع
GET    /sales/orders/{id}      - تفاصيل أمر بيع
PUT    /sales/orders/{id}/confirm - تأكيد أمر بيع
PUT    /sales/orders/{id}/ship    - شحن أمر بيع
PUT    /sales/orders/{id}/cancel  - إلغاء أمر بيع
```

### العملاء والموردين (`/customers`)
```
POST   /customers              - إنشاء عميل
GET    /customers              - قائمة العملاء
GET    /customers/{id}         - تفاصيل عميل
PUT    /customers/{id}         - تحديث عميل

POST   /customers/suppliers    - إنشاء مورد
GET    /customers/suppliers    - قائمة الموردين
GET    /customers/suppliers/{id} - تفاصيل مورد
PUT    /customers/suppliers/{id} - تحديث مورد
```

## الميزات الرئيسية

### 1. إدارة المخزون المتقدمة
- تتبع الكميات المتوفرة والمحجوزة
- حساب متوسط التكلفة تلقائياً
- تحديد الحد الأدنى ونقطة إعادة الطلب
- إنذارات المخزون المنخفض

### 2. دورة حياة المبيعات
- **مسودة**: إنشاء الأمر الأولي
- **مؤكد**: تأكيد الأمر وحجز المخزون
- **مشحون**: شحن الأمر وخصم المخزون
- **مسلم**: تسليم الأمر للعميل
- **ملغي**: إلغاء الأمر وإلغاء حجز المخزون

### 3. الحسابات والضرائب
- حساب الخصومات على مستوى العنصر والأمر
- حساب الضرائب
- تتبع المدفوعات والمبالغ المستحقة

### 4. التتبع والمراجعة
- تسجيل جميع حركات المخزون مع المراجع
- تتبع من قام بالعملية ومتى
- ربط الحركات بأوامر البيع والشراء

## قاعدة البيانات

تم تحديث نماذج قاعدة البيانات لتشمل:
- العلاقات الصحيحة بين الجداول
- قيود الـ foreign keys
- الفهارس للبحث السريع
- الحقول المحسوبة (Properties)

## كيفية الاستخدام

### 1. إعداد قاعدة البيانات
```bash
# إنشاء migration جديد
alembic revision --autogenerate -m "Add sales and inventory models"

# تطبيق الـ migrations
alembic upgrade head
```

### 2. تشغيل التطبيق
```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الخادم
uvicorn app.main:app --reload
```

### 3. الوصول للوثائق
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## المثال العملي

### إنشاء منتج جديد:
```json
POST /products
{
  "sku": "PROD-001",
  "name": "منتج تجريبي",
  "category_id": 1,
  "unit_price": 100.00,
  "unit_of_measure": "قطعة",
  "min_stock_level": 10,
  "is_active": true
}
```

### إنشاء أمر بيع:
```json
POST /sales/orders
{
  "customer_id": 1,
  "branch_id": 1,
  "warehouse_id": 1,
  "order_date": "2024-01-15",
  "sales_items": [
    {
      "product_id": 1,
      "quantity": 5,
      "unit_price": 100.00
    }
  ]
}
```

## التطوير المستقبلي

يمكن إضافة المزيد من الميزات مثل:
- نظام الفواتير
- التكامل مع أنظمة الدفع
- تقارير مبيعات متقدمة
- إدارة المرتجعات
- نظام التنبيهات والإشعارات
- تحليلات المبيعات والمخزون
