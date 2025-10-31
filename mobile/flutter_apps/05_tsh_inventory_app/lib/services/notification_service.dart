import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/notification_models.dart';
import 'auth_service.dart';

class NotificationService {
  static const String baseUrl = 'http://192.168.68.51:8000/api/notifications';
  final AuthService _authService = AuthService();

  Future<Map<String, String>> _getHeaders() async {
    final token = await _authService.getStoredToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // ===============================================
  // Fetch Notifications
  // ===============================================

  /// Get user's notifications with filters
  Future<NotificationListResponse> getNotifications({
    int skip = 0,
    int limit = 50,
    bool unreadOnly = false,
    NotificationType? type,
    NotificationPriority? priority,
  }) async {
    try {
      final queryParams = <String, String>{
        'skip': skip.toString(),
        'limit': limit.toString(),
        if (unreadOnly) 'unread_only': 'true',
        if (type != null) 'notification_type': type.value,
        if (priority != null) 'priority': priority.value,
      };

      final uri = Uri.parse(baseUrl).replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: await _getHeaders());

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return NotificationListResponse.fromJson(data);
      } else {
        throw Exception('Failed to load notifications: ${response.statusCode}');
      }
    } catch (e) {
      // Return empty list for development/offline mode
      return NotificationListResponse(
        notifications: [],
        total: 0,
        unreadCount: 0,
        page: 1,
        pageSize: limit,
        hasMore: false,
      );
    }
  }

  /// Get a single notification by ID
  Future<NotificationModel?> getNotification(int notificationId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/$notificationId'),
        headers: await _getHeaders(),
      );

      if (response.statusCode == 200) {
        return NotificationModel.fromJson(json.decode(response.body));
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  // ===============================================
  // Notification Actions
  // ===============================================

  /// Mark notification as read
  Future<NotificationModel?> markAsRead(int notificationId) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/$notificationId/read'),
        headers: await _getHeaders(),
      );

      if (response.statusCode == 200) {
        return NotificationModel.fromJson(json.decode(response.body));
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  /// Mark all notifications as read
  Future<int> markAllAsRead() async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/read-all'),
        headers: await _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['count'] ?? 0;
      } else {
        return 0;
      }
    } catch (e) {
      return 0;
    }
  }

  /// Delete a notification
  Future<bool> deleteNotification(int notificationId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/$notificationId'),
        headers: await _getHeaders(),
      );

      return response.statusCode == 204;
    } catch (e) {
      return false;
    }
  }

  /// Archive a notification
  Future<NotificationModel?> archiveNotification(int notificationId) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/$notificationId/archive'),
        headers: await _getHeaders(),
      );

      if (response.statusCode == 200) {
        return NotificationModel.fromJson(json.decode(response.body));
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  // ===============================================
  // Bulk Operations
  // ===============================================

  /// Mark multiple notifications as read
  Future<int> bulkMarkAsRead(List<int> notificationIds) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/bulk/mark-read'),
        headers: await _getHeaders(),
        body: json.encode({'notification_ids': notificationIds}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['count'] ?? 0;
      } else {
        return 0;
      }
    } catch (e) {
      return 0;
    }
  }

  /// Delete multiple notifications
  Future<int> bulkDelete(List<int> notificationIds) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/bulk/delete'),
        headers: await _getHeaders(),
        body: json.encode({'notification_ids': notificationIds}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['count'] ?? 0;
      } else {
        return 0;
      }
    } catch (e) {
      return 0;
    }
  }

  /// Archive multiple notifications
  Future<int> bulkArchive(List<int> notificationIds) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/bulk/archive'),
        headers: await _getHeaders(),
        body: json.encode({'notification_ids': notificationIds}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['count'] ?? 0;
      } else {
        return 0;
      }
    } catch (e) {
      return 0;
    }
  }

  // ===============================================
  // Statistics
  // ===============================================

  /// Get notification statistics
  Future<NotificationStats?> getStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/stats'),
        headers: await _getHeaders(),
      );

      if (response.statusCode == 200) {
        return NotificationStats.fromJson(json.decode(response.body));
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  // ===============================================
  // Preferences
  // ===============================================

  /// Get notification preferences
  Future<NotificationPreferences?> getPreferences() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/preferences'),
        headers: await _getHeaders(),
      );

      if (response.statusCode == 200) {
        return NotificationPreferences.fromJson(json.decode(response.body));
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  /// Update notification preferences
  Future<NotificationPreferences?> updatePreferences(
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/preferences'),
        headers: await _getHeaders(),
        body: json.encode(updates),
      );

      if (response.statusCode == 200) {
        return NotificationPreferences.fromJson(json.decode(response.body));
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  /// Register device token for push notifications
  Future<bool> registerDeviceToken({
    required String token,
    required String platform, // 'ios', 'android', 'web'
    String? deviceId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/device-token'),
        headers: await _getHeaders(),
        body: json.encode({
          'token': token,
          'platform': platform,
          if (deviceId != null) 'device_id': deviceId,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Unregister device token
  Future<bool> unregisterDeviceToken(String token) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/device-token/$token'),
        headers: await _getHeaders(),
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // ===============================================
  // Helper Methods
  // ===============================================

  /// Get unread count only (lightweight)
  Future<int> getUnreadCount() async {
    try {
      final response = await getNotifications(limit: 1);
      return response.unreadCount;
    } catch (e) {
      return 0;
    }
  }

  /// Check if there are new notifications
  Future<bool> hasNewNotifications(DateTime since) async {
    try {
      final response = await getNotifications(limit: 1);
      if (response.notifications.isEmpty) return false;

      return response.notifications.first.createdAt.isAfter(since);
    } catch (e) {
      return false;
    }
  }

  /// Get notifications for a specific entity (e.g., order, product)
  Future<List<NotificationModel>> getNotificationsForEntity({
    required String entityType,
    required int entityId,
  }) async {
    try {
      final allNotifications = await getNotifications(limit: 100);
      return allNotifications.notifications
          .where((n) =>
              n.relatedEntityType == entityType &&
              n.relatedEntityId == entityId)
          .toList();
    } catch (e) {
      return [];
    }
  }
}
