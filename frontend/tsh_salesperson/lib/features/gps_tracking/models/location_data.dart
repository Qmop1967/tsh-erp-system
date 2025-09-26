import 'dart:convert';
import 'package:equatable/equatable.dart';

class LocationData extends Equatable {
  final double latitude;
  final double longitude;
  final double accuracy;
  final String? address;
  final DateTime timestamp;
  final double? speed;
  final double? heading;
  final bool isLastKnown;

  const LocationData({
    required this.latitude,
    required this.longitude,
    required this.accuracy,
    this.address,
    required this.timestamp,
    this.speed,
    this.heading,
    this.isLastKnown = false,
  });

  factory LocationData.fromJson(String jsonString) {
    final Map<String, dynamic> json = jsonDecode(jsonString);
    return LocationData(
      latitude: json['latitude'],
      longitude: json['longitude'],
      accuracy: json['accuracy'],
      address: json['address'],
      timestamp: DateTime.parse(json['timestamp']),
      speed: json['speed'],
      heading: json['heading'],
      isLastKnown: json['isLastKnown'] ?? false,
    );
  }

  String toJson() {
    return jsonEncode({
      'latitude': latitude,
      'longitude': longitude,
      'accuracy': accuracy,
      'address': address,
      'timestamp': timestamp.toIso8601String(),
      'speed': speed,
      'heading': heading,
      'isLastKnown': isLastKnown,
    });
  }

  Map<String, dynamic> toMap() {
    return {
      'latitude': latitude,
      'longitude': longitude,
      'accuracy': accuracy,
      'address': address,
      'timestamp': timestamp.toIso8601String(),
      'speed': speed,
      'heading': heading,
      'isLastKnown': isLastKnown,
    };
  }

  String get coordinatesString => '$latitude, $longitude';
  
  String get accuracyText => '${accuracy.toStringAsFixed(1)}m';

  @override
  List<Object?> get props => [
        latitude,
        longitude,
        accuracy,
        address,
        timestamp,
        speed,
        heading,
        isLastKnown,
      ];
} 