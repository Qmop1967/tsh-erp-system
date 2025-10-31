# 🔄 TSH Accounting Real-Time Integration Guide

## Overview

This guide explains the real-time integration between the **TSH Accounting Flutter Mobile App** and the **TSH ERP Admin React Web Application**.

When a journal entry is created in the mobile app, it instantly appears in the React web application through WebSocket real-time communication.

---

## 🏗️ Architecture

```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────────────┐
│  Flutter Mobile App │────────▶│   FastAPI Backend    │◀────────│  React Web Admin    │
│  (Accountant)       │  HTTP   │   + WebSocket        │  WS     │  (Management)       │
│                     │         │                      │         │                     │
│  • Create Journal   │         │  • /api/accounting/  │         │  • View Journals    │
│  • View Dashboard   │         │    journal-entries   │         │  • Real-time        │
│  • Offline Support  │         │  • /api/accounting/  │         │    Updates          │
│                     │         │    ws (WebSocket)    │         │                     │
└─────────────────────┘         └──────────────────────┘         └─────────────────────┘
                                          │
                                          │ Broadcast
                                          ▼
                                  ┌──────────────┐
                                  │  PostgreSQL  │
                                  │   Database   │
                                  └──────────────┘
```

---

## 📡 Communication Flow

### 1. Journal Entry Creation (Flutter → Backend)

**Flutter App** → **POST** `/api/accounting/journal-entries`

```dart
// Flutter app sends HTTP POST request
final response = await http.post(
  Uri.parse('$baseUrl/api/accounting/journal-entries'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'journal_id': 1,
    'reference': 'JE-2025-001',
    'date': '2025-01-15',
    'description_en': 'Sales transaction',
    'description_ar': 'عملية بيع',
    'lines': [
      {'account_id': 100, 'debit': 1000.0, 'credit': 0.0},
      {'account_id': 200, 'debit': 0.0, 'credit': 1000.0},
    ]
  }),
);
```

### 2. Backend Processing & Broadcasting

**Backend** processes and broadcasts via WebSocket:

```python
# app/routers/accounting.py

@router.post("/journal-entries")
async def create_journal_entry(entry: JournalEntryCreate, db: Session = Depends(get_db)):
    # 1. Create entry in database
    new_entry = service.create_journal_entry(entry)

    # 2. Broadcast to all connected WebSocket clients
    entry_dict = {
        "id": new_entry.id,
        "reference": new_entry.reference,
        "date": new_entry.date.isoformat(),
        "description_en": new_entry.description_en,
        "description_ar": new_entry.description_ar,
        "journal_id": new_entry.journal_id,
        "status": new_entry.status,
        "total_debit": float(new_entry.total_debit),
        "total_credit": float(new_entry.total_credit),
    }
    await accounting_ws_manager.broadcast_journal_entry_created(entry_dict)

    return new_entry
```

### 3. Real-Time Update (Backend → React)

**React App** receives WebSocket message:

```typescript
// React hook automatically receives update
useAccountingWebSocket({
  onJournalEntryCreated: (newEntry) => {
    // Add to journal entries list immediately
    setJournalEntries(prev => [newEntry, ...prev])
    // Show toast notification
    toast.success('New journal entry created!')
  }
})
```

---

## 🔌 WebSocket Endpoints

### Backend WebSocket Endpoint

**URL**: `ws://192.168.68.51:8000/api/accounting/ws`

**Events Broadcasted**:
- `journal_entry_created` - New entry created
- `journal_entry_updated` - Entry modified
- `journal_entry_posted` - Entry posted to ledger
- `accounting_summary_updated` - Dashboard stats updated

**Message Format**:
```json
{
  "event": "journal_entry_created",
  "data": {
    "id": 123,
    "reference": "JE-2025-001",
    "date": "2025-01-15",
    "description_en": "Sales transaction",
    "description_ar": "عملية بيع",
    "journal_id": 1,
    "status": "DRAFT",
    "total_debit": 1000.0,
    "total_credit": 1000.0
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

## 🚀 Setup Instructions

### 1. Backend Setup (Already Configured)

✅ **WebSocket Manager Created**: `app/services/accounting_websocket.py`
✅ **WebSocket Endpoint Added**: `app/routers/accounting.py`
✅ **Broadcasting Integrated**: Journal entry creation broadcasts updates

### 2. React Frontend Setup (Already Configured)

✅ **WebSocket Hook Created**: `frontend/src/hooks/useAccountingWebSocket.ts`
✅ **Integrated in Journal Page**: `frontend/src/pages/accounting/JournalEntriesPage.tsx`

### 3. Flutter Mobile App Setup (Next Step)

#### Add web_socket_channel dependency:

```yaml
# pubspec.yaml
dependencies:
  web_socket_channel: ^2.4.0
```

#### Create journal entry form (see implementation below)

---

## 📱 Flutter Implementation Example

### Create Journal Entry Screen

```dart
// lib/screens/create_journal_entry_screen.dart

class CreateJournalEntryScreen extends StatefulWidget {
  @override
  _CreateJournalEntryScreenState createState() =>
      _CreateJournalEntryScreenState();
}

