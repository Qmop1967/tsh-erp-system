# 🔌 Backend Integration Guide
## TSH Field Sales Rep App - API Integration

**Date:** November 15, 2025
**Version:** 1.0.0
**Status:** Phase 4 - Backend Integration Complete (Code Ready, Backend Pending)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [API Services Created](#api-services-created)
3. [Backend Endpoints Required](#backend-endpoints-required)
4. [Authentication Flow](#authentication-flow)
5. [Sync Manager](#sync-manager)
6. [Implementation Guide](#implementation-guide)
7. [Testing Checklist](#testing-checklist)

---

## 🎯 Overview

This document describes the complete backend integration architecture for the TSH Field Sales Rep App. All API service layers have been implemented on the Flutter side and are ready to connect to the TSH ERP backend.

### What's Been Built

✅ **API Client** (`lib/services/api/api_client.dart`)
- Base HTTP client with authentication
- Error handling and response parsing
- Support for GET, POST, PUT, DELETE, file upload/download
- Automatic JWT token management

✅ **GPS API Service** (`lib/services/api/gps_api_service.dart`)
- Upload location tracking data
- Batch sync offline GPS data
- Get location history and summaries
- Verify customer visits

✅ **Transfer API Service** (`lib/services/api/transfer_api_service.dart`)
- Create money transfers
- Upload receipt photos
- Get transfer history and summaries
- Verify and manage transfers

✅ **Commission API Service** (`lib/services/api/commission_api_service.dart`)
- Get commission summaries and history
- Calculate commission previews
- Manage sales targets
- Get leaderboard rankings

✅ **Sync Manager** (`lib/services/api/sync_manager.dart`)
- Automatic background sync every 15 minutes
- Connectivity monitoring
- Batch upload offline data
- Conflict resolution

---

## 🔧 API Services Created

### 1. ApiClient (Base Service)

**Location:** `lib/services/api/api_client.dart`

**Features:**
- Centralized HTTP client for all API calls
- Automatic JWT token injection
- Request/response logging
- Error handling and parsing
- Timeout management (30 seconds)
- Environment configuration (prod/staging/dev)

**Key Methods:**
```dart
Future<ApiResponse> get(String endpoint, {Map<String, dynamic>? queryParameters})
Future<ApiResponse> post(String endpoint, {dynamic body})
Future<ApiResponse> put(String endpoint, {dynamic body})
Future<ApiResponse> delete(String endpoint)
Future<ApiResponse> uploadFile(String endpoint, {required String filePath})
Future<ApiResponse> downloadFile(String endpoint)
```

**Configuration:**
```dart
// Base URLs (configurable)
Production: https://erp.tsh.sale/api
Staging: https://staging.erp.tsh.sale/api
Development: http://localhost:8000/api

// Current environment
static const String _environment = 'production';
```

### 2. GpsApiService

**Location:** `lib/services/api/gps_api_service.dart`

**Endpoints:**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/bff/salesperson/gps/track` | Upload single location |
| POST | `/bff/salesperson/gps/track/batch` | Batch upload offline locations |
| GET | `/bff/salesperson/gps/history` | Get location history |
| GET | `/bff/salesperson/gps/summary/daily` | Get daily tracking summary |
| GET | `/bff/salesperson/gps/summary/weekly` | Get weekly tracking summary |
| POST | `/bff/salesperson/gps/verify-visit` | Verify customer visit location |
| GET | `/bff/salesperson/gps/sync-status` | Get sync status |
| DELETE | `/bff/salesperson/gps/locations/{id}` | Delete location record |

**Key Features:**
- Real-time location upload
- Batch sync for offline data
- Customer visit verification with geofencing
- Daily/weekly analytics

### 3. TransferApiService

**Location:** `lib/services/api/transfer_api_service.dart`

**Endpoints:**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/bff/salesperson/transfers/create` | Create new transfer |
| POST | `/bff/salesperson/transfers/{id}/receipt` | Upload receipt photo |
| GET | `/bff/salesperson/transfers/list` | Get transfer list with filters |
| GET | `/bff/salesperson/transfers/{id}` | Get transfer details |
| PUT | `/bff/salesperson/transfers/{id}/verify` | Update transfer status |
| GET | `/bff/salesperson/transfers/balance` | Get cash box balance |
| GET | `/bff/salesperson/transfers/summary/daily` | Get daily summary |
| GET | `/bff/salesperson/transfers/summary/weekly` | Get weekly summary |
| POST | `/bff/salesperson/transfers/sync` | Batch sync offline transfers |
| POST | `/bff/salesperson/transfers/{id}/whatsapp` | Send WhatsApp verification |
| PUT | `/bff/salesperson/transfers/{id}/cancel` | Cancel transfer |

**Key Features:**
- ALTaif, ZAIN Cash, SuperQi support
- Receipt photo upload (multipart/form-data)
- Cash box balance tracking
- WhatsApp verification integration

### 4. CommissionApiService

**Location:** `lib/services/api/commission_api_service.dart`

**Endpoints:**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/bff/salesperson/commissions/summary` | Get commission summary by period |
| GET | `/bff/salesperson/commissions/history` | Get commission history |
| GET | `/bff/salesperson/commissions/{id}` | Get commission details |
| POST | `/bff/salesperson/commissions/calculate` | Calculate commission preview |
| GET | `/bff/salesperson/commissions/targets` | Get sales target |
| POST | `/bff/salesperson/commissions/targets/set` | Set sales target |
| GET | `/bff/salesperson/commissions/leaderboard` | Get team leaderboard |
| GET | `/bff/salesperson/commissions/weekly-earnings` | Get weekly earnings breakdown |
| PUT | `/bff/salesperson/commissions/{id}/status` | Update commission status |
| PUT | `/bff/salesperson/commissions/{id}/mark-paid` | Mark commission as paid |
| GET | `/bff/salesperson/commissions/statistics` | Get commission statistics |
| POST | `/bff/salesperson/commissions/request-payout` | Request payout |

**Key Features:**
- 2.25% automatic calculation
- Multi-period views (today, week, month, all-time)
- Sales target tracking
- Team leaderboard with rankings
- Payout request workflow

### 5. SyncManager

**Location:** `lib/services/api/sync_manager.dart`

**Features:**
- Automatic periodic sync (every 15 minutes)
- Connectivity monitoring
- Batch upload of offline GPS locations
- Batch upload of offline transfers
- Pending sync count tracking
- Force sync capability
- Sync status callbacks

**Key Methods:**
```dart
Future<void> initialize()
Future<SyncResult> syncAll({int? salespersonId})
Future<Map<String, int>> getPendingSyncCount()
Future<SyncResult> forceSyncNow({int? salespersonId})
void setAutoSync(bool enabled)
void startPeriodicSync({Duration? interval})
void stopPeriodicSync()
```

---

## 🌐 Backend Endpoints Required

### Required BFF (Backend for Frontend) Endpoints

All endpoints must be created under the `/api/bff/salesperson/` prefix in the TSH ERP backend.

#### GPS Tracking Endpoints

```python
# app/routers/bff/salesperson_gps.py

@router.post("/gps/track")
async def track_location(
    location: GPSLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload single GPS location
    Body: {latitude, longitude, timestamp, accuracy, altitude, speed, heading}
    Response: {success: true, location_id: 123}
    """
    pass

@router.post("/gps/track/batch")
async def batch_track_locations(
    request: BatchLocationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Batch upload GPS locations (for offline sync)
    Body: {locations: []}
    Response: {uploaded: 10, failed: 0, errors: []}
    """
    pass

@router.get("/gps/history")
async def get_location_history(
    salesperson_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get GPS location history
    Response: {locations: [...]}
    """
    pass

@router.get("/gps/summary/daily")
async def get_daily_summary(
    salesperson_id: int,
    date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily GPS tracking summary
    Response: {total_distance, total_duration, customer_visits, route: []}
    """
    pass

@router.get("/gps/summary/weekly")
async def get_weekly_summary(
    salesperson_id: int,
    week_start: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly GPS tracking summary
    Response: {total_distance, total_duration, daily_breakdown: []}
    """
    pass

@router.post("/gps/verify-visit")
async def verify_customer_visit(
    request: VerifyVisitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify customer visit using GPS coordinates
    Body: {customer_id, latitude, longitude, visit_time}
    Response: {verified: true, distance_from_customer: 50, within_geofence: true}
    """
    pass
```

#### Money Transfer Endpoints

```python
# app/routers/bff/salesperson_transfers.py

@router.post("/transfers/create")
async def create_transfer(
    transfer: MoneyTransferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new money transfer
    Body: {method, amount, currency, latitude, longitude, reference_number, ...}
    Response: {transfer_id, reference_number, status, message}
    """
    pass

@router.post("/transfers/{transfer_id}/receipt")
async def upload_receipt(
    transfer_id: int,
    receipt_photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload receipt photo (multipart/form-data)
    Response: {photo_url, uploaded_at}
    """
    pass

@router.get("/transfers/list")
async def get_transfer_list(
    salesperson_id: int,
    status: Optional[str] = None,
    method: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transfer list with filters
    Response: {transfers: [...], total: 50}
    """
    pass

@router.get("/transfers/balance")
async def get_cash_box_balance(
    salesperson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cash box balance by payment method
    Response: {cashIQD, cashUSD, altaifIQD, zainCashIQD, superQiIQD, totalIQD}
    """
    pass

@router.post("/transfers/sync")
async def batch_sync_transfers(
    request: BatchTransferSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Batch sync offline transfers
    Body: {transfers: [...]}
    Response: {synced: 5, failed: 0, errors: [], transfer_ids: []}
    """
    pass
```

#### Commission Endpoints

```python
# app/routers/bff/salesperson_commissions.py

@router.get("/commissions/summary")
async def get_commission_summary(
    salesperson_id: int,
    period: str = "month",  # today, week, month, all
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get commission summary for period
    Response: {totalCommission, pendingCommission, paidCommission, totalSales, ordersCount}
    """
    pass

@router.get("/commissions/history")
async def get_commission_history(
    salesperson_id: int,
    status: Optional[str] = None,
    period: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get commission history
    Response: {commissions: [...]}
    """
    pass

@router.post("/commissions/calculate")
async def calculate_commission(
    request: CalculateCommissionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate commission preview
    Body: {sales_amount, commission_rate}
    Response: {sales_amount, commission_rate, commission_amount, estimated_payout}
    """
    pass

@router.get("/commissions/leaderboard")
async def get_leaderboard(
    period: str = "month",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get team leaderboard
    Response: {leaderboard: [{rank, name, totalSales, totalCommission, ordersCount}, ...]}
    """
    pass

@router.get("/commissions/targets")
async def get_sales_target(
    salesperson_id: int,
    period: str = "monthly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get sales target
    Response: {targetAmount, currentAmount, progressPercentage, isAchieved, ...}
    """
    pass

@router.post("/commissions/targets/set")
async def set_sales_target(
    request: SetTargetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set sales target
    Body: {salesperson_id, target_amount, period}
    Response: {target_id, target_amount, period, starts_at, ends_at}
    """
    pass
```

---

## 🔐 Authentication Flow

### JWT Token Management

The app uses JWT (JSON Web Token) for authentication:

1. **Login** → Store `access_token` in SharedPreferences
2. **API Calls** → Inject token in `Authorization: Bearer {token}` header
3. **Token Refresh** → Automatic refresh when expired (401 response)
4. **Logout** → Clear token from storage

### Current Implementation

```dart
// Already implemented in lib/services/auth_service.dart

// Login
final authModel = await authService.login(email, password);
// Token stored automatically in SharedPreferences

// API calls automatically include token
final response = await apiClient.get('/bff/salesperson/gps/history');
// Header: Authorization: Bearer {token}

// Logout
await authService.logout();
// Token cleared from storage
```

---

## 🔄 Sync Manager

### How It Works

1. **Initialization**
   ```dart
   final syncManager = SyncManager();
   await syncManager.initialize();
   ```

2. **Automatic Sync** (every 15 minutes)
   - Checks connectivity
   - Uploads unsync GPS locations (where `isSynced == false`)
   - Uploads unsynced transfers (where `isSynced == false`)
   - Marks successfully synced records as `isSynced = true`

3. **Manual Sync**
   ```dart
   final result = await syncManager.forceSyncNow(salespersonId: userId);
   print('Uploaded: ${result.totalUploaded}, Failed: ${result.totalFailed}');
   ```

4. **Pending Count**
   ```dart
   final pending = await syncManager.getPendingSyncCount();
   print('Pending GPS: ${pending['gps']}');
   print('Pending Transfers: ${pending['transfers']}');
   ```

### Sync Strategy

**Offline-First Architecture:**
1. User performs action (e.g., record transfer)
2. Data saved to local Hive database immediately
3. Marked as `isSynced = false`
4. Background sync picks it up on next cycle
5. Uploads to backend
6. On success, marked as `isSynced = true`
7. On failure, retries on next sync cycle

---

## 📝 Implementation Guide

### Step 1: Enable Backend Integration

Currently, all features use local storage only. To enable backend integration:

**GPS Tracking Service:**
```dart
// lib/services/gps/gps_tracking_service.dart

import '../api/gps_api_service.dart';

class GPSTrackingService {
  final GpsApiService _gpsApi = GpsApiService();

  Future<void> trackLocation(...) async {
    // Save to Hive (existing code)
    await _locationsBox.add(location);

    // NEW: Upload to backend immediately (if online)
    try {
      final uploaded = await _gpsApi.uploadLocation(location);
      if (uploaded) {
        location.isSynced = true;
        await location.save();
      }
    } catch (e) {
      // Will be synced by SyncManager later
      print('Upload failed, will sync later: $e');
    }
  }
}
```

**Transfer Service:**
```dart
// lib/services/transfers/transfer_service.dart

import '../api/transfer_api_service.dart';

class TransferService {
  final TransferApiService _transferApi = TransferApiService();

  Future<MoneyTransfer> createTransfer(...) async {
    // Save to Hive (existing code)
    await _transfersBox.add(transfer);

    // NEW: Upload to backend immediately (if online)
    try {
      final result = await _transferApi.createTransfer(transfer);
      if (result['success'] == true) {
        transfer.backendId = result['transfer_id'];
        transfer.isSynced = true;
        await transfer.save();
      }
    } catch (e) {
      // Will be synced by SyncManager later
      print('Upload failed, will sync later: $e');
    }

    return transfer;
  }
}
```

**Commission Service:**
```dart
// lib/services/commission/commission_service.dart

import '../api/commission_api_service.dart';

class CommissionService {
  final CommissionApiService _commissionApi = CommissionApiService();

  Future<CommissionSummary> getSummary(int salespersonId, String period) async {
    // Try to get from backend first
    try {
      final summary = await _commissionApi.getCommissionSummary(
        salespersonId: salespersonId,
        period: period,
      );

      if (summary != null) {
        return summary;
      }
    } catch (e) {
      print('Failed to get from backend, using local: $e');
    }

    // Fallback to local calculation (existing code)
    return _calculateLocalSummary(salespersonId, period);
  }
}
```

### Step 2: Initialize Sync Manager

**In main.dart:**
```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Hive
  await Hive.initFlutter();

  // Initialize Sync Manager
  final syncManager = SyncManager();
  await syncManager.initialize();

  // Set up callbacks
  syncManager.onSyncStatusChanged = (status) {
    print('Sync status: $status');
  };

  syncManager.onSyncCompleted = (result) {
    print('Sync completed: ${result.totalUploaded} uploaded');
  };

  runApp(MyApp());
}
```

### Step 3: Add Sync Status UI

**Show pending sync count in UI:**
```dart
// Example: In HomePage
FutureBuilder<Map<String, int>>(
  future: syncManager.getPendingSyncCount(),
  builder: (context, snapshot) {
    if (snapshot.hasData) {
      final pending = snapshot.data!;
      return Badge(
        label: Text('${pending['total']}'),
        child: Icon(Icons.sync),
      );
    }
    return Icon(Icons.sync);
  },
)
```

**Add manual sync button:**
```dart
IconButton(
  icon: Icon(Icons.sync),
  onPressed: () async {
    final userId = authProvider.user?.id ?? 1;
    final result = await syncManager.forceSyncNow(salespersonId: userId);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          result.success
            ? 'تم المزامنة بنجاح: ${result.totalUploaded} سجل'
            : 'فشلت المزامنة: ${result.message}',
        ),
      ),
    );
  },
)
```

---

## ✅ Testing Checklist

### Backend Development Tasks

- [ ] Create BFF router files
  - [ ] `app/routers/bff/salesperson_gps.py`
  - [ ] `app/routers/bff/salesperson_transfers.py`
  - [ ] `app/routers/bff/salesperson_commissions.py`

- [ ] Create database models
  - [ ] `GPSLocation` model
  - [ ] `MoneyTransfer` model
  - [ ] `Commission` model
  - [ ] `SalesTarget` model

- [ ] Implement authentication
  - [ ] JWT token validation
  - [ ] Role-based access control
  - [ ] Salesperson-specific data filtering

- [ ] Implement GPS endpoints
  - [ ] Single location upload
  - [ ] Batch location upload
  - [ ] Location history with pagination
  - [ ] Daily/weekly summaries
  - [ ] Customer visit verification

- [ ] Implement Transfer endpoints
  - [ ] Create transfer with GPS coordinates
  - [ ] Upload receipt photo (multipart)
  - [ ] Transfer list with filters
  - [ ] Cash box balance calculation
  - [ ] Batch sync endpoint

- [ ] Implement Commission endpoints
  - [ ] Commission summary by period
  - [ ] Commission history
  - [ ] Calculate commission preview
  - [ ] Sales target CRUD
  - [ ] Leaderboard rankings

### Mobile Integration Tasks

- [ ] Enable backend calls in services
  - [ ] Update `GPSTrackingService`
  - [ ] Update `TransferService`
  - [ ] Update `CommissionService`

- [ ] Initialize Sync Manager in main.dart
- [ ] Add sync status UI indicators
- [ ] Add manual sync button
- [ ] Test offline mode
- [ ] Test online mode
- [ ] Test sync after reconnection

### End-to-End Testing

- [ ] Test GPS tracking upload
- [ ] Test batch GPS sync (offline → online)
- [ ] Test transfer creation and upload
- [ ] Test receipt photo upload
- [ ] Test commission calculations
- [ ] Test sales target setting
- [ ] Test leaderboard display
- [ ] Test sync manager automatic sync
- [ ] Test force sync functionality
- [ ] Test error handling and retry

---

## 🎉 Next Steps

1. **Backend Development**
   - Create all required BFF endpoints in TSH ERP backend
   - Implement database models and migrations
   - Add authentication and authorization
   - Test endpoints with Postman/curl

2. **Mobile Integration**
   - Enable backend calls in existing services
   - Initialize SyncManager in main.dart
   - Add sync status UI
   - Test offline/online scenarios

3. **Testing & Deployment**
   - Test on staging environment
   - Verify all sync scenarios
   - Performance testing with real data
   - Deploy to production

---

**Built with ❤️ for TSH ERP System**
**Status:** ✅ API Services Complete - Ready for Backend Implementation
**Next Phase:** Backend BFF Endpoint Development
**Business Value:** Real-time sync + offline capability + fraud prevention
