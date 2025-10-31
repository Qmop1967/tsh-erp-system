import 'dart:async';
import '../models/user.dart';
import '../models/common.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthService {
  final ApiService _apiService;
  final StorageService _storageService;
  
  static const String _userKey = 'current_user';
  
  final StreamController<User?> _userController = StreamController<User?>.broadcast();
  Stream<User?> get userStream => _userController.stream;
  
  User? _currentUser;
  User? get currentUser => _currentUser;
  bool get isAuthenticated => _currentUser != null;

  AuthService(this._apiService, this._storageService) {
    _loadSavedUser();
  }

  Future<void> _loadSavedUser() async {
    try {
      final userData = await _storageService.getData(_userKey);
      if (userData != null) {
        _currentUser = User.fromJson(userData);
        _userController.add(_currentUser);
      } else {
        // For demo purposes, auto-create a demo user if none exists
        await _createDemoUser();
      }
    } catch (e) {
      // If loading saved user fails, create demo user
      await _storageService.removeData(_userKey);
      await _createDemoUser();
    }
  }

  Future<void> _createDemoUser() async {
    final demoUser = User(
      id: 1,
      email: 'demo@tsh.com',
      firstName: 'Demo',
      lastName: 'User',
      phoneNumber: '+1234567890',
      isActive: true,
      createdAt: DateTime.now().subtract(const Duration(days: 30)),
      updatedAt: DateTime.now(),
      role: Role(
        id: 1,
        name: 'Sales Representative',
        permissions: ['sales', 'customers', 'orders'],
        createdAt: DateTime.now().subtract(const Duration(days: 30)),
        updatedAt: DateTime.now(),
      ),
      branch: Branch(
        id: 1,
        name: 'Main Branch',
        address: '123 Business St, City, Country',
        phoneNumber: '+1234567890',
        email: 'main@tsh.com',
        isActive: true,
        createdAt: DateTime.now().subtract(const Duration(days: 30)),
        updatedAt: DateTime.now(),
      ),
    );

    _currentUser = demoUser;
    _userController.add(_currentUser);
    await _storageService.saveData(_userKey, demoUser.toJson());
  }

  Future<ApiResponse<User>> login(String email, String password) async {
    try {
      // Call mobile login endpoint
      final response = await _apiService.post(
        '/auth/login/mobile',
        data: {
          'email': email,
          'password': password,
        },
      );

      if (response.success && response.data != null) {
        final data = response.data;

        // Save tokens (access token + refresh token)
        await _apiService.saveTokens(
          data['access_token'],
          data['refresh_token'], // 30 days expiration
        );

        // Parse and save user data
        final userData = data['user'];
        _currentUser = User(
          id: userData['id'],
          email: userData['email'],
          firstName: userData['name'].split(' ').first,
          lastName: userData['name'].split(' ').length > 1
              ? userData['name'].split(' ').sublist(1).join(' ')
              : '',
          phoneNumber: userData['phone'] ?? '',
          isActive: true,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
          role: Role(
            id: 1,
            name: userData['role'] ?? 'User',
            permissions: List<String>.from(userData['permissions'] ?? []),
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ),
          branch: Branch(
            id: 1,
            name: userData['branch'] ?? 'Main Branch',
            address: '',
            phoneNumber: '',
            email: '',
            isActive: true,
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ),
        );

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

  Future<ApiResponse<User>> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String? phoneNumber,
  }) async {
    try {
      final response = await _apiService.post<User>(
        '/auth/register',
        data: {
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
          if (phoneNumber != null) 'phone_number': phoneNumber,
        },
        fromJson: (json) => User.fromJson(json),
      );

      if (response.success && response.data != null) {
        return ApiResponse.success(
          data: response.data,
          message: 'Registration successful',
        );
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Registration failed',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  Future<ApiResponse<void>> logout() async {
    try {
      // Try to logout from server
      await _apiService.post('/auth/logout');
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

  Future<ApiResponse<void>> forgotPassword(String email) async {
    try {
      final response = await _apiService.post(
        '/auth/forgot-password',
        data: {'email': email},
      );

      if (response.success) {
        return ApiResponse.success(
          message: 'Password reset instructions sent to your email',
        );
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Failed to send reset instructions',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  Future<ApiResponse<void>> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    try {
      final response = await _apiService.post(
        '/auth/reset-password',
        data: {
          'token': token,
          'new_password': newPassword,
        },
      );

      if (response.success) {
        return ApiResponse.success(message: 'Password reset successfully');
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Failed to reset password',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  Future<ApiResponse<void>> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    try {
      final response = await _apiService.post(
        '/auth/change-password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      );

      if (response.success) {
        return ApiResponse.success(message: 'Password changed successfully');
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Failed to change password',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  Future<ApiResponse<User>> updateProfile({
    String? firstName,
    String? lastName,
    String? phoneNumber,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (firstName != null) data['first_name'] = firstName;
      if (lastName != null) data['last_name'] = lastName;
      if (phoneNumber != null) data['phone_number'] = phoneNumber;

      final response = await _apiService.put<User>(
        '/auth/profile',
        data: data,
        fromJson: (json) => User.fromJson(json),
      );

      if (response.success && response.data != null) {
        _currentUser = response.data;
        await _storageService.saveData(_userKey, _currentUser!.toJson());
        _userController.add(_currentUser);

        return ApiResponse.success(
          data: _currentUser,
          message: 'Profile updated successfully',
        );
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Failed to update profile',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  Future<ApiResponse<User>> getCurrentUser() async {
    try {
      final response = await _apiService.get<User>(
        '/auth/me',
        fromJson: (json) => User.fromJson(json),
      );

      if (response.success && response.data != null) {
        _currentUser = response.data;
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

  bool hasPermission(String permission) {
    return _currentUser?.role?.permissions.contains(permission) ?? false;
  }

  bool hasAnyPermission(List<String> permissions) {
    if (_currentUser?.role?.permissions == null) return false;
    return permissions.any((permission) => 
        _currentUser!.role!.permissions.contains(permission));
  }

  bool hasAllPermissions(List<String> permissions) {
    if (_currentUser?.role?.permissions == null) return false;
    return permissions.every((permission) => 
        _currentUser!.role!.permissions.contains(permission));
  }

  void dispose() {
    _userController.close();
  }
}
