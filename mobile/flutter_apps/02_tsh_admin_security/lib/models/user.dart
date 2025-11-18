/// User Model - Matches backend User model
class User {
  final int id;
  final String email;
  final String? name;
  final String? employeeCode;
  final String? phone;
  final bool isActive;
  final bool isSalesperson;
  final int? roleId;
  final String? roleName;
  final int? branchId;
  final String? branchName;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final DateTime? lastLogin;
  final List<String> permissions;

  // Zoho sync fields
  final String? zohoUserId;
  final DateTime? zohoLastSync;

  User({
    required this.id,
    required this.email,
    this.name,
    this.employeeCode,
    this.phone,
    this.isActive = true,
    this.isSalesperson = false,
    this.roleId,
    this.roleName,
    this.branchId,
    this.branchName,
    this.createdAt,
    this.updatedAt,
    this.lastLogin,
    this.permissions = const [],
    this.zohoUserId,
    this.zohoLastSync,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      email: json['email'] as String,
      name: json['name'] as String?,
      employeeCode: json['employee_code'] as String?,
      phone: json['phone'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      isSalesperson: json['is_salesperson'] as bool? ?? false,
      roleId: json['role_id'] as int?,
      roleName: json['role_name'] as String? ?? json['role'] as String?,
      branchId: json['branch_id'] as int?,
      branchName: json['branch_name'] as String? ?? json['branch'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      lastLogin: json['last_login'] != null
          ? DateTime.parse(json['last_login'] as String)
          : null,
      permissions: json['permissions'] != null
          ? List<String>.from(json['permissions'] as List)
          : [],
      zohoUserId: json['zoho_user_id'] as String?,
      zohoLastSync: json['zoho_last_sync'] != null
          ? DateTime.parse(json['zoho_last_sync'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'employee_code': employeeCode,
      'phone': phone,
      'is_active': isActive,
      'is_salesperson': isSalesperson,
      'role_id': roleId,
      'role_name': roleName,
      'branch_id': branchId,
      'branch_name': branchName,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
      'permissions': permissions,
      'zoho_user_id': zohoUserId,
      'zoho_last_sync': zohoLastSync?.toIso8601String(),
    };
  }

  String get displayName => name ?? email;

  User copyWith({
    int? id,
    String? email,
    String? name,
    String? employeeCode,
    String? phone,
    bool? isActive,
    bool? isSalesperson,
    int? roleId,
    String? roleName,
    int? branchId,
    String? branchName,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastLogin,
    List<String>? permissions,
    String? zohoUserId,
    DateTime? zohoLastSync,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      employeeCode: employeeCode ?? this.employeeCode,
      phone: phone ?? this.phone,
      isActive: isActive ?? this.isActive,
      isSalesperson: isSalesperson ?? this.isSalesperson,
      roleId: roleId ?? this.roleId,
      roleName: roleName ?? this.roleName,
      branchId: branchId ?? this.branchId,
      branchName: branchName ?? this.branchName,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLogin: lastLogin ?? this.lastLogin,
      permissions: permissions ?? this.permissions,
      zohoUserId: zohoUserId ?? this.zohoUserId,
      zohoLastSync: zohoLastSync ?? this.zohoLastSync,
    );
  }

  /// Check if user is synced with Zoho
  bool get isSyncedWithZoho => zohoUserId != null && zohoUserId!.isNotEmpty;

  /// Get sync status message
  String get syncStatusMessage {
    if (!isSyncedWithZoho) return 'Not synced with Zoho';
    if (zohoLastSync == null) return 'Synced (no timestamp)';

    final now = DateTime.now();
    final difference = now.difference(zohoLastSync!);

    if (difference.inMinutes < 60) {
      return 'Synced ${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return 'Synced ${difference.inHours}h ago';
    } else {
      return 'Synced ${difference.inDays}d ago';
    }
  }
}

/// Login Response from backend
class LoginResponse {
  final String accessToken;
  final String tokenType;
  final User user;
  final bool requiresMfa;
  final String? mfaMethod;

  LoginResponse({
    required this.accessToken,
    required this.tokenType,
    required this.user,
    this.requiresMfa = false,
    this.mfaMethod,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
      user: User.fromJson(json['user'] as Map<String, dynamic>),
      requiresMfa: json['requires_mfa'] as bool? ?? false,
      mfaMethod: json['mfa_method'] as String?,
    );
  }
}
