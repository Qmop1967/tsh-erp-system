class User {
  final String id;
  final String email;
  final String name;
  final String? fullName;
  final String? phone;
  final String? role;
  final String? branch;
  final List<String> permissions;
  final bool isActive;
  final DateTime? createdAt;

  User({
    required this.id,
    required this.email,
    required this.name,
    this.fullName,
    this.phone,
    this.role,
    this.branch,
    this.permissions = const [],
    this.isActive = true,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id']?.toString() ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? '',
      fullName: json['full_name'],
      phone: json['phone'],
      role: json['role'],
      branch: json['branch'],
      permissions: (json['permissions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      isActive: json['is_active'] ?? true,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'full_name': fullName,
      'phone': phone,
      'role': role,
      'branch': branch,
      'permissions': permissions,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  bool hasPermission(String permission) {
    return permissions.contains(permission);
  }

  bool hasAnyPermission(List<String> permissionList) {
    return permissionList.any((p) => permissions.contains(p));
  }

  bool hasAllPermissions(List<String> permissionList) {
    return permissionList.every((p) => permissions.contains(p));
  }
}
