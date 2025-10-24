import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/security_event.dart';
import 'api_client.dart';

/// Security Event Service
class SecurityEventService {
  final ApiClient _apiClient = ApiClient();

  /// Get all security events
  Future<List<SecurityEvent>> getSecurityEvents({
    String? eventType,
    String? severity,
    bool? isResolved,
    int? userId,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (eventType != null) {
        queryParams['event_type'] = eventType;
      }
      if (severity != null) {
        queryParams['severity'] = severity;
      }
      if (isResolved != null) {
        queryParams['is_resolved'] = isResolved;
      }
      if (userId != null) {
        queryParams['user_id'] = userId;
      }

      final response = await _apiClient.dio.get(
        ApiConfig.securityEvents,
        queryParameters: queryParams,
      );

      // Handle both list and paginated response
      if (response.data is List) {
        return (response.data as List)
            .map((json) => SecurityEvent.fromJson(json as Map<String, dynamic>))
            .toList();
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['items'] as List? ?? [];
        return items
            .map((json) => SecurityEvent.fromJson(json as Map<String, dynamic>))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch security events',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Mark security event as resolved
  Future<SecurityEvent> resolveSecurityEvent(int id) async {
    try {
      final response = await _apiClient.dio.put(
        '${ApiConfig.securityEvents}/$id/resolve',
      );
      return SecurityEvent.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to resolve security event',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}
