class UserDevice {
  final String deviceId;
  final String deviceName;
  final String deviceType;
  final String platform;
  final String status;
  final bool isTrusted;
  final DateTime firstSeen;
  final DateTime lastSeen;
  final String? lastIpAddress;
  final Map<String, dynamic>? lastLocation;
  
  UserDevice({
    required this.deviceId,
    required this.deviceName,
    required this.deviceType,
    required this.platform,
    required this.status,
    required this.isTrusted,
    required this.firstSeen,
    required this.lastSeen,
    this.lastIpAddress,
    this.lastLocation,
  });
  
  factory UserDevice.fromJson(Map<String, dynamic> json) {
    return UserDevice(
      deviceId: json['device_id'] ?? '',
      deviceName: json['device_name'] ?? '',
      deviceType: json['device_type'] ?? '',
      platform: json['platform'] ?? '',
      status: json['status'] ?? '',
      isTrusted: json['is_trusted'] ?? false,
      firstSeen: DateTime.tryParse(json['first_seen'] ?? '') ?? DateTime.now(),
      lastSeen: DateTime.tryParse(json['last_seen'] ?? '') ?? DateTime.now(),
      lastIpAddress: json['last_ip_address'],
      lastLocation: json['last_location'] != null 
          ? Map<String, dynamic>.from(json['last_location'])
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'device_id': deviceId,
      'device_name': deviceName,
      'device_type': deviceType,
      'platform': platform,
      'status': status,
      'is_trusted': isTrusted,
      'first_seen': firstSeen.toIso8601String(),
      'last_seen': lastSeen.toIso8601String(),
      'last_ip_address': lastIpAddress,
      'last_location': lastLocation,
    };
  }
  
  bool get isActive => status.toLowerCase() == 'active';
  bool get isPending => status.toLowerCase() == 'pending';
  bool get isBlocked => status.toLowerCase() == 'blocked';
  
  String get statusDisplayName {
    switch (status.toLowerCase()) {
      case 'active':
        return 'Active';
      case 'pending':
        return 'Pending Approval';
      case 'blocked':
        return 'Blocked';
      case 'suspended':
        return 'Suspended';
      default:
        return status;
    }
  }
  
  String get locationString {
    if (lastLocation == null || lastLocation!.isEmpty) {
      return 'Unknown Location';
    }
    
    final city = lastLocation!['city'] ?? '';
    final country = lastLocation!['country_name'] ?? lastLocation!['country'] ?? '';
    
    if (city.isNotEmpty && country.isNotEmpty) {
      return '$city, $country';
    } else if (country.isNotEmpty) {
      return country;
    } else {
      return 'Unknown Location';
    }
  }
}
