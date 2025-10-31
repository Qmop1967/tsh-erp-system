# Database Connection Architecture - Flutter Apps to PostgreSQL

**How TSH ERP Flutter Apps Connect to the Central Database**

---

## 🔄 Complete Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Flutter Mobile App (Dart)                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  UI Layer (Screens & Widgets)                            │  │
│  │  - User interacts with app                               │  │
│  │  - Shows forms, lists, dashboards                        │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Service Layer (lib/services/api_service.dart)      │  │
│  │  - Makes HTTP requests                                   │  │
│  │  - Handles authentication (JWT tokens)                   │  │
│  │  - Serializes/deserializes JSON                          │  │
│  │  - Error handling                                        │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│                   │ HTTP Request                                 │
│                   │ (GET/POST/PUT/DELETE)                        │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │
                    │ 📡 Network (WiFi/Cellular)
                    │ http://192.168.68.51:8000/api/[endpoint]
                    │
┌───────────────────▼──────────────────────────────────────────────┐
│              FastAPI Backend (Python)                            │
│                Port 8000                                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Router (app/routers/accounting.py, etc.)       │  │
│  │  - Receives HTTP request                                 │  │
│  │  - Validates request data                                │  │
│  │  - Checks JWT authentication                             │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Service Layer (app/services/accounting_service.py)     │  │
│  │  - Business logic                                        │  │
│  │  - Data validation                                       │  │
│  │  - Transaction management                                │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Database Session (app/db/database.py)                  │  │
│  │  - SQLAlchemy Session                                    │  │
│  │  - Connection pooling                                    │  │
│  │  - get_db() dependency injection                         │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│                   │ SQL Query                                    │
│                   │ (SELECT/INSERT/UPDATE/DELETE)                │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │
                    │ PostgreSQL Protocol
                    │ localhost:5432
                    │
┌───────────────────▼──────────────────────────────────────────────┐
│            PostgreSQL Database Server                            │
│                 Database: erp_db                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tables (100+ tables):                                   │  │
│  │  - accounting_periods                                    │  │
│  │  - accounts                                              │  │
│  │  - chart_of_accounts                                     │  │
│  │  - currencies                                            │  │
│  │  - journal_entries                                       │  │
│  │  - journal_lines                                         │  │
│  │  - customers                                             │  │
│  │  - employees                                             │  │
│  │  - inventory_items                                       │  │
│  │  - sales_orders                                          │  │
│  │  - ...and many more                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📊 Single Source of Truth for ALL apps                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Authentication Flow

### 1. Login Process

```dart
// Flutter App (api_service.dart)
Future<Map<String, dynamic>> login(String email, String password) async {
  final response = await http.post(
    Uri.parse('http://192.168.68.51:8000/api/auth/login'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({
      'email': email,
      'password': password,
    }),
  );

  if (response.statusCode == 200) {
    final data = json.decode(response.body);

    // Save JWT token locally
    _token = data['access_token'];
    await prefs.setString('auth_token', _token!);

    return {'success': true, 'data': data};
  }
}
```

**What happens:**
1. User enters credentials in Flutter app
2. App sends HTTP POST to FastAPI `/api/auth/login`
3. FastAPI validates credentials against `users` table in PostgreSQL
4. If valid, FastAPI generates JWT token
5. Flutter app stores token in SharedPreferences (local device storage)
6. Token is included in all subsequent requests

### 2. Authenticated API Requests

```dart
// Flutter App - Adding JWT to requests
Future<Map<String, String>> _getHeaders() async {
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer $_token',  // JWT token
  };
}
```

---

## 📊 Data Operations Flow

### Example: Creating a Journal Entry

#### **Step 1: Flutter App UI**
```dart
// User fills form in Flutter app
final entry = JournalEntry(
  reference: 'JE-2025-001',
  date: DateTime.now(),
  description_en: 'Cash payment for supplies',
  description_ar: 'دفع نقدي للوازم',
  journal_id: 1,
  lines: [
    JournalLine(account_id: 10, debit: 5000, credit: 0),
    JournalLine(account_id: 1, debit: 0, credit: 5000),
  ],
);
```

#### **Step 2: API Service Call**
```dart
// api_service.dart
Future<JournalEntry?> createJournalEntry(JournalEntry entry) async {
  final headers = await _getHeaders();  // Includes JWT token

  final response = await http.post(
    Uri.parse('http://192.168.68.51:8000/api/accounting/journal-entries'),
    headers: headers,
    body: json.encode(entry.toJson()),  // Convert to JSON
  );

  if (response.statusCode == 200 || response.statusCode == 201) {
    final data = json.decode(response.body);
    return JournalEntry.fromJson(data);  // Convert back to Dart object
  }
}
```

#### **Step 3: FastAPI Router**
```python
# app/routers/accounting.py
@router.post("/journal-entries", response_model=JournalEntry)
async def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db)  # Get database session
):
    service = AccountingService(db)
    new_entry = service.create_journal_entry(entry)

    # Broadcast to React Admin via WebSocket
    await accounting_ws_manager.broadcast_journal_entry_created({
        "id": new_entry.id,
        "reference": new_entry.reference,
        ...
    })

    return new_entry
```

