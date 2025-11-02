import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/product.dart';
import '../../utils/tsh_theme.dart';
import '../../utils/tsh_localizations.dart';
import '../../services/cart_service.dart';

class EnhancedProductCatalogScreen extends StatefulWidget {
  const EnhancedProductCatalogScreen({super.key});

  @override
  State<EnhancedProductCatalogScreen> createState() =>
      _EnhancedProductCatalogScreenState();
}

class _EnhancedProductCatalogScreenState
    extends State<EnhancedProductCatalogScreen> {
  List<Product> _allProducts = [];
  List<Product> _filteredProducts = [];
  bool _isLoading = false;
  String _searchQuery = '';
  String? _selectedCategory;
  final List<String> _categories = ['All', 'Electronics', 'Accessories', 'Components'];

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    setState(() => _isLoading = true);

    // Mock data - Replace with actual API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _allProducts = [
        Product(
          id: '1',
          name: 'iPhone 15 Pro Max',
          description: 'Latest flagship smartphone with advanced features',
          sku: 'IPHPM15',
          wholesalePrice: 1200000,
          retailPrice: 1500000,
          currency: 'IQD',
          stockQuantity: 50,
          minOrderQuantity: 1,
          category: 'Electronics',
          brand: 'Apple',
          imageUrl: null,
        ),
        Product(
          id: '2',
          name: 'Samsung Galaxy S24 Ultra',
          description: 'Premium Android smartphone',
          sku: 'SGS24U',
          wholesalePrice: 1150000,
          retailPrice: 1450000,
          currency: 'IQD',
          stockQuantity: 35,
          minOrderQuantity: 1,
          category: 'Electronics',
          brand: 'Samsung',
        ),
        Product(
          id: '3',
          name: 'Wireless Earbuds Pro',
          description: 'High-quality wireless earphones',
          sku: 'WEPRO',
          wholesalePrice: 80000,
          retailPrice: 120000,
          currency: 'IQD',
          stockQuantity: 200,
          minOrderQuantity: 5,
          category: 'Accessories',
          brand: 'Generic',
        ),
        Product(
          id: '4',
          name: 'USB-C Cable 2m',
          description: 'Fast charging USB-C cable',
          sku: 'USBC2M',
          wholesalePrice: 5000,
          retailPrice: 10000,
          currency: 'IQD',
          stockQuantity: 500,
          minOrderQuantity: 10,
          category: 'Accessories',
          brand: 'Generic',
        ),
        Product(
          id: '5',
          name: 'Power Bank 20000mAh',
          description: 'High capacity portable charger',
          sku: 'PB20K',
          wholesalePrice: 35000,
          retailPrice: 50000,
          currency: 'IQD',
          stockQuantity: 3,
          minOrderQuantity: 5,
          category: 'Accessories',
          brand: 'Anker',
        ),
        Product(
          id: '6',
          name: 'Laptop Stand Aluminum',
          description: 'Ergonomic aluminum laptop stand',
          sku: 'LSAL',
          wholesalePrice: 45000,
          retailPrice: 70000,
          currency: 'IQD',
          stockQuantity: 80,
          minOrderQuantity: 2,
          category: 'Accessories',
          brand: 'Generic',
        ),
      ];
      _filteredProducts = _allProducts;
      _isLoading = false;
    });
  }

  void _filterProducts() {
    setState(() {
      _filteredProducts = _allProducts.where((product) {
        // Search filter
        final matchesSearch = _searchQuery.isEmpty ||
            product.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            (product.description?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false) ||
            (product.sku?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false);

        // Category filter
        final matchesCategory = _selectedCategory == null ||
            _selectedCategory == 'All' ||
            product.category == _selectedCategory;

        return matchesSearch && matchesCategory;
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    final loc = TSHLocalizations.of(context)!;

    return Scaffold(
      body: Column(
        children: [
          // Search Bar
          Container(
            padding: const EdgeInsets.all(16),
            color: TSHTheme.backgroundLight,
            child: Column(
              children: [
                TextField(
                  decoration: InputDecoration(
                    hintText: loc.translate('search'),
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                  onChanged: (value) {
                    setState(() => _searchQuery = value);
                    _filterProducts();
                  },
                ),
                const SizedBox(height: 12),
                // Category Filter
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: _categories.map((category) {
                      final isSelected = _selectedCategory == category ||
                          (category == 'All' && _selectedCategory == null);
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: Text(category),
                          selected: isSelected,
                          onSelected: (selected) {
                            setState(() {
                              _selectedCategory = selected && category != 'All' ? category : null;
                            });
                            _filterProducts();
                          },
                          selectedColor: TSHTheme.primary.withOpacity(0.2),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),

          // Products Grid
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredProducts.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.inventory_2,
                                size: 64, color: TSHTheme.textSecondary),
                            const SizedBox(height: 16),
                            Text(
                              'No products found',
                              style: TSHTheme.bodyLarge
                                  .copyWith(color: TSHTheme.textSecondary),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadProducts,
                        child: GridView.builder(
                          padding: const EdgeInsets.all(16),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            childAspectRatio: 0.75,
                            crossAxisSpacing: 12,
                            mainAxisSpacing: 12,
                          ),
                          itemCount: _filteredProducts.length,
                          itemBuilder: (context, index) {
                            final product = _filteredProducts[index];
                            return _buildProductCard(product, loc);
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductCard(Product product, TSHLocalizations loc) {
    final cartService = Provider.of<CartService>(context);
    final isInCart = cartService.isInCart(product.id);

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
            // Image placeholder
            Container(
              height: 110,
              color: TSHTheme.backgroundLight,
              child: Center(
                child: Icon(
                  Icons.image,
                  size: 48,
                  color: TSHTheme.textSecondary,
                ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.name,
                      style: TSHTheme.bodyMedium.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    if (product.brand != null)
                      Text(
                        product.brand!,
                        style: TSHTheme.bodySmall,
                      ),
                    const Spacer(),
                    Text(
                      loc.formatCurrency(product.wholesalePrice),
                      style: TSHTheme.bodyLarge.copyWith(
                        color: TSHTheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          product.inStock ? Icons.check_circle : Icons.cancel,
                          size: 16,
                          color: product.inStock
                              ? TSHTheme.successGreen
                              : TSHTheme.errorRed,
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            product.inStock
                                ? (product.lowStock
                                    ? 'Low Stock (${product.stockQuantity})'
                                    : 'In Stock (${product.stockQuantity})')
                                : 'Out of Stock',
                            style: TSHTheme.bodySmall.copyWith(
                              color: product.inStock
                                  ? (product.lowStock
                                      ? TSHTheme.warningOrange
                                      : TSHTheme.successGreen)
                                  : TSHTheme.errorRed,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            // Add to Cart Button
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                border: Border(
                  top: BorderSide(color: TSHTheme.border, width: 1),
                ),
              ),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: product.inStock ? () {
                    cartService.addToCart(product, quantity: product.minOrderQuantity);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('${product.name} added to cart'),
                        duration: const Duration(seconds: 1),
                        backgroundColor: TSHTheme.successGreen,
                      ),
                    );
                  } : null,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          isInCart ? Icons.shopping_cart : Icons.add_shopping_cart,
                          size: 18,
                          color: product.inStock
                            ? (isInCart ? TSHTheme.successGreen : TSHTheme.primary)
                            : TSHTheme.textSecondary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          isInCart ? 'In Cart' : 'Add to Cart',
                          style: TSHTheme.bodySmall.copyWith(
                            fontWeight: FontWeight.bold,
                            color: product.inStock
                              ? (isInCart ? TSHTheme.successGreen : TSHTheme.primary)
                              : TSHTheme.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
