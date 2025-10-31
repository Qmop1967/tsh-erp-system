# Flutter Apps Backend Connection Guide

**How 11 Flutter Mobile Apps Connect to FastAPI Backend & PostgreSQL Database**

---

## 🎯 Overview

The TSH ERP system uses a **3-layer architecture**:

```
Flutter Apps (Mobile) → FastAPI Backend (API Server) → PostgreSQL Database
```

All 11 Flutter apps connect to the **same centralized FastAPI backend** running on your Mac, which then connects to a **single PostgreSQL database** (`erp_db`).

---

## 📱 Flutter Apps Architecture

### Current Flutter Apps (11 Total)

1. **01_tsh_admin_app** - Admin Dashboard & Security Management
2. **02_tsh_admin_security** - Enhanced Security & MFA
3. **03_tsh_accounting_app** - Accounting & Financial Management
4. **04_tsh_hr_app** - HR & Employee Management
5. **05_tsh_inventory_app** - Inventory & Warehouse Management
6. **06_tsh_salesperson_app** - Salesperson & GPS Tracking
7. **07_tsh_retail_sales_app** - Retail POS Sales
8. **08_tsh_partner_network_app** - Partner Salesmen Network
9. **09_tsh_wholesale_client_app** - Wholesale Client Portal
10. **10_tsh_consumer_app** - Consumer E-commerce App
11. **11_tsh_aso_app** - After-Sales Operations (ASO)

---

## 🔌 Connection Configuration

### Backend Server Details

