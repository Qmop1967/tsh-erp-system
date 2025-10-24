import 'package:flutter/material.dart';
import '../../services/user_management_service.dart';

/// Action Permissions Screen
/// Allows admins to manage CRUD permissions for users
class ActionPermissionsScreen extends StatefulWidget {
  final int userId;
  final String userName;

  const ActionPermissionsScreen({
    Key? key,
    required this.userId,
    required this.userName,
  }) : super(key: key);

  @override
  State<ActionPermissionsScreen> createState() =>
      _ActionPermissionsScreenState();
}

class _ActionPermissionsScreenState extends State<ActionPermissionsScreen> {
  final UserManagementService _service = UserManagementService();

  Map<String, Map<String, bool>> _permissions = {};
  bool _isLoading = true;
  bool _isSaving = false;
  final List<String> _actions = ['create', 'read', 'update', 'delete'];

  @override
  void initState() {
    super.initState();
    _loadActionPermissions();
  }

  Future<void> _loadActionPermissions() async {
    setState(() => _isLoading = true);
    try {
      final permissions =
          await _service.getUserActionPermissions(widget.userId);

      setState(() {
        _permissions = _parsePermissions(permissions);
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Failed to load action permissions: $e');
    }
  }

  Map<String, Map<String, bool>> _parsePermissions(
      Map<String, dynamic> data) {
    final Map<String, Map<String, bool>> parsed = {};

    // If empty, create default modules
    if (data.isEmpty) {
      final defaultModules = [
        'Dashboard',
        'Users',
        'Sales',
        'Customers',
        'Warehouse',
        'Accounting',
      ];

      for (var module in defaultModules) {
        parsed[module] = {
          'create': false,
          'read': false,
          'update': false,
          'delete': false,
        };
      }
      return parsed;
    }

    // Parse from API response
    data.forEach((module, actions) {
      if (actions is Map<String, dynamic>) {
        parsed[module] = {
          'create': actions['create'] ?? false,
          'read': actions['read'] ?? false,
          'update': actions['update'] ?? false,
          'delete': actions['delete'] ?? false,
        };
      }
    });

    return parsed;
  }

  Future<void> _savePermissions() async {
    setState(() => _isSaving = true);
    try {
      await _service.updateActionPermissions(widget.userId, _permissions);
      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Action permissions updated successfully'),
            backgroundColor: Color(0xFF10B981),
          ),
        );
      }
    } catch (e) {
      setState(() => _isSaving = false);
      _showError('Failed to save permissions: $e');
    }
  }

  void _togglePermission(String module, String action) {
    setState(() {
      _permissions[module]![action] = !_permissions[module]![action]!;
    });
  }

  void _toggleAllActions(String module, bool value) {
    setState(() {
      for (var action in _actions) {
        _permissions[module]![action] = value;
      }
    });
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFF2563EB),
        title: const Text(
          'Action Permissions',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          // User Info Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF2563EB),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                const Text(
                  'Managing CRUD permissions for:',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  widget.userName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),

          // Legend
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildLegendItem('Allowed', const Color(0xFF10B981)),
                const SizedBox(width: 24),
                _buildLegendItem('Denied', const Color(0xFFEF4444)),
              ],
            ),
          ),

          // Permissions List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _permissions.isEmpty
                    ? _buildEmptyState()
                    : _buildPermissionsList(),
          ),

          // Save Button
          if (!_isLoading)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 4,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: SafeArea(
                child: SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _isSaving ? null : _savePermissions,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isSaving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : const Text(
                            'Save Permissions',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[700],
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildPermissionsList() {
    final modules = _permissions.keys.toList()..sort();

    return RefreshIndicator(
      onRefresh: _loadActionPermissions,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: modules.length,
        itemBuilder: (context, index) {
          final module = modules[index];
          return _buildModuleCard(module);
        },
      ),
    );
  }

  Widget _buildModuleCard(String module) {
    final moduleColor = _getModuleColor(module);
    final allEnabled =
        _permissions[module]!.values.every((enabled) => enabled);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          childrenPadding: const EdgeInsets.all(16),
          leading: Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: moduleColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(_getModuleIcon(module), color: moduleColor, size: 24),
          ),
          title: Text(
            module,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: moduleColor,
            ),
          ),
          subtitle: Text(
            allEnabled ? 'All actions allowed' : 'Some actions restricted',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          trailing: Switch(
            value: allEnabled,
            onChanged: (value) => _toggleAllActions(module, value),
            activeColor: const Color(0xFF10B981),
          ),
          children: [
            _buildActionsList(module),
          ],
        ),
      ),
    );
  }

  Widget _buildActionsList(String module) {
    return Column(
      children: _actions.map((action) {
        final isAllowed = _permissions[module]![action]!;
        final actionColor = isAllowed ? const Color(0xFF10B981) : const Color(0xFFEF4444);

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: actionColor.withOpacity(0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: actionColor.withOpacity(0.2),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              // Action Icon
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: actionColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getActionIcon(action),
                  color: actionColor,
                  size: 20,
                ),
              ),
              const SizedBox(width: 16),

              // Action Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getActionLabel(action),
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: actionColor,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _getActionDescription(action, module),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),

              // Toggle Switch
              Switch(
                value: isAllowed,
                onChanged: (_) => _togglePermission(module, action),
                activeColor: const Color(0xFF10B981),
                inactiveThumbColor: const Color(0xFFEF4444),
                inactiveTrackColor: const Color(0xFFEF4444).withOpacity(0.3),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.lock_outline,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'No permissions configured',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Pull to refresh',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  String _getActionLabel(String action) {
    switch (action) {
      case 'create':
        return 'Create';
      case 'read':
        return 'Read';
      case 'update':
        return 'Update';
      case 'delete':
        return 'Delete';
      default:
        return action.toUpperCase();
    }
  }

  String _getActionDescription(String action, String module) {
    switch (action) {
      case 'create':
        return 'Can create new $module records';
      case 'read':
        return 'Can view $module records';
      case 'update':
        return 'Can modify existing $module records';
      case 'delete':
        return 'Can delete $module records';
      default:
        return 'Permission for $action action';
    }
  }

  IconData _getActionIcon(String action) {
    switch (action) {
      case 'create':
        return Icons.add_circle;
      case 'read':
        return Icons.visibility;
      case 'update':
        return Icons.edit;
      case 'delete':
        return Icons.delete;
      default:
        return Icons.lock;
    }
  }

  Color _getModuleColor(String module) {
    final moduleLower = module.toLowerCase();
    if (moduleLower.contains('dashboard')) return const Color(0xFF2563EB);
    if (moduleLower.contains('user')) return const Color(0xFF8B5CF6);
    if (moduleLower.contains('sales')) return const Color(0xFF10B981);
    if (moduleLower.contains('customer')) return const Color(0xFFF59E0B);
    if (moduleLower.contains('warehouse')) return const Color(0xFFEF4444);
    if (moduleLower.contains('accounting')) return const Color(0xFF2563EB);
    return const Color(0xFF6B7280);
  }

  IconData _getModuleIcon(String module) {
    final moduleLower = module.toLowerCase();
    if (moduleLower.contains('dashboard')) return Icons.dashboard;
    if (moduleLower.contains('user')) return Icons.people;
    if (moduleLower.contains('sales')) return Icons.shopping_cart;
    if (moduleLower.contains('customer')) return Icons.person;
    if (moduleLower.contains('warehouse')) return Icons.warehouse;
    if (moduleLower.contains('accounting')) return Icons.account_balance;
    return Icons.lock;
  }
}
