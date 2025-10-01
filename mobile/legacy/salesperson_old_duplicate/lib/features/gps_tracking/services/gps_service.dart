import 'dart:async';
import 'dart:io';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/location_data.dart';
import 'package:flutter/material.dart';

class GPSService {
  static GPSService? _instance;
  static GPSService get instance => _instance ??= GPSService._internal();
  
  GPSService._internal();

  StreamController<LocationData>? _locationController;
  StreamSubscription<Position>? _positionSubscription;
  Position? _lastKnownPosition;
  bool _isTracking = false;

  // Stream for real-time location updates
  Stream<LocationData> get locationStream => _locationController!.stream;

  // ==============================================
  // 🚨 CRITICAL: FRAUD PREVENTION GPS TRACKING
  // ==============================================

  /// Initialize GPS service and request permissions
  Future<bool> initialize() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw GPSException('Location services are disabled. Please enable location services for fraud prevention.', 'SERVICE_DISABLED');
      }

      // Request location permission
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw GPSException('Location permission denied. This is required for fraud prevention.', 'PERMISSION_DENIED');
        }
      }

      if (permission == LocationPermission.deniedForever) {
        throw GPSException('Location permission permanently denied. Please enable in settings for fraud prevention.', 'PERMISSION_DENIED_FOREVER');
      }

      // Get current position to verify GPS is working
      await getCurrentLocation();
      
      print('🎯 GPS Service initialized successfully for fraud prevention');
      return true;
    } catch (e) {
      print('❌ GPS Service initialization failed: $e');
      return false;
    }
  }

  /// Get current location immediately (CRITICAL for money transfers)
  Future<LocationData> getCurrentLocation() async {
    try {
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 15),
      );

      _lastKnownPosition = position;

      // Get address from coordinates
      String? address = await _getAddressFromCoordinates(
        position.latitude, 
        position.longitude
      );

      LocationData locationData = LocationData(
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        address: address,
        timestamp: DateTime.now(),
        speed: position.speed,
        heading: position.heading,
      );

      // Save location for offline use
      await _saveLocationOffline(locationData);

      print('📍 Current location captured: ${position.latitude}, ${position.longitude}');
      return locationData;
    } catch (e) {
      // Try to return last known location if available
      if (_lastKnownPosition != null) {
        print('⚠️ Using last known location due to error: $e');
        return LocationData(
          latitude: _lastKnownPosition!.latitude,
          longitude: _lastKnownPosition!.longitude,
          accuracy: _lastKnownPosition!.accuracy,
          address: 'Last known location',
          timestamp: DateTime.now(),
          speed: _lastKnownPosition!.speed,
          heading: _lastKnownPosition!.heading,
          isLastKnown: true,
        );
      }
      
      throw GPSException('Unable to get current location: $e', 'LOCATION_ERROR');
    }
  }

  /// Start continuous location tracking (for route monitoring)
  Future<void> startLocationTracking() async {
    if (_isTracking) return;

    _locationController = StreamController<LocationData>.broadcast();
    
    // Use platform-specific settings for geolocator 12.0.0
    late LocationSettings locationSettings;
    if (Platform.isAndroid) {
      locationSettings = AndroidSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
        forceLocationManager: true,
      );
    } else if (Platform.isIOS) {
      locationSettings = AppleSettings(
        accuracy: LocationAccuracy.high,
        activityType: ActivityType.other,
        distanceFilter: 10,
        pauseLocationUpdatesAutomatically: true,
      );
    } else {
      locationSettings = const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      );
    }

    _positionSubscription = Geolocator.getPositionStream(
      locationSettings: locationSettings,
    ).listen(
      (Position position) async {
        String? address = await _getAddressFromCoordinates(
          position.latitude, 
          position.longitude
        );

        LocationData locationData = LocationData(
          latitude: position.latitude,
          longitude: position.longitude,
          accuracy: position.accuracy,
          address: address,
          timestamp: DateTime.now(),
          speed: position.speed,
          heading: position.heading,
        );

        _lastKnownPosition = position;
        await _saveLocationOffline(locationData);
        
        _locationController?.add(locationData);
        print('📍 Location updated: ${position.latitude}, ${position.longitude}');
      },
      onError: (error) {
        print('❌ Location tracking error: $error');
        _locationController?.addError(GPSException('Location tracking error: $error', 'TRACKING_ERROR'));
      },
    );

    _isTracking = true;
    print('🚀 GPS tracking started for fraud prevention');
  }

  /// Stop location tracking
  Future<void> stopLocationTracking() async {
    await _positionSubscription?.cancel();
    await _locationController?.close();
    _positionSubscription = null;
    _locationController = null;
    _isTracking = false;
    print('🛑 GPS tracking stopped');
  }

  /// Verify location for money transfer (CRITICAL FRAUD PREVENTION)
  Future<LocationVerification> verifyLocationForTransfer(LocationData location) async {
    try {
      // Check if location is accurate enough
      if (location.accuracy > 50) {
        return LocationVerification(
          isValid: false,
          reason: 'Location accuracy too low for transfer verification',
          reasonArabic: 'دقة الموقع منخفضة جداً للتحقق من التحويل',
          riskLevel: 0.8,
        );
      }

      // Check if location is in a reasonable area (not in the middle of nowhere)
      if (location.address == null || location.address!.isEmpty) {
        return LocationVerification(
          isValid: false,
          reason: 'Unable to verify location address',
          reasonArabic: 'غير قادر على التحقق من عنوان الموقع',
          riskLevel: 0.7,
        );
      }

      // Check for suspicious locations (hardcoded for now, should be configurable)
      List<String> suspiciousKeywords = [
        'desert', 'unknown', 'unnamed', 'water', 'sea', 'ocean',
        'صحراء', 'مجهول', 'بحر', 'محيط'
      ];

      for (String keyword in suspiciousKeywords) {
        if (location.address!.toLowerCase().contains(keyword.toLowerCase())) {
          return LocationVerification(
            isValid: false,
            reason: 'Suspicious location detected: ${location.address}',
            reasonArabic: 'تم اكتشاف موقع مشبوه: ${location.address}',
            riskLevel: 0.9,
          );
        }
      }

      // Location is valid
      return LocationVerification(
        isValid: true,
        reason: 'Location verified successfully',
        reasonArabic: 'تم التحقق من الموقع بنجاح',
        riskLevel: 0.1,
      );
    } catch (e) {
      return LocationVerification(
        isValid: false,
        reason: 'Location verification failed: $e',
        reasonArabic: 'فشل التحقق من الموقع: $e',
        riskLevel: 1.0,
      );
    }
  }

  /// Get distance between two points (for route verification)
  double getDistanceBetween(double lat1, double lon1, double lat2, double lon2) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2);
  }

  /// Check if device location settings are optimal
  Future<LocationSettingsCheck> checkLocationSettings() async {
    bool isLocationServiceEnabled = await Geolocator.isLocationServiceEnabled();
    LocationPermission permission = await Geolocator.checkPermission();
    
    return LocationSettingsCheck(
      isLocationServiceEnabled: isLocationServiceEnabled,
      permission: permission,
      isOptimal: isLocationServiceEnabled && 
                 (permission == LocationPermission.always || 
                  permission == LocationPermission.whileInUse),
    );
  }

  /// Get offline cached location (fallback)
  Future<LocationData?> getOfflineLocation() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final String? locationJson = prefs.getString('last_location');
      
      if (locationJson != null) {
        return LocationData.fromJson(locationJson);
      }
      return null;
    } catch (e) {
      print('❌ Error getting offline location: $e');
      return null;
    }
  }

  // ==============================================
  // 🔒 PRIVATE HELPER METHODS
  // ==============================================

  /// Get address from GPS coordinates
  Future<String?> _getAddressFromCoordinates(double latitude, double longitude) async {
    try {
      List<Placemark> placemarks = await placemarkFromCoordinates(latitude, longitude);
      
      if (placemarks.isNotEmpty) {
        Placemark place = placemarks[0];
        return '${place.street ?? ''}, ${place.locality ?? ''}, ${place.administrativeArea ?? ''}, ${place.country ?? ''}'
            .replaceAll(RegExp(r'^[,\s]+|[,\s]+$'), '') // Remove leading/trailing commas and spaces
            .replaceAll(RegExp(r'[,\s]{2,}'), ', '); // Replace multiple commas/spaces with single comma
      }
      return null;
    } catch (e) {
      print('❌ Error getting address: $e');
      return 'Address lookup failed';
    }
  }

  /// Save location data for offline use
  Future<void> _saveLocationOffline(LocationData location) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('last_location', location.toJson());
      await prefs.setString('last_location_time', DateTime.now().toIso8601String());
    } catch (e) {
      print('❌ Error saving location offline: $e');
    }
  }

  /// Cleanup resources
  void dispose() {
    stopLocationTracking();
    _instance = null;
  }
}

