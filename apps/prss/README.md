# TSH After-Sales Operations System (PRSS)

**نظام خدمات ما بعد البيع الشامل**

## 📋 نظرة عامة

PRSS هو نظام متكامل لإدارة جميع عمليات ما بعد البيع بما في ذلك:
- المردودات (Returns)
- الفحص (Inspection)
- الصيانة (Maintenance)
- الضمان (Warranty)
- الاستبدال والاسترداد المالي
- إدارة الخسائر اللوجستية

## 🏗️ البنية المعمارية

```
apps/prss/
├── backend/              # FastAPI Backend
│   ├── src/prss/
│   │   ├── api/         # REST API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── integration/ # External system clients
│   │   ├── security/    # Authentication & Authorization
│   │   └── events/      # Outbox pattern
│   ├── alembic/         # Database migrations
│   └── tests/           # Pytest tests
├── web-admin/           # React Admin Dashboard
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── store/
├── mobile-tech/         # Flutter Mobile App
│   └── lib/
└── docker-compose.yml   # Docker orchestration
```

## 🚀 البدء السريع

### المتطلبات الأساسية

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (اختياري)
- Flutter 3.0+ (لتطبيق الموبايل)

### التثبيت باستخدام Docker (موصى به)

```bash
cd apps/prss

# إنشاء ملف .env
cp backend/.env.example backend/.env

# تعديل المتغيرات في .env حسب الحاجة

# بدء جميع الخدمات
docker-compose up -d

# انتظر حتى تبدأ الخدمات ثم افتح:
# - API Docs: http://localhost:8001/docs
# - Web Admin: http://localhost:5174
```

### التثبيت اليدوي

#### 1. Backend Setup

```bash
cd apps/prss/backend

# تثبيت Poetry
curl -sSL https://install.python-poetry.org | python3 -

# تثبيت المكتبات
poetry install

# إنشاء قاعدة البيانات
createdb prss_db

# تشغيل المهاجرات
poetry run alembic upgrade head

# إنشاء مستخدم admin (اختياري)
poetry run python -c "
from prss.db import SessionLocal
from prss.models.all_models import User
from prss.models.base import UserRole
from prss.security.auth import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@tsh.com',
    full_name='System Administrator',
    role=UserRole.ADMIN,
    hashed_password=get_password_hash('admin123'),
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created: admin / admin123')
"

# تشغيل الخادم
poetry run uvicorn prss.main:app --reload --port 8001
```

#### 2. Web Admin Setup

```bash
cd apps/prss/web-admin

# تثبيت المكتبات
npm install

# تشغيل خادم التطوير
npm run dev
```

#### 3. Mobile App Setup

```bash
cd apps/prss/mobile-tech

# تثبيت المكتبات
flutter pub get

# تشغيل التطبيق
flutter run
```

## 📡 API Documentation

### Authentication

جميع المسارات محمية بـ JWT. للحصول على Token:

```bash
curl -X POST http://localhost:8001/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### مسارات API الرئيسية

#### إنشاء طلب إرجاع

```bash
POST /v1/returns
Content-Type: application/json
Authorization: Bearer <token>

{
  "customer_id": 1,
  "sales_order_id": 100,
  "product_id": 50,
  "serial_number": "SN-12345",
  "reason_code": "defective",
  "reason_description": "المنتج لا يعمل بشكل صحيح",
  "photos": []
}
```

#### استلام المرتجع

```bash
POST /v1/returns/{id}/receive
Authorization: Bearer <token>

{
  "received_by": 1,
  "notes": "تم الاستلام بحالة جيدة",
  "condition_photos": []
}
```

#### الفحص

```bash
POST /v1/returns/{id}/inspect
Authorization: Bearer <token>

{
  "return_request_id": 1,
  "inspector_id": 2,
  "finding": "functional_defect",
  "recommendation": "repair",
  "notes": "عيب في الدائرة الكهربائية",
  "checklists": {},
  "inspection_photos": []
}
```

#### بدء الصيانة

```bash
POST /v1/returns/{id}/maintenance/start
Authorization: Bearer <token>

