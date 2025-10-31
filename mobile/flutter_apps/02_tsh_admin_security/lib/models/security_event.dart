/// Security Event Model
class SecurityEvent {
  final int id;
  final String eventType;
  final String severity;
  final String? title;
  final String? description;
  final int? userId;
  final String? sessionId;
  final String? ipAddress;
  final bool isResolved;
  final DateTime? createdAt;
  final DateTime? resolvedAt;

  SecurityEvent({
    required this.id,
    required this.eventType,
    required this.severity,
    this.title,
    this.description,
    this.userId,
    this.sessionId,
    this.ipAddress,
    this.isResolved = false,
    this.createdAt,
    this.resolvedAt,
  });

  factory SecurityEvent.fromJson(Map<String, dynamic> json) {
    return SecurityEvent(
      id: json['id'] as int,
      eventType: json['event_type'] as String,
      severity: json['severity'] as String,
      title: json['title'] as String?,
      description: json['description'] as String?,
      userId: json['user_id'] as int?,
      sessionId: json['session_id'] as String?,
      ipAddress: json['ip_address'] as String?,
      isResolved: json['is_resolved'] as bool? ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      resolvedAt: json['resolved_at'] != null
          ? DateTime.parse(json['resolved_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'event_type': eventType,
      'severity': severity,
      'title': title,
      'description': description,
      'user_id': userId,
      'session_id': sessionId,
      'ip_address': ipAddress,
      'is_resolved': isResolved,
      'created_at': createdAt?.toIso8601String(),
      'resolved_at': resolvedAt?.toIso8601String(),
    };
  }
}
