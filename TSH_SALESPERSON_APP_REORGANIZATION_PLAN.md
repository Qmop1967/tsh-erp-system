# 📱 TSH Salesperson App - Complete Reorganization & Feature Implementation Plan

## 🎯 Current Status Analysis

### ✅ Existing Features
1. **Authentication** - Login page with JWT integration
2. **Dashboard** - Main dashboard, leaderboard
3. **Customers** - Customer list and management
4. **Products** - Product viewing
5. **Orders** - Order list and management
6. **POS** - Point of sale system
7. **Profile** - User profile page
8. **Menu** - Settings and options

### ❌ Missing/Incomplete Features Based on Requirements

#### 1. **GPS Tracking & Location Services**
- ❌ No GPS location tracking
- ❌ No route planning
- ❌ No visit verification
- ❌ No location-based fraud prevention

#### 2. **Money Transfer Management**
- ❌ No money transfer submission
- ❌ No commission tracking (2.25%)
- ❌ No receipt upload
- ❌ No platform selection (ZAIN Cash, SuperQi, ALTaif)
- ❌ No fraud detection alerts

#### 3. **Advanced Customer Features**
- ❌ No customer visit logging
- ❌ No customer route planning
- ❌ No visit history tracking
- ❌ No customer location mapping

#### 4. **Sales Features**
- ❌ No offline order creation
- ❌ No sales target tracking
- ❌ No commission calculator
- ❌ No sales analytics

#### 5. **Inventory Features**
- ❌ No product search by barcode
- ❌ No stock availability check
- ❌ No product availability alerts

#### 6. **Reports & Analytics**
- ❌ No daily sales report
- ❌ No commission reports
- ❌ No visit reports
- ❌ No performance analytics

#### 7. **Offline Support**
- ❌ No offline data sync
- ❌ No local database caching
- ❌ No sync status indicator

---

## 🏗️ New Organized Folder Structure