{
  "return_request_id": 1,
  "technician_id": 3,
  "cost_estimate": 150.00
}
```

#### إكمال الصيانة

```bash
POST /v1/returns/{id}/maintenance/complete
Authorization: Bearer <token>

{
  "outcome": "fixed",
  "parts_used": [
    {"part_id": 10, "quantity": 1, "cost": 50.00}
  ],
  "labor_minutes": 120,
  "actual_cost": 150.00,
  "notes": "تم استبدال المكون التالف"
}
```

#### اتخاذ القرار النهائي

```bash
POST /v1/returns/{id}/decide
Authorization: Bearer <token>

{
  "return_request_id": 1,
  "final_decision": "restock",
  "approved_by": 1,
  "reason": "المنتج في حالة جيدة بعد الإصلاح",
  "estimated_value": 500.00
}
```

#### تحويل إلى المخزون

```bash
POST /v1/returns/{id}/transfer-to-inventory
Authorization: Bearer <token>
```

### التقارير

```bash
# KPIs
GET /v1/reports/kpis

# معدل العيوب
GET /v1/reports/defect-rate

# أعلى أسباب الإرجاع
GET /v1/reports/top-reasons?limit=5
```

## 🔐 الأدوار والصلاحيات

| الدور | الصلاحيات |
|------|-----------|
| `admin` | صلاحيات كاملة |
| `inspector` | استلام وفحص المرتجعات |
| `technician` | إدارة أعمال الصيانة |
| `warranty_officer` | إدارة حالات الضمان واتخاذ القرارات |
| `logistics` | تحديث حالة الشحن العكسي |
| `accounting_view` | قراءة التأثيرات المالية فقط |

## 🧪 الاختبارات

```bash
cd apps/prss/backend

# تشغيل جميع الاختبارات
poetry run pytest

# مع التغطية
poetry run pytest --cov=prss --cov-report=html

# اختبارات محددة
poetry run pytest tests/test_returns.py -v

# فتح تقرير التغطية
open htmlcov/index.html
```

## 🔄 سير العمل (Workflow)

```
1. إنشاء طلب إرجاع (Submitted)
   ↓
2. استلام المنتج (Received) → منطقة: Received Returns
   ↓
3. الفحص (Inspecting) → منطقة: Under Inspection
   ↓
   ├─→ عيب فني → ورشة الصيانة (To Repair) → منطقة: Repair Workshop
   │   ↓
   │   إصلاح أو عدم إمكانية الإصلاح
   │   ↓
   └─→ اتخاذ القرار (Awaiting Decision) → منطقة: Awaiting Decision
       ↓
       ├─→ Restock: إعادة للمخزون الرئيسي
       ├─→ Refurbished: بيع كـ Open Box
       ├─→ Scrap: إتلاف → منطقة: Scrap Zone
       ├─→ Return to Supplier: إرجاع للمورد
       └─→ Refund: استرداد مالي للعميل
```

## 📊 مخطط قاعدة البيانات (ERD)

الجداول الرئيسية:

- `return_requests` - طلبات الإرجاع
- `products` - المنتجات (مرجعي)
- `reverse_logistics` - الشحن العكسي
- `inspections` - الفحوصات
- `maintenance_jobs` - أعمال الصيانة
- `warranty_cases` - حالات الضمان
- `warranty_policies` - سياسات الضمان
- `decisions` - القرارات النهائية
- `return_inventory_moves` - حركة المخزون الداخلية
- `accounting_effects` - التأثيرات المحاسبية
- `outbox_events` - أحداث التكامل
- `users` - المستخدمون
- `activity_logs` - سجلات النشاط

## 🔗 التكامل مع الأنظمة الأخرى

### Inventory System

```python
from prss.integration.inventory_client import InventoryClient

client = InventoryClient()
await client.create_transfer({
    "source_zone": "AFTER_SALES_ZONE",
    "destination_zone": "MAIN_WAREHOUSE",
    "product_id": 100,
    "quantity": 1,
    "reference": "AFS-RR-12345",
    "reason": "Return - Non-Defective"
})
```

### Sales System

```python
from prss.integration.sales_client import SalesClient

