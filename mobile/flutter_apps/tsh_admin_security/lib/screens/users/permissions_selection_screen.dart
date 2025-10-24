import 'package:flutter/material.dart';
import '../../services/user_management_service.dart';

/// Permissions Selection Screen
/// Allows admins to grant permissions to users
class PermissionsSelectionScreen extends StatefulWidget {
  final int userId;
  final String userName;

  const PermissionsSelectionScreen({
    Key? key,
    required this.userId,
    required this.userName,
  }) : super(key: key);

  @override
  State<PermissionsSelectionScreen> createState() =>
      _PermissionsSelectionScreenState();
}

class _PermissionsSelectionScreenState
    extends State<PermissionsSelectionScreen> {
  final UserManagementService _service = UserManagementService();
  final TextEditingController _searchController = TextEditingController();

  List<Map<String, dynamic>> _allPermissions = [];
  List<Map<String, dynamic>> _filteredPermissions = [];
  Set<int> _selectedPermissionIds = {};
  bool _isLoading = true;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _loadPermissions();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadPermissions() async {
    setState(() => _isLoading = true);
    try {
      final permissions = await _service.getAvailablePermissions();
      final userPermissions = await _service.getUserPermissions(widget.userId);

      // Mark user's current permissions as selected
      final currentPermissionIds =
          userPermissions.map((p) => p['id'] as int).toSet();

      setState(() {
        _allPermissions = permissions;
        _filteredPermissions = permissions;
        _selectedPermissionIds = currentPermissionIds;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Failed to load permissions: $e');
    }
  }

  void _filterPermissions(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredPermissions = _allPermissions;
      } else {
        _filteredPermissions = _allPermissions.where((permission) {
          final name = (permission['name'] ?? '').toLowerCase();
          final description = (permission['description'] ?? '').toLowerCase();
          final module = (permission['module'] ?? '').toLowerCase();
          final searchLower = query.toLowerCase();

          return name.contains(searchLower) ||
              description.contains(searchLower) ||
              module.contains(searchLower);
        }).toList();
      }
    });
  }

  Map<String, List<Map<String, dynamic>>> _groupPermissionsByModule() {
    final grouped = <String, List<Map<String, dynamic>>>{};

    for (var permission in _filteredPermissions) {
      final module = permission['module'] ?? 'Other';
      if (!grouped.containsKey(module)) {
        grouped[module] = [];
      }
      grouped[module]!.add(permission);
    }

    return grouped;
  }

  Future<void> _grantPermissions() async {
    if (_selectedPermissionIds.isEmpty) {
      _showError('Please select at least one permission');
      return;
    }

    setState(() => _isSaving = true);
    try {
      await _service.grantPermissions(
        widget.userId,
        _selectedPermissionIds.toList(),
      );
      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Permissions granted successfully'),
            backgroundColor: Color(0xFF10B981),
          ),
        );
      }
    } catch (e) {
      setState(() => _isSaving = false);
      _showError('Failed to grant permissions: $e');
    }
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
        backgroundColor: const Color(0xFF10B981),
        title: const Text(
          'Grant Permissions',
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
              color: const Color(0xFF10B981),
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
                  'Granting permissions to:',
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

          // Search Bar
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: TextField(
              controller: _searchController,
              onChanged: _filterPermissions,
              decoration: InputDecoration(
                hintText: 'Search permissions...',
                prefixIcon: const Icon(Icons.search, color: Color(0xFF10B981)),
                filled: true,
                fillColor: Colors.grey[100],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
            ),
          ),

          // Selected Count
          if (_selectedPermissionIds.isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: const Color(0xFF10B981).withOpacity(0.1),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Color(0xFF10B981)),
                  const SizedBox(width: 8),
                  Text(
                    '${_selectedPermissionIds.length} permissions selected',
                    style: const TextStyle(
                      color: Color(0xFF10B981),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),

          // Permissions List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredPermissions.isEmpty
                    ? _buildEmptyState()
                    : _buildPermissionsList(),
          ),

          // Grant Button
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
                    onPressed: _isSaving ? null : _grantPermissions,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
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
                            'Grant Permissions',
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

  Widget _buildPermissionsList() {
    final groupedPermissions = _groupPermissionsByModule();
    final modules = groupedPermissions.keys.toList()..sort();

    return RefreshIndicator(
      onRefresh: _loadPermissions,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: modules.length,
        itemBuilder: (context, index) {
          final module = modules[index];
          final permissions = groupedPermissions[module]!;
          return _buildModuleSection(module, permissions);
        },
      ),
    );
  }

  Widget _buildModuleSection(
    String module,
    List<Map<String, dynamic>> permissions,
  ) {
    final moduleColor = _getModuleColor(module);

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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Module Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: moduleColor.withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                Icon(_getModuleIcon(module), color: moduleColor, size: 24),
                const SizedBox(width: 12),
                Text(
                  module,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: moduleColor,
                  ),
                ),
                const Spacer(),
                Text(
                  '${permissions.length} permissions',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),

          // Permissions List
          ...permissions.map((permission) => _buildPermissionItem(permission)),
        ],
      ),
    );
  }

  Widget _buildPermissionItem(Map<String, dynamic> permission) {
    final permissionId = permission['id'] as int;
    final isSelected = _selectedPermissionIds.contains(permissionId);
    final permissionType = permission['type'] ?? 'direct';
    final typeColor =
        permissionType == 'role' ? const Color(0xFF8B5CF6) : const Color(0xFF10B981);

    return InkWell(
      onTap: () {
        setState(() {
          if (isSelected) {
            _selectedPermissionIds.remove(permissionId);
          } else {
            _selectedPermissionIds.add(permissionId);
          }
        });
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(color: Colors.grey[200]!),
          ),
        ),
        child: Row(
          children: [
            // Checkbox
            Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                color: isSelected ? const Color(0xFF10B981) : Colors.transparent,
                border: Border.all(
                  color: isSelected ? const Color(0xFF10B981) : Colors.grey[400]!,
                  width: 2,
                ),
                borderRadius: BorderRadius.circular(6),
              ),
              child: isSelected
                  ? const Icon(Icons.check, color: Colors.white, size: 16)
                  : null,
            ),
            const SizedBox(width: 12),

            // Permission Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          permission['name'] ?? 'Unknown',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1F2937),
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: typeColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          permissionType.toUpperCase(),
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: typeColor,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (permission['description'] != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      permission['description'],
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.lock_open,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'No permissions found',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _searchController.text.isEmpty
                ? 'No permissions available'
                : 'Try a different search term',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
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
    return Icons.lock_open;
  }
}
