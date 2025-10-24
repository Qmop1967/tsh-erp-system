import 'package:flutter/material.dart';
import '../services/notification_service.dart';
import 'notification_center_screen.dart';

class EnhancedInventoryDashboardScreen extends StatefulWidget {
  const EnhancedInventoryDashboardScreen({super.key});

  @override
  State<EnhancedInventoryDashboardScreen> createState() => _EnhancedInventoryDashboardScreenState();
}

class _EnhancedInventoryDashboardScreenState extends State<EnhancedInventoryDashboardScreen> {
  final NotificationService _notificationService = NotificationService();
  int _unreadNotificationCount = 0;

  // Sample data - in real implementation, this would come from API
  final Map<String, dynamic> _dashboardData = {
    'pendingSalesOrders': 24,
    'oddItemsQuantity': 156,
    'fullBoxItemsQuantity': 89,
    'preparedBoxes': 12,
    'shippedBoxesPending': 8,
    'deliveryCompletionRate': 85.5,
  };

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
    _loadUnreadNotificationCount();
  }

  Future<void> _loadDashboardData() async {
    // TODO: Load real-time data from API
    setState(() {
      // Data loaded
    });
  }

  Future<void> _loadUnreadNotificationCount() async {
    try {
      final count = await _notificationService.getUnreadCount();
      setState(() {
        _unreadNotificationCount = count;
      });
    } catch (e) {
      // Silently fail - notifications are not critical
    }
  }

  void _openNotificationCenter() async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const NotificationCenterScreen(),
      ),
    );
    // Refresh unread count when returning from notification center
    _loadUnreadNotificationCount();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🧭 Inventory Dashboard'),
            Text(
              'Real-time Overview & KPIs',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        actions: [
          // Notification bell with badge
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications),
                onPressed: _openNotificationCenter,
                tooltip: 'Notifications',
              ),
              if (_unreadNotificationCount > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 18,
                      minHeight: 18,
                    ),
                    child: Text(
                      _unreadNotificationCount > 99
                          ? '99+'
                          : '$_unreadNotificationCount',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboardData,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboardData,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildQuickActionsSection(),
              const SizedBox(height: 20),
              _buildKPICardsSection(),
              const SizedBox(height: 20),
              _buildPackagingVariantsSection(),
              const SizedBox(height: 20),
              _buildProgressSection(),
              const SizedBox(height: 20),
              _buildRecentActivitySection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quick Actions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(context, '/sales-orders');
                    },
                    icon: const Icon(Icons.inventory_2),
                    label: const Text('View Orders to Pack'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.teal,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(context, '/shipments');
                    },
                    icon: const Icon(Icons.local_shipping),
                    label: const Text('Manage Shipments'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
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

  Widget _buildKPICardsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Key Performance Indicators',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.2,
          children: [
            _buildKPICard(
              '📋 Pending Sales Orders',
              '${_dashboardData['pendingSalesOrders']}',
              'Orders to prepare',
              Colors.blue,
              Icons.pending_actions,
            ),
            _buildKPICard(
              '📦 Odd Items to Prepare',
              '${_dashboardData['oddItemsQuantity']}',
              'Individual items',
              Colors.orange,
              Icons.inventory,
            ),
            _buildKPICard(
              '📦 Full Box Items',
              '${_dashboardData['fullBoxItemsQuantity']}',
              'Complete boxes',
              Colors.green,
              Icons.all_inbox,
            ),
            _buildKPICard(
              '✅ Prepared Boxes',
              '${_dashboardData['preparedBoxes']}',
              'Ready for shipment',
              Colors.teal,
              Icons.check_box,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildKPICard(String title, String value, String subtitle, Color color, IconData icon) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 2,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              subtitle,
              style: const TextStyle(fontSize: 10, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Shipment & Delivery Progress',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildProgressItem(
              '🚛 Shipped Boxes Pending Delivery',
              _dashboardData['shippedBoxesPending'],
              Colors.amber,
            ),
            const SizedBox(height: 12),
            _buildProgressItem(
              '🎯 Delivery Completion Rate',
              '${_dashboardData['deliveryCompletionRate']}%',
              Colors.green,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressItem(String title, dynamic value, Color color) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 4),
              Text(
                value.toString(),
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        ),
        CircleAvatar(
          backgroundColor: color.withOpacity(0.2),
          child: Text(
            value.toString().split('.')[0],
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRecentActivitySection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Recent Activity',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () {
                    // Navigate to full activity log
                  },
                  child: const Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildActivityItem(
              '📦 New sales order #SO-2024-1245 received',
              '5 minutes ago',
              Icons.new_releases,
              Colors.blue,
            ),
            _buildActivityItem(
              '✅ Order #SO-2024-1244 packed and ready',
              '15 minutes ago',
              Icons.check_circle,
              Colors.green,
            ),
            _buildActivityItem(
              '🚛 Shipment #SH-2024-089 dispatched',
              '1 hour ago',
              Icons.local_shipping,
              Colors.orange,
            ),
            _buildActivityItem(
              '📥 Purchase order #PO-2024-567 received',
              '2 hours ago',
              Icons.shopping_cart,
              Colors.teal,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityItem(String title, String time, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: color.withOpacity(0.2),
            child: Icon(icon, color: color, size: 16),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                ),
                Text(
                  time,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPackagingVariantsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🧃 Packaging Variants & Details',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Current packaging options available for products',
              style: TextStyle(color: Colors.grey, fontSize: 14),
            ),
            const SizedBox(height: 16),
            _buildPackagingVariantItem(
              'USB Cable Type-C',
              [
                {'type': 'Box', 'color': 'White', 'size': '10cm', 'specs': '1-pack'},
                {'type': 'Bundle', 'color': 'Black', 'size': '15cm', 'specs': '5-pack'},
                {'type': 'Bag', 'color': 'Clear', 'size': '20cm', 'specs': '10-pack'},
              ],
            ),
            const Divider(),
            _buildPackagingVariantItem(
              'Wireless Charger Pad',
              [
                {'type': 'Box', 'color': 'Premium White', 'size': '12x12cm', 'specs': 'Individual'},
                {'type': 'Bundle', 'color': 'Retail Package', 'size': '15x20cm', 'specs': '3-pack'},
              ],
            ),
            const Divider(),
            _buildPackagingVariantItem(
              'Phone Cases (Mixed)',
              [
                {'type': 'Box', 'color': 'Transparent', 'size': 'Standard', 'specs': 'iPhone 14'},
                {'type': 'Box', 'color': 'Black', 'size': 'Standard', 'specs': 'Samsung S23'},
                {'type': 'Bundle', 'color': 'Mixed Colors', 'size': 'Bulk', 'specs': 'Various Models'},
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue.shade700),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Clear packaging labeling helps TSH Salesperson Users and customers ensure accurate delivery',
                      style: TextStyle(
                        color: Colors.blue.shade700,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPackagingVariantItem(String productName, List<Map<String, String>> variants) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            productName,
            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: variants.map((variant) {
              MaterialColor getVariantColor(String type) {
                switch (type.toLowerCase()) {
                  case 'box':
                    return Colors.green;
                  case 'bundle':
                    return Colors.orange;
                  case 'bag':
                    return Colors.blue;
                  default:
                    return Colors.grey;
                }
              }

              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: getVariantColor(variant['type']!).shade100,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: getVariantColor(variant['type']!).shade300),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      variant['type'] == 'Box' ? Icons.inventory_2 :
                      variant['type'] == 'Bundle' ? Icons.category :
                      Icons.shopping_bag,
                      size: 14,
                      color: getVariantColor(variant['type']!).shade700,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${variant['type']} - ${variant['color']} (${variant['specs']})',
                      style: TextStyle(
                        fontSize: 12,
                        color: getVariantColor(variant['type']!).shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
