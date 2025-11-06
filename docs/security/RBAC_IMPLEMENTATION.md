# Role-Based Access Control (RBAC) Implementation

## نظام التحكم بالصلاحيات المبني على الأدوار في FastAPI

---

## 📋 نظرة عامة

تم تطبيق نظام RBAC كامل في TSH ERP بحيث يحمل كل JWT token صلاحيات المستخدم، ويتم التحقق منها عند كل طلب API.

### المزايا الرئيسية

✅ **الأمان**: التحقق من الصلاحيات في كل طلب
✅ **الأداء**: الصلاحيات محفوظة في الـ token (لا حاجة لاستعلام قاعدة البيانات)
✅ **المرونة**: دعم صلاحيات متعددة وأدوار معقدة
✅ **السهولة**: استخدام decorators بسيطة للتحقق

---

## 🏗️ البنية المعمارية

### 1. الصلاحيات في JWT Token

```python
# عند تسجيل الدخول، يُنشأ token يحمل:
{
    "sub": "user@example.com",           # البريد الإلكتروني
    "user_id": 123,                       # معرف المستخدم
    "role": "accountant",                 # الدور
    "permissions": [                       # الصلاحيات
        "accounting.view",
        "accounting.create",
        "accounting.update"
    ],
    "platform": "mobile",                 # المنصة
    "exp": 1706198400,                    # تاريخ الانتهاء
    "iat": 1706196600,                    # تاريخ الإصدار
    "type": "access"                      # نوع الرمز
}
```

### 2. التحقق من الصلاحيات

```python
# عند كل طلب API:
1. استخراج JWT token من Header
2. فك تشفير الـ token
3. قراءة permissions من الـ token
4. التحقق من وجود الصلاحيات المطلوبة
5. إذا كانت الصلاحيات موجودة → السماح بالوصول
6. إذا كانت الصلاحيات ناقصة → رفض الوصول (403)
```

---

## 📝 الملفات المُنشأة والمُعدَّلة

### 1. إنشاء نظام RBAC

**الملف**: `/app/dependencies/rbac.py`

يحتوي على:
- `PermissionChecker`: فحص الصلاحيات
- `RoleChecker`: فحص الأدوار
- `get_current_user_from_token`: استخراج بيانات المستخدم

### 2. تحديث إنشاء الـ Tokens

**الملف**: `/app/routers/auth.py`

**التحديثات**:
```python
# إضافة الصلاحيات إلى access token
access_token = AuthService.create_access_token(
    data={
        "sub": user.email,
        "platform": "mobile",
        "role": user.role.name if user.role else "user",
        "permissions": permissions,  # ← الصلاحيات
        "user_id": user.id
    },
    expires_delta=access_token_expires
)
```

**الأسطر المُعدَّلة**:
- `mobile_login()`: 197-221
- `refresh_token()`: 317-331

### 3. إضافة أمثلة على Accounting Router

**الملف**: `/app/routers/accounting.py`

**أمثلة التطبيق**:
```python
# مثال 1: فحص صلاحية محددة
@router.get("/currencies")
def get_currencies(
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker(["accounting.view"]))  # ← فحص الصلاحية
):
    ...

# مثال 2: فحص صلاحيات متعددة
@router.post("/journal-entries")
def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker([
        "accounting.create",
        "accounting.view"
    ]))
):
    ...

# مثال 3: فحص الدور
@router.delete("/currencies/{id}")
def delete_currency(
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(RoleChecker(["admin", "manager"]))  # ← فقط admin أو manager
):
    ...
```

---

## 🔐 أنواع الصلاحيات المُعرَّفة

### الصلاحيات حسب الوحدات

#### 1. Admin (المدير)
```python
permissions = [
    'admin',                  # صلاحيات إدارية كاملة
    'dashboard.view',
    'users.view',
    'users.create',
    'users.update',
    'users.delete',
    'hr.view',
    'branches.view',
    'warehouses.view',
    'items.view',
    'products.view',
    'inventory.view',
    'customers.view',
    'vendors.view',
    'sales.view',
    'sales.create',
    'purchase.view',
    'accounting.view',
    'pos.view',
    'cashflow.view',
    'migration.view',
    'reports.view',
    'settings.view'
]
```

#### 2. Manager (مدير)
```python
permissions = [
    'dashboard.view',
    'users.view',
    'hr.view',
    'branches.view',
    'warehouses.view',
    'items.view',
    'products.view',
    'inventory.view',
    'customers.view',
    'vendors.view',
    'sales.view',
    'sales.create',
    'purchase.view',
    'accounting.view',
    'pos.view',
    'cashflow.view',
    'reports.view'
]
```

#### 3. Salesperson (مندوب مبيعات)
```python
permissions = [
    'dashboard.view',
    'customers.view',
    'customers.create',
    'customers.update',
    'sales.view',
    'sales.create',
    'sales.update',
    'products.view',
    'inventory.view',
    'pos.view',
    'cashflow.view',
    'reports.view'
]
```

