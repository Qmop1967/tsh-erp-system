import 'package:flutter/material.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

class ProductsPage extends StatefulWidget {
  const ProductsPage({super.key});

  @override
  State<ProductsPage> createState() => _ProductsPageState();
}

class _ProductsPageState extends State<ProductsPage> {
  String _searchQuery = '';
  String _selectedCategory = 'All';
  bool _showOutOfStock = true;

  @override
  Widget build(BuildContext context) {
    final filteredProducts = _getFilteredProducts();

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Search and Filters
            _buildSearchAndFilters(),
            const SizedBox(height: 16),
            
            // Products List
            Expanded(
              child: filteredProducts.isEmpty
                  ? _buildEmptyState()
                  : ListView.separated(
                      itemCount: filteredProducts.length,
                      separatorBuilder: (context, index) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final product = filteredProducts[index];
                        return _buildProductCard(product);
                      },
                    ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddProductDialog,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildSearchAndFilters() {
    return Column(
      children: [
        // Search Bar
        AppTextField(
          hint: 'Search products...',
          prefixIcon: const Icon(Icons.search),
          onChanged: (value) {
            setState(() {
              _searchQuery = value;
            });
          },
        ),
        const SizedBox(height: 12),
        
        // Filters Row
        Row(
          children: [
            // Category Filter
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _selectedCategory,
                decoration: const InputDecoration(
                  labelText: 'Category',
                  prefixIcon: Icon(Icons.category),
                ),
                items: ['All', 'Electronics', 'Clothing', 'Home & Garden', 'Sports']
                    .map((category) => DropdownMenuItem(
                          value: category,
                          child: Text(category),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedCategory = value!;
                  });
                },
              ),
            ),
            const SizedBox(width: 12),
            
            // Filter Button
            OutlinedButton.icon(
              onPressed: _showFilterDialog,
              icon: const Icon(Icons.filter_list),
              label: const Text('Filters'),
            ),
          ],
        ),
      ],
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
            color: AppColors.textSecondary400,
          ),
          const SizedBox(height: 16),
          Text(
            'No products found',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Try adjusting your search or filters',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.textSecondary500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductCard(Product product) {
    return AppCard(
      onTap: () => _showProductDetails(product),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              // Product Image
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: AppColors.textSecondary100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.inventory_2_outlined,
                  color: AppColors.textSecondary400,
                  size: 32,
                ),
              ),
              const SizedBox(width: 16),
              
