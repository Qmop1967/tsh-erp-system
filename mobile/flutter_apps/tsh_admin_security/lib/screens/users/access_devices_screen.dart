import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/user_management_service.dart';

/// Access Devices Screen
/// Allows admins to manage user's trusted devices
class AccessDevicesScreen extends StatefulWidget {
  final int userId;
  final String userName;

  const AccessDevicesScreen({
    Key? key,
    required this.userId,
    required this.userName,
  }) : super(key: key);

  @override
  State<AccessDevicesScreen> createState() => _AccessDevicesScreenState();
}

class _AccessDevicesScreenState extends State<AccessDevicesScreen> {
  final UserManagementService _service = UserManagementService();

  List<Map<String, dynamic>> _devices = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDevices();
  }

  Future<void> _loadDevices() async {
    setState(() => _isLoading = true);
    try {
      final devices = await _service.getUserTrustedDevices(widget.userId);
      setState(() {
        _devices = devices;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showError('Failed to load devices: $e');
    }
  }

  Future<void> _revokeDevice(String deviceId, String deviceName) async {
    final confirmed = await _showConfirmDialog(
      'Revoke Trust',
      'Are you sure you want to revoke trust for "$deviceName"? The user will need to re-authenticate on this device.',
    );

    if (confirmed != true) return;

    try {
      await _service.revokeTrustedDevice(widget.userId, deviceId);
      await _loadDevices();
      _showSuccess('Device trust revoked successfully');
    } catch (e) {
      _showError('Failed to revoke device: $e');
    }
  }

  Future<void> _addDevice() async {
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => _AddDeviceDialog(),
    );

    if (result == null) return;

    try {
      await _service.addTrustedDevice(widget.userId, result);
      await _loadDevices();
      _showSuccess('Device added successfully');
    } catch (e) {
      _showError('Failed to add device: $e');
    }
  }

  Future<bool?> _showConfirmDialog(String title, String message) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: const Text('Revoke', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: const Color(0xFF10B981),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFFF59E0B),
        title: const Text(
          'Trusted Devices',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add, color: Colors.white),
            onPressed: _addDevice,
            tooltip: 'Add Device',
          ),
        ],
      ),
      body: Column(
        children: [
          // User Info Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFFF59E0B),
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
                  'Managing devices for:',
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
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.devices, color: Colors.white, size: 16),
                      const SizedBox(width: 6),
                      Text(
                        '${_devices.length} trusted devices',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Devices List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _devices.isEmpty
                    ? _buildEmptyState()
                    : _buildDevicesList(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _addDevice,
        backgroundColor: const Color(0xFFF59E0B),
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text(
          'Add Device',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  Widget _buildDevicesList() {
    return RefreshIndicator(
      onRefresh: _loadDevices,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _devices.length,
        itemBuilder: (context, index) {
          final device = _devices[index];
          return _buildDeviceCard(device);
        },
      ),
    );
  }

  Widget _buildDeviceCard(Map<String, dynamic> device) {
    final deviceType = device['device_type'] ?? 'unknown';
    final deviceName = device['device_name'] ?? 'Unknown Device';
    final deviceId = device['device_id'] ?? '';
    final isTrusted = device['is_trusted'] ?? false;
    final lastSeenAt = device['last_seen_at'] != null
        ? DateTime.parse(device['last_seen_at'])
        : null;
    final trustExpiresAt = device['trust_expires_at'] != null
        ? DateTime.parse(device['trust_expires_at'])
        : null;

    final deviceColor = _getDeviceTypeColor(deviceType);
    final statusColor = isTrusted ? const Color(0xFF10B981) : const Color(0xFFEF4444);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
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
        children: [
          // Device Header
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Device Icon
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: deviceColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getDeviceTypeIcon(deviceType),
                    color: deviceColor,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),

                // Device Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              deviceName,
                              style: const TextStyle(
                                fontSize: 16,
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
                              color: statusColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  isTrusted ? Icons.check_circle : Icons.block,
                                  size: 12,
                                  color: statusColor,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  isTrusted ? 'TRUSTED' : 'REVOKED',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: statusColor,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Icon(Icons.smartphone, size: 14, color: Colors.grey[500]),
                          const SizedBox(width: 4),
                          Text(
                            _getDeviceTypeLabel(deviceType),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(width: 16),
                          if (lastSeenAt != null) ...[
                            Icon(Icons.access_time, size: 14, color: Colors.grey[500]),
                            const SizedBox(width: 4),
                            Text(
                              _formatLastSeen(lastSeenAt),
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Device Details
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
            ),
            child: Column(
              children: [
                // Device ID
                Row(
                  children: [
                    Icon(Icons.fingerprint, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      'Device ID:',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[700],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        deviceId,
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.grey[600],
                          fontFamily: 'monospace',
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),

                // Trust Expiry
                if (trustExpiresAt != null && isTrusted) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.schedule, size: 16, color: Colors.grey[600]),
                      const SizedBox(width: 8),
                      Text(
                        'Trust expires:',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[700],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        DateFormat('MMM dd, yyyy').format(trustExpiresAt),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],

                // Actions
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: isTrusted
                            ? () => _revokeDevice(deviceId, deviceName)
                            : null,
                        icon: const Icon(Icons.block, size: 16),
                        label: const Text('Revoke Trust'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFFEF4444),
                          side: const BorderSide(color: Color(0xFFEF4444)),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.devices_other,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'No trusted devices',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Add a device to allow automatic login',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _addDevice,
            icon: const Icon(Icons.add),
            label: const Text('Add First Device'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF59E0B),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getDeviceTypeLabel(String deviceType) {
    switch (deviceType.toLowerCase()) {
      case 'ios':
        return 'iPhone/iPad';
      case 'android':
        return 'Android Device';
      case 'web':
        return 'Web Browser';
      case 'desktop':
        return 'Desktop';
      default:
        return deviceType;
    }
  }

  IconData _getDeviceTypeIcon(String deviceType) {
    switch (deviceType.toLowerCase()) {
      case 'ios':
        return Icons.phone_iphone;
      case 'android':
        return Icons.phone_android;
      case 'web':
        return Icons.web;
      case 'desktop':
        return Icons.computer;
      case 'tablet':
        return Icons.tablet;
      default:
        return Icons.devices;
    }
  }

  Color _getDeviceTypeColor(String deviceType) {
    switch (deviceType.toLowerCase()) {
      case 'ios':
        return const Color(0xFF2563EB);
      case 'android':
        return const Color(0xFF10B981);
      case 'web':
        return const Color(0xFF8B5CF6);
      case 'desktop':
        return const Color(0xFFF59E0B);
      case 'tablet':
        return const Color(0xFFEF4444);
      default:
        return const Color(0xFF6B7280);
    }
  }

  String _formatLastSeen(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return DateFormat('MMM dd').format(dateTime);
    }
  }
}

/// Add Device Dialog
class _AddDeviceDialog extends StatefulWidget {
  @override
  State<_AddDeviceDialog> createState() => _AddDeviceDialogState();
}

class _AddDeviceDialogState extends State<_AddDeviceDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _deviceIdController = TextEditingController();
  String _selectedType = 'android';

  final List<Map<String, dynamic>> _deviceTypes = [
    {'value': 'android', 'label': 'Android Device', 'icon': Icons.phone_android},
    {'value': 'ios', 'label': 'iPhone/iPad', 'icon': Icons.phone_iphone},
    {'value': 'web', 'label': 'Web Browser', 'icon': Icons.web},
    {'value': 'desktop', 'label': 'Desktop', 'icon': Icons.computer},
    {'value': 'tablet', 'label': 'Tablet', 'icon': Icons.tablet},
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _deviceIdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add Trusted Device'),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Device Name
              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: 'Device Name',
                  hintText: 'e.g., John\'s iPhone',
                  prefixIcon: const Icon(Icons.devices),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter device name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Device ID
              TextFormField(
                controller: _deviceIdController,
                decoration: InputDecoration(
                  labelText: 'Device ID',
                  hintText: 'Unique device identifier',
                  prefixIcon: const Icon(Icons.fingerprint),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter device ID';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Device Type
              DropdownButtonFormField<String>(
                value: _selectedType,
                decoration: InputDecoration(
                  labelText: 'Device Type',
                  prefixIcon: const Icon(Icons.category),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                items: _deviceTypes.map((type) {
                  return DropdownMenuItem<String>(
                    value: type['value'],
                    child: Row(
                      children: [
                        Icon(type['icon'], size: 20),
                        const SizedBox(width: 12),
                        Text(type['label']),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedType = value!;
                  });
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            if (_formKey.currentState!.validate()) {
              Navigator.pop(context, {
                'device_name': _nameController.text,
                'device_id': _deviceIdController.text,
                'device_type': _selectedType,
              });
            }
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFF59E0B),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text('Add Device', style: TextStyle(color: Colors.white)),
        ),
      ],
    );
  }
}
