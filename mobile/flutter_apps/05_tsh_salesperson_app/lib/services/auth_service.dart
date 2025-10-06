import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/auth_model.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _apiService;
  
  static const String _baseUrl = 'http://192.168.68.66:8000'; // Mac's local IP address
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';

  AuthService(this._apiService);

  // Login method - Uses mobile-specific endpoint
  Future<AuthModel?> login(String email, String password) async {
    try {
      // Use the mobile login endpoint that allows all users
      // Fixed: Added /api prefix to match backend router configuration
      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/login/mobile'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);

        // Backend returns response directly without 'success'/'data' wrapper
        // Response format: { "access_token": "...", "token_type": "bearer", "user": {...} }
        if (data['access_token'] != null && data['user'] != null) {
          final token = data['access_token'] as String;
          final userInfo = data['user'] as Map<String, dynamic>;

          // Save token and user data locally
          await _saveTokenAndUser(token, userInfo);

          // Create UserModel from user data
          final user = UserModel(
            id: userInfo['id'] as int,
            name: userInfo['name'] as String? ?? 'User',
            email: userInfo['email'] as String?,
            active: true,
          );

          // Return AuthModel with token and user
          return AuthModel(
            token: token,
            user: user,
          );
        }
      }
      
      return null;
    } catch (e) {
      print('Login error: $e');
      return null;
    }
  }

  // Logout method
  Future<void> logout() async {
    try {
      final token = await getToken();
      if (token != null) {
        await http.post(
          Uri.parse('$_baseUrl/auth/logout'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        );
      }
    } catch (e) {
      print('Logout error: $e');
    } finally {
      // Clear local storage
      await _clearTokenAndUser();
    }
  }

  // Get current user
  Future<AuthModel?> getCurrentUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userJson = prefs.getString(_userKey);
      
      if (userJson != null) {
        final Map<String, dynamic> userData = jsonDecode(userJson);
        return AuthModel.fromJson(userData);
      }
      
      return null;
    } catch (e) {
      print('Get current user error: $e');
      return null;
    }
  }

  // Get stored token
  Future<String?> getToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_tokenKey);
    } catch (e) {
      print('Get token error: $e');
      return null;
    }
  }

  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  // Refresh token
  Future<String?> refreshToken() async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/refresh'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        
        // Backend returns response directly without 'success'/'data' wrapper
        if (data['access_token'] != null) {
          final newToken = data['access_token'];
          
          // Save new token
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString(_tokenKey, newToken);
          
          return newToken;
        }
      }
      
      return null;
    } catch (e) {
      print('Refresh token error: $e');
      return null;
    }
  }

  // Change password
  Future<bool> changePassword(String currentPassword, String newPassword) async {
    try {
      final token = await getToken();
      if (token == null) return false;

      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/change-password'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'current_password': currentPassword,
          'new_password': newPassword,
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return data['success'] == true;
      }
      
      return false;
    } catch (e) {
      print('Change password error: $e');
      return false;
    }
  }

  // Reset password request
  Future<bool> requestPasswordReset(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/reset-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return data['success'] == true;
      }
      
      return false;
    } catch (e) {
      print('Password reset request error: $e');
      return false;
    }
  }

  // Update profile
  Future<AuthModel?> updateProfile(Map<String, dynamic> profileData) async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.put(
        Uri.parse('$_baseUrl/api/auth/profile'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(profileData),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        
        if (data['success'] == true && data['data'] != null) {
          final updatedUser = data['data'];
          
          // Update local user data
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString(_userKey, jsonEncode(updatedUser));
          
          return AuthModel.fromJson(updatedUser);
        }
      }
      
      return null;
    } catch (e) {
      print('Update profile error: $e');
      return null;
    }
  }

  // Validate token
  Future<bool> validateToken() async {
    try {
      final token = await getToken();
      if (token == null) return false;

      final response = await http.get(
        Uri.parse('$_baseUrl/auth/validate'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      print('Validate token error: $e');
      return false;
    }
  }

  // Private helper methods
  Future<void> _saveTokenAndUser(String token, Map<String, dynamic> user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    await prefs.setString(_userKey, jsonEncode(user));
  }

  Future<void> _clearTokenAndUser() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }

  // Mock login for demo purposes
  Future<AuthModel?> mockLogin(String email, String password) async {
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    // Mock authentication - in real app, validate against server
    if (email.isNotEmpty && password.isNotEmpty) {
      final mockUser = {
        'id': 1,
        'email': email,
        'display_name': 'مندوب المبيعات',
        'role': 'salesperson',
        'permissions': ['sales', 'customers', 'orders', 'payments'],
        'branch_id': 1,
        'branch_name': 'فرع بغداد الرئيسي',
        'phone': '+964 770 123 4567',
        'avatar_url': null,
        'is_active': true,
        'last_login': DateTime.now().toIso8601String(),
      };

      // Save mock data
      await _saveTokenAndUser('mock_token_${DateTime.now().millisecondsSinceEpoch}', mockUser);

      return AuthModel.fromJson(mockUser);
    }

    return null;
  }

  // Mock current user for demo
  Future<AuthModel?> getMockCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_userKey);
    
    if (userJson != null) {
      final Map<String, dynamic> userData = jsonDecode(userJson);
      return AuthModel.fromJson(userData);
    }

    // Return default mock user if no stored data
    final mockUser = {
      'id': 1,
      'email': 'salesperson@tsh.com',
      'display_name': 'مندوب المبيعات',
      'role': 'salesperson',
      'permissions': ['sales', 'customers', 'orders', 'payments'],
      'branch_id': 1,
      'branch_name': 'فرع بغداد الرئيسي',
      'phone': '+964 770 123 4567',
      'avatar_url': null,
      'is_active': true,
      'last_login': DateTime.now().toIso8601String(),
    };

    return AuthModel.fromJson(mockUser);
  }
}