**FastAPI Server:**
- **Host**: `192.168.68.51` (Your Mac's local IP address)
- **Port**: `8000`
- **Base URL**: `http://192.168.68.51:8000`
- **API Prefix**: `/api`
- **Full API URL**: `http://192.168.68.51:8000/api`

**Running Command:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Why `--host 0.0.0.0`?**
- Allows access from other devices on the network (iPhones, iPads, Android devices)
- Without this, server would only be accessible on `localhost` (Mac only)

---

## 📂 Flutter App Configuration Files

### Two Types of API Configuration

Each Flutter app has **one of two** configuration patterns:

#### Pattern 1: `app_config.dart` (Recommended)
**File Location:** `lib/config/app_config.dart`

**Example:** `03_tsh_accounting_app/lib/config/app_config.dart`

```dart
class AppConfig {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://192.168.68.51:8000';

  // API Endpoints
  static const String authEndpoint = '/api/auth/login';
  static const String accountingEndpoint = '/api/accounting';

  // Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000;

  // Local Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userIdKey = 'user_id';

  // Full API URLs
  static String get authUrl => '$baseUrl$authEndpoint';
  static String get accountingUrl => '$baseUrl$accountingEndpoint';
}
```

**Apps Using This Pattern:**
- `03_tsh_accounting_app`
- `04_tsh_hr_app`
- `06_tsh_salesperson_app`
- `07_tsh_retail_sales_app`
- `08_tsh_partner_network_app`
- `09_tsh_wholesale_client_app`
- `11_tsh_aso_app`

#### Pattern 2: `api_service.dart` (Simple)
**File Location:** `lib/services/api_service.dart`

**Example:** `01_tsh_admin_app/lib/services/api_service.dart`

```dart
class ApiService {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://192.168.68.51:8000/api';

  static Map<String, String> _getHeaders({String? token}) {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }

    return headers;
  }

  static Future<Map<String, dynamic>> post({
    required String endpoint,
    required Map<String, dynamic> data,
    String? token,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final response = await http.post(
      uri,
      headers: _getHeaders(token: token),
      body: json.encode(data),
    );
    return json.decode(response.body);
  }
}
```

**Apps Using This Pattern:**
- `01_tsh_admin_app`
- `05_tsh_inventory_app`
- `10_tsh_consumer_app`

---

## 🔄 Complete Request Flow

### Example: User Login from Accounting App

```
┌─────────────────────────────────────────────────────────────────────┐
│ Step 1: User enters credentials on Flutter App                     │
│ App: 03_tsh_accounting_app (iPhone)                               │
│ Screen: LoginScreen                                                │
│ User inputs: email="user@example.com", password="pass123"         │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 2: API Service prepares HTTP request                          │
│ File: lib/services/api_service.dart                               │
│                                                                     │
│ final response = await http.post(                                  │
│   Uri.parse('http://192.168.68.51:8000/api/auth/login'),          │
│   headers: {'Content-Type': 'application/json'},                  │
│   body: json.encode({                                              │
│     'email': 'user@example.com',                                   │
│     'password': 'pass123'                                          │
│   })                                                               │
│ );                                                                 │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ HTTP POST Request
                         │ Over WiFi Network (192.168.68.x)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 3: FastAPI receives request                                   │
│ Server: Mac (192.168.68.51:8000)                                  │
│ File: app/routers/auth_enhanced.py                                │
│                                                                     │
│ @router.post("/auth/login")                                        │
│ async def login(                                                   │
│     credentials: LoginRequest,                                     │
│     db: Session = Depends(get_db)                                 │
│ ):                                                                 │
│     # Validate credentials                                         │
│     # Check rate limiting                                          │
│     # Generate JWT token                                           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 4: FastAPI queries PostgreSQL database                        │
│ File: app/db/database.py                                          │
│ Database: erp_db @ localhost:5432                                 │
│                                                                     │
│ SELECT * FROM users                                                │
│ WHERE email = 'user@example.com'                                   │
│ AND password_hash = hash('pass123')                                │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 5: PostgreSQL returns user data                               │
│ Result: User found, valid credentials                              │
│ Returns: user_id, email, role, permissions                         │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 6: FastAPI generates JWT token                                │
│ Token contains: user_id, email, role, permissions, expiry         │
│                                                                     │
│ Response JSON:                                                      │
│ {                                                                   │
│   "access_token": "eyJhbGciOiJIUzI1NiIs...",                       │
│   "token_type": "bearer",                                          │
│   "user_id": 5,                                                    │
│   "email": "user@example.com",                                     │
│   "role": "accountant"                                             │
│ }                                                                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ HTTP 200 OK Response
                         │ JSON payload
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 7: Flutter app receives response                              │
│ File: lib/services/api_service.dart                               │
│                                                                     │
│ if (response.statusCode == 200) {                                  │
│   final data = json.decode(response.body);                         │
│   _token = data['access_token'];                                   │
│   await prefs.setString('auth_token', _token!);                    │
│   // Navigate to home screen                                       │
│ }                                                                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 8: User is logged in, can now make authenticated requests    │
│ All future requests include:                                       │
│ headers: {                                                         │
│   'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...'               │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Authentication & Security

### JWT Token Flow

1. **Login** → Server returns JWT token
2. **Store Token** → Saved in `SharedPreferences` (local storage)
3. **Include Token** → All API requests include `Authorization: Bearer <token>`
4. **Token Validation** → Server validates token on every request
5. **Token Refresh** → Automatic refresh when token expires (see `TOKEN_REFRESH_FLOW.md`)

### Token Structure

```dart
// Flutter stores token
final prefs = await SharedPreferences.getInstance();
await prefs.setString('auth_token', token);

// Flutter includes token in requests
headers: {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...'
}
```

### Backend Validates Token

```python
# FastAPI validates JWT token
@router.get("/api/accounting/currencies")
async def get_currencies(
    current_user: User = Depends(get_current_user)
):
    # get_current_user validates JWT token
    # Extracts user_id, role, permissions
    # Returns user object if valid, raises 401 if invalid
```

---

## 📡 Network Communication

### HTTP Methods Used

| Method | Purpose | Example Endpoint |
|--------|---------|------------------|
| `GET` | Retrieve data | `/api/accounting/currencies` |
| `POST` | Create new record | `/api/accounting/journal-entries` |
| `PUT` | Update record | `/api/accounting/currencies/1` |
| `DELETE` | Delete record | `/api/accounting/currencies/1` |

### Request/Response Format

**Request (Flutter → FastAPI):**
```dart
final response = await http.get(
  Uri.parse('http://192.168.68.51:8000/api/accounting/currencies'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...'
  },
);
```

**Response (FastAPI → Flutter):**
```json
[
  {
    "id": 1,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$",
    "is_active": true
  },
  {
    "id": 2,
    "code": "IQD",
    "name": "Iraqi Dinar",
    "symbol": "د.ع",
    "is_active": true
  }
]
```

**Flutter parses response:**
```dart
if (response.statusCode == 200) {
  final List data = json.decode(response.body);
  List<Currency> currencies = data
    .map((item) => Currency.fromJson(item))
    .toList();
}
```

---

## 🛠️ API Service Implementation Patterns

### Pattern 1: Singleton API Service (Recommended)

**File:** `lib/services/api_service.dart`

```dart
class ApiService {
  // Singleton pattern - only one instance
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  String? _token;

  // Initialize from local storage
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(AppConfig.tokenKey);
  }

  // Get headers with token
  Future<Map<String, String>> _getHeaders() async {
    if (_token == null) await init();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (_token != null) 'Authorization': 'Bearer $_token',
    };
  }

  // Generic GET request
  Future<List<T>> getList<T>({
    required String endpoint,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${AppConfig.baseUrl}$endpoint'),
      headers: headers,
    ).timeout(Duration(milliseconds: AppConfig.connectionTimeout));

    if (response.statusCode == 200) {
      final List data = json.decode(response.body);
      return data.map((item) => fromJson(item)).toList();
    }
    throw Exception('Failed to load data');
  }

  // Example usage
  Future<List<Currency>> getCurrencies() async {
    return await getList<Currency>(
      endpoint: '/api/accounting/currencies',
      fromJson: (json) => Currency.fromJson(json),
    );
  }
}
```

### Pattern 2: Static API Service (Simple)

**File:** `lib/services/api_service.dart`

```dart
class ApiService {
  static const String baseUrl = 'http://192.168.68.51:8000/api';

