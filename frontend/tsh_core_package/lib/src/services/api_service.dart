import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/common.dart';

class ApiService {
  static const String _baseUrl = 'http://localhost:8000/api'; // Update with your API URL
  static const String _tokenKey = 'auth_token';
  static const String _refreshTokenKey = 'refresh_token';

  late final Dio _dio;
  late final FlutterSecureStorage _storage;

  ApiService() {
    _storage = const FlutterSecureStorage();
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: AppConfig.defaultTimeout,
      receiveTimeout: AppConfig.defaultTimeout,
      sendTimeout: AppConfig.defaultTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _setupInterceptors();
  }

  void _setupInterceptors() {
    // Request interceptor to add auth token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Try to refresh token
          final refreshed = await _refreshToken();
          if (refreshed) {
            // Retry the original request
            final opts = error.requestOptions;
            final token = await getToken();
            if (token != null) {
              opts.headers['Authorization'] = 'Bearer $token';
            }
            try {
              final response = await _dio.fetch(opts);
              return handler.resolve(response);
            } catch (e) {
              return handler.next(error);
            }
          } else {
            // Refresh failed, clear tokens and redirect to login
            await clearTokens();
            throw AuthException('Session expired. Please login again.');
          }
        }
        handler.next(error);
      },
    ));

    // Logging interceptor (only in debug mode)
    _dio.interceptors.add(LogInterceptor(
      requestHeader: true,
      requestBody: true,
      responseHeader: true,
      responseBody: true,
      error: true,
    ));
  }

  // Token management
  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }

  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: _tokenKey, value: accessToken);
    await _storage.write(key: _refreshTokenKey, value: refreshToken);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        await saveTokens(data['access_token'], data['refresh_token']);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // Generic API methods
  Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final response = await _dio.get(endpoint, queryParameters: queryParameters);
      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> post<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final response = await _dio.post(
        endpoint,
        data: data,
        queryParameters: queryParameters,
      );
      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> put<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final response = await _dio.put(
        endpoint,
        data: data,
        queryParameters: queryParameters,
      );
      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final response = await _dio.delete(
        endpoint,
        data: data,
        queryParameters: queryParameters,
      );
      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  // File upload
  Future<ApiResponse<T>> uploadFile<T>(
    String endpoint,
    File file, {
    String fieldName = 'file',
    Map<String, dynamic>? additionalData,
    T Function(Map<String, dynamic>)? fromJson,
    ProgressCallback? onProgress,
  }) async {
    try {
      final formData = FormData();
      formData.files.add(MapEntry(
        fieldName,
        await MultipartFile.fromFile(file.path, filename: file.path.split('/').last),
      ));

      if (additionalData != null) {
        additionalData.forEach((key, value) {
          formData.fields.add(MapEntry(key, value.toString()));
        });
      }

      final response = await _dio.post(
        endpoint,
        data: formData,
        onSendProgress: onProgress,
      );

      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return _handleError<T>(e);
    }
  }

  ApiResponse<T> _handleResponse<T>(
    Response response,
    T Function(Map<String, dynamic>)? fromJson,
  ) {
    if (response.statusCode! >= 200 && response.statusCode! < 300) {
      final data = response.data;
      T? parsedData;

      if (fromJson != null && data != null) {
        if (data is Map<String, dynamic>) {
          parsedData = fromJson(data);
        } else if (data is List) {
          // Handle list responses - this might need adjustment based on your API
          parsedData = data as T;
        }
      } else {
        parsedData = data as T?;
      }

      return ApiResponse.success(
        data: parsedData,
        message: data['message'] as String?,
      );
    } else {
      return ApiResponse.error(
        error: response.data['error'] ?? 'Request failed',
        statusCode: response.statusCode,
      );
    }
  }

  ApiResponse<T> _handleError<T>(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return ApiResponse.error(
            error: 'Connection timeout. Please check your internet connection.',
            statusCode: error.response?.statusCode,
          );
        case DioExceptionType.badResponse:
          final message = error.response?.data['message'] ?? 
                          error.response?.data['error'] ?? 
                          'Server error occurred';
          return ApiResponse.error(
            error: message,
            statusCode: error.response?.statusCode,
          );
        case DioExceptionType.cancel:
          return ApiResponse.error(error: 'Request was cancelled');
        case DioExceptionType.connectionError:
          return ApiResponse.error(error: 'No internet connection');
        default:
          return ApiResponse.error(
            error: error.message ?? 'An unexpected error occurred',
            statusCode: error.response?.statusCode,
          );
      }
    }

    if (error is SocketException) {
      return ApiResponse.error(error: 'No internet connection');
    }

    return ApiResponse.error(
      error: error.toString(),
    );
  }
}
