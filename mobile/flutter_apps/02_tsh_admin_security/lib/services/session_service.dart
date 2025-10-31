import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/session.dart';
import 'api_client.dart';

/// Session Management Service
class SessionService {
  final ApiClient _apiClient = ApiClient();

  /// Get all active sessions
  Future<List<UserSession>> getSessions({
    String? status,
    int? userId,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) {
        queryParams['status'] = status;
      }
      if (userId != null) {
        queryParams['user_id'] = userId;
      }

      final response = await _apiClient.dio.get(
        ApiConfig.sessions,
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      // Handle both list and paginated response
      if (response.data is List) {
        return (response.data as List)
            .map((json) => UserSession.fromJson(json as Map<String, dynamic>))
            .toList();
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['items'] as List? ?? [];
        return items
            .map((json) => UserSession.fromJson(json as Map<String, dynamic>))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch sessions',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get session by ID
  Future<UserSession> getSessionById(String id) async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.sessionById(id));
      return UserSession.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch session',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Terminate session
  Future<void> terminateSession(String sessionId) async {
    try {
      await _apiClient.dio.delete(ApiConfig.sessionById(sessionId));
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to terminate session',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Terminate user session by user ID and session ID
  Future<void> terminateUserSession(int userId, String sessionId) async {
    try {
      await _apiClient.dio.post(
        ApiConfig.terminateUserSession(userId, sessionId),
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to terminate user session',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}
