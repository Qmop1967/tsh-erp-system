import 'package:flutter/material.dart';

class SalesOrdersPackingScreen extends StatefulWidget {
  const SalesOrdersPackingScreen({super.key});

  @override
  State<SalesOrdersPackingScreen> createState() => _SalesOrdersPackingScreenState();
}

class _SalesOrdersPackingScreenState extends State<SalesOrdersPackingScreen> {
  List<Map<String, dynamic>> _unpreparedOrders = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUnpreparedOrders();
  }

  Future<void> _loadUnpreparedOrders() async {
    setState(() => _isLoading = true);
    
    // Sample data - in real implementation, this would come from API
    await Future.delayed(const Duration(seconds: 1));
    
    setState(() {
      _unpreparedOrders = [
        {
          'orderId': 'SO-2024-1245',
          'customerName': 'Ahmed Electronics Store',
          'customerAddress': 'Al-Mansour District, Baghdad, Iraq',
          'orderDate': DateTime.now().subtract(const Duration(days: 2)),
          'priority': 'High',
          'itemsCount': 5,
          'totalQuantity': 23,
          'cartonCount': 0,
          'items': [
            {
              'productName': 'iPhone 15 Pro Case',
              'requiredQuantity': 10,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': 'Blue, Silicone, Premium',
              'packagingType': 'Box'
            },
            {
              'productName': 'Samsung Galaxy Charger',
              'requiredQuantity': 5,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': 'Fast Charging, 25W',
              'packagingType': 'Bundle'
            },
            {
              'productName': 'Bluetooth Headphones',
              'requiredQuantity': 3,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': 'Black, Wireless, Sony',
              'packagingType': 'Box'
            },
            {
              'productName': 'Phone Screen Protector',
              'requiredQuantity': 3,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': 'Tempered Glass, Clear',
              'packagingType': 'Bag'
            },
            {
              'productName': 'USB-C Cable',
              'requiredQuantity': 2,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': '1.5m, Fast Data Transfer',
              'packagingType': 'Bundle'
            },
          ]
        },
        {
          'orderId': 'SO-2024-1244',
          'customerName': 'Tech Solutions Ltd',
          'customerAddress': 'Karrada, Baghdad, Iraq',
          'orderDate': DateTime.now().subtract(const Duration(days: 1)),
          'priority': 'Medium',
          'itemsCount': 3,
          'totalQuantity': 15,
          'cartonCount': 1,
          'items': [
            {
              'productName': 'Laptop Stand',
              'requiredQuantity': 8,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': 'Aluminum, Adjustable',
              'packagingType': 'Box'
            },
            {
              'productName': 'Wireless Mouse',
              'requiredQuantity': 4,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': 'Black, Ergonomic',
              'packagingType': 'Box'
            },
            {
              'productName': 'Keyboard Cover',
              'requiredQuantity': 3,
              'packedQuantity': 0,
              'imageUrl': 'https://via.placeholder.com/100',
              'variant': 'Clear, MacBook Pro',
              'packagingType': 'Bag'
            },
          ]
        },
      ];
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('📦 Sales Orders to Pack'),
            Text(
              'Prepare orders for shipment',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadUnpreparedOrders,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadUnpreparedOrders,
              child: _unpreparedOrders.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.check_circle, size: 64, color: Colors.green),
                          SizedBox(height: 16),
                          Text(
                            'All orders are packed! 🎉',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          Text('No pending orders to prepare'),
                        ],
                      ),
                    )
                  : Column(
                      children: [
                        _buildSummaryCard(),
                        Expanded(
                          child: ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _unpreparedOrders.length,
                            itemBuilder: (context, index) => _buildOrderCard(_unpreparedOrders[index]),
                          ),
                        ),
                      ],
                    ),
            ),
    );
  }

  Widget _buildSummaryCard() {
    final totalOrders = _unpreparedOrders.length;
    final totalItems = _unpreparedOrders.fold<int>(0, (sum, order) => sum + (order['itemsCount'] as int));
    final totalQuantity = _unpreparedOrders.fold<int>(0, (sum, order) => sum + (order['totalQuantity'] as int));

    return Container(
      margin: const EdgeInsets.all(16),
      child: Card(
        color: Colors.teal[50],
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(Icons.inventory_2, color: Colors.teal[700], size: 32),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Orders to Prepare',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.teal[700],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text('$totalOrders orders • $totalItems items • $totalQuantity total qty'),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOrderCard(Map<String, dynamic> order) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: _getPriorityColor(order['priority']),
          child: Text(
            order['orderId'].toString().split('-').last.substring(0, 2),
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
        title: Text(
          order['orderId'],
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Customer: ${order['customerName']}'),
            Text('Items: ${order['itemsCount']} • Qty: ${order['totalQuantity']}'),
            Text('Cartons: ${order['cartonCount']}'),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildOrderDetails(order),
                const SizedBox(height: 16),
                _buildItemsList(order['items']),
                const SizedBox(height: 16),
                _buildPackingActions(order),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOrderDetails(Map<String, dynamic> order) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.person, size: 16),
              const SizedBox(width: 8),
              Expanded(child: Text('Customer: ${order['customerName']}')),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.location_on, size: 16),
              const SizedBox(width: 8),
              Expanded(child: Text('Address: ${order['customerAddress']}')),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.calendar_today, size: 16),
              const SizedBox(width: 8),
              Text('Order Date: ${_formatDate(order['orderDate'])}'),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: _getPriorityColor(order['priority']),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${order['priority']} Priority',
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildItemsList(List<dynamic> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Items to Pack:',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 8),
        ...items.map((item) => _buildItemCard(item)).toList(),
      ],
    );
  }

  Widget _buildItemCard(Map<String, dynamic> item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.network(
              item['imageUrl'],
              width: 60,
              height: 60,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => Container(
                width: 60,
                height: 60,
                color: Colors.grey[300],
                child: const Icon(Icons.image, color: Colors.grey),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item['productName'],
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  'Variant: ${item['variant']}',
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: _getPackagingColor(item['packagingType']),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        item['packagingType'],
                        style: const TextStyle(fontSize: 10, color: Colors.white),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Qty: ${item['requiredQuantity']}',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
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

  Widget _buildPackingActions(Map<String, dynamic> order) {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () => _startPacking(order),
            icon: const Icon(Icons.play_arrow),
            label: const Text('Start Packing'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(width: 12),
        ElevatedButton.icon(
          onPressed: () => _viewOrderDetails(order),
          icon: const Icon(Icons.visibility),
          label: const Text('Details'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.grey[600],
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 12),
          ),
        ),
      ],
    );
  }

  Color _getPriorityColor(String priority) {
    switch (priority.toLowerCase()) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Color _getPackagingColor(String packageType) {
    switch (packageType.toLowerCase()) {
      case 'box':
        return Colors.brown;
      case 'bundle':
        return Colors.blue;
      case 'bag':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  void _startPacking(Map<String, dynamic> order) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PackingWorkflowScreen(order: order),
      ),
    );
  }

  void _viewOrderDetails(Map<String, dynamic> order) {
    showDialog(
      context: context,
      builder: (context) => OrderDetailsDialog(order: order),
    );
  }
}

