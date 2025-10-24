/// App Configuration
/// إعدادات التطبيق

class AppConfig {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://localhost:8000';
  
  // API Endpoints
  static const String apiVersion = 'v1';
  static const String authEndpoint = '/api/auth/login/mobile';
  static const String asoEndpoint = '/aso';
  
  // App Info
  static const String appName = 'ASO Technician';
  static const String appVersion = '1.0.0';
  
  // Demo Mode
  static const bool isDemoMode = false; // set to true for offline demo
  
  // Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000; // 30 seconds
  
  // Notification Settings
  static const int notificationRefreshInterval = 60; // seconds
  
  // Local Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userIdKey = 'user_id';
  static const String usernameKey = 'username';
  static const String userRoleKey = 'user_role';
  
  // Full API URLs
  static String get authUrl => '$baseUrl$authEndpoint';
  static String get asoUrl => '$baseUrl$asoEndpoint';
  static String notificationsUrl(int userId) => '$asoUrl/notifications?user_id=$userId';
  static String returnsUrl() => '$asoUrl/returns';
  static String maintenanceJobsUrl(int userId) => '$asoUrl/maintenance/assigned/$userId';
}
