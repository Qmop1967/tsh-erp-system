/// Notification models for TSH ERP mobile app
/// Matches backend notification system structure

enum NotificationType {
  // Inventory notifications
  lowStock('low_stock'),
  outOfStock('out_of_stock'),
  stockMovement('stock_movement'),
  stockAdjustment('stock_adjustment'),

  // Sales notifications
  newOrder('new_order'),
  orderConfirmed('order_confirmed'),
  orderShipped('order_shipped'),
  orderDelivered('order_delivered'),
  orderCancelled('order_cancelled'),

  // Purchase notifications
  purchaseOrderCreated('purchase_order_created'),
  purchaseOrderApproved('purchase_order_approved'),
  purchaseOrderReceived('purchase_order_received'),

  // Financial notifications
  invoiceCreated('invoice_created'),
  invoicePaid('invoice_paid'),
  invoiceOverdue('invoice_overdue'),
  paymentReceived('payment_received'),

  // HR notifications
  leaveRequest('leave_request'),
  leaveApproved('leave_approved'),
  leaveRejected('leave_rejected'),
  timesheetReminder('timesheet_reminder'),

  // System notifications
  systemAlert('system_alert'),
  systemUpdate('system_update'),
  backupComplete('backup_complete'),
  backupFailed('backup_failed'),

  // User notifications
  userMentioned('user_mentioned'),
  taskAssigned('task_assigned'),
  approvalRequest('approval_request'),
  messageReceived('message_received'),

  // Custom
  custom('custom');

  final String value;
  const NotificationType(this.value);

  static NotificationType fromString(String value) {
    return NotificationType.values.firstWhere(
      (type) => type.value == value,
      orElse: () => NotificationType.custom,
    );
  }
}

enum NotificationPriority {
  low('low'),
  medium('medium'),
  high('high'),
  critical('critical');

  final String value;
  const NotificationPriority(this.value);

  static NotificationPriority fromString(String value) {
    return NotificationPriority.values.firstWhere(
      (priority) => priority.value == value,
      orElse: () => NotificationPriority.medium,
    );
  }
}

class NotificationAction {
  final String label;
  final String url;
  final String? style;

  NotificationAction({
    required this.label,
    required this.url,
    this.style = 'primary',
  });

  factory NotificationAction.fromJson(Map<String, dynamic> json) {
    return NotificationAction(
      label: json['label'] ?? '',
      url: json['url'] ?? '',
      style: json['style'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'label': label,
      'url': url,
      if (style != null) 'style': style,
    };
  }
}

class NotificationModel {
  final int id;
  final int userId;
  final int? tenantId;
  final NotificationType type;
  final NotificationPriority priority;
  final String title;
  final String message;

  // Rich content
  final String? imageUrl;
  final String? icon;
  final String? color;

  // Actions
  final String? actionUrl;
  final String? actionLabel;
  final List<NotificationAction>? actions;

  // Metadata
  final Map<String, dynamic>? metaData;

  // Status
  final bool isRead;
  final bool isArchived;
  final DateTime? readAt;

  // Delivery
  final List<String> channels;
  final List<String>? sentVia;
  final Map<String, String>? deliveryStatus;

  // Timestamps
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? expiresAt;

  // Related entity
  final String? relatedEntityType;
  final int? relatedEntityId;

