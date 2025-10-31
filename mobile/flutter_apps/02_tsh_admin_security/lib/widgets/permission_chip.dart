import 'package:flutter/material.dart';

/// Permission Chip Widget
/// Displays a permission with visual indicators for source and status
class PermissionChip extends StatelessWidget {
  final Permission permission;
  final bool showSource;
  final VoidCallback? onTap;
  final VoidCallback? onDelete;

  const PermissionChip({
    Key? key,
    required this.permission,
    this.showSource = false,
    this.onTap,
    this.onDelete,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isDirect = permission.source == 'direct';
    final color = isDirect ? Colors.green : Colors.purple;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isDirect ? Icons.person : Icons.badge,
                size: 16,
                color: color,
              ),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  permission.name,
                  style: TextStyle(
                    fontSize: 13,
                    color: color.withOpacity(0.9),
                    fontWeight: FontWeight.w500,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (showSource) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    isDirect ? 'Direct' : 'Role',
                    style: TextStyle(
                      fontSize: 10,
                      color: color,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
              if (onDelete != null) ...[
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: onDelete,
                  child: Icon(
                    Icons.cancel,
                    size: 16,
                    color: Colors.red.withOpacity(0.7),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Permission Model
class Permission {
  final String name;
  final String? description;
  final String? module;
  final String source; // 'direct' or 'role'
  final bool isActive;

  Permission({
    required this.name,
    this.description,
    this.module,
    required this.source,
    this.isActive = true,
  });

  factory Permission.fromJson(Map<String, dynamic> json) {
    return Permission(
      name: json['name'] as String,
      description: json['description'] as String?,
      module: json['module'] as String?,
      source: json['source'] as String? ?? 'role',
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'description': description,
      'module': module,
      'source': source,
      'is_active': isActive,
    };
  }
}
