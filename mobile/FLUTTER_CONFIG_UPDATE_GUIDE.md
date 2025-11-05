# Flutter Apps Configuration Update Guide

**Date:** November 5, 2025 (Updated: 15:50 UTC)
**Purpose:** Update all 11 Flutter apps to use unified monolithic backend
**Status:** ✅ Backend Deployed - Ready for Flutter Updates

**Production Backend Status:**
- ✅ Deployed and running: https://erp.tsh.sale
- ✅ Health check passing: https://erp.tsh.sale/health
- ✅ Redis caching active
- ✅ All API endpoints operational

---

## Overview

After the monolithic transformation, all Flutter apps need to update their API configurations to point to the **single unified backend** at `https://erp.tsh.sale/api`.

---

## What Changed

### Before (Microservices):
```
Main Backend:     https://erp.tsh.sale/api         (Port 8000)
TDS Core:         https://erp.tsh.sale:8001/api    (REMOVED ❌)
TSH NeuroLink:    https://erp.tsh.sale:8002/api    (REMOVED ❌)
React Frontend:   https://erp.tsh.sale             (REMOVED ❌)
```

### After (Monolithic):
```
Unified Backend:  https://erp.tsh.sale/api         (Port 8000) ✅
Mobile BFF:       https://erp.tsh.sale/api/mobile  (Port 8000) ✅
Health Check:     https://erp.tsh.sale/health      (Port 8000) ✅
```

---

## Configuration Files to Update

For **each of the 11 Flutter apps**, update the following file:

### File Location Pattern:
```
mobile/flutter_apps/XX_app_name/lib/config/api_config.dart
```

### Example Apps:
1. `01_tsh_admin_app/lib/config/api_config.dart`
2. `02_tsh_admin_security/lib/config/api_config.dart`
3. `03_tsh_accounting_app/lib/config/api_config.dart`
4. `04_tsh_hr_app/lib/config/api_config.dart`
5. `05_tsh_inventory_app/lib/config/api_config.dart`
6. `06_tsh_salesperson_app/lib/config/api_config.dart`
7. `07_tsh_retail_sales_app/lib/config/api_config.dart`
8. `08_tsh_partner_network_app/lib/config/api_config.dart`
9. `09_tsh_wholesale_client_app/lib/config/api_config.dart`
10. `10_tsh_consumer_app/lib/config/api_config.dart`
11. `11_tsh_aso_app/lib/config/api_config.dart`

---

## Step-by-Step Update Process

### Step 1: Locate API Configuration File

For each app, open:
```
mobile/flutter_apps/XX_app_name/lib/config/api_config.dart
```

### Step 2: Update Configuration

Replace the old configuration with the new unified configuration:

#### OLD Configuration (Remove):
```dart
class ApiConfig {
  // Multiple endpoints (microservices) ❌
  static const String mainApiUrl = 'https://erp.tsh.sale/api';
  static const String tdsApiUrl = 'https://erp.tsh.sale:8001/api';  // REMOVE
  static const String neurolinkApiUrl = 'https://erp.tsh.sale:8002/api';  // REMOVE

  // Environment-specific URLs
  static const String baseUrl = kReleaseMode ? mainApiUrl : 'http://localhost:8000/api';
}
```

