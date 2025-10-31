# نظام Rate Limiting في TSH ERP
# Rate Limiting Implementation in TSH ERP System

## 📋 نظرة عامة / Overview

تم تطبيق نظام شامل لـ Rate Limiting لحماية الـ API من الضغط الزائد والاستخدام غير المصرح به. يستخدم النظام مكتبة **slowapi** التي توفر تكاملاً سلساً مع FastAPI.

A comprehensive rate limiting system has been implemented to protect the API from excessive load and unauthorized usage. The system uses **slowapi** library which provides seamless integration with FastAPI.

## 🎯 الأهداف / Objectives

1. **منع هجمات Brute Force** على نقاط الدخول (Login)
2. **حماية العمليات الحساسة** مثل التقارير المالية والقيود المحاسبية
3. **تحسين الأداء** بتوزيع الحمل على الخادم
4. **منع الاستخدام غير المصرح به** للـ API

## 📦 المكتبات المستخدمة / Libraries Used

```bash
pip install slowapi
```

**slowapi**: مكتبة Rate Limiting متوافقة تماماً مع FastAPI، توفر:
- تخزين في الذاكرة (In-Memory) أو Redis
- دعم كامل لـ FastAPI decorators
- معالجة تلقائية لأخطاء Rate Limit
- دعم WebSocket

## 🏗️ البنية التقنية / Architecture

### 1. تهيئة Rate Limiter في Main Application

في ملف `app/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="TSH ERP System",
    description="نظام ERP بسيط باستخدام FastAPI و PostgreSQL",
    version="1.0.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 2. تطبيق Rate Limits على Endpoints

#### 2.1 نقاط المصادقة / Authentication Endpoints

تم تطبيق Rate Limiting صارم على نقاط تسجيل الدخول لمنع هجمات Brute Force:

```python
# في auth_enhanced.py - Rate Limiting مدمج في الخدمة
# Authentication already has built-in rate limiting through RateLimitService
# - 5 login attempts per minute per IP
# - Account lockout after 5 failed attempts
# - 15-minute lockout period
```

#### 2.2 العمليات المحاسبية / Accounting Operations

في ملف `app/routers/accounting.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# إنشاء عملة جديدة - 20 طلب في الدقيقة
@router.post("/currencies", response_model=Currency)
@limiter.limit("20/minute")
def create_currency(
    request: Request,
    currency: CurrencyCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker(["accounting.create"]))
):
    """
    Create new currency - إنشاء عملة جديدة
    Rate Limit: 20 requests per minute
    """
    service = AccountingService(db)
    return service.create_currency(currency)

