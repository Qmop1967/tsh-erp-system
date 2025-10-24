/// Audit Log Model
class AuditLog {
  final int id;
  final int? userId;
  final String action;
  final String resourceType;
  final String? resourceId;
  final String? description;
  final String? ipAddress;
  final DateTime? timestamp;

  AuditLog({
    required this.id,
    this.userId,
    required this.action,
    required this.resourceType,
    this.resourceId,
    this.description,
    this.ipAddress,
    this.timestamp,
  });

  factory AuditLog.fromJson(Map<String, dynamic> json) {
    return AuditLog(
      id: json['id'] as int,
      userId: json['user_id'] as int?,
      action: json['action'] as String,
      resourceType: json['resource_type'] as String,
      resourceId: json['resource_id'] as String?,
      description: json['description'] as String?,
      ipAddress: json['ip_address'] as String?,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'action': action,
      'resource_type': resourceType,
      'resource_id': resourceId,
      'description': description,
      'ip_address': ipAddress,
      'timestamp': timestamp?.toIso8601String(),
    };
  }
}
