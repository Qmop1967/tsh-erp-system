/// API Configuration for TSH Wholesale Client App
/// Connects to TSH ERP Backend (FastAPI - Port 8000)
class ApiConfig {
  // Base URL Configuration
  // For development:
  // - Web: use localhost
  // - iOS Simulator: use localhost
  // - iOS Physical Device: use Mac's local network IP
  // - Android Emulator: use 10.0.2.2 (alias for host machine)
  // - Android Physical Device: use Mac's local network IP

  // Mac local IP: 192.168.68.51
  // Change this to your actual local IP when testing on physical devices
  static const String _localhostUrl = 'http://localhost:8000';
  static const String _networkUrl = 'http://192.168.68.51:8000';

  // Automatically use appropriate URL based on platform
  // For now, using localhost for development
  static const String baseUrl = _localhostUrl;
  static const String apiPrefix = '/api';

  // Full base API URL
  static String get apiBaseUrl => '$baseUrl$apiPrefix';

  // Authentication Endpoints
  static String get authLoginMobile => '$apiPrefix/auth/login/mobile';
  static String get authLogin => '$apiPrefix/auth/login';
  static String get authLogout => '$apiPrefix/auth/logout';
  static String get authRefresh => '$apiPrefix/auth/refresh';
  static String get authMe => '$apiPrefix/auth/me';
  static String get authRegister => '$apiPrefix/auth/register';
  static String get authForgotPassword => '$apiPrefix/auth/forgot-password';
  static String get authResetPassword => '$apiPrefix/auth/reset-password';
  static String get authChangePassword => '$apiPrefix/auth/change-password';

  // Product Endpoints
  static String get products => '$apiPrefix/products';
  static String productById(String id) => '$apiPrefix/products/$id';
  static String get productsActive => '$apiPrefix/products/active';
  static String get productsSearch => '$apiPrefix/products/search';
  static String productsByCategory(String category) =>
      '$apiPrefix/products/category/$category';

  // Order Endpoints
  static String get orders => '$apiPrefix/orders';
  static String orderById(String id) => '$apiPrefix/orders/$id';
  static String get ordersCreate => '$apiPrefix/orders/create';
  static String get myOrders => '$apiPrefix/orders/my-orders';
  static String orderStatus(String id) => '$apiPrefix/orders/$id/status';

  // Customer Endpoints (for wholesale client profile)
  static String get customers => '$apiPrefix/customers';
  static String customerById(String id) => '$apiPrefix/customers/$id';
  static String get myProfile => '$apiPrefix/customers/me';
  static String get myOrders => '$apiPrefix/customers/me/orders';

  // Category Endpoints
  static String get categories => '$apiPrefix/categories';
  static String categoryById(String id) => '$apiPrefix/categories/$id';

  // Pricelist Endpoints (for wholesale pricing)
  static String get pricelists => '$apiPrefix/pricelists';
  static String pricelistById(String id) => '$apiPrefix/pricelists/$id';
  static String get myPricelist => '$apiPrefix/pricelists/my-pricelist';

  // Branch Endpoints
  static String get branches => '$apiPrefix/branches';
  static String branchById(String id) => '$apiPrefix/branches/$id';

  // Settings Endpoints
  static String get settings => '$apiPrefix/settings';
  static String get appConfig => '$apiPrefix/settings/app-config';

  // Timeout Settings
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);

  // Retry Configuration
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 2);

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // Cache Duration
  static const Duration cacheExpiration = Duration(minutes: 5);
  static const Duration productsCacheExpiration = Duration(minutes: 10);

  // Environment Check
  static bool get isDevelopment => baseUrl.contains('localhost');
  static bool get isProduction => !isDevelopment;

  // Currency Settings
  static const String defaultCurrency = 'IQD';
  static const int decimalPlaces = 0; // Iraqi Dinar has no decimal places
}
