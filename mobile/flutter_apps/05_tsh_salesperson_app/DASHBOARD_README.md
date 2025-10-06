# TSH Salesperson App - Enhanced Dashboard System

## 📱 Overview

This is the redesigned TSH Salesperson mobile application with a modern, stylish dual-dashboard system and comprehensive navigation.

## ✨ New Features

### 1. **Dual Dashboard System**

The app now features two interactive dashboards accessible via top tabs:

#### **Dashboard 1: Personal Metrics (لوحتي)**
- **Commission Summary Card**
  - Total commission earned
  - Paid vs. pending commission
  - Current month commission with trend
  - Visual breakdown of earnings

- **Receivables Summary Card**
  - Total outstanding amounts
  - Overdue payments highlighted
  - Due this week section
  - Customer count with receivables

- **Cash Box Actions Card**
  - Current cash balance
  - Quick action buttons:
    - Transfer money
    - Deposit cash
    - View transaction history

- **Digital Payments Card**
  - Total digital payments received
  - Transaction count
  - QR Code generator
  - Payment history

- **Sales Hot Report Card**
  - Today's sales
  - Weekly sales
  - Monthly sales
  - Growth percentage indicator
  - Top 3 selling products

- **Quick Actions Grid**
  - New customer
  - New order
  - New invoice (POS)
  - Collect payment
  - Reports
  - Search

#### **Dashboard 2: Leaderboard & Challenges (المتصدرين)**
- **Salesperson Level Card**
  - Current level (Bronze, Silver, Gold, Platinum, Diamond)
  - Progress to next level
  - Current rank among team
  - Points earned and remaining

- **Active Challenges Card**
  - Multiple challenges with progress bars
  - Rewards for completion
  - Completed challenges highlighted

- **Sales Comparison Chart**
  - Bar chart comparing your sales with:
    - Team average
    - Top performer

- **Collection Comparison Chart**
  - Bar chart showing your collections vs:
    - Team average
    - Top collector

- **Activity Comparison Card**
  - Customer visits count
  - Phone calls made
  - Follow-ups completed

- **Top Performers List**
  - Ranked list of all salespersons
  - Shows sales and collections
  - Your position highlighted
  - Medal indicators for top 3

### 2. **Bottom Navigation Bar**

Five main sections accessible from anywhere:

1. **الرئيسية (Home)** - Dashboard container with both dashboards
2. **العملاء (Clients)** - Customer management
3. **نقطة البيع (POS)** - Point of sale for invoices
4. **الطلبات (Orders)** - Order management
5. **القائمة (Menu)** - Settings and modules

### 3. **Menu Page**

Comprehensive menu with organized sections:

- **Sales Management**
  - Customer Management
  - Products Catalog
  - Orders
  - Invoices

- **Finance**
  - Payments
  - Receivables
  - My Commissions

- **Reports**
  - Sales Reports
  - Financial Reports

- **Settings**
  - Profile
  - App Settings
  - Help & Support
  - Logout

## 🎨 Design Features

### Color Scheme
- **Primary Green**: `#1B5E20` - Main brand color
- **Light Green**: `#4CAF50` - Accents and highlights
- **Gold Accent**: `#FFB300` - Premium features and achievements
- **Info Blue**: `#2196F3` - Information and statistics
- **Success Green**: `#4CAF50` - Positive indicators
- **Warning Orange**: `#FF9800` - Alerts and pending items
- **Error Red**: `#F44336` - Critical items

### UI Components
- **Gradients**: Smooth gradients for premium feel
- **Shadows**: Subtle shadows for depth
- **Rounded Corners**: 15-25px radius for modern look
- **Animations**: Staggered animations for smooth transitions
- **Shimmer Effects**: Loading states with shimmer
- **Icons**: Material Design Icons for consistency

## 📂 File Structure

