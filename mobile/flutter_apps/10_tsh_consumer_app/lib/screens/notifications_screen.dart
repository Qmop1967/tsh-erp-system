import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

/// Notification Model
class AppNotification {
  final String id;
  final String title;
  final String body;
  final String severity; // info, warning, error, critical
  final DateTime createdAt;
  final bool isRead;
  final bool requiresAcknowledgment;
  final String? actionUrl;
  final String? actionLabel;
  final Map<String, dynamic>? data;

  AppNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.severity,
    required this.createdAt,
    this.isRead = false,
    this.requiresAcknowledgment = false,
    this.actionUrl,
    this.actionLabel,
    this.data,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'],
      title: json['title'],
      body: json['body'],
      severity: json['severity'] ?? 'info',
      createdAt: DateTime.parse(json['created_at']),
      isRead: json['is_read'] ?? false,
      requiresAcknowledgment: json['requires_acknowledgment'] ?? false,
      actionUrl: json['action_url'],
      actionLabel: json['action_label'],
      data: json['data'],
    );
  }

  AppNotification copyWith({
    bool? isRead,
    bool? requiresAcknowledgment,
  }) {
    return AppNotification(
      id: id,
      title: title,
      body: body,
      severity: severity,
      createdAt: createdAt,
      isRead: isRead ?? this.isRead,
      requiresAcknowledgment:
          requiresAcknowledgment ?? this.requiresAcknowledgment,
      actionUrl: actionUrl,
      actionLabel: actionLabel,
      data: data,
    );
  }
}

/// Notifications State Provider
final notificationsProvider =
    StateNotifierProvider<NotificationsNotifier, List<AppNotification>>((ref) {
  return NotificationsNotifier();
});

class NotificationsNotifier extends StateNotifier<List<AppNotification>> {
  NotificationsNotifier() : super([]) {
    // Load notifications from API
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    // TODO: Fetch from NeuroLink API
    // final response = await http.get('$apiUrl/v1/notifications/my');
    // final List<dynamic> data = jsonDecode(response.body);
    // state = data.map((json) => AppNotification.fromJson(json)).toList();

    // Mock data for development
    state = [
      AppNotification(
        id: '1',
        title: '💰 Price List Updated: Consumer Price List',
        body:
            '150 products have been updated. Please review the new prices before quoting to customers.',
        severity: 'warning',
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
        isRead: false,
        requiresAcknowledgment: true,
        actionUrl: '/products',
        actionLabel: 'View Updated Prices',
        data: {'products_updated': 150, 'price_list_name': 'Consumer Price List'},
      ),
      AppNotification(
        id: '2',
        title: '✅ Sync Completed: Products',
        body:
            'Successfully synced 1,234/1,250 products items (98.7% success rate) in 45.3s.',
        severity: 'info',
        createdAt: DateTime.now().subtract(const Duration(hours: 5)),
        isRead: true,
        actionUrl: '/sync-details',
        actionLabel: 'View Sync Details',
      ),
      AppNotification(
        id: '3',
        title: '🚨 CRITICAL: Sync Failed - Orders',
        body:
            'Sync operation failed: Connection timeout. Immediate action required to restore data synchronization.',
        severity: 'critical',
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
        isRead: false,
        requiresAcknowledgment: true,
        actionUrl: '/alerts',
        actionLabel: 'View Error Details',
      ),
      AppNotification(
        id: '4',
        title: '⚠️ Stock Discrepancy: Philips LED Bulb 9W',
        body:
            'Large stock difference detected. Zoho: 450, Local: 520, Difference: 70 units.',
        severity: 'warning',
        createdAt: DateTime.now().subtract(const Duration(days: 2)),
        isRead: true,
        actionUrl: '/products/PHL-LED-9W',
        actionLabel: 'Review Stock',
      ),
    ];
  }

  void markAsRead(String notificationId) {
    state = [
      for (final notification in state)
        if (notification.id == notificationId)
          notification.copyWith(isRead: true)
        else
          notification,
    ];

    // TODO: Update on backend
    // await http.put('$apiUrl/v1/notifications/$notificationId/read');
  }

  void acknowledge(String notificationId) {
    state = [
      for (final notification in state)
        if (notification.id == notificationId)
          notification.copyWith(
            isRead: true,
            requiresAcknowledgment: false,
          )
        else
          notification,
    ];

    // TODO: Acknowledge on backend
    // await http.post('$apiUrl/v1/notifications/$notificationId/acknowledge');
  }

  Future<void> refresh() async {
    await _loadNotifications();
  }
}

