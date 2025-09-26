import 'package:flutter/material.dart';
import '../models/inventory_models.dart';
import '../services/inventory_service.dart';

class ItemsManagementScreen extends StatefulWidget {
  const ItemsManagementScreen({super.key});

  @override
  State<ItemsManagementScreen> createState() => _ItemsManagementScreenState();
}

class _ItemsManagementScreenState extends State<ItemsManagementScreen> {
  List<InventoryItem> _items = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  Future<void> _loadItems() async {
    setState(() => _isLoading = true);
    try {
      final service = InventoryService();
      final items = await service.getItems();
      if (mounted) {
        setState(() {
          _items = items;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading items: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Items Management'),
            Text(
              '${_items.length} items loaded',
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {},
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _items.isEmpty
              ? const Center(child: Text('No items found'))
              : ListView.builder(
                  itemCount: _items.length,
                  itemBuilder: (context, index) => _buildItemCard(_items[index]),
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildItemCard(InventoryItem item) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          child: Text(item.nameEn.substring(0, 1).toUpperCase()),
        ),
        title: Text(item.nameEn),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('SKU: ${item.sku}'),
            Text('Category: ${item.categoryId}'),
            Text('Brand: ${item.brand}'),
            Text('Unit: ${item.unitOfMeasure}'),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              item.salesPriceLists.isNotEmpty 
                  ? '\$${item.salesPriceLists.first.toStringAsFixed(2)}'
                  : 'No price',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Icon(
              item.trackStock ? Icons.check_circle : Icons.info,
              color: item.trackStock ? Colors.green : Colors.orange,
              size: 16,
            ),
          ],
        ),
        onTap: () => _showItemDetails(item),
      ),
    );
  }

  void _showItemDetails(InventoryItem item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(item.nameEn),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('SKU: ${item.sku}'),
            Text('Barcode: ${item.barcode}'),
            Text('Arabic Name: ${item.nameAr}'),
            Text('Category ID: ${item.categoryId}'),
            Text('Brand: ${item.brand}'),
            Text('Unit: ${item.unitOfMeasure}'),
            Text('ABC Class: ${item.abcClass.name}'),
            Text('Track Stock: ${item.trackStock ? "Yes" : "No"}'),
            if (item.salesPriceLists.isNotEmpty)
              Text('Price: \$${item.salesPriceLists.first.toStringAsFixed(2)}'),
            if (item.defaultSupplierId != null)
              Text('Supplier ID: ${item.defaultSupplierId}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
