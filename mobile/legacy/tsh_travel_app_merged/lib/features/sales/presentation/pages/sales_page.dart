import 'package:flutter/material.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

class SalesPage extends StatefulWidget {
  const SalesPage({super.key});

  @override
  State<SalesPage> createState() => _SalesPageState();
}

class _SalesPageState extends State<SalesPage> with TickerProviderStateMixin {
  late TabController _tabController;
  final _cart = Cart.empty();

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
      body: Column(
        children: [
          // Enhanced Header
          Container(
            padding: const EdgeInsets.fromLTRB(16, 60, 16, 20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  AppColors.primary,
                  AppColors.primary.withValues(alpha: 0.8),
                ],
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Sales Center',
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Create orders and manage your sales pipeline',
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: 0.9),
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Badge(
                        isLabelVisible: _cart.items.isNotEmpty,
                        label: Text('${_cart.items.length}'),
                        child: const Icon(
                          Icons.shopping_cart_rounded,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                
                // Tab Bar
                TabBar(
                  controller: _tabController,
                  tabs: const [
                    Tab(text: 'New Sale', icon: Icon(Icons.add_shopping_cart)),
                    Tab(text: 'Cart', icon: Icon(Icons.shopping_cart)),
                  ],
                  labelColor: Colors.white,
                  unselectedLabelColor: Colors.white70,
                  indicatorColor: Colors.white,
                ),
              ],
            ),
          ),
          // Tab Bar View
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildNewSaleTab(),
                _buildCartTab(),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: _cart.isNotEmpty
          ? FloatingActionButton.extended(
              onPressed: _processCheckout,
              icon: const Icon(Icons.payment),
              label: Text('Checkout (\$${_cart.totalAmount.toStringAsFixed(2)})'),
            )
          : null,
    );
  }

  Widget _buildNewSaleTab() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Search Bar
          AppTextField(
            hint: 'Search products...',
            prefixIcon: const Icon(Icons.search),
            onChanged: (value) {
              // TODO: Implement product search
            },
          ),
          const SizedBox(height: 16),
          
          // Categories
          SizedBox(
            height: 50,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                _buildCategoryChip('All', true),
                _buildCategoryChip('Electronics', false),
                _buildCategoryChip('Clothing', false),
                _buildCategoryChip('Home & Garden', false),
                _buildCategoryChip('Sports', false),
              ],
            ),
          ),
          const SizedBox(height: 16),
          
          // Products Grid
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.8,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
              ),
              itemCount: _mockProducts.length,
              itemBuilder: (context, index) {
                final product = _mockProducts[index];
                return _buildProductCard(product);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCartTab() {
    if (_cart.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.shopping_cart_outlined,
              size: 64,
              color: AppColors.textSecondary400,
            ),
            const SizedBox(height: 16),
            Text(
              'Your cart is empty',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Add some products to get started',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary500,
              ),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Cart Items
          Expanded(
            child: ListView.separated(
              itemCount: _cart.items.length,
              separatorBuilder: (context, index) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final item = _cart.items[index];
                return _buildCartItem(item);
              },
            ),
          ),
          
          // Cart Summary
          AppCard(
            child: Column(
              children: [
                _buildSummaryRow('Subtotal', _cart.subtotal),
                _buildSummaryRow('Tax', _cart.taxAmount),
                _buildSummaryRow('Discount', -_cart.discountAmount),
                const Divider(),
                _buildSummaryRow('Total', _cart.totalAmount, isTotal: true),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryChip(String label, bool isSelected) {
    return Container(
      margin: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (selected) {
          // TODO: Handle category selection
        },
        backgroundColor: Colors.white,
        selectedColor: AppColors.primary.withValues(alpha: 0.2),
        labelStyle: TextStyle(
          color: isSelected ? AppColors.primary : AppColors.textSecondary,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
        ),
      ),
    );
  }

  Widget _buildProductCard(Product product) {
    return AppCard(
      onTap: () => _addToCart(product),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Product Image
          Container(
            width: double.infinity,
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
          const SizedBox(height: 8),
          
          // Product Name
          Text(
            product.name,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          
          // Product Price
          Text(
            '\$${product.price.toStringAsFixed(2)}',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          
          // Stock Status
          Row(
            children: [
              Icon(
                product.stockQuantity > 0 ? Icons.check_circle : Icons.error,
                size: 16,
                color: product.stockQuantity > 0 ? AppColors.success : AppColors.error,
              ),
              const SizedBox(width: 4),
              Text(
                product.stockQuantity > 0 ? 'In Stock (${product.stockQuantity})' : 'Out of Stock',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: product.stockQuantity > 0 ? AppColors.success : AppColors.error,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCartItem(CartItem item) {
    return AppCard(
      child: Row(
        children: [
          // Product Image
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: AppColors.textSecondary100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.inventory_2_outlined,
              color: AppColors.textSecondary400,
            ),
          ),
          const SizedBox(width: 12),
          
          // Product Details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.product.name,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '\$${item.unitPrice.toStringAsFixed(2)} each',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          
          // Quantity Controls
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                onPressed: () => _updateQuantity(item, item.quantity - 1),
                icon: const Icon(Icons.remove_circle_outline),
                constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  border: Border.all(color: AppColors.textSecondary300),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  item.quantity.toString(),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              IconButton(
                onPressed: () => _updateQuantity(item, item.quantity + 1),
                icon: const Icon(Icons.add_circle_outline),
                constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
              ),
            ],
          ),
          
          // Total Price
          Text(
            '\$${item.totalPrice.toStringAsFixed(2)}',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, double amount, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            '\$${amount.toStringAsFixed(2)}',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
              color: isTotal ? AppColors.primary : null,
            ),
          ),
        ],
      ),
    );
  }

  void _addToCart(Product product) {
    // TODO: Implement add to cart functionality
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('${product.name} added to cart'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  void _updateQuantity(CartItem item, int newQuantity) {
    // TODO: Implement quantity update
    if (newQuantity <= 0) {
      // Remove from cart
    } else {
      // Update quantity
    }
  }

  void _processCheckout() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Checkout'),
        content: const Text('Proceed with checkout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          AppButton.primary(
            text: 'Confirm',
            onPressed: () {
              Navigator.of(context).pop();
              // TODO: Process order
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Order placed successfully!'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

// Mock data
final List<Product> _mockProducts = [
  Product(
    id: 1,
    name: 'Wireless Headphones',
    sku: 'WH001',
    price: 99.99,
    stockQuantity: 25,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 2,
    name: 'Smartphone Case',
    sku: 'SC001',
    price: 19.99,
    stockQuantity: 50,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 3,
    name: 'Bluetooth Speaker',
    sku: 'BS001',
    price: 79.99,
    stockQuantity: 15,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 4,
    name: 'USB Cable',
    sku: 'UC001',
    price: 12.99,
    stockQuantity: 100,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 5,
    name: 'Wireless Mouse',
    sku: 'WM001',
    price: 29.99,
    stockQuantity: 30,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
  Product(
    id: 6,
    name: 'Laptop Stand',
    sku: 'LS001',
    price: 45.99,
    stockQuantity: 0,
    isActive: true,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  ),
];