class _CreateJournalEntryScreenState extends State<CreateJournalEntryScreen> {
  final _apiService = ApiService();
  final _referenceController = TextEditingController();
  final _descriptionController = TextEditingController();

  List<JournalLine> _lines = [];
  bool _isSubmitting = false;

  Future<void> _submitJournalEntry() async {
    if (_isSubmitting) return;

    setState(() => _isSubmitting = true);

    try {
      final entryData = {
        'journal_id': 1, // Default journal
        'reference': _referenceController.text,
        'date': DateTime.now().toIso8601String().split('T')[0],
        'description_en': _descriptionController.text,
        'description_ar': _descriptionController.text,
        'lines': _lines.map((line) => line.toJson()).toList(),
      };

      final response = await _apiService.createJournalEntry(entryData);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ Journal entry created successfully!'),
          backgroundColor: Colors.green,
        ),
      );

      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Error: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('إنشاء قيد يومية - Create Journal Entry'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _referenceController,
              decoration: InputDecoration(labelText: 'Reference'),
            ),
            TextField(
              controller: _descriptionController,
              decoration: InputDecoration(labelText: 'Description'),
            ),
            // ... Add journal lines builder
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isSubmitting ? null : _submitJournalEntry,
              child: _isSubmitting
                  ? CircularProgressIndicator()
                  : Text('Create Entry'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### API Service Method

```dart
// lib/services/api_service.dart

Future<Map<String, dynamic>> createJournalEntry(Map<String, dynamic> entryData) async {
  final token = await _getToken();

  final response = await http.post(
    Uri.parse('$baseUrl/api/accounting/journal-entries'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode(entryData),
  );

  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to create journal entry');
  }
}
```

---

## 🧪 Testing the Integration

### Test Flow:

1. **Open React Admin** → Navigate to Journal Entries page
   - URL: `http://localhost:5173/accounting/journal-entries`
   - WebSocket connection establishes automatically

2. **Open Flutter Mobile App** → Create new journal entry
   - Fill in reference, description, and line items
   - Click "Create Entry"

3. **Watch React Admin** → Entry appears instantly!
   - Toast notification shows
   - Entry appears at top of list
   - No page refresh needed

### Expected Results:

✅ Journal entry created in mobile app
✅ Backend receives POST request
✅ Entry saved to database
✅ WebSocket broadcasts to all connected clients
✅ React app receives WebSocket message
✅ Toast notification appears
✅ Entry added to list in real-time

---

## 🔧 Configuration

### Backend Configuration

**File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/routers/accounting.py`

WebSocket endpoint is automatically registered when accounting router is included in main app.

### React Configuration

**File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/frontend/src/hooks/useAccountingWebSocket.ts`

WebSocket connects to:
- Development: `ws://localhost:8000/api/accounting/ws`
- Same network: `ws://192.168.68.51:8000/api/accounting/ws`

### Flutter Configuration

**File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/apps/accounting_app/lib/config/app_config.dart`

```dart
static const String baseUrl = 'http://192.168.68.51:8000';
```

---

## 🎯 Features Implemented

### ✅ Backend Features
- [x] WebSocket connection manager
- [x] Real-time broadcasting for journal entries
- [x] Automatic reconnection handling
- [x] Event types: created, updated, posted

### ✅ Frontend Features (React)
- [x] WebSocket hook with automatic reconnection
- [x] Toast notifications for updates
- [x] Automatic list refresh on new entries
- [x] Connection status indicator

### 🔜 Mobile Features (Flutter) - To Be Implemented
- [ ] Journal entry creation form
- [ ] Account selection dropdown
- [ ] Debit/Credit line items
- [ ] Validation (debit = credit)
- [ ] Offline support

---

## 📋 Next Steps

1. **Implement Flutter Journal Entry Form**
   - Complete the journal entry creation screen
   - Add form validation
   - Integrate with API service

2. **Add Chart of Accounts to Flutter**
   - Fetch accounts list from backend
   - Show in dropdown for line items
   - Support hierarchical display

3. **Enhance Real-Time Features**
   - Add accounting summary updates
   - Broadcast account balance changes
   - Real-time dashboard stats

4. **Testing**
   - Test with multiple concurrent users
   - Verify WebSocket reconnection
   - Test offline/online scenarios

---

## 🆘 Troubleshooting

### Issue: WebSocket Connection Refused

**Solution**: Ensure backend is running on all interfaces:
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: CORS Errors

**Solution**: Backend should already have CORS configured for WebSocket connections.

### Issue: Mobile App Can't Connect

**Solution**: Use Mac's local IP address (192.168.68.51) instead of localhost.

---

## 📚 Documentation References

- **FastAPI WebSockets**: https://fastapi.tiangolo.com/advanced/websockets/
- **Flutter HTTP Package**: https://pub.dev/packages/http
- **React WebSocket**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

---

**Status**: ✅ Backend & React Integration Complete | ⏳ Flutter Implementation Pending

**Last Updated**: 2025-01-15
