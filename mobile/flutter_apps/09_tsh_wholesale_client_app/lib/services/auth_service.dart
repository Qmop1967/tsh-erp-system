import 'dart:async';
import '../config/api_config.dart';
import '../models/api_response.dart';
import '../models/user.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthService {
  final ApiService _apiService;
  final StorageService _storageService;

  static const String _userKey = 'current_user';

  final StreamController<User?> _userController =
      StreamController<User?>.broadcast();
  Stream<User?> get userStream => _userController.stream;

  User? _currentUser;
  User? get currentUser => _currentUser;
  bool get isAuthenticated => _currentUser != null;

  AuthService(this._apiService, this._storageService) {
    _loadSavedUser();
  }

  /// Load saved user from storage on app start
  Future<void> _loadSavedUser() async {
    try {
      final userData = await _storageService.getData(_userKey);
      if (userData != null) {
        _currentUser = User.fromJson(userData);
        _userController.add(_currentUser);
      }
    } catch (e) {
      // If loading saved user fails, clear it
      await _storageService.removeData(_userKey);
      _currentUser = null;
      _userController.add(null);
    }
  }

  /// Login with email and password - Uses mobile login endpoint
  Future<ApiResponse<User>> login(String email, String password) async {
    try {
      // Call mobile login endpoint (returns access_token + refresh_token)
      final response = await _apiService.post(
        ApiConfig.authLoginMobile,
        data: {
          'email': email,
          'password': password,
        },
      );

      if (response.success && response.data != null) {
        final data = response.data as Map<String, dynamic>;

        // Save tokens (access token + refresh token with 30 days expiration)
        await _apiService.saveTokens(
          data['access_token'],
          data['refresh_token'],
        );

        // Parse and save user data
        final userData = data['user'] as Map<String, dynamic>;
        _currentUser = User.fromJson(userData);

        await _storageService.saveData(_userKey, _currentUser!.toJson());
        _userController.add(_currentUser);

        return ApiResponse.success(
          data: _currentUser,
          message: 'Login successful',
        );
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Login failed',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  /// Logout - Clear tokens and user data
  Future<ApiResponse<void>> logout() async {
    try {
      // Try to logout from server
      await _apiService.post(ApiConfig.authLogout);
    } catch (e) {
      // Continue with local logout even if server logout fails
    }

    // Clear local data
    await _apiService.clearTokens();
    await _storageService.removeData(_userKey);
    _currentUser = null;
    _userController.add(null);

    return ApiResponse.success(message: 'Logged out successfully');
  }

  /// Get current user info from server
  Future<ApiResponse<User>> getCurrentUser() async {
    try {
      final response = await _apiService.get(ApiConfig.authMe);

      if (response.success && response.data != null) {
        final userData = response.data as Map<String, dynamic>;
        _currentUser = User.fromJson(userData);
        await _storageService.saveData(_userKey, _currentUser!.toJson());
        _userController.add(_currentUser);

        return ApiResponse.success(data: _currentUser);
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Failed to get user info',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  /// Check if user has specific permission
  bool hasPermission(String permission) {
    return _currentUser?.hasPermission(permission) ?? false;
  }

  /// Check if user has any of the specified permissions
  bool hasAnyPermission(List<String> permissions) {
    return _currentUser?.hasAnyPermission(permissions) ?? false;
  }

  /// Check if user has all of the specified permissions
  bool hasAllPermissions(List<String> permissions) {
    return _currentUser?.hasAllPermissions(permissions) ?? false;
  }

  /// Dispose the service
  void dispose() {
    _userController.close();
  }
}