#### 4. Accountant (محاسب)
```python
permissions = [
    'dashboard.view',
    'accounting.view',
    'accounting.create',
    'accounting.update',
    'cashflow.view',
    'reports.view',
    'sales.view',
    'purchase.view'
]
```

#### 5. Inventory (مسؤول مخزون)
```python
permissions = [
    'dashboard.view',
    'items.view',
    'items.create',
    'items.update',
    'products.view',
    'inventory.view',
    'inventory.create',
    'inventory.update',
    'warehouses.view'
]
```

#### 6. Cashier (كاشير)
```python
permissions = [
    'dashboard.view',
    'pos.view',
    'pos.create',
    'sales.view',
    'sales.create',
    'customers.view',
    'products.view'
]
```

---

## 💻 كيفية الاستخدام

### 1. التحقق من صلاحية واحدة

```python
from fastapi import APIRouter, Depends
from app.dependencies.rbac import PermissionChecker

router = APIRouter()

@router.get("/currencies")
def get_currencies(
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker(["accounting.view"]))
):
    """
    هذا الـ endpoint يتطلب صلاحية accounting.view
    إذا لم تكن موجودة → 403 Forbidden
    """
    # الكود هنا
    return data
```

### 2. التحقق من صلاحيات متعددة

```python
@router.post("/journal-entries")
def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker([
        "accounting.view",
        "accounting.create"
    ]))
):
    """
    يتطلب صلاحيتين:
    1. accounting.view
    2. accounting.create

    إذا كانت واحدة ناقصة → 403 Forbidden
    """
    # الكود هنا
    return created_entry
```

### 3. التحقق من الدور (Role)

```python
from app.dependencies.rbac import RoleChecker

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(RoleChecker(["admin"]))
):
    """
    فقط مستخدمي دور admin يمكنهم حذف المستخدمين
    """
    # الكود هنا
    return {"message": "User deleted"}
```

### 4. الحصول على بيانات المستخدم الحالي

```python
from app.dependencies.rbac import get_current_user_from_token

@router.get("/me")
def get_my_profile(
    user: dict = Depends(get_current_user_from_token)
):
    """
    الحصول على بيانات المستخدم من الـ token
    بدون فحص صلاحيات محددة
    """
    return {
        "email": user["email"],
        "role": user["role"],
        "permissions": user["permissions"],
        "user_id": user["user_id"]
    }
```

---

## 🎯 استراتيجية التطبيق على جميع Endpoints

### الخطة

1. **Admin & Settings Endpoints**: تتطلب `admin` role
2. **View Endpoints** (GET): تتطلب `module.view` permission
3. **Create Endpoints** (POST): تتطلب `module.create` permission
4. **Update Endpoints** (PUT/PATCH): تتطلب `module.update` permission
5. **Delete Endpoints** (DELETE): تتطلب `module.delete` أو `admin` role

### مثال: تطبيق على وحدة Accounting

```python
# GET /accounting/currencies
# ✅ Required: accounting.view
@router.get("/currencies")
def get_currencies(user: dict = Depends(PermissionChecker(["accounting.view"]))):
    ...

# POST /accounting/currencies
# ✅ Required: accounting.create
@router.post("/currencies")
def create_currency(user: dict = Depends(PermissionChecker(["accounting.create"]))):
    ...

# PUT /accounting/currencies/{id}
# ✅ Required: accounting.update
@router.put("/currencies/{id}")
def update_currency(user: dict = Depends(PermissionChecker(["accounting.update"]))):
    ...

# DELETE /accounting/currencies/{id}
# ✅ Required: admin role only
@router.delete("/currencies/{id}")
def delete_currency(user: dict = Depends(RoleChecker(["admin"]))):
    ...
```

---

## 🔍 اختبار RBAC

### 1. اختبار عبر cURL

#### تسجيل دخول
```bash
curl -X POST http://192.168.68.51:8000/api/auth/login/mobile \
  -H "Content-Type: application/json" \
  -d '{
    "email": "accountant@tsh.com",
    "password": "password123"
  }'
```

**النتيجة**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": 5,
    "email": "accountant@tsh.com",
    "role": "Accountant",
    "permissions": [
      "dashboard.view",
      "accounting.view",
      "accounting.create",
      "accounting.update",
      "reports.view"
    ]
  }
}
```

#### استخدام الـ Token
```bash
# طلب ناجح - المستخدم لديه accounting.view
curl -X GET http://192.168.68.51:8000/api/accounting/currencies \
  -H "Authorization: Bearer eyJ..."
```

**النتيجة**: ✅ 200 OK

```bash
# طلب مرفوض - المستخدم ليس لديه users.view
curl -X GET http://192.168.68.51:8000/api/users \
  -H "Authorization: Bearer eyJ..."
```

**النتيجة**: ❌ 403 Forbidden
```json
{
  "detail": "Missing required permissions: users.view"
}
```

### 2. اختبار من Flutter App

```dart
// Login
final loginResponse = await apiService.post('/auth/login/mobile', data: {
  'email': 'salesperson@tsh.com',
  'password': 'password123'
});

// Token محفوظ تلقائياً في apiService