  static Future<Map<String, dynamic>> post({
    required String endpoint,
    required Map<String, dynamic> data,
    String? token,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: json.encode(data),
    );
    return json.decode(response.body);
  }
}

// Usage in screens
final result = await ApiService.post(
  endpoint: '/auth/login',
  data: {'email': email, 'password': password},
);
```

---

## 🧪 Testing Connection

### 1. Check Backend is Running

```bash
# From Mac terminal
curl http://localhost:8000/health

# Expected response:
{"status":"healthy","message":"النظام يعمل بشكل طبيعي"}
```

### 2. Check Backend is Accessible from Network

```bash
# From Mac terminal
curl http://192.168.68.51:8000/health

# Expected response:
{"status":"healthy","message":"النظام يعمل بشكل طبيعي"}
```

### 3. Test from iPhone/iPad

**Use Safari on iPhone:**
```
http://192.168.68.51:8000/health
```

If you see the JSON response, your Flutter apps can connect!

### 4. Test Login Endpoint

```bash
curl -X POST http://192.168.68.51:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Expected response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "admin@example.com"
}
```

---

## ⚙️ Configuration Checklist

### ✅ Backend Configuration

- [x] **FastAPI running with `--host 0.0.0.0`** ✓
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

- [x] **CORS enabled in `app/main.py`** ✓
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],  # Allows all origins
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- [x] **Firewall allows connections on port 8000** ✓
  - Mac firewall should allow incoming connections

- [x] **Backend and mobile devices on same WiFi network** ✓
  - Both must be on `192.168.68.x` network

### ✅ Flutter App Configuration

- [ ] **Update `baseUrl` in all apps to Mac IP**

  **Currently configured:** `http://192.168.68.51:8000` ✓

  **Verify your current Mac IP:**
  ```bash
  ipconfig getifaddr en0
  # Output: 192.168.68.51
  ```

  If your Mac IP changes, update all Flutter apps:
  ```bash
  # Script to update all apps at once
  ./mobile/flutter_apps/verify_api_config.sh
  ```

- [ ] **Test connection from each app**
  - Login with valid credentials
  - Check API calls in debug console

---

## 🔧 Troubleshooting

### Problem 1: "Connection Refused" Error

**Symptom:**
```
Exception: Network error: Connection refused
```

**Causes & Solutions:**

