import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/user.dart';
import 'api_client.dart';

/// Authentication Service
class AuthService {
  final ApiClient _apiClient = ApiClient();

  /// Login with email and password
  Future<LoginResponse> login(String email, String password) async {
    try {
      final response = await _apiClient.dio.post(
        ApiConfig.authLogin,
        data: {
          'email': email,
          'password': password,
        },
      );

      final loginResponse = LoginResponse.fromJson(response.data);

      // Save token
      await _apiClient.saveToken(loginResponse.accessToken);

      return loginResponse;
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Login failed',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Verify MFA code
  Future<LoginResponse> verifyMfa(String code) async {
    try {
      final response = await _apiClient.dio.post(
        ApiConfig.authMfaVerify,
        data: {'code': code},
      );

      final loginResponse = LoginResponse.fromJson(response.data);

      // Update token
      await _apiClient.saveToken(loginResponse.accessToken);

      return loginResponse;
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'MFA verification failed',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get current authenticated user
  Future<User> getCurrentUser() async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.authMe);
      return User.fromJson(response.data);
    } on DioException catch (e) {
      print('🔍 DioException caught - Type: ${e.type}');
      print('🔍 Status Code: ${e.response?.statusCode}');
      print('🔍 Error: ${e.error}');
      print('🔍 Message: ${e.message}');

      // Handle specific error cases
      if (e.response?.statusCode == 401) {
        throw ApiException(
          message: 'Your session has expired. Please log in again.',
          statusCode: 401,
          data: e.response?.data,
        );
      }

      // Use error message from interceptor if available
      final errorMessage = e.error?.toString() ?? 'Failed to get user info';
      throw ApiException(
        message: errorMessage,
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    } catch (e) {
      print('🔍 Unexpected error type: ${e.runtimeType}');
      print('🔍 Error: $e');
      rethrow;
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      // Call backend logout endpoint
      await _apiClient.dio.post(ApiConfig.authLogout);
    } catch (e) {
      // Continue with local logout even if backend fails
      print('Logout error: $e');
    } finally {
      // Always remove local token
      await _apiClient.removeToken();
    }
  }

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    return await _apiClient.isAuthenticated();
  }

  /// Refresh access token
  Future<void> refreshToken() async {
    try {
      final response = await _apiClient.dio.post(ApiConfig.authRefresh);
      final newToken = response.data['access_token'] as String;
      await _apiClient.saveToken(newToken);
    } on DioException catch (e) {
      // If refresh fails, logout
      await logout();
      throw ApiException(
        message: 'Session expired. Please login again.',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}

/// API Exception
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException({
    required this.message,
    this.statusCode,
    this.data,
  });

  @override
  String toString() => message;
}
