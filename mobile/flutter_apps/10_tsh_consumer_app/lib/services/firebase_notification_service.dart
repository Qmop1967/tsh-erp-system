import 'dart:async';
import 'dart:io';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/foundation.dart';

/// Firebase Notification Service for TSH Consumer App
///
/// Handles:
/// - Firebase Cloud Messaging (FCM) initialization
/// - Push notification reception and display
/// - Notification click handling
/// - Token management for user device registration
class FirebaseNotificationService {
  static final FirebaseNotificationService _instance =
      FirebaseNotificationService._internal();
  factory FirebaseNotificationService() => _instance;
  FirebaseNotificationService._internal();

  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  // Stream controllers for notification events
  final StreamController<RemoteMessage> _messageStreamController =
      StreamController<RemoteMessage>.broadcast();
  final StreamController<String> _tokenStreamController =
      StreamController<String>.broadcast();

  Stream<RemoteMessage> get onMessageReceived => _messageStreamController.stream;
  Stream<String> get onTokenRefresh => _tokenStreamController.stream;

  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  /// Initialize Firebase and notification services
  Future<void> initialize() async {
    try {
      // Initialize Firebase
      await Firebase.initializeApp();
      debugPrint('✅ Firebase initialized successfully');

      // Request notification permissions
      await _requestPermissions();

      // Initialize local notifications
      await _initializeLocalNotifications();

      // Configure FCM
      await _configureFCM();

      // Get and store FCM token
      await _retrieveFCMToken();

      debugPrint('✅ Firebase Notification Service initialized');
    } catch (e) {
      debugPrint('❌ Failed to initialize Firebase: $e');
      rethrow;
    }
  }

  /// Request notification permissions (iOS)
  Future<void> _requestPermissions() async {
    final settings = await _firebaseMessaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      debugPrint('✅ Notification permissions granted');
    } else if (settings.authorizationStatus ==
        AuthorizationStatus.provisional) {
      debugPrint('⚠️ Provisional notification permissions granted');
    } else {
      debugPrint('❌ Notification permissions denied');
    }
  }

  /// Initialize local notifications plugin
  Future<void> _initializeLocalNotifications() async {
    // Android initialization
    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS initialization
    final iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
      onDidReceiveLocalNotification: (id, title, body, payload) async {
        // Handle iOS foreground notification
        debugPrint('iOS foreground notification: $title');
      },
    );

    final initializationSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        // Handle notification tap
        _handleNotificationTap(response.payload);
      },
    );

    debugPrint('✅ Local notifications initialized');
  }

  /// Configure Firebase Cloud Messaging handlers
  Future<void> _configureFCM() async {
    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      debugPrint('📬 Foreground notification received: ${message.notification?.title}');
      _messageStreamController.add(message);
      _showLocalNotification(message);
    });

    // Handle notification tap when app is in background/terminated
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      debugPrint('📬 Notification tapped (background): ${message.notification?.title}');
      _messageStreamController.add(message);
      _handleNotificationTap(message.data['notification_id']);
    });

    // Handle notification tap when app was terminated
    final initialMessage = await _firebaseMessaging.getInitialMessage();
    if (initialMessage != null) {
      debugPrint('📬 Notification tapped (terminated): ${initialMessage.notification?.title}');
      _messageStreamController.add(initialMessage);
      _handleNotificationTap(initialMessage.data['notification_id']);
    }

    debugPrint('✅ FCM configured');
  }

  /// Retrieve and store FCM token
  Future<void> _retrieveFCMToken() async {
    try {
      _fcmToken = await _firebaseMessaging.getToken();
      if (_fcmToken != null) {
        debugPrint('📱 FCM Token: $_fcmToken');
        _tokenStreamController.add(_fcmToken!);

        // TODO: Send token to backend for registration
        // await _registerTokenWithBackend(_fcmToken!);
      }

      // Listen for token refresh
      _firebaseMessaging.onTokenRefresh.listen((newToken) {
        debugPrint('🔄 FCM Token refreshed: $newToken');
        _fcmToken = newToken;
        _tokenStreamController.add(newToken);

        // TODO: Update token on backend
        // await _registerTokenWithBackend(newToken);
      });
    } catch (e) {
      debugPrint('❌ Failed to retrieve FCM token: $e');
    }
  }

  /// Register FCM token with NeuroLink backend
  Future<void> registerTokenWithBackend(String token, int userId) async {
    // TODO: Implement API call to register device token
    // POST /v1/notifications/register-device
    // {
    //   "user_id": userId,
    //   "fcm_token": token,
    //   "platform": Platform.isAndroid ? "android" : "ios",
    //   "device_info": {...}
    // }
    debugPrint('TODO: Register FCM token with backend');
  }

  /// Show local notification for foreground messages
  Future<void> _showLocalNotification(RemoteMessage message) async {
    final notification = message.notification;
    if (notification == null) return;

    // Determine notification channel based on severity/priority
    final data = message.data;
    final severity = data['severity'] ?? 'info';
    final channelId = 'tsh_$severity';
    final channelName = 'TSH ${severity.toUpperCase()} Notifications';

    // Android notification details
    final androidDetails = AndroidNotificationDetails(
      channelId,
      channelName,
      channelDescription: 'TSH ERP notifications for $severity level',
      importance: _getImportance(severity),
      priority: _getPriority(severity),
      icon: '@mipmap/ic_launcher',
      color: _getColor(severity),
      enableVibration: true,
      playSound: true,
    );

    // iOS notification details
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      notificationDetails,
      payload: data['notification_id'],
    );

    debugPrint('✅ Local notification displayed: ${notification.title}');
  }

  /// Handle notification tap
  void _handleNotificationTap(String? notificationId) {
    if (notificationId == null || notificationId.isEmpty) return;

    debugPrint('🔔 Notification tapped: $notificationId');

    // TODO: Navigate to notification details screen
    // Example: Get.to(() => NotificationDetailScreen(notificationId: notificationId));
    // Or: context.push('/notifications/$notificationId');
  }

  /// Get Android notification importance based on severity
  Importance _getImportance(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Importance.max;
      case 'error':
      case 'warning':
        return Importance.high;
      case 'info':
      default:
        return Importance.defaultImportance;
    }
  }

  /// Get Android notification priority based on severity
  Priority _getPriority(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Priority.max;
      case 'error':
      case 'warning':
        return Priority.high;
      case 'info':
      default:
        return Priority.defaultPriority;
    }
  }

  /// Get notification color based on severity
  int? _getColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 0xFFB71C1C; // Deep red
      case 'error':
        return 0xFFF44336; // Red
      case 'warning':
        return 0xFFFF9800; // Orange
      case 'info':
      default:
        return 0xFF2196F3; // Blue
    }
  }

  /// Subscribe to a topic
  Future<void> subscribeToTopic(String topic) async {
    try {
      await _firebaseMessaging.subscribeToTopic(topic);
      debugPrint('✅ Subscribed to topic: $topic');
    } catch (e) {
      debugPrint('❌ Failed to subscribe to topic $topic: $e');
    }
  }

  /// Unsubscribe from a topic
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _firebaseMessaging.unsubscribeFromTopic(topic);
      debugPrint('✅ Unsubscribed from topic: $topic');
    } catch (e) {
      debugPrint('❌ Failed to unsubscribe from topic $topic: $e');
    }
  }

  /// Clean up resources
  void dispose() {
    _messageStreamController.close();
    _tokenStreamController.close();
  }
}

/// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  debugPrint('📬 Background notification received: ${message.notification?.title}');
  // Handle background message if needed
}
