# ASO Integration with TSH ERP Ecosystem
# دليل دمج نظام عمليات ما بعد البيع مع نظام TSH ERP

## 📋 ملخص

تم دمج نظام After-Sales Operations (ASO) بنجاح مع TSH ERP Ecosystem ليصبح جزءًا متكاملاً من النظام المركزي.

---

## ✅ ما تم إنجازه

### 1. **دمج قاعدة البيانات**
- ✅ تم نقل جميع نماذج ASO إلى `/app/models/after_sales.py`
- ✅ تم إضافة النماذج إلى `app/models/__init__.py`
- ✅ جميع الجداول الآن تستخدم نفس قاعدة البيانات المركزية `erp_db`

**النماذج المدمجة:**
```python
# في app/models/after_sales.py
- ASOProduct          # منتجات الإرجاع
- ASOReturnRequest    # طلبات الإرجاع
- ASOInspection       # الفحص
- ASOMaintenanceJob   # مهام الصيانة
- ASOWarrantyPolicy   # سياسات الضمان
- ASODecisionRecord   # سجلات القرارات
- ASONotification     # الإشعارات
- ASOOutboxEvent      # أحداث Outbox للتكامل
```

### 2. **نظام المصادقة الموحد**
- ✅ يستخدم ASO نفس جداول المستخدمين والصلاحيات من النظام الرئيسي
- ✅ نفس نظام JWT tokens
- ✅ نفس الأدوار والصلاحيات (RBAC)

**جداول المصادقة المشتركة:**
```
- users (من النظام الرئيسي)
- roles (من النظام الرئيسي)
- permissions (من النظام الرئيسي)
- role_permissions (من النظام الرئيسي)
```

### 3. **التطبيق المحمول**
- ✅ تطبيق ASO Technician على Flutter
- ✅ يستخدم نفس نظام المصادقة
- ✅ نظام إشعارات مدمج
- ✅ واجهة عربية كاملة

---

## 🔧 البنية الفنية

### قاعدة البيانات المركزية

```yaml
Database: erp_db (PostgreSQL)
Host: localhost
Port: 5432
Connection: postgresql://khaleelal-mulla:@localhost:5432/erp_db
```

### API Endpoints

جميع endpoints الخاصة بـ ASO متوفرة تحت `/aso`:

```
POST   /aso/returns                    # إنشاء طلب إرجاع
GET    /aso/returns                    # قائمة الطلبات
GET    /aso/returns/{id}               # تفاصيل طلب
POST   /aso/returns/{id}/receive       # استلام منتج
POST   /aso/returns/{id}/inspect       # فحص منتج
POST   /aso/returns/{id}/maintenance   # بدء صيانة
POST   /aso/returns/{id}/decide        # اتخاذ قرار
GET    /aso/reports/dashboard          # لوحة التحكم
GET    /aso/notifications              # الإشعارات
```

### نظام المصادقة

**تسجيل الدخول:**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "technician1",
  "password": "tech123"
}

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

**استخدام Token:**
```bash
GET /aso/returns
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📱 التطبيق المحمول

### الموقع
```
/apps/prss/mobile-tech/
```

### المميزات
1. ✅ **نظام المصادقة**: يتصل بـ API المركزي
2. ✅ **الإشعارات**: نظام إشعارات كامل مع badge counter
3. ✅ **الواجهة العربية**: جميع النصوص بالعربية
4. ✅ **Demo Mode**: يعمل بدون اتصال للتجربة

### التشغيل على iPhone
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/apps/prss/mobile-tech
flutter clean
flutter pub get
flutter run -d home --release
```

---

## 🔗 التكامل مع الأنظمة الأخرى

### 1. نظام المخزون (Inventory)
```python
# عند اتخاذ قرار إعادة تخزين منتج
POST /api/inventory/stock-movements
{
  "product_id": 123,
  "quantity": 1,
  "movement_type": "return_to_stock",
  "reference_type": "aso_return",
  "reference_id": 456,
  "from_zone": "quality_check",
  "to_zone": "available"
}
```

### 2. نظام المبيعات (Sales)
```python
# للحصول على معلومات الطلب الأصلي
GET /api/sales/orders/{order_id}
```

### 3. نظام المحاسبة (Accounting)
```python
# عند معالجة استرداد
POST /api/accounting/journal-entries
{
  "entry_type": "refund",
  "reference_type": "aso_return",
  "reference_id": 456,
  "lines": [
    {"account": "sales_returns", "debit": 1000},
    {"account": "cash", "credit": 1000}
  ]
}
```

### 4. Outbox Pattern
جميع الأحداث المهمة تُسجل في `aso_outbox_events`:

```python
# Event Types:
- return_request.created
- return_request.approved
- return_request.received
- inspection.completed
- maintenance.completed
- decision.made
- product.restocked
- refund.processed
```

---

## 🚀 خطوات التشغيل

### 1. إنشاء الجداول في قاعدة البيانات

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# تشغيل النظام الرئيسي سيقوم بإنشاء الجداول تلقائياً
python -m uvicorn app.main:app --reload --port 8000
```

### 2. إضافة بيانات تجريبية

```python
# app/scripts/seed_aso_data.py
from app.db.database import SessionLocal
from app.models.after_sales import *