// طلب الصلاحيات من الـ token
final permissions = loginResponse.data['user']['permissions'];
print('User permissions: $permissions');
// Output: [dashboard.view, customers.view, customers.create, sales.view, sales.create]

// الطلبات التالية ستُرسل مع الـ token تلقائياً
// إذا لم تكن لديك الصلاحية → ستحصل على 403
```

---

## ⚠️ رسائل الخطأ

### 1. Token غير صالح
```json
{
  "detail": "Could not validate credentials"
}
```
**Status Code**: 401 Unauthorized

**الأسباب**:
- Token منتهي الصلاحية
- Token غير صحيح
- Token لا يحتوي على البيانات المطلوبة

### 2. صلاحيات ناقصة
```json
{
  "detail": "Missing required permissions: accounting.create, accounting.update"
}
```
**Status Code**: 403 Forbidden

**الأسباب**:
- المستخدم لا يملك الصلاحيات المطلوبة

### 3. دور غير مسموح
```json
{
  "detail": "Access denied. Required role: admin, manager"
}
```
**Status Code**: 403 Forbidden

**الأسباب**:
- دور المستخدم لا يطابق الأدوار المطلوبة

---

## 🔄 دورة حياة الـ Token مع RBAC

```
1. User logs in
   ↓
2. Backend creates token with permissions
   {
     "sub": "user@example.com",
     "role": "accountant",
     "permissions": ["accounting.view", "accounting.create"]
   }
   ↓
3. Token saved in secure storage (mobile) or localStorage (web)
   ↓
4. User makes API request
   GET /api/accounting/currencies
   Authorization: Bearer eyJ...
   ↓
5. PermissionChecker dependency runs
   - Decodes token
   - Extracts permissions
   - Checks if "accounting.view" exists
   ↓
6a. Permission exists → Allow access (200 OK)
6b. Permission missing → Deny access (403 Forbidden)
   ↓
7. After 30 minutes, access token expires
   ↓
8. App automatically refreshes token
   POST /api/auth/refresh
   ↓
9. New token created with same permissions
   ↓
10. User continues working seamlessly
```

---

## 📊 مقارنة بين الطرق المختلفة

### قبل RBAC (السابق)

```python
@router.get("/currencies")
def get_currencies(db: Session = Depends(get_db)):
    # ❌ لا يوجد فحص صلاحيات
    # أي مستخدم يمكنه الوصول
    return service.get_currencies()
```

**المشاكل**:
- ❌ لا يوجد أمان
- ❌ أي مستخدم يمكنه الوصول لأي endpoint
- ❌ لا يمكن التحكم في الصلاحيات

### بعد RBAC (الحالي)

```python
@router.get("/currencies")
def get_currencies(
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker(["accounting.view"]))
):
    # ✅ فحص تلقائي للصلاحيات
    # فقط المستخدمين الذين لديهم accounting.view
    return service.get_currencies()
```

**المزايا**:
- ✅ أمان كامل
- ✅ فحص تلقائي للصلاحيات
- ✅ رسائل خطأ واضحة
- ✅ سهولة التطبيق

---

## 🚀 التوسع المستقبلي

### 1. صلاحيات ديناميكية

بدلاً من تحديد الصلاحيات في الكود:
```python
# حالياً
permissions = {
    'admin': ['admin', 'users.view', 'users.create', ...]
}

# مستقبلاً: من قاعدة البيانات
# جدول: role_permissions
# عمود: role_id | permission_name
```

### 2. صلاحيات على مستوى البيانات (Data-Level)

```python
# مثال: مندوب مبيعات يرى فقط عملاءه
@router.get("/customers")
def get_customers(
    user: dict = Depends(PermissionChecker(["customers.view"])),
    db: Session = Depends(get_db)
):
    # فلترة حسب مندوب المبيعات
    if user["role"] == "salesperson":
        return service.get_customers_by_salesperson(user["user_id"])
    else:
        return service.get_all_customers()
```

### 3. تدقيق الصلاحيات (Audit Log)

```python
# تسجيل كل محاولة وصول
def log_permission_check(user: dict, permission: str, allowed: bool):
    audit_log = {
        "user_id": user["user_id"],
        "permission": permission,
        "allowed": allowed,
        "timestamp": datetime.now()
    }
    # حفظ في جدول audit_logs
```

---

## 📚 ملخص الملفات

### ملفات جديدة
1. `/app/dependencies/rbac.py` - نظام RBAC الكامل
2. `/app/dependencies/__init__.py` - init file للمجلد

### ملفات معدلة
1. `/app/services/auth_service.py` - إضافة `iat` للـ token
2. `/app/routers/auth.py` - إضافة صلاحيات للـ tokens
3. `/app/routers/accounting.py` - أمثلة التطبيق

---

## ✅ الحالة

**✅ تم التنفيذ بنجاح**

**جاهز للاستخدام**

**يشمل**:
- ✅ الصلاحيات في JWT tokens
- ✅ PermissionChecker dependency
- ✅ RoleChecker dependency
- ✅ أمثلة في accounting router
- ✅ وثائق كاملة

---

**تاريخ التحديث**: 2025-01-24

**المطور**: TSH ERP Development Team
