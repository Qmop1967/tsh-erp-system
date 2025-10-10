# Financial Management Feature - TSH Salesperson App

## Overview
A comprehensive financial management system for salespersons to track all their financial transactions, including commissions, payroll, rewards, fines, and more.

## Features Implemented

### 1. **Main Financial Management Page**
   - **Location**: `lib/pages/financial/financial_management_page.dart`
   - **Features**:
     - Financial summary card displaying total commissions
     - This month vs. total commissions
     - Paid vs. pending breakdown
     - 5 tabs for different financial categories
     - Export/Download functionality
     - Modern, clean UI with gradient cards

### 2. **Commissions Tab**
   - **Location**: `lib/widgets/financial/commissions_tab.dart`
   - **Features**:
     - Monthly statistics (This month + Average)
     - Detailed commission history
     - Commission details per order
     - Status indicators (Paid, Pending, Cancelled)
     - Commission rate display
     - Customer and order information

### 3. **Payroll Tab**
   - **Location**: `lib/widgets/financial/payroll_tab.dart`
   - **Features**:
     - Monthly salary card
     - Detailed payroll breakdown:
       - Basic salary
       - Housing allowance
       - Transportation allowance
       - Communication allowance
       - Deductions (insurance, etc.)
     - Net salary calculation
     - Payroll history with monthly records
     - Payment status tracking

### 4. **Rewards Tab**
   - **Location**: `lib/widgets/financial/rewards_tab.dart`
   - **Features**:
     - Total rewards summary
     - Monetary vs. gift rewards breakdown
     - Detailed reward history:
       - Best salesperson award
       - Performance bonuses
       - Gift items (laptops, etc.)
       - New customer acquisition bonuses
     - Reward descriptions and dates
     - Visual icons for different reward types

### 5. **Fines Tab**
   - **Location**: `lib/widgets/financial/fines_tab.dart`
   - **Features**:
     - Total fines summary
     - Deducted vs. pending fines
     - Detailed fines list with:
       - Late report submission
       - Cash shortage
       - Uniform violations
       - Lost receipts
       - Time violations
     - Severity indicators (High, Medium, Low)
     - Fine descriptions and status
     - Deduction confirmations

### 6. **Transactions Tab**
   - **Location**: `lib/widgets/financial/transactions_tab.dart`
   - **Features**:
     - Filterable transaction history
     - Filter by type: All, Commissions, Salaries, Rewards, Fines, Discounts
     - Complete transaction log with:
       - Transaction type icons
       - Amount (credit/debit)
       - Date and time
       - Status (Completed, Pending)
     - Color-coded transaction types
     - Chronological ordering

## Navigation

The commission card on the main dashboard has been made clickable:
- **File Updated**: `lib/widgets/dashboard/main_dashboard/commission_summary_card.dart`
- **Action**: Tap the commission card to navigate to Financial Management page
- **Visual Feedback**: Card acts as a button

## Design Features

### Color Scheme
- **Commissions**: Green gradient (`AppTheme.primaryGreen`)
- **Payroll**: Blue gradient
- **Rewards**: Purple gradient
- **Fines**: Red gradient
- **Success**: Green indicators
- **Warning**: Orange/Yellow indicators
- **Error**: Red indicators

### UI Components
- Gradient cards with shadows
- Icon-based visual hierarchy
- Status badges (Paid, Pending, Cancelled)
- Rounded corners (16-20px border radius)
- Card-based layout
- Responsive design
- RTL (Right-to-Left) support for Arabic

### Typography
- Bold titles (18-22px)
- Regular body text (13-15px)
- Small labels (11-12px)
- Currency formatting with IQD symbol
- Compact number formatting (K, M suffixes)

## Data Structure

### Sample Data Included
All tabs include sample data to demonstrate functionality:
- **Commissions**: 5 sample transactions
- **Payroll**: 4 months of salary history
- **Rewards**: 4 different types of rewards
- **Fines**: 5 different types of violations
- **Transactions**: 8 mixed transaction types

### Ready for API Integration
All components are structured to easily integrate with backend APIs:
- Replace sample data with API calls
- Add loading states (shimmer effects included)
- Error handling ready
- Refresh functionality can be added

## How to Test

1. **Restart the Flutter app** on your device
2. **Navigate to Dashboard**
3. **Tap on the Commission Card** (green card showing "عمولاتي")
4. **Explore all 5 tabs**:
   - العمولات (Commissions)
   - الرواتب (Payroll)
   - المكافآت (Rewards)
   - الغرامات (Fines)
   - المعاملات (Transactions)

## Future Enhancements

### Potential Features to Add:
1. **Export/Download**:
   - PDF report generation
   - Excel export
   - Email reports

2. **Filtering & Search**:
   - Date range filters
   - Amount range filters
   - Search by customer/order

3. **Charts & Analytics**:
   - Commission trends
   - Monthly comparison charts
   - Performance analytics

4. **Notifications**:
   - New commission alerts
   - Salary payment notifications
   - Fine warnings

5. **Payment Methods**:
   - Bank transfer details
   - Cash collection history
   - Digital wallet integration

## Technical Details

### Dependencies Required
- `material_design_icons_flutter`: For icons
- `intl`: For currency and number formatting
- `shimmer`: For loading states (already included)

### File Structure
```
lib/
├── pages/
│   └── financial/
│       └── financial_management_page.dart
└── widgets/
    └── financial/
        ├── commissions_tab.dart
        ├── payroll_tab.dart
        ├── rewards_tab.dart
        ├── fines_tab.dart
        └── transactions_tab.dart
```

## Screenshots Locations
After testing, you can take screenshots and save them to:
- `docs/screenshots/financial_management/`

## API Integration Guide

### Endpoints Needed:
```dart
// Commissions
GET /api/financial/commissions
GET /api/financial/commissions/{id}

// Payroll
GET /api/financial/payroll
GET /api/financial/payroll/{month}

// Rewards
GET /api/financial/rewards
GET /api/financial/rewards/{id}

// Fines
GET /api/financial/fines
GET /api/financial/fines/{id}

// Transactions
GET /api/financial/transactions
GET /api/financial/transactions?type={type}&from={date}&to={date}

// Summary
GET /api/financial/summary
```

### Response Format Example:
```json
{
  "success": true,
  "data": {
    "commissions": {
      "total": 45000000,
      "this_month": 8500000,
      "paid": 30000000,
      "pending": 15000000
    },
    "transactions": [
      {
        "id": "TXN-001",
        "type": "commission",
        "amount": 850000,
        "date": "2024-01-15T14:30:00Z",
        "status": "completed",
        "description": "Commission for order #ORD-2024-1234"
      }
    ]
  }
}
```

## Notes
- All amounts are in IQD (Iraqi Dinar)
- RTL layout for Arabic language support
- Responsive design works on all screen sizes
- Dark mode support can be added later
- Offline support can be implemented with local storage

---

**Created**: January 2024
**Version**: 1.0.0
**Status**: ✅ Ready for Testing
