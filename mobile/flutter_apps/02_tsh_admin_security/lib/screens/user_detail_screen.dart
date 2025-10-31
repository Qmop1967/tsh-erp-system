import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/user.dart';
import '../providers/user_provider.dart';
import '../widgets/security_section_card.dart';
import '../widgets/permission_chip.dart';
import '../widgets/data_scope_bar.dart';

/// Comprehensive User Detail Screen
/// Shows complete authentication, role, and permission details
class UserDetailScreen extends StatefulWidget {
  final int userId;

  const UserDetailScreen({Key? key, required this.userId}) : super(key: key);

  @override
  State<UserDetailScreen> createState() => _UserDetailScreenState();
}

class _UserDetailScreenState extends State<UserDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  User? _user;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _loadUserDetails();
  }

  Future<void> _loadUserDetails() async {
    final provider = Provider.of<UserProvider>(context, listen: false);
    await provider.loadUserDetails(widget.userId);
    setState(() {
      _user = provider.selectedUser;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('User Details')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_user == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('User Details')),
        body: const Center(child: Text('User not found')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(_user!.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () => _editUser(context),
            tooltip: 'Edit User',
          ),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () => _showMoreOptions(context),
            tooltip: 'More Options',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Overview', icon: Icon(Icons.dashboard, size: 18)),
            Tab(text: 'Auth & Security', icon: Icon(Icons.security, size: 18)),
            Tab(text: 'Permissions', icon: Icon(Icons.lock_open, size: 18)),
            Tab(text: 'Data Access', icon: Icon(Icons.visibility, size: 18)),
            Tab(text: 'Activity', icon: Icon(Icons.timeline, size: 18)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildOverviewTab(),
          _buildAuthSecurityTab(),
          _buildPermissionsTab(),
          _buildDataAccessTab(),
          _buildActivityTab(),
        ],
      ),
    );
  }

  // ============================================================================
  // OVERVIEW TAB
  // ============================================================================
  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // User Profile Card
          _buildProfileCard(),
          const SizedBox(height: 16),

          // Quick Stats
          _buildQuickStatsGrid(),
          const SizedBox(height: 16),

          // Role Information
          _buildRoleCard(),
          const SizedBox(height: 16),

          // Security Status
          _buildSecurityStatusCard(),
          const SizedBox(height: 16),

          // Active Sessions Preview
          _buildActiveSessionsPreview(),
        ],
      ),
    );
  }

  Widget _buildProfileCard() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Avatar
            CircleAvatar(
              radius: 50,
              backgroundColor: Theme.of(context).colorScheme.primary,
              child: Text(
                _user!.name[0].toUpperCase(),
                style: const TextStyle(fontSize: 36, color: Colors.white),
              ),
            ),
            const SizedBox(height: 16),

            // Name
            Text(
              _user!.name,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),

            // Email
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.email, size: 16, color: Colors.grey),
                const SizedBox(width: 8),
                Text(
                  _user!.email,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Status Badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: _user!.isActive ? Colors.green[50] : Colors.red[50],
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: _user!.isActive ? Colors.green : Colors.red,
                  width: 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    _user!.isActive ? Icons.check_circle : Icons.cancel,
                    size: 16,
                    color: _user!.isActive ? Colors.green : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _user!.isActive ? 'Active' : 'Inactive',
                    style: TextStyle(
                      color: _user!.isActive ? Colors.green : Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Quick Info Grid
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildInfoColumn(
                  Icons.calendar_today,
                  'Joined',
                  _formatDate(_user!.createdAt),
                ),
                _buildInfoColumn(
                  Icons.access_time,
                  'Last Login',
                  _formatRelativeTime(_user!.lastLoginAt),
                ),
                _buildInfoColumn(
                  Icons.business,
                  'Branch',
                  _user!.branchName ?? 'Not Assigned',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoColumn(IconData icon, String label, String value) {
    return Column(
      children: [
        Icon(icon, size: 24, color: Theme.of(context).colorScheme.primary),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickStatsGrid() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Active Sessions',
            '${_user!.activeSessions?.length ?? 0}',
            Icons.devices,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Permissions',
            '${_user!.permissions?.length ?? 0}',
            Icons.lock_open,
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Data Tables',
            '${_user!.accessibleTables?.length ?? 0}',
            Icons.table_chart,
            Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
      String label, String value, IconData icon, Color color) {
    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 12),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRoleCard() {
    return SecuritySectionCard(
      title: 'Role Assignment',
      icon: Icons.badge,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Primary Role
          ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.admin_panel_settings,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            title: Text(
              _user!.role?.name ?? 'No Role Assigned',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            subtitle: Text(
              _user!.role?.description ?? '',
              style: TextStyle(color: Colors.grey[600]),
            ),
            trailing: Chip(
              label: Text(
                _user!.role?.level.toString() ?? 'N/A',
                style: const TextStyle(fontSize: 12),
              ),
              backgroundColor: Colors.purple[50],
            ),
          ),
          const Divider(),

          // Role Capabilities
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Role Capabilities',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _buildRoleCapabilities(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  List<Widget> _buildRoleCapabilities() {
    final capabilities = _user!.role?.capabilities ?? [];
    return capabilities
        .map((cap) => Chip(
              label: Text(cap, style: const TextStyle(fontSize: 12)),
              avatar: const Icon(Icons.check_circle, size: 16),
              backgroundColor: Colors.green[50],
            ))
        .toList();
  }

  Widget _buildSecurityStatusCard() {
    return SecuritySectionCard(
      title: 'Security Status',
      icon: Icons.security,
      child: Column(
        children: [
          _buildSecurityItem(
            'Two-Factor Auth (2FA)',
            _user!.mfaEnabled ?? false,
            Icons.smartphone,
          ),
          _buildSecurityItem(
            'Email Verified',
            _user!.emailVerified ?? false,
            Icons.email,
          ),
          _buildSecurityItem(
            'Account Locked',
            _user!.isLocked ?? false,
            Icons.lock,
            isNegative: true,
          ),
          _buildSecurityItem(
            'Password Expired',
            _user!.passwordExpired ?? false,
            Icons.password,
            isNegative: true,
          ),
        ],
      ),
    );
  }

  Widget _buildSecurityItem(String label, bool status, IconData icon,
      {bool isNegative = false}) {
    final isGood = isNegative ? !status : status;
    return ListTile(
      leading: Icon(
        icon,
        color: isGood ? Colors.green : Colors.red,
      ),
      title: Text(label),
      trailing: Icon(
        isGood ? Icons.check_circle : Icons.cancel,
        color: isGood ? Colors.green : Colors.red,
      ),
    );
  }

  Widget _buildActiveSessionsPreview() {
    final sessions = _user!.activeSessions ?? [];
    return SecuritySectionCard(
      title: 'Active Sessions (${sessions.length})',
      icon: Icons.devices,
      trailing: TextButton(
        onPressed: () => _tabController.animateTo(4),
        child: const Text('View All'),
      ),
      child: sessions.isEmpty
          ? const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: Text('No active sessions')),
            )
          : ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: sessions.length.clamp(0, 3),
              itemBuilder: (context, index) {
                final session = sessions[index];
                return ListTile(
                  leading: Icon(
                    _getDeviceIcon(session.deviceType),
                    color: Colors.blue,
                  ),
                  title: Text(session.deviceName ?? 'Unknown Device'),
                  subtitle: Text(
                      '${session.ipAddress} • ${_formatRelativeTime(session.lastActivity)}'),
                  trailing: Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Colors.green,
                      shape: BoxShape.circle,
                    ),
                  ),
                );
              },
            ),
    );
  }

  // ============================================================================
  // AUTH & SECURITY TAB
  // ============================================================================
  Widget _buildAuthSecurityTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Authentication Methods
          _buildAuthMethodsCard(),
          const SizedBox(height: 16),

          // Security Context (RLS Variables)
          _buildSecurityContextCard(),
          const SizedBox(height: 16),

          // Password Security
          _buildPasswordSecurityCard(),
          const SizedBox(height: 16),

          // Trusted Devices
          _buildTrustedDevicesCard(),
          const SizedBox(height: 16),

          // Security Events
          _buildRecentSecurityEventsCard(),
        ],
      ),
    );
  }

  Widget _buildAuthMethodsCard() {
    return SecuritySectionCard(
      title: 'Authentication Methods',
      icon: Icons.verified_user,
      child: Column(
        children: [
          _buildAuthMethodTile(
            'Password Authentication',
            enabled: true,
            icon: Icons.password,
            subtitle: 'Last changed: ${_formatDate(_user!.passwordChangedAt)}',
          ),
          _buildAuthMethodTile(
            'Two-Factor Authentication (TOTP)',
            enabled: _user!.mfaEnabled ?? false,
            icon: Icons.smartphone,
            subtitle: _user!.mfaEnabled ?? false
                ? 'Enabled via authenticator app'
                : 'Not configured',
          ),
          _buildAuthMethodTile(
            'Trusted Device Auto-Login',
            enabled: _user!.trustedDevices?.isNotEmpty ?? false,
            icon: Icons.fingerprint,
            subtitle:
                '${_user!.trustedDevices?.length ?? 0} trusted device(s)',
          ),
        ],
      ),
    );
  }

  Widget _buildAuthMethodTile(String title,
      {required bool enabled,
      required IconData icon,
      required String subtitle}) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: enabled ? Colors.green[50] : Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          icon,
          color: enabled ? Colors.green : Colors.grey,
        ),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: Switch(
        value: enabled,
        onChanged: (value) => _toggleAuthMethod(title, value),
      ),
    );
  }

  Widget _buildSecurityContextCard() {
    return SecuritySectionCard(
      title: 'Row-Level Security (RLS) Context',
      icon: Icons.shield,
      subtitle: 'PostgreSQL session variables set for this user',
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.purple[50],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.purple[200]!),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildRLSVariable('app.current_user_id', _user!.id.toString()),
            const Divider(),
            _buildRLSVariable(
                'app.current_user_role', _user!.role?.name ?? 'Not Set'),
            const Divider(),
            _buildRLSVariable('app.current_tenant_id',
                _user!.tenantId?.toString() ?? 'Not Set'),
            const Divider(),
            _buildRLSVariable('app.current_branch_id',
                _user!.branchId?.toString() ?? 'Not Set'),
            const Divider(),
            _buildRLSVariable('app.current_warehouse_id',
                _user!.warehouseId?.toString() ?? 'Not Set'),
          ],
        ),
      ),
    );
  }

  Widget _buildRLSVariable(String key, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(
              key,
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 13,
                color: Colors.purple[900],
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const Text('=', style: TextStyle(color: Colors.grey)),
          const SizedBox(width: 8),
          Expanded(
            flex: 2,
            child: Text(
              value,
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 13,
                color: Colors.purple[700],
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.copy, size: 16),
            onPressed: () => _copyToClipboard(value),
            tooltip: 'Copy',
          ),
        ],
      ),
    );
  }

  Widget _buildPasswordSecurityCard() {
    return SecuritySectionCard(
      title: 'Password Security',
      icon: Icons.lock,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ListTile(
            leading: const Icon(Icons.calendar_today, color: Colors.blue),
            title: const Text('Last Password Change'),
            subtitle: Text(_formatDate(_user!.passwordChangedAt)),
          ),
          ListTile(
            leading: const Icon(Icons.timer, color: Colors.orange),
            title: const Text('Password Age'),
            subtitle: Text(_getPasswordAge()),
          ),
          ListTile(
            leading: Icon(
              _user!.passwordExpired ?? false ? Icons.error : Icons.check_circle,
              color: _user!.passwordExpired ?? false ? Colors.red : Colors.green,
            ),
            title: const Text('Password Status'),
            subtitle: Text(
              _user!.passwordExpired ?? false
                  ? 'Expired - Requires reset'
                  : 'Valid',
            ),
          ),
          const Divider(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _resetPassword(),
                    icon: const Icon(Icons.refresh),
                    label: const Text('Reset Password'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _forcePasswordChange(),
                    icon: const Icon(Icons.lock_reset),
                    label: const Text('Force Change'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrustedDevicesCard() {
    final devices = _user!.trustedDevices ?? [];
    return SecuritySectionCard(
      title: 'Trusted Devices (${devices.length})',
      icon: Icons.devices_other,
      child: devices.isEmpty
          ? const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: Text('No trusted devices')),
            )
          : ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: devices.length,
              itemBuilder: (context, index) {
                final device = devices[index];
                return ListTile(
                  leading: Icon(_getDeviceIcon(device.deviceType)),
                  title: Text(device.deviceName ?? 'Unknown Device'),
                  subtitle: Text(
                      'Added: ${_formatDate(device.trustedAt)}\n${device.deviceFingerprint}'),
                  isThreeLine: true,
                  trailing: IconButton(
                    icon: const Icon(Icons.delete, color: Colors.red),
                    onPressed: () => _revokeDeviceTrust(device),
                  ),
                );
              },
            ),
    );
  }

  Widget _buildRecentSecurityEventsCard() {
    final events = _user!.recentSecurityEvents ?? [];
    return SecuritySectionCard(
      title: 'Recent Security Events',
      icon: Icons.history,
      trailing: TextButton(
        onPressed: () => _viewAllSecurityEvents(),
        child: const Text('View All'),
      ),
      child: events.isEmpty
          ? const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: Text('No recent events')),
            )
          : ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: events.length.clamp(0, 5),
              itemBuilder: (context, index) {
                final event = events[index];
                return _buildSecurityEventTile(event);
              },
            ),
    );
  }

  Widget _buildSecurityEventTile(SecurityEvent event) {
    return ListTile(
      leading: Icon(
        _getEventIcon(event.type),
        color: _getEventColor(event.severity),
      ),
      title: Text(event.type),
      subtitle: Text(
        '${event.description}\n${_formatRelativeTime(event.timestamp)}',
      ),
      isThreeLine: true,
      trailing: Chip(
        label: Text(
          event.severity.toUpperCase(),
          style: const TextStyle(fontSize: 10),
        ),
        backgroundColor: _getEventColor(event.severity).withOpacity(0.1),
      ),
    );
  }

  // ============================================================================
  // PERMISSIONS TAB
  // ============================================================================
  Widget _buildPermissionsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Permission Summary
          _buildPermissionSummaryCard(),
          const SizedBox(height: 16),

          // Permissions by Category
          _buildPermissionsByCategoryCard(),
          const SizedBox(height: 16),

          // Permission Grants (Direct vs Inherited)
          _buildPermissionGrantsCard(),
        ],
      ),
    );
  }

  Widget _buildPermissionSummaryCard() {
    final totalPermissions = _user!.permissions?.length ?? 0;
    final directPermissions =
        _user!.permissions?.where((p) => p.source == 'direct').length ?? 0;
    final rolePermissions =
        _user!.permissions?.where((p) => p.source == 'role').length ?? 0;

    return SecuritySectionCard(
      title: 'Permission Summary',
      icon: Icons.analytics,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildPermissionStat(
              'Total',
              totalPermissions.toString(),
              Colors.blue,
            ),
            _buildPermissionStat(
              'Direct',
              directPermissions.toString(),
              Colors.green,
            ),
            _buildPermissionStat(
              'From Role',
              rolePermissions.toString(),
              Colors.purple,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPermissionStat(String label, String value, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildPermissionsByCategoryCard() {
    // Group permissions by module
    final permissionsByModule = <String, List<Permission>>{};
    for (final permission in _user!.permissions ?? []) {
      final module = permission.module ?? 'Other';
      permissionsByModule.putIfAbsent(module, () => []).add(permission);
    }

    return SecuritySectionCard(
      title: 'Permissions by Module',
      icon: Icons.category,
      child: Column(
        children: permissionsByModule.entries.map((entry) {
          return ExpansionTile(
            leading: Icon(_getModuleIcon(entry.key)),
            title: Text(entry.key),
            subtitle: Text('${entry.value.length} permission(s)'),
            children: entry.value.map((permission) {
              return PermissionChip(
                permission: permission,
                showSource: true,
              );
            }).toList(),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildPermissionGrantsCard() {
    return SecuritySectionCard(
      title: 'Permission Grants',
      icon: Icons.assignment_turned_in,
      child: Column(
        children: [
          // Direct Permissions
          ExpansionTile(
            leading: const Icon(Icons.person, color: Colors.green),
            title: const Text('Direct Permissions'),
            subtitle: Text(
                '${_user!.permissions?.where((p) => p.source == 'direct').length ?? 0} granted directly to user'),
            children: _user!.permissions
                    ?.where((p) => p.source == 'direct')
                    .map((p) => ListTile(
                          title: Text(p.name),
                          subtitle: Text(p.description ?? ''),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            onPressed: () => _revokePermission(p),
                          ),
                        ))
                    .toList() ??
                [],
          ),

          // Role Permissions
          ExpansionTile(
            leading: const Icon(Icons.badge, color: Colors.purple),
            title: const Text('Role Permissions'),
            subtitle: Text(
                '${_user!.permissions?.where((p) => p.source == 'role').length ?? 0} inherited from ${_user!.role?.name ?? "role"}'),
            children: _user!.permissions
                    ?.where((p) => p.source == 'role')
                    .map((p) => ListTile(
                          title: Text(p.name),
                          subtitle: Text(p.description ?? ''),
                          trailing: const Chip(
                            label: Text('From Role', style: TextStyle(fontSize: 10)),
                            backgroundColor: Colors.purple,
                          ),
                        ))
                    .toList() ??
                [],
          ),
        ],
      ),
    );
  }

  // ============================================================================
  // DATA ACCESS TAB
  // ============================================================================
  Widget _buildDataAccessTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Data Scope Overview
          _buildDataScopeOverviewCard(),
          const SizedBox(height: 16),

          // RLS Policy Impact
          _buildRLSPolicyImpactCard(),
          const SizedBox(height: 16),

          // Table Access Details
          _buildTableAccessDetailsCard(),
        ],
      ),
    );
  }

  Widget _buildDataScopeOverviewCard() {
    return SecuritySectionCard(
      title: 'Data Access Scope',
      icon: Icons.visibility,
      subtitle: 'What data can this user access based on RLS policies',
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'User: ${_user!.name}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text('Role: ${_user!.role?.name ?? "Not Assigned"}'),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 8),
            _buildAccessScopeRow('Total Tables', '8'),
            _buildAccessScopeRow('Protected by RLS', '5'),
            _buildAccessScopeRow('Full Access', '3'),
            _buildAccessScopeRow('Restricted Access', '5'),
          ],
        ),
      ),
    );
  }

  Widget _buildAccessScopeRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildRLSPolicyImpactCard() {
    return SecuritySectionCard(
      title: 'Active RLS Policies',
      icon: Icons.shield,
      subtitle: 'Policies that affect this user\'s data access',
      child: Column(
        children: [
          _buildPolicyImpactTile(
            'customers_sales_rep_own_clients',
            'customers',
            'Can only view own assigned customers',
            RLSPolicyType.rebac,
          ),
          _buildPolicyImpactTile(
            'sales_orders_sales_rep_own_orders',
            'sales_orders',
            'Can only view orders for own customers',
            RLSPolicyType.rebac,
          ),
          _buildPolicyImpactTile(
            'expenses_own_expenses_edit',
            'expenses',
            'Can edit own expenses under \$5,000',
            RLSPolicyType.abac,
          ),
        ],
      ),
    );
  }

  Widget _buildPolicyImpactTile(
    String policyName,
    String tableName,
    String description,
    RLSPolicyType type,
  ) {
    return ExpansionTile(
      leading: Icon(
        Icons.policy,
        color: _getPolicyTypeColor(type),
      ),
      title: Text(policyName),
      subtitle: Text('Table: $tableName'),
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Chip(
                    label: Text(type.toString().split('.').last.toUpperCase()),
                    backgroundColor: _getPolicyTypeColor(type).withOpacity(0.1),
                  ),
                  const SizedBox(width: 8),
                  const Chip(label: Text('ACTIVE')),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                description,
                style: TextStyle(color: Colors.grey[700]),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => _testPolicyForUser(policyName),
                icon: const Icon(Icons.play_arrow),
                label: const Text('Test Policy'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTableAccessDetailsCard() {
    return SecuritySectionCard(
      title: 'Table Access Details',
      icon: Icons.table_chart,
      child: Column(
        children: [
          DataScopeBar(
            tableName: 'customers',
            totalRecords: 1250,
            accessibleRecords: 45,
            policyName: 'customers_sales_rep_own_clients',
            reason: 'Only own assigned customers',
          ),
          const SizedBox(height: 12),
          DataScopeBar(
            tableName: 'sales_orders',
            totalRecords: 3420,
            accessibleRecords: 156,
            policyName: 'sales_orders_sales_rep_own_orders',
            reason: 'Orders for assigned customers only',
          ),
          const SizedBox(height: 12),
          DataScopeBar(
            tableName: 'expenses',
            totalRecords: 892,
            accessibleRecords: 23,
            policyName: 'expenses_own_expenses_view',
            reason: 'Only own expenses',
          ),
          const SizedBox(height: 12),
          DataScopeBar(
            tableName: 'users',
            totalRecords: 37,
            accessibleRecords: 1,
            policyName: 'users_view_own_profile',
            reason: 'Only own profile',
          ),
          const SizedBox(height: 12),
          DataScopeBar(
            tableName: 'products',
            totalRecords: 5600,
            accessibleRecords: 5600,
            policyName: 'N/A',
            reason: 'Full access - No RLS',
          ),
        ],
      ),
    );
  }

  // ============================================================================
  // ACTIVITY TAB
  // ============================================================================
  Widget _buildActivityTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Activity Timeline
          _buildActivityTimelineCard(),
          const SizedBox(height: 16),

          // Login History
          _buildLoginHistoryCard(),
          const SizedBox(height: 16),

          // Recent Actions
          _buildRecentActionsCard(),
        ],
      ),
    );
  }

  Widget _buildActivityTimelineCard() {
    return SecuritySectionCard(
      title: 'Activity Timeline',
      icon: Icons.timeline,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildTimelineItem(
              'Login',
              'Logged in from Chrome on Windows',
              DateTime.now().subtract(const Duration(hours: 2)),
              Icons.login,
              Colors.green,
            ),
            _buildTimelineItem(
              'Data Access',
              'Viewed customer records (45 results)',
              DateTime.now().subtract(const Duration(hours: 2, minutes: 15)),
              Icons.visibility,
              Colors.blue,
            ),
            _buildTimelineItem(
              'Permission Change',
              'Admin granted "customers.update" permission',
              DateTime.now().subtract(const Duration(days: 1)),
              Icons.lock_open,
              Colors.orange,
            ),
            _buildTimelineItem(
              'Profile Update',
              'Updated email address',
              DateTime.now().subtract(const Duration(days: 3)),
              Icons.edit,
              Colors.purple,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineItem(String title, String description,
      DateTime timestamp, IconData icon, Color color) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, size: 20, color: color),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(
                description,
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
              Text(
                _formatRelativeTime(timestamp),
                style: TextStyle(fontSize: 11, color: Colors.grey[500]),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLoginHistoryCard() {
    return SecuritySectionCard(
      title: 'Login History',
      icon: Icons.history,
      child: ListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: 5,
        itemBuilder: (context, index) {
          return ListTile(
            leading: const Icon(Icons.login, color: Colors.green),
            title: Text('Login from Chrome'),
            subtitle: Text('IP: 192.168.1.100 • Baghdad, Iraq'),
            trailing: Text(_formatRelativeTime(
                DateTime.now().subtract(Duration(hours: index * 6)))),
          );
        },
      ),
    );
  }

  Widget _buildRecentActionsCard() {
    return SecuritySectionCard(
      title: 'Recent Actions',
      icon: Icons.history,
      child: ListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: 10,
        itemBuilder: (context, index) {
          return ListTile(
            leading: Icon(_getActionIcon(index), color: Colors.blue),
            title: Text('Action ${index + 1}'),
            subtitle: Text('Description of action'),
            trailing: Text(_formatRelativeTime(
                DateTime.now().subtract(Duration(minutes: index * 30)))),
          );
        },
      ),
    );
  }

  // ============================================================================
  // HELPER METHODS
  // ============================================================================

  IconData _getDeviceIcon(String? deviceType) {
    switch (deviceType?.toLowerCase()) {
      case 'mobile':
        return Icons.phone_android;
      case 'tablet':
        return Icons.tablet;
      case 'desktop':
      default:
        return Icons.computer;
    }
  }

  IconData _getEventIcon(String type) {
    switch (type.toLowerCase()) {
      case 'login':
        return Icons.login;
      case 'logout':
        return Icons.logout;
      case 'failed_login':
        return Icons.error;
      case 'password_change':
        return Icons.lock;
      case 'permission_change':
        return Icons.lock_open;
      default:
        return Icons.info;
    }
  }

  Color _getEventColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Colors.red;
      case 'high':
        return Colors.orange;
      case 'medium':
        return Colors.yellow;
      case 'low':
      default:
        return Colors.blue;
    }
  }

  IconData _getModuleIcon(String module) {
    switch (module.toLowerCase()) {
      case 'dashboard':
        return Icons.dashboard;
      case 'users':
        return Icons.people;
      case 'customers':
        return Icons.person;
      case 'sales':
        return Icons.shopping_cart;
      case 'inventory':
        return Icons.inventory;
      case 'reports':
        return Icons.analytics;
      default:
        return Icons.category;
    }
  }

  Color _getPolicyTypeColor(RLSPolicyType type) {
    switch (type) {
      case RLSPolicyType.rbac:
        return Colors.blue;
      case RLSPolicyType.rebac:
        return Colors.purple;
      case RLSPolicyType.abac:
        return Colors.orange;
    }
  }

  IconData _getActionIcon(int index) {
    final icons = [
      Icons.edit,
      Icons.delete,
      Icons.add,
      Icons.visibility,
      Icons.download,
    ];
    return icons[index % icons.length];
  }

  String _formatDate(DateTime? date) {
    if (date == null) return 'Never';
    return '${date.day}/${date.month}/${date.year}';
  }

  String _formatRelativeTime(DateTime? date) {
    if (date == null) return 'Never';
    final difference = DateTime.now().difference(date);
    if (difference.inMinutes < 1) return 'Just now';
    if (difference.inMinutes < 60) return '${difference.inMinutes}m ago';
    if (difference.inHours < 24) return '${difference.inHours}h ago';
    if (difference.inDays < 7) return '${difference.inDays}d ago';
    return _formatDate(date);
  }

  String _getPasswordAge() {
    if (_user!.passwordChangedAt == null) return 'Unknown';
    final age = DateTime.now().difference(_user!.passwordChangedAt!);
    if (age.inDays < 30) return '${age.inDays} days';
    if (age.inDays < 365) return '${(age.inDays / 30).floor()} months';
    return '${(age.inDays / 365).floor()} years';
  }

  // ============================================================================
  // ACTION METHODS
  // ============================================================================

  void _editUser(BuildContext context) {
    // Navigate to edit user screen
  }

  void _showMoreOptions(BuildContext context) {
    // Show bottom sheet with more options
  }

  void _toggleAuthMethod(String method, bool enabled) {
    // Toggle authentication method
  }

  void _copyToClipboard(String text) {
    // Copy text to clipboard
  }

  void _resetPassword() {
    // Reset user password
  }

  void _forcePasswordChange() {
    // Force user to change password on next login
  }

  void _revokeDeviceTrust(TrustedDevice device) {
    // Revoke device trust
  }

  void _viewAllSecurityEvents() {
    // Navigate to full security events screen
  }

  void _revokePermission(Permission permission) {
    // Revoke specific permission
  }

  void _testPolicyForUser(String policyName) {
    // Test RLS policy for this user
  }
}

// ============================================================================
// MODELS
// ============================================================================

enum RLSPolicyType { rbac, rebac, abac }

class SecurityEvent {
  final String type;
  final String description;
  final String severity;
  final DateTime timestamp;

  SecurityEvent({
    required this.type,
    required this.description,
    required this.severity,
    required this.timestamp,
  });
}

class TrustedDevice {
  final String deviceName;
  final String deviceType;
  final String deviceFingerprint;
  final DateTime trustedAt;

  TrustedDevice({
    required this.deviceName,
    required this.deviceType,
    required this.deviceFingerprint,
    required this.trustedAt,
  });
}

class Permission {
  final String name;
  final String? description;
  final String? module;
  final String source; // 'direct' or 'role'

  Permission({
    required this.name,
    this.description,
    this.module,
    required this.source,
  });
}
