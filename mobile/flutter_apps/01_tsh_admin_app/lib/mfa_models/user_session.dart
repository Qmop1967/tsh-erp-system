class UserSession {
  final String sessionId;
  final DateTime createdAt;
  final DateTime lastActivity;
  final DateTime? expiresAt;
  final String ipAddress;
  final Map<String, dynamic>? location;
  final String riskLevel;
  final bool isMobile;
  final Map<String, dynamic>? device;
  final bool isCurrent;
  
  UserSession({
    required this.sessionId,
    required this.createdAt,
    required this.lastActivity,
    this.expiresAt,
    required this.ipAddress,
    this.location,
    required this.riskLevel,
    required this.isMobile,
    this.device,
    required this.isCurrent,
  });
  
  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      sessionId: json['session_id'] ?? '',
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      lastActivity: DateTime.tryParse(json['last_activity'] ?? '') ?? DateTime.now(),
      expiresAt: json['expires_at'] != null 
          ? DateTime.tryParse(json['expires_at'])
          : null,
      ipAddress: json['ip_address'] ?? '',
      location: json['location'] != null 
          ? Map<String, dynamic>.from(json['location'])
          : null,
      riskLevel: json['risk_level'] ?? 'low',
      isMobile: json['is_mobile'] ?? false,
      device: json['device'] != null 
          ? Map<String, dynamic>.from(json['device'])
          : null,
      isCurrent: json['is_current'] ?? false,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'created_at': createdAt.toIso8601String(),
      'last_activity': lastActivity.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'ip_address': ipAddress,
      'location': location,
      'risk_level': riskLevel,
      'is_mobile': isMobile,
      'device': device,
      'is_current': isCurrent,
    };
  }
  
  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }
  
  Duration? get timeUntilExpiry {
    if (expiresAt == null) return null;
    final now = DateTime.now();
    if (now.isAfter(expiresAt!)) return Duration.zero;
    return expiresAt!.difference(now);
  }
  
  String get locationString {
    if (location == null || location!.isEmpty) {
      return 'Unknown Location';
    }
    
    final city = location!['city'] ?? '';
    final country = location!['country_name'] ?? location!['country'] ?? '';
    
    if (city.isNotEmpty && country.isNotEmpty) {
      return '$city, $country';
    } else if (country.isNotEmpty) {
      return country;
    } else {
      return 'Unknown Location';
    }
  }
  
  String get deviceString {
    if (device == null || device!.isEmpty) {
      return 'Unknown Device';
    }
    
    final deviceName = device!['device_name'] ?? '';
    final platform = device!['platform'] ?? '';
    
    if (deviceName.isNotEmpty) {
      return deviceName;
    } else if (platform.isNotEmpty) {
      return platform;
    } else {
      return 'Unknown Device';
    }
  }
  
  String get riskLevelDisplayName {
    switch (riskLevel.toLowerCase()) {
      case 'low':
        return 'Low Risk';
      case 'medium':
        return 'Medium Risk';
      case 'high':
        return 'High Risk';
      case 'critical':
        return 'Critical Risk';
      default:
        return riskLevel;
    }
  }
}
