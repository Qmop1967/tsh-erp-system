# PRSS - دليل البدء السريع ⚡
# Quick Start Guide

## 🚀 البدء في 5 دقائق

### الطريقة 1: Docker (الأسهل والموصى به)

```bash
# 1. الانتقال إلى مجلد PRSS
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/apps/prss

# 2. إنشاء ملف .env (اختياري - يوجد إعدادات افتراضية)
cp backend/.env.example backend/.env

# 3. بدء جميع الخدمات
docker-compose up -d

# 4. انتظر 30-60 ثانية للتهيئة الأولية

# 5. تحميل بيانات تجريبية
docker-compose exec backend poetry run python scripts/seed_data.py

# 6. افتح المتصفح
# API Documentation: http://localhost:8001/docs
# Web Dashboard:     http://localhost:5174
```

### تسجيل الدخول:
```
Username: admin
Password: admin123
```

---

## 🖥️ الطريقة 2: تشغيل محلي (للتطوير)

### المتطلبات:
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+
- Poetry

### الخطوات:

#### 1. إعداد قاعدة البيانات
```bash
# إنشاء قاعدة بيانات
createdb prss_db

# أو عبر psql
psql -U postgres
CREATE DATABASE prss_db;
\q
```

#### 2. Backend
```bash
cd apps/prss/backend

# تثبيت Poetry (إذا لم يكن مثبتاً)
curl -sSL https://install.python-poetry.org | python3 -

# تثبيت المكتبات
poetry install

# تشغيل المهاجرات
poetry run alembic upgrade head

# تحميل بيانات تجريبية
poetry run python scripts/seed_data.py

# تشغيل الخادم
poetry run uvicorn prss.main:app --reload --port 8001
```

#### 3. Frontend
```bash
# في نافذة terminal جديدة
cd apps/prss/web-admin

# تثبيت المكتبات
npm install

# تشغيل خادم التطوير
npm run dev
```

---

## 🧪 تجربة النظام

### 1. فتح Swagger UI
```
http://localhost:8001/docs
```

### 2. تسجيل الدخول
```bash
curl -X POST http://localhost:8001/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

سيعطيك Token على الشكل:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. إنشاء طلب إرجاع
في Swagger UI:
1. اضغط على "Authorize" في الأعلى
2. أدخل Token: `Bearer <token>`
3. اذهب إلى `POST /v1/returns`
4. اضغط "Try it out"
5. أدخل:
```json
{
  "customer_id": 1001,
  "sales_order_id": 5000,
  "product_id": 1,
  "serial_number": "SN-TEST-12345",
  "reason_code": "defective",
  "reason_description": "المنتج لا يعمل"
}
```

### 4. فتح Web Dashboard
```
http://localhost:5174
```
Login: `admin` / `admin123`

---

## 📊 الحسابات التجريبية

| المستخدم | كلمة المرور | الدور |
|----------|-------------|-------|
| admin | admin123 | Administrator |
| inspector1 | inspect123 | Inspector |
| technician1 | tech123 | Technician |
| warranty1 | warranty123 | Warranty Officer |
| logistics1 | logistics123 | Logistics |

---

## 🔍 التحقق من حالة الخدمات

### Docker:
```bash
# عرض الخدمات
docker-compose ps

# عرض السجلات
docker-compose logs -f backend
docker-compose logs -f web-admin

# إعادة تشغيل خدمة
docker-compose restart backend
```

### Local:
```bash
# Backend health check
curl http://localhost:8001/health

# Database connection
pg_isready -h localhost -p 5432
```

---

## 🧪 تشغيل الاختبارات

```bash
cd apps/prss/backend

# جميع الاختبارات
poetry run pytest

# مع التغطية
poetry run pytest --cov=prss --cov-report=html

# فتح تقرير التغطية
open htmlcov/index.html
```

---

## 🛑 إيقاف النظام

### Docker:
```bash
# إيقاف الخدمات
docker-compose down

# إيقاف وحذف البيانات
docker-compose down -v
```

### Local:
```bash
# Ctrl+C في كل terminal
```

---

## 🚨 حل المشاكل الشائعة

### مشكلة: Port 8001 مستخدم
```bash
# معرفة العملية
lsof -ti:8001

# إيقافها
kill -9 $(lsof -ti:8001)
```

### مشكلة: قاعدة البيانات غير متصلة
```bash
# تحقق من PostgreSQL
pg_isready

# إعادة تشغيل PostgreSQL (macOS)
brew services restart postgresql@14
```

### مشكلة: Migration fails
```bash
# حذف جميع الجداول وإعادة إنشائها
poetry run alembic downgrade base
poetry run alembic upgrade head
```

### مشكلة: Cannot import prss
```bash
# تأكد من تشغيل الأمر في المجلد الصحيح
cd apps/prss/backend

# تفعيل البيئة الافتراضية
poetry shell

# إعادة التثبيت
poetry install
```

---

## 📚 الخطوات التالية

1. ✅ **اقرأ README.md** للمزيد من التفاصيل
2. ✅ **افتح JOURNEY_EXAMPLE.json** لمشاهدة مثال كامل
3. ✅ **اقرأ DELIVERY_SUMMARY.md** لفهم البنية الكاملة
4. ✅ **جرب API endpoints** عبر Swagger UI
5. ✅ **استكشف Web Dashboard**
6. ✅ **اقرأ الكود** لفهم التفاصيل التقنية

---

## 🎯 أول مهمة مقترحة

جرب إنشاء رحلة كاملة لطلب إرجاع:

1. إنشاء طلب إرجاع (POST /v1/returns)
2. استلام المنتج (POST /v1/returns/{id}/receive)
3. إجراء فحص (POST /v1/returns/{id}/inspect)
4. بدء صيانة (POST /v1/returns/{id}/maintenance/start)
5. إكمال صيانة (POST /v1/returns/{id}/maintenance/complete)
6. اتخاذ قرار (POST /v1/returns/{id}/decide)
7. تحويل للمخزون (POST /v1/returns/{id}/transfer-to-inventory)

---

## 💡 نصائح مفيدة

- **استخدم Swagger UI** للتجربة السريعة
- **افتح Developer Tools** في المتصفح لمراقبة API calls
- **اقرأ السجلات** عند حدوث مشاكل
- **استخدم Thunder Client** أو **Postman** لاختبار API

---

## 📞 المساعدة

إذا واجهت مشاكل:
1. تحقق من السجلات: `docker-compose logs -f backend`
2. اقرأ قسم "استكشاف الأخطاء" في README.md
3. تأكد من تشغيل جميع الخدمات: `docker-compose ps`

---

**استمتع باستخدام PRSS! 🚀**
