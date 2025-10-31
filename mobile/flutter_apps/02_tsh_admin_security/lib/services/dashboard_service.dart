import '../services/api_client.dart';
import '../models/dashboard_stats.dart';

/// Dashboard Service - Fetches dashboard statistics
class DashboardService {
  final ApiClient _apiClient = ApiClient();

  /// Get dashboard statistics
  Future<DashboardStats> getDashboardStats() async {
    try {
      print('📊 DashboardService: Fetching dashboard stats...');

      final response = await _apiClient.dio.get('/api/dashboard/stats');

      print('✅ DashboardService: Stats fetched successfully');
      return DashboardStats.fromJson(response.data);
    } catch (e) {
      print('❌ DashboardService: Error fetching stats: $e');
      rethrow;
    }
  }

  /// Get total users count
  Future<int> getTotalUsers() async {
    try {
      final response = await _apiClient.dio.get('/api/users/count');
      return response.data['count'] ?? 0;
    } catch (e) {
      print('❌ DashboardService: Error fetching users count: $e');
      return 0;
    }
  }

  /// Get active sessions count
  Future<int> getActiveSessions() async {
    try {
      final response = await _apiClient.dio.get('/api/sessions/active/count');
      return response.data['count'] ?? 0;
    } catch (e) {
      print('❌ DashboardService: Error fetching active sessions: $e');
      return 0;
    }
  }

  /// Get security alerts count
  Future<int> getSecurityAlerts() async {
    try {
      final response = await _apiClient.dio.get('/api/security/alerts/count');
      return response.data['count'] ?? 0;
    } catch (e) {
      print('❌ DashboardService: Error fetching security alerts: $e');
      return 0;
    }
  }

  /// Get failed logins count
  Future<int> getFailedLogins() async {
    try {
      final response = await _apiClient.dio.get('/api/auth/failed-logins/count');
      return response.data['count'] ?? 0;
    } catch (e) {
      print('❌ DashboardService: Error fetching failed logins: $e');
      return 0;
    }
  }
}