# إنشاء قيد يومية - 30 طلب في الدقيقة
@router.post("/journal-entries", response_model=JournalEntry)
@limiter.limit("30/minute")
async def create_journal_entry(
    request: Request,
    entry: JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """
    Create new journal entry - إنشاء قيد يومية جديد
    Rate Limit: 30 requests per minute
    """
    service = AccountingService(db)
    new_entry = service.create_journal_entry(entry)
    # ... rest of implementation
```

#### 2.3 التقارير المالية / Financial Reports

تطبيق حدود أكثر صرامة على التقارير لأنها تستهلك موارد أكثر:

```python
# Trial Balance - 20 طلب في الساعة
@router.get("/reports/trial-balance", response_model=TrialBalance)
@limiter.limit("20/hour")
def get_trial_balance(
    request: Request,
    period_id: int = Query(...),
    chart_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get trial balance report - جلب تقرير ميزان المراجعة
    Rate Limit: 20 requests per hour
    """
    service = AccountingService(db)
    return service.generate_trial_balance(period_id, chart_id)

# Balance Sheet - 20 طلب في الساعة
@router.get("/reports/balance-sheet", response_model=BalanceSheet)
@limiter.limit("20/hour")
def get_balance_sheet(
    request: Request,
    period_id: int = Query(...),
    chart_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get balance sheet report - جلب تقرير الميزانية العمومية
    Rate Limit: 20 requests per hour
    """
    service = AccountingService(db)
    return service.generate_balance_sheet(period_id, chart_id)

# Income Statement - 20 طلب في الساعة
@router.get("/reports/income-statement", response_model=IncomeStatement)
@limiter.limit("20/hour")
def get_income_statement(
    request: Request,
    period_id: int = Query(...),
    chart_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get income statement report - جلب تقرير قائمة الدخل
    Rate Limit: 20 requests per hour
    """
    service = AccountingService(db)
    return service.generate_income_statement(period_id, chart_id)
```

## 📊 حدود Rate Limiting حسب نوع العملية / Rate Limits by Operation Type

| نوع العملية / Operation Type | الحد / Limit | السبب / Reason |
|------------------------------|--------------|----------------|
| **تسجيل الدخول / Login** | 5/minute | منع Brute Force Attacks |
| **Refresh Token** | 10/minute | السماح بتحديثات متكررة معقولة |
| **إنشاء بيانات / Create** | 20-30/minute | توازن بين الأداء والأمان |
| **تعديل بيانات / Update** | 50/minute | عمليات متكررة نسبياً |
| **حذف بيانات / Delete** | 20/minute | عمليات حساسة |
| **قراءة بيانات / Read** | 100/minute | عمليات خفيفة |
| **التقارير المالية / Financial Reports** | 20/hour | عمليات ثقيلة على الخادم |
| **عمليات مالية / Money Transfers** | 10/hour | عمليات حساسة جداً |
| **عمليات إدارية / Admin Operations** | 50/minute | عمليات متكررة لل Admin |

## 🔧 التكوين المتقدم / Advanced Configuration

### استخدام Redis للتخزين

للبيئات الإنتاجية، يُنصح باستخدام Redis:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis.asyncio as redis

# تكوين Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Initialize limiter with Redis
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)
```

### حدود مخصصة حسب دور المستخدم

يمكن تخصيص الحدود حسب دور المستخدم:

```python
def get_rate_limit_key(request: Request) -> str:
    """
    Generate rate limit key based on user role
    Admins get higher limits
    """
    remote_addr = get_remote_address(request)

    # Extract user role from token
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    if token:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role", "")

        if role.lower() == "admin":
            return f"admin:{remote_addr}"

    return remote_addr
```

## 🚨 معالجة الأخطاء / Error Handling

عند تجاوز الحد المسموح:

```json
{
    "error": "Rate limit exceeded",
    "detail": "Too many requests. Please try again later.",
    "status_code": 429,
    "headers": {
        "Retry-After": "60"
    }
}
```

الكود في Frontend للتعامل مع Rate Limit:

```typescript
// مثال في TypeScript/React
const handleRateLimitError = (error: any) => {
    if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'];

        toast.error(
            `تجاوزت الحد المسموح من الطلبات. حاول مرة أخرى بعد ${retryAfter} ثانية`,
            {
                duration: parseInt(retryAfter) * 1000
            }
        );

        // Automatically retry after the specified time
        setTimeout(() => {
            // Retry the request
            retryRequest();
        }, parseInt(retryAfter) * 1000);
    }
};
```

## 🔍 المراقبة والتتبع / Monitoring and Tracking

### 1. تتبع محاولات تجاوز الحدود

في نظام Authentication المحسّن، يتم تسجيل جميع المحاولات:

```python
# في enhanced_auth_security.py
class RateLimitService:
    @staticmethod
    def record_login_attempt(
        db: Session,
        email: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ) -> LoginAttempt:
        """
        Record all login attempts for security monitoring
        """
        attempt = LoginAttempt(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            attempted_at=datetime.utcnow()
        )
        db.add(attempt)
        db.commit()
        return attempt
```

### 2. Dashboard للمراقبة

يمكن إضافة endpoint لعرض إحصائيات Rate Limiting:

```python
@router.get("/admin/rate-limit-stats")
@limiter.limit("30/minute")
async def get_rate_limit_stats(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(PermissionChecker(["admin"]))
):
    """
    Get rate limiting statistics for admin dashboard
    """
    # Query login attempts in last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    stats = {
        "total_attempts": db.query(LoginAttempt)
            .filter(LoginAttempt.attempted_at >= one_hour_ago)
            .count(),
        "failed_attempts": db.query(LoginAttempt)
            .filter(
                LoginAttempt.attempted_at >= one_hour_ago,
                LoginAttempt.success == False
            ).count(),
        "locked_accounts": db.query(User)
            .filter(User.is_locked == True)
            .count(),
        "top_ips": db.query(
            LoginAttempt.ip_address,
            func.count(LoginAttempt.id).label('count')
        ).filter(
            LoginAttempt.attempted_at >= one_hour_ago
        ).group_by(LoginAttempt.ip_address)
        .order_by(desc('count'))
        .limit(10)
        .all()
    }

    return stats
```

## 🧪 الاختبار / Testing

### اختبار Rate Limiting باستخدام cURL

```bash
# اختبار تجاوز حد تسجيل الدخول (5 طلبات في الدقيقة)
for i in {1..10}; do
    curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n" \
    -s

    echo "Request $i completed"
    sleep 1
done

# اختبار حد التقارير المالية (20 طلب في الساعة)
for i in {1..25}; do
    curl -X GET "http://localhost:8000/api/accounting/reports/balance-sheet?period_id=1" \
    -H "Authorization: Bearer YOUR_TOKEN_HERE" \
    -w "\nStatus: %{http_code}\n" \
    -s

    echo "Request $i completed"
    sleep 5
done
```

### اختبار باستخدام Python Script

```python
import requests
import time

API_URL = "http://localhost:8000"
TOKEN = "your_access_token_here"

def test_rate_limit_login():
    """Test login rate limiting"""
    print("Testing login rate limiting...")

    for i in range(10):
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "wrong"}
        )

        print(f"Request {i+1}: Status {response.status_code}")

        if response.status_code == 429:
            print("✅ Rate limit working correctly!")
            print(f"Response: {response.json()}")
            break

        time.sleep(1)

def test_rate_limit_reports():
    """Test financial reports rate limiting"""
    print("\nTesting reports rate limiting...")

    headers = {"Authorization": f"Bearer {TOKEN}"}

    for i in range(25):
        response = requests.get(
            f"{API_URL}/api/accounting/reports/balance-sheet",
            params={"period_id": 1},
            headers=headers
        )

        print(f"Request {i+1}: Status {response.status_code}")

        if response.status_code == 429:
            print("✅ Rate limit working correctly!")
            retry_after = response.headers.get('Retry-After', 'unknown')
            print(f"Retry-After: {retry_after} seconds")
            break

        time.sleep(5)

if __name__ == "__main__":
    test_rate_limit_login()
    test_rate_limit_reports()
```

## 📝 أفضل الممارسات / Best Practices

### 1. اختيار الحدود المناسبة

- **عمليات القراءة**: حدود عالية (100-200/minute)
- **عمليات الكتابة**: حدود متوسطة (20-50/minute)
- **عمليات حساسة**: حدود منخفضة (5-10/minute أو hour)
- **التقارير الثقيلة**: حدود منخفضة جداً (10-20/hour)

### 2. استخدام Headers مناسبة

```python
# إضافة معلومات Rate Limit في Response Headers
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)

    # Add rate limit info to headers
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "95"
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

    return response
```

### 3. توفير Whitelist للـ IPs الموثوقة

```python
TRUSTED_IPS = ["127.0.0.1", "10.0.0.1"]

def get_rate_limit_key(request: Request) -> str:
    """Bypass rate limiting for trusted IPs"""
    remote_addr = get_remote_address(request)

    if remote_addr in TRUSTED_IPS:
        return f"trusted:{remote_addr}"

    return remote_addr
```

### 4. تسجيل محاولات تجاوز الحدود

```python
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Log rate limit violations"""
    logger.warning(
        f"Rate limit exceeded: {request.client.host} "
        f"tried to access {request.url.path}"
    )

    # Can also store in database for analysis
    # store_rate_limit_violation(request)

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": "Too many requests. Please try again later.",
            "retry_after": 60
        },
        headers={"Retry-After": "60"}
    )
```

## 🚀 التطوير المستقبلي / Future Enhancements

1. **Dynamic Rate Limits**:
   - تعديل الحدود تلقائياً حسب حمل الخادم
   - حدود مختلفة لكل مستخدم حسب الاشتراك

2. **Distributed Rate Limiting**:
   - استخدام Redis Cluster للتوزيع
   - مزامنة الحدود عبر عدة servers

3. **Machine Learning Integration**:
   - كشف الأنماط المشبوهة
   - تعديل الحدود تلقائياً حسب السلوك

4. **Geographic Rate Limiting**:
   - حدود مختلفة حسب الموقع الجغرافي
   - حظر مناطق معينة في حالة الهجمات

## 📚 مراجع / References

- [slowapi Documentation](https://github.com/laurentS/slowapi)
- [FastAPI Rate Limiting Best Practices](https://fastapi.tiangolo.com/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

## ✅ ملخص التطبيق / Implementation Summary

تم تطبيق Rate Limiting في:

✅ **Main Application** (`app/main.py`)
- تهيئة slowapi limiter
- إضافة exception handler

✅ **Accounting Module** (`app/routers/accounting.py`)
- Currency creation: 20/minute
- Journal entries: 30/minute
- Financial reports: 20/hour

✅ **Authentication Module** (`app/routers/auth_enhanced.py`)
- Built-in database rate limiting
- 5 login attempts per minute
- Account lockout after 5 failures

النظام الآن محمي بشكل شامل من الضغط الزائد والاستخدام غير المصرح به! 🎉