```
tsh_salesperson_app/
├── lib/
│   ├── core/                           # Core functionality
│   │   ├── api/
│   │   │   ├── api_client.dart         # HTTP client with interceptors
│   │   │   ├── api_endpoints.dart      # API endpoint constants
│   │   │   └── api_response.dart       # Response models
│   │   ├── constants/
│   │   │   ├── app_constants.dart      # App-wide constants
│   │   │   ├── commission_rates.dart   # 2.25% commission config
│   │   │   └── routes.dart             # Route names
│   │   ├── theme/
│   │   │   ├── app_theme.dart
│   │   │   ├── app_colors.dart
│   │   │   └── app_text_styles.dart
│   │   ├── utils/
│   │   │   ├── date_formatter.dart
│   │   │   ├── number_formatter.dart
│   │   │   ├── validators.dart
│   │   │   └── logger.dart
│   │   └── config/
│   │       ├── app_config.dart
│   │       └── environment.dart
│   │
│   ├── features/                       # Feature modules
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── user_model.dart
│   │   │   │   │   └── auth_response.dart
│   │   │   │   ├── repositories/
│   │   │   │   │   └── auth_repository.dart
│   │   │   │   └── services/
│   │   │   │       └── auth_service.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── login_page.dart
│   │   │   │   │   └── splash_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── login_form.dart
│   │   │   │   │   └── auth_button.dart
│   │   │   │   └── providers/
│   │   │   │       └── auth_provider.dart
│   │   │
│   │   ├── dashboard/
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── dashboard_stats.dart
│   │   │   │   │   ├── sales_summary.dart
│   │   │   │   │   └── commission_summary.dart
│   │   │   │   └── repositories/
│   │   │   │       └── dashboard_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── dashboard_page.dart
│   │   │   │   │   ├── main_dashboard_page.dart
│   │   │   │   │   └── leaderboard_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── stats_card.dart
│   │   │   │   │   ├── commission_card.dart
│   │   │   │   │   ├── receivables_card.dart
│   │   │   │   │   └── quick_stats.dart
│   │   │   │   └── providers/
│   │   │   │       └── dashboard_provider.dart
│   │   │
│   │   ├── customers/
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── customer_model.dart
│   │   │   │   │   ├── customer_visit.dart
│   │   │   │   │   └── customer_location.dart
│   │   │   │   └── repositories/
│   │   │   │       └── customer_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── customers_list_page.dart
│   │   │   │   │   ├── customer_detail_page.dart
│   │   │   │   │   ├── customer_form_page.dart
│   │   │   │   │   └── customer_visit_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── customer_card.dart
│   │   │   │   │   ├── customer_search.dart
│   │   │   │   │   └── visit_history_list.dart
│   │   │   │   └── providers/
│   │   │   │       └── customer_provider.dart
│   │   │
│   │   ├── products/
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── product_model.dart
│   │   │   │   │   └── product_category.dart
│   │   │   │   └── repositories/
│   │   │   │       └── product_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── products_list_page.dart
│   │   │   │   │   ├── product_detail_page.dart
│   │   │   │   │   └── product_search_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── product_card.dart
│   │   │   │   │   ├── product_grid.dart
│   │   │   │   │   └── category_filter.dart
│   │   │   │   └── providers/
│   │   │   │       └── product_provider.dart
│   │   │
│   │   ├── orders/
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── order_model.dart
│   │   │   │   │   ├── order_item.dart
│   │   │   │   │   └── order_status.dart
│   │   │   │   └── repositories/
│   │   │   │       └── order_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── orders_list_page.dart
│   │   │   │   │   ├── order_detail_page.dart
│   │   │   │   │   ├── create_order_page.dart
│   │   │   │   │   └── order_history_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── order_card.dart
│   │   │   │   │   ├── order_item_list.dart
│   │   │   │   │   └── order_summary.dart
│   │   │   │   └── providers/
│   │   │   │       └── order_provider.dart
│   │   │
│   │   ├── pos/                        # 🆕 NEW
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── cart_item.dart
│   │   │   │   │   ├── pos_transaction.dart
│   │   │   │   │   └── payment_method.dart
│   │   │   │   └── repositories/
│   │   │   │       └── pos_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── pos_page.dart
│   │   │   │   │   ├── checkout_page.dart
│   │   │   │   │   └── payment_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── cart_widget.dart
│   │   │   │   │   ├── product_selector.dart
│   │   │   │   │   └── payment_buttons.dart
│   │   │   │   └── providers/
│   │   │   │       └── pos_provider.dart
│   │   │
│   │   ├── money_transfer/             # 🆕 NEW - CRITICAL FEATURE
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── money_transfer.dart
│   │   │   │   │   ├── transfer_platform.dart    # ZAIN, SuperQi, ALTaif
│   │   │   │   │   ├── commission_details.dart   # 2.25% tracking
│   │   │   │   │   └── fraud_alert.dart
│   │   │   │   └── repositories/
│   │   │   │       └── money_transfer_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── money_transfer_page.dart
│   │   │   │   │   ├── transfer_list_page.dart
│   │   │   │   │   ├── transfer_detail_page.dart
│   │   │   │   │   └── commission_report_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── transfer_form.dart
│   │   │   │   │   ├── platform_selector.dart
│   │   │   │   │   ├── commission_calculator.dart
│   │   │   │   │   ├── receipt_uploader.dart
│   │   │   │   │   └── fraud_alert_widget.dart
│   │   │   │   └── providers/
│   │   │   │       └── money_transfer_provider.dart
│   │   │
│   │   ├── gps_tracking/               # 🆕 NEW - CRITICAL FEATURE
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── location_data.dart
│   │   │   │   │   ├── visit_location.dart
│   │   │   │   │   └── route_plan.dart
│   │   │   │   └── repositories/
│   │   │   │       └── location_repository.dart
│   │   │   ├── services/
│   │   │   │   ├── gps_service.dart
│   │   │   │   ├── location_tracker.dart
│   │   │   │   └── geofence_service.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── route_map_page.dart
│   │   │   │   │   ├── visit_tracking_page.dart
│   │   │   │   │   └── location_history_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── map_widget.dart
│   │   │   │   │   ├── location_button.dart
│   │   │   │   │   └── route_planner.dart
│   │   │   │   └── providers/
│   │   │   │       └── gps_provider.dart
│   │   │
│   │   ├── reports/                    # 🆕 NEW
│   │   │   ├── data/
│   │   │   │   ├── models/
│   │   │   │   │   ├── sales_report.dart
│   │   │   │   │   ├── commission_report.dart
│   │   │   │   │   └── visit_report.dart
│   │   │   │   └── repositories/
│   │   │   │       └── report_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── reports_page.dart
│   │   │   │   │   ├── sales_report_page.dart
│   │   │   │   │   ├── commission_report_page.dart
│   │   │   │   │   └── visit_report_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── report_card.dart
│   │   │   │   │   ├── chart_widget.dart
│   │   │   │   │   └── export_button.dart
│   │   │   │   └── providers/
│   │   │   │       └── report_provider.dart
│   │   │
│   │   ├── profile/
│   │   │   ├── data/
│   │   │   │   └── models/
│   │   │   │       └── user_profile.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── profile_page.dart
│   │   │   │   │   └── settings_page.dart
│   │   │   │   └── widgets/
│   │   │   │       ├── profile_header.dart
│   │   │   │       └── settings_item.dart
│   │   │
│   │   └── offline_sync/               # 🆕 NEW
│   │       ├── data/
│   │       │   ├── local/
│   │       │   │   ├── hive_database.dart
│   │       │   │   └── cache_manager.dart
│   │       │   └── repositories/
│   │       │       └── sync_repository.dart
│   │       ├── services/
│   │       │   ├── sync_service.dart
│   │       │   └── connectivity_service.dart
│   │       └── presentation/
│   │           └── widgets/
│   │               └── sync_indicator.dart
│   │
│   ├── shared/                         # Shared widgets and utilities
│   │   ├── widgets/
│   │   │   ├── tsh_button.dart
│   │   │   ├── tsh_card.dart
│   │   │   ├── tsh_text_field.dart
│   │   │   ├── tsh_loading_indicator.dart
│   │   │   ├── tsh_error_widget.dart
│   │   │   └── tsh_bottom_nav.dart
│   │   ├── dialogs/
│   │   │   ├── confirmation_dialog.dart
│   │   │   ├── error_dialog.dart
│   │   │   └── loading_dialog.dart
│   │   └── animations/
│   │       └── page_transitions.dart
│   │
│   ├── routes/
│   │   ├── app_router.dart             # GoRouter configuration
│   │   └── route_guards.dart           # Auth guards
│   │
│   └── main.dart
│
├── assets/
│   ├── images/
│   ├── icons/
│   ├── animations/
│   └── fonts/
│
└── test/
    ├── unit/
    ├── widget/
    └── integration/
```

