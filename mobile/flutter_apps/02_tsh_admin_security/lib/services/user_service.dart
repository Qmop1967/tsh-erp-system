import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/user.dart';
import 'api_client.dart';

/// User Management Service
class UserService {
  final ApiClient _apiClient = ApiClient();

  /// Get all users (paginated)
  Future<List<User>> getUsers({
    int page = 1,
    int pageSize = 20,
    String? search,
    bool? isActive,
  }) async {
    try {
      // Convert page/pageSize to skip/limit for backend
      final skip = (page - 1) * pageSize;

      final queryParams = <String, dynamic>{
        'skip': skip,
        'limit': pageSize,
      };
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      if (isActive != null) {
        queryParams['is_active'] = isActive;
      }

      final response = await _apiClient.dio.get(
        ApiConfig.users,
        queryParameters: queryParams,
      );

      // Handle both list and paginated response
      if (response.data is List) {
        return (response.data as List)
            .map((json) => User.fromJson(json as Map<String, dynamic>))
            .toList();
      } else if (response.data is Map<String, dynamic>) {
        // Backend returns 'data' key, not 'items'
        final data = response.data['data'] as List? ??
                     response.data['items'] as List? ?? [];
        return data
            .map((json) => User.fromJson(json as Map<String, dynamic>))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch users',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get user by ID
  Future<User> getUserById(int id) async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.userById(id));
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch user',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Create new user
  Future<User> createUser(Map<String, dynamic> data) async {
    try {
      final response = await _apiClient.dio.post(
        ApiConfig.users,
        data: data,
      );
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to create user',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Update user
  Future<User> updateUser(int id, Map<String, dynamic> data) async {
    try {
      final response = await _apiClient.dio.put(
        ApiConfig.userById(id),
        data: data,
      );
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to update user',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Delete user
  Future<void> deleteUser(int id) async {
    try {
      await _apiClient.dio.delete(ApiConfig.userById(id));
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to delete user',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}
