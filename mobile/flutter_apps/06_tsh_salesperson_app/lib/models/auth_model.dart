import 'package:json_annotation/json_annotation.dart';

part 'auth_model.g.dart';

@JsonSerializable()
class AuthResult {
  final bool success;
  final int? userId;
  final String? username;
  final String? sessionId;
  final Map<String, dynamic>? userDetails;
  final String? error;
  final String? errorCode;
  
  const AuthResult({
    required this.success,
    this.userId,
    this.username,
    this.sessionId,
    this.userDetails,
    this.error,
    this.errorCode,
  });
  
  factory AuthResult.fromJson(Map<String, dynamic> json) => 
      _$AuthResultFromJson(json);
  
  Map<String, dynamic> toJson() => _$AuthResultToJson(this);
  
  AuthResult copyWith({
    bool? success,
    int? userId,
    String? username,
    String? sessionId,
    Map<String, dynamic>? userDetails,
    String? error,
    String? errorCode,
  }) {
    return AuthResult(
      success: success ?? this.success,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      sessionId: sessionId ?? this.sessionId,
      userDetails: userDetails ?? this.userDetails,
      error: error ?? this.error,
      errorCode: errorCode ?? this.errorCode,
    );
  }
  
  @override
  String toString() {
    return 'AuthResult{success: $success, userId: $userId, username: $username}';
  }
}

@JsonSerializable()
class UserModel {
  final int id;
  final String name;
  final String? email;
  final int? partnerId;
  final List<int>? groupIds;
  final List<int>? companyIds;
  final String? phone;
  final String? mobile;
  final String? image;
  final bool active;
  final DateTime? lastLogin;
  final String? timezone;
  final String? lang;
  final String? role;
  final List<String>? permissions;
  
  const UserModel({
    required this.id,
    required this.name,
    this.email,
    this.partnerId,
    this.groupIds,
    this.companyIds,
    this.phone,
    this.mobile,
    this.image,
    this.active = true,
    this.lastLogin,
    this.timezone,
    this.lang,
    this.role,
    this.permissions,
  });
  
  factory UserModel.fromJson(Map<String, dynamic> json) => 
      _$UserModelFromJson(json);
  
  Map<String, dynamic> toJson() => _$UserModelToJson(this);
  
  String get displayName => name;
  String get initials {
    final parts = name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }
  
  @override
  String toString() => 'UserModel{id: $id, name: $name, email: $email}';
}

// Alias for backward compatibility
typedef AuthModel = UserModel;

@JsonSerializable()
class LoginRequest {
  final String username;
  final String password;
  final String? database;
  final bool rememberMe;
  
  const LoginRequest({
    required this.username,
    required this.password,
    this.database,
    this.rememberMe = false,
  });
  
  factory LoginRequest.fromJson(Map<String, dynamic> json) => 
      _$LoginRequestFromJson(json);
  
  Map<String, dynamic> toJson() => _$LoginRequestToJson(this);
}

@JsonSerializable()
class SessionInfo {
  final int userId;
  final String username;
  final String? sessionId;
  final DateTime loginTime;
  final DateTime? lastActivity;
  final Map<String, dynamic>? context;
  
  const SessionInfo({
    required this.userId,
    required this.username,
    this.sessionId,
    required this.loginTime,
    this.lastActivity,
    this.context,
  });
  
  factory SessionInfo.fromJson(Map<String, dynamic> json) => 
      _$SessionInfoFromJson(json);
  
  Map<String, dynamic> toJson() => _$SessionInfoToJson(this);
  
  bool get isExpired {
    if (lastActivity == null) return false;
    final expiry = lastActivity!.add(const Duration(hours: 8));
    return DateTime.now().isAfter(expiry);
  }
  
  Duration get sessionDuration {
    final end = lastActivity ?? DateTime.now();
    return end.difference(loginTime);
  }
}