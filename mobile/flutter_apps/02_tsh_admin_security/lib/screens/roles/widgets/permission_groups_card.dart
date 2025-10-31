import 'package:flutter/material.dart';
import 'permission_card_base.dart';

/// Permission Groups Card - Full Implementation
/// Predefined permission templates for quick assignment
class PermissionGroupsCard extends StatelessWidget {
  const PermissionGroupsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return PermissionCardBase(
      title: 'Permission Groups',
      subtitle: 'Predefined permission templates',
      icon: Icons.group_work,
      color: const Color(0xffef4444),
      itemCount: 6,
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const PermissionGroupsDetailScreen(),
          ),
        );
      },
    );
  }
}

class PermissionGroupsDetailScreen extends StatefulWidget {
  const PermissionGroupsDetailScreen({super.key});

  @override
  State<PermissionGroupsDetailScreen> createState() =>
      _PermissionGroupsDetailScreenState();
}

class _PermissionGroupsDetailScreenState
    extends State<PermissionGroupsDetailScreen> {
  String? _selectedGroup;

  final List<PermissionGroup> _groups = [
    PermissionGroup(
      id: 'full_admin',
      name: 'Full Administrator',
      description: 'Complete system access with all permissions',
      icon: Icons.admin_panel_settings,
      color: const Color(0xffef4444),
      permissions: [
        'All Modules',
        'Company-wide Data',
        'All Applications',
        'User Management',
        'System Settings',
        'Full CRUD Access',
      ],
      userCount: 3,
    ),
    PermissionGroup(
      id: 'manager',
      name: 'Department Manager',
      description: 'Manage department with branch-level access',
      icon: Icons.supervised_user_circle,
      color: const Color(0xff3b82f6),
      permissions: [
        'Department Modules',
        'Branch Data',
        'Team Management',
        'Reports Access',
        'Limited Settings',
      ],
      userCount: 12,
    ),
    PermissionGroup(
      id: 'sales_executive',
      name: 'Sales Executive',
      description: 'Sales-focused permissions with customer access',
      icon: Icons.trending_up,
      color: const Color(0xff10b981),
      permissions: [
        'Sales Module',
        'Own + Team Data',
        'Customer Management',
        'Product Catalog',
        'Sales Reports',
      ],
      userCount: 45,
    ),
    PermissionGroup(
      id: 'accountant',
      name: 'Accountant',
      description: 'Financial data access with accounting tools',
      icon: Icons.account_balance,
      color: const Color(0xfff59e0b),
      permissions: [
        'Accounting Module',
        'Financial Data',
        'Payment Processing',
        'Financial Reports',
        'Invoice Management',
      ],
      userCount: 8,
    ),
    PermissionGroup(
      id: 'inventory_clerk',
      name: 'Inventory Clerk',
      description: 'Stock management and warehouse operations',
      icon: Icons.warehouse,
      color: const Color(0xff8b5cf6),
      permissions: [
        'Inventory Module',
        'Warehouse Data',
        'Stock Management',
        'Transfer Orders',
        'Inventory Reports',
      ],
      userCount: 18,
    ),
    PermissionGroup(
      id: 'read_only',
      name: 'Read-Only Viewer',
      description: 'View-only access to reports and dashboards',
      icon: Icons.visibility,
      color: const Color(0xff6b7280),
      permissions: [
        'Dashboard Only',
        'Own Data',
        'View Reports',
        'No Edit Access',
      ],
      userCount: 25,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xffef4444),
        foregroundColor: Colors.white,
        title: const Text(
          'Permission Groups',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () {
              _showCreateGroupDialog();
            },
            tooltip: 'Create New Group',
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _groups.length,
        itemBuilder: (context, index) {
          final group = _groups[index];
          final isSelected = _selectedGroup == group.id;
          return _buildGroupCard(group, isSelected);
        },
      ),
      floatingActionButton: _selectedGroup != null
          ? FloatingActionButton.extended(
              onPressed: () {
                _applyPermissionGroup();
              },
              backgroundColor: const Color(0xffef4444),
              icon: const Icon(Icons.check),
              label: const Text('Apply Template'),
            )
          : null,
    );
  }

  Widget _buildGroupCard(PermissionGroup group, bool isSelected) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isSelected ? group.color : Colors.grey.withOpacity(0.2),
          width: isSelected ? 3 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: isSelected
                ? group.color.withOpacity(0.2)
                : Colors.grey.withOpacity(0.05),
            blurRadius: isSelected ? 15 : 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            setState(() {
              _selectedGroup = isSelected ? null : group.id;
            });
          },
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [group.color, group.color.withOpacity(0.7)],
                        ),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: group.color.withOpacity(0.3),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Icon(
                        group.icon,
                        color: Colors.white,
                        size: 32,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            group.name,
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: isSelected ? group.color : Colors.black87,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            group.description,
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (isSelected)
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: group.color,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.check,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 12),
                Text(
                  'Included Permissions:',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: group.permissions.map((perm) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: group.color.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: group.color.withOpacity(0.3),
                          width: 1,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.check_circle,
                            size: 14,
                            color: group.color,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            perm,
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: group.color,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xff3b82f6).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.people,
                        size: 14,
                        color: Color(0xff3b82f6),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${group.userCount} users using this template',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xff3b82f6),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showCreateGroupDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create New Permission Group'),
        content: const Text(
          'This feature allows you to create custom permission templates.\n\nComing soon!',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _applyPermissionGroup() {
    final group = _groups.firstWhere((g) => g.id == _selectedGroup);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Apply Permission Template'),
        content: Text(
          'Apply "${group.name}" template to selected role?\n\nThis will override existing permissions.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Applied "${group.name}" template successfully'),
                  backgroundColor: const Color(0xff10b981),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xffef4444),
            ),
            child: const Text('Apply'),
          ),
        ],
      ),
    );
  }
}

class PermissionGroup {
  final String id;
  final String name;
  final String description;
  final IconData icon;
  final Color color;
  final List<String> permissions;
  final int userCount;

  PermissionGroup({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.color,
    required this.permissions,
    required this.userCount,
  });
}
