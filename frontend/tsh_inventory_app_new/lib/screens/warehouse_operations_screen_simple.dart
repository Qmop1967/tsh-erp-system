import 'package:flutter/material.dart';
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
      final warehouses = await _inventoryService.getWarehouses();
      final movements = await _inventoryService.getStockMovements();
      if (mounted) {
        setState(() {
          _warehouses = warehouses;
          _recentMovements = movements.take(10).toList();
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Warehouse Operations'),
            Text(
              'Multi-Location Stock Management',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              // TODO: Implement new movement
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildWarehousesSection(),
                  const SizedBox(height: 20),
                  _buildRecentMovementsSection(),
                ],
              ),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: Implement new stock movement
        },
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildWarehousesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Warehouses',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        if (_warehouses.isEmpty)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('No warehouses configured'),
            ),
          )
        else
          ...(_warehouses.map((warehouse) => _buildWarehouseCard(warehouse)).toList()),
      ],
    );
  }

  Widget _buildWarehouseCard(Warehouse warehouse) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  warehouse.type == WarehouseType.main 
                      ? Icons.warehouse 
                      : Icons.store,
                  color: Colors.teal,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    warehouse.name,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),
                Text(
                  '${warehouse.utilizationPercentage.toStringAsFixed(1)}%',
                  style: TextStyle(
                    color: warehouse.utilizationPercentage > 80 
                        ? Colors.red 
                        : Colors.green,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(warehouse.address),
            const SizedBox(height: 8),
            Row(
              children: [
                Text('Capacity: ${warehouse.capacity}'),
                const SizedBox(width: 16),
                Text('Used: ${warehouse.currentUsage}'),
                const SizedBox(width: 16),
                Text('Available: ${warehouse.capacity - warehouse.currentUsage}'),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: warehouse.utilizationPercentage / 100,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(
                warehouse.utilizationPercentage > 80 ? Colors.red : Colors.green,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentMovementsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Movements',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        if (_recentMovements.isEmpty)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('No recent movements'),
            ),
          )
        else
          ...(_recentMovements.map((movement) => _buildMovementCard(movement)).toList()),
      ],
    );
  }

  Widget _buildMovementCard(StockMovement movement) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getMovementColor(movement.type),
          child: Icon(
            _getMovementIcon(movement.type),
            color: Colors.white,
          ),
        ),
        title: Text(_getMovementTypeText(movement.type)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Quantity: ${movement.quantity}'),
            Text('Value: \$${movement.totalValue.toStringAsFixed(2)}'),
            Text('Date: ${movement.createdAt.toString().split(' ')[0]}'),
          ],
        ),
        trailing: Chip(
          label: Text(movement.status.name.toUpperCase()),
          backgroundColor: _getStatusColor(movement.status),
        ),
      ),
    );
  }

  Color _getMovementColor(MovementType type) {
    switch (type) {
      case MovementType.receipt:
        return Colors.green;
      case MovementType.issue:
        return Colors.red;
      case MovementType.transfer:
        return Colors.blue;
      case MovementType.adjustment:
        return Colors.orange;
    }
  }

  IconData _getMovementIcon(MovementType type) {
    switch (type) {
      case MovementType.receipt:
        return Icons.arrow_downward;
      case MovementType.issue:
        return Icons.arrow_upward;
      case MovementType.transfer:
        return Icons.swap_horiz;
      case MovementType.adjustment:
        return Icons.tune;
    }
  }

  String _getMovementTypeText(MovementType type) {
    switch (type) {
      case MovementType.receipt:
        return 'Stock Receipt';
      case MovementType.issue:
        return 'Stock Issue';
      case MovementType.transfer:
        return 'Stock Transfer';
      case MovementType.adjustment:
        return 'Stock Adjustment';
    }
  }

  Color _getStatusColor(MovementStatus status) {
    switch (status) {
      case MovementStatus.pending:
        return Colors.orange[100]!;
      case MovementStatus.approved:
        return Colors.blue[100]!;
      case MovementStatus.completed:
        return Colors.green[100]!;
      case MovementStatus.cancelled:
        return Colors.red[100]!;
    }
  }
}
