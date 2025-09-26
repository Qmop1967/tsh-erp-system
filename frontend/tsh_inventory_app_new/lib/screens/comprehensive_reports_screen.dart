import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/export_service.dart';
import '../services/mock_data_service.dart';

class ComprehensiveReportsScreen extends StatefulWidget {
  const ComprehensiveReportsScreen({super.key});

  @override
  State<ComprehensiveReportsScreen> createState() => _ComprehensiveReportsScreenState();
}

class _ComprehensiveReportsScreenState extends State<ComprehensiveReportsScreen> {
  String _selectedReportType = 'stock_levels';
  String _selectedTimeRange = 'month';
  bool _isGeneratingReport = false;

  // Sample data - in real implementation, this would come from API
  late Map<String, dynamic> _reportsData;

  @override
  void initState() {
    super.initState();
    _reportsData = MockDataService.getInventoryData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('📊 Comprehensive Reports'),
            Text(
              'Analytics & Export Tools',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshReports,
          ),
        ],
      ),
      body: Column(
        children: [
          _buildKPIOverview(),
          _buildReportControls(),
          Expanded(
            child: _buildReportContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildKPIOverview() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '📈 Key Performance Indicators',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildKPICard(
                'Total Inventory Value',
                '\$${_reportsData['totalInventoryValue'].toStringAsFixed(0)}',
                Icons.attach_money,
                Colors.green,
              ),
              const SizedBox(width: 12),
              _buildKPICard(
                'Stock Turnover Ratio',
                '${_reportsData['stockTurnoverRatio']}x',
                Icons.sync,
                Colors.blue,
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildKPICard(
                'Low Stock Items',
                '${_reportsData['lowStockItemsCount']}',
                Icons.warning,
                Colors.orange,
              ),
              const SizedBox(width: 12),
              _buildKPICard(
                'Warehouse Utilization',
                '${_reportsData['warehouseUtilization']}%',
                Icons.warehouse,
                Colors.purple,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildKPICard(String title, String value, IconData icon, MaterialColor color) {
    return Expanded(
      child: Card(
        elevation: 4,
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            gradient: LinearGradient(
              colors: [color.shade100, color.shade50],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, color: color.shade700, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      title,
                      style: TextStyle(
                        fontSize: 12,
                        color: color.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                value,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: color.shade800,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildReportControls() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '🔧 Report Configuration',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Report Type:', style: TextStyle(fontWeight: FontWeight.w500)),
                    const SizedBox(height: 4),
                    DropdownButtonFormField<String>(
                      value: _selectedReportType,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'stock_levels', child: Text('📦 Current Stock Levels')),
                        DropdownMenuItem(value: 'movement_history', child: Text('📋 Stock Movement History')),
                        DropdownMenuItem(value: 'low_stock_alerts', child: Text('⚠️ Low Stock Alerts')),
                        DropdownMenuItem(value: 'packaging_summary', child: Text('� Packaging Summary')),
                        DropdownMenuItem(value: 'shipment_tracking', child: Text('🚚 Shipment Tracking')),
                        DropdownMenuItem(value: 'warehouse_utilization', child: Text('🏭 Warehouse Utilization')),
                      ],
                      onChanged: (value) => setState(() => _selectedReportType = value!),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Time Range:', style: TextStyle(fontWeight: FontWeight.w500)),
                    const SizedBox(height: 4),
                    DropdownButtonFormField<String>(
                      value: _selectedTimeRange,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'week', child: Text('📅 This Week')),
                        DropdownMenuItem(value: 'month', child: Text('📅 This Month')),
                        DropdownMenuItem(value: 'quarter', child: Text('📅 This Quarter')),
                        DropdownMenuItem(value: 'year', child: Text('📅 This Year')),
                        DropdownMenuItem(value: 'custom', child: Text('📅 Custom Range')),
                      ],
                      onChanged: (value) => setState(() => _selectedTimeRange = value!),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _isGeneratingReport ? null : _generateReport,
                  icon: _isGeneratingReport 
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.play_arrow),
                  label: Text(_isGeneratingReport ? 'Generating...' : 'Generate Report'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              _buildExportButton('📄 PDF', Icons.picture_as_pdf, Colors.red),
              const SizedBox(width: 8),
              _buildExportButton('📊 Excel', Icons.table_chart, Colors.green),
              const SizedBox(width: 8),
              _buildExportButton('📋 CSV', Icons.description, Colors.blue),
            ],
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildExportButton(String label, IconData icon, MaterialColor color) {
    final format = label.split(' ')[1].toLowerCase();
    return ElevatedButton.icon(
      onPressed: _isGeneratingReport ? null : () => _exportReport(format),
      icon: _isGeneratingReport 
        ? SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(color.shade700),
            ),
          )
        : Icon(icon, size: 16),
      label: Text(_isGeneratingReport ? 'Exporting...' : label.split(' ')[1]),
      style: ElevatedButton.styleFrom(
        backgroundColor: _isGeneratingReport ? Colors.grey.shade200 : color.shade100,
        foregroundColor: _isGeneratingReport ? Colors.grey.shade600 : color.shade700,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        minimumSize: const Size(0, 40),
      ),
    );
  }

  Widget _buildReportContent() {
    switch (_selectedReportType) {
      case 'stock_levels':
        return _buildStockLevelsReport();
      case 'movement_history':
        return _buildMovementHistoryReport();
      case 'low_stock_alerts':
        return _buildLowStockAlertsReport();
      case 'packaging_summary':
        return _buildPackagingSummaryReport();
      case 'shipment_tracking':
        return _buildShipmentTrackingReport();
      case 'warehouse_utilization':
        return _buildWarehouseUtilizationReport();
      default:
        return _buildStockLevelsReport();
    }
  }

  Widget _buildLowStockAlertsReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '⚠️ Low Stock Alerts Report',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _buildAlertSummaryCards(),
          const SizedBox(height: 16),
          _buildLowStockTable(),
        ],
      ),
    );
  }

  Widget _buildAlertSummaryCards() {
    return Row(
      children: [
        _buildKPICard(
          'Critical (Out of Stock)',
          '${_reportsData['zeroStockItemsCount']}',
          Icons.error,
          Colors.red,
        ),
        const SizedBox(width: 12),
        _buildKPICard(
          'Low Stock Warning',
          '${_reportsData['lowStockItemsCount']}',
          Icons.warning,
          Colors.orange,
        ),
      ],
    );
  }

  Widget _buildLowStockTable() {
    final alertData = MockDataService.getLowStockAlerts();

    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(Colors.orange.shade50),
          columns: const [
            DataColumn(label: Text('Item Name', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Current Stock', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Min Stock', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Status', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Value', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Action', style: TextStyle(fontWeight: FontWeight.bold))),
          ],
          rows: alertData.map((item) {
            Color statusColor = Colors.green;
            if (item['status'] == 'Low Stock') statusColor = Colors.orange;
            if (item['status'] == 'Out of Stock') statusColor = Colors.red;

            return DataRow(
              cells: [
                DataCell(Text(item['itemName'].toString())),
                DataCell(Text(item['currentStock'].toString())),
                DataCell(Text(item['minStock'].toString())),
                DataCell(
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withAlpha(200),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      item['status'].toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                DataCell(Text('\$${item['value'].toStringAsFixed(0)}')),
                DataCell(
                  ElevatedButton.icon(
                    onPressed: () => _createPurchaseOrder(item['itemName'].toString()),
                    icon: const Icon(Icons.add_shopping_cart, size: 16),
                    label: const Text('Reorder'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.teal.shade100,
                      foregroundColor: Colors.teal.shade700,
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    ),
                  ),
                ),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildPackagingSummaryReport() {
    final packageData = _reportsData['packageVariants'];
    final total = packageData['boxes'] + packageData['bundles'] + packageData['bags'];
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '� Packaging Summary Report',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text(
                    'Packaging Variants Distribution',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    height: 200,
                    child: PieChart(
                      PieChartData(
                        sectionsSpace: 2,
                        centerSpaceRadius: 40,
                        sections: [
                          PieChartSectionData(
                            color: Colors.blue.shade400,
                            value: packageData['boxes'].toDouble(),
                            title: 'Boxes\n${packageData['boxes']}',
                            radius: 80,
                            titleStyle: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          PieChartSectionData(
                            color: Colors.green.shade400,
                            value: packageData['bundles'].toDouble(),
                            title: 'Bundles\n${packageData['bundles']}',
                            radius: 80,
                            titleStyle: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          PieChartSectionData(
                            color: Colors.orange.shade400,
                            value: packageData['bags'].toDouble(),
                            title: 'Bags\n${packageData['bags']}',
                            radius: 80,
                            titleStyle: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildPackageCard('📦 Boxes', packageData['boxes'], total, Colors.blue, 
                'Standard packaging for electronics'),
              const SizedBox(width: 12),
              _buildPackageCard('🎁 Bundles', packageData['bundles'], total, Colors.green,
                'Multi-item promotional packages'),
            ],
          ),
          const SizedBox(height: 12),
          _buildPackageCard('👝 Bags', packageData['bags'], total, Colors.orange,
            'Flexible packaging for accessories'),
        ],
      ),
    );
  }

  Widget _buildPackageCard(String title, int count, int total, MaterialColor color, String description) {
    final percentage = (count / total * 100).toStringAsFixed(1);
    
    return Expanded(
      child: Card(
        elevation: 4,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            gradient: LinearGradient(
              colors: [color.shade100, color.shade50],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color.shade800,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '$count packages ($percentage%)',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: color.shade700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: TextStyle(
                  fontSize: 12,
                  color: color.shade600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildShipmentTrackingReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '🚚 Shipment Tracking Report',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _buildShipmentSummaryCards(),
          const SizedBox(height: 16),
          _buildShipmentTable(),
        ],
      ),
    );
  }

  Widget _buildShipmentSummaryCards() {
    return Row(
      children: [
        _buildKPICard(
          'Pending Shipments',
          '${_reportsData['pendingShipments']}',
          Icons.local_shipping,
          Colors.orange,
        ),
        const SizedBox(width: 12),
        _buildKPICard(
          'Completed Packages',
          '${_reportsData['completedPackaging']}',
          Icons.check_circle,
          Colors.green,
        ),
      ],
    );
  }

  Widget _buildShipmentTable() {
    final shipmentData = [
      {'id': 'SH-001', 'customer': 'Ahmed Electronics', 'packages': 3, 'status': 'In Transit', 'driver': 'Mohammed Ali'},
      {'id': 'SH-002', 'customer': 'Tech Store Baghdad', 'packages': 1, 'status': 'Delivered', 'driver': 'Hassan Omar'},
      {'id': 'SH-003', 'customer': 'Mobile World', 'packages': 2, 'status': 'Preparing', 'driver': 'Ali Ahmed'},
      {'id': 'SH-004', 'customer': 'Gadget Zone', 'packages': 4, 'status': 'In Transit', 'driver': 'Omar Hassan'},
      {'id': 'SH-005', 'customer': 'Phone Paradise', 'packages': 1, 'status': 'Preparing', 'driver': 'Ahmed Ali'},
    ];

    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(Colors.blue.shade50),
          columns: const [
            DataColumn(label: Text('Shipment ID', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Customer', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Packages', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Status', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Driver', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Action', style: TextStyle(fontWeight: FontWeight.bold))),
          ],
          rows: shipmentData.map((shipment) {
            Color statusColor = Colors.blue;
            if (shipment['status'] == 'Delivered') statusColor = Colors.green;
            if (shipment['status'] == 'In Transit') statusColor = Colors.orange;
            if (shipment['status'] == 'Preparing') statusColor = Colors.purple;

            return DataRow(
              cells: [
                DataCell(Text(shipment['id'].toString())),
                DataCell(Text(shipment['customer'].toString())),
                DataCell(Text(shipment['packages'].toString())),
                DataCell(
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withAlpha(200),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      shipment['status'].toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                DataCell(Text(shipment['driver'].toString())),
                DataCell(
                  ElevatedButton.icon(
                    onPressed: () => _trackShipment(shipment['id'].toString()),
                    icon: const Icon(Icons.track_changes, size: 16),
                    label: const Text('Track'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue.shade100,
                      foregroundColor: Colors.blue.shade700,
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    ),
                  ),
                ),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildWarehouseUtilizationReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '🏭 Warehouse Utilization Report',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _buildUtilizationCards(),
          const SizedBox(height: 16),
          _buildCapacityChart(),
        ],
      ),
    );
  }

  Widget _buildUtilizationCards() {
    return Column(
      children: [
        Row(
          children: [
            _buildKPICard(
              'Main Warehouse',
              '7,850 / 10,000',
              Icons.warehouse,
              Colors.blue,
            ),
            const SizedBox(width: 12),
            _buildKPICard(
              'Retail Shop',
              '1,560 / 2,000',
              Icons.store,
              Colors.green,
            ),
          ],
        ),
        const SizedBox(height: 12),
        _buildKPICard(
          'Overall Utilization',
          '${_reportsData['warehouseUtilization']}%',
          Icons.analytics,
          Colors.purple,
        ),
      ],
    );
  }

  Widget _buildCapacityChart() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Capacity Utilization by Location',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Container(
              height: 200,
              padding: const EdgeInsets.all(20),
              child: const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.bar_chart, size: 64, color: Colors.grey),
                    SizedBox(height: 16),
                    Text(
                      'Interactive capacity chart coming soon',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _createPurchaseOrder(String sku) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('🛒 Creating purchase order for $sku...')),
    );
  }

  void _trackShipment(String shipmentId) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('📍 Tracking shipment $shipmentId...')),
    );
  }

  Widget _buildStockLevelsReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '📦 Current Stock Levels Report',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _buildStockTable(),
        ],
      ),
    );
  }

  Widget _buildStockTable() {
    final stockData = [
      {'item': 'USB Cable Type-C', 'sku': 'USB-C-001', 'stock': 250, 'reorder': 100, 'status': 'Good'},
      {'item': 'Phone Case iPhone 15', 'sku': 'CASE-IP15', 'stock': 45, 'reorder': 50, 'status': 'Low'},
      {'item': 'Wireless Charger', 'sku': 'WC-001', 'stock': 0, 'reorder': 25, 'status': 'Out'},
      {'item': 'Bluetooth Headphones', 'sku': 'BT-HP-001', 'stock': 120, 'reorder': 30, 'status': 'Good'},
      {'item': 'Power Bank 10000mAh', 'sku': 'PB-10K', 'stock': 15, 'reorder': 20, 'status': 'Low'},
    ];

    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(Colors.teal.shade50),
          columns: const [
            DataColumn(label: Text('Item Name', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('SKU', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Current Stock', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Reorder Point', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Status', style: TextStyle(fontWeight: FontWeight.bold))),
          ],
          rows: stockData.map((item) {
            Color statusColor = Colors.green;
            if (item['status'] == 'Low') statusColor = Colors.orange;
            if (item['status'] == 'Out') statusColor = Colors.red;

            return DataRow(
              cells: [
                DataCell(Text(item['item'].toString())),
                DataCell(Text(item['sku'].toString())),
                DataCell(Text(item['stock'].toString())),
                DataCell(Text(item['reorder'].toString())),
                DataCell(
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withAlpha(200),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      item['status'].toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildMovementHistoryReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '📋 Stock Movement History',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _buildMovementTable(),
        ],
      ),
    );
  }

  Widget _buildMovementTable() {
    final movementData = [
      {'date': '2025-01-10', 'item': 'USB Cable Type-C', 'type': 'Receipt', 'qty': '+100', 'ref': 'PO-001'},
      {'date': '2025-01-10', 'item': 'Phone Case iPhone 15', 'type': 'Sale', 'qty': '-5', 'ref': 'SO-023'},
      {'date': '2025-01-09', 'item': 'Wireless Charger', 'type': 'Sale', 'qty': '-25', 'ref': 'SO-022'},
      {'date': '2025-01-09', 'item': 'Power Bank 10000mAh', 'type': 'Transfer', 'qty': '-10', 'ref': 'TR-005'},
      {'date': '2025-01-08', 'item': 'Bluetooth Headphones', 'type': 'Receipt', 'qty': '+50', 'ref': 'PO-002'},
    ];

    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(Colors.teal.shade50),
          columns: const [
            DataColumn(label: Text('Date', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Item', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Movement Type', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Quantity', style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Reference', style: TextStyle(fontWeight: FontWeight.bold))),
          ],
          rows: movementData.map((movement) {
            Color typeColor = Colors.blue;
            if (movement['type'] == 'Receipt') typeColor = Colors.green;
            if (movement['type'] == 'Sale') typeColor = Colors.orange;
            if (movement['type'] == 'Transfer') typeColor = Colors.purple;

            return DataRow(
              cells: [
                DataCell(Text(movement['date'].toString())),
                DataCell(Text(movement['item'].toString())),
                DataCell(
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: typeColor.withAlpha(200),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      movement['type'].toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                DataCell(Text(movement['qty'].toString())),
                DataCell(Text(movement['ref'].toString())),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  void _refreshReports() {
    setState(() {
      // Refresh data with new mock data
      _reportsData = MockDataService.getInventoryData();
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('📊 Reports refreshed with latest data!')),
    );
  }

  void _generateReport() async {
    setState(() => _isGeneratingReport = true);
    
    // Simulate report generation
    await Future.delayed(const Duration(seconds: 2));
    
    setState(() => _isGeneratingReport = false);
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('✅ ${_getReportTypeName()} report generated successfully!')),
    );
  }

  void _exportReport(String format) async {
    final reportName = _getReportTypeName();
    
    setState(() {
      _isGeneratingReport = true;
    });
    
    try {
      switch (format.toLowerCase()) {
        case 'pdf':
          await ExportService.exportToPDF(
            reportTitle: reportName,
            reportType: _selectedReportType,
            data: _reportsData,
            context: context,
          );
          break;
        case 'excel':
          await ExportService.exportToExcel(
            reportTitle: reportName,
            reportType: _selectedReportType,
            data: _reportsData,
            context: context,
          );
          break;
        case 'csv':
          await ExportService.exportToCSV(
            reportTitle: reportName,
            reportType: _selectedReportType,
            data: _reportsData,
            context: context,
          );
          break;
        default:
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('❌ Unsupported export format: $format')),
            );
          }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ Export failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isGeneratingReport = false;
        });
      }
    }
  }

  String _getReportTypeName() {
    switch (_selectedReportType) {
      case 'stock_levels': return 'Stock Levels';
      case 'movement_history': return 'Movement History';
      case 'low_stock_alerts': return 'Low Stock Alerts';
      case 'packaging_summary': return 'Packaging Summary';
      case 'shipment_tracking': return 'Shipment Tracking';
      case 'warehouse_utilization': return 'Warehouse Utilization';
      default: return 'Report';
    }
  }
}
