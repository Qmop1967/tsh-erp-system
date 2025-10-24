import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/device.dart';
import 'api_client.dart';

/// Device Management Service
class DeviceService {
  final ApiClient _apiClient = ApiClient();

  /// Get all devices
  Future<List<UserDevice>> getDevices({
    String? status,
    int? userId,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) {
        queryParams['status'] = status;
      }
      if (userId != null) {
        queryParams['user_id'] = userId;
      }

      final response = await _apiClient.dio.get(
        ApiConfig.devices,
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      // Handle both list and paginated response
      if (response.data is List) {
        return (response.data as List)
            .map((json) => UserDevice.fromJson(json as Map<String, dynamic>))
            .toList();
      } else if (response.data is Map<String, dynamic>) {
        final items = response.data['items'] as List? ?? [];
        return items
            .map((json) => UserDevice.fromJson(json as Map<String, dynamic>))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch devices',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Get device by ID
  Future<UserDevice> getDeviceById(String id) async {
    try {
      final response = await _apiClient.dio.get(ApiConfig.deviceById(id));
      return UserDevice.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to fetch device',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Update device status (approve, block, revoke)
  Future<UserDevice> updateDeviceStatus(String id, String status) async {
    try {
      final response = await _apiClient.dio.put(
        ApiConfig.deviceStatus(id),
        data: {'status': status},
      );
      return UserDevice.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to update device status',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }

  /// Delete/Revoke device
  Future<void> deleteDevice(String id) async {
    try {
      await _apiClient.dio.delete(ApiConfig.deviceById(id));
    } on DioException catch (e) {
      throw ApiException(
        message: e.error?.toString() ?? 'Failed to delete device',
        statusCode: e.response?.statusCode,
        data: e.response?.data,
      );
    }
  }
}
