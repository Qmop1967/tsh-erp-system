// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'gps_location.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GPSLocation _$GPSLocationFromJson(Map<String, dynamic> json) => GPSLocation(
      id: (json['id'] as num?)?.toInt(),
      salespersonId: (json['salespersonId'] as num).toInt(),
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracy: (json['accuracy'] as num?)?.toDouble(),
      altitude: (json['altitude'] as num?)?.toDouble(),
      speed: (json['speed'] as num?)?.toDouble(),
      timestamp: json['timestamp'] as String,
      address: json['address'] as String?,
      customerId: (json['customerId'] as num?)?.toInt(),
      visitType: json['visitType'] as String?,
      notes: json['notes'] as String?,
      isSynced: json['isSynced'] as bool? ?? false,
    );

Map<String, dynamic> _$GPSLocationToJson(GPSLocation instance) =>
    <String, dynamic>{
      'id': instance.id,
      'salespersonId': instance.salespersonId,
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'accuracy': instance.accuracy,
      'altitude': instance.altitude,
      'speed': instance.speed,
      'timestamp': instance.timestamp,
      'address': instance.address,
      'customerId': instance.customerId,
      'visitType': instance.visitType,
      'notes': instance.notes,
      'isSynced': instance.isSynced,
    };

DailyTrackingSummary _$DailyTrackingSummaryFromJson(
        Map<String, dynamic> json) =>
    DailyTrackingSummary(
      date: json['date'] as String,
      totalLocations: (json['totalLocations'] as num).toInt(),
      totalDistanceKm: (json['totalDistanceKm'] as num).toDouble(),
      startTime: json['startTime'] as String,
      endTime: json['endTime'] as String?,
      customerVisits: (json['customerVisits'] as num).toInt(),
      totalDuration: json['totalDuration'] as String,
      locations: (json['locations'] as List<dynamic>)
          .map((e) => GPSLocation.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$DailyTrackingSummaryToJson(
        DailyTrackingSummary instance) =>
    <String, dynamic>{
      'date': instance.date,
      'totalLocations': instance.totalLocations,
      'totalDistanceKm': instance.totalDistanceKm,
      'startTime': instance.startTime,
      'endTime': instance.endTime,
      'customerVisits': instance.customerVisits,
      'totalDuration': instance.totalDuration,
      'locations': instance.locations,
    };