#### **Step 4: Service Layer**
```python
# app/services/accounting_service.py
class AccountingService:
    def create_journal_entry(self, entry: JournalEntryCreate) -> JournalEntry:
        # Validate data
        # Check if journal entry is balanced (debit = credit)

        # Create database objects
        db_entry = JournalEntry(**entry.dict())
        self.db.add(db_entry)

        # Create journal lines
        for line in entry.lines:
            db_line = JournalLine(**line.dict(), entry_id=db_entry.id)
            self.db.add(db_line)

        # Commit transaction to database
        self.db.commit()
        self.db.refresh(db_entry)

        return db_entry
```

#### **Step 5: Database Session**
```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connection string from .env
DATABASE_URL = "postgresql://khaleelal-mulla:@localhost:5432/erp_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()  # Create new database session
    try:
        yield db
    finally:
        db.close()  # Always close connection
```

#### **Step 6: PostgreSQL Database**
```sql
-- Tables involved:
-- 1. journal_entries table
INSERT INTO journal_entries (reference, date, description_en, description_ar, ...)
VALUES ('JE-2025-001', '2025-01-24', 'Cash payment for supplies', 'دفع نقدي للوازم', ...);

-- 2. journal_lines table
INSERT INTO journal_lines (entry_id, account_id, debit, credit)
VALUES (123, 10, 5000.00, 0.00);

INSERT INTO journal_lines (entry_id, account_id, debit, credit)
VALUES (123, 1, 0.00, 5000.00);
```

---

## 🗄️ Database Configuration

### Environment Variables (`.env` file)
```bash
DATABASE_URL=postgresql://khaleelal-mulla:@localhost:5432/erp_db
```

**Format**: `postgresql://[username]:[password]@[host]:[port]/[database_name]`

- **Username**: `khaleelal-mulla` (your Mac username)
- **Password**: Empty (trusted local connection)
- **Host**: `localhost` (database on same machine as FastAPI)
- **Port**: `5432` (default PostgreSQL port)
- **Database**: `erp_db` (TSH ERP database)

### SQLAlchemy Models

SQLAlchemy ORM (Object-Relational Mapping) converts Python classes to database tables:

```python
# app/models/accounting.py
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from app.db.database import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, nullable=False)
    date = Column(Date, nullable=False)
    description_en = Column(String)
    description_ar = Column(String)
    journal_id = Column(Integer, ForeignKey("journals.id"))
    status = Column(String, default="draft")
    total_debit = Column(Numeric(precision=15, scale=2))
    total_credit = Column(Numeric(precision=15, scale=2))
```

---

## 🔄 Key Technologies

### Flutter Side (Mobile)
- **`http` package**: Makes HTTP requests
- **`dart:convert`**: JSON serialization/deserialization
- **`shared_preferences`**: Local storage for JWT tokens
- **Models**: Dart classes that mirror database structure

### Backend Side (FastAPI)
- **FastAPI**: Web framework for API endpoints
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **psycopg2**: PostgreSQL driver (under the hood)

### Database Side (PostgreSQL)
- **PostgreSQL 14+**: Relational database
- **Tables**: Structured data storage
- **Indexes**: Fast data retrieval
- **Constraints**: Data integrity (foreign keys, unique, not null)

---

## 📡 Connection Pool

FastAPI uses connection pooling for efficiency:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,         # Number of connections to keep open
    max_overflow=10,     # Additional connections when pool is full
    pool_timeout=30,     # Timeout for getting connection from pool
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

**Benefits:**
- Reuses database connections instead of creating new ones
- Faster response times
- Handles multiple Flutter apps simultaneously
- Prevents overwhelming database with connections

---

## 🚀 Important Facts

1. **Flutter apps DO NOT connect directly to PostgreSQL**
   - Flutter → FastAPI → PostgreSQL
   - This is correct and secure

2. **All 11 Flutter apps share the SAME database**
   - Database: `erp_db` on localhost:5432
   - All data in one place

3. **FastAPI is the ONLY layer that touches the database**
   - Flutter apps never know PostgreSQL exists
   - They only know HTTP endpoints

4. **JWT tokens provide security**
   - Each request is authenticated
   - Users can only access data they're authorized for

5. **WebSocket for real-time updates**
   - When one app creates data, others get notified instantly
   - React Admin sees mobile app changes in real-time

---

## 📝 Data Flow Summary

```
Flutter App           HTTP Request            FastAPI              SQL Query            PostgreSQL
(Mobile UI)    --->   (REST API)      --->   (Business Logic)  --->  (Storage)    --->  (erp_db)

                      HTTP Response           Python Objects        SQL Results
(Update UI)    <---   (JSON Data)     <---   (Process Data)    <---  (Query DB)   <---
```

---

## 🔍 Verification

To verify the database connection is working:

```bash
# 1. Check if PostgreSQL is running
pg_isready -U khaleelal-mulla -d erp_db

# 2. Check if FastAPI can connect
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
PYTHONPATH=/Users/khaleelal-mulla/TSH_ERP_Ecosystem python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Test API endpoint
curl http://192.168.68.51:8000/api/accounting/currencies

# 4. Check database tables
psql -U khaleelal-mulla -d erp_db -c "\dt"

# 5. Verify Flutter apps use correct API
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps
./verify_api_config.sh
```

---

**Last Updated**: 2025-01-24
**Architecture**: Hub & Spoke Model with Centralized Database
**Status**: ✅ All 11 apps unified with same API and database