1. **Backend not running**
   ```bash
   # Start backend
   cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Wrong IP address in Flutter app**
   ```bash
   # Check your current Mac IP
   ipconfig getifaddr en0

   # Update Flutter app config if different
   # File: lib/config/app_config.dart
   static const String baseUrl = 'http://YOUR_MAC_IP:8000';
   ```

3. **Devices on different networks**
   - iPhone must be on same WiFi as Mac
   - Check WiFi settings on both devices

### Problem 2: "401 Unauthorized" Error

**Symptom:**
```
HTTP Status Code: 401
{"detail": "Not authenticated"}
```

**Causes & Solutions:**

1. **Token expired**
   ```dart
   // Clear token and re-login
   final prefs = await SharedPreferences.getInstance();
   await prefs.remove('auth_token');
   // Navigate to login screen
   ```

2. **Token not included in request**
   ```dart
   // Ensure headers include token
   headers: {
     'Authorization': 'Bearer $token'
   }
   ```

3. **Invalid token format**
   - Token should start with "Bearer "
   - Check for extra spaces or line breaks

### Problem 3: "Timeout" Error

**Symptom:**
```
TimeoutException after 30000ms
```

**Causes & Solutions:**

1. **Slow network**
   ```dart
   // Increase timeout in app_config.dart
   static const int connectionTimeout = 60000; // 60 seconds
   ```

2. **Backend slow response**
   ```bash
   # Check backend logs for slow queries
   tail -f app/logs/tsh_erp_20251024.log
   ```

3. **Database connection issues**
   ```bash
   # Check PostgreSQL is running
   pg_isready -U khaleelal-mulla -d erp_db
   ```

### Problem 4: "CORS" Error

**Symptom:**
```
Access to XMLHttpRequest at 'http://192.168.68.51:8000/api/...'
from origin has been blocked by CORS policy
```

**Solution:**

This typically only affects web apps, not mobile Flutter apps. But if it occurs:

```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Architecture Summary

### Current System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     11 Flutter Mobile Apps                      │
│                                                                 │
│  • 01_admin         • 05_inventory      • 09_wholesale         │
│  • 02_security      • 06_salesperson    • 10_consumer          │
│  • 03_accounting    • 07_retail         • 11_aso               │
│  • 04_hr            • 08_partner                               │
│                                                                 │
│  All running on: iPhones, iPads, Android devices              │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    │ HTTP REST API
                    │ JWT Authentication
                    │ JSON Data Format
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│               FastAPI Backend (Python)                          │
│                                                                 │
│  • Host: 192.168.68.51:8000                                    │
│  • 50+ API Endpoints                                           │
│  • JWT Authentication                                          │
│  • Rate Limiting                                               │
│  • RBAC (Role-Based Access Control)                           │
│  • Structured Logging                                          │
│  • WebSocket (Real-time updates)                              │
│                                                                 │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    │ SQLAlchemy ORM
                    │ Connection Pooling
                    │ Transaction Management
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│            PostgreSQL Database (erp_db)                         │
│                                                                 │
│  • 100+ Tables                                                 │
│  • Single Source of Truth                                      │
│  • ACID Transactions                                           │
│  • Referential Integrity                                       │
│  • Indexed for Performance                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Benefits of This Architecture

1. **Centralized Data**
   - All apps read/write to same database
   - No data sync issues
   - Single source of truth

2. **Secure Authentication**
   - JWT tokens with expiry
   - Token refresh mechanism
   - Rate limiting protection

3. **Scalable**
   - Add new Flutter apps easily
   - Backend can scale horizontally
   - Connection pooling handles concurrent requests

4. **Maintainable**
   - Business logic in backend (one place)
   - Flutter apps are thin clients
   - Easy to update API without rebuilding apps

---

## 📚 Related Documentation

- **`DATABASE_CONNECTION_ARCHITECTURE.md`** - Complete architecture details
- **`TOKEN_REFRESH_FLOW.md`** - JWT token refresh mechanism
- **`ARCHITECTURE_IMPROVEMENTS_STATUS.md`** - Architecture analysis
- **`app/main.py:161`** - Authentication router configuration
- **`app/routers/auth_enhanced.py`** - Authentication endpoints
- **`app/dependencies/rbac.py`** - Role-based access control

---

## 🎯 Quick Reference

### Backend URL
```
http://192.168.68.51:8000
```

### Common Endpoints
```
POST   /api/auth/login              - User login
POST   /api/auth/refresh-token      - Refresh JWT token
GET    /api/accounting/currencies   - Get currencies
GET    /api/accounting/summary      - Dashboard stats
POST   /api/accounting/journal-entries - Create journal entry
GET    /api/hr/employees            - Get employees list
```

### Flutter API Call Pattern
```dart
final response = await http.get(
  Uri.parse('http://192.168.68.51:8000/api/accounting/currencies'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $token',
  },
);

if (response.statusCode == 200) {
  final data = json.decode(response.body);
  // Process data
}
```

---

**Last Updated:** 2025-10-24
**System Status:** ✅ All services running
**Backend:** FastAPI on `192.168.68.51:8000`
**Database:** PostgreSQL `erp_db` on `localhost:5432`
