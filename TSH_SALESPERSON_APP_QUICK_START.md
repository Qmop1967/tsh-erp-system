# 🚀 TSH Salesperson App - Quick Start Guide

## ✅ What Has Been Done

### 1. New Architecture Created
```
lib/
├── core/              ✅ DONE
│   ├── api/          → API client with interceptors
│   ├── constants/    → App constants & endpoints
│   ├── theme/        → Ready for theme files
│   ├── utils/        → Ready for utilities
│   └── config/       → Ready for configs
│
├── features/          ✅ DONE
│   ├── money_transfer/   → Models & fraud prevention
│   ├── gps_tracking/     → GPS service & models
│   ├── reports/          → Ready for reports
│   └── offline_sync/     → Ready for sync
│
└── shared/            ✅ DONE (folders ready)
    ├── widgets/
    ├── dialogs/
    └── animations/
```

### 2. Critical Files Created

#### Core Infrastructure:
- ✅ `lib/core/api/api_client.dart` - Complete HTTP client
- ✅ `lib/core/constants/api_endpoints.dart` - All API endpoints
- ✅ `lib/core/constants/app_constants.dart` - Commission rates, GPS settings

#### Money Transfer (CRITICAL):
- ✅ `lib/features/money_transfer/data/models/money_transfer.dart`
  - Transfer model with fraud prevention
  - Platform enums (ZAIN, SuperQi, ALTaif, Cash)
  - Commission calculation (2.25%)
  - Fraud alert system

#### GPS Tracking (CRITICAL):
- ✅ `lib/features/gps_tracking/services/gps_service.dart`
  - Real-time GPS tracking
  - Location verification
  - Fraud prevention checks
- ✅ `lib/features/gps_tracking/data/models/location_data.dart`
  - Location data model

### 3. Dependencies Updated
- ✅ Added `geolocator: ^12.0.0` - GPS tracking
- ✅ Added `geocoding: ^3.0.0` - Address from GPS
- ✅ Added `google_maps_flutter: ^2.5.0` - Maps
- ✅ Added `camera: ^0.11.0` - Receipt photos

---

## 📋 Next Steps for Full Implementation

### Phase 1: Money Transfer UI (Priority: CRITICAL)

Create: `lib/features/money_transfer/presentation/pages/money_transfer_page.dart`

**Required Widgets:**
1. GPS verification card (shows location status)
2. Amount input (USD/IQD)
3. Platform selector (ZAIN/SuperQi/ALTaif/Cash)
4. Commission calculator (shows 2.25% automatically)
5. Receipt photo upload
6. Fraud alert display
7. Submit button

**Example Structure:**
```dart
class MoneyTransferPage extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('تحويل الأموال')),
      body: SingleChildScrollView(
        child: Column(
          children: [
            GPSVerificationCard(),
            AmountInputCard(),
            CommissionCalculatorCard(),
            PlatformSelectorCard(),
            ReceiptUploadCard(),
            FraudAlertWidget(),
            SubmitButton(),
          ],
        ),
      ),
    );
  }
}
```

### Phase 2: Provider Implementation

Create: `lib/features/money_transfer/presentation/providers/money_transfer_provider.dart`

**Required Methods:**
```dart
class MoneyTransferProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final GPSService _gpsService;

  // Submit transfer
  Future<void> submitTransfer(MoneyTransfer transfer) async {
    // 1. Verify GPS location
    final locationResult = await _gpsService.verifyLocationForTransfer();

    // 2. Upload receipt photo
    // 3. Calculate commission
    // 4. Submit to API
    // 5. Handle response
  }

  // Get transfer history
  Future<List<MoneyTransfer>> getTransferHistory() async {}

  // Get fraud alerts
  Future<List<FraudAlert>> getFraudAlerts() async {}
}
```

### Phase 3: Repository Layer

Create: `lib/features/money_transfer/data/repositories/money_transfer_repository.dart`

