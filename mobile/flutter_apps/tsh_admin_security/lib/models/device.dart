/// User Device Model
class UserDevice {
  final String id;
  final int userId;
  final String? deviceName;
  final String? deviceType;
  final String? platform;
  final String? browser;
  final String status;
  final bool isTrusted;
  final String? lastIpAddress;
  final DateTime? firstSeen;
  final DateTime? lastSeen;

  UserDevice({
    required this.id,
    required this.userId,
    this.deviceName,
    this.deviceType,
    this.platform,
    this.browser,
    required this.status,
    this.isTrusted = false,
    this.lastIpAddress,
    this.firstSeen,
    this.lastSeen,
  });

  factory UserDevice.fromJson(Map<String, dynamic> json) {
    return UserDevice(
      id: json['id'] as String,
      userId: json['user_id'] as int,
      deviceName: json['device_name'] as String?,
      deviceType: json['device_type'] as String?,
      platform: json['platform'] as String?,
      browser: json['browser'] as String?,
      status: json['status'] as String,
      isTrusted: json['is_trusted'] as bool? ?? false,
      lastIpAddress: json['last_ip_address'] as String?,
      firstSeen: json['first_seen'] != null
          ? DateTime.parse(json['first_seen'] as String)
          : null,
      lastSeen: json['last_seen'] != null
          ? DateTime.parse(json['last_seen'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'device_name': deviceName,
      'device_type': deviceType,
      'platform': platform,
      'browser': browser,
      'status': status,
      'is_trusted': isTrusted,
      'last_ip_address': lastIpAddress,
      'first_seen': firstSeen?.toIso8601String(),
      'last_seen': lastSeen?.toIso8601String(),
    };
  }

  String get displayName =>
      deviceName ?? '$platform - $browser' ?? 'Unknown Device';
}
