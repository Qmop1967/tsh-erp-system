/// App Configuration
/// إعدادات تطبيق نقاط البيع (POS)

class AppConfig {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://192.168.68.51:8000';

  // API Endpoints
  static const String apiVersion = 'v1';
  static const String authEndpoint = '/api/auth/login';
  static const String posEndpoint = '/api/pos';
  static const String salesEndpoint = '/api/sales';

  // App Info
  static const String appName = 'TSH POS';
  static const String appNameAr = 'نقطة البيع';
  static const String appVersion = '1.0.0';

  // Demo Mode
  static const bool isDemoMode = false;

  // Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000; // 30 seconds

  // Pagination
  static const int defaultPageSize = 50;

  // Local Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userIdKey = 'user_id';
  static const String usernameKey = 'username';
  static const String userRoleKey = 'user_role';
  static const String cashierIdKey = 'cashier_id';

  // Full API URLs
  static String get authUrl => '$baseUrl$authEndpoint';
  static String get posUrl => '$baseUrl$posEndpoint';
  static String get salesUrl => '$baseUrl$salesEndpoint';

  // POS Endpoints
  static String get productsUrl => '$posUrl/products';
  static String get salesOrdersUrl => '$salesUrl/orders';
  static String get paymentsUrl => '$posUrl/payments';
  static String get receiptUrl => '$posUrl/receipt';
  static String get dailyReportUrl => '$posUrl/daily-report';
  static String get cashRegisterUrl => '$posUrl/cash-register';

  // Theme Colors
  static const int primaryColorValue = 0xFF1565C0; // Blue 800
  static const int accentColorValue = 0xFF2E7D32; // Green 800
  static const int errorColorValue = 0xFFD32F2F; // Red 700
}
