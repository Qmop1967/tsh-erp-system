import 'package:dio/dio.dart';
import '../config/api_config.dart';
import 'api_client.dart';

/// User Management Service
/// Handles user roles, permissions, and trusted devices
class UserManagementService {
  final ApiClient _apiClient = ApiClient();

  /// Get available roles
  Future<List<Map<String, dynamic>>> getAvailableRoles() async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.roles);

      if (response.data is List) {
        return List<Map<String, dynamic>>.from(response.data);
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['items'] as List? ?? [];
        return List<Map<String, dynamic>>.from(items);
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

  /// Assign role to user
  Future<void> assignRole(int userId, int roleId) async {
    try {
      await _apiClient.dio.put(
        ApiConfig.userById(userId),
        data: {'role_id': roleId},
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to assign role',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get available permissions
  Future<List<Map<String, dynamic>>> getAvailablePermissions({
    String? search,
    String? module,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      if (module != null && module.isNotEmpty) {
        queryParams['module'] = module;
      }

      final response = await _apiClient.dio.get(
        ApiConfig.permissions,
        queryParameters: queryParams,
      );

      if (response.data is List) {
        return List<Map<String, dynamic>>.from(response.data);
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['items'] as List? ?? [];
        return List<Map<String, dynamic>>.from(items);
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch permissions',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get user's current permissions
  Future<List<Map<String, dynamic>>> getUserPermissions(int userId) async {
    try {
      final response = await _apiClient.dio.get(
        ApiConfig.userPermissions(userId),
      );

      if (response.data is List) {
        return List<Map<String, dynamic>>.from(response.data);
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['permissions'] as List? ?? [];
        return List<Map<String, dynamic>>.from(items);
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch user permissions',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Grant permissions to user
  Future<void> grantPermissions(int userId, List<int> permissionIds) async {
    try {
      await _apiClient.dio.post(
        ApiConfig.userPermissions(userId),
        data: {'permission_ids': permissionIds},
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to grant permissions',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get user's action permissions (CRUD)
  Future<Map<String, dynamic>> getUserActionPermissions(int userId) async {
    try {
      final response = await _apiClient.dio.get(
        '${ApiConfig.userPermissions(userId)}/actions',
      );

      if (response.data is Map<String, dynamic>) {
        return response.data;
      }

      return {};
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch action permissions',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Update user's action permissions
  Future<void> updateActionPermissions(
    int userId,
    Map<String, Map<String, bool>> permissions,
  ) async {
    try {
      await _apiClient.dio.put(
        '${ApiConfig.userPermissions(userId)}/actions',
        data: {'permissions': permissions},
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to update action permissions',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get user's trusted devices
  Future<List<Map<String, dynamic>>> getUserTrustedDevices(int userId) async {
    try {
      final response = await _apiClient.dio.get(
        ApiConfig.userDevices(userId),
      );

      if (response.data is List) {
        return List<Map<String, dynamic>>.from(response.data);
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['devices'] as List? ?? [];
        return List<Map<String, dynamic>>.from(items);
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch trusted devices',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Revoke trust for a device
  Future<void> revokeTrustedDevice(int userId, String deviceId) async {
    try {
      await _apiClient.dio.delete(
        '${ApiConfig.userDevices(userId)}/$deviceId',
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to revoke device trust',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Add trusted device for user
  Future<void> addTrustedDevice(
    int userId,
    Map<String, dynamic> deviceData,
  ) async {
    try {
      await _apiClient.dio.post(
        ApiConfig.userDevices(userId),
        data: deviceData,
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to add trusted device',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}
