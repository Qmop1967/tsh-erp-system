import 'dart:convert';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/mfa_request.dart';
import '../screens/mfa/mfa_approval_screen.dart';
import 'navigation_service.dart';

class NotificationService {
  static final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  
  static Future<void> initialize() async {
    // Request notification permissions
    await _requestPermissions();
    
    // Initialize local notifications
    await _initializeLocalNotifications();
    
    // Initialize Firebase messaging
    await _initializeFirebaseMessaging();
    
    // Handle background messages
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  }
  
  static Future<void> _requestPermissions() async {
    // Request notification permission
    await Permission.notification.request();
    
    // Request Firebase messaging permissions
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );
    
    print('User granted permission: ${settings.authorizationStatus}');
  }
  
  static Future<void> _initializeLocalNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    
    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
      requestSoundPermission: true,
      requestBadgePermission: true,
      requestAlertPermission: true,
    );
    
    const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );
    
    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onDidReceiveNotificationResponse,
    );
  }
  
  static Future<void> _initializeFirebaseMessaging() async {
    // Get the token
    String? token = await _firebaseMessaging.getToken();
    print('FCM Token: $token');
    
    // Handle messages when app is in foreground
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    
    // Handle messages when app is opened from notification
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);
    
    // Check for initial message when app is opened from terminated state
    RemoteMessage? initialMessage = await _firebaseMessaging.getInitialMessage();
    if (initialMessage != null) {
      _handleMessageOpenedApp(initialMessage);
    }
  }
  
  static Future<void> _handleForegroundMessage(RemoteMessage message) async {
    print('Received foreground message: ${message.messageId}');
    
    if (message.data['type'] == 'mfa_request') {
      // Show local notification for MFA request
      await _showMFARequestNotification(message);
    }
  }
  
  static Future<void> _handleMessageOpenedApp(RemoteMessage message) async {
    print('Message opened app: ${message.messageId}');
    
    if (message.data['type'] == 'mfa_request') {
      // Navigate to MFA approval screen
      final mfaRequest = MFARequest.fromJson(message.data);
      NavigationService.push(MFAApprovalScreen(request: mfaRequest));
    }
  }
  
  static Future<void> _showMFARequestNotification(RemoteMessage message) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'mfa_requests',
      'MFA Requests',
      channelDescription: 'Multi-factor authentication requests',
      importance: Importance.max,
      priority: Priority.high,
      category: AndroidNotificationCategory.security,
      fullScreenIntent: true,
      actions: <AndroidNotificationAction>[
        AndroidNotificationAction(
          'approve',
          'Approve',
          icon: DrawableResourceAndroidBitmap('@drawable/ic_check'),
        ),
        AndroidNotificationAction(
          'deny',
          'Deny',
          icon: DrawableResourceAndroidBitmap('@drawable/ic_close'),
        ),
      ],
    );
    
    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      categoryIdentifier: 'mfa_request',
      interruptionLevel: InterruptionLevel.critical,
    );
    
    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: iOSPlatformChannelSpecifics,
    );
    
    await _localNotifications.show(
      message.hashCode,
      message.notification?.title ?? 'Authentication Request',
      message.notification?.body ?? 'Approve or deny access request',
      platformChannelSpecifics,
      payload: jsonEncode(message.data),
    );
  }
  
  static void _onDidReceiveNotificationResponse(NotificationResponse response) {
    if (response.actionId == 'approve') {
      _handleMFAResponse(response.payload, true);
    } else if (response.actionId == 'deny') {
      _handleMFAResponse(response.payload, false);
    } else if (response.payload != null) {
      // Handle tap on notification body
      final data = jsonDecode(response.payload!);
      if (data['type'] == 'mfa_request') {
        final mfaRequest = MFARequest.fromJson(data);
        NavigationService.push(MFAApprovalScreen(request: mfaRequest));
      }
    }
  }
  
  static void _handleMFAResponse(String? payload, bool approved) {
    if (payload != null) {
      final data = jsonDecode(payload);
      final mfaRequest = MFARequest.fromJson(data);
      
      // Handle the MFA response
      // This would typically call an API to approve/deny the request
      print('MFA Response: ${approved ? 'Approved' : 'Denied'} for request ${mfaRequest.requestId}');
    }
  }
  
  static Future<String?> getToken() async {
    return await _firebaseMessaging.getToken();
  }
  
  static Future<void> subscribeToTopic(String topic) async {
    await _firebaseMessaging.subscribeToTopic(topic);
  }
  
  static Future<void> unsubscribeFromTopic(String topic) async {
    await _firebaseMessaging.unsubscribeFromTopic(topic);
  }
}

// Top-level function for handling background messages
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('Handling a background message: ${message.messageId}');
  
  if (message.data['type'] == 'mfa_request') {
    // Show local notification even in background
    await NotificationService._showMFARequestNotification(message);
  }
}
