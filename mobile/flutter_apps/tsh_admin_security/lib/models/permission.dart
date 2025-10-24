/// Permission Model
class Permission {
  final int id;
  final String name;
  final String? description;
  final String resourceType;
  final String permissionType;
  final bool isActive;

  Permission({
    required this.id,
    required this.name,
    this.description,
    required this.resourceType,
    required this.permissionType,
    this.isActive = true,
  });

  factory Permission.fromJson(Map<String, dynamic> json) {
    return Permission(
      id: json['id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
      resourceType: json['resource_type'] as String,
      permissionType: json['permission_type'] as String,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'resource_type': resourceType,
      'permission_type': permissionType,
      'is_active': isActive,
    };
  }
}
