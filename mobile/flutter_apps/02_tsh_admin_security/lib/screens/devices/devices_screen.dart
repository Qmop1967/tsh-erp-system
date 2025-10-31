import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/device.dart';
import '../../services/device_service.dart';

class DevicesScreen extends StatefulWidget {
  const DevicesScreen({super.key});

  @override
  State<DevicesScreen> createState() => _DevicesScreenState();
}

class _DevicesScreenState extends State<DevicesScreen> {
  final DeviceService _deviceService = DeviceService();
  List<UserDevice> _devices = [];
  bool _isLoading = true;
  String? _statusFilter;

  @override
  void initState() {
    super.initState();
    _loadDevices();
  }

  Future<void> _loadDevices() async {
    setState(() => _isLoading = true);
    try {
      final devices = await _deviceService.getDevices(status: _statusFilter);
      setState(() {
        _devices = devices;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading devices: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _updateDeviceStatus(UserDevice device, String status) async {
    try {
      await _deviceService.updateDeviceStatus(device.id, status);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Device ${status.toLowerCase()} successfully'),
            backgroundColor: Colors.green,
          ),
        );
        _loadDevices();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error updating device: $e'),
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
        title: const Text('Filter Devices'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: const Text('All Devices'),
              leading: Radio<String?>(
                value: null,
                groupValue: _statusFilter,
                onChanged: (value) {
                  setState(() => _statusFilter = value);
                  Navigator.pop(context);
                  _loadDevices();
                },
              ),
            ),
            ListTile(
              title: const Text('Approved'),
              leading: Radio<String?>(
                value: 'approved',
                groupValue: _statusFilter,
                onChanged: (value) {
                  setState(() => _statusFilter = value);
                  Navigator.pop(context);
                  _loadDevices();
                },
              ),
            ),
            ListTile(
              title: const Text('Pending'),
              leading: Radio<String?>(
                value: 'pending',
                groupValue: _statusFilter,
                onChanged: (value) {
                  setState(() => _statusFilter = value);
                  Navigator.pop(context);
                  _loadDevices();
                },
              ),
            ),
            ListTile(
              title: const Text('Blocked'),
              leading: Radio<String?>(
                value: 'blocked',
                groupValue: _statusFilter,
                onChanged: (value) {
                  setState(() => _statusFilter = value);
                  Navigator.pop(context);
                  _loadDevices();
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'approved':
        return const Color(0xff10b981);
      case 'pending':
        return const Color(0xfff59e0b);
      case 'blocked':
        return const Color(0xffef4444);
      default:
        return Colors.grey;
    }
  }

  IconData _getDeviceIcon(String? deviceType) {
    switch (deviceType?.toLowerCase()) {
      case 'mobile':
        return Icons.phone_android;
      case 'tablet':
        return Icons.tablet;
      case 'desktop':
        return Icons.computer;
      default:
        return Icons.devices;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xff10b981),
        foregroundColor: Colors.white,
        title: const Text(
          'Device Management',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
            tooltip: 'Filter',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDevices,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _devices.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.devices_other_outlined, size: 64, color: Colors.grey[400]),
                      const SizedBox(height: 16),
                      Text(
                        'No devices found',
                        style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadDevices,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _devices.length,
                    itemBuilder: (context, index) {
                      final device = _devices[index];
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
                        child: ExpansionTile(
                          leading: Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              color: const Color(0xff10b981).withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              _getDeviceIcon(device.deviceType),
                              color: const Color(0xff10b981),
                              size: 28,
                            ),
                          ),
                          title: Text(
                            device.displayName,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Color(0xff1f2937),
                            ),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 4),
                              Text(
                                '${device.platform ?? 'Unknown'} - ${device.browser ?? 'Unknown'}',
                                style: TextStyle(fontSize: 13, color: Colors.grey[600]),
                              ),
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: _getStatusColor(device.status).withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Container(
                                      width: 6,
                                      height: 6,
                                      decoration: BoxDecoration(
                                        color: _getStatusColor(device.status),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    const SizedBox(width: 6),
                                    Text(
                                      device.status.toUpperCase(),
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: _getStatusColor(device.status),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  _InfoRow(
                                    icon: Icons.fingerprint,
                                    label: 'Device ID',
                                    value: device.id,
                                  ),
                                  if (device.lastIpAddress != null) ...[
                                    const SizedBox(height: 8),
                                    _InfoRow(
                                      icon: Icons.location_on_outlined,
                                      label: 'IP Address',
                                      value: device.lastIpAddress!,
                                    ),
                                  ],
                                  if (device.lastSeen != null) ...[
                                    const SizedBox(height: 8),
                                    _InfoRow(
                                      icon: Icons.access_time,
                                      label: 'Last Seen',
                                      value: DateFormat('MMM dd, yyyy HH:mm').format(device.lastSeen!),
                                    ),
                                  ],
                                  const SizedBox(height: 16),
                                  Wrap(
                                    spacing: 8,
                                    runSpacing: 8,
                                    children: [
                                      if (device.status.toLowerCase() == 'pending')
                                        ElevatedButton.icon(
                                          onPressed: () => _updateDeviceStatus(device, 'approved'),
                                          icon: const Icon(Icons.check, size: 18),
                                          label: const Text('Approve'),
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(0xff10b981),
                                            foregroundColor: Colors.white,
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 16,
                                              vertical: 8,
                                            ),
                                          ),
                                        ),
                                      if (device.status.toLowerCase() != 'blocked')
                                        ElevatedButton.icon(
                                          onPressed: () => _updateDeviceStatus(device, 'blocked'),
                                          icon: const Icon(Icons.block, size: 18),
                                          label: const Text('Block'),
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(0xffef4444),
                                            foregroundColor: Colors.white,
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 16,
                                              vertical: 8,
                                            ),
                                          ),
                                        ),
                                      if (device.status.toLowerCase() == 'blocked')
                                        ElevatedButton.icon(
                                          onPressed: () => _updateDeviceStatus(device, 'approved'),
                                          icon: const Icon(Icons.check_circle, size: 18),
                                          label: const Text('Unblock'),
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(0xff10b981),
                                            foregroundColor: Colors.white,
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 16,
                                              vertical: 8,
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
                    },
                  ),
                ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey[600]),
        const SizedBox(width: 8),
        Text(
          '$label: ',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              color: Color(0xff1f2937),
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}
