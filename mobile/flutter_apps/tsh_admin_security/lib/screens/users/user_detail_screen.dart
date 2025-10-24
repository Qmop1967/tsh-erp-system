import 'package:flutter/material.dart';
import '../../models/user.dart';
import '../../models/role.dart';
import '../../services/user_service.dart';
import '../../services/role_service.dart';

class UserDetailScreen extends StatefulWidget {
  final User? user;

  const UserDetailScreen({super.key, this.user});

  @override
  State<UserDetailScreen> createState() => _UserDetailScreenState();
}

class _UserDetailScreenState extends State<UserDetailScreen> {
  final _formKey = GlobalKey<FormState>();
  final UserService _userService = UserService();
  final RoleService _roleService = RoleService();

  late TextEditingController _emailController;
  late TextEditingController _fullNameEnController;
  late TextEditingController _fullNameArController;
  late TextEditingController _passwordController;

  List<Role> _roles = [];
  int? _selectedRoleId;
  bool _isActive = true;
  bool _isLoading = false;
  bool _isLoadingRoles = true;

  bool get _isEditMode => widget.user != null;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.user?.email ?? '');
    _fullNameEnController = TextEditingController(text: widget.user?.name ?? '');
    _fullNameArController = TextEditingController(text: '');
    _passwordController = TextEditingController();
    _selectedRoleId = widget.user?.roleId;
    _isActive = widget.user?.isActive ?? true;
    _loadRoles();
  }

  @override
  void dispose() {
    _emailController.dispose();
    _fullNameEnController.dispose();
    _fullNameArController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _loadRoles() async {
    setState(() => _isLoadingRoles = true);
    try {
      final roles = await _roleService.getRoles();
      setState(() {
        _roles = roles;
        _isLoadingRoles = false;
      });
    } catch (e) {
      setState(() => _isLoadingRoles = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading roles: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _saveUser() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    try {
      final data = <String, dynamic>{
        'email': _emailController.text.trim(),
        'name': _fullNameEnController.text.trim(),
        'role_id': _selectedRoleId,
        'is_active': _isActive,
      };

      // Add password only if provided (for create or update)
      if (_passwordController.text.isNotEmpty) {
        data['password'] = _passwordController.text;
      }

      if (_isEditMode) {
        await _userService.updateUser(widget.user!.id, data);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('User updated successfully'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        // Password is required for new users
        if (_passwordController.text.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Password is required for new users'),
              backgroundColor: Colors.red,
            ),
          );
          setState(() => _isLoading = false);
          return;
        }
        await _userService.createUser(data);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('User created successfully'),
              backgroundColor: Colors.green,
            ),
          );
        }
      }

      setState(() => _isLoading = false);
      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving user: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _deleteUser() async {
    if (!_isEditMode) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete User'),
        content: Text('Are you sure you want to delete ${widget.user!.displayName}?'),
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
      setState(() => _isLoading = true);
      try {
        await _userService.deleteUser(widget.user!.id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('User deleted successfully'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pop(context, true);
        }
      } catch (e) {
        setState(() => _isLoading = false);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xff2563eb),
        foregroundColor: Colors.white,
        title: Text(
          _isEditMode ? 'Edit User' : 'Add User',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          if (_isEditMode)
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: _deleteUser,
              tooltip: 'Delete User',
            ),
        ],
      ),
      body: _isLoadingRoles
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Email Field
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: InputDecoration(
                        labelText: 'Email',
                        prefixIcon: const Icon(Icons.email_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.white,
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter email';
                        }
                        if (!value.contains('@')) {
                          return 'Please enter a valid email';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Full Name (English)
                    TextFormField(
                      controller: _fullNameEnController,
                      decoration: InputDecoration(
                        labelText: 'Full Name (English)',
                        prefixIcon: const Icon(Icons.person_outline),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Full Name (Arabic)
                    TextFormField(
                      controller: _fullNameArController,
                      decoration: InputDecoration(
                        labelText: 'Full Name (Arabic)',
                        prefixIcon: const Icon(Icons.person_outline),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Password Field
                    TextFormField(
                      controller: _passwordController,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: _isEditMode ? 'Password (leave blank to keep current)' : 'Password',
                        prefixIcon: const Icon(Icons.lock_outline),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.white,
                      ),
                      validator: (value) {
                        if (!_isEditMode && (value == null || value.isEmpty)) {
                          return 'Please enter password';
                        }
                        if (value != null && value.isNotEmpty && value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Role Dropdown
                    DropdownButtonFormField<int>(
                      value: _selectedRoleId,
                      decoration: InputDecoration(
                        labelText: 'Role',
                        prefixIcon: const Icon(Icons.badge_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.white,
                      ),
                      items: _roles.map((role) {
                        return DropdownMenuItem(
                          value: role.id,
                          child: Text(role.name),
                        );
                      }).toList(),
                      onChanged: (value) {
                        setState(() => _selectedRoleId = value);
                      },
                    ),
                    const SizedBox(height: 16),

                    // Active Status Switch
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey[300]!),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: Row(
                        children: [
                          const Icon(Icons.toggle_on_outlined, color: Colors.grey),
                          const SizedBox(width: 12),
                          const Expanded(
                            child: Text(
                              'Active Status',
                              style: TextStyle(fontSize: 16),
                            ),
                          ),
                          Switch(
                            value: _isActive,
                            onChanged: (value) {
                              setState(() => _isActive = value);
                            },
                            activeColor: const Color(0xff10b981),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Save Button
                    ElevatedButton(
                      onPressed: _isLoading ? null : _saveUser,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xff2563eb),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        elevation: 0,
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : Text(
                              _isEditMode ? 'Update User' : 'Create User',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
