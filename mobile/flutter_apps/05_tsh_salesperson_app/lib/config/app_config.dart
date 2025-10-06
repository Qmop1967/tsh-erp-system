import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  // TSH ERP System API Configuration
  static const String apiUrl = 'http://192.168.68.66:8000'; // TSH ERP Backend API (Mac's local IP)
  static const String defaultUsername = 'frati@tsh.sale'; // Salesperson: Ayad
  static const String defaultPassword = 'password123'; // Working password
  
  // App Constants
  static const String appName = 'TSH Salesperson';
  static const String appVersion = '1.0.0';
  static const String appBuildNumber = '1';
  
  // Commission Configuration
  static const double commissionRate = 0.0225; // 2.25%
  
  // Currency Configuration
  static const String primaryCurrency = 'IQD';
  static const String secondaryCurrency = 'USD';
  
  // Regional Configuration
  static const List<String> supportedRegions = [
    'بغداد',
    'البصرة', 
    'النجف',
    'بابل',
    'كربلاء',
    'الأنبار',
    'نينوى',
    'أربيل',
    'السليمانية',
    'دهوك',
  ];
  
  // Transfer Methods
  static const List<String> transferMethods = [
    'شركة الطيف للصرافة',
    'مصرف التنمية',
    'مصرف الطيف',
    'ماستر الرافدين',
    'زين كاش',
    'آسيا حوالة',
    'الكرار للحوالات',
  ];
  
  // Theme Configuration
  static const String primaryColorHex = '#1B5E20';
  static const String secondaryColorHex = '#4CAF50';
  static const String accentColorHex = '#FFC107';
  static const String errorColorHex = '#F44336';
  
  // Cache Configuration
  static const Duration cacheTimeout = Duration(minutes: 30);
  static const int maxCacheItems = 1000;
  
  // Network Configuration
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const int maxRetries = 3;
  
  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // File Upload
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedFileTypes = [
    'jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'
  ];
  
  // Local Storage Keys
  static const String keyAuthToken = 'auth_token';
  static const String keyUserId = 'user_id';
  static const String keyUsername = 'username';
  static const String keyUserData = 'user_data';
  static const String keyLastSync = 'last_sync';
  static const String keyCachedCustomers = 'cached_customers';
  static const String keyCachedProducts = 'cached_products';
  static const String keyCachedOrders = 'cached_orders';
  static const String keySettings = 'app_settings';
  static const String keyThemeMode = 'theme_mode';
  static const String keyLanguage = 'language';
  
  // Static Configuration Instance
  static late SharedPreferences _prefs;
  static bool _initialized = false;
  
  static Future<void> initialize() async {
    if (_initialized) return;
    
    _prefs = await SharedPreferences.getInstance();
    _initialized = true;
    
    if (kDebugMode) {
      print('✅ AppConfig initialized');
      print('📊 API URL: $apiUrl');
      print('💰 Commission Rate: ${(commissionRate * 100)}%');
    }
  }
  
  // Settings Management
  static Future<void> saveUserCredentials({
    required String username,
    required String accessToken,
    int? userId,
  }) async {
    await _prefs.setString(keyUsername, username);
    await _prefs.setString(keyAuthToken, accessToken);
    if (userId != null) {
      await _prefs.setInt(keyUserId, userId);
    }
  }
  
  static String? get savedUsername => _prefs.getString(keyUsername);
  static String? get savedAccessToken => _prefs.getString(keyAuthToken);
  static int? get savedUserId => _prefs.getInt(keyUserId);
  
  static Future<void> clearUserData() async {
    await _prefs.remove(keyUsername);
    await _prefs.remove(keyAuthToken);
    await _prefs.remove(keyUserId);
    await _prefs.remove(keyUserData);
  }
  
  // Cache Management
  static Future<void> setLastSyncTime(DateTime time) async {
    await _prefs.setString(keyLastSync, time.toIso8601String());
  }
  
  static DateTime? get lastSyncTime {
    final timeString = _prefs.getString(keyLastSync);
    return timeString != null ? DateTime.parse(timeString) : null;
  }
  
  static bool get isCacheExpired {
    final lastSync = lastSyncTime;
    if (lastSync == null) return true;
    return DateTime.now().difference(lastSync) > cacheTimeout;
  }
  
  // Theme Management
  static Future<void> setThemeMode(String mode) async {
    await _prefs.setString(keyThemeMode, mode);
  }
  
  static String get themeMode => _prefs.getString(keyThemeMode) ?? 'system';
  
  // Language Management
  static Future<void> setLanguage(String languageCode) async {
    await _prefs.setString(keyLanguage, languageCode);
  }
  
  static String get language => _prefs.getString(keyLanguage) ?? 'ar';
  
  // Environment Detection
  static bool get isProduction => !kDebugMode;
  static bool get isDevelopment => kDebugMode;
  
  // Platform Detection
  static bool get isMobile => defaultTargetPlatform == TargetPlatform.android || 
                             defaultTargetPlatform == TargetPlatform.iOS;
  static bool get isWeb => kIsWeb;
  static bool get isDesktop => defaultTargetPlatform == TargetPlatform.windows ||
                              defaultTargetPlatform == TargetPlatform.macOS ||
                              defaultTargetPlatform == TargetPlatform.linux;
  
  // Debug Helpers
  static void debugPrint(String message) {
    if (kDebugMode) {
      print('🐛 [TSH App] $message');
    }
  }
  
  static void logInfo(String message) {
    if (kDebugMode) {
      print('ℹ️ [TSH App] $message');
    }
  }
  
  static void logError(String message, [dynamic error]) {
    if (kDebugMode) {
      print('❌ [TSH App] $message');
      if (error != null) {
        print('Error details: $error');
      }
    }
  }
  
  static void logSuccess(String message) {
    if (kDebugMode) {
      print('✅ [TSH App] $message');
    }
  }
}

// App Environment Configuration
enum AppEnvironment {
  development,
  staging,
  production,
}

class EnvironmentConfig {
  static const AppEnvironment current = kDebugMode 
    ? AppEnvironment.development 
    : AppEnvironment.production;
  
  static String get environmentName {
    switch (current) {
      case AppEnvironment.development:
        return 'Development';
      case AppEnvironment.staging:
        return 'Staging';
      case AppEnvironment.production:
        return 'Production';
    }
  }
  
  static bool get enableLogging => current != AppEnvironment.production;
  static bool get enableDebugTools => current == AppEnvironment.development;
}
