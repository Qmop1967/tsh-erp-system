class LocationDataModel {
  final double latitude;
  final double longitude;
  final double? accuracy;
  final String? address;
  final DateTime timestamp;
  final String? notes;

  LocationDataModel({
    required this.latitude,
    required this.longitude,
    this.accuracy,
    this.address,
    required this.timestamp,
    this.notes,
  });

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
      'accuracy': accuracy,
      'address': address,
      'timestamp': timestamp.toIso8601String(),
      'notes': notes,
    };
  }

  // Create from JSON
  factory LocationDataModel.fromJson(Map<String, dynamic> json) {
    return LocationDataModel(
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracy: (json['accuracy'] as num?)?.toDouble(),
      address: json['address'],
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      notes: json['notes'],
    );
  }

  // Create a copy with updated fields
  LocationDataModel copyWith({
    double? latitude,
    double? longitude,
    double? accuracy,
    String? address,
    DateTime? timestamp,
    String? notes,
  }) {
    return LocationDataModel(
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      accuracy: accuracy ?? this.accuracy,
      address: address ?? this.address,
      timestamp: timestamp ?? this.timestamp,
      notes: notes ?? this.notes,
    );
  }

  @override
  String toString() {
    return 'LocationDataModel(lat: $latitude, lon: $longitude, accuracy: $accuracy, address: $address)';
  }
}
