import 'package:flutter/material.dart';
import 'package:tsh_core_package/tsh_core_package.dart';
import '../models/inventory_models.dart';
import '../services/inventory_service.dart';

class WarehouseOperationsScreen extends StatefulWidget {
  const WarehouseOperationsScreen({super.key});

  @override
  State<WarehouseOperationsScreen> createState() => _WarehouseOperationsScreenState();
}

class _WarehouseOperationsScreenState extends State<WarehouseOperationsScreen> {
  final InventoryService _inventoryService = InventoryService();
  List<Warehouse> _warehouses = [];
  List<StockMovement> _recentMovements = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final warehousesFuture = _inventoryService.getWarehouses();
      final movementsFuture = _inventoryService.getStockMovements(limit: 10);

      final results = await Future.wait([warehousesFuture, movementsFuture]);
      
      setState(() {
        _warehouses = results[0] as List<Warehouse>;
        _recentMovements = results[1] as List<StockMovement>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading warehouse data: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Warehouse Operations'),
        subtitle: Text('${_warehouses.length} locations'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: _showWarehouseAnalytics,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildWarehouseContent(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showNewMovementDialog,
        backgroundColor: TSHTheme.primaryTeal,
        icon: const Icon(Icons.move_up),
        label: const Text('New Movement'),
      ),
    );
  }

  Widget _buildWarehouseContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Warehouse Overview
          _buildWarehouseOverview(),
          
          const SizedBox(height: 24),
          
          // Quick Actions
          _buildQuickActions(),
          
          const SizedBox(height: 24),
          
          // Recent Movements
          _buildRecentMovements(),
          
          const SizedBox(height: 24),
          
          // Pending Approvals
          _buildPendingApprovals(),
        ],
      ),
    );
  }

  Widget _buildWarehouseOverview() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Warehouse Overview',
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.2,
          ),
          itemCount: _warehouses.length,
          itemBuilder: (context, index) {
            final warehouse = _warehouses[index];
            return _buildWarehouseCard(warehouse);
          },
        ),
      ],
    );
  }

  Widget _buildWarehouseCard(Warehouse warehouse) {
    final utilizationPercentage = warehouse.utilizationPercentage;
    final utilizationColor = _getUtilizationColor(utilizationPercentage);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                _getWarehouseIcon(warehouse.type),
                color: TSHTheme.primaryTeal,
                size: 24,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  warehouse.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Utilization Progress
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Utilization',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  Text(
                    '${utilizationPercentage.toStringAsFixed(1)}%',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: utilizationColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              LinearProgressIndicator(
                value: utilizationPercentage / 100,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation<Color>(utilizationColor),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Capacity Info
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Used: ${warehouse.currentUsage}',
                      style: const TextStyle(fontSize: 11),
                    ),
                    Text(
                      'Total: ${warehouse.capacity}',
                      style: const TextStyle(fontSize: 11),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.more_vert, size: 18),
                onPressed: () => _showWarehouseMenu(warehouse),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildActionButton(
                'Transfer Items',
                Icons.swap_horiz,
                TSHTheme.primaryBlue,
                () => _showTransferDialog(),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildActionButton(
                'Receive Stock',
                Icons.move_down,
                TSHTheme.successGreen,
                () => _showReceiveDialog(),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildActionButton(
                'Issue Stock',
                Icons.move_up,
                TSHTheme.warningYellow,
                () => _showIssueDialog(),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildActionButton(
                'Adjust Stock',
                Icons.tune,
                TSHTheme.accentOrange,
                () => _showAdjustmentDialog(),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionButton(String title, IconData icon, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: color,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentMovements() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Recent Movements',
              style: TSHTheme.headingSmall,
            ),
            TextButton(
              onPressed: () => _showAllMovements(),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(
            color: TSHTheme.surfaceWhite,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey.shade200),
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _recentMovements.take(5).length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final movement = _recentMovements[index];
              return _buildMovementListItem(movement);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildMovementListItem(StockMovement movement) {
    final statusColor = _getMovementStatusColor(movement.status);
    final typeIcon = _getMovementTypeIcon(movement.type);

    return ListTile(
      leading: CircleAvatar(
        backgroundColor: statusColor.withOpacity(0.1),
        child: Icon(typeIcon, color: statusColor, size: 20),
      ),
      title: Text(
        'Item ID: ${movement.itemId}',
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: Text(
        '${movement.type.name.toUpperCase()} • Qty: ${movement.quantity} • ${_formatMovementStatus(movement.status)}',
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            '\$${movement.totalValue.toStringAsFixed(2)}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(
            _formatDateTime(movement.createdAt),
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
      onTap: () => _showMovementDetails(movement),
    );
  }

  Widget _buildPendingApprovals() {
    final pendingMovements = _recentMovements
        .where((movement) => movement.status == MovementStatus.pending)
        .toList();

    if (pendingMovements.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.pending_actions, color: TSHTheme.warningYellow),
            const SizedBox(width: 8),
            Text(
              'Pending Approvals (${pendingMovements.length})',
              style: TSHTheme.headingSmall,
            ),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(
            color: TSHTheme.warningYellow.withOpacity(0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: TSHTheme.warningYellow.withOpacity(0.3)),
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: pendingMovements.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final movement = pendingMovements[index];
              return _buildPendingMovementItem(movement);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildPendingMovementItem(StockMovement movement) {
    return ListTile(
      leading: const CircleAvatar(
        backgroundColor: TSHTheme.warningYellow,
        child: Icon(Icons.pending, color: Colors.white, size: 20),
      ),
      title: Text('${movement.type.name.toUpperCase()} - Item ${movement.itemId}'),
      subtitle: Text('Qty: ${movement.quantity} • Created by: ${movement.createdBy}'),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.check, color: TSHTheme.successGreen),
            onPressed: () => _approveMovement(movement),
          ),
          IconButton(
            icon: const Icon(Icons.close, color: TSHTheme.errorRed),
            onPressed: () => _rejectMovement(movement),
          ),
        ],
      ),
    );
  }

  // Helper methods
  Color _getUtilizationColor(double percentage) {
    if (percentage >= 90) return TSHTheme.errorRed;
    if (percentage >= 75) return TSHTheme.warningYellow;
    return TSHTheme.successGreen;
  }

  IconData _getWarehouseIcon(WarehouseType type) {
    switch (type) {
      case WarehouseType.main:
        return Icons.warehouse;
      case WarehouseType.retail:
        return Icons.store;
      case WarehouseType.secondary:
        return Icons.business;
      case WarehouseType.temporary:
        return Icons.storage;
    }
  }

  Color _getMovementStatusColor(MovementStatus status) {
    switch (status) {
      case MovementStatus.pending:
        return TSHTheme.warningYellow;
      case MovementStatus.approved:
        return TSHTheme.primaryBlue;
      case MovementStatus.completed:
        return TSHTheme.successGreen;
      case MovementStatus.cancelled:
        return TSHTheme.errorRed;
    }
  }

  IconData _getMovementTypeIcon(MovementType type) {
    switch (type) {
      case MovementType.receipt:
        return Icons.input;
      case MovementType.issue:
        return Icons.output;
      case MovementType.transfer:
        return Icons.swap_horiz;
      case MovementType.adjustment:
        return Icons.tune;
    }
  }

  String _formatMovementStatus(MovementStatus status) {
    return status.name.toUpperCase();
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  // Action methods
  void _showWarehouseMenu(Warehouse warehouse) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.inventory),
              title: Text('View Stock Levels'),
              onTap: () {
                Navigator.pop(context);
                _viewWarehouseStock(warehouse);
              },
            ),
            ListTile(
              leading: const Icon(Icons.analytics),
              title: Text('Warehouse Analytics'),
              onTap: () {
                Navigator.pop(context);
                _showWarehouseAnalytics();
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: Text('Warehouse Settings'),
              onTap: () {
                Navigator.pop(context);
                _editWarehouse(warehouse);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showNewMovementDialog() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => CreateMovementScreen(
          warehouses: _warehouses,
          onMovementCreated: () => _loadData(),
        ),
      ),
    );
  }

  void _showTransferDialog() {
    _showNewMovementDialog(); // Same as new movement for now
  }

  void _showReceiveDialog() {
    _showNewMovementDialog();
  }

  void _showIssueDialog() {
    _showNewMovementDialog();
  }

  void _showAdjustmentDialog() {
    _showNewMovementDialog();
  }

  void _showAllMovements() {
    // Navigate to full movements screen
  }

  void _showMovementDetails(StockMovement movement) {
    showDialog(
      context: context,
      builder: (context) => MovementDetailsDialog(movement: movement),
    );
  }

  void _viewWarehouseStock(Warehouse warehouse) {
    // Implementation for viewing warehouse stock
  }

  void _showWarehouseAnalytics() {
    // Implementation for warehouse analytics
  }

  void _editWarehouse(Warehouse warehouse) {
    // Implementation for editing warehouse
  }

  void _approveMovement(StockMovement movement) async {
    try {
      await _inventoryService.approveStockMovement(movement.id, 'current_user');
      _loadData();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Movement approved successfully')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error approving movement: $e')),
      );
    }
  }

  void _rejectMovement(StockMovement movement) {
    // Implementation for rejecting movement
  }
}

// Placeholder screens
class CreateMovementScreen extends StatelessWidget {
  final List<Warehouse> warehouses;
  final VoidCallback onMovementCreated;

  const CreateMovementScreen({
    super.key,
    required this.warehouses,
    required this.onMovementCreated,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Movement')),
      body: const Center(child: Text('Create Movement Form - To be implemented')),
    );
  }
}

class MovementDetailsDialog extends StatelessWidget {
  final StockMovement movement;

  const MovementDetailsDialog({super.key, required this.movement});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('${movement.type.name.toUpperCase()} Movement'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Item ID: ${movement.itemId}'),
          Text('Quantity: ${movement.quantity}'),
          Text('Status: ${movement.status.name}'),
          Text('Created by: ${movement.createdBy}'),
          if (movement.referenceNumber != null)
            Text('Reference: ${movement.referenceNumber}'),
        ],
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
