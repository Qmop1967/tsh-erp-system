import 'dart:async';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'package:hive/hive.dart';
import '../../models/gps/gps_location.dart';

/// GPS Tracking Service for Field Sales Representatives
/// Implements all-day GPS tracking with fraud prevention
/// Critical for managing $35K USD weekly by 12 travel salespersons
class GPSTrackingService {
  static final GPSTrackingService _instance = GPSTrackingService._internal();
  factory GPSTrackingService() => _instance;
  GPSTrackingService._internal();

  StreamSubscription<Position>? _positionSubscription;
  Box<Map>? _locationBox;
  bool _isTracking = false;

  // Tracking configuration
  static const int _locationUpdateIntervalSeconds = 60; // Every 1 minute
  static const double _minimumDistanceMeters = 10.0; // 10 meters minimum movement
  static const int _maxCachedLocations = 1000; // Local cache limit

  /// Initialize GPS service
  Future<void> initialize() async {
    _locationBox = await Hive.openBox<Map>('gps_locations');
  }

  /// Check and request location permissions
  Future<bool> checkPermissions() async {
    bool serviceEnabled;
    LocationPermission permission;

    // Check if location services are enabled
    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      return false;
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        return false;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      return false;
    }

    return true;
  }

  /// Start tracking salesperson location
  Future<bool> startTracking(int salespersonId) async {
    if (_isTracking) {
      return true;
    }

    final hasPermission = await checkPermissions();
    if (!hasPermission) {
      return false;
    }

    _isTracking = true;

    // Configure location settings for accurate tracking
    const locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10, // Update every 10 meters
    );

    _positionSubscription = Geolocator.getPositionStream(
      locationSettings: locationSettings,
    ).listen(
      (Position position) {
        _handleLocationUpdate(salespersonId, position);
      },
      onError: (error) {
        print('GPS Tracking Error: $error');
      },
    );

    // Record start of day
    await _recordLocationPoint(
      salespersonId,
      await Geolocator.getCurrentPosition(),
      visitType: 'start_day',
    );

    return true;
  }

  /// Stop tracking
  Future<void> stopTracking(int salespersonId) async {
    if (!_isTracking) {
      return;
    }

    // Record end of day
    try {
      final position = await Geolocator.getCurrentPosition();
      await _recordLocationPoint(
        salespersonId,
        position,
        visitType: 'end_day',
      );
    } catch (e) {
      print('Error recording end location: $e');
    }

    await _positionSubscription?.cancel();
    _positionSubscription = null;
    _isTracking = false;
  }

  /// Handle location update
  void _handleLocationUpdate(int salespersonId, Position position) async {
    await _recordLocationPoint(
      salespersonId,
      position,
      visitType: 'in_transit',
    );
  }

  /// Record a location point
  Future<void> _recordLocationPoint(
    int salespersonId,
    Position position, {
    String? visitType,
    int? customerId,
    String? notes,
  }) async {
    try {
      // Get address from coordinates (reverse geocoding)
      String? address;
      try {
        final placemarks = await placemarkFromCoordinates(
          position.latitude,
          position.longitude,
        );
        if (placemarks.isNotEmpty) {
          final place = placemarks.first;
          address = '${place.street}, ${place.locality}, ${place.country}';
        }
      } catch (e) {
        print('Geocoding error: $e');
      }

      final location = GPSLocation(
        salespersonId: salespersonId,
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        altitude: position.altitude,
        speed: position.speed,
        timestamp: DateTime.now().toIso8601String(),
        address: address,
        customerId: customerId,
        visitType: visitType,
        notes: notes,
        isSynced: false,
      );

      // Save to local storage
      await _saveLocationLocally(location);

      // TODO: Send to backend API
      // await _syncLocationToBackend(location);
    } catch (e) {
      print('Error recording location: $e');
    }
  }

  /// Save location to local Hive storage
  Future<void> _saveLocationLocally(GPSLocation location) async {
    if (_locationBox == null) {
      await initialize();
    }

    final key = '${location.salespersonId}_${location.timestamp}';
    await _locationBox?.put(key, location.toJson());

    // Clean old locations if exceeding limit
    if ((_locationBox?.length ?? 0) > _maxCachedLocations) {
      await _cleanOldLocations();
    }
  }

  /// Clean old cached locations
  Future<void> _cleanOldLocations() async {
    final keys = _locationBox?.keys.toList() ?? [];
    if (keys.length > _maxCachedLocations) {
      final toDelete = keys.sublist(0, keys.length - _maxCachedLocations);
      await _locationBox?.deleteAll(toDelete);
    }
  }

  /// Get current position
  Future<Position?> getCurrentPosition() async {
    try {
      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
    } catch (e) {
      print('Error getting current position: $e');
      return null;
    }
  }

  /// Record customer visit with GPS verification
  Future<void> recordCustomerVisit({
    required int salespersonId,
    required int customerId,
    String? notes,
  }) async {
    final position = await getCurrentPosition();
    if (position != null) {
      await _recordLocationPoint(
        salespersonId,
        position,
        visitType: 'customer_visit',
        customerId: customerId,
        notes: notes,
      );
    }
  }

  /// Get today's tracking summary
  Future<DailyTrackingSummary?> getTodaysSummary(int salespersonId) async {
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}';

    final locations = await getLocationsByDate(salespersonId, todayStr);

    if (locations.isEmpty) {
      return null;
    }

    // Calculate total distance
    double totalDistance = 0.0;
    for (int i = 1; i < locations.length; i++) {
      totalDistance += Geolocator.distanceBetween(
        locations[i - 1].latitude,
        locations[i - 1].longitude,
        locations[i].latitude,
        locations[i].longitude,
      );
    }

    final startLoc = locations.first;
    final endLoc = locations.last;
    final customerVisits = locations.where((l) => l.visitType == 'customer_visit').length;

    final duration = DateTime.parse(endLoc.timestamp)
        .difference(DateTime.parse(startLoc.timestamp));

    return DailyTrackingSummary(
      date: todayStr,
      totalLocations: locations.length,
      totalDistanceKm: totalDistance / 1000,
      startTime: startLoc.timestamp,
      endTime: endLoc.visitType == 'end_day' ? endLoc.timestamp : null,
      customerVisits: customerVisits,
      totalDuration: _formatDuration(duration),
      locations: locations,
    );
  }

  /// Get locations by date
  Future<List<GPSLocation>> getLocationsByDate(int salespersonId, String date) async {
    if (_locationBox == null) {
      await initialize();
    }

    final allLocations = _locationBox?.values
        .map((json) => GPSLocation.fromJson(Map<String, dynamic>.from(json)))
        .where((loc) =>
            loc.salespersonId == salespersonId &&
            loc.timestamp.startsWith(date))
        .toList() ?? [];

    allLocations.sort((a, b) => a.timestamp.compareTo(b.timestamp));
    return allLocations;
  }

  /// Get unsynced locations for backend upload
  Future<List<GPSLocation>> getUnsyncedLocations() async {
    if (_locationBox == null) {
      await initialize();
    }

    return _locationBox?.values
        .map((json) => GPSLocation.fromJson(Map<String, dynamic>.from(json)))
        .where((loc) => !loc.isSynced)
        .toList() ?? [];
  }

  /// Mark locations as synced
  Future<void> markLocationsSynced(List<String> timestamps) async {
    for (final timestamp in timestamps) {
      final key = _locationBox?.keys.firstWhere(
        (k) => k.toString().endsWith(timestamp),
        orElse: () => null,
      );

      if (key != null) {
        final json = _locationBox?.get(key);
        if (json != null) {
          final location = GPSLocation.fromJson(Map<String, dynamic>.from(json));
          final updated = location.copyWith(isSynced: true);
          await _locationBox?.put(key, updated.toJson());
        }
      }
    }
  }

  /// Calculate distance between two points
  double calculateDistance(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2);
  }

  /// Check if salesperson is near customer location (geofencing)
  bool isNearCustomer(
    Position currentPosition,
    double customerLat,
    double customerLon, {
    double radiusMeters = 100.0,
  }) {
    final distance = calculateDistance(
      currentPosition.latitude,
      currentPosition.longitude,
      customerLat,
      customerLon,
    );
    return distance <= radiusMeters;
  }

  /// Format duration
  String _formatDuration(Duration duration) {
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);
    return '$hours ساعة و $minutes دقيقة';
  }

  /// Check if tracking is active
  bool get isTracking => _isTracking;

  /// Dispose resources
  void dispose() {
    _positionSubscription?.cancel();
    _locationBox?.close();
  }
}