client = SalesClient()
await client.create_credit_note({
    "order_id": 1000,
    "amount": 500.00,
    "reason": "Product return"
})
```

### Accounting System

```python
from prss.integration.accounting_client import AccountingClient

client = AccountingClient()
await client.post_transaction({
    "type": "loss_writeoff",
    "amount": 100.00,
    "reference": "RR-12345"
})
```

## 📈 مؤشرات الأداء (KPIs)

- **Total Returns**: إجمالي عدد المرتجعات
- **Avg Processing Time**: متوسط وقت المعالجة (ساعات)
- **Defect Rate**: نسبة المنتجات المعيبة
- **Restock Rate**: نسبة المنتجات المعادة للمخزون
- **Refund Rate**: نسبة الاستردادات المالية
- **Top Return Reasons**: أعلى أسباب الإرجاع

## 🛠️ التطوير

### إضافة Migration جديد

```bash
cd apps/prss/backend
poetry run alembic revision --autogenerate -m "Description"
poetry run alembic upgrade head
```

### تشغيل Outbox Processor

```python
from prss.events.outbox import OutboxProcessor
from prss.db import SessionLocal

db = SessionLocal()
processor = OutboxProcessor(db)
processor.process_pending_events(batch_size=10)
```

## 📝 بيانات تجريبية

```bash
cd apps/prss/backend

# تشغيل سكريبت البيانات التجريبية
poetry run python scripts/seed_data.py
```

## 🐛 استكشاف الأخطاء

### مشاكل الاتصال بقاعدة البيانات

```bash
# التحقق من حالة PostgreSQL
pg_isready -h localhost -p 5432

# اتصال يدوي
psql -U prss_user -d prss_db
```

### مشاكل المهاجرات

```bash
# عرض الحالة الحالية
poetry run alembic current

# الرجوع خطوة واحدة
poetry run alembic downgrade -1

# إعادة التطبيق
poetry run alembic upgrade head
```

### مشاكل الأذونات

تأكد من أن المستخدم لديه الدور الصحيح:

```sql
SELECT id, username, role FROM users WHERE username = 'your_username';
```

## 📦 النشر (Deployment)

### Production با Docker

```bash
# بناء الصور
docker-compose -f docker-compose.prod.yml build

# بدء الخدمات
docker-compose -f docker-compose.prod.yml up -d

# عرض السجلات
docker-compose logs -f backend
```

### متغيرات البيئة للإنتاج

```bash
# .env.production
PRSS_DB_URL=postgresql+psycopg://user:pass@db-host:5432/prss_db
PRSS_JWT_SECRET=<strong-random-secret>
DEBUG=false
ENVIRONMENT=production
INVENTORY_API_BASE=https://inventory.yourdomain.com/api
SALES_API_BASE=https://sales.yourdomain.com/api
ACCOUNTING_API_BASE=https://accounting.yourdomain.com/api
```

## 📞 الدعم

للدعم الفني:
- Email: support@tsh.com
- Docs: http://localhost:8001/docs
- Redoc: http://localhost:8001/redoc

## 📄 الترخيص

Proprietary - TSH Company © 2024

## 🎯 خارطة الطريق

### v1.1 (Q1 2024)
- [ ] تصنيف Open-Box وقناة بيع ثانوية
- [ ] تحسين لوحة التحكم بالتحليلات المتقدمة
- [ ] دعم المرفقات الكبيرة (فيديوهات)

### v1.2 (Q2 2024)
- [ ] نموذج AI للفحص البصري الأولي
- [ ] تطبيق موبايل للعملاء
- [ ] إشعارات SMS وEmail

### v1.3 (Q3 2024)
- [ ] بوابة موردين
- [ ] منازعات الشحن
- [ ] تكامل مع شركات الشحن

## 🙏 الشكر

تم تطوير PRSS بواسطة فريق TSH لخدمة أعمال ما بعد البيع بكفاءة وشفافية.
