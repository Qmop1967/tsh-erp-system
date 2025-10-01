import 'package:flutter/material.dart';

class EnhancedPurchaseOrdersScreen extends StatefulWidget {
  const EnhancedPurchaseOrdersScreen({Key? key}) : super(key: key);

  @override
  _EnhancedPurchaseOrdersScreenState createState() => _EnhancedPurchaseOrdersScreenState();
}

class _EnhancedPurchaseOrdersScreenState extends State<EnhancedPurchaseOrdersScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String userRole = 'inventory'; // 'inventory' or 'admin' - for permission-based display

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Purchase Orders'),
        backgroundColor: Colors.purple.shade700,
        elevation: 4,
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(
              icon: Icon(Icons.pending_actions),
              text: 'Pending',
            ),
            Tab(
              icon: Icon(Icons.check_circle),
              text: 'Received',
            ),
          ],
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
        ),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() {
                userRole = value;
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Switched to $value view'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'inventory',
                child: Text('Inventory User View'),
              ),
              PopupMenuItem(
                value: 'admin',
                child: Text('Admin User View'),
              ),
            ],
            icon: Icon(Icons.account_circle),
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildPendingTab(),
          _buildReceivedTab(),
        ],
      ),
      floatingActionButton: userRole == 'admin'
          ? FloatingActionButton.extended(
              onPressed: () => _showCreatePurchaseOrderDialog(),
              label: Text('Create PO'),
              icon: Icon(Icons.add),
              backgroundColor: Colors.purple.shade600,
            )
          : null,
    );
  }

  Widget _buildPendingTab() {
    return Container(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeaderCard(
            'Pending Purchase Orders',
            'Orders awaiting receipt and processing',
            Icons.pending_actions,
            Colors.orange,
          ),
          SizedBox(height: 20),
          Expanded(
            child: ListView.builder(
              itemCount: _getPendingPurchaseOrders().length,
              itemBuilder: (context, index) {
                final po = _getPendingPurchaseOrders()[index];
                return _buildPendingPOCard(po);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReceivedTab() {
    return Container(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeaderCard(
            'Received Purchase Orders',
            'Completed orders with auto-matching records',
            Icons.check_circle,
            Colors.green,
          ),
          SizedBox(height: 20),
          Expanded(
            child: ListView.builder(
              itemCount: _getReceivedPurchaseOrders().length,
              itemBuilder: (context, index) {
                final po = _getReceivedPurchaseOrders()[index];
                return _buildReceivedPOCard(po);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderCard(String title, String subtitle, IconData icon, MaterialColor color) {
    return Card(
      elevation: 6,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        padding: EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [color.shade600, color.shade800],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: Colors.white, size: 30),
            ),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 14,
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

  Widget _buildPendingPOCard(Map<String, dynamic> po) {
    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: InkWell(
        onTap: () => _showPODetails(po),
        borderRadius: BorderRadius.circular(10),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade600,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'PENDING',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Spacer(),
                  Text(
                    'PO: ${po['poNumber']}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 12),
              // Permission-based display
              if (userRole == 'admin')
                Text(
                  'Vendor: ${po['vendorName']}',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                )
              else
                Text(
                  'Vendor: [Admin Access Required]',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey.shade500,
                  ),
                ),
              SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 16, color: Colors.grey.shade600),
                  SizedBox(width: 4),
                  Text('Created: ${po['creationDate']}'),
                  Spacer(),
                  Icon(Icons.schedule, size: 16, color: Colors.grey.shade600),
                  SizedBox(width: 4),
                  Text('Expected: ${po['expectedDate']}'),
                ],
              ),
              SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.inventory_2, size: 16, color: Colors.grey.shade600),
                  SizedBox(width: 4),
                  Text('${po['itemCount']} items'),
                  Spacer(),
                  if (userRole == 'admin')
                    Text(
                      'Total: \$${po['totalValue']}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.green.shade700,
                      ),
                    )
                  else
                    Text(
                      'Total: [Admin Only]',
                      style: TextStyle(
                        color: Colors.grey.shade500,
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildReceivedPOCard(Map<String, dynamic> po) {
    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: InkWell(
        onTap: () => _showAutoMatchingMatrix(po),
        borderRadius: BorderRadius.circular(10),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green.shade600,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'RECEIVED',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Spacer(),
                  Text(
                    'PO: ${po['poNumber']}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 12),
              if (userRole == 'admin')
                Text(
                  'Vendor: ${po['vendorName']}',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                )
              else
                Text(
                  'Vendor: [Admin Access Required]',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey.shade500,
                  ),
                ),
              SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.check_circle, size: 16, color: Colors.green.shade600),
                  SizedBox(width: 4),
                  Text('Received: ${po['receivedDate']}'),
                  Spacer(),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: po['matchingStatus'] == 'Complete' ? Colors.green.shade100 : Colors.orange.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      'Matching: ${po['matchingStatus']}',
                      style: TextStyle(
                        fontSize: 12,
                        color: po['matchingStatus'] == 'Complete' ? Colors.green.shade700 : Colors.orange.shade700,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.inventory_2, size: 16, color: Colors.grey.shade600),
                  SizedBox(width: 4),
                  Text('${po['matchedItems']}/${po['totalItems']} items matched'),
                  Spacer(),
                  Text(
                    'Tap to view matrix',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.blue.shade600,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showPODetails(Map<String, dynamic> po) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Purchase Order Details'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('PO Number:', po['poNumber']),
              if (userRole == 'admin')
                _buildDetailRow('Vendor:', po['vendorName'])
              else
                _buildDetailRow('Vendor:', '[Admin Access Required]'),
              _buildDetailRow('Creation Date:', po['creationDate']),
              _buildDetailRow('Expected Date:', po['expectedDate']),
              _buildDetailRow('Items Count:', po['itemCount'].toString()),
              if (userRole == 'admin')
                _buildDetailRow('Total Value:', '\$${po['totalValue']}')
              else
                _buildDetailRow('Total Value:', '[Admin Only]'),
              SizedBox(height: 16),
              Text(
                'Items List:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              ...po['items'].map<Widget>((item) => Padding(
                padding: EdgeInsets.only(bottom: 4),
                child: Text('• ${item['name']} (Qty: ${item['quantity']})'),
              )).toList(),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
          if (po['status'] == 'pending')
            ElevatedButton(
              onPressed: () => _markAsReceived(po),
              child: Text('Mark as Received'),
            ),
        ],
      ),
    );
  }

  void _showAutoMatchingMatrix(Map<String, dynamic> po) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        child: Container(
          width: MediaQuery.of(context).size.width * 0.9,
          height: MediaQuery.of(context).size.height * 0.8,
          padding: EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    'Auto-Matching Matrix',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  Spacer(),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: Icon(Icons.close),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Text(
                'PO: ${po['poNumber']} - ${po['vendorName']}',
                style: TextStyle(color: Colors.grey.shade600),
              ),
              SizedBox(height: 20),
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    children: po['items'].map<Widget>((item) => _buildMatchingItem(item)).toList(),
                  ),
                ),
              ),
              SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => _autoMatchAll(po),
                      child: Text('Auto-Match All'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => _confirmMatching(po),
                      child: Text('Confirm & Update Inventory'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMatchingItem(Map<String, dynamic> item) {
    return Card(
      margin: EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    item['name'],
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: item['matched'] ? Colors.green.shade100 : Colors.orange.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    item['matched'] ? 'MATCHED' : 'PENDING',
                    style: TextStyle(
                      fontSize: 12,
                      color: item['matched'] ? Colors.green.shade700 : Colors.orange.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Ordered: ${item['orderedQty']}', style: TextStyle(fontSize: 12)),
                      Text('Received: ${item['receivedQty']}', style: TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
                Container(
                  width: 100,
                  child: TextField(
                    decoration: InputDecoration(
                      labelText: 'Match Qty',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    ),
                    keyboardType: TextInputType.number,
                    style: TextStyle(fontSize: 12),
                  ),
                ),
                SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _matchItem(item),
                  child: Text('Match', style: TextStyle(fontSize: 12)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    minimumSize: Size(60, 30),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  void _showCreatePurchaseOrderDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Create Purchase Order'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                decoration: InputDecoration(
                  labelText: 'Vendor Name',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 12),
              TextField(
                decoration: InputDecoration(
                  labelText: 'Expected Arrival Date',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 12),
              TextField(
                decoration: InputDecoration(
                  labelText: 'Total Value (USD)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Purchase Order created successfully!'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            child: Text('Create'),
          ),
        ],
      ),
    );
  }

  void _markAsReceived(Map<String, dynamic> po) {
    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('PO ${po['poNumber']} marked as received!'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _matchItem(Map<String, dynamic> item) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Item ${item['name']} matched successfully!'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _autoMatchAll(Map<String, dynamic> po) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('All items auto-matched for PO ${po['poNumber']}!'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _confirmMatching(Map<String, dynamic> po) {
    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Inventory updated with matched items!'),
        backgroundColor: Colors.blue,
      ),
    );
  }

  List<Map<String, dynamic>> _getPendingPurchaseOrders() {
    return [
      {
        'poNumber': 'PO-2024-001',
        'vendorName': 'Shenzhen Tech Suppliers',
        'creationDate': '2024-01-10',
        'expectedDate': '2024-01-20',
        'itemCount': 25,
        'totalValue': '15,500',
        'status': 'pending',
        'items': [
          {'name': 'USB Cable Type-C', 'quantity': 500},
          {'name': 'Wireless Charger Pad', 'quantity': 100},
          {'name': 'Phone Cases (Mixed)', 'quantity': 200},
        ],
      },
      {
        'poNumber': 'PO-2024-002',
        'vendorName': 'Local Electronics Ltd.',
        'creationDate': '2024-01-12',
        'expectedDate': '2024-01-18',
        'itemCount': 18,
        'totalValue': '8,200',
        'status': 'pending',
        'items': [
          {'name': 'Power Banks 10000mAh', 'quantity': 50},
          {'name': 'Screen Protectors', 'quantity': 300},
        ],
      },
    ];
  }

  List<Map<String, dynamic>> _getReceivedPurchaseOrders() {
    return [
      {
        'poNumber': 'PO-2024-003',
        'vendorName': 'Gulf Trading Corp.',
        'receivedDate': '2024-01-15',
        'totalItems': 20,
        'matchedItems': 18,
        'matchingStatus': 'Partial',
        'items': [
          {
            'name': 'Bluetooth Earbuds',
            'orderedQty': 100,
            'receivedQty': 95,
            'matched': true
          },
          {
            'name': 'Car Chargers',
            'orderedQty': 200,
            'receivedQty': 200,
            'matched': true
          },
          {
            'name': 'Tablet Stands',
            'orderedQty': 50,
            'receivedQty': 45,
            'matched': false
          },
        ],
      },
      {
        'poNumber': 'PO-2024-004',
        'vendorName': 'China Direct Import',
        'receivedDate': '2024-01-14',
        'totalItems': 15,
        'matchedItems': 15,
        'matchingStatus': 'Complete',
        'items': [
          {
            'name': 'Lightning Cables',
            'orderedQty': 300,
            'receivedQty': 300,
            'matched': true
          },
          {
            'name': 'Wall Adapters',
            'orderedQty': 150,
            'receivedQty': 150,
            'matched': true
          },
        ],
      },
    ];
  }
}
