import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/role.dart';
import 'api_client.dart';

/// Role Management Service
class RoleService {
  final ApiClient _apiClient = ApiClient();

  /// Get all roles
  Future<List<Role>> getRoles() async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.roles);

      // Handle both list and paginated response
      if (response.data is List) {
        return (response.data as List)
            .map((json) => Role.fromJson(json as Map<String, dynamic>))
            .toList();
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['items'] as List? ?? [];
        return items
            .map((json) => Role.fromJson(json as Map<String, dynamic>))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch roles',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get role by ID
  Future<Role> getRoleById(int id) async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.roleById(id));
      return Role.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch role',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Create new role
  Future<Role> createRole(Map<String, dynamic> data) async {
    try {
      final response = await _apiClient.dio.post(
        ApiConfig.roles,
        data: data,
      );
      return Role.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to create role',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Update role
  Future<Role> updateRole(int id, Map<String, dynamic> data) async {
    try {
      final response = await _apiClient.dio.put(
        ApiConfig.roleById(id),
        data: data,
      );
      return Role.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to update role',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Delete role
  Future<void> deleteRole(int id) async {
    try {
      await _apiClient.dio.delete(ApiConfig.roleById(id));
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to delete role',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}