// GPS Exception class
class GPSException implements Exception {
  final String message;
  final String code;

  GPSException(this.message, this.code);

  @override
  String toString() => 'GPSException: $message (Code: $code)';
}

// Location Verification Result
class LocationVerification {
  final bool isValid;
  final String reason;
  final String reasonArabic;
  final double riskLevel; // 0.0 (safe) to 1.0 (high risk)

  LocationVerification({
    required this.isValid,
    required this.reason,
    required this.reasonArabic,
    required this.riskLevel,
  });
}

// Location Settings Check Result (renamed to avoid conflict with geolocator LocationSettings)
class LocationSettingsCheck {
  final bool isLocationServiceEnabled;
  final LocationPermission permission;
  final bool isOptimal;

  LocationSettingsCheck({
    required this.isLocationServiceEnabled,
    required this.permission,
    required this.isOptimal,
  });

  String get statusMessage {
    if (isOptimal) return 'Location settings are optimal for fraud prevention';
    if (!isLocationServiceEnabled) return 'Location services are disabled';
    return 'Location permission not granted';
  }

  String get statusMessageArabic {
    if (isOptimal) return 'إعدادات الموقع مثلى لمنع الاحتيال';
    if (!isLocationServiceEnabled) return 'خدمات الموقع معطلة';
    return 'لم يتم منح إذن الموقع';
  }
} 