/// API Configuration for TSH Access Management
/// Connects to TSH ERP Backend (FastAPI - Port 8000)
class ApiConfig {
  // Environment Configuration
  static const String environment = String.fromEnvironment(
    'ENVIRONMENT',
    defaultValue: 'development',
  );

  // Base URLs for different environments
  static const String productionUrl = 'https://erp.tsh.sale';
  static const String stagingUrl = 'https://staging.erp.tsh.sale';
  static const String developmentUrl = 'http://192.168.68.51:8000'; // Local development

  // Select base URL based on environment
  static String get baseUrl {
    switch (environment) {
      case 'production':
        return productionUrl;
      case 'staging':
        return stagingUrl;
      case 'development':
      default:
        return developmentUrl;
    }
  }

  static const String apiPrefix = '/api';

  // Full base API URL
  static String get apiBaseUrl => '$baseUrl$apiPrefix';

  // Authentication Endpoints
  static String get authLogin => '$apiPrefix/auth/login';
  static String get authLogout => '$apiPrefix/auth/logout';
  static String get authRefresh => '$apiPrefix/auth/refresh';
  static String get authMe => '$apiPrefix/auth/me';
  static String get authMfaVerify => '$apiPrefix/auth/mfa/verify';
  static String get authMfaSetup => '$apiPrefix/auth/mfa/setup';

  // User Management Endpoints
  static String get users => '$apiPrefix/users';
  static String userById(int id) => '$apiPrefix/users/$id';
  static String userSessions(int id) => '$apiPrefix/users/$id/sessions';
  static String terminateUserSession(int userId, String sessionId) =>
      '$apiPrefix/users/$userId/sessions/$sessionId/terminate';
  static String userDevices(int id) => '$apiPrefix/users/$id/devices';
  static String userPermissions(int id) => '$apiPrefix/users/$id/permissions';

  // Role & Permission Endpoints
  static String get roles => '$apiPrefix/permissions/roles';
  static String roleById(int id) => '$apiPrefix/permissions/roles/$id';
  static String rolePermissions(int id) =>
      '$apiPrefix/permissions/roles/$id/permissions';
  static String get permissions => '$apiPrefix/permissions';
  static String permissionById(int id) => '$apiPrefix/permissions/$id';

  // Security Endpoints
  static String get securityEvents => '$apiPrefix/security/events';
  static String get auditLogs => '$apiPrefix/security/audit-logs';
  static String get devices => '$apiPrefix/security/devices';
  static String deviceById(String id) => '$apiPrefix/security/devices/$id';
  static String deviceStatus(String id) =>
      '$apiPrefix/security/devices/$id/status';
  static String get loginAttempts => '$apiPrefix/security/login-attempts';
  static String get sessions => '$apiPrefix/security/sessions';
  static String sessionById(String id) => '$apiPrefix/security/sessions/$id';

  // Trusted Devices Endpoints
  static String get trustedDevicesTrust => '$apiPrefix/trusted-devices/trust';
  static String get trustedDevicesCheck => '$apiPrefix/trusted-devices/check';
  static String get trustedDevicesAutoLogin => '$apiPrefix/trusted-devices/auto-login';
  static String get trustedDevicesList => '$apiPrefix/trusted-devices/';
  static String trustedDevicesRevoke(String deviceId) => '$apiPrefix/trusted-devices/$deviceId';

  // Admin Dashboard Endpoints
  static String get dashboardMetrics => '$apiPrefix/admin/dashboard/metrics';
  static String get dashboardAnalytics => '$apiPrefix/admin/dashboard/analytics';
  static String get dashboardStats => '$apiPrefix/admin/dashboard/stats';

  // Settings Endpoints
  static String get settings => '$apiPrefix/settings';
  static String get securitySettings => '$apiPrefix/security/settings';
  static String get systemConfig => '$apiPrefix/settings/system';

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

  // Environment Check
  static bool get isDevelopment => environment == 'development';
  static bool get isStaging => environment == 'staging';
  static bool get isProduction => environment == 'production';

  // Environment display name
  static String get environmentName {
    switch (environment) {
      case 'production':
        return 'Production';
      case 'staging':
        return 'Staging';
      case 'development':
      default:
        return 'Development';
    }
  }

  // Zoho TDS Endpoints (via TDS Core)
  static String get tdsZohoUserMapping => '$apiPrefix/tds/sync/user-mapping';
  static String get tdsZohoSyncStatus => '$apiPrefix/tds/sync/status';
  static String get tdsZohoSyncTrigger => '$apiPrefix/tds/sync/trigger';
}
