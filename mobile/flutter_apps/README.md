# TSH ERP Flutter Apps - Complete Mobile Ecosystem

**Unified Mobile Apps Directory**

All 11 Flutter apps are now organized in a single, consistent location with standardized naming.

---

## 📱 Complete App List

### 01. TSH Admin App
- **Directory**: `01_tsh_admin_app`
- **Package**: `tsh_admin_app`
- **Purpose**: Complete owner dashboard with full project control
- **Users**: Business owners, executives
- **React Module**: Dashboard/Admin
- **Features**:
  - Unified business overview
  - All module dashboards
  - High-level analytics
  - System configuration

---

### 02. TSH Admin Security App
- **Directory**: `02_tsh_admin_security`
- **Package**: `tsh_admin_security`
- **Purpose**: Security management and monitoring
- **Users**: System administrators, security officers
- **React Module**: Security
- **Features**:
  - User management
  - Role & permissions (RBAC)
  - Session monitoring
  - Audit logs
  - Security events
  - Two-factor authentication (2FA)

---

### 03. TSH Accounting App
- **Directory**: `03_tsh_accounting_app`
- **Package**: `tsh_accounting`
- **Purpose**: Field accounting operations
- **Users**: Accountants, financial controllers
- **React Module**: Accounting
- **Features**:
  - Dashboard with accounting equation
  - Journal entries (create/view)
  - Chart of accounts
  - Real-time sync ✅
- **Integration**: WebSocket real-time sync with React Admin
- **Documentation**: See `/apps/accounting_app/INTEGRATION_GUIDE.md`

---

### 04. TSH HR App
- **Directory**: `04_tsh_hr_app`
- **Package**: `tsh_hr_app`
- **Purpose**: Human resources management
- **Users**: HR managers, employees
- **React Module**: HR
- **Features**:
  - Employee management
  - Attendance tracking
  - Leave requests
  - Payroll

---

### 05. TSH Inventory App
- **Directory**: `05_tsh_inventory_app`
- **Package**: `tsh_inventory_app`
- **Purpose**: Warehouse and inventory management
- **Users**: Warehouse staff, inventory managers
- **React Module**: Inventory, Warehouses
- **Features**:
  - Stock management
  - Warehouse operations
  - Receiving goods
  - Stock transfers
  - Cycle counting
  - Barcode scanning

---

### 06. TSH Salesperson App (Field Sales Rep)
- **Directory**: `06_tsh_salesperson_app`
- **Package**: `tsh_salesperson_app`
- **Purpose**: Field sales operations
- **Users**: Field sales representatives
- **React Module**: Sales
- **Features**:
  - Client visits tracking
  - Order creation
  - Product catalog
  - Route planning
  - Performance tracking
  - Offline support

---

### 07. TSH Retail Sales App (POS)
- **Directory**: `07_tsh_retail_sales_app`
- **Package**: `tsh_retail_sales_app`
- **Purpose**: Point of sale for retail operations
- **Users**: Cashiers, store managers
- **React Module**: POS, Sales
- **Features**:
  - Quick checkout
  - Product scanning
  - Payment processing
  - Receipt generation
  - Daily sales reports
  - Offline mode

---

### 08. TSH Partner Network App
- **Directory**: `08_tsh_partner_network_app`
- **Package**: `tsh_partner_network_app`
- **Purpose**: Partner and distributor management
- **Users**: Business partners, distributors
- **React Module**: Sales, Partners
- **Features**:
  - Retailer management
  - Network oversight
  - Commission tracking
  - Order management
  - Performance analytics

---

### 09. TSH Wholesale Client App
- **Directory**: `09_tsh_wholesale_client_app`
- **Package**: `tsh_wholesale_client_app`
- **Purpose**: Wholesale client portal
- **Users**: Wholesale customers, B2B clients
- **React Module**: Customers, Sales
- **Features**:
  - Product browsing
  - Bulk ordering
  - Invoice viewing
  - Payment history
  - Credit management

---

### 10. TSH Consumer App
- **Directory**: `10_tsh_consumer_app`
- **Package**: `tsh_consumer_app`
- **Purpose**: End-consumer e-commerce
- **Users**: End consumers, individual shoppers
- **React Module**: Sales, E-commerce
- **Features**:
  - Product catalog & search
  - Shopping cart
  - Order tracking
  - Wishlist
  - Reviews & ratings
  - Loyalty program

