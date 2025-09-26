import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tsh_core_package/tsh_core_package.dart';
import '../models/inventory_models.dart';
import '../services/inventory_service.dart';

class ItemsManagementScreen extends StatefulWidget {
  const ItemsManagementScreen({super.key});

  @override
  State<ItemsManagementScreen> createState() => _ItemsManagementScreenState();
}

class _ItemsManagementScreenState extends State<ItemsManagementScreen> {
  final InventoryService _inventoryService = InventoryService();
  List<InventoryItem> _items = [];
  List<Category> _categories = [];
  bool _isLoading = true;
  String _searchQuery = '';
  String? _selectedCategoryId;
  ABCClassification? _selectedABCClass;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final itemsFuture = _inventoryService.getItems(
        categoryId: _selectedCategoryId,
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        abcClass: _selectedABCClass,
      );
      final categoriesFuture = _inventoryService.getCategories();

      final results = await Future.wait([itemsFuture, categoriesFuture]);
      
      setState(() {
        _items = results[0] as List<InventoryItem>;
        _categories = results[1] as List<Category>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading items: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;
    final languageService = Provider.of<LanguageService>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text('Items Management'),
        subtitle: Text('${_items.length} items loaded'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search and Filter Bar
          _buildSearchAndFilterBar(),
          
          // Items List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _items.isEmpty
                    ? _buildEmptyState()
                    : _buildItemsList(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddItemDialog(),
        backgroundColor: TSHTheme.primaryTeal,
        icon: const Icon(Icons.add),
        label: const Text('Add Item'),
      ),
    );
  }

  Widget _buildSearchAndFilterBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        border: Border(bottom: BorderSide(color: Colors.grey.shade200)),
      ),
      child: Column(
        children: [
          // Search Bar
          TextField(
            decoration: InputDecoration(
              hintText: 'Search items by name, SKU, or barcode...',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        setState(() => _searchQuery = '');
                        _loadData();
                      },
                    )
                  : null,
            ),
            onChanged: (value) {
              setState(() => _searchQuery = value);
              // Debounced search would be implemented here
            },
            onSubmitted: (value) => _loadData(),
          ),
          
          const SizedBox(height: 12),
          
          // Filter Chips
          Row(
            children: [
              // Category Filter
              if (_selectedCategoryId != null)
                Chip(
                  label: Text(_getCategoryName(_selectedCategoryId!)),
                  onDeleted: () {
                    setState(() => _selectedCategoryId = null);
                    _loadData();
                  },
                ),
              
              // ABC Class Filter
              if (_selectedABCClass != null)
                Chip(
                  label: Text('ABC: ${_selectedABCClass!.name}'),
                  onDeleted: () {
                    setState(() => _selectedABCClass = null);
                    _loadData();
                  },
                ),
                
              const Spacer(),
              
              Text('${_items.length} items'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildItemsList() {
    return ListView.separated(
      itemCount: _items.length,
      separatorBuilder: (context, index) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final item = _items[index];
        return _buildItemCard(item);
      },
    );
  }

  Widget _buildItemCard(InventoryItem item) {
    final languageService = Provider.of<LanguageService>(context, listen: false);
    final itemName = languageService.currentLocale.languageCode == 'ar' 
        ? item.nameAr 
        : item.nameEn;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getABCColor(item.abcClass),
          child: Text(
            item.abcClass.name,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          itemName,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('SKU: ${item.sku}'),
            Text('Brand: ${item.brand}'),
            if (item.variants.isNotEmpty)
              Text('Variants: ${item.variants.length}'),
            Row(
              children: [
                Text('USD: \$${item.purchaseCosts['USD']?.toStringAsFixed(2) ?? 'N/A'}'),
                const SizedBox(width: 16),
                Text('IQD: ${item.purchaseCosts['IQD']?.toStringAsFixed(0) ?? 'N/A'}'),
              ],
            ),
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) => _handleItemAction(value, item),
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'edit', child: Text('Edit')),
            const PopupMenuItem(value: 'duplicate', child: Text('Duplicate')),
            const PopupMenuItem(value: 'view_stock', child: Text('View Stock')),
            const PopupMenuItem(value: 'barcode', child: Text('Generate Barcode')),
            const PopupMenuItem(value: 'delete', child: Text('Delete')),
          ],
        ),
        onTap: () => _showItemDetails(item),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.inventory_2_outlined,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            'No items found',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Add your first inventory item to get started',
            style: TextStyle(color: Colors.grey.shade500),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => _showAddItemDialog(),
            icon: const Icon(Icons.add),
            label: const Text('Add First Item'),
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter Items'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Category Filter
            DropdownButtonFormField<String>(
              value: _selectedCategoryId,
              decoration: const InputDecoration(labelText: 'Category'),
              items: [
                const DropdownMenuItem(value: null, child: Text('All Categories')),
                ..._categories.map((category) => DropdownMenuItem(
                  value: category.id,
                  child: Text(category.nameEn),
                )),
              ],
              onChanged: (value) => setState(() => _selectedCategoryId = value),
            ),
            
