/// App Configuration
/// إعدادات تطبيق عملاء الجملة

class AppConfig {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://192.168.68.51:8000';

  // API Endpoints
  static const String apiVersion = 'v1';
  static const String authEndpoint = '/api/auth/login';
  static const String customersEndpoint = '/api/customers';
  static const String salesEndpoint = '/api/sales';

  // App Info
  static const String appName = 'TSH Wholesale Client';
  static const String appNameAr = 'بوابة عملاء الجملة';
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
  static const String customerIdKey = 'customer_id';

  // Full API URLs
  static String get authUrl => '$baseUrl$authEndpoint';
  static String get customersUrl => '$baseUrl$customersEndpoint';
  static String get salesUrl => '$baseUrl$salesEndpoint';

  // Customer Endpoints
  static String get productsUrl => '$salesUrl/products';
  static String get ordersUrl => '$salesUrl/orders';
  static String get invoicesUrl => '$customersUrl/invoices';
  static String get paymentsUrl => '$customersUrl/payments';
  static String get creditUrl => '$customersUrl/credit';
  static String get accountStatementUrl => '$customersUrl/account-statement';

  // Theme Colors
  static const int primaryColorValue = 0xFF1565C0; // Blue 800
  static const int accentColorValue = 0xFF2E7D32; // Green 800
}
