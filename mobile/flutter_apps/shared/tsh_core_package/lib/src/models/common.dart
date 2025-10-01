import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'common.g.dart';

@JsonSerializable(genericArgumentFactories: true)
class ApiResponse<T> extends Equatable {
  final bool success;
  final String? message;
  final T? data;
  final String? error;
  final int? statusCode;

  const ApiResponse({
    required this.success,
    this.message,
    this.data,
    this.error,
    this.statusCode,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object? json) fromJsonT,
  ) =>
      _$ApiResponseFromJson(json, fromJsonT);

  Map<String, dynamic> toJson(Object? Function(T value) toJsonT) =>
      _$ApiResponseToJson(this, toJsonT);

  factory ApiResponse.success({T? data, String? message}) => ApiResponse(
        success: true,
        data: data,
        message: message,
      );

  factory ApiResponse.error({String? error, int? statusCode}) => ApiResponse(
        success: false,
        error: error,
        statusCode: statusCode,
      );

  @override
  List<Object?> get props => [success, message, data, error, statusCode];
}

@JsonSerializable(genericArgumentFactories: true)
class PaginatedResponse<T> extends Equatable {
  final List<T> items;
  final int total;
  final int page;
  final int perPage;
  final int totalPages;
  final bool hasNext;
  final bool hasPrevious;

  const PaginatedResponse({
    required this.items,
    required this.total,
    required this.page,
    required this.perPage,
    required this.totalPages,
    required this.hasNext,
    required this.hasPrevious,
  });

  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object? json) fromJsonT,
  ) =>
      _$PaginatedResponseFromJson(json, fromJsonT);

  Map<String, dynamic> toJson(Object? Function(T value) toJsonT) =>
      _$PaginatedResponseToJson(this, toJsonT);

  @override
  List<Object> get props => [items, total, page, perPage, totalPages, hasNext, hasPrevious];
}

@JsonSerializable()
class Address extends Equatable {
  final int? id;
  final String street;
  final String city;
  final String state;
  final String zipCode;
  final String country;
  final bool isDefault;
  final String? label; // e.g., "Home", "Office"

  const Address({
    this.id,
    required this.street,
    required this.city,
    required this.state,
    required this.zipCode,
    required this.country,
    this.isDefault = false,
    this.label,
  });

  factory Address.fromJson(Map<String, dynamic> json) => _$AddressFromJson(json);
  Map<String, dynamic> toJson() => _$AddressToJson(this);

  String get fullAddress => '$street, $city, $state $zipCode, $country';

  @override
  List<Object?> get props => [id, street, city, state, zipCode, country, isDefault, label];
}

@JsonSerializable()
class Contact extends Equatable {
  final int? id;
  final String? firstName;
  final String? lastName;
  final String? email;
  final String? phoneNumber;
  final String? company;
  final String? position;
  final Address? address;
  final Map<String, String>? customFields;

  const Contact({
    this.id,
    this.firstName,
    this.lastName,
    this.email,
    this.phoneNumber,
    this.company,
    this.position,
    this.address,
    this.customFields,
  });

  factory Contact.fromJson(Map<String, dynamic> json) => _$ContactFromJson(json);
  Map<String, dynamic> toJson() => _$ContactToJson(this);

  String get fullName {
    if (firstName == null && lastName == null) return '';
    return '${firstName ?? ''} ${lastName ?? ''}'.trim();
  }

  @override
  List<Object?> get props => [
        id,
        firstName,
        lastName,
        email,
        phoneNumber,
        company,
        position,
        address,
        customFields,
      ];
}

@JsonSerializable()
class FileUpload extends Equatable {
  final String fileName;
  final String fileUrl;
  final String mimeType;
  final int fileSize;
  final DateTime uploadedAt;

  const FileUpload({
    required this.fileName,
    required this.fileUrl,
    required this.mimeType,
    required this.fileSize,
    required this.uploadedAt,
  });

  factory FileUpload.fromJson(Map<String, dynamic> json) => _$FileUploadFromJson(json);
  Map<String, dynamic> toJson() => _$FileUploadToJson(this);

  String get fileSizeFormatted {
    if (fileSize < 1024) return '${fileSize}B';
    if (fileSize < 1024 * 1024) return '${(fileSize / 1024).toStringAsFixed(1)}KB';
    return '${(fileSize / (1024 * 1024)).toStringAsFixed(1)}MB';
  }

  @override
  List<Object> get props => [fileName, fileUrl, mimeType, fileSize, uploadedAt];
}

// Error handling
class AppException implements Exception {
  final String message;
  final int? statusCode;
  final String? details;

  const AppException(this.message, {this.statusCode, this.details});

  @override
  String toString() => 'AppException: $message${details != null ? ' ($details)' : ''}';
}

class NetworkException extends AppException {
  const NetworkException(super.message, {super.statusCode, super.details});
}

class AuthException extends AppException {
  const AuthException(super.message, {super.statusCode, super.details});
}

class ValidationException extends AppException {
  final Map<String, List<String>>? fieldErrors;

  const ValidationException(super.message, {super.statusCode, super.details, this.fieldErrors});
}

// Loading states
enum LoadingState {
  initial,
  loading,
  success,
  error,
}

// App configuration
class AppConfig {
  static const String appName = 'TSH ERP System';
  static const String version = '1.0.0';
  static const int defaultPageSize = 20;
  static const Duration defaultTimeout = Duration(seconds: 30);
  static const Duration cacheTimeout = Duration(hours: 1);
}