---

### 11. TSH After-Sales Operations App (ASO)
- **Directory**: `11_tsh_aso_app`
- **Package**: `tsh_aso`
- **Purpose**: Service technician operations
- **Users**: Service technicians, maintenance staff
- **React Module**: After-Sales Operations
- **Features**:
  - Service request management
  - Maintenance jobs
  - Returns & inspections
  - Warranty claims
  - QR code scanning
  - Photo documentation
  - Customer signatures
  - Real-time sync ✅
- **Integration**: WebSocket real-time sync with central ERP
- **Documentation**: See `/apps/prss/README.md`

---

## 🗂️ Directory Structure

```
/Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/
│
├── 01_tsh_admin_app/           # Owner Dashboard
├── 02_tsh_admin_security/       # Security Management
├── 03_tsh_accounting_app/       # Accounting Operations
├── 04_tsh_hr_app/               # HR Management
├── 05_tsh_inventory_app/        # Inventory & Warehouse
├── 06_tsh_salesperson_app/      # Field Sales Rep
├── 07_tsh_retail_sales_app/     # Point of Sale (POS)
├── 08_tsh_partner_network_app/  # Partner Management
├── 09_tsh_wholesale_client_app/ # Wholesale Clients
├── 10_tsh_consumer_app/         # Consumer E-commerce
├── 11_tsh_aso_app/              # After-Sales Operations
│
└── shared/                      # Shared code & utilities
```

---

## 📊 Apps by Module

### 🎛️ Admin & System (2 apps)
- 01_tsh_admin_app
- 02_tsh_admin_security

### 📊 Accounting (1 app)
- 03_tsh_accounting_app

### 👥 HR (1 app)
- 04_tsh_hr_app

### 📦 Inventory (1 app)
- 05_tsh_inventory_app

### 💰 Sales (5 apps)
- 06_tsh_salesperson_app (Field Sales)
- 07_tsh_retail_sales_app (POS)
- 08_tsh_partner_network_app (Partners)
- 09_tsh_wholesale_client_app (Wholesale)
- 10_tsh_consumer_app (B2C)

### 🔧 After-Sales Operations (1 app)
- 11_tsh_aso_app

---

## 🏗️ Architecture

All apps follow the **Hub & Spoke Model**:

```
┌─────────────────────────────────────────────────────┐
│        React Admin Web Application                  │
│     (Central Control & Oversight - Hub)             │
└─────────────────────┬───────────────────────────────┘
                      │
         WebSocket Real-Time Sync
                      │
┌─────────────────────┴───────────────────────────────┐
│       PostgreSQL Central Database                    │
│     (Single Source of Truth - Shared by All)        │
└─────────────────────┬───────────────────────────────┘
                      │
          All Apps Read/Write Same Data
                      │
      ┌───────────────┴───────────────┐
      │                               │
┌─────▼─────┐   ┌─────▼─────┐   ┌───▼────┐
│11 Flutter │   │ React     │   │ FastAPI│
│   Apps    │◀──│ Admin     │◀──│Backend │
│  (Mobile) │   │  (Web)    │   │  (API) │
└───────────┘   └───────────┘   └────────┘
```

---

## 🔄 Feature Parity Principle

**Every feature in any Flutter app MUST exist in its corresponding React Admin module.**

React Admin provides:
- ✅ All features from ALL Flutter apps
- ✅ Additional admin-only features (analytics, reports, bulk operations)
- ✅ Centralized oversight across all apps
- ✅ Real-time monitoring via WebSocket

---

## 🚀 Quick Start

### Prerequisites
- Flutter 3.0+
- Dart SDK
- iOS/Android development environment
- Access to TSH ERP central database

### Running an App

```bash
# Navigate to app directory
cd 03_tsh_accounting_app

# Get dependencies
flutter pub get

# Run on connected device
flutter run

# Or run in release mode
flutter run --release

# Or run on specific device
flutter run -d <device-id>
```

### Building for Production

```bash
# iOS
flutter build ios --release

# Android
flutter build apk --release
flutter build appbundle --release
```

---

## 🔐 Authentication

All apps use **centralized JWT authentication**:

1. User logs in via app
2. Backend validates credentials
3. JWT token issued
4. Token stored securely (SharedPreferences/Keychain)
5. Token included in all API requests
6. Token refresh handled automatically

**Base URL**: `http://192.168.68.51:8000` (Development)

