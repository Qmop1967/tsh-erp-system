import 'package:flutter/material.dart';

class EnhancedShipmentsScreen extends StatefulWidget {
  const EnhancedShipmentsScreen({Key? key}) : super(key: key);

  @override
  _EnhancedShipmentsScreenState createState() => _EnhancedShipmentsScreenState();
}

class _EnhancedShipmentsScreenState extends State<EnhancedShipmentsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

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
        title: Text('Enhanced Shipments'),
        backgroundColor: Colors.blue.shade700,
        elevation: 4,
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(
              icon: Icon(Icons.local_shipping),
              text: 'Dispatched',
            ),
            Tab(
              icon: Icon(Icons.inventory),
              text: 'Received',
            ),
          ],
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildDispatchedTab(),
          _buildReceivedTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showCreateShipmentDialog(),
        label: Text('Create Shipment'),
        icon: Icon(Icons.add),
        backgroundColor: Colors.green.shade600,
      ),
    );
  }

  Widget _buildDispatchedTab() {
    return Container(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeaderCard(
            'Dispatched Shipments',
            'Track all outgoing shipments and delivery status',
            Icons.local_shipping,
            Colors.blue,
          ),
          SizedBox(height: 20),
          Expanded(
            child: ListView.builder(
              itemCount: _getDispatchedShipments().length,
              itemBuilder: (context, index) {
                final shipment = _getDispatchedShipments()[index];
                return _buildDispatchedShipmentCard(shipment);
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
            'Received Shipments',
            'Historical and expected incoming shipments',
            Icons.inventory,
            Colors.green,
          ),
          SizedBox(height: 20),
          Expanded(
            child: ListView.builder(
              itemCount: _getReceivedShipments().length,
              itemBuilder: (context, index) {
                final shipment = _getReceivedShipments()[index];
                return _buildReceivedShipmentCard(shipment);
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

  Widget _buildDispatchedShipmentCard(Map<String, dynamic> shipment) {
    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: InkWell(
        onTap: () => _showShipmentDetails(shipment),
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
                      color: _getStatusColor(shipment['status']),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      shipment['status'],
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Spacer(),
                  Text(
                    'ID: ${shipment['id']}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 12),
              Text(
                'Customer: ${shipment['customerName']}',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              SizedBox(height: 4),
              Text(
                'Driver: ${shipment['driverName']}',
                style: TextStyle(color: Colors.grey.shade600),
              ),
              SizedBox(height: 4),
              Text(
                'Vehicle: ${shipment['vehicleInfo']}',
                style: TextStyle(color: Colors.grey.shade600),
              ),
              SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.inventory_2, size: 16, color: Colors.grey.shade600),
                  SizedBox(width: 4),
                  Text('${shipment['cartonCount']} cartons'),
                  Spacer(),
                  Text(
                    'Dispatched: ${shipment['dispatchDate']}',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildReceivedShipmentCard(Map<String, dynamic> shipment) {
    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: InkWell(
        onTap: () => _showShipmentDetails(shipment),
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
                    'ID: ${shipment['id']}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 12),
              Text(
                'Supplier: ${shipment['supplierName']}',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              SizedBox(height: 4),
              Text(
                'Reference: ${shipment['referenceNumber']}',
                style: TextStyle(color: Colors.grey.shade600),
              ),
              SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.inventory_2, size: 16, color: Colors.grey.shade600),
                  SizedBox(width: 4),
                  Text('${shipment['itemCount']} items'),
                  Spacer(),
                  Text(
                    'Received: ${shipment['receivedDate']}',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'delivered':
        return Colors.green.shade600;
      case 'in transit':
        return Colors.orange.shade600;
      case 'dispatched':
        return Colors.blue.shade600;
      default:
        return Colors.grey.shade600;
    }
  }

  void _showShipmentDetails(Map<String, dynamic> shipment) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Shipment Details'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('Shipment ID:', shipment['id']),
              _buildDetailRow('Status:', shipment['status']),
              if (shipment['customerName'] != null)
                _buildDetailRow('Customer:', shipment['customerName']),
              if (shipment['supplierName'] != null)
                _buildDetailRow('Supplier:', shipment['supplierName']),
              if (shipment['driverName'] != null)
                _buildDetailRow('Driver:', shipment['driverName']),
              if (shipment['vehicleInfo'] != null)
                _buildDetailRow('Vehicle:', shipment['vehicleInfo']),
              _buildDetailRow('Items/Cartons:', 
                shipment['cartonCount']?.toString() ?? shipment['itemCount']?.toString() ?? 'N/A'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
          if (shipment['status'] != 'Delivered')
            ElevatedButton(
              onPressed: () => _updateShipmentStatus(shipment),
              child: Text('Update Status'),
            ),
        ],
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
            width: 100,
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

  void _showCreateShipmentDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Create New Shipment'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                decoration: InputDecoration(
                  labelText: 'Customer/Supplier Name',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 12),
              TextField(
                decoration: InputDecoration(
                  labelText: 'Driver Name',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 12),
              TextField(
                decoration: InputDecoration(
                  labelText: 'Vehicle Information',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 12),
              TextField(
                decoration: InputDecoration(
                  labelText: 'Number of Cartons/Packages',
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
                  content: Text('Shipment created successfully!'),
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

  void _updateShipmentStatus(Map<String, dynamic> shipment) {
    Navigator.pop(context); // Close details dialog first
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Update Shipment Status'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: Text('In Transit'),
              leading: Radio(value: 'In Transit', groupValue: null, onChanged: null),
            ),
            ListTile(
              title: Text('Delivered'),
              leading: Radio(value: 'Delivered', groupValue: null, onChanged: null),
            ),
          ],
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
                  content: Text('Shipment status updated!'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            child: Text('Update'),
          ),
        ],
      ),
    );
  }

  List<Map<String, dynamic>> _getDispatchedShipments() {
    return [
      {
        'id': 'SH-2024-001',
        'customerName': 'Al-Noor Electronics',
        'driverName': 'Ahmed Hassan',
        'vehicleInfo': 'Toyota Hiace - 123ABC',
        'cartonCount': 15,
        'dispatchDate': '2024-01-15',
        'status': 'Delivered'
      },
      {
        'id': 'SH-2024-002',
        'customerName': 'Baghdad Mobile Center',
        'driverName': 'Omar Ali',
        'vehicleInfo': 'Nissan Van - 456DEF',
        'cartonCount': 8,
        'dispatchDate': '2024-01-16',
        'status': 'In Transit'
      },
      {
        'id': 'SH-2024-003',
        'customerName': 'Tech Hub Store',
        'driverName': 'Mohammed Said',
        'vehicleInfo': 'Ford Transit - 789GHI',
        'cartonCount': 22,
        'dispatchDate': '2024-01-16',
        'status': 'Dispatched'
      },
    ];
  }

  List<Map<String, dynamic>> _getReceivedShipments() {
    return [
      {
        'id': 'RCV-2024-001',
        'supplierName': 'Shenzhen Electronics Co.',
        'referenceNumber': 'PO-2024-158',
        'itemCount': 1200,
        'receivedDate': '2024-01-14',
      },
      {
        'id': 'RCV-2024-002',
        'supplierName': 'Local Accessories Ltd.',
        'referenceNumber': 'PO-2024-159',
        'itemCount': 450,
        'receivedDate': '2024-01-15',
      },
      {
        'id': 'RCV-2024-003',
        'supplierName': 'Gulf Trading Company',
        'referenceNumber': 'PO-2024-160',
        'itemCount': 800,
        'receivedDate': '2024-01-16',
      },
    ];
  }
}