---

## 📋 Required Features Implementation

### 1. **Money Transfer Management** (CRITICAL)

**Required Features:**
- ✅ Transfer submission with GPS verification
- ✅ Platform selection (ZAIN Cash, SuperQi, ALTaif Bank, Cash)
- ✅ Commission tracking (2.25% calculation)
- ✅ Receipt photo upload
- ✅ Fraud detection alerts
- ✅ Transfer history
- ✅ Commission reports

**Permissions Required:**
```yaml
permissions:
  - camera           # Receipt photos
  - location         # GPS verification
  - storage          # Photo storage
```

### 2. **GPS Tracking & Location Services** (CRITICAL)

**Required Features:**
- ✅ Real-time GPS tracking
- ✅ Visit location verification
- ✅ Route planning
- ✅ Customer location mapping
- ✅ Visit history with locations
- ✅ Geofencing alerts
- ✅ Location-based fraud prevention

**Dependencies:**
```yaml
dependencies:
  geolocator: ^12.0.0
  geocoding: ^3.0.0
  google_maps_flutter: ^2.5.0
  flutter_map: ^6.1.0
```

### 3. **Enhanced Dashboard**

**Required Metrics:**
- Daily sales summary
- Commission earned (2.25%)
- Pending transfers
- Customer visits count
- Orders completed
- Target vs achieved
- Fraud alerts

### 4. **Customer Management Enhancements**

**Required Features:**
- Customer visit logging
- Visit history with GPS
- Route planning
- Customer notes
- Contact management
- Customer location on map

### 5. **Sales & Orders**

**Required Features:**
- Offline order creation
- Order sync when online
- Sales target tracking
- Commission calculator
- Order history
- Invoice generation

### 6. **Reports & Analytics**

**Required Reports:**
- Daily sales report
- Weekly sales summary
- Commission report
- Visit report
- Customer activity report
- Transfer report

### 7. **Offline Support**

**Required Features:**
- Local data caching (Hive)
- Offline order creation
- Background sync
- Sync status indicator
- Conflict resolution

---

## 🔧 Technical Implementation

### Phase 1: Core Infrastructure (Week 1)
1. ✅ Reorganize folder structure
2. ✅ Setup API client with interceptors
3. ✅ Implement authentication flow
4. ✅ Setup state management (Provider)
5. ✅ Configure routing (GoRouter)

### Phase 2: Critical Features (Week 2)
1. ✅ Implement GPS tracking service
2. ✅ Implement money transfer module
3. ✅ Add commission tracking (2.25%)
4. ✅ Implement receipt upload
5. ✅ Add fraud detection alerts

### Phase 3: Customer & Sales (Week 3)
1. ✅ Enhanced customer management
2. ✅ Visit logging with GPS
3. ✅ Route planning
4. ✅ Offline order creation
5. ✅ Order sync

### Phase 4: Reports & Analytics (Week 4)
1. ✅ Dashboard enhancements
2. ✅ Sales reports
3. ✅ Commission reports
4. ✅ Visit reports
5. ✅ Analytics charts

### Phase 5: Offline & Polish (Week 5)
1. ✅ Offline data sync
2. ✅ Background sync service
3. ✅ UI/UX polish
4. ✅ Performance optimization
5. ✅ Testing & bug fixes

---

## 📦 Required Dependencies

