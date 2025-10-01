# 📱 TSH ERP System - Mobile Applications

## Overview
Complete mobile ecosystem for TSH ERP System with 8 specialized applications serving different business units and user roles.

## Applications

### 01 - TSH Admin App
**Purpose:** Complete owner/admin dashboard with full project control  
**Users:** Business owner, system administrators  
**Bundle ID:** `com.tsh.admin`  
**Features:**
- Complete system overview
- Financial reports and analytics
- User management
- System configuration
- Real-time business metrics

### 02 - TSH HR App
**Purpose:** Complete HR management system  
**Users:** HR Director, HR team (19 employees)  
**Bundle ID:** `com.tsh.hr`  
**Features:**
- Payroll management
- Attendance tracking with WhatsApp integration
- Performance reviews
- Employee database
- Leave management
- Bilingual (Arabic/English) with RTL support

### 03 - TSH Inventory App
**Purpose:** Multi-location inventory tracking and management  
**Users:** Inventory managers, warehouse staff  
**Bundle ID:** `com.tsh.inventory`  
**Features:**
- Google Lens image recognition for inventory
- Damage and returns tracking
- Multi-location management
- Reorder point automation
- Stock alerts
- Slow-moving inventory reports
- 3000+ items with images from Zoho

### 04 - TSH Retail Sales App
**Purpose:** Retail shop operations and customer management  
**Users:** Retail shop staff (small town inside Baghdad)  
**Bundle ID:** `com.tsh.retailsales`  
**Features:**
- 30 daily retail customers (1M IQD average)
- Warranty tracking
- Returns and exchanges
- Daily margin reports
- Payment reminders
- Customer database
- POS integration

### 05 - TSH Salesperson App (MERGED & ENHANCED)
**Purpose:** Unified app for travel and partner salespersons  
**Users:** 12 travel salespersons + 100+ partner salesmen  
**Bundle ID:** `com.tsh.salesperson`  
**Features:**

#### Travel Salesperson Features:
- All-day GPS tracking with geofencing
- Fraud prevention system
- Money transfer tracking (ALTaif, ZAIN Cash, SuperQi)
- Weekly financial management ($35K USD)
- Commission calculations (2.25%)
- Receipt verification via WhatsApp
- Location-based sales tracking
- Transfer verification system

#### Partner Salesman Features:
- Social media seller management
- Order placement and tracking
- Commission tracking
- Customer assignment
- Product catalog access
- Price list management (5 tiers)
- Third-party delivery integration

#### Shared Features:
- Bilingual (Arabic/English)
- Offline mode
- Real-time sync
- Push notifications
- Analytics dashboard

### 06 - TSH Partner Network App
**Purpose:** Partner salesmen network management  
**Users:** 100+ partner salesmen across all Iraq cities  
**Bundle ID:** `com.tsh.partnernetwork`  
**Features:**
- Nationwide network management
- Starting with 20, scaling to 100+
- Multi-city coordination
- Performance tracking
- Training resources
- Communication hub

### 07 - TSH Wholesale Client App
**Purpose:** B2B wholesale client portal  
**Users:** 500+ wholesale business clients  
**Bundle ID:** `com.tsh.wholesaleclient`  
**Features:**
- 30 daily wholesale orders
- Bulk ordering
- Payment terms management
- Order history (2000+ customers from Zoho)
- Price negotiations
- Credit management
- Invoice tracking
- Relationship management

### 08 - TSH Consumer App
**Purpose:** Direct consumer B2C marketplace  
**Users:** End consumers  
**Bundle ID:** `com.tsh.consumer`  
**Features:**
- Product browsing and search
- Online ordering
- Delivery tracking
- Customer reviews
- Wishlist
- Payment integration
- 24/7 bilingual AI customer assistant
- Order history
- Returns management

## Shared Components

### tsh_core_package
Shared utilities, models, widgets, and business logic used across all apps.

**Includes:**
- API client
- Authentication
- Data models
- Shared widgets
- Utilities
- Constants
- Theme system
- Localization

## Technical Stack

- **Framework:** Flutter 3.35.5+
- **Language:** Dart 3.0+
- **State Management:** Provider + BLoC
- **Navigation:** GoRouter
- **API:** RESTful + WebSocket
- **Storage:** Hive + SharedPreferences
- **Localization:** Arabic + English with RTL support
- **Platforms:** iOS, Android, Web

## Deployment

### iOS Deployment
Each app can be deployed to iPhone/iPad:
1. Open `ios/Runner.xcworkspace` in Xcode
2. Configure Signing & Capabilities
3. Select your Apple Developer team
4. Build and deploy

### Android Deployment
Each app can be built for Android:
```bash
flutter build apk --release
```

### Web Deployment
Progressive Web App support:
```bash
flutter build web --release
```

## Development Commands

```bash
# Navigate to specific app
cd mobile/flutter_apps/01_tsh_admin_app

# Install dependencies
flutter pub get

# Run in debug mode
flutter run

# Build for iOS
flutter build ios

# Build for Android
flutter build apk

# Run tests
flutter test
```

## Scalability Features

### Current Scale
- 19 employees (HR app)
- 12 travel salespersons (GPS tracking)
- 100+ partner salesmen (growing)
- 500+ wholesale clients
- 30 daily retail customers
- 2000+ customer records from Zoho
- 3000+ inventory items with images

### Designed to Scale
- Multi-location inventory (expansion ready)
- Multi-city partner network
- Nationwide e-commerce platform
- 1000+ client capacity
- Additional retail locations

### Performance Optimizations
- Lazy loading
- Image caching
- Offline-first architecture
- Incremental sync
- Database indexing
- API request batching

## Security

- End-to-end encryption for financial data
- Secure authentication (JWT)
- Fraud prevention algorithms
- GPS verification
- Receipt validation
- Role-based access control
- Audit logging

## Data Sources

All apps sync with central backend:
- **Customer Data:** 2000+ records from Zoho
- **Inventory:** 3000+ items with images from Zoho
- **Vendor Data:** 200+ vendors from Zoho
- **Real-time Sync:** WebSocket for live updates

## Support

- Bilingual support (Arabic/English)
- 24/7 AI customer assistant
- WhatsApp integration for communication
- In-app help and tutorials

## Backup & Recovery

- Daily automated backups
- Cloud sync
- Local data persistence
- Disaster recovery plan

---

**Last Updated:** September 30, 2025  
**System Version:** TSH ERP v1.0  
**Total Apps:** 8 production apps + 1 shared package
