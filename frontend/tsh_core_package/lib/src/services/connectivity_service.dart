import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

class ConnectivityService {
  static final ConnectivityService _instance = ConnectivityService._internal();
  factory ConnectivityService() => _instance;
  ConnectivityService._internal();

  final Connectivity _connectivity = Connectivity();
  final StreamController<ConnectivityResult> _connectivityController = 
      StreamController<ConnectivityResult>.broadcast();

  StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  ConnectivityResult _currentStatus = ConnectivityResult.none;

  // Getters
  Stream<ConnectivityResult> get connectivityStream => _connectivityController.stream;
  ConnectivityResult get currentStatus => _currentStatus;
  bool get isConnected => _currentStatus != ConnectivityResult.none;
  bool get isWifi => _currentStatus == ConnectivityResult.wifi;
  bool get isMobile => _currentStatus == ConnectivityResult.mobile;

  // Initialize the service
  Future<void> initialize() async {
    _currentStatus = await _connectivity.checkConnectivity();
    _connectivityController.add(_currentStatus);

    _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
      (ConnectivityResult result) {
        _currentStatus = result;
        _connectivityController.add(result);
      },
    );
  }

  // Check current connectivity status
  Future<ConnectivityResult> checkConnectivity() async {
    try {
      final result = await _connectivity.checkConnectivity();
      _currentStatus = result;
      return result;
    } catch (e) {
      _currentStatus = ConnectivityResult.none;
      return ConnectivityResult.none;
    }
  }

  // Wait for internet connection
  Future<bool> waitForConnection({Duration timeout = const Duration(seconds: 30)}) async {
    if (isConnected) return true;

    final completer = Completer<bool>();
    late StreamSubscription subscription;

    subscription = connectivityStream.listen((result) {
      if (result != ConnectivityResult.none) {
        subscription.cancel();
        if (!completer.isCompleted) {
          completer.complete(true);
        }
      }
    });

    // Set up timeout
    Timer(timeout, () {
      subscription.cancel();
      if (!completer.isCompleted) {
        completer.complete(false);
      }
    });

    return completer.future;
  }

  // Get connectivity status as string
  String getStatusString() {
    switch (_currentStatus) {
      case ConnectivityResult.wifi:
        return 'WiFi';
      case ConnectivityResult.mobile:
        return 'Mobile Data';
      case ConnectivityResult.ethernet:
        return 'Ethernet';
      case ConnectivityResult.bluetooth:
        return 'Bluetooth';
      case ConnectivityResult.vpn:
        return 'VPN';
      case ConnectivityResult.other:
        return 'Other';
      case ConnectivityResult.none:
      default:
        return 'No Connection';
    }
  }

  // Check if specific connection type is available
  bool hasConnectionType(ConnectivityResult type) {
    return _currentStatus == type;
  }

  // Check if any of the specified connection types are available
  bool hasAnyConnectionType(List<ConnectivityResult> types) {
    return types.contains(_currentStatus);
  }

  // Dispose of resources
  void dispose() {
    _connectivitySubscription?.cancel();
    _connectivityController.close();
  }
}

// Extension to make connectivity results more readable
extension ConnectivityResultExtension on ConnectivityResult {
  bool get isConnected => this != ConnectivityResult.none;
  bool get isWifi => this == ConnectivityResult.wifi;
  bool get isMobile => this == ConnectivityResult.mobile;
  bool get isEthernet => this == ConnectivityResult.ethernet;
  
  String get displayName {
    switch (this) {
      case ConnectivityResult.wifi:
        return 'WiFi';
      case ConnectivityResult.mobile:
        return 'Mobile Data';
      case ConnectivityResult.ethernet:
        return 'Ethernet';
      case ConnectivityResult.bluetooth:
        return 'Bluetooth';
      case ConnectivityResult.vpn:
        return 'VPN';
      case ConnectivityResult.other:
        return 'Other';
      case ConnectivityResult.none:
      default:
        return 'No Connection';
    }
  }
}
