import '../../models/gps/gps_location.dart';
import 'api_client.dart';

/// GPS Tracking API Service
/// Handles all GPS-related backend communication
class GpsApiService {
  final ApiClient _apiClient = ApiClient();

  /// BFF endpoint prefix for salesperson GPS operations
  static const String _bffPrefix = '/bff/salesperson/gps';

  /// Upload GPS location to backend
  /// Endpoint: POST /api/bff/salesperson/gps/track
  Future<bool> uploadLocation(GPSLocation location) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/track',
        body: location.toJson(),
      );

      return response.isSuccess;
    } catch (e) {
      print('Error uploading GPS location: $e');
      return false;
    }
  }

  /// Batch upload multiple GPS locations
  /// Endpoint: POST /api/bff/salesperson/gps/track/batch
  /// Used for syncing offline data
  Future<Map<String, dynamic>> batchUploadLocations(
    List<GPSLocation> locations,
  ) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/track/batch',
        body: {
          'locations': locations.map((loc) => loc.toJson()).toList(),
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'uploaded': response.data['uploaded'] ?? 0,
          'failed': response.data['failed'] ?? 0,
          'errors': response.data['errors'] ?? [],
        };
      }

      return {
        'success': false,
        'uploaded': 0,
        'failed': locations.length,
        'error': response.error,
      };
    } catch (e) {
      print('Error batch uploading GPS locations: $e');
      return {
        'success': false,
        'uploaded': 0,
        'failed': locations.length,
        'error': e.toString(),
      };
    }
  }

  /// Get GPS location history from backend
  /// Endpoint: GET /api/bff/salesperson/gps/history
  Future<List<GPSLocation>> getLocationHistory({
    required int salespersonId,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'salesperson_id': salespersonId,
      };

      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String();
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String();
      }
      if (limit != null) {
        queryParams['limit'] = limit;
      }

      final response = await _apiClient.get(
        '$_bffPrefix/history',
        queryParameters: queryParams,
      );

      if (response.isSuccess && response.data != null) {
        final List<dynamic> locationsJson = response.data['locations'] ?? [];
        return locationsJson
            .map((json) => GPSLocation.fromJson(json))
            .toList();
      }

      return [];
    } catch (e) {
      print('Error getting GPS history: $e');
      return [];
    }
  }

  /// Get daily GPS summary
  /// Endpoint: GET /api/bff/salesperson/gps/summary/daily
  Future<Map<String, dynamic>?> getDailySummary({
    required int salespersonId,
    required DateTime date,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/summary/daily',
        queryParameters: {
          'salesperson_id': salespersonId,
          'date': date.toIso8601String().split('T')[0], // YYYY-MM-DD
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'totalDistance': response.data['total_distance'] ?? 0.0,
          'totalDuration': response.data['total_duration'] ?? 0,
          'customerVisits': response.data['customer_visits'] ?? 0,
          'startTime': response.data['start_time'],
          'endTime': response.data['end_time'],
          'route': response.data['route'] ?? [],
        };
      }

      return null;
    } catch (e) {
      print('Error getting daily summary: $e');
      return null;
    }
  }

  /// Get weekly GPS summary
  /// Endpoint: GET /api/bff/salesperson/gps/summary/weekly
  Future<Map<String, dynamic>?> getWeeklySummary({
    required int salespersonId,
    required DateTime weekStart,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/summary/weekly',
        queryParameters: {
          'salesperson_id': salespersonId,
          'week_start': weekStart.toIso8601String().split('T')[0],
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'totalDistance': response.data['total_distance'] ?? 0.0,
          'totalDuration': response.data['total_duration'] ?? 0,
          'totalVisits': response.data['total_visits'] ?? 0,
          'dailyBreakdown': response.data['daily_breakdown'] ?? [],
          'mostVisitedAreas': response.data['most_visited_areas'] ?? [],
        };
      }

      return null;
    } catch (e) {
      print('Error getting weekly summary: $e');
      return null;
    }
  }

  /// Verify customer visit location
  /// Endpoint: POST /api/bff/salesperson/gps/verify-visit
  Future<Map<String, dynamic>> verifyCustomerVisit({
    required int customerId,
    required double latitude,
    required double longitude,
    required DateTime visitTime,
  }) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/verify-visit',
        body: {
          'customer_id': customerId,
          'latitude': latitude,
          'longitude': longitude,
          'visit_time': visitTime.toIso8601String(),
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'verified': response.data['verified'] ?? false,
          'distance_from_customer': response.data['distance_from_customer'],
          'customer_name': response.data['customer_name'],
          'customer_address': response.data['customer_address'],
          'within_geofence': response.data['within_geofence'] ?? false,
        };
      }

      return {
        'verified': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error verifying customer visit: $e');
      return {
        'verified': false,
        'error': e.toString(),
      };
    }
  }

  /// Get sync status
  /// Endpoint: GET /api/bff/salesperson/gps/sync-status
  Future<Map<String, dynamic>?> getSyncStatus({
    required int salespersonId,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/sync-status',
        queryParameters: {
          'salesperson_id': salespersonId,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'lastSyncTime': response.data['last_sync_time'],
          'pendingCount': response.data['pending_count'] ?? 0,
          'syncedCount': response.data['synced_count'] ?? 0,
          'failedCount': response.data['failed_count'] ?? 0,
        };
      }

      return null;
    } catch (e) {
      print('Error getting sync status: $e');
      return null;
    }
  }

  /// Delete location records (admin only)
  /// Endpoint: DELETE /api/bff/salesperson/gps/locations/{locationId}
  Future<bool> deleteLocation(int locationId) async {
    try {
      final response = await _apiClient.delete(
        '$_bffPrefix/locations/$locationId',
      );

      return response.isSuccess;
    } catch (e) {
      print('Error deleting GPS location: $e');
      return false;
    }
  }

  /// Test GPS tracking system
  /// Endpoint: POST /api/bff/salesperson/gps/test
  Future<bool> testGpsTracking({
    required int salespersonId,
  }) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/test',
        body: {
          'salesperson_id': salespersonId,
        },
      );

      return response.isSuccess;
    } catch (e) {
      print('Error testing GPS tracking: $e');
      return false;
    }
  }
}