```
lib/
├── pages/
│   ├── home/
│   │   └── home_page.dart                    # Main container with bottom nav
│   ├── dashboard/
│   │   ├── dashboard_container_page.dart     # Tab controller for 2 dashboards
│   │   ├── main_dashboard_page.dart          # Personal metrics dashboard
│   │   └── leaderboard_dashboard_page.dart   # Leaderboard & challenges
│   ├── customers/
│   │   └── customers_list_page.dart          # Customer list
│   ├── sales/
│   │   └── pos_page.dart                     # Point of sale
│   ├── orders/
│   │   └── orders_list_page.dart             # Orders list
│   └── menu/
│       └── menu_page.dart                    # Settings menu
├── widgets/
│   └── dashboard/
│       ├── main_dashboard/
│       │   ├── commission_summary_card.dart
│       │   ├── receivables_summary_card.dart
│       │   ├── cash_box_actions_card.dart
│       │   ├── digital_payments_card.dart
│       │   ├── sales_hotReport_card.dart
│       │   └── quick_actions_card.dart
│       └── leaderboard/
│           ├── salesperson_level_card.dart
│           ├── challenges_card.dart
│           ├── sales_comparison_chart.dart
│           ├── collection_comparison_chart.dart
│           ├── activity_comparison_card.dart
│           └── top_performers_list.dart
├── providers/
│   └── dashboard_provider.dart               # Updated with leaderboard support
└── config/
    └── app_theme.dart                        # Centralized theme
```

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.32.0 or higher
- Dart 3.0.0 or higher

### Dependencies
All required dependencies are already in `pubspec.yaml`:
- `provider` - State management
- `fl_chart` - Charts and graphs
- `material_design_icons_flutter` - Icons
- `flutter_staggered_animations` - Animations
- `shimmer` - Loading effects
- `intl` - Number formatting

### Running the App

```bash
# Install dependencies
flutter pub get

# Run on iOS
flutter run -d ios

# Run on Android
flutter run -d android

# Build release
flutter build ios
flutter build apk
```

## 🔧 Configuration

### Mock Data
Currently, the app uses mock data for demonstration. The `DashboardProvider` has two methods:
- `fetchDashboardData()` - Loads personal metrics
- `fetchLeaderboardData(period)` - Loads leaderboard data

### Connecting to Real Backend
To connect to your Odoo backend:

1. Update `OdooService` in `lib/services/odoo_service.dart`
2. Implement actual API calls in:
   - `getDashboardData()`
   - `getLeaderboardData()`
3. Update `DashboardProvider` methods to call actual services

## 📊 Data Models

### Dashboard Data Structure
```dart
{
  'commission': {
    'total': double,
    'paid': double,
    'pending': double,
    'this_month': double,
  },
  'receivables': {
    'total': double,
    'overdue': double,
    'due_this_week': double,
    'customer_count': int,
  },
  'cash_box': {
    'amount': double,
  },
  'digital_payments': {
    'amount': double,
    'count': int,
  },
  'sales': {
    'today': double,
    'this_week': double,
    'this_month': double,
    'growth_percentage': double,
    'top_products': List<Map>,
  },
}
```

### Leaderboard Data Structure
```dart
{
  'current_level': {
    'name': String,
    'progress': double,
    'current_points': int,
    'next_level_points': int,
    'rank': int,
    'total_salespeople': int,
  },
  'challenges': List<Map>,
  'sales_comparison': Map,
  'collection_comparison': Map,
  'activity': Map,
  'top_performers': List<Map>,
}
```

## 🎯 Future Enhancements

1. **Real-time Updates**: WebSocket integration for live data
2. **Push Notifications**: Challenge completions, new orders
3. **Offline Mode**: Local data caching with sync
4. **Advanced Analytics**: More detailed charts and insights
5. **Social Features**: Team chat, achievement sharing
6. **Customization**: User-configurable dashboard widgets
7. **AR Features**: Product visualization
8. **Voice Commands**: Hands-free operation

## 📝 Notes

- All text is in Arabic (RTL supported)
- Number formatting uses Iraqi Dinar (IQD)
- Dates formatted in Arabic locale
- Animations are optimized for performance
- All widgets are reusable and modular

## 🤝 Contributing

When adding new features:
1. Follow the existing file structure
2. Use `AppTheme` for colors
3. Add loading states with shimmer
4. Include error handling
5. Support RTL layout
6. Test on both iOS and Android

## 📱 Screenshots

The app includes:
- Modern gradient cards
- Smooth animations
- Interactive charts
- Level-based gamification
- Comprehensive metrics
- Professional UI/UX

---

**Version**: 1.0.0  
**Last Updated**: October 1, 2025  
**Platform**: iOS, Android, Web
