import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

class ConnectivityService extends ChangeNotifier {
  final Connectivity _connectivity = Connectivity();
  late StreamSubscription<List<ConnectivityResult>> _connectivitySubscription;
  
  List<ConnectivityResult> _connectionStatus = [ConnectivityResult.none];
  bool _isInitialized = false;

  // Getters
  List<ConnectivityResult> get connectionStatus => _connectionStatus;
  bool get isConnected => !_connectionStatus.contains(ConnectivityResult.none);
  bool get isWifiConnected => _connectionStatus.contains(ConnectivityResult.wifi);
  bool get isMobileConnected => _connectionStatus.contains(ConnectivityResult.mobile);
  bool get isInitialized => _isInitialized;

  // Connection type getters
  String get connectionType {
    if (_connectionStatus.contains(ConnectivityResult.wifi)) {
      return 'WiFi';
    } else if (_connectionStatus.contains(ConnectivityResult.mobile)) {
      return 'Mobile Data';
    } else if (_connectionStatus.contains(ConnectivityResult.ethernet)) {
      return 'Ethernet';
    } else if (_connectionStatus.contains(ConnectivityResult.vpn)) {
      return 'VPN';
    } else if (_connectionStatus.contains(ConnectivityResult.bluetooth)) {
      return 'Bluetooth';
    } else {
      return 'No Connection';
    }
  }

  // Initialize the service
  Future<void> initialize() async {
    try {
      // Get initial connectivity status
      _connectionStatus = await _connectivity.checkConnectivity();
      _isInitialized = true;
      notifyListeners();

      // Listen for connectivity changes
      _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
        _updateConnectionStatus,
        onError: (error) {
          debugPrint('Connectivity error: $error');
        },
      );
    } catch (e) {
      debugPrint('Error initializing connectivity service: $e');
      _isInitialized = false;
    }
  }

  // Update connection status
  void _updateConnectionStatus(List<ConnectivityResult> connectivityResult) {
    _connectionStatus = connectivityResult;
    notifyListeners();
    
    debugPrint('Connectivity changed: ${_connectionStatus.join(', ')}');
    
    // Trigger callbacks based on connectivity status
    if (isConnected) {
      _onConnected();
    } else {
      _onDisconnected();
    }
  }

  // Called when connected
  void _onConnected() {
    debugPrint('Device is now connected to the internet');
    // Add any logic needed when connection is restored
  }

  // Called when disconnected
  void _onDisconnected() {
    debugPrint('Device is now disconnected from the internet');
    // Add any logic needed when connection is lost
  }

  // Check current connectivity status
  Future<bool> checkConnectivity() async {
    try {
      final result = await _connectivity.checkConnectivity();
      _connectionStatus = result;
      notifyListeners();
      return isConnected;
    } catch (e) {
      debugPrint('Error checking connectivity: $e');
      return false;
    }
  }

  // Wait for connection
  Future<bool> waitForConnection({Duration timeout = const Duration(seconds: 30)}) async {
    if (isConnected) return true;

    final completer = Completer<bool>();
    late StreamSubscription subscription;

    // Set up timeout
    final timer = Timer(timeout, () {
      if (!completer.isCompleted) {
        subscription.cancel();
        completer.complete(false);
      }
    });

    // Listen for connection
    subscription = _connectivity.onConnectivityChanged.listen((result) {
      if (!result.contains(ConnectivityResult.none) && !completer.isCompleted) {
        timer.cancel();
        subscription.cancel();
        completer.complete(true);
      }
    });

    return completer.future;
  }

  // Test internet connectivity by pinging a reliable server
  Future<bool> hasInternetAccess() async {
    try {
      // This would normally ping a server to verify internet access
      // For demo purposes, we'll just return the connectivity status
      return isConnected;
    } catch (e) {
      debugPrint('Internet access test failed: $e');
      return false;
    }
  }

  // Get detailed connection info
  Map<String, dynamic> getConnectionInfo() {
    return {
      'is_connected': isConnected,
      'connection_types': _connectionStatus.map((c) => c.name).toList(),
      'primary_connection': connectionType,
      'is_wifi': isWifiConnected,
      'is_mobile': isMobileConnected,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  // Get connection quality (mock implementation)
  ConnectionQuality getConnectionQuality() {
    if (!isConnected) {
      return ConnectionQuality.none;
    } else if (isWifiConnected) {
      return ConnectionQuality.excellent;
    } else if (isMobileConnected) {
      return ConnectionQuality.good;
    } else {
      return ConnectionQuality.fair;
    }
  }

  // Get connection strength (mock implementation)
  double getConnectionStrength() {
    switch (getConnectionQuality()) {
      case ConnectionQuality.excellent:
        return 1.0;
      case ConnectionQuality.good:
        return 0.8;
      case ConnectionQuality.fair:
        return 0.5;
      case ConnectionQuality.poor:
        return 0.3;
      case ConnectionQuality.none:
        return 0.0;
    }
  }

  // Check if specific connection type is available
  bool hasConnectionType(ConnectivityResult type) {
    return _connectionStatus.contains(type);
  }

  // Get human-readable status
  String getStatusText() {
    if (!isConnected) {
      return 'غير متصل بالإنترنت';
    } else if (isWifiConnected) {
      return 'متصل عبر WiFi';
    } else if (isMobileConnected) {
      return 'متصل عبر بيانات الجوال';
    } else {
      return 'متصل بالإنترنت';
    }
  }

  // Dispose of resources
  @override
  void dispose() {
    _connectivitySubscription.cancel();
    super.dispose();
  }

  // Reset service
  void reset() {
    _connectionStatus = [ConnectivityResult.none];
    _isInitialized = false;
    notifyListeners();
  }
}

// Connection quality enum
enum ConnectionQuality {
  none,
  poor,
  fair,
  good,
  excellent,
}

// Extension for connection quality
extension ConnectionQualityExtension on ConnectionQuality {
  String get displayName {
    switch (this) {
      case ConnectionQuality.none:
        return 'لا يوجد اتصال';
      case ConnectionQuality.poor:
        return 'ضعيف';
      case ConnectionQuality.fair:
        return 'متوسط';
      case ConnectionQuality.good:
        return 'جيد';
      case ConnectionQuality.excellent:
        return 'ممتاز';
    }
  }

  String get description {
    switch (this) {
      case ConnectionQuality.none:
        return 'لا يوجد اتصال بالإنترنت';
      case ConnectionQuality.poor:
        return 'اتصال ضعيف - قد تواجه بطء في التحميل';
      case ConnectionQuality.fair:
        return 'اتصال متوسط - الخدمات الأساسية متاحة';
      case ConnectionQuality.good:
        return 'اتصال جيد - جميع الخدمات متاحة';
      case ConnectionQuality.excellent:
        return 'اتصال ممتاز - أداء مثالي';
    }
  }
}
