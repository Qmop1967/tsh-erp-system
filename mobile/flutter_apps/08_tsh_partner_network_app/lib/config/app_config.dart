/// App Configuration
/// إعدادات تطبيق شبكة الشركاء

class AppConfig {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://192.168.68.51:8000';

  // API Endpoints
  static const String apiVersion = 'v1';
  static const String authEndpoint = '/api/auth/login';
  static const String partnersEndpoint = '/api/partners';
  static const String salesEndpoint = '/api/sales';

  // App Info
  static const String appName = 'TSH Partner Network';
  static const String appNameAr = 'شبكة الشركاء';
  static const String appVersion = '1.0.0';

  // Demo Mode
  static const bool isDemoMode = false;

  // Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000; // 30 seconds

  // Pagination
  static const int defaultPageSize = 20;

  // Local Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userIdKey = 'user_id';
  static const String usernameKey = 'username';
  static const String userRoleKey = 'user_role';
  static const String partnerIdKey = 'partner_id';

  // Full API URLs
  static String get authUrl => '$baseUrl$authEndpoint';
  static String get partnersUrl => '$baseUrl$partnersEndpoint';
  static String get salesUrl => '$baseUrl$salesEndpoint';

  // Partner Endpoints
  static String get retailersUrl => '$partnersUrl/retailers';
  static String get ordersUrl => '$salesUrl/orders';
  static String get commissionsUrl => '$partnersUrl/commissions';
  static String get performanceUrl => '$partnersUrl/performance';
  static String get networkUrl => '$partnersUrl/network';

  // Theme Colors
  static const int primaryColorValue = 0xFF6A1B9A; // Purple 800
  static const int accentColorValue = 0xFFFF6F00; // Orange 900
}
