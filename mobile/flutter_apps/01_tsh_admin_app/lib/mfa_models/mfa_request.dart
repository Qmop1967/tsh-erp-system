class MFARequest {
  final String requestId;
  final String description;
  final String ipAddress;
  final Map<String, dynamic> location;
  final String userAgent;
  final String riskLevel;
  final DateTime timestamp;
  final DateTime expiresAt;
  
  MFARequest({
    required this.requestId,
    required this.description,
    required this.ipAddress,
    required this.location,
    required this.userAgent,
    required this.riskLevel,
    required this.timestamp,
    required this.expiresAt,
  });
  
  factory MFARequest.fromJson(Map<String, dynamic> json) {
    return MFARequest(
      requestId: json['request_id'] ?? '',
      description: json['description'] ?? '',
      ipAddress: json['ip_address'] ?? '',
      location: Map<String, dynamic>.from(json['location'] ?? {}),
      userAgent: json['user_agent'] ?? '',
      riskLevel: json['risk_level'] ?? 'medium',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
      expiresAt: DateTime.tryParse(json['expires_at'] ?? '') ?? DateTime.now().add(const Duration(minutes: 5)),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'request_id': requestId,
      'description': description,
      'ip_address': ipAddress,
      'location': location,
      'user_agent': userAgent,
      'risk_level': riskLevel,
      'timestamp': timestamp.toIso8601String(),
      'expires_at': expiresAt.toIso8601String(),
    };
  }
  
  bool get isExpired => DateTime.now().isAfter(expiresAt);
  
  Duration get timeRemaining {
    final now = DateTime.now();
    if (now.isAfter(expiresAt)) {
      return Duration.zero;
    }
    return expiresAt.difference(now);
  }
  
  String get locationString {
    if (location.isEmpty) return 'Unknown Location';
    
    final city = location['city'] ?? '';
    final country = location['country_name'] ?? location['country'] ?? '';
    
    if (city.isNotEmpty && country.isNotEmpty) {
      return '$city, $country';
    } else if (country.isNotEmpty) {
      return country;
    } else {
      return 'Unknown Location';
    }
  }
}