            const SizedBox(height: 16),
            
            // ABC Classification Filter
            DropdownButtonFormField<ABCClassification>(
              value: _selectedABCClass,
              decoration: const InputDecoration(labelText: 'ABC Classification'),
              items: [
                const DropdownMenuItem(value: null, child: Text('All Classes')),
                ...ABCClassification.values.map((abc) => DropdownMenuItem(
                  value: abc,
                  child: Text('Class ${abc.name}'),
                )),
              ],
              onChanged: (value) => setState(() => _selectedABCClass = value),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _selectedCategoryId = null;
                _selectedABCClass = null;
              });
              Navigator.pop(context);
              _loadData();
            },
            child: const Text('Clear All'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _loadData();
            },
            child: const Text('Apply'),
          ),
        ],
      ),
    );
  }

  void _showAddItemDialog() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => AddEditItemScreen(
          categories: _categories,
          onItemSaved: () {
            _loadData();
          },
        ),
      ),
    );
  }

  void _showItemDetails(InventoryItem item) {
    showDialog(
      context: context,
      builder: (context) => ItemDetailsDialog(item: item),
    );
  }

  void _handleItemAction(String action, InventoryItem item) {
    switch (action) {
      case 'edit':
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => AddEditItemScreen(
              item: item,
              categories: _categories,
              onItemSaved: () => _loadData(),
            ),
          ),
        );
        break;
      case 'duplicate':
        _duplicateItem(item);
        break;
      case 'view_stock':
        _viewItemStock(item);
        break;
      case 'barcode':
        _generateBarcode(item);
        break;
      case 'delete':
        _deleteItem(item);
        break;
    }
  }

  void _duplicateItem(InventoryItem item) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => AddEditItemScreen(
          item: item,
          categories: _categories,
          isDuplicate: true,
          onItemSaved: () => _loadData(),
        ),
      ),
    );
  }

  void _viewItemStock(InventoryItem item) {
    // Implementation for viewing stock levels across warehouses
  }

  void _generateBarcode(InventoryItem item) {
    // Implementation for barcode generation
  }

  void _deleteItem(InventoryItem item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Item'),
        content: Text('Are you sure you want to delete "${item.nameEn}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () async {
              try {
                await _inventoryService.deleteItem(item.id);
                Navigator.pop(context);
                _loadData();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Item deleted successfully')),
                );
              } catch (e) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Error deleting item: $e')),
                );
              }
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  String _getCategoryName(String categoryId) {
    final category = _categories.firstWhere(
      (cat) => cat.id == categoryId,
      orElse: () => Category(id: '', nameEn: 'Unknown', nameAr: 'غير معروف'),
    );
    return category.nameEn;
  }

  Color _getABCColor(ABCClassification abc) {
    switch (abc) {
      case ABCClassification.A:
        return Colors.green;
      case ABCClassification.B:
        return Colors.orange;
      case ABCClassification.C:
        return Colors.red;
    }
  }
}

// Placeholder screens - will be implemented separately
class AddEditItemScreen extends StatefulWidget {
  final InventoryItem? item;
  final List<Category> categories;
  final bool isDuplicate;
  final VoidCallback onItemSaved;

  const AddEditItemScreen({
    super.key,
    this.item,
    required this.categories,
    this.isDuplicate = false,
    required this.onItemSaved,
  });

  @override
  State<AddEditItemScreen> createState() => _AddEditItemScreenState();
}

class _AddEditItemScreenState extends State<AddEditItemScreen> {
  // Implementation will be added in next phase
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.item == null ? 'Add Item' : 'Edit Item'),
      ),
      body: const Center(
        child: Text('Add/Edit Item Form - To be implemented'),
      ),
    );
  }
}

class ItemDetailsDialog extends StatelessWidget {
  final InventoryItem item;

  const ItemDetailsDialog({super.key, required this.item});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(item.nameEn),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('SKU: ${item.sku}'),
          Text('Brand: ${item.brand}'),
          Text('ABC Class: ${item.abcClass.name}'),
          if (item.variants.isNotEmpty)
            Text('Variants: ${item.variants.length}'),
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