**Methods:**
```dart
class MoneyTransferRepository {
  final ApiClient _apiClient;

  Future<MoneyTransfer> createTransfer(MoneyTransfer transfer) async {
    final response = await _apiClient.post(
      ApiEndpoints.createTransfer,
      data: transfer.toJson(),
    );
    return MoneyTransfer.fromJson(response.data);
  }

  Future<String> uploadReceipt(String transferId, String photoPath) async {
    final response = await _apiClient.uploadFile(
      ApiEndpoints.replaceParams(
        ApiEndpoints.uploadReceipt,
        {'id': transferId},
      ),
      photoPath,
      fieldName: 'receipt',
    );
    return response.data['url'];
  }
}
```

### Phase 4: Update Navigation

Edit: `lib/config/app_routes.dart`

```dart
GoRoute(
  path: '/money-transfer',
  name: 'money-transfer',
  builder: (context, state) => const MoneyTransferPage(),
),
GoRoute(
  path: '/transfer-history',
  name: 'transfer-history',
  builder: (context, state) => const TransferHistoryPage(),
),
```

### Phase 5: Update Home Page Navigation

Edit: `lib/pages/home/home_page.dart`

Add Money Transfer to bottom navigation or menu:
```dart
BottomNavigationBarItem(
  icon: Icon(MdiIcons.bankTransfer),
  label: 'التحويلات',
),
```

---

## 🔧 How to Use the New Features

### Using GPS Service:

```dart
import '../features/gps_tracking/services/gps_service.dart';

final gpsService = GPSService();

// Get current location
final location = await gpsService.getCurrentLocation();
print('Location: ${location?.latitude}, ${location?.longitude}');

// Verify location for transfer
final verification = await gpsService.verifyLocationForTransfer();
if (verification.isValid) {
  print('Location verified!');
} else {
  print('Location verification failed: ${verification.message}');
}
```

### Using Money Transfer Model:

```dart
import '../features/money_transfer/data/models/money_transfer.dart';

// Create a transfer
final transfer = MoneyTransfer(
  salespersonId: '123',
  amountUSD: 1000.0,
  amountIQD: 1450000.0,
  platform: TransferPlatform.zainCash,
  commissionAmount: MoneyTransfer.calculateCommission(1000.0),
  claimedCommission: 22.50,
  location: locationData,
  createdAt: DateTime.now(),
);

// Check if commission is valid
if (transfer.isCommissionValid()) {
  print('Commission is correct!');
} else {
  print('Commission mismatch detected!');
}
```

### Using API Client:

```dart
import '../core/api/api_client.dart';
import '../core/constants/api_endpoints.dart';

final apiClient = ApiClient();

// Login
await apiClient.setAuthToken(token);

// Get dashboard stats
final response = await apiClient.get(ApiEndpoints.dashboardStats);

// Create transfer
final response = await apiClient.post(
  ApiEndpoints.createTransfer,
  data: transfer.toJson(),
);

// Upload receipt
final response = await apiClient.uploadFile(
  ApiEndpoints.uploadReceipt,
  '/path/to/photo.jpg',
);
```

---

## 📱 Testing the App

### 1. Install Dependencies:
```bash
flutter pub get
```

### 2. Run the App:
```bash
# For web
flutter run -d chrome

# For iOS
flutter run -d "iPhone 15 Pro"

# For Android
flutter run
```

### 3. Test GPS Service:
```bash
# Create a test file
lib/features/gps_tracking/services/gps_service_test.dart
```

```dart
void main() async {
  final gpsService = GPSService();

  // Test location
  final location = await gpsService.getCurrentLocation();
  print('Location: $location');

  // Test verification
  final verification = await gpsService.verifyLocationForTransfer();
  print('Verification: ${verification.isValid}');
}
```

---

## 🎯 Features Ready to Use

