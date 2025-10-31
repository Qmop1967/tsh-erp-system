import 'package:dio/dio.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'dart:io';
import '../config/api_config.dart';
import '../models/user.dart';
import 'api_client.dart';

/// Trusted Device Service for Automatic Login
class TrustedDeviceService {
  final ApiClient _apiClient = ApiClient();
  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();

  /// Get unique device ID
  Future<String> getDeviceId() async {
    try {
      if (Platform.isIOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        return iosInfo.identifierForVendor ?? 'unknown-ios';
      } else if (Platform.isAndroid) {
        final androidInfo = await _deviceInfo.androidInfo;
        return androidInfo.id;
      }
      return 'unknown-device';
    } catch (e) {
      return 'unknown-device';
    }
  }

  /// Get device name
  Future<String> getDeviceName() async {
    try {
      if (Platform.isIOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        return '${iosInfo.name} (${iosInfo.model})';
      } else if (Platform.isAndroid) {
        final androidInfo = await _deviceInfo.androidInfo;
        return '${androidInfo.brand} ${androidInfo.model}';
      }
      return 'Unknown Device';
    } catch (e) {
      return 'Unknown Device';
    }
  }

  /// Get device type
  String getDeviceType() {
    if (Platform.isIOS) {
      return 'ios';
    } else if (Platform.isAndroid) {
      return 'android';
    }
    return 'unknown';
  }

  /// Check if device is trusted
  Future<bool> isDeviceTrusted() async {
    try {
      final deviceId = await getDeviceId();

      final response = await _apiClient.dio.post(
        ApiConfig.trustedDevicesCheck,
        data: {'device_id': deviceId},
      );

      return response.data['can_auto_login'] ?? false;
    } catch (e) {
      print('Error checking device trust: $e');
      return false;
    }
  }

  /// Auto-login with trusted device
  Future<LoginResponse?> autoLogin() async {
    try {
      final deviceId = await getDeviceId();

      final response = await _apiClient.dio.post(
        ApiConfig.trustedDevicesAutoLogin,
        data: {'device_id': deviceId},
      );

      if (response.statusCode == 200) {
        final loginResponse = LoginResponse.fromJson(response.data);

        // Save token
        await _apiClient.saveToken(loginResponse.accessToken);

        return loginResponse;
      }

      return null;
    } on DioException catch (e) {
      print('Auto-login failed: ${e.message}');
      return null;
    }
  }

  /// Trust current device after login
  Future<bool> trustDevice({int trustDurationDays = 30}) async {
    try {
      final deviceId = await getDeviceId();
      final deviceName = await getDeviceName();
      final deviceType = getDeviceType();

      final response = await _apiClient.dio.post(
        ApiConfig.trustedDevicesTrust,
        data: {
          'device_id': deviceId,
          'device_name': deviceName,
          'device_type': deviceType,
          'trust_duration_days': trustDurationDays,
        },
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error trusting device: ${e.message}');
      return false;
    }
  }

  /// Revoke trust for current device
  Future<bool> revokeTrust() async {
    try {
      final deviceId = await getDeviceId();

      final response = await _apiClient.dio.delete(
        ApiConfig.trustedDevicesRevoke(deviceId),
      );

      return response.statusCode == 200;
    } on DioException catch (e) {
      print('Error revoking trust: ${e.message}');
      return false;
    }
  }

  /// Get list of all trusted devices
  Future<List<TrustedDeviceModel>> getTrustedDevices() async {
    try {
      final response = await _apiClient.dio.get(
        ApiConfig.trustedDevicesList,
      );

      if (response.statusCode == 200 && response.data is List) {
        return (response.data as List)
            .map((device) => TrustedDeviceModel.fromJson(device))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      print('Error getting trusted devices: ${e.message}');
      return [];
    }
  }
}

/// Trusted Device Model
class TrustedDeviceModel {
  final int id;
  final String deviceId;
  final String deviceName;
  final String deviceType;
  final bool isTrusted;
  final DateTime? trustExpiresAt;
  final DateTime firstSeenAt;
  final DateTime lastSeenAt;

  TrustedDeviceModel({
    required this.id,
    required this.deviceId,
    required this.deviceName,
    required this.deviceType,
    required this.isTrusted,
    this.trustExpiresAt,
    required this.firstSeenAt,
    required this.lastSeenAt,
  });

  factory TrustedDeviceModel.fromJson(Map<String, dynamic> json) {
    return TrustedDeviceModel(
      id: json['id'],
      deviceId: json['device_id'],
      deviceName: json['device_name'],
      deviceType: json['device_type'],
      isTrusted: json['is_trusted'] ?? false,
      trustExpiresAt: json['trust_expires_at'] != null
          ? DateTime.parse(json['trust_expires_at'])
          : null,
      firstSeenAt: DateTime.parse(json['first_seen_at']),
      lastSeenAt: DateTime.parse(json['last_seen_at']),
    );
  }
}
