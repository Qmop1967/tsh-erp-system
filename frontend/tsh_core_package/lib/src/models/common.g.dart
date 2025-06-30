// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'common.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ApiResponse<T> _$ApiResponseFromJson<T>(
  Map<String, dynamic> json,
  T Function(Object? json) fromJsonT,
) => ApiResponse<T>(
  success: json['success'] as bool,
  message: json['message'] as String?,
  data: _$nullableGenericFromJson(json['data'], fromJsonT),
  error: json['error'] as String?,
  statusCode: (json['statusCode'] as num?)?.toInt(),
);

Map<String, dynamic> _$ApiResponseToJson<T>(
  ApiResponse<T> instance,
  Object? Function(T value) toJsonT,
) => <String, dynamic>{
  'success': instance.success,
  'message': instance.message,
  'data': _$nullableGenericToJson(instance.data, toJsonT),
  'error': instance.error,
  'statusCode': instance.statusCode,
};

T? _$nullableGenericFromJson<T>(
  Object? input,
  T Function(Object? json) fromJson,
) => input == null ? null : fromJson(input);

Object? _$nullableGenericToJson<T>(
  T? input,
  Object? Function(T value) toJson,
) => input == null ? null : toJson(input);

PaginatedResponse<T> _$PaginatedResponseFromJson<T>(
  Map<String, dynamic> json,
  T Function(Object? json) fromJsonT,
) => PaginatedResponse<T>(
  items: (json['items'] as List<dynamic>).map(fromJsonT).toList(),
  total: (json['total'] as num).toInt(),
  page: (json['page'] as num).toInt(),
  perPage: (json['perPage'] as num).toInt(),
  totalPages: (json['totalPages'] as num).toInt(),
  hasNext: json['hasNext'] as bool,
  hasPrevious: json['hasPrevious'] as bool,
);

Map<String, dynamic> _$PaginatedResponseToJson<T>(
  PaginatedResponse<T> instance,
  Object? Function(T value) toJsonT,
) => <String, dynamic>{
  'items': instance.items.map(toJsonT).toList(),
  'total': instance.total,
  'page': instance.page,
  'perPage': instance.perPage,
  'totalPages': instance.totalPages,
  'hasNext': instance.hasNext,
  'hasPrevious': instance.hasPrevious,
};

Address _$AddressFromJson(Map<String, dynamic> json) => Address(
  id: (json['id'] as num?)?.toInt(),
  street: json['street'] as String,
  city: json['city'] as String,
  state: json['state'] as String,
  zipCode: json['zipCode'] as String,
  country: json['country'] as String,
  isDefault: json['isDefault'] as bool? ?? false,
  label: json['label'] as String?,
);

Map<String, dynamic> _$AddressToJson(Address instance) => <String, dynamic>{
  'id': instance.id,
  'street': instance.street,
  'city': instance.city,
  'state': instance.state,
  'zipCode': instance.zipCode,
  'country': instance.country,
  'isDefault': instance.isDefault,
  'label': instance.label,
};

Contact _$ContactFromJson(Map<String, dynamic> json) => Contact(
  id: (json['id'] as num?)?.toInt(),
  firstName: json['firstName'] as String?,
  lastName: json['lastName'] as String?,
  email: json['email'] as String?,
  phoneNumber: json['phoneNumber'] as String?,
  company: json['company'] as String?,
  position: json['position'] as String?,
  address: json['address'] == null
      ? null
      : Address.fromJson(json['address'] as Map<String, dynamic>),
  customFields: (json['customFields'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
);

Map<String, dynamic> _$ContactToJson(Contact instance) => <String, dynamic>{
  'id': instance.id,
  'firstName': instance.firstName,
  'lastName': instance.lastName,
  'email': instance.email,
  'phoneNumber': instance.phoneNumber,
  'company': instance.company,
  'position': instance.position,
  'address': instance.address,
  'customFields': instance.customFields,
};

FileUpload _$FileUploadFromJson(Map<String, dynamic> json) => FileUpload(
  fileName: json['fileName'] as String,
  fileUrl: json['fileUrl'] as String,
  mimeType: json['mimeType'] as String,
  fileSize: (json['fileSize'] as num).toInt(),
  uploadedAt: DateTime.parse(json['uploadedAt'] as String),
);

Map<String, dynamic> _$FileUploadToJson(FileUpload instance) =>
    <String, dynamic>{
      'fileName': instance.fileName,
      'fileUrl': instance.fileUrl,
      'mimeType': instance.mimeType,
      'fileSize': instance.fileSize,
      'uploadedAt': instance.uploadedAt.toIso8601String(),
    };
