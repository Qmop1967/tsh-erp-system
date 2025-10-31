/// App Configuration
/// إعدادات التطبيق المحاسبي

class AppConfig {
  // API Base URL - النظام المركزي
  // Use Mac's local IP address for iPhone testing
  static const String baseUrl = 'http://192.168.68.51:8000';

  // API Endpoints
  static const String apiVersion = 'v1';
  static const String authEndpoint = '/api/auth/login';
  static const String accountingEndpoint = '/api/accounting';

  // App Info
  static const String appName = 'TSH Accounting';
  static const String appNameAr = 'نظام المحاسبة';
  static const String appVersion = '1.0.0';

  // Demo Mode
  static const bool isDemoMode = false; // set to true for offline demo

  // Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000; // 30 seconds

  // Pagination
  static const int defaultPageSize = 20;

  // Local Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userIdKey = 'user_id';
  static const String usernameKey = 'username';
  static const String userEmailKey = 'user_email';
  static const String userRoleKey = 'user_role';
  static const String languageKey = 'language';
  static const String themeKey = 'theme';

  // Full API URLs
  static String get authUrl => '$baseUrl$authEndpoint';
  static String get accountingUrl => '$baseUrl$accountingEndpoint';

  // Accounting Endpoints
  static String get currenciesUrl => '$accountingUrl/currencies';
  static String get chartOfAccountsUrl => '$accountingUrl/chart-of-accounts';
  static String get accountsUrl => '$accountingUrl/accounts';
  static String get journalsUrl => '$accountingUrl/journals';
  static String get journalEntriesUrl => '$accountingUrl/journal-entries';
  static String get fiscalYearsUrl => '$accountingUrl/fiscal-years';
  static String get accountingPeriodsUrl => '$accountingUrl/accounting-periods';
  static String get dashboardUrl => '$accountingUrl/summary';

  // Reports Endpoints
  static String get trialBalanceUrl => '$accountingUrl/reports/trial-balance';
  static String get balanceSheetUrl => '$accountingUrl/reports/balance-sheet';
  static String get incomeStatementUrl => '$accountingUrl/reports/income-statement';

  // Theme Colors
  static const int primaryColorValue = 0xFF1565C0; // Blue 800
  static const int accentColorValue = 0xFF2E7D32; // Green 800
  static const int assetColorValue = 0xFF1976D2; // Blue
  static const int liabilityColorValue = 0xFFE53935; // Red
  static const int equityColorValue = 0xFF7B1FA2; // Purple
  static const int revenueColorValue = 0xFF388E3C; // Green
  static const int expenseColorValue = 0xFFF57C00; // Orange
}