---

## 📡 Real-Time Integration

Apps with WebSocket real-time sync:
- ✅ 03_tsh_accounting_app - Journal entries sync
- ✅ 11_tsh_aso_app - Service requests, maintenance jobs sync
- 🔜 Other apps - Implementation pending

**WebSocket Pattern**:
```dart
// 1. Flutter creates/updates record via API
final response = await http.post('$baseUrl/api/endpoint', ...);

// 2. Backend broadcasts to React Admin
await ws_manager.broadcast_event(data);

// 3. React Admin receives update instantly
// Toast notification shown
// UI updated automatically
```

---

## 📝 Development Guidelines

### When Adding New Features:

1. **Check Feature Parity** - See `/FEATURE_PARITY_TRACKER.md`
2. **Backend First** - Implement API endpoint + WebSocket broadcast
3. **Flutter App** - Create mobile UI and connect to API
4. **React Admin** - Add to corresponding module + WebSocket listener
5. **Test Integration** - Verify real-time sync works
6. **Update Docs** - Update tracker and integration guides

### Code Organization:
```
app_name/
├── lib/
│   ├── main.dart              # App entry point
│   ├── config/
│   │   └── app_config.dart    # Configuration (API URL, etc.)
│   ├── models/                # Data models
│   ├── services/
│   │   ├── api_service.dart   # API calls
│   │   └── auth_service.dart  # Authentication
│   ├── screens/               # UI screens
│   ├── widgets/               # Reusable widgets
│   └── utils/                 # Utilities
├── pubspec.yaml               # Dependencies
└── README.md                  # App-specific docs
```

---

## 🔧 Configuration

### ✅ Unified API Configuration

**ALL 11 apps now use the SAME API and SAME database!**

- **API URL**: `http://192.168.68.51:8000` (TSH FastAPI Backend)
- **Database**: PostgreSQL (Centralized ERP Database)
- **Authentication**: JWT tokens (shared across all apps)

Each app has `/lib/config/app_config.dart` or `/lib/config/api_config.dart`:

```dart
class AppConfig {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://192.168.68.51:8000';

  // API Endpoints
  static const String authEndpoint = '/api/auth/login';
  static const String moduleEndpoint = '/api/[module]'; // accounting, hr, sales, etc.

  // WebSocket URL (if applicable)
  static const String wsUrl = 'ws://192.168.68.51:8000';

  // App-specific configuration
  // ...
}
```

**Important Notes**:
- ✅ Use Mac's local IP (192.168.68.51) for device testing, not `localhost`
- ✅ All apps connect to the SAME PostgreSQL database
- ✅ Salesperson app migrated from Odoo to FastAPI (deprecated old config)
- ✅ Use `./verify_api_config.sh` to check all apps are configured correctly

### Verification Script

Run the verification script to ensure all apps use the correct API:

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps
./verify_api_config.sh
```

This will show:
- ✅ Apps using correct API (192.168.68.51:8000)
- ❌ Apps needing configuration updates
- ⚠️  Apps with deprecated configurations

---

## 📚 Documentation

- **Feature Parity Guide**: `/FEATURE_PARITY_GUIDE.md`
- **Feature Parity Tracker**: `/FEATURE_PARITY_TRACKER.md`
- **Accounting Integration**: `/apps/accounting_app/INTEGRATION_GUIDE.md`
- **ASO Integration**: `/apps/prss/ASO_INTEGRATION_GUIDE.md`
- **Backend API**: `/app/routers/` (FastAPI routers)

---

## 🎯 Current Status

**Total Apps**: 11
**Fully Integrated**: 2 (Accounting, ASO)
**In Development**: 9 (Remaining apps)

**Next Priorities**:
1. Complete Accounting app features
2. Integrate Field Sales Rep app (06)
3. Integrate Inventory app (05)
4. Integrate HR app (04)

---

## 🤝 Contributing

When working on apps:
1. Always test on physical devices, not just emulators
2. Ensure offline support where applicable
3. Follow Material Design 3 guidelines
4. Implement proper error handling
5. Add loading states for all async operations
6. Test real-time sync thoroughly

---

## 📞 Support

For issues or questions:
- Check app-specific README in each directory
- Review integration guides
- Check backend API documentation
- Test API endpoints with Postman/Thunder Client

---

**Last Updated**: 2025-01-24

**Maintained by**: TSH ERP Development Team