### ✅ Implemented:
1. **GPS Service** - Full location tracking
2. **Money Transfer Models** - All data structures
3. **Commission Calculator** - 2.25% automatic
4. **Fraud Alert System** - Critical/High/Medium/Low
5. **API Client** - Complete HTTP infrastructure
6. **All Endpoints** - Mapped and ready
7. **Platform Support** - ZAIN, SuperQi, ALTaif, Cash

### 🔄 Needs UI Implementation:
1. Money Transfer Page
2. GPS Map Display
3. Transfer History Page
4. Fraud Alert Dashboard
5. Commission Reports
6. Visit Tracking Page

---

## 📊 Expected User Flow

```
1. Login ✅
   ↓
2. Dashboard (shows today's stats) ✅
   ↓
3. Money Transfer 🆕
   ├── Verify GPS ✅
   ├── Enter Amount 🔄 (needs UI)
   ├── Calculate Commission (2.25%) ✅
   ├── Select Platform ✅
   ├── Upload Receipt 🔄 (needs UI)
   └── Submit ✅
   ↓
4. View Transfer History 🔄 (needs UI)
   ↓
5. Check Fraud Alerts ✅
   ↓
6. View Commission Report 🔄 (needs UI)
```

---

## 🔒 Security Checklist

### ✅ Implemented:
- [x] GPS verification for all transfers
- [x] Commission validation (2.25%)
- [x] Fraud alert system
- [x] Location accuracy checking
- [x] JWT authentication
- [x] Secure API client

### 🔄 Needs Implementation:
- [ ] Receipt photo encryption
- [ ] Offline data encryption
- [ ] Biometric authentication
- [ ] Session timeout

---

## 💡 Pro Tips

### 1. GPS Testing:
- Use real device for accurate GPS
- Simulator/emulator may have limited GPS
- Test in different locations

### 2. Commission Calculation:
```dart
// Always use the helper method
final commission = MoneyTransfer.calculateCommission(amount);

// Don't calculate manually
final commission = amount * 0.0225; // ❌ Don't do this
```

### 3. Error Handling:
```dart
try {
  final location = await gpsService.getCurrentLocation();
} catch (e) {
  // Handle GPS errors
  showDialog(context, 'GPS Error: $e');
}
```

### 4. Testing Fraud Detection:
```dart
// Test with mismatched commission
final transfer = MoneyTransfer(
  commissionAmount: 22.50,
  claimedCommission: 25.00, // Mismatch!
);

if (!transfer.isCommissionValid()) {
  print('Fraud detected!'); // This will trigger
}
```

---

## 📞 Common Issues & Solutions

### Issue 1: GPS Not Working
**Solution:**
1. Check permissions in `AndroidManifest.xml` and `Info.plist`
2. Request permissions at runtime
3. Enable location services on device

### Issue 2: API Connection Failed
**Solution:**
1. Verify backend is running: `http://localhost:8000/docs`
2. Check API base URL in `api_endpoints.dart`
3. Verify JWT token is set

### Issue 3: Dependencies Error
**Solution:**
```bash
flutter clean
flutter pub get
flutter pub upgrade
```

---

## 🎉 You're Ready!

The **critical infrastructure** is now in place:
- ✅ GPS tracking service
- ✅ Money transfer models
- ✅ Fraud prevention system
- ✅ API client
- ✅ All endpoints
- ✅ Commission calculator (2.25%)

**Next:** Build the UI and connect everything together!

---

**Quick Commands:**
```bash
# Get dependencies
flutter pub get

# Run app
flutter run

# Clean build
flutter clean

# Analyze code
flutter analyze
```

**Files to Edit Next:**
1. `lib/features/money_transfer/presentation/pages/money_transfer_page.dart` (create)
2. `lib/features/money_transfer/presentation/providers/money_transfer_provider.dart` (create)
3. `lib/config/app_routes.dart` (add routes)
4. `lib/pages/home/home_page.dart` (add navigation)

**Good Luck! 🚀**
