// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AuthModel _$AuthModelFromJson(Map<String, dynamic> json) => AuthModel(
      token: json['token'] as String,
      user: UserModel.fromJson(json['user'] as Map<String, dynamic>),
      refreshToken: json['refreshToken'] as String?,
    );

Map<String, dynamic> _$AuthModelToJson(AuthModel instance) => <String, dynamic>{
      'token': instance.token,
      'user': instance.user,
      'refreshToken': instance.refreshToken,
    };

AuthResult _$AuthResultFromJson(Map<String, dynamic> json) => AuthResult(
      success: json['success'] as bool,
      userId: (json['userId'] as num?)?.toInt(),
      username: json['username'] as String?,
      sessionId: json['sessionId'] as String?,
      userDetails: json['userDetails'] as Map<String, dynamic>?,
      error: json['error'] as String?,
      errorCode: json['errorCode'] as String?,
    );

Map<String, dynamic> _$AuthResultToJson(AuthResult instance) =>
    <String, dynamic>{
      'success': instance.success,
      'userId': instance.userId,
      'username': instance.username,
      'sessionId': instance.sessionId,
      'userDetails': instance.userDetails,
      'error': instance.error,
      'errorCode': instance.errorCode,
    };

UserModel _$UserModelFromJson(Map<String, dynamic> json) => UserModel(
      id: (json['id'] as num).toInt(),
      name: json['name'] as String,
      email: json['email'] as String?,
      partnerId: (json['partnerId'] as num?)?.toInt(),
      groupIds: (json['groupIds'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList(),
      companyIds: (json['companyIds'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList(),
      phone: json['phone'] as String?,
      mobile: json['mobile'] as String?,
      image: json['image'] as String?,
      active: json['active'] as bool? ?? true,
      lastLogin: json['lastLogin'] == null
          ? null
          : DateTime.parse(json['lastLogin'] as String),
      timezone: json['timezone'] as String?,
      lang: json['lang'] as String?,
    );

Map<String, dynamic> _$UserModelToJson(UserModel instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'email': instance.email,
      'partnerId': instance.partnerId,
      'groupIds': instance.groupIds,
      'companyIds': instance.companyIds,
      'phone': instance.phone,
      'mobile': instance.mobile,
      'image': instance.image,
      'active': instance.active,
      'lastLogin': instance.lastLogin?.toIso8601String(),
      'timezone': instance.timezone,
      'lang': instance.lang,
    };

LoginRequest _$LoginRequestFromJson(Map<String, dynamic> json) => LoginRequest(
      username: json['username'] as String,
      password: json['password'] as String,
      database: json['database'] as String?,
      rememberMe: json['rememberMe'] as bool? ?? false,
    );

Map<String, dynamic> _$LoginRequestToJson(LoginRequest instance) =>
    <String, dynamic>{
      'username': instance.username,
      'password': instance.password,
      'database': instance.database,
      'rememberMe': instance.rememberMe,
    };

SessionInfo _$SessionInfoFromJson(Map<String, dynamic> json) => SessionInfo(
      userId: (json['userId'] as num).toInt(),
      username: json['username'] as String,
      sessionId: json['sessionId'] as String?,
      loginTime: DateTime.parse(json['loginTime'] as String),
      lastActivity: json['lastActivity'] == null
          ? null
          : DateTime.parse(json['lastActivity'] as String),
      context: json['context'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$SessionInfoToJson(SessionInfo instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'username': instance.username,
      'sessionId': instance.sessionId,
      'loginTime': instance.loginTime.toIso8601String(),
      'lastActivity': instance.lastActivity?.toIso8601String(),
      'context': instance.context,
    };
