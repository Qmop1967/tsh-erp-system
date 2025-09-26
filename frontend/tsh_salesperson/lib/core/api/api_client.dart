import 'dart:io';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000'; // Development URL
  static const String productionUrl = 'https://api.tsh-erp.com'; // Production URL
  
  late Dio _dio;
  static ApiClient? _instance;
  String? _authToken;

  static ApiClient get instance {
    _instance ??= ApiClient._internal();
    return _instance!;
  }

  ApiClient._internal() {
    _initializeDio();
  }

  void _initializeDio() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl, // Change to productionUrl for production
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add request interceptor for authentication
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        if (_authToken != null) {
          options.headers['Authorization'] = 'Bearer $_authToken';
        }
        
        // Log requests in debug mode
        print('🌐 REQUEST: ${options.method} ${options.path}');
        if (options.data != null) {
          print('📤 DATA: ${options.data}');
        }
        
        handler.next(options);
      },
      onResponse: (response, handler) {
        print('✅ RESPONSE: ${response.statusCode} ${response.requestOptions.path}');
        handler.next(response);
      },
      onError: (error, handler) {
        print('❌ ERROR: ${error.response?.statusCode} ${error.requestOptions.path}');
        print('❌ MESSAGE: ${error.message}');
        
        if (error.response?.statusCode == 401) {
          // Handle unauthorized access
          _handleUnauthorized();
        }
        
        handler.next(error);
      },
    ));
  }

  // Set authentication token
  Future<void> setAuthToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  // Load stored auth token
  Future<void> loadAuthToken() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
  }

  // Clear authentication
  Future<void> clearAuth() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  // Handle unauthorized access
  void _handleUnauthorized() async {
    await clearAuth();
    // Navigate to login screen (implement navigation logic)
  }

  // Check internet connectivity
  Future<bool> hasInternetConnection() async {
    final connectivityResult = await Connectivity().checkConnectivity();
    return connectivityResult != ConnectivityResult.none;
  }

  // ============================================
  // 🚨 CRITICAL: MONEY TRANSFER API ENDPOINTS
  // ============================================

  // Submit money transfer (FRAUD PREVENTION)
  Future<Response> submitMoneyTransfer(Map<String, dynamic> transferData) async {
    try {
      return await _dio.post('/api/money-transfers', data: transferData);
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // Get fraud alerts
  Future<Response> getFraudAlerts() async {
    try {
      return await _dio.get('/api/money-transfers/fraud-alerts');
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // Get money transfer dashboard
  Future<Response> getMoneyTransferDashboard() async {
    try {
      return await _dio.get('/api/money-transfers/dashboard');
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // Get salesperson transfers
  Future<Response> getMyTransfers({int limit = 100}) async {
    try {
      return await _dio.get('/api/money-transfers/my-transfers?limit=$limit');
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // Get weekly commission report
  Future<Response> getWeeklyCommissionReport(String weekStart) async {
    try {
      return await _dio.get('/api/money-transfers/reports/weekly-commission/me?week_start=$weekStart');
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // Verify receipt
  Future<Response> verifyReceipt(int transferId) async {
    try {
      return await _dio.post('/api/money-transfers/$transferId/verify-receipt');
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // Confirm money received
  Future<Response> confirmMoneyReceived(int transferId) async {
    try {
      return await _dio.post('/api/money-transfers/$transferId/confirm-received');
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // ============================================
  // 📍 GPS TRACKING API ENDPOINTS  
  // ============================================

  // Submit GPS location
  Future<Response> submitGPSLocation(Map<String, dynamic> locationData) async {
    try {
      return await _dio.post('/api/gps-tracking/location', data: locationData);
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // ============================================
  // 🔐 AUTHENTICATION API ENDPOINTS
  // ============================================

  // Login
  Future<Response> login(String email, String password) async {
    try {
      return await _dio.post('/api/auth/login', data: {
        'email': email,
        'password': password,
      });
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // Get current user profile
  Future<Response> getCurrentUser() async {
    try {
      return await _dio.get('/api/auth/me');
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // ============================================
  // 📁 FILE UPLOAD (Receipt Photos)
  // ============================================

  // Upload receipt photo
  Future<Response> uploadReceiptPhoto(String filePath) async {
    try {
      FormData formData = FormData.fromMap({
        'receipt': await MultipartFile.fromFile(filePath, filename: 'receipt.jpg'),
      });
      
      return await _dio.post('/api/upload/receipt', data: formData);
    } catch (e) {
      throw _handleApiError(e);
    }
  }

  // ============================================
  // ERROR HANDLING
  // ============================================

  ApiException _handleApiError(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return ApiException('Connection timeout. Please check your internet connection.', 'TIMEOUT');
        
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode;
          final message = error.response?.data?['detail'] ?? 'Server error occurred';
          return ApiException(message, 'HTTP_$statusCode');
        
        case DioExceptionType.cancel:
          return ApiException('Request was cancelled', 'CANCELLED');
        
        default:
          return ApiException('Network error. Please try again.', 'NETWORK_ERROR');
      }
    }
    
    return ApiException('An unexpected error occurred', 'UNKNOWN_ERROR');
  }
}

// Custom API Exception class
class ApiException implements Exception {
  final String message;
  final String code;

  ApiException(this.message, this.code);

  @override
  String toString() => 'ApiException: $message (Code: $code)';
} 