/// Notifications Screen
class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() =>
      _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  String _filter = 'all'; // all, unread, read

  @override
  Widget build(BuildContext context) {
    final notifications = ref.watch(notificationsProvider);
    final filteredNotifications = _filterNotifications(notifications);

    return Scaffold(
      appBar: AppBar(
        title: const Text('الإشعارات', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        actions: [
          // Filter menu
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            onSelected: (value) {
              setState(() => _filter = value);
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'all', child: Text('الكل')),
              const PopupMenuItem(value: 'unread', child: Text('غير مقروء')),
              const PopupMenuItem(value: 'read', child: Text('مقروء')),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(notificationsProvider.notifier).refresh(),
        child: filteredNotifications.isEmpty
            ? _buildEmptyState()
            : ListView.builder(
                itemCount: filteredNotifications.length,
                itemBuilder: (context, index) {
                  final notification = filteredNotifications[index];
                  return _NotificationCard(
                    notification: notification,
                    onTap: () => _handleNotificationTap(notification),
                    onAcknowledge: () =>
                        _handleAcknowledge(notification.id),
                  );
                },
              ),
      ),
    );
  }

  List<AppNotification> _filterNotifications(
      List<AppNotification> notifications) {
    switch (_filter) {
      case 'unread':
        return notifications.where((n) => !n.isRead).toList();
      case 'read':
        return notifications.where((n) => n.isRead).toList();
      default:
        return notifications;
    }
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.notifications_off_outlined,
              size: 80, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'لا توجد إشعارات',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w500,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'سنُعلمك عند وصول إشعارات جديدة',
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  void _handleNotificationTap(AppNotification notification) {
    // Mark as read
    ref.read(notificationsProvider.notifier).markAsRead(notification.id);

    // Show notification details dialog
    showDialog(
      context: context,
      builder: (context) => _NotificationDetailDialog(
        notification: notification,
        onAcknowledge: notification.requiresAcknowledgment
            ? () {
                _handleAcknowledge(notification.id);
                Navigator.of(context).pop();
              }
            : null,
        onAction: notification.actionUrl != null
            ? () {
                Navigator.of(context).pop();
                // Navigate to action URL
                // TODO: Implement navigation
                debugPrint('Navigate to: ${notification.actionUrl}');
              }
            : null,
      ),
    );
  }

  void _handleAcknowledge(String notificationId) {
    ref.read(notificationsProvider.notifier).acknowledge(notificationId);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم تأكيد الإشعار')),
    );
  }
}

/// Notification Card Widget
class _NotificationCard extends StatelessWidget {
  final AppNotification notification;
  final VoidCallback onTap;
  final VoidCallback? onAcknowledge;

  const _NotificationCard({
    required this.notification,
    required this.onTap,
    this.onAcknowledge,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = _getSeverityColors(notification.severity);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: notification.isRead ? Colors.white : colorScheme['bg'],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme['border']!,
          width: notification.isRead ? 1 : 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header: Title and Time
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Unread indicator
                    if (!notification.isRead)
                      Container(
                        width: 8,
                        height: 8,
                        margin: const EdgeInsets.only(top: 6, left: 8),
                        decoration: BoxDecoration(
                          color: colorScheme['accent'],
                          shape: BoxShape.circle,
                        ),
                      ),
                    // Title
                    Expanded(
                      child: Text(
                        notification.title,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: notification.isRead
                              ? FontWeight.w500
                              : FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Time
                    Text(
                      _formatTime(notification.createdAt),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // Body
                Text(
                  notification.body,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[700],
                    height: 1.4,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),

                // Actions
                if (notification.requiresAcknowledgment ||
                    notification.actionLabel != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Row(
                      children: [
                        if (notification.requiresAcknowledgment)
                          OutlinedButton.icon(
                            onPressed: onAcknowledge,
                            icon: const Icon(Icons.check_circle_outline, size: 18),
                            label: const Text('تأكيد'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: colorScheme['accent'],
                              side: BorderSide(color: colorScheme['accent']!),
                            ),
                          ),
                        if (notification.requiresAcknowledgment &&
                            notification.actionLabel != null)
                          const SizedBox(width: 8),
                        if (notification.actionLabel != null)
                          TextButton.icon(
                            onPressed: onTap,
                            icon: const Icon(Icons.arrow_forward, size: 18),
                            label: Text(notification.actionLabel!),
                            style: TextButton.styleFrom(
                              foregroundColor: Theme.of(context).primaryColor,
                            ),
                          ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Map<String, Color> _getSeverityColors(String severity) {
    switch (severity) {
      case 'critical':
        return {
          'bg': Colors.red.shade50,
          'border': Colors.red.shade300,
          'accent': Colors.red.shade600,
        };
      case 'error':
        return {
          'bg': Colors.red.shade50,
          'border': Colors.red.shade200,
          'accent': Colors.red.shade500,
        };
      case 'warning':
        return {
          'bg': Colors.amber.shade50,
          'border': Colors.amber.shade300,
          'accent': Colors.amber.shade700,
        };
      default: // info
        return {
          'bg': Colors.blue.shade50,
          'border': Colors.blue.shade200,
          'accent': Colors.blue.shade600,
        };
    }
  }

  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 60) {
      return 'منذ ${difference.inMinutes} دقيقة';
    } else if (difference.inHours < 24) {
      return 'منذ ${difference.inHours} ساعة';
    } else if (difference.inDays < 7) {
      return 'منذ ${difference.inDays} يوم';
    } else {
      return DateFormat('dd/MM/yyyy').format(dateTime);
    }
  }
}

/// Notification Detail Dialog
class _NotificationDetailDialog extends StatelessWidget {
  final AppNotification notification;
  final VoidCallback? onAcknowledge;
  final VoidCallback? onAction;

  const _NotificationDetailDialog({
    required this.notification,
    this.onAcknowledge,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(notification.title),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(notification.body),
            const SizedBox(height: 16),
            Text(
              DateFormat('dd MMMM yyyy, hh:mm a').format(notification.createdAt),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
      actions: [
        if (onAcknowledge != null)
          TextButton.icon(
            onPressed: onAcknowledge,
            icon: const Icon(Icons.check_circle_outline),
            label: const Text('تأكيد'),
          ),
        if (onAction != null)
          ElevatedButton.icon(
            onPressed: onAction,
            icon: const Icon(Icons.arrow_forward),
            label: Text(notification.actionLabel ?? 'عرض'),
          ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('إغلاق'),
        ),
      ],
    );
  }
}
