class ApiEndpoints {
  // Base URL - Update based on environment
  static const String baseUrl = 'http://192.168.68.82:8000/api';

  // Authentication
  static const String login = '/auth/login/mobile';
  static const String logout = '/auth/logout';
  static const String refreshToken = '/auth/refresh';

  // Dashboard
  static const String dashboardStats = '/dashboard/stats';
  static const String salesSummary = '/dashboard/sales-summary';
  static const String commissionSummary = '/dashboard/commission-summary';

  // Customers
  static const String customers = '/customers';
  static const String customerDetail = '/customers/{id}';
  static const String customerVisits = '/customers/{id}/visits';
  static const String createCustomer = '/customers';
  static const String updateCustomer = '/customers/{id}';

  // Products
  static const String products = '/products';
  static const String productDetail = '/products/{id}';
  static const String productSearch = '/products/search';

  // Orders
  static const String orders = '/orders';
  static const String orderDetail = '/orders/{id}';
  static const String createOrder = '/orders';
  static const String updateOrder = '/orders/{id}';
  static const String orderHistory = '/orders/history';

  // Money Transfers - CRITICAL
  static const String moneyTransfers = '/money-transfers';
  static const String createTransfer = '/money-transfers/create';
  static const String transferDetail = '/money-transfers/{id}';
  static const String uploadReceipt = '/money-transfers/{id}/receipt';
  static const String transferHistory = '/money-transfers/history';
  static const String commissionReport = '/money-transfers/commission-report';
  static const String fraudAlerts = '/money-transfers/fraud-alerts';

  // GPS & Location - CRITICAL
  static const String logVisit = '/visits/log';
  static const String visitHistory = '/visits/history';
  static const String routePlan = '/visits/route-plan';
  static const String updateLocation = '/location/update';

  // Reports
  static const String salesReport = '/reports/sales';
  static const String commissionReportEndpoint = '/reports/commission';
  static const String visitReport = '/reports/visits';
  static const String dailyReport = '/reports/daily';

  // Sync
  static const String syncData = '/sync/data';
  static const String pendingSync = '/sync/pending';

  // Helper method to replace path parameters
  static String replaceParams(String path, Map<String, String> params) {
    String result = path;
    params.forEach((key, value) {
      result = result.replaceAll('{$key}', value);
    });
    return result;
  }
}
