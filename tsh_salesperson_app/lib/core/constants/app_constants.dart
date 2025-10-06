class AppConstants {
  // App Info
  static const String appName = 'TSH Salesperson';
  static const String appVersion = '1.0.0';

  // Commission
  static const double commissionRate = 2.25; // 2.25%

  // Currency
  static const String currencyUSD = 'USD';
  static const String currencyIQD = 'IQD';
  static const double usdToIqdRate = 1450.0; // Update as needed

  // GPS
  static const double gpsAccuracyThreshold = 50.0; // meters
  static const int locationUpdateInterval = 30; // seconds
  static const double visitGeofenceRadius = 100.0; // meters

  // Transfer Platforms
  static const String platformZainCash = 'ZAIN_CASH';
  static const String platformSuperQi = 'SUPER_QI';
  static const String platformAltaif = 'ALTAIF_BANK';
  static const String platformCash = 'CASH';

  // Transfer Status
  static const String statusPending = 'PENDING';
  static const String statusVerified = 'VERIFIED';
  static const String statusRejected = 'REJECTED';
  static const String statusInvestigating = 'INVESTIGATING';

  // Fraud Alert Levels
  static const String alertCritical = 'CRITICAL';
  static const String alertHigh = 'HIGH';
  static const String alertMedium = 'MEDIUM';
  static const String alertLow = 'LOW';

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // Cache Duration
  static const Duration cacheCustomers = Duration(hours: 1);
  static const Duration cacheProducts = Duration(hours: 2);
  static const Duration cacheDashboard = Duration(minutes: 5);

  // File Upload
  static const int maxFileSize = 5 * 1024 * 1024; // 5MB
  static const List<String> allowedImageTypes = ['jpg', 'jpeg', 'png'];

  // Sync
  static const Duration syncInterval = Duration(minutes: 15);
  static const int maxSyncRetries = 3;
}
