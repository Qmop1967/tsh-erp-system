import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/audit_log.dart';
import 'api_client.dart';

/// Audit Log Service
class AuditService {
  final ApiClient _apiClient = ApiClient();

  /// Get all audit logs
  Future<List<AuditLog>> getAuditLogs({
    int? userId,
    String? action,
    String? resourceType,
    DateTime? startDate,
    DateTime? endDate,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };

      if (userId != null) {
        queryParams['user_id'] = userId;
      }
      if (action != null) {
        queryParams['action'] = action;
      }
      if (resourceType != null) {
        queryParams['resource_type'] = resourceType;
      }
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }

      final response = await _apiClient.dio.get(
        ApiConfig.auditLogs,
        queryParameters: queryParams,
      );

      // Handle both list and paginated response
      if (response.data is List) {
        return (response.data as List)
            .map((json) => AuditLog.fromJson(json as Map<String, dynamic>))
            .toList();
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['items'] as List? ?? [];
        return items
            .map((json) => AuditLog.fromJson(json as Map<String, dynamic>))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch audit logs',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}
