import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:geolocator/geolocator.dart';

import '../models/mfa_request.dart';
import '../models/user_device.dart';
import '../models/user_session.dart';
import '../models/biometric_auth_result.dart';

class ApiService {
  static const String baseUrl = 'https://your-erp-domain.com/api/v1';
  static const FlutterSecureStorage _storage = FlutterSecureStorage();
  
  final http.Client _client;
  String? _accessToken;
  String? _deviceId;
  Map<String, dynamic>? _deviceInfo;

  ApiService({http.Client? client}) : _client = client ?? http.Client() {
    _initializeDevice();
  }

  // === INITIALIZATION ===

  Future<void> _initializeDevice() async {
    await _loadStoredTokens();
    await _collectDeviceInfo();
  }

  Future<void> _loadStoredTokens() async {
    _accessToken = await _storage.read(key: 'access_token');
    _deviceId = await _storage.read(key: 'device_id');
  }

  Future<void> _collectDeviceInfo() async {
    final deviceInfoPlugin = DeviceInfoPlugin();
    
    try {
      if (Platform.isAndroid) {
        final androidInfo = await deviceInfoPlugin.androidInfo;
        _deviceInfo = {
          'deviceType': 'mobile',
          'platform': 'android',
          'deviceName': '${androidInfo.brand} ${androidInfo.model}',
          'osVersion': 'Android ${androidInfo.version.release}',
          'deviceId': androidInfo.id,
          'manufacturer': androidInfo.manufacturer,
          'model': androidInfo.model,
          'fingerprint': androidInfo.fingerprint,
          'isPhysicalDevice': androidInfo.isPhysicalDevice,
        };
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfoPlugin.iosInfo;
        _deviceInfo = {
          'deviceType': 'mobile',
          'platform': 'ios',
          'deviceName': '${iosInfo.name}',
          'osVersion': 'iOS ${iosInfo.systemVersion}',
          'deviceId': iosInfo.identifierForVendor,
          'model': iosInfo.model,
          'systemName': iosInfo.systemName,
          'isPhysicalDevice': iosInfo.isPhysicalDevice,
        };
      }
    } catch (e) {
      print('Error collecting device info: $e');
      _deviceInfo = {
        'deviceType': 'mobile',
        'platform': Platform.operatingSystem,
        'deviceName': 'Unknown Device',
        'osVersion': 'Unknown',
      };
    }
  }

  // === HTTP HELPERS ===

  Future<Map<String, String>> _getHeaders({bool includeAuth = true}) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (includeAuth && _accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }

    if (_deviceId != null) {
      headers['X-Device-ID'] = _deviceId!;
    }

    // Add device fingerprinting
    if (_deviceInfo != null) {
      headers['X-Device-Info'] = base64Encode(utf8.encode(json.encode(_deviceInfo)));
    }

    // Add location if available
    try {
      final position = await _getCurrentLocation();
      if (position != null) {
        headers['X-Location'] = '${position.latitude},${position.longitude}';
      }
    } catch (e) {
      // Location not available or permission denied
    }

