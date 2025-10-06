import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../models/auth_model.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService;
  
  AuthModel? _user;
  bool _isLoading = false;
  String? _error;
  bool _isLoggedIn = false;

  AuthProvider(this._authService);

  // Getters
  AuthModel? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isLoggedIn => _isLoggedIn;
  AuthService get authService => _authService;

  // Sign in method
  Future<bool> signIn(String email, String password) async {
    _setLoading(true);
    _clearError();

    try {
      final user = await _authService.login(email, password);
      if (user != null) {
        _user = user;
        _isLoggedIn = true;
        _setLoading(false);
        return true;
      }
      _setError('Invalid credentials');
      _setLoading(false);
      return false;
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Sign out method
  Future<void> signOut() async {
    _setLoading(true);
    
    try {
      await _authService.logout();
      _user = null;
      _isLoggedIn = false;
      _clearError();
    } catch (e) {
      _setError(e.toString());
    }
    
    _setLoading(false);
  }
  
  // Alias for signOut (for backward compatibility)
  Future<void> logout() => signOut();

  // Check authentication status
  Future<void> checkAuthStatus() async {
    _setLoading(true);
    
    try {
      final user = await _authService.getCurrentUser();
      if (user != null) {
        _user = user;
        _isLoggedIn = true;
      } else {
        _user = null;
        _isLoggedIn = false;
      }
    } catch (e) {
      _user = null;
      _isLoggedIn = false;
      _setError(e.toString());
    }
    
    _setLoading(false);
  }

  // Refresh user data
  Future<void> refreshUser() async {
    if (!_isLoggedIn || _user == null) return;

    try {
      final updatedUser = await _authService.getCurrentUser();
      if (updatedUser != null) {
        _user = updatedUser;
        notifyListeners();
      }
    } catch (e) {
      _setError(e.toString());
    }
  }

  // Private helper methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }

  // Update user info
  void updateUser(AuthModel user) {
    _user = user;
    notifyListeners();
  }

  // Check if user has specific permissions
  bool hasPermission(String permission) {
    return _user?.permissions?.contains(permission) ?? false;
  }

  // Get user role
  String get userRole => _user?.role ?? 'guest';

  // Get user display name
  String get displayName => _user?.displayName ?? 'User';

  // Get user initials
  String get userInitials {
    if (_user?.displayName != null) {
      final names = _user!.displayName.split(' ');
      if (names.length >= 2) {
        return '${names.first.substring(0, 1)}${names.last.substring(0, 1)}'.toUpperCase();
      } else if (names.isNotEmpty) {
        return names.first.substring(0, 1).toUpperCase();
      }
    }
    return 'U';
  }
}
