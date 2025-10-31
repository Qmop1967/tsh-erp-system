/// User Session Model
class UserSession {
  final String id;
  final int userId;
  final String? deviceId;
  final String status;
  final bool isMobile;
  final String? ipAddress;
  final String? userAgent;
  final DateTime? createdAt;
  final DateTime? expiresAt;
  final DateTime? lastActivity;
  final String? riskLevel;

  UserSession({
    required this.id,
    required this.userId,
    this.deviceId,
    required this.status,
    this.isMobile = false,
    this.ipAddress,
    this.userAgent,
    this.createdAt,
    this.expiresAt,
    this.lastActivity,
    this.riskLevel,
  });

  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      id: json['id'] as String,
      userId: json['user_id'] as int,
      deviceId: json['device_id'] as String?,
      status: json['status'] as String,
      isMobile: json['is_mobile'] as bool? ?? false,
      ipAddress: json['ip_address'] as String?,
      userAgent: json['user_agent'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      lastActivity: json['last_activity'] != null
          ? DateTime.parse(json['last_activity'] as String)
          : null,
      riskLevel: json['risk_level'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'device_id': deviceId,
      'status': status,
      'is_mobile': isMobile,
      'ip_address': ipAddress,
      'user_agent': userAgent,
      'created_at': createdAt?.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'last_activity': lastActivity?.toIso8601String(),
      'risk_level': riskLevel,
    };
  }

  bool get isActive => status == 'active';
  bool get isExpired => expiresAt != null && expiresAt!.isBefore(DateTime.now());
}
