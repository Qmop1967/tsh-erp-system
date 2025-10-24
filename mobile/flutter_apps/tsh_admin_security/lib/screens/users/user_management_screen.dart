import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'roles_selection_screen.dart';
import 'permissions_selection_screen.dart';
import 'action_permissions_screen.dart';
import 'access_devices_screen.dart';
import 'activity_logs_screen.dart';
import 'security_events_screen.dart';
import 'active_sessions_screen.dart';

/// Comprehensive User Management & Control Center
/// Redesigned to provide complete control over user permissions, roles, and access
class UserManagementScreen extends StatefulWidget {
  final int userId;

  const UserManagementScreen({Key? key, required this.userId}) : super(key: key);

  @override
  State<UserManagementScreen> createState() => _UserManagementScreenState();
}

class _UserManagementScreenState extends State<UserManagementScreen> {
  // User data (will be loaded from API)
  Map<String, dynamic> userData = {
    'email': 'owner@tsh.sale',
    'name': 'TSH Owner',
    'name_ar': '',
    'role': 'Admin',
    'is_active': true,
    'last_login': DateTime.now().subtract(const Duration(hours: 2)),
    'created_at': DateTime.now().subtract(const Duration(days: 45)),
  };

  // Statistics
  Map<String, int> stats = {
    'total_permissions': 48,
    'active_sessions': 2,
    'trusted_devices': 3,
    'recent_activities': 156,
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFF2563EB),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'User Management',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: () => _refreshData(),
          ),
          IconButton(
            icon: const Icon(Icons.more_vert, color: Colors.white),
            onPressed: () => _showMoreOptions(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            children: [
              // User Profile Header Card
              _buildUserProfileHeader(),

              // Quick Statistics Cards
              _buildQuickStatsSection(),

              const SizedBox(height: 16),

              // Main Action Cards Section
              _buildMainActionCards(),

              const SizedBox(height: 16),

              // Activity & Monitoring Section
              _buildActivityMonitoringSection(),

              const SizedBox(height: 16),

              // Basic Information Section
              _buildBasicInformationSection(),

              const SizedBox(height: 80),
            ],
          ),
        ),
      ),
    );
  }

  // ============================================================================
  // USER PROFILE HEADER
  // ============================================================================

  Widget _buildUserProfileHeader() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            const Color(0xFF2563EB),
            const Color(0xFF2563EB).withOpacity(0.8),
          ],
        ),
      ),
      child: Column(
        children: [
          const SizedBox(height: 24),

          // User Avatar
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              border: Border.all(color: Colors.white, width: 4),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ClipOval(
              child: Container(
                color: const Color(0xFF2563EB).withOpacity(0.1),
                child: const Icon(
                  Icons.person,
                  size: 50,
                  color: Color(0xFF2563EB),
                ),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // User Name
          Text(
            userData['name'] ?? 'User Name',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),

          const SizedBox(height: 8),

          // User Email
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.email, size: 16, color: Colors.white),
                const SizedBox(width: 6),
                Text(
                  userData['email'] ?? '',
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                ),
              ],
            ),
          ),

          const SizedBox(height: 12),

          // Role Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.verified_user,
                  size: 20,
                  color: const Color(0xFF10B981),
                ),
                const SizedBox(width: 8),
                Text(
                  userData['role'] ?? 'No Role',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2563EB),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Status Indicators
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildStatusChip(
                icon: Icons.circle,
                label: userData['is_active'] ? 'Active' : 'Inactive',
                color: userData['is_active'] ? Colors.green : Colors.red,
              ),
              const SizedBox(width: 12),
              _buildStatusChip(
                icon: Icons.access_time,
                label: _getLastLoginText(),
                color: Colors.white.withOpacity(0.9),
              ),
            ],
          ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildStatusChip({
    required IconData icon,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(color: color, fontSize: 12),
          ),
        ],
      ),
    );
  }

  // ============================================================================
  // QUICK STATISTICS SECTION
  // ============================================================================

  Widget _buildQuickStatsSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Quick Overview',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  icon: Icons.lock_open,
                  label: 'Permissions',
                  value: stats['total_permissions'].toString(),
                  color: const Color(0xFF8B5CF6),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  icon: Icons.devices,
                  label: 'Sessions',
                  value: stats['active_sessions'].toString(),
                  color: const Color(0xFF2563EB),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  icon: Icons.phone_android,
                  label: 'Devices',
                  value: stats['trusted_devices'].toString(),
                  color: const Color(0xFF10B981),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  icon: Icons.timeline,
                  label: 'Activities',
                  value: stats['recent_activities'].toString(),
                  color: const Color(0xFFF59E0B),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
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
          ),
        ],
      ),
    );
  }

  // ============================================================================
  // MAIN ACTION CARDS SECTION
  // ============================================================================

  Widget _buildMainActionCards() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Access Management',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 12),

          // Row 1: Roles and Permissions
          Row(
            children: [
              Expanded(
                child: _buildActionCard(
                  icon: Icons.badge,
                  title: 'Roles',
                  subtitle: 'Assign user roles',
                  color: const Color(0xFF8B5CF6),
                  onTap: () => _navigateToRolesSelection(),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildActionCard(
                  icon: Icons.lock_open,
                  title: 'Permissions',
                  subtitle: 'Grant permissions',
                  color: const Color(0xFF10B981),
                  onTap: () => _navigateToPermissionsSelection(),
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Row 2: Action Permissions and Access Devices
          Row(
            children: [
              Expanded(
                child: _buildActionCard(
                  icon: Icons.play_circle_outline,
                  title: 'Action Rights',
                  subtitle: 'CRUD permissions',
                  color: const Color(0xFF2563EB),
                  onTap: () => _navigateToActionPermissions(),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildActionCard(
                  icon: Icons.devices,
                  title: 'Access Devices',
                  subtitle: 'Manage devices',
                  color: const Color(0xFFF59E0B),
                  onTap: () => _navigateToAccessDevices(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, color: color, size: 28),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 16,
                  color: Colors.grey[400],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================================
  // ACTIVITY & MONITORING SECTION
  // ============================================================================

  Widget _buildActivityMonitoringSection() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Activity & Monitoring',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),
          const SizedBox(height: 12),

          // Logs Card
          _buildMonitoringCard(
            icon: Icons.description,
            title: 'Activity Logs',
            subtitle: 'View all user activities',
            count: '156 entries',
            color: const Color(0xFF6366F1),
            onTap: () => _navigateToActivityLogs(),
          ),

          const SizedBox(height: 12),

          // Security Events Card
          _buildMonitoringCard(
            icon: Icons.security,
            title: 'Security Events',
            subtitle: 'Login attempts & security alerts',
            count: '12 events',
            color: const Color(0xFFEF4444),
            onTap: () => _navigateToSecurityEvents(),
          ),

          const SizedBox(height: 12),

          // Sessions Card
          _buildMonitoringCard(
            icon: Icons.computer,
            title: 'Active Sessions',
            subtitle: 'Manage active login sessions',
            count: '2 active',
            color: const Color(0xFF10B981),
            onTap: () => _navigateToActiveSessions(),
          ),
        ],
      ),
    );
  }

  Widget _buildMonitoringCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required String count,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  count,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                const SizedBox(height: 4),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 16,
                  color: Colors.grey[400],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================================
  // BASIC INFORMATION SECTION
  // ============================================================================

  Widget _buildBasicInformationSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Basic Information',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.edit, color: Color(0xFF2563EB)),
                onPressed: () => _navigateToEditBasicInfo(),
              ),
            ],
          ),
          const SizedBox(height: 16),

          _buildInfoRow(Icons.email, 'Email', userData['email'] ?? ''),
          const Divider(height: 24),

          _buildInfoRow(Icons.person, 'Full Name (English)', userData['name'] ?? ''),
          const Divider(height: 24),

          _buildInfoRow(Icons.language, 'Full Name (Arabic)', userData['name_ar'] ?? 'Not set'),
          const Divider(height: 24),

          _buildInfoRow(Icons.badge, 'Role', userData['role'] ?? 'No Role'),
          const Divider(height: 24),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(Icons.toggle_on, color: Colors.grey[600], size: 20),
                  const SizedBox(width: 12),
                  const Text(
                    'Active Status',
                    style: TextStyle(
                      fontSize: 14,
                      color: Color(0xFF6B7280),
                    ),
                  ),
                ],
              ),
              Switch(
                value: userData['is_active'],
                onChanged: (value) => _toggleActiveStatus(value),
                activeColor: const Color(0xFF10B981),
              ),
            ],
          ),

          const Divider(height: 24),

          _buildInfoRow(
            Icons.calendar_today,
            'Member Since',
            DateFormat('MMM dd, yyyy').format(userData['created_at']),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, color: Colors.grey[600], size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: Color(0xFF1F2937),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ============================================================================
  // HELPER METHODS
  // ============================================================================

  String _getLastLoginText() {
    final lastLogin = userData['last_login'] as DateTime;
    final now = DateTime.now();
    final difference = now.difference(lastLogin);

    if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }

  // ============================================================================
  // NAVIGATION METHODS
  // ============================================================================

  void _navigateToRolesSelection() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => RolesSelectionScreen(
          userId: widget.userId,
          userName: userData['name'] ?? userData['email'],
          currentRoleId: userData['role_id'],
        ),
      ),
    );
    if (result != null) {
      _refreshData(); // Refresh to show updated role
    }
  }

  void _navigateToPermissionsSelection() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PermissionsSelectionScreen(
          userId: widget.userId,
          userName: userData['name'] ?? userData['email'],
        ),
      ),
    );
    if (result != null) {
      _refreshData(); // Refresh to show updated permissions
    }
  }

  void _navigateToActionPermissions() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ActionPermissionsScreen(
          userId: widget.userId,
          userName: userData['name'] ?? userData['email'],
        ),
      ),
    );
    if (result != null) {
      _refreshData(); // Refresh to show updated action permissions
    }
  }

  void _navigateToAccessDevices() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AccessDevicesScreen(
          userId: widget.userId,
          userName: userData['name'] ?? userData['email'],
        ),
      ),
    );
    if (result != null) {
      _refreshData(); // Refresh to show updated devices
    }
  }

  void _navigateToActivityLogs() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ActivityLogsScreen(
          userId: widget.userId,
        ),
      ),
    );
  }

  void _navigateToSecurityEvents() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SecurityEventsScreen(
          userId: widget.userId,
        ),
      ),
    );
  }

  void _navigateToActiveSessions() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ActiveSessionsScreen(
          userId: widget.userId,
        ),
      ),
    );
  }

  void _navigateToEditBasicInfo() {
    // Use the existing edit user screen
    Navigator.pushNamed(
      context,
      '/users/edit',
      arguments: {'userId': widget.userId},
    );
  }

  // ============================================================================
  // ACTION METHODS
  // ============================================================================

  Future<void> _refreshData() async {
    // TODO: Implement data refresh from API
    await Future.delayed(const Duration(seconds: 1));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Data refreshed')),
    );
  }

  void _showMoreOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.delete, color: Colors.red),
              title: const Text('Delete User'),
              onTap: () {
                Navigator.pop(context);
                _confirmDeleteUser();
              },
            ),
            ListTile(
              leading: const Icon(Icons.block, color: Colors.orange),
              title: const Text('Suspend User'),
              onTap: () {
                Navigator.pop(context);
                _suspendUser();
              },
            ),
            ListTile(
              leading: const Icon(Icons.lock_reset, color: Colors.blue),
              title: const Text('Reset Password'),
              onTap: () {
                Navigator.pop(context);
                _resetPassword();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _toggleActiveStatus(bool value) {
    setState(() {
      userData['is_active'] = value;
    });
    // TODO: Update via API
  }

  void _confirmDeleteUser() {
    // TODO: Show confirmation dialog and delete user
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Delete user action')),
    );
  }

  void _suspendUser() {
    // TODO: Suspend user
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Suspend user action')),
    );
  }

  void _resetPassword() {
    // TODO: Reset user password
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Reset password action')),
    );
  }
}
