import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/user.dart';
import 'api_client.dart';

/// Pagination metadata for user lists
class PaginatedUserResponse {
  final List<User> users;
  final int total;
  final int page;
  final int pages;
  final int perPage;

  PaginatedUserResponse({
    required this.users,
    required this.total,
    required this.page,
    required this.pages,
    required this.perPage,
  });

  factory PaginatedUserResponse.fromJson(Map<String, dynamic> json) {
    return PaginatedUserResponse(
      users: (json['data'] as List)
          .map((userJson) => User.fromJson(userJson as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      pages: json['pages'] as int? ?? 1,
      perPage: json['per_page'] as int? ?? 20,
    );
  }

  bool get hasNextPage => page < pages;
  bool get hasPreviousPage => page > 1;
}

/// User Management Service
class UserService {
  final ApiClient _apiClient = ApiClient();

  /// Get all users (paginated) with metadata
  /// Enhanced to load ALL users by fetching all pages automatically
  Future<PaginatedUserResponse> getUsersPaginated({
    int page = 1,
    int pageSize = 20,
    String? search,
    bool? isActive,
    String? role,
    bool loadAll = false, // New parameter to load all users
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

      // Backend returns paginated response with 'data' key
      if (response.data is Map<String, dynamic>) {
        final paginatedResponse = PaginatedUserResponse.fromJson(response.data);
        
        // If loadAll is true and there are more pages, fetch them all
        if (loadAll && paginatedResponse.hasNextPage) {
          final allUsers = <User>[...paginatedResponse.users];
          int currentPage = page + 1;
          
          // Fetch remaining pages
          while (currentPage <= paginatedResponse.pages) {
            final nextPageResponse = await getUsersPaginated(
              page: currentPage,
              pageSize: pageSize,
              search: search,
              isActive: isActive,
              role: role,
              loadAll: false, // Don't recurse
            );
            allUsers.addAll(nextPageResponse.users);
            currentPage++;
          }
          
          // Return combined response
          return PaginatedUserResponse(
            users: allUsers,
            total: paginatedResponse.total,
            page: 1,
            pages: 1,
            perPage: allUsers.length,
          );
        }
        
        return paginatedResponse;
      }

      // Fallback for simple list response
      if (response.data is List) {
        final users = (response.data as List)
            .map((json) => User.fromJson(json as Map<String, dynamic>))
            .toList();
        return PaginatedUserResponse(
          users: users,
          total: users.length,
          page: 1,
          pages: 1,
          perPage: users.length,
        );
      }

      return PaginatedUserResponse(
        users: [],
        total: 0,
        page: 1,
        pages: 1,
        perPage: pageSize,
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch users',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get ALL users from database (loads all pages automatically)
  Future<List<User>> getAllUsers({
    String? search,
    bool? isActive,
    String? role,
  }) async {
    final response = await getUsersPaginated(
      page: 1,
      pageSize: 100, // Use max page size for efficiency
      search: search,
      isActive: isActive,
      role: role,
      loadAll: true, // Load all pages
    );
    return response.users;
  }

  /// Get all users (simple list - backward compatibility)
  Future<List<User>> getUsers({
    int page = 1,
    int pageSize = 20,
    String? search,
    bool? isActive,
  }) async {
    final response = await getUsersPaginated(
      page: page,
      pageSize: pageSize,
      search: search,
      isActive: isActive,
    );
    return response.users;
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

  /// Activate user
  Future<User> activateUser(int id) async {
    try {
      final response = await _apiClient.dio.put(
        ApiConfig.userById(id),
        data: {'is_active': true},
      );
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to activate user',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Deactivate user
  Future<User> deactivateUser(int id) async {
    try {
      final response = await _apiClient.dio.put(
        ApiConfig.userById(id),
        data: {'is_active': false},
      );
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to deactivate user',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Update user role
  Future<User> updateUserRole(int id, int roleId) async {
    try {
      final response = await _apiClient.dio.put(
        ApiConfig.userById(id),
        data: {'role_id': roleId},
      );
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to update user role',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Reset user password
  Future<void> resetUserPassword(int id, String newPassword) async {
    try {
      await _apiClient.dio.put(
        ApiConfig.userById(id),
        data: {'password': newPassword},
      );
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to reset password',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get user permissions
  Future<List<String>> getUserPermissions(int id) async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.userPermissions(id));
      if (response.data is List) {
        return List<String>.from(response.data);
      }
      if (response.data is Map && response.data['permissions'] != null) {
        return List<String>.from(response.data['permissions']);
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

  /// Get available roles
  Future<List<Map<String, dynamic>>> getRoles() async {
    try {
      final response = await _apiClient.dio.get('${ApiConfig.users}/roles');
      if (response.data is List) {
        return List<Map<String, dynamic>>.from(response.data);
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
}
