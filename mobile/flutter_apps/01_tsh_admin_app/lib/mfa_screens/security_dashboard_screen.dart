import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

import '../models/mfa_request.dart';
import '../models/user_device.dart';
import '../models/user_session.dart';
import '../services/api_service.dart';
import '../services/biometric_service.dart';
import '../services/notification_service.dart';

class SecurityDashboardScreen extends ConsumerStatefulWidget {
  const SecurityDashboardScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<SecurityDashboardScreen> createState() => _SecurityDashboardScreenState();
}

class _SecurityDashboardScreenState extends ConsumerState<SecurityDashboardScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  late Timer _refreshTimer;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    
    // Auto-refresh every 30 seconds
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      _refreshData();
    });
    
    _refreshData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _refreshTimer.cancel();
    super.dispose();
  }

  void _refreshData() {
    ref.read(apiServiceProvider).refreshDashboard();
    ref.read(apiServiceProvider).refreshDevices();
    ref.read(apiServiceProvider).refreshSessions();
    ref.read(apiServiceProvider).refreshMFARequests();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('TSH Security'),
        elevation: 0,
        backgroundColor: isDark ? Colors.grey[900] : theme.primaryColor,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: 'Dashboard'),
            Tab(icon: Icon(Icons.security), text: 'MFA'),
            Tab(icon: Icon(Icons.devices), text: 'Devices'),
            Tab(icon: Icon(Icons.timeline), text: 'Sessions'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildDashboardTab(),
          _buildMFATab(),
          _buildDevicesTab(),
          _buildSessionsTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showQuickActions,
        icon: const Icon(Icons.add_moderator),
        label: const Text('Quick Actions'),
        backgroundColor: theme.primaryColor,
      ),
    );
  }

  Widget _buildDashboardTab() {
    return Consumer(
      builder: (context, ref, child) {
        final dashboardData = ref.watch(dashboardProvider);
        
        return RefreshIndicator(
          onRefresh: () async => _refreshData(),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSecurityOverview(dashboardData),
                const SizedBox(height: 20),
                _buildRecentActivity(dashboardData),
                const SizedBox(height: 20),
                _buildRiskAssessment(dashboardData),
                const SizedBox(height: 20),
                _buildSystemHealth(dashboardData),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSecurityOverview(AsyncValue<Map<String, dynamic>> dashboardData) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Security Overview',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            dashboardData.when(
              data: (data) => Column(
                children: [
                  _buildSecurityMetric(
                    'Active Sessions',
                    data['active_sessions']?.toString() ?? '0',
                    Icons.people_alt,
                    Colors.blue,
                  ),
                  const SizedBox(height: 12),
                  _buildSecurityMetric(
                    'Failed Logins (24h)',
                    data['failed_logins_24h']?.toString() ?? '0',
                    Icons.security,
                    Colors.orange,
                  ),
                  const SizedBox(height: 12),
                  _buildSecurityMetric(
                    'Open Incidents',
                    data['open_incidents']?.toString() ?? '0',
                    Icons.warning,
                    Colors.red,
                  ),
                  const SizedBox(height: 12),
                  _buildSecurityMetric(
                    'MFA Devices',
                    data['mfa_devices']?.toString() ?? '0',
                    Icons.phone_android,
                    Colors.green,
                  ),
                ],
              ),
              loading: () => const CircularProgressIndicator(),
              error: (error, stack) => Text('Error: $error'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSecurityMetric(String title, String value, IconData icon, Color color) {
    return Row(
      children: [
        CircleAvatar(
          backgroundColor: color.withOpacity(0.1),
          child: Icon(icon, color: color),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontSize: 14)),
              Text(
                value,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMFATab() {
    return Consumer(
      builder: (context, ref, child) {
        final mfaRequests = ref.watch(mfaRequestsProvider);
        
        return RefreshIndicator(
          onRefresh: () async => ref.read(apiServiceProvider).refreshMFARequests(),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withOpacity(0.1),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.security, size: 32),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Text(
                        'Pending MFA Approvals',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                    ),
                    IconButton(
                      onPressed: () => _scanQRCode(),
                      icon: const Icon(Icons.qr_code_scanner),
                      tooltip: 'Scan QR Code',
                    ),
                  ],
                ),
              ),
              Expanded(
                child: mfaRequests.when(
                  data: (requests) => requests.isEmpty
                      ? const Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.check_circle, size: 64, color: Colors.green),
                              SizedBox(height: 16),
                              Text('No pending MFA requests'),
                            ],
                          ),
                        )
                      : ListView.builder(
                          itemCount: requests.length,
                          itemBuilder: (context, index) {
                            final request = requests[index];
                            return _buildMFARequestCard(request);
                          },
                        ),
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (error, stack) => Center(child: Text('Error: $error')),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMFARequestCard(MFARequest request) {
    final isExpired = request.expiresAt.isBefore(DateTime.now());
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: isExpired ? Colors.red : Colors.blue,
                  child: Text(
                    request.userEmail.substring(0, 1).toUpperCase(),
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        request.userEmail,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Action: ${request.action}',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                if (!isExpired)
                  Text(
                    _formatTimeRemaining(request.expiresAt),
                    style: const TextStyle(fontSize: 12, color: Colors.orange),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Resource: ${request.resourceType}',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            if (request.location != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.location_on, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    '${request.location!['city']}, ${request.location!['country']}',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                ],
              ),
            ],
            if (request.deviceInfo != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.devices, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    request.deviceInfo!['deviceName'] ?? 'Unknown Device',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: isExpired ? null : () => _approveMFARequest(request),
                    icon: const Icon(Icons.check),
                    label: const Text('Approve'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: isExpired ? null : () => _denyMFARequest(request),
                    icon: const Icon(Icons.close),
                    label: const Text('Deny'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDevicesTab() {
    return Consumer(
      builder: (context, ref, child) {
        final devices = ref.watch(devicesProvider);
        
        return RefreshIndicator(
          onRefresh: () async => ref.read(apiServiceProvider).refreshDevices(),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withOpacity(0.1),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.devices, size: 32),
                    SizedBox(width: 16),
                    Text(
                      'Registered Devices',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: devices.when(
                  data: (deviceList) => ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: deviceList.length,
                    itemBuilder: (context, index) {
                      final device = deviceList[index];
                      return _buildDeviceCard(device);
                    },
                  ),
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (error, stack) => Center(child: Text('Error: $error')),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDeviceCard(UserDevice device) {
    final isCurrentDevice = device.isCurrent;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: device.isActive ? Colors.green : Colors.grey,
          child: Icon(
            _getDeviceIcon(device.deviceType),
            color: Colors.white,
          ),
        ),
        title: Text(
          device.deviceName,
          style: TextStyle(
            fontWeight: isCurrentDevice ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${device.deviceType} • ${device.osVersion}'),
            if (device.lastUsed != null)
              Text(
                'Last used: ${_formatDateTime(device.lastUsed!)}',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
            if (device.location != null)
              Text(
                '${device.location!['city']}, ${device.location!['country']}',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) => _handleDeviceAction(device, value),
          itemBuilder: (context) => [
            if (!isCurrentDevice) ...[
              const PopupMenuItem(
                value: 'revoke',
                child: ListTile(
                  leading: Icon(Icons.block, color: Colors.red),
                  title: Text('Revoke Access'),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ],
            const PopupMenuItem(
              value: 'details',
              child: ListTile(
                leading: Icon(Icons.info),
                title: Text('View Details'),
                contentPadding: EdgeInsets.zero,
              ),
            ),
          ],
        ),
        isThreeLine: true,
      ),
    );
  }

  Widget _buildSessionsTab() {
    return Consumer(
      builder: (context, ref, child) {
        final sessions = ref.watch(sessionsProvider);
        
        return RefreshIndicator(
          onRefresh: () async => ref.read(apiServiceProvider).refreshSessions(),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withOpacity(0.1),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.timeline, size: 32),
                    SizedBox(width: 16),
                    Text(
                      'Active Sessions',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: sessions.when(
                  data: (sessionList) => ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: sessionList.length,
                    itemBuilder: (context, index) {
                      final session = sessionList[index];
                      return _buildSessionCard(session);
                    },
                  ),
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (error, stack) => Center(child: Text('Error: $error')),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSessionCard(UserSession session) {
    final riskColor = _getRiskColor(session.riskScore);
    final isCurrentSession = session.isCurrent;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: riskColor.withOpacity(0.2),
          child: Icon(Icons.computer, color: riskColor),
        ),
        title: Text(
          session.deviceInfo?['deviceName'] ?? 'Unknown Device',
          style: TextStyle(
            fontWeight: isCurrentSession ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Risk Score: ${(session.riskScore * 100).toInt()}%'),
            Text('Started: ${_formatDateTime(session.createdAt)}'),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (session.location != null) ...[
                  _buildSessionDetail(
                    'Location',
                    '${session.location!['city']}, ${session.location!['country']}',
                    Icons.location_on,
                  ),
                ],
                if (session.ipAddress != null) ...[
                  _buildSessionDetail(
                    'IP Address',
                    session.ipAddress!,
                    Icons.wifi,
                  ),
                ],
                _buildSessionDetail(
                  'Last Activity',
                  _formatDateTime(session.lastActivity),
                  Icons.access_time,
                ),
                _buildSessionDetail(
                  'Expires At',
                  _formatDateTime(session.expiresAt),
                  Icons.schedule,
                ),
                const SizedBox(height: 16),
                if (!isCurrentSession)
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () => _terminateSession(session),
                      icon: const Icon(Icons.power_off),
                      label: const Text('Terminate Session'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSessionDetail(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 16, color: Colors.grey),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  // Helper methods
  IconData _getDeviceIcon(String deviceType) {
    switch (deviceType.toLowerCase()) {
      case 'mobile':
        return Icons.phone_android;
      case 'desktop':
        return Icons.computer;
      case 'tablet':
        return Icons.tablet;
      default:
        return Icons.devices;
    }
  }

  Color _getRiskColor(double riskScore) {
    if (riskScore >= 0.8) return Colors.red;
    if (riskScore >= 0.6) return Colors.orange;
    if (riskScore >= 0.3) return Colors.yellow[700]!;
    return Colors.green;
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else {
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    }
  }

  String _formatTimeRemaining(DateTime expiresAt) {
    final now = DateTime.now();
    final difference = expiresAt.difference(now);
    
    if (difference.isNegative) {
      return 'Expired';
    } else if (difference.inMinutes < 1) {
      return '< 1m';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m';
    } else {
      return '${difference.inHours}h ${difference.inMinutes % 60}m';
    }
  }

  // Action handlers
  Future<void> _scanQRCode() async {
    // Navigate to QR scanner
    // Implementation would depend on your QR scanner setup
  }

  Future<void> _approveMFARequest(MFARequest request) async {
    try {
      // Perform biometric authentication first
      final biometricService = ref.read(biometricServiceProvider);
      final biometricResult = await biometricService.authenticate(
        'Approve access request for ${request.userEmail}',
      );
      
      if (biometricResult.success) {
        await ref.read(apiServiceProvider).approveMFARequest(
          request.id,
          biometricResult.biometricData,
        );
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('MFA request approved successfully'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error approving request: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _denyMFARequest(MFARequest request) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Deny Access Request'),
        content: Text('Are you sure you want to deny access for ${request.userEmail}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Deny'),
          ),
        ],
      ),
    );
    
    if (confirmed == true) {
      try {
        await ref.read(apiServiceProvider).denyMFARequest(request.id);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('MFA request denied'),
            backgroundColor: Colors.orange,
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error denying request: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _handleDeviceAction(UserDevice device, String action) {
    switch (action) {
      case 'revoke':
        _revokeDevice(device);
        break;
      case 'details':
        _showDeviceDetails(device);
        break;
    }
  }

  Future<void> _revokeDevice(UserDevice device) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Revoke Device Access'),
        content: Text('Are you sure you want to revoke access for "${device.deviceName}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Revoke'),
          ),
        ],
      ),
    );
    
    if (confirmed == true) {
      try {
        await ref.read(apiServiceProvider).revokeDevice(device.id);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Device access revoked'),
            backgroundColor: Colors.orange,
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error revoking device: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showDeviceDetails(UserDevice device) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(device.deviceName),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('Device Type', device.deviceType),
              _buildDetailRow('OS Version', device.osVersion),
              _buildDetailRow('Status', device.isActive ? 'Active' : 'Inactive'),
              if (device.lastUsed != null)
                _buildDetailRow('Last Used', _formatDateTime(device.lastUsed!)),
              if (device.location != null) ...[
                _buildDetailRow('Location', '${device.location!['city']}, ${device.location!['country']}'),
                if (device.location!['latitude'] != null)
                  _buildDetailRow('Coordinates', '${device.location!['latitude']}, ${device.location!['longitude']}'),
              ],
              _buildDetailRow('Registered', _formatDateTime(device.createdAt)),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Future<void> _terminateSession(UserSession session) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Terminate Session'),
        content: const Text('Are you sure you want to terminate this session?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Terminate'),
          ),
        ],
      ),
    );
    
    if (confirmed == true) {
      try {
        await ref.read(apiServiceProvider).terminateSession(session.id);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Session terminated'),
            backgroundColor: Colors.orange,
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error terminating session: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showQuickActions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Quick Actions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.qr_code_scanner),
              title: const Text('Scan QR Code'),
              onTap: () {
                Navigator.pop(context);
                _scanQRCode();
              },
            ),
            ListTile(
              leading: const Icon(Icons.refresh),
              title: const Text('Refresh All Data'),
              onTap: () {
                Navigator.pop(context);
                _refreshData();
              },
            ),
            ListTile(
              leading: const Icon(Icons.security),
              title: const Text('Emergency Lockdown'),
              onTap: () {
                Navigator.pop(context);
                _showEmergencyLockdown();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showEmergencyLockdown() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency Lockdown'),
        content: const Text(
          'This will immediately terminate all active sessions and lock the account. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.of(context).pop();
              // Implement emergency lockdown
              try {
                await ref.read(apiServiceProvider).emergencyLockdown();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Emergency lockdown activated'),
                    backgroundColor: Colors.red,
                  ),
                );
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Error: $e'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Lockdown'),
          ),
        ],
      ),
    );
  }

  // Additional helper widgets for dashboard
  Widget _buildRecentActivity(AsyncValue<Map<String, dynamic>> dashboardData) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Recent Activity',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            dashboardData.when(
              data: (data) {
                final recentAudits = data['recent_audits'] as List<dynamic>? ?? [];
                return recentAudits.isEmpty
                    ? const Text('No recent activity')
                    : Column(
                        children: recentAudits.take(5).map((audit) {
                          return ListTile(
                            leading: CircleAvatar(
                              backgroundColor: _getActionColor(audit['action']),
                              child: Icon(
                                _getActionIcon(audit['action']),
                                color: Colors.white,
                                size: 16,
                              ),
                            ),
                            title: Text(audit['action'] ?? 'Unknown Action'),
                            subtitle: Text(audit['user_email'] ?? 'Unknown User'),
                            trailing: Text(
                              _formatDateTime(DateTime.parse(audit['timestamp'])),
                              style: const TextStyle(fontSize: 12),
                            ),
                          );
                        }).toList(),
                      );
              },
              loading: () => const CircularProgressIndicator(),
              error: (error, stack) => Text('Error: $error'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRiskAssessment(AsyncValue<Map<String, dynamic>> dashboardData) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Risk Assessment',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            dashboardData.when(
              data: (data) {
                final highRiskSessions = data['high_risk_sessions'] ?? 0;
                final policyViolations = data['policy_violations_7d'] ?? 0;
                
                return Column(
                  children: [
                    _buildRiskIndicator('High Risk Sessions', highRiskSessions, Colors.red),
                    const SizedBox(height: 12),
                    _buildRiskIndicator('Policy Violations (7d)', policyViolations, Colors.orange),
                  ],
                );
              },
              loading: () => const CircularProgressIndicator(),
              error: (error, stack) => Text('Error: $error'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRiskIndicator(String title, int value, Color color) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: value > 0 ? color : Colors.green,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(child: Text(title)),
        Text(
          value.toString(),
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: value > 0 ? color : Colors.green,
          ),
        ),
      ],
    );
  }

  Widget _buildSystemHealth(AsyncValue<Map<String, dynamic>> dashboardData) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'System Health',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            dashboardData.when(
              data: (data) {
                final systemHealth = data['system_health'] ?? 'unknown';
                final healthColor = systemHealth == 'healthy' ? Colors.green : Colors.orange;
                
                return Row(
                  children: [
                    Icon(
                      systemHealth == 'healthy' ? Icons.check_circle : Icons.warning,
                      color: healthColor,
                      size: 32,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Status: ${systemHealth.toUpperCase()}',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: healthColor,
                            ),
                          ),
                          const Text('All security systems operational'),
                        ],
                      ),
                    ),
                  ],
                );
              },
              loading: () => const CircularProgressIndicator(),
              error: (error, stack) => Text('Error: $error'),
            ),
          ],
        ),
      ),
    );
  }

  Color _getActionColor(String action) {
    switch (action.toLowerCase()) {
      case 'login':
        return Colors.green;
      case 'login_failed':
        return Colors.red;
      case 'logout':
        return Colors.blue;
      case 'policy_violation':
        return Colors.orange;
      case 'mfa_approved':
        return Colors.green;
      case 'mfa_denied':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getActionIcon(String action) {
    switch (action.toLowerCase()) {
      case 'login':
        return Icons.login;
      case 'login_failed':
        return Icons.error;
      case 'logout':
        return Icons.logout;
      case 'policy_violation':
        return Icons.warning;
      case 'mfa_approved':
        return Icons.check;
      case 'mfa_denied':
        return Icons.close;
      default:
        return Icons.info;
    }
  }
}

// Providers for state management
final dashboardProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getDashboardData();
});

final mfaRequestsProvider = FutureProvider<List<MFARequest>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getMFARequests();
});

final devicesProvider = FutureProvider<List<UserDevice>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getDevices();
});

final sessionsProvider = FutureProvider<List<UserSession>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getSessions();
});