  NotificationModel({
    required this.id,
    required this.userId,
    this.tenantId,
    required this.type,
    required this.priority,
    required this.title,
    required this.message,
    this.imageUrl,
    this.icon,
    this.color,
    this.actionUrl,
    this.actionLabel,
    this.actions,
    this.metaData,
    required this.isRead,
    required this.isArchived,
    this.readAt,
    required this.channels,
    this.sentVia,
    this.deliveryStatus,
    required this.createdAt,
    required this.updatedAt,
    this.expiresAt,
    this.relatedEntityType,
    this.relatedEntityId,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'],
      userId: json['user_id'],
      tenantId: json['tenant_id'],
      type: NotificationType.fromString(json['type']),
      priority: NotificationPriority.fromString(json['priority']),
      title: json['title'],
      message: json['message'],
      imageUrl: json['image_url'],
      icon: json['icon'],
      color: json['color'],
      actionUrl: json['action_url'],
      actionLabel: json['action_label'],
      actions: json['actions'] != null
          ? (json['actions'] as List)
              .map((action) => NotificationAction.fromJson(action))
              .toList()
          : null,
      metaData: json['meta_data'],
      isRead: json['is_read'] ?? false,
      isArchived: json['is_archived'] ?? false,
      readAt: json['read_at'] != null ? DateTime.parse(json['read_at']) : null,
      channels: List<String>.from(json['channels'] ?? ['in_app']),
      sentVia: json['sent_via'] != null ? List<String>.from(json['sent_via']) : null,
      deliveryStatus: json['delivery_status'] != null
          ? Map<String, String>.from(json['delivery_status'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      expiresAt: json['expires_at'] != null ? DateTime.parse(json['expires_at']) : null,
      relatedEntityType: json['related_entity_type'],
      relatedEntityId: json['related_entity_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'tenant_id': tenantId,
      'type': type.value,
      'priority': priority.value,
      'title': title,
      'message': message,
      'image_url': imageUrl,
      'icon': icon,
      'color': color,
      'action_url': actionUrl,
      'action_label': actionLabel,
      'actions': actions?.map((a) => a.toJson()).toList(),
      'meta_data': metaData,
      'is_read': isRead,
      'is_archived': isArchived,
      'read_at': readAt?.toIso8601String(),
      'channels': channels,
      'sent_via': sentVia,
      'delivery_status': deliveryStatus,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'related_entity_type': relatedEntityType,
      'related_entity_id': relatedEntityId,
    };
  }

  NotificationModel copyWith({
    bool? isRead,
    bool? isArchived,
    DateTime? readAt,
  }) {
    return NotificationModel(
      id: id,
      userId: userId,
      tenantId: tenantId,
      type: type,
      priority: priority,
      title: title,
      message: message,
      imageUrl: imageUrl,
      icon: icon,
      color: color,
      actionUrl: actionUrl,
      actionLabel: actionLabel,
      actions: actions,
      metaData: metaData,
      isRead: isRead ?? this.isRead,
      isArchived: isArchived ?? this.isArchived,
      readAt: readAt ?? this.readAt,
      channels: channels,
      sentVia: sentVia,
      deliveryStatus: deliveryStatus,
      createdAt: createdAt,
      updatedAt: updatedAt,
      expiresAt: expiresAt,
      relatedEntityType: relatedEntityType,
      relatedEntityId: relatedEntityId,
    );
  }
}

class NotificationListResponse {
  final List<NotificationModel> notifications;
  final int total;
  final int unreadCount;
  final int page;
  final int pageSize;
  final bool hasMore;

  NotificationListResponse({
    required this.notifications,
    required this.total,
    required this.unreadCount,
    required this.page,
    required this.pageSize,
    required this.hasMore,
  });

  factory NotificationListResponse.fromJson(Map<String, dynamic> json) {
    return NotificationListResponse(
      notifications: (json['notifications'] as List)
          .map((n) => NotificationModel.fromJson(n))
          .toList(),
      total: json['total'],
      unreadCount: json['unread_count'],
      page: json['page'],
      pageSize: json['page_size'],
      hasMore: json['has_more'],
    );
  }
}

class NotificationStats {
  final int totalNotifications;
  final int unreadCount;
  final int readCount;
  final int archivedCount;
  final Map<String, int> byPriority;
  final Map<String, int> byType;
  final List<Map<String, dynamic>> recentActivity;

  NotificationStats({
    required this.totalNotifications,
    required this.unreadCount,
    required this.readCount,
    required this.archivedCount,
    required this.byPriority,
    required this.byType,
    required this.recentActivity,
  });

  factory NotificationStats.fromJson(Map<String, dynamic> json) {
    return NotificationStats(
      totalNotifications: json['total_notifications'],
      unreadCount: json['unread_count'],
      readCount: json['read_count'],
      archivedCount: json['archived_count'],
      byPriority: Map<String, int>.from(json['by_priority'] ?? {}),
      byType: Map<String, int>.from(json['by_type'] ?? {}),
      recentActivity: List<Map<String, dynamic>>.from(json['recent_activity'] ?? []),
    );
  }
}

class NotificationPreferences {
  final int id;
  final int userId;
  final bool enabled;
  final bool quietHoursEnabled;
  final String? quietHoursStart;
  final String? quietHoursEnd;
  final bool enableInApp;
  final bool enablePush;
  final bool enableEmail;
  final bool enableSms;
  final Map<String, Map<String, bool>>? typePreferences;
  final NotificationPriority minPriority;
  final List<String>? fcmTokens;
  final List<String>? apnsTokens;
  final String? emailAddress;
  final bool emailDigestEnabled;
  final String emailDigestFrequency;
  final DateTime createdAt;
  final DateTime updatedAt;

  NotificationPreferences({
    required this.id,
    required this.userId,
    required this.enabled,
    required this.quietHoursEnabled,
    this.quietHoursStart,
    this.quietHoursEnd,
    required this.enableInApp,
    required this.enablePush,
    required this.enableEmail,
    required this.enableSms,
    this.typePreferences,
    required this.minPriority,
    this.fcmTokens,
    this.apnsTokens,
    this.emailAddress,
    required this.emailDigestEnabled,
    required this.emailDigestFrequency,
    required this.createdAt,
    required this.updatedAt,
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    return NotificationPreferences(
      id: json['id'],
      userId: json['user_id'],
      enabled: json['enabled'] ?? true,
      quietHoursEnabled: json['quiet_hours_enabled'] ?? false,
      quietHoursStart: json['quiet_hours_start'],
      quietHoursEnd: json['quiet_hours_end'],
      enableInApp: json['enable_in_app'] ?? true,
      enablePush: json['enable_push'] ?? true,
      enableEmail: json['enable_email'] ?? true,
      enableSms: json['enable_sms'] ?? false,
      typePreferences: json['type_preferences'] != null
          ? Map<String, Map<String, bool>>.from(json['type_preferences'])
          : null,
      minPriority: NotificationPriority.fromString(json['min_priority'] ?? 'low'),
      fcmTokens: json['fcm_tokens'] != null ? List<String>.from(json['fcm_tokens']) : null,
      apnsTokens: json['apns_tokens'] != null ? List<String>.from(json['apns_tokens']) : null,
      emailAddress: json['email_address'],
      emailDigestEnabled: json['email_digest_enabled'] ?? false,
      emailDigestFrequency: json['email_digest_frequency'] ?? 'daily',
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'enabled': enabled,
      'quiet_hours_enabled': quietHoursEnabled,
      'quiet_hours_start': quietHoursStart,
      'quiet_hours_end': quietHoursEnd,
      'enable_in_app': enableInApp,
      'enable_push': enablePush,
      'enable_email': enableEmail,
      'enable_sms': enableSms,
      'type_preferences': typePreferences,
      'min_priority': minPriority.value,
      'fcm_tokens': fcmTokens,
      'apns_tokens': apnsTokens,
      'email_address': emailAddress,
      'email_digest_enabled': emailDigestEnabled,
      'email_digest_frequency': emailDigestFrequency,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