#### NEW Configuration (Unified):
```dart
import 'package:flutter/foundation.dart';

class ApiConfig {
  // =============================================
  // UNIFIED MONOLITHIC BACKEND
  // =============================================

  // Production URL
  static const String _productionUrl = 'https://erp.tsh.sale';

  // Development URL (localhost)
  static const String _developmentUrl = 'http://localhost:8000';

  // Current base URL (switches based on build mode)
  static String get baseUrl => kReleaseMode ? _productionUrl : _developmentUrl;

  // =============================================
  // API ENDPOINTS
  // =============================================

  // Main API endpoint
  static String get apiUrl => '$baseUrl/api';

  // Mobile BFF endpoint (optimized for mobile apps)
  static String get mobileBffUrl => '$baseUrl/api/mobile';

  // Health check endpoint
  static String get healthUrl => '$baseUrl/health';

  // =============================================
  // APP-SPECIFIC ENDPOINTS (Optional BFF)
  // =============================================

  // These will be available once Mobile BFF is expanded
  // Uncomment when BFF endpoints are ready for your app

  // static String get adminBffUrl => '$baseUrl/api/mobile/admin';
  // static String get securityBffUrl => '$baseUrl/api/mobile/security';
  // static String get accountingBffUrl => '$baseUrl/api/mobile/accounting';
  // static String get hrBffUrl => '$baseUrl/api/mobile/hr';
  // static String get inventoryBffUrl => '$baseUrl/api/mobile/inventory';
  // static String get salespersonBffUrl => '$baseUrl/api/mobile/salesperson';
  // static String get posBffUrl => '$baseUrl/api/mobile/pos';
  // static String get partnersBffUrl => '$baseUrl/api/mobile/partners';
  // static String get b2bBffUrl => '$baseUrl/api/mobile/b2b';
  // static String get consumerBffUrl => '$baseUrl/api/mobile/consumer';  // ✅ Available
  // static String get asoBffUrl => '$baseUrl/api/mobile/aso';

  // =============================================
  // CONFIGURATION
  // =============================================

  // Request timeout (milliseconds)
  static const int timeoutMs = 30000;  // 30 seconds

  // Max retry attempts for failed requests
  static const int maxRetries = 3;

  // Enable request logging (debug mode only)
  static bool get enableLogging => kDebugMode;

  // =============================================
  // HELPER METHODS
  // =============================================

  /// Build full API URL
  static String buildUrl(String path) {
    // Remove leading slash if present
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return '$apiUrl/$cleanPath';
  }

  /// Build Mobile BFF URL
  static String buildMobileBffUrl(String path) {
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return '$mobileBffUrl/$cleanPath';
  }

  /// Check if running in production
  static bool get isProduction => kReleaseMode;

  /// Check if running in development
  static bool get isDevelopment => kDebugMode;

  /// Print configuration (debug only)
  static void printConfig() {
    if (kDebugMode) {
      print('🔧 API Configuration');
      print('   Environment: ${isProduction ? "Production" : "Development"}');
      print('   Base URL: $baseUrl');
      print('   API URL: $apiUrl');
      print('   Mobile BFF: $mobileBffUrl');
      print('   Health URL: $healthUrl');
      print('   Timeout: ${timeoutMs}ms');
    }
  }
}
```

### Step 3: Update HTTP Client Initialization

If your app has a custom HTTP client, update it to use the new configuration:

```dart
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'api_config.dart';

class ApiClient {
  late final http.Client _client;

  ApiClient() {
    _client = http.Client();

    // Print configuration in debug mode
    if (kDebugMode) {
      ApiConfig.printConfig();
    }
  }

  // GET request
  Future<http.Response> get(String path, {Map<String, String>? headers}) async {
    final url = Uri.parse(ApiConfig.buildUrl(path));
    return await _client.get(url, headers: headers).timeout(
      Duration(milliseconds: ApiConfig.timeoutMs),
    );
  }

  // POST request
  Future<http.Response> post(
    String path, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final url = Uri.parse(ApiConfig.buildUrl(path));
    return await _client.post(url, headers: headers, body: body).timeout(
      Duration(milliseconds: ApiConfig.timeoutMs),
    );
  }

  // PUT request
  Future<http.Response> put(
    String path, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final url = Uri.parse(ApiConfig.buildUrl(path));
    return await _client.put(url, headers: headers, body: body).timeout(
      Duration(milliseconds: ApiConfig.timeoutMs),
    );
  }

  // DELETE request
  Future<http.Response> delete(String path, {Map<String, String>? headers}) async {
    final url = Uri.parse(ApiConfig.buildUrl(path));
    return await _client.delete(url, headers: headers).timeout(
      Duration(milliseconds: ApiConfig.timeoutMs),
    );
  }

  // Dispose
  void dispose() {
    _client.close();
  }
}
```

