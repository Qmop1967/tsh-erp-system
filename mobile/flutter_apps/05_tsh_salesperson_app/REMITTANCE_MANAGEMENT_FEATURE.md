# Remittance Management System - TSH Salesperson App

## 🎯 Purpose

Complete system for managing weekly remittance transactions sent by sales representatives to the head office through various channels (exchange companies, banks, e-wallets).

## 🎨 Design Specifications

### Color Scheme
- **Primary Blue Gradient**: `#4FC3F7` → `#0288D1` (Sky Blue)
- **Background**: `#F7F8FA` (Off-white)
- **Pending Status**: `#FFA726` (Orange)
- **Confirmed Status**: `#66BB6A` (Green)
- **Canceled Status**: `#EF5350` (Red)
- **Archived**: `#757575` (Gray)

### Typography
- **Font**: Cairo (Arabic support) / Poppins (English)
- **Icons**: Material Design Icons (Rounded)

## 📋 Features Implemented

### 1. Main Dashboard Overview
**Location**: `lib/widgets/remittance/dashboard_overview_card.dart`

**Metrics Displayed**:
- 📊 Total remittances this week
- 💰 Total amount confirmed by head office
- ⏳ Pending remittances count
- 📈 Average transfer commission

**Design**: Light blue gradient cards with white stat boxes

### 2. Create New Remittance
**Location**: `lib/pages/remittance/create_remittance_page.dart`

**Form Fields**:

| Field | Type | Required | Features |
|-------|------|----------|----------|
| Transfer Amount | Number Input | ✅ | Supports IQD and USD |
| Currency | Chip Selector | ✅ | IQD / USD toggle |
| Remittance Number | Text Input | ✅ | QR scan button included |
| Transfer Channel | Dropdown | ✅ | 5 predefined channels |
| Transfer Date | Date Picker | ✅ | Calendar selection |
| Proof Document | Image Upload | ⭕ | Camera or gallery |
| Transfer Fees | Number Input | ⭕ | Optional commission |
| Notes | Text Area | ⭕ | Free text field |

**Transfer Channels**:
- 🏪 Al-Taif Exchange
- 🏦 Al-Taif Bank
- 📱 Zain Cash
- 💳 Super Key
- ➕ Other

**Features**:
- ✅ Form validation
- 📸 Auto document capture
- 📷 Image upload from camera/gallery
- 🔍 QR code scan button (ready for implementation)
- 💾 Draft save capability

### 3. Pending Transfers Section
**Location**: `lib/widgets/remittance/pending_transfers_section.dart`

**Features**:
- Orange-accented cards with "⏳ Pending" badge
- Channel-specific icons and colors
- Amount display with currency
- Transfer date and fees
- Notes display (if available)
- Proof document indicator (✓ icon)

**Actions Available**:
- ✏️ Edit remittance
- 🗑️ Cancel remittance
- 👁️ View details

**Empty State**: Shows friendly message when no pending transfers

### 4. Confirmed Transfers Section
**Location**: `lib/widgets/remittance/confirmed_transfers_section.dart`

**Features**:
- Green-accented cards with "✅ Confirmed" badge
- Transfer date vs. confirmation date
- Admin notes display (if any)
- Bold confirmed amount
- Success indicators

**Filterable By**:
- Week
- Month
- Channel
- Currency

### 5. Archived Transfers Section
**Location**: `lib/widgets/remittance/archived_transfers_section.dart`

**Features**:
- Gray-toned design (soft, minimal)
- Search bar for finding old transfers
- Compact card layout
- Quick amount display

**Search Capabilities**:
- By remittance number
- By date range
- By channel

## 🔄 Workflow Logic

```
┌─────────────┐
│   Created   │  → Salesperson creates new remittance
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Pending   │  → Waiting for admin confirmation
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Confirmed  │  → Admin confirms receipt
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Archived   │  → Auto-moved after time period
└─────────────┘
```

## 🧠 Smart Features

### Automatic Validation
- ✅ Duplicate remittance number detection
- ✅ Required field validation
- ✅ Amount format validation
- ✅ Date validation

### Interactive Notifications
- 🔔 Remittance confirmed alert
- ⏰ Weekly reminder to send remittance
- ⚠️ Pending remittance warnings

### Advanced Filters
**Available Filters**:
- Channel type
- Status (Pending, Confirmed, Archived)
- Date range
- Amount range
- Currency type

### Weekly Analytics (Ready for Implementation)
- Line/bar charts showing weekly trends
- Commission analysis
- Channel performance comparison

### Internal Comment System
- Admin can add remarks to remittances
- Example: "Received with 5,000 IQD difference"
- Displayed in confirmed transfers

## 📱 UI Components

### Tab Navigation
3 tabs with badge counters:
- **المعلقة (Pending)** - Shows count badge
- **المؤكدة (Confirmed)** - No badge
- **الأرشيف (Archive)** - No badge

