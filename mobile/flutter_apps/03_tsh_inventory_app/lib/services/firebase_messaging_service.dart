import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'notification_service.dart';
import 'dart:io' show Platform;

/// Firebase Cloud Messaging service for push notifications
/// Handles token registration, message receiving, and notification display
class FirebaseMessagingService {
  static final FirebaseMessagingService _instance = FirebaseMessagingService._internal();
  factory FirebaseMessagingService() => _instance;
  FirebaseMessagingService._internal();

  final NotificationService _notificationService = NotificationService();
  FirebaseMessaging? _messaging;
  String? _fcmToken;

  /// Initialize Firebase and set up messaging
  Future<void> initialize() async {
    try {
      // Initialize Firebase
      await Firebase.initializeApp();
      _messaging = FirebaseMessaging.instance;

      // Request permission for iOS
      await _requestPermission();

      // Get FCM token
      await _getToken();

      // Set up message handlers
      _setupMessageHandlers();

      print('✅ Firebase Messaging initialized successfully');
    } catch (e) {
      print('❌ Firebase initialization error: $e');
      // Continue without Firebase - app should work without push notifications
    }
  }

  /// Request notification permissions (iOS only)
  Future<void> _requestPermission() async {
    if (_messaging == null) return;

    try {
      NotificationSettings settings = await _messaging!.requestPermission(
        alert: true,
        announcement: false,
        badge: true,
        carPlay: false,
        criticalAlert: false,
        provisional: false,
        sound: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        print('✅ User granted notification permission');
      } else if (settings.authorizationStatus == AuthorizationStatus.provisional) {
        print('⚠️ User granted provisional notification permission');
      } else {
        print('❌ User declined notification permission');
      }
    } catch (e) {
      print('❌ Permission request error: $e');
    }
  }

  /// Get FCM token and register with backend
  Future<String?> _getToken() async {
    if (_messaging == null) return null;

    try {
      // For iOS, get APNS token first
      if (!kIsWeb && Platform.isIOS) {
        String? apnsToken = await _messaging!.getAPNSToken();
        if (apnsToken == null) {
          print('⚠️ APNS token not available yet, retrying...');
          // Wait and retry
          await Future.delayed(const Duration(seconds: 3));
          apnsToken = await _messaging!.getAPNSToken();
        }
        print('APNS Token: $apnsToken');
      }

      // Get FCM token
      _fcmToken = await _messaging!.getToken();
      print('FCM Token: $_fcmToken');

      if (_fcmToken != null) {
        // Register token with backend
        await _registerTokenWithBackend(_fcmToken!);

        // Listen for token refresh
        _messaging!.onTokenRefresh.listen((newToken) {
          _fcmToken = newToken;
          _registerTokenWithBackend(newToken);
        });
      }

      return _fcmToken;
    } catch (e) {
      print('❌ Error getting FCM token: $e');
      return null;
    }
  }

  /// Register FCM token with backend
  Future<void> _registerTokenWithBackend(String token) async {
    try {
      String platform;
      if (kIsWeb) {
        platform = 'web';
      } else if (Platform.isIOS) {
        platform = 'ios';
      } else if (Platform.isAndroid) {
        platform = 'android';
      } else {
        platform = 'other';
      }

      final success = await _notificationService.registerDeviceToken(
        token: token,
        platform: platform,
      );

      if (success) {
        print('✅ FCM token registered with backend: ${token.substring(0, 20)}...');
      } else {
        print('❌ Failed to register FCM token with backend');
      }
    } catch (e) {
      print('❌ Error registering token with backend: $e');
    }
  }

  /// Set up message handlers for different states
  void _setupMessageHandlers() {
    if (_messaging == null) return;

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📱 Foreground message received: ${message.notification?.title}');
      _handleMessage(message, isForeground: true);
    });

    // Handle background messages
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('📱 Background message opened: ${message.notification?.title}');
      _handleMessage(message, isForeground: false);
    });

    // Handle message when app is terminated
    _handleInitialMessage();
  }

  /// Handle initial message when app is opened from terminated state
  Future<void> _handleInitialMessage() async {
    if (_messaging == null) return;

    RemoteMessage? initialMessage = await _messaging!.getInitialMessage();
    if (initialMessage != null) {
      print('📱 App opened from terminated state: ${initialMessage.notification?.title}');
      _handleMessage(initialMessage, isForeground: false);
    }
  }

  /// Handle incoming message
  void _handleMessage(RemoteMessage message, {required bool isForeground}) {
    print('Message data: ${message.data}');
    print('Notification: ${message.notification?.toMap()}');

    // Extract notification data
    final notification = message.notification;
    final data = message.data;

    if (notification != null) {
      // Show local notification if in foreground
      if (isForeground) {
        _showLocalNotification(
          title: notification.title ?? 'New Notification',
          body: notification.body ?? '',
          data: data,
        );
      }

      // Handle navigation based on notification data
      if (data.containsKey('action_url')) {
        final actionUrl = data['action_url'];
        print('Navigate to: $actionUrl');
        // TODO: Implement navigation logic
      }
    }
  }

  /// Show local notification (when app is in foreground)
  void _showLocalNotification({
    required String title,
    required String body,
    Map<String, dynamic>? data,
  }) {
    // TODO: Implement local notification display using flutter_local_notifications
    print('📱 Local notification: $title - $body');
  }

  /// Get current FCM token
  String? get fcmToken => _fcmToken;

  /// Check if Firebase is initialized
  bool get isInitialized => _messaging != null;

  /// Delete FCM token (on logout)
  Future<void> deleteToken() async {
    if (_messaging == null) return;

    try {
      await _messaging!.deleteToken();
      _fcmToken = null;
      print('✅ FCM token deleted');
    } catch (e) {
      print('❌ Error deleting FCM token: $e');
    }
  }
}

/// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('📱 Background message received: ${message.notification?.title}');
  // Handle background message
}