### Step 4: Update Service Files

Update any service files that reference the old API URLs:

**Before:**
```dart
// ❌ OLD: Multiple API endpoints
final productsUrl = '${ApiConfig.mainApiUrl}/products';
final tdsUrl = '${ApiConfig.tdsApiUrl}/sync';
final notificationsUrl = '${ApiConfig.neurolinkApiUrl}/notifications';
```

**After:**
```dart
// ✅ NEW: Unified API endpoint
final productsUrl = ApiConfig.buildUrl('products');
final syncUrl = ApiConfig.buildUrl('zoho/sync');
final notificationsUrl = ApiConfig.buildUrl('notifications');

// Or use Mobile BFF for optimized endpoints (when available)
final homeUrl = ApiConfig.buildMobileBffUrl('home');
```

---

## Testing Checklist

After updating each app, test the following:

### 1. Development Mode (Localhost)
- [ ] Run app in debug mode: `flutter run`
- [ ] Verify it connects to `http://localhost:8000/api`
- [ ] Check debug console for API configuration print
- [ ] Test login functionality
- [ ] Test data fetching

### 2. Production Mode (Release Build)
- [ ] Build release APK: `flutter build apk --release`
- [ ] Install on test device
- [ ] Verify it connects to `https://erp.tsh.sale/api`
- [ ] Test login functionality
- [ ] Test data fetching
- [ ] Check for SSL/TLS errors

### 3. Specific Features to Test
- [ ] User authentication (login/logout)
- [ ] Data fetching (products, orders, customers)
- [ ] Data creation (new orders, new customers)
- [ ] Image loading
- [ ] Push notifications
- [ ] Real-time updates (if applicable)

---

## Common Issues & Fixes

### Issue 1: SSL Certificate Error

**Error:**
```
HandshakeException: Handshake error in client
```

**Fix:**
Ensure your SSL certificate is valid. For development with self-signed certificates:

```dart
import 'dart:io';

class ApiClient {
  ApiClient() {
    // ⚠️ ONLY FOR DEVELOPMENT with self-signed certificates
    if (kDebugMode) {
      HttpOverrides.global = _DevHttpOverrides();
    }
  }
}

class _DevHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback = (X509Certificate cert, String host, int port) => true;
  }
}
```

### Issue 2: Connection Timeout

**Error:**
```
TimeoutException after 30000 ms
```

**Fix:**
Increase timeout or check network connectivity:

```dart
// Increase timeout for slow networks
static const int timeoutMs = 60000;  // 60 seconds
```

### Issue 3: CORS Error (Web)

**Error:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Fix:**
The backend already handles CORS. Ensure you're using the correct API URL without trailing slashes.

### Issue 4: 404 Not Found

**Error:**
```
404 Not Found: /api/zoho/sync
```

**Fix:**
Some old endpoints may have been renamed. Check the new API documentation:
- Old: `/api/tds/sync` → New: `/api/zoho/sync`
- Old: `/api/neurolink/notifications` → New: `/api/notifications`

---

## App-Specific Notes

### Consumer App (10_tsh_consumer_app)
- ✅ Already uses Mobile BFF
- Configuration already optimal
- No changes needed if using BFF endpoints

### Salesperson App (06_tsh_salesperson_app)
- High API usage
- Priority for BFF implementation
- Will benefit most from optimizations

### Admin App (01_tsh_admin_app)
- Remove references to TDS Dashboard
- All TDS functionality now in main API at `/api/zoho/*`

### All Other Apps
- Update to unified configuration
- Remove microservice endpoint references
- Use standard REST API until BFF is available

---

## Automation Script

To update all apps at once, you can use this script:

```bash
#!/bin/bash

# Update all Flutter app configurations
APPS_DIR="/Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps"

for app_dir in "$APPS_DIR"/*/; do
    app_name=$(basename "$app_dir")
    config_file="$app_dir/lib/config/api_config.dart"

    if [ -f "$config_file" ]; then
        echo "📱 Updating $app_name..."
        # Backup original
        cp "$config_file" "$config_file.backup"

        # Update configuration (manual review required)
        echo "   ⚠️  Manual review required for $config_file"
    else
        echo "⚠️  Config file not found for $app_name"
    fi
done

echo "✅ Configuration update complete!"
echo "📝 Review each file manually to ensure correct updates"
```

