import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'package:logger/logger.dart';
import '../../../core/constants/app_constants.dart';
import '../data/models/location_data.dart';

class GPSService {
  final Logger _logger = Logger();
  Position? _lastKnownPosition;

  // Check if location services are enabled
  Future<bool> isLocationServiceEnabled() async {
    return await Geolocator.isLocationServiceEnabled();
  }

  // Check location permissions
  Future<LocationPermission> checkPermission() async {
    return await Geolocator.checkPermission();
  }

  // Request location permissions
  Future<LocationPermission> requestPermission() async {
    return await Geolocator.requestPermission();
  }

  // Ensure permissions are granted
  Future<bool> ensurePermissions() async {
    // Check if location service is enabled
    bool serviceEnabled = await isLocationServiceEnabled();
    if (!serviceEnabled) {
      _logger.w('Location services are disabled');
      return false;
    }

    // Check permission status
    LocationPermission permission = await checkPermission();

    if (permission == LocationPermission.denied) {
      permission = await requestPermission();
      if (permission == LocationPermission.denied) {
        _logger.w('Location permissions are denied');
        return false;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      _logger.e('Location permissions are permanently denied');
      return false;
    }

    _logger.i('Location permissions granted');
    return true;
  }

  // Get current location
  Future<LocationDataModel?> getCurrentLocation() async {
    try {
      // Ensure permissions
      bool hasPermissions = await ensurePermissions();
      if (!hasPermissions) {
        _logger.e('Cannot get location: permissions not granted');
        return null;
      }

      // Get current position
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );

      _lastKnownPosition = position;

      // Get address from coordinates
      String? address = await _getAddressFromCoordinates(
        position.latitude,
        position.longitude,
      );

      return LocationDataModel(
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        address: address,
        timestamp: DateTime.now(),
      );
    } catch (e) {
      _logger.e('Error getting current location: $e');
      return null;
    }
  }

  // Get last known location
  Future<LocationDataModel?> getLastKnownLocation() async {
    try {
      Position? position = await Geolocator.getLastKnownPosition();

      if (position == null) {
        _logger.w('No last known position available');
        return null;
      }

      String? address = await _getAddressFromCoordinates(
        position.latitude,
        position.longitude,
      );

      return LocationDataModel(
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        address: address,
        timestamp: DateTime.now(),
      );
    } catch (e) {
      _logger.e('Error getting last known location: $e');
      return null;
    }
  }

  // Stream location updates
  Stream<LocationDataModel> getLocationStream() {
    const LocationSettings locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10, // Update every 10 meters
    );

    return Geolocator.getPositionStream(locationSettings: locationSettings)
        .asyncMap((position) async {
      _lastKnownPosition = position;

      String? address = await _getAddressFromCoordinates(
        position.latitude,
        position.longitude,
      );

      return LocationDataModel(
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        address: address,
        timestamp: DateTime.now(),
      );
    });
  }

  // Calculate distance between two points (in meters)
  double calculateDistance(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2);
  }

  // Check if location is within geofence radius
  bool isWithinGeofence(
    double currentLat,
    double currentLon,
    double targetLat,
    double targetLon, {
    double radius = AppConstants.visitGeofenceRadius,
  }) {
    double distance = calculateDistance(
      currentLat,
      currentLon,
      targetLat,
      targetLon,
    );
    return distance <= radius;
  }

  // Check if GPS accuracy is acceptable
  bool isAccuracyAcceptable(double? accuracy) {
    if (accuracy == null) return false;
    return accuracy <= AppConstants.gpsAccuracyThreshold;
  }

  // Verify location for money transfer (fraud prevention)
  Future<LocationVerificationResult> verifyLocationForTransfer() async {
    final location = await getCurrentLocation();

    if (location == null) {
      return LocationVerificationResult(
        isValid: false,
        message: 'فشل الحصول على الموقع الحالي',
        messageEn: 'Failed to get current location',
      );
    }

    // Check accuracy
    if (!isAccuracyAcceptable(location.accuracy)) {
      return LocationVerificationResult(
        isValid: false,
        location: location,
        message: 'دقة GPS منخفضة جداً (${location.accuracy?.toStringAsFixed(0)}م)',
        messageEn: 'GPS accuracy too low (${location.accuracy?.toStringAsFixed(0)}m)',
      );
    }

    // Check if location is suspicious (optional - can add logic here)
    bool isSuspicious = await _isSuspiciousLocation(location);
    if (isSuspicious) {
      return LocationVerificationResult(
        isValid: false,
        location: location,
        message: 'موقع مشبوه - يتطلب التحقق اليدوي',
        messageEn: 'Suspicious location - requires manual verification',
        isSuspicious: true,
      );
    }

    return LocationVerificationResult(
      isValid: true,
      location: location,
      message: 'تم التحقق من الموقع بنجاح',
      messageEn: 'Location verified successfully',
    );
  }

  // Get address from coordinates using geocoding
  Future<String?> _getAddressFromCoordinates(
    double latitude,
    double longitude,
  ) async {
    try {
      List<Placemark> placemarks = await placemarkFromCoordinates(
        latitude,
        longitude,
      );

      if (placemarks.isEmpty) return null;

      Placemark place = placemarks[0];
      return '${place.street}, ${place.locality}, ${place.country}';
    } catch (e) {
      _logger.w('Error getting address from coordinates: $e');
      return null;
    }
  }

  // Check if location is suspicious (can implement custom logic)
  Future<bool> _isSuspiciousLocation(LocationDataModel location) async {
    // TODO: Implement suspicious location detection logic
    // For example:
    // - Check if location is outside Iraq
    // - Check if location matches known fraud patterns
    // - Check if location is in restricted area
    return false;
  }

  // Open device location settings
  Future<void> openLocationSettings() async {
    await Geolocator.openLocationSettings();
  }

  // Open app settings
  Future<void> openAppSettings() async {
    await Geolocator.openAppSettings();
  }
}

// Location Verification Result
class LocationVerificationResult {
  final bool isValid;
  final LocationDataModel? location;
  final String message;
  final String messageEn;
  final bool isSuspicious;

  LocationVerificationResult({
    required this.isValid,
    this.location,
    required this.message,
    required this.messageEn,
    this.isSuspicious = false,
  });
}
