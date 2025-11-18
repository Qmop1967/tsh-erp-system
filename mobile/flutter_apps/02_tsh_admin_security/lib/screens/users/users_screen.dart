import 'package:flutter/material.dart';
import '../../models/user.dart';
import '../../services/user_service.dart';
import '../../config/api_config.dart';
import 'user_detail_screen.dart';
import 'user_management_screen.dart';

class UsersScreen extends StatefulWidget {
  const UsersScreen({super.key});

  @override
  State<UsersScreen> createState() => _UsersScreenState();
}

class _UsersScreenState extends State<UsersScreen> {
  final UserService _userService = UserService();
  List<User> _users = [];
  bool _isLoading = true;
  bool _isLoadingAll = false;
  String _searchQuery = '';
  bool? _activeFilter;
  int _totalUsers = 0;
  bool _showAllUsers = false; // Toggle between paginated and all users

  @override
  void initState() {
    super.initState();
    _loadUsers();
  }

  /// Load users (paginated by default)
  Future<void> _loadUsers({bool loadAll = false}) async {
    setState(() {
      _isLoading = !loadAll;
      _isLoadingAll = loadAll;
      _showAllUsers = loadAll;
    });
    
    try {
      if (loadAll) {
        // Load ALL users from database
        final users = await _userService.getAllUsers(
          search: _searchQuery.isNotEmpty ? _searchQuery : null,
          isActive: _activeFilter,
        );
        setState(() {
          _users = users;
          _totalUsers = users.length;
          _isLoadingAll = false;
        });
      } else {
        // Load paginated users
        final response = await _userService.getUsersPaginated(
          page: 1,
          pageSize: 20,
          search: _searchQuery.isNotEmpty ? _searchQuery : null,
          isActive: _activeFilter,
        );
        setState(() {
          _users = response.users;
          _totalUsers = response.total;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _isLoadingAll = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading users: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _deleteUser(User user) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete User'),
        content: Text('Are you sure you want to delete ${user.displayName}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await _userService.deleteUser(user.id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('User deleted successfully'),
              backgroundColor: Colors.green,
            ),
          );
          _loadUsers();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error deleting user: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  /// Toggle user active/inactive status
  Future<void> _toggleUserStatus(User user, {required bool activate}) async {
    try {
      final updatedUser = activate
          ? await _userService.activateUser(user.id)
          : await _userService.deactivateUser(user.id);
      
      // Update local state
      setState(() {
        final index = _users.indexWhere((u) => u.id == user.id);
        if (index != -1) {
          _users[index] = updatedUser;
        }
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              activate
                  ? 'User activated successfully'
                  : 'User deactivated successfully',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter Users'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: const Text('All Users'),
              leading: Radio<bool?>(
                value: null,
                groupValue: _activeFilter,
                onChanged: (value) {
                  setState(() => _activeFilter = value);
                  Navigator.pop(context);
                  _loadUsers(loadAll: _showAllUsers);
                },
              ),
            ),
            ListTile(
              title: const Text('Active Only'),
              leading: Radio<bool?>(
                value: true,
                groupValue: _activeFilter,
                onChanged: (value) {
                  setState(() => _activeFilter = value);
                  Navigator.pop(context);
                  _loadUsers(loadAll: _showAllUsers);
                },
              ),
            ),
            ListTile(
              title: const Text('Inactive Only'),
              leading: Radio<bool?>(
                value: false,
                groupValue: _activeFilter,
                onChanged: (value) {
                  setState(() => _activeFilter = value);
                  Navigator.pop(context);
                  _loadUsers(loadAll: _showAllUsers);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xff2563eb),
        foregroundColor: Colors.white,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'User Management',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            Text(
              'Environment: ${ApiConfig.environmentName}',
              style: TextStyle(
                fontSize: 11,
                color: Colors.white.withOpacity(0.8),
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
            tooltip: 'Filter',
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            onSelected: (value) {
              if (value == 'load_all') {
                _loadUsers(loadAll: true);
              } else if (value == 'load_paginated') {
                _loadUsers(loadAll: false);
              } else if (value == 'refresh') {
                _loadUsers(loadAll: _showAllUsers);
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'load_all',
                child: Row(
                  children: [
                    const Icon(Icons.cloud_download, size: 20),
                    const SizedBox(width: 8),
                    Text(_showAllUsers ? '✓ Load All Users' : 'Load All Users'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'load_paginated',
                child: Row(
                  children: [
                    const Icon(Icons.list, size: 20),
                    const SizedBox(width: 8),
                    Text(_showAllUsers ? 'Load Paginated' : '✓ Load Paginated'),
                  ],
                ),
              ),
              const PopupMenuDivider(),
              const PopupMenuItem(
                value: 'refresh',
                child: Row(
                  children: [
                    Icon(Icons.refresh, size: 20),
                    SizedBox(width: 8),
                    Text('Refresh'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Container(
            color: const Color(0xff2563eb),
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: TextField(
              onChanged: (value) {
                setState(() => _searchQuery = value);
                _loadUsers(loadAll: _showAllUsers);
              },
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Search users...',
                hintStyle: TextStyle(color: Colors.white.withOpacity(0.7)),
                prefixIcon: const Icon(Icons.search, color: Colors.white),
                filled: true,
                fillColor: Colors.white.withOpacity(0.2),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),

          // Users Count & Status
          if (!_isLoading && !_isLoadingAll)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Colors.white,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _showAllUsers
                        ? 'Showing ALL $_totalUsers users'
                        : 'Showing ${_users.length} of $_totalUsers users',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  if (_showAllUsers)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xff10b981).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.cloud_done, size: 14, color: Color(0xff10b981)),
                          const SizedBox(width: 4),
                          Text(
                            'All Loaded',
                            style: TextStyle(
                              fontSize: 11,
                              color: const Color(0xff10b981),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),

          // Users List
          Expanded(
            child: (_isLoading || _isLoadingAll)
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const CircularProgressIndicator(),
                        const SizedBox(height: 16),
                        Text(
                          _isLoadingAll
                              ? 'Loading all users from database...'
                              : 'Loading users...',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                        if (_isLoadingAll && _users.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(
                              'Loaded ${_users.length} users so far...',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[500],
                              ),
                            ),
                          ),
                      ],
                    ),
                  )
                : _users.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.person_outline,
                                size: 64, color: Colors.grey[400]),
                            const SizedBox(height: 16),
                            Text(
                              'No users found',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: () => _loadUsers(loadAll: _showAllUsers),
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _users.length,
                          itemBuilder: (context, index) {
                            final user = _users[index];
                            return Dismissible(
                              key: Key(user.id.toString()),
                              background: Container(
                                margin: const EdgeInsets.only(bottom: 12),
                                decoration: BoxDecoration(
                                  color: Colors.red,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                alignment: Alignment.centerRight,
                                padding: const EdgeInsets.only(right: 20),
                                child: const Icon(Icons.delete,
                                    color: Colors.white),
                              ),
                              direction: DismissDirection.endToStart,
                              confirmDismiss: (direction) async {
                                final confirmed = await showDialog<bool>(
                                  context: context,
                                  builder: (context) => AlertDialog(
                                    title: const Text('Delete User'),
                                    content: Text(
                                        'Are you sure you want to delete ${user.displayName}?'),
                                    actions: [
                                      TextButton(
                                        onPressed: () =>
                                            Navigator.pop(context, false),
                                        child: const Text('Cancel'),
                                      ),
                                      TextButton(
                                        onPressed: () =>
                                            Navigator.pop(context, true),
                                        style: TextButton.styleFrom(
                                            foregroundColor: Colors.red),
                                        child: const Text('Delete'),
                                      ),
                                    ],
                                  ),
                                );

                                if (confirmed == true) {
                                  try {
                                    await _userService.deleteUser(user.id);
                                    if (mounted) {
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(
                                        const SnackBar(
                                          content:
                                              Text('User deleted successfully'),
                                          backgroundColor: Colors.green,
                                        ),
                                      );
                                      _loadUsers();
                                    }
                                    return true;
                                  } catch (e) {
                                    if (mounted) {
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(
                                        SnackBar(
                                          content: Text('Error: $e'),
                                          backgroundColor: Colors.red,
                                        ),
                                      );
                                    }
                                    return false;
                                  }
                                }
                                return false;
                              },
                              child: _UserCard(
                                user: user,
                                onTap: () async {
                                  final result = await Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (_) =>
                                          UserManagementScreen(userId: user.id),
                                    ),
                                  );
                                  if (result == true) {
                                    _loadUsers(loadAll: _showAllUsers);
                                  }
                                },
                                onActivate: () => _toggleUserStatus(user, activate: true),
                                onDeactivate: () => _toggleUserStatus(user, activate: false),
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => const UserDetailScreen(),
            ),
          );
          if (result == true) {
            _loadUsers(loadAll: _showAllUsers);
          }
        },
        backgroundColor: const Color(0xff2563eb),
        icon: const Icon(Icons.add),
        label: const Text('Add User'),
      ),
    );
  }
}

class _UserCard extends StatelessWidget {
  final User user;
  final VoidCallback onTap;
  final VoidCallback? onActivate;
  final VoidCallback? onDeactivate;

  const _UserCard({
    required this.user,
    required this.onTap,
    this.onActivate,
    this.onDeactivate,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Avatar
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: const Color(0xff2563eb).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      user.displayName.substring(0, 1).toUpperCase(),
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Color(0xff2563eb),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),

                // User Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        user.displayName,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xff1f2937),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        user.email,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                        ),
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 4,
                        children: [
                          if (user.roleName != null)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: const Color(0xff7c3aed).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(
                                    Icons.badge,
                                    size: 12,
                                    color: Color(0xff7c3aed),
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    user.roleName!,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                      color: Color(0xff7c3aed),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          // Zoho sync status badge
                          if (user.isSyncedWithZoho)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: const Color(0xff10b981).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(
                                    Icons.cloud_done,
                                    size: 12,
                                    color: Color(0xff10b981),
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    user.syncStatusMessage,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                      color: Color(0xff10b981),
                                    ),
                                  ),
                                ],
                              ),
                            )
                          else
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.orange.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(
                                    Icons.cloud_off,
                                    size: 12,
                                    color: Colors.orange,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    'Not synced',
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                      color: Colors.orange[700],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Status Badge with Quick Actions
                PopupMenuButton<String>(
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: user.isActive
                          ? const Color(0xff10b981).withOpacity(0.1)
                          : Colors.grey.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: user.isActive
                                ? const Color(0xff10b981)
                                : Colors.grey,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          user.isActive ? 'Active' : 'Inactive',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: user.isActive
                                ? const Color(0xff10b981)
                                : Colors.grey,
                          ),
                        ),
                        const SizedBox(width: 4),
                        const Icon(Icons.arrow_drop_down, size: 16),
                      ],
                    ),
                  ),
                  onSelected: (value) {
                    if (value == 'activate' && onActivate != null) {
                      onActivate!();
                    } else if (value == 'deactivate' && onDeactivate != null) {
                      onDeactivate!();
                    }
                  },
                  itemBuilder: (context) => [
                    if (!user.isActive)
                      const PopupMenuItem(
                        value: 'activate',
                        child: Row(
                          children: [
                            Icon(Icons.check_circle, size: 18, color: Color(0xff10b981)),
                            SizedBox(width: 8),
                            Text('Activate User'),
                          ],
                        ),
                      ),
                    if (user.isActive)
                      const PopupMenuItem(
                        value: 'deactivate',
                        child: Row(
                          children: [
                            Icon(Icons.cancel, size: 18, color: Colors.orange),
                            SizedBox(width: 8),
                            Text('Deactivate User'),
                          ],
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
