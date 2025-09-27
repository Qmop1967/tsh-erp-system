import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class AuthService {
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';
  
  // Login user
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await ApiService.post(
        endpoint: '/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );
      
      // Store token and user data
      if (response['access_token'] != null) {
        await storeToken(response['access_token']);
        if (response['user'] != null) {
          await storeUserData(response['user']);
        }
      }
      
      return response;
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }
  
  // Verify token
  Future<bool> verifyToken(String token) async {
    try {
      await ApiService.get(
        endpoint: '/auth/me',
        token: token,
      );
      return true;
    } catch (e) {
      return false;
    }
  }
  
  // Store token
  Future<void> storeToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }
  
  // Get stored token
  Future<String?> getStoredToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }
  
  // Store user data
  Future<void> storeUserData(Map<String, dynamic> userData) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, json.encode(userData));
  }
  
  // Get stored user data
  Future<Map<String, dynamic>?> getStoredUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString(_userKey);
    if (userDataString != null) {
      return json.decode(userDataString);
    }
    return null;
  }
  
  // Get current user info
  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final token = await getStoredToken();
      if (token == null) {
        throw Exception('No token found');
      }
      
      final response = await ApiService.get(
        endpoint: '/auth/me',
        token: token,
      );
      
      return response;
    } catch (e) {
      throw Exception('Failed to get current user: $e');
    }
  }
  
  // Logout
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }
  
  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await getStoredToken();
    if (token == null) return false;
    
    return await verifyToken(token);
  }
}