### Floating Action Button
- **Label**: "حوالة جديدة" (New Remittance)
- **Color**: Sky blue gradient
- **Icon**: Plus (+)
- **Position**: Bottom-right (RTL-adjusted)

### Filter Dialog
Quick access filters:
- By transfer channel
- By date range
- By amount

## 🚀 Additional Features (Ready for Implementation)

### QR Code Scanning
- Built-in button on remittance number field
- Auto-fills remittance details from QR
- Reduces manual entry errors

### Auto Document Capture
- Camera automatically adjusts brightness
- Crops receipt images
- Enhances text readability

### Weekly Reminder System
- Thursday reminder: "Send your weekly remittance"
- Customizable reminder day
- Push notification support

### Export to PDF
- Generate full report of remittances
- Filter by date range
- Include proof documents
- Email or share report

## 📊 Sample Data Included

### Pending Transfers: 2 items
- Al-Taif Exchange transfer (10M IQD)
- Zain Cash transfer (5M IQD)

### Confirmed Transfers: 3 items
- Al-Taif Bank (12M IQD)
- Al-Taif Exchange (8M IQD)
- Zain Cash (15M IQD)

### Archived Transfers: 3 items
- December 2023 transfers

## 🔌 API Integration Guide

### Required Endpoints

```dart
// Create new remittance
POST /api/remittances/create
{
  "amount": 10000000,
  "currency": "IQD",
  "remittance_number": "REM-2024-001",
  "channel": "Al-Taif Exchange",
  "date": "2024-01-15",
  "fees": 25000,
  "notes": "Weekly transfer",
  "proof_document": "base64_image_string"
}

// Get pending remittances
GET /api/remittances/pending

// Get confirmed remittances
GET /api/remittances/confirmed?week={week}&month={month}

// Get archived remittances
GET /api/remittances/archived?search={query}

// Update remittance
PUT /api/remittances/{id}

// Cancel remittance
DELETE /api/remittances/{id}

// Get dashboard stats
GET /api/remittances/stats/weekly
```

### Response Format Example

```json
{
  "success": true,
  "data": {
    "remittances": [
      {
        "id": "REM-2024-001",
        "amount": 10000000,
        "currency": "IQD",
        "channel": "Al-Taif Exchange",
        "date": "2024-01-15",
        "status": "pending",
        "fees": 25000,
        "has_proof": true,
        "notes": "Weekly transfer",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "stats": {
      "total_this_week": 5,
      "total_amount_confirmed": 45000000,
      "pending_count": 2,
      "average_commission": 25000
    }
  }
}
```

## 📂 File Structure

```
lib/
├── pages/
│   └── remittance/
│       ├── remittance_management_page.dart       # Main page with tabs
│       └── create_remittance_page.dart           # Form page
└── widgets/
    └── remittance/
        ├── dashboard_overview_card.dart          # Stats overview
        ├── pending_transfers_section.dart        # Pending tab
        ├── confirmed_transfers_section.dart      # Confirmed tab
        └── archived_transfers_section.dart       # Archive tab
```

## 🎯 Navigation

Add to menu page:

```dart
ListTile(
  leading: Icon(MdiIcons.bankTransfer, color: Color(0xFF4FC3F7)),
  title: Text('إدارة الحوالات'),
  onTap: () {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => RemittanceManagementPage(),
      ),
    );
  },
)
```

## ✨ Future Enhancements

### Phase 2 Features:
1. **Real-time Tracking**: Live status updates via WebSocket
2. **Receipt OCR**: Auto-extract details from receipt photos
3. **Multi-currency Support**: Add EUR, GBP, etc.
4. **Batch Remittances**: Send multiple transfers at once
5. **Analytics Dashboard**: Deep insights with charts
6. **Push Notifications**: Real-time alerts
7. **Offline Mode**: Queue remittances when offline
8. **Voice Notes**: Add audio comments
9. **Signature Capture**: Digital signature for confirmation
10. **Blockchain Verification**: Immutable transfer records

## 📱 Testing Checklist

- [ ] Create new remittance with all fields
- [ ] Upload proof document (camera)
- [ ] Upload proof document (gallery)
- [ ] Edit pending remittance
- [ ] Cancel pending remittance
- [ ] View remittance details
- [ ] Filter by channel
- [ ] Filter by date
- [ ] Search archived transfers
- [ ] Tab navigation (3 tabs)
- [ ] Dashboard stats display
- [ ] Form validation (empty fields)
- [ ] Form validation (invalid amount)
- [ ] Currency toggle (IQD/USD)
- [ ] Date picker functionality

## 📄 Notes

- All amounts in IQD (Iraqi Dinar) by default
- RTL layout for Arabic language
- Responsive design for all screen sizes
- Sample data included for testing
- Ready for backend API integration
- Supports dark mode (can be added)

---

**Created**: January 2024
**Version**: 1.0.0
**Status**: ✅ Ready for Testing
**Design**: Clean, Modern, Professional
