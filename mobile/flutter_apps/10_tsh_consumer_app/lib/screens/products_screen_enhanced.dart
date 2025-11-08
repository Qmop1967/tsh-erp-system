import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shimmer/shimmer.dart';
import '../models/product.dart';
import '../services/bff_api_service.dart';
import '../providers/cart_provider.dart';
import '../utils/tsh_theme.dart';
import '../widgets/enhanced_product_card.dart';

final productsProvider = FutureProvider<List<Product>>((ref) async {
  final result = await BFFApiService.getConsumerProducts();
  return result['products'] as List<Product>;
});

class ProductsScreenEnhanced extends ConsumerStatefulWidget {
  const ProductsScreenEnhanced({super.key});

  @override
  ConsumerState<ProductsScreenEnhanced> createState() =>
      _ProductsScreenEnhancedState();
}

class _ProductsScreenEnhancedState extends ConsumerState<ProductsScreenEnhanced>
    with SingleTickerProviderStateMixin {
  String _searchQuery = '';
  String _selectedCategory = 'الكل';
  String _sortBy = 'default'; // default, price_low, price_high, name
  List<String> _categories = ['الكل'];
  final TextEditingController _searchController = TextEditingController();
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _loadCategories();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeIn),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _loadCategories() async {
    final categories = await BFFApiService.getConsumerCategories();
    if (mounted) {
      setState(() {
        _categories = ['الكل', ...categories];
      });
    }
  }

  List<Product> _filterProducts(List<Product> products) {
    var filtered = products.where((p) => p.inStock).toList();

    if (_selectedCategory != 'الكل') {
      filtered =
          filtered.where((p) => p.category == _selectedCategory).toList();
    }

    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      filtered = filtered.where((p) {
        final productText =
            '${p.name} ${p.sku} ${p.description ?? ''} ${p.category ?? ''}'
                .toLowerCase();
        return productText.contains(query);
      }).toList();
    }

    // Apply sorting
    switch (_sortBy) {
      case 'price_low':
        filtered.sort((a, b) => a.price.compareTo(b.price));
        break;
      case 'price_high':
        filtered.sort((a, b) => b.price.compareTo(a.price));
        break;
      case 'name':
        filtered.sort((a, b) => a.name.compareTo(b.name));
        break;
      default:
        // Keep default order
        break;
    }

    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    final productsAsync = ref.watch(productsProvider);
    final cart = ref.watch(cartProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: _buildAppBar(cart),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: Column(
          children: [
            // Search Bar with elegant design
            _buildSearchBar(),

            // Category Filter with scrolling
            _buildCategoryFilter(),

            // Sort/Filter Bar
            _buildSortBar(),

            const SizedBox(height: 8),

            // Products Grid
            Expanded(
              child: productsAsync.when(
                data: (products) => _buildProductsGrid(products),
                loading: () => _buildLoadingSkeleton(),
                error: (error, stack) => _buildErrorState(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(List cart) {
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.white,
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [TSHTheme.primary, TSHTheme.accent],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.smart_toy_rounded, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 12),
          const Text(
            'متجر TSH',
            style: TextStyle(
              color: Color(0xFF0F172A),
              fontWeight: FontWeight.bold,
              fontSize: 20,
            ),
          ),
        ],
      ),
      actions: [
        // Cart Icon with animated badge
        Stack(
          children: [
            IconButton(
              icon: const Icon(Icons.shopping_cart_outlined,
                  color: Color(0xFF0F172A)),
              onPressed: () {
                Navigator.pushNamed(context, '/cart');
              },
            ),
            if (cart.isNotEmpty)
              Positioned(
                right: 6,
                top: 6,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [TSHTheme.errorRed, TSHTheme.warningOrange],
                    ),
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: TSHTheme.errorRed.withOpacity(0.4),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  constraints: const BoxConstraints(
                    minWidth: 20,
                    minHeight: 20,
                  ),
                  child: Text(
                    '${cart.length}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(width: 8),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: TextField(
        controller: _searchController,
        onChanged: (value) => setState(() => _searchQuery = value),
        decoration: InputDecoration(
          hintText: 'ابحث عن منتج...',
          hintStyle: TextStyle(color: Colors.grey[400]),
          prefixIcon: Icon(Icons.search, color: TSHTheme.primary, size: 24),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: Icon(Icons.clear, color: Colors.grey[400]),
                  onPressed: () {
                    setState(() {
                      _searchQuery = '';
                      _searchController.clear();
                    });
                  },
                )
              : null,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.white,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        ),
      ),
    );
  }

  // Helper method to get icon for each category
  IconData _getCategoryIcon(String category) {
    final categoryLower = category.toLowerCase();

    if (categoryLower == 'الكل' || categoryLower == 'all') {
      return Icons.grid_view_rounded;
    } else if (categoryLower.contains('laptop') || categoryLower.contains('لابتوب')) {
      return Icons.laptop_mac_rounded;
    } else if (categoryLower.contains('mobile') || categoryLower.contains('phone') || categoryLower.contains('موبايل') || categoryLower.contains('هاتف')) {
      return Icons.smartphone_rounded;
    } else if (categoryLower.contains('tablet') || categoryLower.contains('تابلت')) {
      return Icons.tablet_mac_rounded;
    } else if (categoryLower.contains('printer') || categoryLower.contains('طابعة')) {
      return Icons.print_rounded;
    } else if (categoryLower.contains('camera') || categoryLower.contains('كاميرا')) {
      return Icons.camera_alt_rounded;
    } else if (categoryLower.contains('network') || categoryLower.contains('router') || categoryLower.contains('شبكة')) {
      return Icons.router_rounded;
    } else if (categoryLower.contains('storage') || categoryLower.contains('تخزين')) {
      return Icons.storage_rounded;
    } else if (categoryLower.contains('accessory') || categoryLower.contains('accessories') || categoryLower.contains('إكسسوار')) {
      return Icons.headphones_rounded;
    } else if (categoryLower.contains('monitor') || categoryLower.contains('شاشة')) {
      return Icons.monitor_rounded;
    } else if (categoryLower.contains('keyboard') || categoryLower.contains('لوحة مفاتيح')) {
      return Icons.keyboard_rounded;
    } else if (categoryLower.contains('mouse') || categoryLower.contains('ماوس')) {
      return Icons.mouse_rounded;
    } else if (categoryLower.contains('uncategorized') || categoryLower.contains('غير مصنف')) {
      return Icons.category_rounded;
    }

    // Default icon
    return Icons.inventory_2_rounded;
  }

  Widget _buildCategoryFilter() {
    return SizedBox(
      height: 56,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: _categories.length,
        itemBuilder: (context, index) {
          final category = _categories[index];
          final isSelected = category == _selectedCategory;
          final categoryIcon = _getCategoryIcon(category);

          return Padding(
            padding: const EdgeInsets.only(left: 10),
            child: GestureDetector(
              onTap: () => setState(() => _selectedCategory = category),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 250),
                curve: Curves.easeInOut,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  gradient: isSelected
                      ? LinearGradient(
                          colors: [TSHTheme.primary, TSHTheme.accent],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        )
                      : null,
                  color: isSelected ? null : Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isSelected
                        ? TSHTheme.primary.withOpacity(0.3)
                        : Colors.grey.withOpacity(0.2),
                    width: isSelected ? 2 : 1,
                  ),
                  boxShadow: isSelected
                      ? [
                          BoxShadow(
                            color: TSHTheme.primary.withOpacity(0.3),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ]
                      : [],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      categoryIcon,
                      size: 20,
                      color: isSelected ? Colors.white : TSHTheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      category,
                      style: TextStyle(
                        color: isSelected ? Colors.white : TSHTheme.textPrimary,
                        fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                        fontSize: 14,
                        letterSpacing: 0.2,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSortBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'المنتجات المتوفرة',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: TSHTheme.textSecondary,
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.withOpacity(0.3)),
            ),
            child: DropdownButton<String>(
              value: _sortBy,
              isDense: true,
              underline: const SizedBox(),
              icon: Icon(Icons.sort, size: 18, color: TSHTheme.primary),
              style: TextStyle(fontSize: 13, color: TSHTheme.textPrimary),
              items: const [
                DropdownMenuItem(value: 'default', child: Text('الافتراضي')),
                DropdownMenuItem(value: 'price_low', child: Text('السعر: من الأقل')),
                DropdownMenuItem(value: 'price_high', child: Text('السعر: من الأعلى')),
                DropdownMenuItem(value: 'name', child: Text('الاسم: أ-ي')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _sortBy = value);
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductsGrid(List<Product> products) {
    final filteredProducts = _filterProducts(products);

    if (filteredProducts.isEmpty) {
      return _buildEmptyState();
    }

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(productsProvider);
      },
      color: TSHTheme.primary,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // Responsive grid columns based on screen width
          int crossAxisCount;
          double childAspectRatio;

          if (constraints.maxWidth < 600) {
            // Mobile: 2 columns
            crossAxisCount = 2;
            childAspectRatio = 0.75;
          } else if (constraints.maxWidth < 900) {
            // Tablet: 3 columns
            crossAxisCount = 3;
            childAspectRatio = 0.78;
          } else if (constraints.maxWidth < 1200) {
            // Small Desktop: 4 columns
            crossAxisCount = 4;
            childAspectRatio = 0.76;
          } else {
            // Large Desktop: 5 columns for more products visible
            crossAxisCount = 5;
            childAspectRatio = 0.75;
          }

          return GridView.builder(
            padding: const EdgeInsets.all(20),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              crossAxisSpacing: 20,
              mainAxisSpacing: 24,
              childAspectRatio: childAspectRatio,
            ),
            itemCount: filteredProducts.length,
            itemBuilder: (context, index) {
              return EnhancedProductCard(
                product: filteredProducts[index],
              );
            },
          );
        },
      ),
    );
  }


  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: TSHTheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.inventory_2_outlined,
              size: 80,
              color: TSHTheme.primary.withOpacity(0.5),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'لا توجد منتجات',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: TSHTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'جرب البحث بكلمات مختلفة',
            style: TextStyle(
              fontSize: 14,
              color: TSHTheme.mutedForeground,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: TSHTheme.errorRed.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.error_outline,
              size: 80,
              color: TSHTheme.errorRed,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'فشل في تحميل المنتجات',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: TSHTheme.errorRed,
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () => ref.invalidate(productsProvider),
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
            style: ElevatedButton.styleFrom(
              backgroundColor: TSHTheme.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingSkeleton() {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 0.68,
      ),
      itemCount: 6,
      itemBuilder: (context, index) {
        return Shimmer.fromColors(
          baseColor: Colors.grey[200]!,
          highlightColor: Colors.grey[50]!,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  height: 160,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(16),
                      topRight: Radius.circular(16),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        height: 12,
                        width: 60,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        height: 16,
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Container(
                        height: 16,
                        width: 100,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Container(
                        height: 36,
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
