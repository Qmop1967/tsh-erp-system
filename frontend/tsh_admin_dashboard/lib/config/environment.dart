class Environment {
  static const String apiBaseUrl = 'http://192.168.0.237:8000';
  
  static const Map<String, String> endpoints = {
    'dashboard': '/api/admin/dashboard',
    'users': '/api/admin/users',
    'analytics': '/api/admin/analytics',
    'settings': '/api/admin/settings',
  };
  
  static String getFullUrl(String endpoint) {
    return '$apiBaseUrl${endpoints[endpoint] ?? endpoint}';
  }
}
