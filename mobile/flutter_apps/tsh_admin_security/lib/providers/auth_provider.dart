import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

/// Authentication Provider - State Management
class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();

  User? _currentUser;
  bool _isLoading = false;
  bool _isAuthenticated = false;
  String? _error;

  User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  String? get error => _error;

  /// Initialize - Check if user is already authenticated
  Future<void> initialize() async {
    print('🔧 AuthProvider: Initializing...');
    _isLoading = true;
    notifyListeners();

    try {
      final isAuth = await _authService.isAuthenticated();
      print('🔐 AuthProvider: Is authenticated? $isAuth');

      if (isAuth) {
        print('👤 AuthProvider: Fetching current user...');
        _currentUser = await _authService.getCurrentUser();
        _isAuthenticated = true;
        print('✅ AuthProvider: User loaded: ${_currentUser?.email}');
      } else {
        print('ℹ️  AuthProvider: No stored authentication found');
      }
    } catch (e, stackTrace) {
      print('❌ AuthProvider: Initialization error: $e');
      print('❌ Stack trace: $stackTrace');
      _isAuthenticated = false;
      _currentUser = null;
    } finally {
      _isLoading = false;
      notifyListeners();
      print('🏁 AuthProvider: Initialization complete (authenticated: $_isAuthenticated)');
    }
  }

  /// Login
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final loginResponse = await _authService.login(email, password);

      // Check if MFA is required
      if (loginResponse.requiresMfa) {
        _isLoading = false;
        notifyListeners();
        return false; // Return false to show MFA screen
      }

      _currentUser = loginResponse.user;
      _isAuthenticated = true;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isAuthenticated = false;
      _currentUser = null;
      _isLoading = false;
      notifyListeners();
      rethrow;
    }
  }

  /// Verify MFA
  Future<bool> verifyMfa(String code) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final loginResponse = await _authService.verifyMfa(code);
      _currentUser = loginResponse.user;
      _isAuthenticated = true;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      rethrow;
    }
  }

  /// Logout
  Future<void> logout() async {
    await _authService.logout();
    _currentUser = null;
    _isAuthenticated = false;
    notifyListeners();
  }

  /// Refresh user data
  Future<void> refreshUser() async {
    try {
      _currentUser = await _authService.getCurrentUser();
      notifyListeners();
    } catch (e) {
      print('Failed to refresh user: $e');
    }
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
