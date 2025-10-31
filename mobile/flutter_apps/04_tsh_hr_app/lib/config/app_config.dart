/// App Configuration
/// إعدادات تطبيق الموارد البشرية

class AppConfig {
  // API Base URL - النظام المركزي
  static const String baseUrl = 'http://192.168.68.51:8000';

  // API Endpoints
  static const String apiVersion = 'v1';
  static const String authEndpoint = '/api/auth/login';
  static const String hrEndpoint = '/api/hr';

  // App Info
  static const String appName = 'TSH HR';
  static const String appNameAr = 'إدارة الموارد البشرية';
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
  static const String userEmailKey = 'user_email';
  static const String userRoleKey = 'user_role';

  // Full API URLs
  static String get authUrl => '$baseUrl$authEndpoint';
  static String get hrUrl => '$baseUrl$hrEndpoint';

  // HR Endpoints
  static String get employeesUrl => '$hrUrl/employees';
  static String get attendanceUrl => '$hrUrl/attendance';
  static String get leaveRequestsUrl => '$hrUrl/leave-requests';
  static String get payrollUrl => '$hrUrl/payroll';
  static String get departmentsUrl => '$hrUrl/departments';
  static String get positionsUrl => '$hrUrl/positions';

  // Theme Colors
  static const int primaryColorValue = 0xFF0D47A1; // Blue 900
  static const int accentColorValue = 0xFFFF6F00; // Orange 900
}