    return headers;
  }

  Future<Position?> _getCurrentLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) return null;

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) return null;
      }

      if (permission == LocationPermission.deniedForever) return null;

      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.medium,
        timeLimit: const Duration(seconds: 10),
      );
    } catch (e) {
      return null;
    }
  }

  Future<http.Response> _makeRequest(
    String method,
    String endpoint, {
    Map<String, dynamic>? body,
    bool includeAuth = true,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _getHeaders(includeAuth: includeAuth);

    http.Response response;
    
    try {
      switch (method.toUpperCase()) {
        case 'GET':
          response = await _client.get(uri, headers: headers);
          break;
        case 'POST':
          response = await _client.post(
            uri,
            headers: headers,
            body: body != null ? json.encode(body) : null,
          );
          break;
        case 'PUT':
          response = await _client.put(
            uri,
            headers: headers,
            body: body != null ? json.encode(body) : null,
          );
          break;
        case 'DELETE':
          response = await _client.delete(uri, headers: headers);
          break;
        default:
          throw ArgumentError('Unsupported HTTP method: $method');
      }

      // Handle token refresh
      if (response.statusCode == 401) {
        final refreshed = await _refreshToken();
        if (refreshed) {
          // Retry the request with new token
          headers['Authorization'] = 'Bearer $_accessToken';
          response = await _client.request(method, uri, headers: headers, body: body != null ? json.encode(body) : null);
        }
      }

      return response;
    } catch (e) {
      throw ApiException('Network error: $e');
    }
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: 'refresh_token');
      if (refreshToken == null) return false;

      final response = await _client.post(
        Uri.parse('$baseUrl/auth/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh_token': refreshToken}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _accessToken = data['access_token'];
        await _storage.write(key: 'access_token', value: _accessToken);
        
        if (data['refresh_token'] != null) {
          await _storage.write(key: 'refresh_token', value: data['refresh_token']);
        }
        
        return true;
      }
    } catch (e) {
      print('Token refresh failed: $e');
    }
    
    return false;
  }

  // === AUTHENTICATION ===

  Future<AuthResult> login(String email, String password) async {
    try {
      final response = await _makeRequest(
        'POST',
        '/auth/login',
        body: {
          'email': email,
          'password': password,
          'device_info': _deviceInfo,
        },
        includeAuth: false,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        _accessToken = data['access_token'];
        await _storage.write(key: 'access_token', value: _accessToken!);
        
        if (data['refresh_token'] != null) {
          await _storage.write(key: 'refresh_token', value: data['refresh_token']);
        }

        if (data['device_id'] != null) {
          _deviceId = data['device_id'];
          await _storage.write(key: 'device_id', value: _deviceId!);
        }

        return AuthResult(
          success: true,
          requiresMFA: data['requires_mfa'] ?? false,
          mfaChallengeId: data['mfa_challenge_id'],
          userInfo: data['user'],
        );
      } else {
        final error = json.decode(response.body);
        return AuthResult(
          success: false,
          error: error['message'] ?? 'Login failed',
        );
      }
    } catch (e) {
      return AuthResult(
        success: false,
        error: 'Login error: $e',
      );
    }
  }

  Future<AuthResult> verifyMFA(String challengeId, String code, {String? biometricData}) async {
    try {
      final response = await _makeRequest(
        'POST',
        '/auth/verify-mfa',
        body: {
          'challenge_id': challengeId,
          'verification_code': code,
          'biometric_data': biometricData,
          'device_info': _deviceInfo,
        },
        includeAuth: false,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        _accessToken = data['access_token'];
        await _storage.write(key: 'access_token', value: _accessToken!);
        
        return AuthResult(
          success: true,
          userInfo: data['user'],
        );
      } else {
        final error = json.decode(response.body);
        return AuthResult(
          success: false,
          error: error['message'] ?? 'MFA verification failed',
        );
      }
    } catch (e) {
      return AuthResult(
        success: false,
        error: 'MFA verification error: $e',
      );
    }
  }

  Future<void> logout() async {
    try {
      await _makeRequest('POST', '/auth/logout');
    } catch (e) {
      // Continue with logout even if API call fails
    } finally {
      _accessToken = null;
      await _storage.deleteAll();
    }
  }

  // === DEVICE REGISTRATION ===

  Future<DeviceRegistrationResult> registerDevice(String deviceName, String? biometricData, String? pushToken) async {
    try {
      final response = await _makeRequest(
        'POST',
        '/auth/register-device',
        body: {
          'device_name': deviceName,
          'device_info': _deviceInfo,
          'biometric_data': biometricData,
          'push_token': pushToken,
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        _deviceId = data['device_id'].toString();
        await _storage.write(key: 'device_id', value: _deviceId!);
        
        return DeviceRegistrationResult(
          success: true,
          deviceId: data['device_id'],
          registrationToken: data['registration_token'],
          qrCodeUrl: data['qr_code_url'],
          setupInstructions: List<String>.from(data['setup_instructions'] ?? []),
        );
      } else {
        final error = json.decode(response.body);
        return DeviceRegistrationResult(
          success: false,
          error: error['message'] ?? 'Device registration failed',
        );
      }
    } catch (e) {
      return DeviceRegistrationResult(
        success: false,
        error: 'Device registration error: $e',
      );
    }
  }

  // === MFA REQUESTS ===

  Future<List<MFARequest>> getMFARequests() async {
    try {
      final response = await _makeRequest('GET', '/mfa/requests');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> requestsJson = data['requests'] ?? [];
        
        return requestsJson.map((json) => MFARequest.fromJson(json)).toList();
      } else {
        throw ApiException('Failed to load MFA requests');
      }
    } catch (e) {
      throw ApiException('Error loading MFA requests: $e');
    }
  }

  Future<bool> approveMFARequest(String requestId, String? biometricData) async {
    try {
      final response = await _makeRequest(
        'POST',
        '/mfa/requests/$requestId/approve',
        body: {
          'biometric_data': biometricData,
          'device_info': _deviceInfo,
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error approving MFA request: $e');
    }
  }

  Future<bool> denyMFARequest(String requestId, {String? reason}) async {
    try {
      final response = await _makeRequest(
        'POST',
        '/mfa/requests/$requestId/deny',
        body: {
          'reason': reason,
          'device_info': _deviceInfo,
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error denying MFA request: $e');
    }
  }

  // === DEVICES ===

  Future<List<UserDevice>> getDevices() async {
    try {
      final response = await _makeRequest('GET', '/devices');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> devicesJson = data['devices'] ?? [];
        
        return devicesJson.map((json) => UserDevice.fromJson(json)).toList();
      } else {
        throw ApiException('Failed to load devices');
      }
    } catch (e) {
      throw ApiException('Error loading devices: $e');
    }
  }

  Future<bool> revokeDevice(int deviceId) async {
    try {
      final response = await _makeRequest('DELETE', '/devices/$deviceId');
      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error revoking device: $e');
    }
  }

  Future<bool> updateDeviceName(int deviceId, String newName) async {
    try {
      final response = await _makeRequest(
        'PUT',
        '/devices/$deviceId',
        body: {'device_name': newName},
      );
      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error updating device name: $e');
    }
  }

  // === SESSIONS ===

  Future<List<UserSession>> getSessions() async {
    try {
      final response = await _makeRequest('GET', '/sessions');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> sessionsJson = data['sessions'] ?? [];
        
        return sessionsJson.map((json) => UserSession.fromJson(json)).toList();
      } else {
        throw ApiException('Failed to load sessions');
      }
    } catch (e) {
      throw ApiException('Error loading sessions: $e');
    }
  }

  Future<bool> terminateSession(String sessionId) async {
    try {
      final response = await _makeRequest('DELETE', '/sessions/$sessionId');
      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error terminating session: $e');
    }
  }

  Future<bool> terminateAllSessions() async {
    try {
      final response = await _makeRequest('DELETE', '/sessions/all');
      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error terminating all sessions: $e');
    }
  }

  // === DASHBOARD ===

  Future<Map<String, dynamic>> getDashboardData() async {
    try {
      final response = await _makeRequest('GET', '/dashboard');
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw ApiException('Failed to load dashboard data');
      }
    } catch (e) {
      throw ApiException('Error loading dashboard data: $e');
    }
  }

  // === SECURITY ACTIONS ===

  Future<bool> emergencyLockdown() async {
    try {
      final response = await _makeRequest(
        'POST',
        '/security/emergency-lockdown',
        body: {
          'device_info': _deviceInfo,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error activating emergency lockdown: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getSecurityAlerts() async {
    try {
      final response = await _makeRequest('GET', '/security/alerts');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['alerts'] ?? []);
      } else {
        throw ApiException('Failed to load security alerts');
      }
    } catch (e) {
      throw ApiException('Error loading security alerts: $e');
    }
  }

  // === BIOMETRIC AUTHENTICATION ===

  Future<BiometricChallengeResult> requestBiometricChallenge() async {
    try {
      final response = await _makeRequest(
        'POST',
        '/auth/biometric-challenge',
        body: {
          'device_info': _deviceInfo,
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return BiometricChallengeResult(
          success: true,
          challengeId: data['challenge_id'],
          challengeData: data['challenge_data'],
          expiresAt: DateTime.parse(data['expires_at']),
        );
      } else {
        final error = json.decode(response.body);
        return BiometricChallengeResult(
          success: false,
          error: error['message'] ?? 'Failed to create biometric challenge',
        );
      }
    } catch (e) {
      return BiometricChallengeResult(
        success: false,
        error: 'Biometric challenge error: $e',
      );
    }
  }

  Future<BiometricVerificationResult> verifyBiometric(
    String challengeId,
    String biometricType,
    String biometricData,
  ) async {
    try {
      final response = await _makeRequest(
        'POST',
        '/auth/verify-biometric',
        body: {
          'challenge_id': challengeId,
          'biometric_type': biometricType,
          'biometric_data': biometricData,
          'device_info': _deviceInfo,
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return BiometricVerificationResult(
          success: true,
          confidenceScore: data['confidence_score']?.toDouble() ?? 0.0,
          sessionToken: data['session_token'],
        );
      } else {
        final error = json.decode(response.body);
        return BiometricVerificationResult(
          success: false,
          error: error['message'] ?? 'Biometric verification failed',
        );
      }
    } catch (e) {
      return BiometricVerificationResult(
        success: false,
        error: 'Biometric verification error: $e',
      );
    }
  }

  // === NOTIFICATIONS ===

  Future<bool> updatePushToken(String pushToken) async {
    try {
      final response = await _makeRequest(
        'PUT',
        '/notifications/push-token',
        body: {
          'push_token': pushToken,
          'device_info': _deviceInfo,
        },
      );
      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error updating push token: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getNotifications({int limit = 50}) async {
    try {
      final response = await _makeRequest('GET', '/notifications?limit=$limit');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['notifications'] ?? []);
      } else {
        throw ApiException('Failed to load notifications');
      }
    } catch (e) {
      throw ApiException('Error loading notifications: $e');
    }
  }

  Future<bool> markNotificationAsRead(String notificationId) async {
    try {
      final response = await _makeRequest(
        'PUT',
        '/notifications/$notificationId/read',
      );
      return response.statusCode == 200;
    } catch (e) {
      throw ApiException('Error marking notification as read: $e');
    }
  }

  // === REFRESH METHODS ===

  Future<void> refreshDashboard() async {
    // Trigger refresh by invalidating cache
    // This would depend on your state management implementation
  }

  Future<void> refreshDevices() async {
    // Trigger refresh by invalidating cache
  }

  Future<void> refreshSessions() async {
    // Trigger refresh by invalidating cache
  }

  Future<void> refreshMFARequests() async {
    // Trigger refresh by invalidating cache
  }

  // === CLEANUP ===

  void dispose() {
    _client.close();
  }
}

// === RESULT CLASSES ===

class AuthResult {
  final bool success;
  final String? error;
  final bool requiresMFA;
  final String? mfaChallengeId;
  final Map<String, dynamic>? userInfo;

  AuthResult({
    required this.success,
    this.error,
    this.requiresMFA = false,
    this.mfaChallengeId,
    this.userInfo,
  });
}

class DeviceRegistrationResult {
  final bool success;
  final String? error;
  final int? deviceId;
  final String? registrationToken;
  final String? qrCodeUrl;
  final List<String> setupInstructions;

  DeviceRegistrationResult({
    required this.success,
    this.error,
    this.deviceId,
    this.registrationToken,
    this.qrCodeUrl,
    this.setupInstructions = const [],
  });
}

class BiometricChallengeResult {
  final bool success;
  final String? error;
  final String? challengeId;
  final Map<String, dynamic>? challengeData;
  final DateTime? expiresAt;

  BiometricChallengeResult({
    required this.success,
    this.error,
    this.challengeId,
    this.challengeData,
    this.expiresAt,
  });
}

class BiometricVerificationResult {
  final bool success;
  final String? error;
  final double confidenceScore;
  final String? sessionToken;

  BiometricVerificationResult({
    required this.success,
    this.error,
    this.confidenceScore = 0.0,
    this.sessionToken,
  });
}

// === EXCEPTIONS ===

class ApiException implements Exception {
  final String message;
  
  ApiException(this.message);
  
  @override
  String toString() => 'ApiException: $message';
}

// === PROVIDER ===

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});