              // Product Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.name,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'SKU: ${product.sku}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Text(
                          '\$${product.price.toStringAsFixed(2)}',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (product.costPrice != null) ...[
                          const SizedBox(width: 8),
                          Text(
                            'Cost: \$${product.costPrice!.toStringAsFixed(2)}',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              
              // Actions
              PopupMenuButton<String>(
                onSelected: (value) => _handleProductAction(value, product),
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'edit',
                    child: ListTile(
                      leading: Icon(Icons.edit),
                      title: Text('Edit'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'duplicate',
                    child: ListTile(
                      leading: Icon(Icons.copy),
                      title: Text('Duplicate'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'delete',
                    child: ListTile(
                      leading: Icon(Icons.delete, color: Colors.red),
                      title: Text('Delete', style: TextStyle(color: Colors.red)),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          // Stock and Status
          Row(
            children: [
              _buildStockChip(product),
              const SizedBox(width: 8),
              _buildStatusChip(product.isActive),
              const Spacer(),
              if (product.isLowStock) ...[
                Icon(
                  Icons.warning,
                  size: 16,
                  color: AppColors.warning,
                ),
                const SizedBox(width: 4),
                Text(
                  'Low Stock',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.warning,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStockChip(Product product) {
    Color color = product.isOutOfStock 
        ? AppColors.error 
        : product.isLowStock 
            ? AppColors.warning 
            : AppColors.success;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        'Stock: ${product.stockQuantity}',
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildStatusChip(bool isActive) {
    Color color = isActive ? AppColors.success : AppColors.error;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        isActive ? 'Active' : 'Inactive',
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  List<Product> _getFilteredProducts() {
    return _mockProducts.where((product) {
      // Search filter
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        if (!product.name.toLowerCase().contains(query) &&
            !product.sku.toLowerCase().contains(query)) {
          return false;
        }
      }
      
      // Category filter (simplified - in real app, products would have categories)
      if (_selectedCategory != 'All') {
        // Mock category logic
        if (_selectedCategory == 'Electronics' && !product.name.contains('phone') && 
            !product.name.contains('Speaker') && !product.name.contains('Mouse')) {
          return false;
        }
      }
      
      // Stock filter
      if (!_showOutOfStock && product.isOutOfStock) {
        return false;
      }
      
      return true;
    }).toList();
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filters'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CheckboxListTile(
              title: const Text('Show out of stock products'),
              value: _showOutOfStock,
              onChanged: (value) {
                setState(() {
                  _showOutOfStock = value!;
                });
                Navigator.of(context).pop();
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showProductDetails(Product product) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.9,
        builder: (context, scrollController) => Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle bar
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.textSecondary300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              
              // Product details
              Text(
                product.name,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'SKU: ${product.sku}',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 16),
              
              // Price and stock info
              Row(
                children: [
                  AppStatsCard(
                    title: 'Price',
                    value: '\$${product.price.toStringAsFixed(2)}',
                    icon: Icons.attach_money,
                    color: AppColors.primary,
                  ),
                  const SizedBox(width: 16),
                  AppStatsCard(
                    title: 'Stock',
                    value: product.stockQuantity.toString(),
                    icon: Icons.inventory,
                    color: product.isOutOfStock ? AppColors.error : AppColors.success,
                  ),
                ],
              ),
              
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: AppButton.outline(
                      text: 'Edit Product',
                      onPressed: () => _editProduct(product),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: AppButton.primary(
                      text: 'Add to Sale',
                      onPressed: () => _addToSale(product),
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

  void _showAddProductDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add New Product'),
        content: const Text('Add product functionality would be implemented here.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          AppButton.primary(
            text: 'Add',
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Product added successfully!'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _handleProductAction(String action, Product product) {
    switch (action) {
      case 'edit':
        _editProduct(product);
        break;
      case 'duplicate':
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${product.name} duplicated'),
            backgroundColor: AppColors.info,
          ),
        );
        break;
      case 'delete':
        _deleteProduct(product);
        break;
    }
  }

  void _editProduct(Product product) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Edit ${product.name}'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  void _deleteProduct(Product product) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Product'),
        content: Text('Are you sure you want to delete ${product.name}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          AppButton.primary(
            text: 'Delete',
            customColor: AppColors.error,
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('${product.name} deleted'),
                  backgroundColor: AppColors.error,
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _addToSale(Product product) {
    Navigator.of(context).pop(); // Close bottom sheet
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('${product.name} added to current sale'),
        backgroundColor: AppColors.success,
      ),
    );
  }
}

// Using the same mock products from sales page
final List<Product> _mockProducts = [
  Product(
    id: 1,
    name: 'Wireless Headphones',
    sku: 'WH001',
    price: 99.99,
    costPrice: 60.00,
    stockQuantity: 25,
    minStockLevel: 10,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 2,
    name: 'Smartphone Case',
    sku: 'SC001',
    price: 19.99,
    costPrice: 8.00,
    stockQuantity: 50,
    minStockLevel: 20,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 3,
    name: 'Bluetooth Speaker',
    sku: 'BS001',
    price: 79.99,
    costPrice: 45.00,
    stockQuantity: 5,
    minStockLevel: 10,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 4,
    name: 'USB Cable',
    sku: 'UC001',
    price: 12.99,
    costPrice: 5.00,
    stockQuantity: 100,
    minStockLevel: 50,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 5,
    name: 'Wireless Mouse',
    sku: 'WM001',
    price: 29.99,
    costPrice: 15.00,
    stockQuantity: 30,
    minStockLevel: 15,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 6,
    name: 'Laptop Stand',
    sku: 'LS001',
    price: 45.99,
    costPrice: 25.00,
    stockQuantity: 0,
    minStockLevel: 5,
    isActive: false,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
];
