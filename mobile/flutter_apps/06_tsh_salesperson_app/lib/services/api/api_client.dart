import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Base API Client for all backend communication
/// Handles authentication, error handling, and common HTTP operations
class ApiClient {
  // API Base URLs (configurable per environment)
  static const String _productionUrl = 'https://erp.tsh.sale/api';
  static const String _stagingUrl = 'https://staging.erp.tsh.sale/api';
  static const String _developmentUrl = 'http://localhost:8000/api';

  // Current environment (can be changed via config)
  static const String _environment = 'production'; // production | staging | development

  // Storage keys
  static const String _tokenKey = 'auth_token';
  static const String _refreshTokenKey = 'refresh_token';

  // Timeout durations
  static const Duration _connectTimeout = Duration(seconds: 30);
  static const Duration _receiveTimeout = Duration(seconds: 30);

  /// Get base URL based on environment
  String get baseUrl {
    switch (_environment) {
      case 'production':
        return _productionUrl;
      case 'staging':
        return _stagingUrl;
      case 'development':
        return _developmentUrl;
      default:
        return _productionUrl;
    }
  }

  /// Get stored auth token
  Future<String?> _getToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_tokenKey);
    } catch (e) {
      print('Error getting token: $e');
      return null;
    }
  }

  /// Save auth token
  Future<void> _saveToken(String token) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey, token);
    } catch (e) {
      print('Error saving token: $e');
    }
  }

  /// Build headers with authentication
  Future<Map<String, String>> _buildHeaders({
    bool requiresAuth = true,
    Map<String, String>? additionalHeaders,
  }) async {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (requiresAuth) {
      final token = await _getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    if (additionalHeaders != null) {
      headers.addAll(additionalHeaders);
    }

    return headers;
  }

  /// Handle API response and errors
  ApiResponse _handleResponse(http.Response response) {
    try {
      final statusCode = response.statusCode;
      final body = response.body;

      // Parse response body
      dynamic data;
      try {
        data = jsonDecode(body);
      } catch (e) {
        data = body;
      }

      // Success responses (2xx)
      if (statusCode >= 200 && statusCode < 300) {
        return ApiResponse(
          success: true,
          statusCode: statusCode,
          data: data,
        );
      }

      // Error responses
      String errorMessage = 'Unknown error occurred';
      if (data is Map<String, dynamic>) {
        errorMessage = data['message'] ?? data['detail'] ?? data['error'] ?? errorMessage;
      }

      return ApiResponse(
        success: false,
        statusCode: statusCode,
        data: data,
        errorMessage: errorMessage,
      );
    } catch (e) {
      return ApiResponse(
        success: false,
        statusCode: response.statusCode,
        errorMessage: 'Failed to parse response: $e',
      );
    }
  }

  /// GET request
  Future<ApiResponse> get(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    bool requiresAuth = true,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint').replace(
        queryParameters: queryParameters?.map(
          (key, value) => MapEntry(key, value.toString()),
        ),
      );

      final headers = await _buildHeaders(requiresAuth: requiresAuth);

      final response = await http
          .get(uri, headers: headers)
          .timeout(_connectTimeout);

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse(
        success: false,
        statusCode: 0,
        errorMessage: 'Network error: $e',
      );
    }
  }

  /// POST request
  Future<ApiResponse> post(
    String endpoint, {
    dynamic body,
    bool requiresAuth = true,
    Map<String, String>? additionalHeaders,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final headers = await _buildHeaders(
        requiresAuth: requiresAuth,
        additionalHeaders: additionalHeaders,
      );

      final response = await http
          .post(
            uri,
            headers: headers,
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(_connectTimeout);

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse(
        success: false,
        statusCode: 0,
        errorMessage: 'Network error: $e',
      );
    }
  }

  /// PUT request
  Future<ApiResponse> put(
    String endpoint, {
    dynamic body,
    bool requiresAuth = true,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final headers = await _buildHeaders(requiresAuth: requiresAuth);

      final response = await http
          .put(
            uri,
            headers: headers,
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(_connectTimeout);

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse(
        success: false,
        statusCode: 0,
        errorMessage: 'Network error: $e',
      );
    }
  }

  /// DELETE request
  Future<ApiResponse> delete(
    String endpoint, {
    bool requiresAuth = true,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final headers = await _buildHeaders(requiresAuth: requiresAuth);

      final response = await http
          .delete(uri, headers: headers)
          .timeout(_connectTimeout);

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse(
        success: false,
        statusCode: 0,
        errorMessage: 'Network error: $e',
      );
    }
  }

  /// Upload file (multipart request)
  Future<ApiResponse> uploadFile(
    String endpoint, {
    required String filePath,
    required String fieldName,
    Map<String, dynamic>? additionalFields,
    bool requiresAuth = true,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final request = http.MultipartRequest('POST', uri);

      // Add authentication
      if (requiresAuth) {
        final token = await _getToken();
        if (token != null) {
          request.headers['Authorization'] = 'Bearer $token';
        }
      }

      // Add file
      request.files.add(await http.MultipartFile.fromPath(
        fieldName,
        filePath,
      ));

      // Add additional fields
      if (additionalFields != null) {
        additionalFields.forEach((key, value) {
          request.fields[key] = value.toString();
        });
      }

      final streamedResponse = await request.send().timeout(_connectTimeout);
      final response = await http.Response.fromStream(streamedResponse);

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse(
        success: false,
        statusCode: 0,
        errorMessage: 'Upload error: $e',
      );
    }
  }

  /// Download file
  Future<ApiResponse> downloadFile(
    String endpoint, {
    bool requiresAuth = true,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final headers = await _buildHeaders(requiresAuth: requiresAuth);

      final response = await http
          .get(uri, headers: headers)
          .timeout(_receiveTimeout);

      if (response.statusCode == 200) {
        return ApiResponse(
          success: true,
          statusCode: response.statusCode,
          data: response.bodyBytes, // Return raw bytes for file
        );
      }

      return _handleResponse(response);
    } catch (e) {
      return ApiResponse(
        success: false,
        statusCode: 0,
        errorMessage: 'Download error: $e',
      );
    }
  }
}

/// API Response model
class ApiResponse {
  final bool success;
  final int statusCode;
  final dynamic data;
  final String? errorMessage;

  ApiResponse({
    required this.success,
    required this.statusCode,
    this.data,
    this.errorMessage,
  });

  /// Check if response is successful
  bool get isSuccess => success && statusCode >= 200 && statusCode < 300;

  /// Check if response is unauthorized (401)
  bool get isUnauthorized => statusCode == 401;

  /// Check if response is forbidden (403)
  bool get isForbidden => statusCode == 403;

  /// Check if response is not found (404)
  bool get isNotFound => statusCode == 404;

  /// Check if response is server error (5xx)
  bool get isServerError => statusCode >= 500;

  /// Get error message
  String get error => errorMessage ?? 'Unknown error';

  @override
  String toString() {
    return 'ApiResponse(success: $success, statusCode: $statusCode, error: ${errorMessage ?? "none"})';
  }
}