// Packing Workflow Screen
class PackingWorkflowScreen extends StatefulWidget {
  final Map<String, dynamic> order;

  const PackingWorkflowScreen({super.key, required this.order});

  @override
  State<PackingWorkflowScreen> createState() => _PackingWorkflowScreenState();
}

class _PackingWorkflowScreenState extends State<PackingWorkflowScreen> {
  int _currentItemIndex = 0;
  List<Map<String, dynamic>> _cartons = [];
  Map<String, int> _packedQuantities = {};

  @override
  void initState() {
    super.initState();
    _initializePacking();
  }

  void _initializePacking() {
    for (var item in widget.order['items']) {
      _packedQuantities[item['productName']] = 0;
    }
  }

  @override
  Widget build(BuildContext context) {
    final items = widget.order['items'] as List<dynamic>;
    final currentItem = items[_currentItemIndex];

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Packing: ${widget.order['orderId']}'),
            Text(
              'Item ${_currentItemIndex + 1} of ${items.length}',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildProgressIndicator(items.length),
            const SizedBox(height: 20),
            _buildCurrentItemCard(currentItem),
            const SizedBox(height: 20),
            _buildQuantityInput(currentItem),
            const Spacer(),
            _buildNavigationButtons(items.length),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressIndicator(int totalItems) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Packing Progress',
                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.teal[700]),
                ),
                Text('${_currentItemIndex + 1}/$totalItems'),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: (_currentItemIndex + 1) / totalItems,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(Colors.teal),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentItemCard(Map<String, dynamic> item) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    item['imageUrl'],
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Container(
                      width: 80,
                      height: 80,
                      color: Colors.grey[300],
                      child: const Icon(Icons.image, color: Colors.grey),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item['productName'],
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Variant: ${item['variant']}',
                        style: const TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: _getPackagingColor(item['packagingType']),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              item['packagingType'],
                              style: const TextStyle(fontSize: 12, color: Colors.white),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Required: ${item['requiredQuantity']}',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Enhanced Packaging Variants Section
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.inventory_2, color: Colors.blue.shade700, size: 18),
                      const SizedBox(width: 8),
                      Text(
                        'Packaging Variants Available:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.blue.shade700,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  _buildPackagingVariants(item),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPackagingVariants(Map<String, dynamic> item) {
    // Sample packaging variants based on the item type
    List<Map<String, String>> variants = _getItemPackagingVariants(item['productName']);
    
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: variants.map((variant) {
        bool isSelected = variant['type'] == item['packagingType'];
        Color variantColor = _getPackagingColor(variant['type']!);
        
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: isSelected ? variantColor : variantColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? variantColor : variantColor.withOpacity(0.3),
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                variant['type'] == 'Box' ? Icons.inventory_2 :
                variant['type'] == 'Bundle' ? Icons.category :
                Icons.shopping_bag,
                size: 14,
                color: isSelected ? Colors.white : variantColor,
              ),
              const SizedBox(width: 4),
              Text(
                '${variant['type']}: ${variant['description']}',
                style: TextStyle(
                  fontSize: 11,
                  color: isSelected ? Colors.white : variantColor,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
              if (isSelected) ...[
                const SizedBox(width: 4),
                Icon(
                  Icons.check_circle,
                  size: 14,
                  color: Colors.white,
                ),
              ],
            ],
          ),
        );
      }).toList(),
    );
  }

  List<Map<String, String>> _getItemPackagingVariants(String productName) {
    // Return different packaging options based on the product
    switch (productName.toLowerCase()) {
      case 'usb-c cable':
        return [
          {'type': 'Box', 'description': 'Individual Premium White'},
          {'type': 'Bundle', 'description': '5-pack Retail Black'},
          {'type': 'Bag', 'description': '10-pack Bulk Clear'},
        ];
      case 'laptop stand':
        return [
          {'type': 'Box', 'description': 'Individual with Manual'},
          {'type': 'Bundle', 'description': '3-pack Commercial'},
        ];
      case 'wireless mouse':
        return [
          {'type': 'Box', 'description': 'Retail Packaging'},
          {'type': 'Bundle', 'description': '2-pack Office Set'},
          {'type': 'Bag', 'description': 'Bulk OEM'},
        ];
      case 'wireless charger':
        return [
          {'type': 'Box', 'description': 'Premium Individual'},
          {'type': 'Bundle', 'description': '2-pack Family Set'},
        ];
      case 'bluetooth headphones':
        return [
          {'type': 'Box', 'description': 'High-end Retail'},
          {'type': 'Bundle', 'description': '2-pack Discount'},
        ];
      default:
        return [
          {'type': 'Box', 'description': 'Standard Individual'},
          {'type': 'Bundle', 'description': 'Multi-pack'},
          {'type': 'Bag', 'description': 'Bulk Package'},
        ];
    }
  }

  Widget _buildQuantityInput(Map<String, dynamic> item) {
    final controller = TextEditingController(
      text: _packedQuantities[item['productName']].toString(),
    );

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter Packed Quantity:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: controller,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Packed Quantity',
                      border: OutlineInputBorder(),
                    ),
                    onChanged: (value) {
                      final quantity = int.tryParse(value) ?? 0;
                      setState(() {
                        _packedQuantities[item['productName']] = quantity;
                      });
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  children: [
                    IconButton(
                      onPressed: () {
                        final current = _packedQuantities[item['productName']] ?? 0;
                        if (current < item['requiredQuantity']) {
                          setState(() {
                            _packedQuantities[item['productName']] = current + 1;
                            controller.text = (current + 1).toString();
                          });
                        }
                      },
                      icon: const Icon(Icons.add),
                      style: IconButton.styleFrom(backgroundColor: Colors.teal),
                    ),
                    IconButton(
                      onPressed: () {
                        final current = _packedQuantities[item['productName']] ?? 0;
                        if (current > 0) {
                          setState(() {
                            _packedQuantities[item['productName']] = current - 1;
                            controller.text = (current - 1).toString();
                          });
                        }
                      },
                      icon: const Icon(Icons.remove),
                      style: IconButton.styleFrom(backgroundColor: Colors.grey),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavigationButtons(int totalItems) {
    return Row(
      children: [
        if (_currentItemIndex > 0)
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () {
                setState(() {
                  _currentItemIndex--;
                });
              },
              icon: const Icon(Icons.arrow_back),
              label: const Text('Previous'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[600],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        if (_currentItemIndex > 0) const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _currentItemIndex < totalItems - 1 ? _nextItem : _completePacking,
            icon: Icon(_currentItemIndex < totalItems - 1 ? Icons.arrow_forward : Icons.check),
            label: Text(_currentItemIndex < totalItems - 1 ? 'Next Item' : 'Complete'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
      ],
    );
  }

  Color _getPackagingColor(String packageType) {
    switch (packageType.toLowerCase()) {
      case 'box':
        return Colors.brown;
      case 'bundle':
        return Colors.blue;
      case 'bag':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  void _nextItem() {
    setState(() {
      _currentItemIndex++;
    });
  }

  void _completePacking() {
    // Generate carton number and complete packing
    final cartonNumber = 'CTN-${DateTime.now().millisecondsSinceEpoch}';
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Packing Complete! ✅'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Carton Number: $cartonNumber'),
            const SizedBox(height: 16),
            const Text('Order has been packed successfully and is ready for shipment.'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Go back to orders list
            },
            child: const Text('Print Label'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Go back to orders list
            },
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }
}

// Order Details Dialog
class OrderDetailsDialog extends StatelessWidget {
  final Map<String, dynamic> order;

  const OrderDetailsDialog({super.key, required this.order});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Order ${order['orderId']}'),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Customer: ${order['customerName']}'),
            Text('Address: ${order['customerAddress']}'),
            Text('Items: ${order['itemsCount']}'),
            Text('Total Quantity: ${order['totalQuantity']}'),
            Text('Cartons: ${order['cartonCount']}'),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Close'),
        ),
      ],
    );
  }
}