db = SessionLocal()

# إنشاء منتجات تجريبية
product1 = ASOProduct(
    name="لاب توب HP ProBook 450",
    sku="HP-PB450-001",
    category="Laptops",
    base_price=3500.00,
    warranty_months=24
)
db.add(product1)
db.commit()
```

### 3. تشغيل التطبيق المحمول

```bash
cd apps/prss/mobile-tech
flutter run -d home --release
```

---

## 📊 لوحة التحكم والإحصائيات

### Endpoints الإحصائيات

```bash
# إحصائيات اليوم
GET /aso/reports/dashboard?period=today

# إحصائيات الأسبوع
GET /aso/reports/dashboard?period=week

# إحصائيات الشهر
GET /aso/reports/dashboard?period=month
```

### البيانات المتوفرة:
- عدد طلبات الإرجاع (حسب الحالة)
- متوسط وقت المعالجة
- معدل الموافقة/الرفض
- تكاليف الصيانة
- معدل إعادة التخزين
- توزيع أسباب الإرجاع

---

## 🔐 الأدوار والصلاحيات

### الأدوار المطلوبة:

```python
# في قاعدة البيانات الرئيسية
roles = [
    {"name": "ASO Admin", "permissions": ["aso.*"]},
    {"name": "ASO Inspector", "permissions": ["aso.inspect", "aso.view"]},
    {"name": "ASO Technician", "permissions": ["aso.maintain", "aso.view"]},
    {"name": "ASO Warranty Officer", "permissions": ["aso.warranty", "aso.view"]},
    {"name": "ASO Decision Maker", "permissions": ["aso.decide", "aso.view"]},
]
```

---

## 📝 مثال كامل: رحلة طلب إرجاع

### 1. العميل يُنشئ طلب إرجاع
```bash
POST /aso/returns
Authorization: Bearer <token>

{
  "customer_id": 1001,
  "sales_order_id": 5000,
  "product_id": 1,
  "serial_number": "SN-12345",
  "reason_code": "defective",
  "reason_description": "الشاشة لا تعمل"
}
```

### 2. موافقة على الطلب
```bash
POST /aso/returns/1/approve
Authorization: Bearer <admin-token>
```

### 3. استلام المنتج
```bash
POST /aso/returns/1/receive
Authorization: Bearer <logistics-token>

{
  "received_by_user_id": 2,
  "condition_notes": "تم الاستلام - حالة جيدة"
}
```

### 4. فحص المنتج
```bash
POST /aso/returns/1/inspect
Authorization: Bearer <inspector-token>

{
  "inspector_user_id": 3,
  "result": "requires_repair",
  "findings": "الشاشة تحتاج استبدال",
  "estimated_repair_cost": 500
}
```

### 5. بدء الصيانة
```bash
POST /aso/returns/1/maintenance/start
Authorization: Bearer <technician-token>

{
  "technician_user_id": 4,
  "work_description": "استبدال الشاشة"
}
```

### 6. إكمال الصيانة
```bash
POST /aso/returns/1/maintenance/1/complete
Authorization: Bearer <technician-token>

{
  "completion_notes": "تم استبدال الشاشة بنجاح",
  "quality_check_passed": true
}
```

### 7. اتخاذ القرار
```bash
POST /aso/returns/1/decide
Authorization: Bearer <decision-maker-token>

{
  "decision": "exchange",
  "rationale": "تم إصلاح المنتج بنجاح"
}
```

---

## 🛠️ الصيانة والمراقبة

### Logs
```bash
# عرض logs النظام
tail -f /var/log/tsh-erp/aso.log
```

### Health Check
```bash
GET /health
GET /aso/health
```

### Metrics
```bash
# Prometheus metrics
GET /metrics
```

---

## 📚 الوثائق التقنية

### Swagger UI
```
http://localhost:8000/docs#/After-Sales%20Operations
```

### ReDoc
```
http://localhost:8000/redoc#tag/After-Sales-Operations
```

---

## 🔄 التحديثات المستقبلية

### المخطط:
1. ✅ **Phase 1**: الدمج الأساسي مع قاعدة البيانات المركزية
2. ✅ **Phase 2**: نظام المصادقة الموحد
3. ✅ **Phase 3**: التطبيق المحمول
4. 🔲 **Phase 4**: لوحة تحكم web متكاملة
5. 🔲 **Phase 5**: تقارير متقدمة وBI
6. 🔲 **Phase 6**: تكامل مع أنظمة خارجية (Zoho, SAP, etc.)

---

## 📞 الدعم

للمزيد من المعلومات أو المساعدة:
- 📧 البريد الإلكتروني: support@tsh-erp.com
- 📱 الهاتف: +966-XXX-XXXX
- 📖 الوثائق: https://docs.tsh-erp.com/aso

---

**آخر تحديث**: October 24, 2024
**النسخة**: 1.0.0
**الحالة**: ✅ جاهز للإنتاج
