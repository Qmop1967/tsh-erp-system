import 'package:json_annotation/json_annotation.dart';

part 'gps_location.g.dart';

/// GPS location data model for tracking salesperson movements
/// Critical for fraud prevention in $35K USD weekly money tracking
@JsonSerializable()
class GPSLocation {
  final int? id;
  final int salespersonId;
  final double latitude;
  final double longitude;
  final double? accuracy;
  final double? altitude;
  final double? speed;
  final String timestamp;
  final String? address;
  final int? customerId;
  final String? visitType; // 'customer_visit', 'in_transit', 'start_day', 'end_day'
  final String? notes;
  final bool isSynced;

  GPSLocation({
    this.id,
    required this.salespersonId,
    required this.latitude,
    required this.longitude,
    this.accuracy,
    this.altitude,
    this.speed,
    required this.timestamp,
    this.address,
    this.customerId,
    this.visitType,
    this.notes,
    this.isSynced = false,
  });

  factory GPSLocation.fromJson(Map<String, dynamic> json) =>
      _$GPSLocationFromJson(json);

  Map<String, dynamic> toJson() => _$GPSLocationToJson(this);

  GPSLocation copyWith({
    int? id,
    int? salespersonId,
    double? latitude,
    double? longitude,
    double? accuracy,
    double? altitude,
    double? speed,
    String? timestamp,
    String? address,
    int? customerId,
    String? visitType,
    String? notes,
    bool? isSynced,
  }) {
    return GPSLocation(
      id: id ?? this.id,
      salespersonId: salespersonId ?? this.salespersonId,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      accuracy: accuracy ?? this.accuracy,
      altitude: altitude ?? this.altitude,
      speed: speed ?? this.speed,
      timestamp: timestamp ?? this.timestamp,
      address: address ?? this.address,
      customerId: customerId ?? this.customerId,
      visitType: visitType ?? this.visitType,
      notes: notes ?? this.notes,
      isSynced: isSynced ?? this.isSynced,
    );
  }
}

/// Daily tracking summary
@JsonSerializable()
class DailyTrackingSummary {
  final String date;
  final int totalLocations;
  final double totalDistanceKm;
  final String startTime;
  final String? endTime;
  final int customerVisits;
  final String totalDuration;
  final List<GPSLocation> locations;

  DailyTrackingSummary({
    required this.date,
    required this.totalLocations,
    required this.totalDistanceKm,
    required this.startTime,
    this.endTime,
    required this.customerVisits,
    required this.totalDuration,
    required this.locations,
  });

  factory DailyTrackingSummary.fromJson(Map<String, dynamic> json) =>
      _$DailyTrackingSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$DailyTrackingSummaryToJson(this);
}