```yaml
dependencies:
  # Core
  flutter:
    sdk: flutter

  # State Management
  provider: ^6.1.2
  flutter_bloc: ^8.1.5

  # Navigation
  go_router: ^16.2.4

  # HTTP & API
  http: ^1.2.2
  dio: ^5.7.0

  # Local Storage
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  shared_preferences: ^2.3.2
  path_provider: ^2.1.4

  # GPS & Location - CRITICAL
  geolocator: ^12.0.0
  geocoding: ^3.0.0
  google_maps_flutter: ^2.5.0

  # Camera & Photos
  image_picker: ^1.1.2
  camera: ^0.11.0

  # Permissions
  permission_handler: ^11.3.1

  # Charts & Analytics
  fl_chart: ^1.1.0
  syncfusion_flutter_charts: ^31.1.19

  # Utils
  intl: ^0.20.2
  uuid: ^4.5.1
  logger: ^2.4.0

  # UI Components
  material_design_icons_flutter: ^7.0.7296
  shimmer: ^3.0.0
  cached_network_image: ^3.4.1

  # Connectivity
  connectivity_plus: ^7.0.0
```

---

## 🎯 Key Requirements Checklist

### Salesperson App Must Have:
- ✅ Login with role-based access
- ✅ GPS tracking for all visits
- ✅ Money transfer submission
- ✅ Commission tracking (2.25%)
- ✅ Receipt photo upload
- ✅ Customer visit logging
- ✅ Route planning
- ✅ Offline order creation
- ✅ Sales reports
- ✅ Commission reports
- ✅ Fraud detection alerts
- ✅ Offline sync
- ✅ Arabic/English support

---

## 🚀 Launch Checklist

Before launching the app:
- [ ] All features implemented
- [ ] GPS tracking working
- [ ] Money transfer module tested
- [ ] Offline sync functional
- [ ] All reports generating correctly
- [ ] UI/UX polished
- [ ] Performance optimized
- [ ] Security reviewed
- [ ] Documentation complete
- [ ] User training materials ready

---

## 📱 Expected User Flow

1. **Login** → Authenticate with credentials
2. **Dashboard** → View daily stats, alerts, targets
3. **Start Route** → GPS tracking begins
4. **Visit Customer** → Log visit with GPS
5. **Create Order** → Add items, calculate total
6. **Collect Payment** → Record payment method
7. **Submit Transfer** → Upload receipt, verify GPS, calculate commission
8. **Sync Data** → Background sync when online
9. **View Reports** → Daily sales, commission, visits
10. **End Day** → Submit daily report

---

## 💰 Commission Tracking (2.25%)

**Formula:**
```
Commission = Transfer Amount × 2.25%
```

**Example:**
- Transfer: $1,000 USD
- Commission: $22.50 USD
- Platform: ZAIN Cash
- Receipt: Photo uploaded
- GPS: Location verified
- Status: Pending verification

**Fraud Detection:**
- Commission claimed ≠ Calculated commission → Alert
- GPS location suspicious → Alert
- Receipt missing → Blocked
- Duplicate transfer → Alert

---

## 📊 Dashboard Metrics

### Daily View:
- Total Sales: IQD/USD
- Orders Count: #
- Customers Visited: #
- Transfers Submitted: #
- Commission Earned: IQD/USD
- Pending Verifications: #

### Weekly View:
- Weekly Sales Trend
- Top Customers
- Best Selling Products
- Commission Summary
- Visit Heatmap

### Monthly View:
- Monthly Target vs Achieved
- Commission Report
- Customer Growth
- Performance Score

---

## 🔒 Security Features

1. **Authentication**
   - JWT token-based
   - Secure storage
   - Auto-refresh tokens

2. **GPS Verification**
   - All transfers require GPS
   - Visit logging with location
   - Route tracking

3. **Data Encryption**
   - Local data encrypted
   - Secure API communication
   - Photo encryption

4. **Fraud Prevention**
   - Commission verification
   - Location verification
   - Duplicate detection
   - Suspicious activity alerts

---

## 🎨 UI/UX Guidelines

1. **Arabic-First Design**
   - RTL layout
   - Arabic typography
   - Cultural considerations

2. **Color Scheme**
   - Primary: TSH Green (#1976D2)
   - Success: Green
   - Warning: Orange
   - Error: Red
   - Background: Light gray

3. **Accessibility**
   - Large touch targets
   - High contrast
   - Clear labels
   - Voice feedback

---

## 📝 Next Steps

1. **Review and Approve Plan**
2. **Begin Phase 1: Reorganization**
3. **Implement Critical Features**
4. **Test Each Module**
5. **Launch Beta Version**
6. **Gather Feedback**
7. **Production Release**

---

**Document Version:** 1.0
**Date:** October 6, 2025
**Status:** Ready for Implementation
