import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';

/// API Client with JWT Authentication and Interceptors
class ApiClient {
  late final Dio _dio;
  // Use FlutterSecureStorage for mobile, SharedPreferences for web
  final FlutterSecureStorage? _storage = kIsWeb ? null : const FlutterSecureStorage();
  SharedPreferences? _prefs;

  // Singleton pattern
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  ApiClient._internal() {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: ApiConfig.connectionTimeout,
        receiveTimeout: ApiConfig.receiveTimeout,
        sendTimeout: ApiConfig.sendTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Initialize SharedPreferences for web
    if (kIsWeb) {
      SharedPreferences.getInstance().then((prefs) {
        _prefs = prefs;
      });
    }

    // Add interceptors
    _dio.interceptors.add(_AuthInterceptor(_storage, _prefs));
    _dio.interceptors.add(_LoggingInterceptor());
    _dio.interceptors.add(_ErrorInterceptor());
  }

  Dio get dio => _dio;

  // Save auth token
  Future<void> saveToken(String token) async {
    if (kIsWeb) {
      final prefs = _prefs ?? await SharedPreferences.getInstance();
      await prefs.setString('access_token', token);
      _prefs = prefs;
    } else {
      await _storage!.write(key: 'access_token', value: token);
    }
  }

  // Get auth token
  Future<String?> getToken() async {
    if (kIsWeb) {
      final prefs = _prefs ?? await SharedPreferences.getInstance();
      _prefs = prefs;
      return prefs.getString('access_token');
    } else {
      return await _storage!.read(key: 'access_token');
    }
  }

  // Remove auth token
  Future<void> removeToken() async {
    if (kIsWeb) {
      final prefs = _prefs ?? await SharedPreferences.getInstance();
      await prefs.remove('access_token');
      _prefs = prefs;
    } else {
      await _storage!.delete(key: 'access_token');
    }
  }

  // Check if user is authenticated
  Future<bool> isAuthenticated() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}

/// Authentication Interceptor - Adds JWT token to requests
class _AuthInterceptor extends Interceptor {
  final FlutterSecureStorage? _storage;
  final SharedPreferences? _prefs;

  _AuthInterceptor(this._storage, this._prefs);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Skip auth for login endpoint
    if (options.path.contains('/auth/login')) {
      return handler.next(options);
    }

    // Add JWT token to headers
    String? token;
    if (kIsWeb) {
      token = _prefs?.getString('access_token');
    } else {
      token = await _storage?.read(key: 'access_token');
    }
    
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }

    handler.next(options);
  }
}

/// Logging Interceptor - Logs requests and responses (development only)
class _LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (ApiConfig.isDevelopment) {
      print('🌐 REQUEST[${options.method}] => ${options.uri}');
      if (options.data != null) {
        print('📤 Data: ${options.data}');
      }
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (ApiConfig.isDevelopment) {
      print('✅ RESPONSE[${response.statusCode}] => ${response.requestOptions.uri}');
      print('📥 Data: ${response.data}');
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (ApiConfig.isDevelopment) {
      print('❌ ERROR[${err.response?.statusCode}] => ${err.requestOptions.uri}');
      print('⚠️ Message: ${err.message}');
      if (err.response?.data != null) {
        print('📛 Error Data: ${err.response?.data}');
      }
    }
    handler.next(err);
  }
}

/// Error Interceptor - Handles common errors
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    String errorMessage;

    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        errorMessage = 'Connection timeout. Please check your internet connection.';
        break;

      case DioExceptionType.badResponse:
        errorMessage = _handleResponseError(err.response);
        break;

      case DioExceptionType.cancel:
        errorMessage = 'Request was cancelled';
        break;

      case DioExceptionType.unknown:
        errorMessage = 'Network error occurred. Please try again.';
        break;

      default:
        errorMessage = 'An unexpected error occurred';
    }

    // Create custom error with user-friendly message
    final customError = DioException(
      requestOptions: err.requestOptions,
      response: err.response,
      type: err.type,
      error: errorMessage,
    );

    handler.next(customError);
  }

  String _handleResponseError(Response? response) {
    if (response == null) return 'Unknown error occurred';

    switch (response.statusCode) {
      case 400:
        return _extractErrorMessage(response) ?? 'Bad request';
      case 401:
        return 'Your session has expired. Please log in again.';
      case 403:
        return 'Access denied. You don\'t have permission.';
      case 404:
        return 'Resource not found';
      case 422:
        return _extractErrorMessage(response) ?? 'Validation error';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return 'Error ${response.statusCode}: ${response.statusMessage}';
    }
  }

  String? _extractErrorMessage(Response response) {
    try {
      final data = response.data;
      if (data is Map<String, dynamic>) {
        return data['detail'] ?? data['message'] ?? data['error'];
      }
    } catch (e) {
      // Ignore parsing errors
    }
    return null;
  }
}

/// API Exception for better error handling
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