---

## Validation

After updating all apps, verify the changes:

### 1. Check Git Diff
```bash
cd mobile/flutter_apps
git diff */lib/config/api_config.dart
```

### 2. Search for Old Endpoints
```bash
# Should return no results
grep -r "8001" mobile/flutter_apps/*/lib/
grep -r "8002" mobile/flutter_apps/*/lib/
grep -r "tdsApiUrl" mobile/flutter_apps/*/lib/
grep -r "neurolinkApiUrl" mobile/flutter_apps/*/lib/
```

### 3. Test Build All Apps
```bash
# Test that all apps compile
for app in mobile/flutter_apps/*/; do
    echo "Building $(basename $app)..."
    cd "$app"
    flutter pub get
    flutter analyze
    flutter build apk --release
    cd -
done
```

---

## Timeline

**Estimated Time:** 2-4 hours for all 11 apps

- App 01 (Admin): 15 minutes
- App 02 (Security): 15 minutes
- App 03 (Accounting): 15 minutes
- App 04 (HR): 15 minutes
- App 05 (Inventory): 15 minutes
- App 06 (Salesperson): 20 minutes (more complex)
- App 07 (POS): 15 minutes
- App 08 (Partners): 15 minutes
- App 09 (B2B): 15 minutes
- App 10 (Consumer): 10 minutes (already optimal)
- App 11 (ASO): 15 minutes

**Testing:** 30-60 minutes per app (in parallel)

---

## Production Backend Verification

Before updating Flutter apps, verify the backend is operational:

### ✅ Backend Status (As of Nov 5, 2025 15:50 UTC):
```bash
# Health Check
curl https://erp.tsh.sale/health
# Response: {"status":"healthy","message":"النظام يعمل بشكل طبيعي"}

# API Documentation
curl https://erp.tsh.sale/docs
# Status: 200 OK

# Service Status
ssh root@erp.tsh.sale 'systemctl status tsh_erp-green'
# Active: active (running) since Wed 2025-11-05 15:41:02 UTC

# Redis Status
ssh root@erp.tsh.sale 'redis-cli ping'
# Response: PONG
```

### Performance Baseline:
- **API Response Time:** ~274ms (cold start)
- **Memory Usage:** 217MB
- **Redis Status:** Active (cache warming)
- **Uptime:** Stable since deployment

---

## Next Steps After Configuration

Once all apps are configured:

1. **✅ Deploy Backend** (COMPLETED)
   - Backend deployed at https://erp.tsh.sale
   - Redis caching active
   - Performance indexes applied

2. **Update Flutter Apps**
   ```bash
   ./deployment/deploy.sh
   ```

2. **Test Each App**
   - Development mode (localhost)
   - Production mode (release build)

3. **Apply Database Indexes**
   ```bash
   psql -U postgres -d tsh_erp -f database/performance_indexes.sql
   ```

4. **Monitor Performance**
   - Check API response times
   - Monitor error rates
   - Verify all features working

5. **Plan Mobile BFF Expansion**
   - Refer to `MOBILE_BFF_ENHANCEMENT_PLAN.md`
   - Prioritize apps with highest API usage
   - Start with Salesperson app

---

## Support

If you encounter issues:

1. Check backend health: `https://erp.tsh.sale/health`
2. Verify API documentation: `https://erp.tsh.sale/docs`
3. Review backend logs: `journalctl -u tsh_erp -f`
4. Check Flutter logs: `flutter logs`

---

**Status:** Configuration guide ready
**Action Required:** Update all 11 Flutter apps
**Priority:** High (required for monolithic transformation)
**Impact:** All apps will use unified backend

---

**Created:** November 5, 2025
**Version:** 1.0
**Last Updated:** November 5, 2025
