import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Import local services and theme
import 'services/language_service.dart';
import 'services/api_service.dart';
import 'utils/tsh_theme.dart';
import 'l10n/tsh_localizations.dart';

void main() {
  runApp(const TSHConsumerApp());
}

class TSHConsumerApp extends StatelessWidget {
  const TSHConsumerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => LanguageService(),
      child: Consumer<LanguageService>(
        builder: (context, languageService, child) {
          return MaterialApp(
            title: 'TSH Consumer App',
            theme: TSHTheme.lightTheme,
            darkTheme: TSHTheme.darkTheme,
            themeMode: languageService.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            locale: languageService.currentLocale,
            localizationsDelegates: const [
              TSHLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            supportedLocales: TSHLocalizations.supportedLocales,
            home: const ConsumerMainScreen(),
            debugShowCheckedModeBanner: false,
            builder: (context, child) {
              return Directionality(
                textDirection: languageService.isRTL 
                    ? TextDirection.rtl 
                    : TextDirection.ltr,
                child: child!,
              );
            },
          );
        },
      ),
    );
  }
}

class ConsumerMainScreen extends StatefulWidget {
  const ConsumerMainScreen({super.key});

  @override
  State<ConsumerMainScreen> createState() => _ConsumerMainScreenState();
}

class _ConsumerMainScreenState extends State<ConsumerMainScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const ConsumerShopScreen(),
    const ProductCatalogScreen(),
    const MyOrdersScreen(),
    const MyAccountScreen(),
    const SupportScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;
    final languageService = Provider.of<LanguageService>(context);

    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                TSHTheme.tshLogo(height: 35),
                const SizedBox(width: 12),
                Text(localizations.translate('tsh_consumer_app')),
              ],
            ),
            Text(
              'Electronics Shopping',
              style: TSHTheme.bodySmall.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
            ),
          ],
        ),
        actions: [
          // Shopping Cart
          IconButton(
            icon: Stack(
              children: [
                const Icon(Icons.shopping_cart),
                Positioned(
                  right: 0,
                  top: 0,
                  child: Container(
                    padding: const EdgeInsets.all(1),
                    decoration: BoxDecoration(
                      color: TSHTheme.accentOrange,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 16,
                      minHeight: 16,
                    ),
                    child: const Text(
                      '3',
                      style: TextStyle(
                        color: TSHTheme.surfaceWhite,
                        fontSize: 12,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ],
            ),
            onPressed: () {},
          ),
          // Language Toggle
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              border: Border.all(color: TSHTheme.surfaceWhite.withOpacity(0.3)),
              borderRadius: BorderRadius.circular(6),
            ),
            child: TextButton(
              onPressed: () => languageService.toggleLanguage(),
              child: Text(
                languageService.currentLocale.languageCode == 'en' ? 'عربي' : 'EN',
                style: const TextStyle(
                  color: TSHTheme.surfaceWhite,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          // Dark Mode Toggle
          IconButton(
            icon: Icon(
              languageService.isDarkMode ? Icons.light_mode : Icons.dark_mode,
              color: TSHTheme.surfaceWhite,
            ),
            onPressed: () => languageService.toggleDarkMode(),
          ),
        ],
      ),
      
      body: _screens[_selectedIndex],
      
      // Bottom Navigation Bar
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.shopping_bag),
            label: 'Shop',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.category),
            label: localizations.translate('products'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.receipt_long),
            label: localizations.translate('orders'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person),
            label: 'Account',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.support_agent),
            label: 'Support',
          ),
        ],
      ),
    );
  }
}

// ===============================================
// CONSUMER SHOP SCREEN - Main Shopping Interface
// ===============================================
class ConsumerShopScreen extends StatefulWidget {
  const ConsumerShopScreen({super.key});

  @override
  State<ConsumerShopScreen> createState() => _ConsumerShopScreenState();
}

class _ConsumerShopScreenState extends State<ConsumerShopScreen> {
  List<Map<String, dynamic>> _products = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    setState(() => _isLoading = true);
    final products = await ApiService.fetchProducts();
    setState(() {
      _products = products;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          localizations.translate('welcome_message'),
                          style: TSHTheme.headingMedium,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Shop Electronics Online',
                          style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.textLight),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () {},
                          child: Text('Start Shopping'),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: TSHTheme.primaryTeal.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.shopping_bag,
                      size: 48,
                      color: TSHTheme.primaryTeal,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          // Featured Categories
          Text(
            'Featured Categories',
            style: TSHTheme.headingSmall,
          ),
          const SizedBox(height: 16),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.2,
            children: [
              _buildCategoryCard('Laptop Accessories', Icons.laptop, TSHTheme.primaryBlue),
              _buildCategoryCard('Mobile Accessories', Icons.smartphone, TSHTheme.primaryTeal),
              _buildCategoryCard('Printer Accessories', Icons.print, TSHTheme.successGreen),
              _buildCategoryCard('Network Equipment', Icons.router, TSHTheme.accentOrange),
            ],
          ),
          const SizedBox(height: 24),
          
          // Special Offers
          Text(
            'Special Offers',
            style: TSHTheme.headingSmall,
          ),
          const SizedBox(height: 16),
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _products.isEmpty
                  ? const Center(child: Text('No products available'))
                  : SizedBox(
                      height: 220,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: _products.length > 10 ? 10 : _products.length,
                        itemBuilder: (context, index) {
                          final product = _products[index];
                          final imageUrl = ApiService.getImageUrl(product['image_path']);

                          return Container(
                            width: 160,
                            margin: const EdgeInsets.only(right: 12),
                            child: Card(
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Container(
                                      height: 90,
                                      decoration: BoxDecoration(
                                        color: TSHTheme.surfaceLight,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: ClipRRect(
                                        borderRadius: BorderRadius.circular(8),
                                        child: imageUrl.isNotEmpty
                                            ? Image.network(
                                                imageUrl,
                                                width: double.infinity,
                                                height: 90,
                                                fit: BoxFit.cover,
                                                errorBuilder: (context, error, stackTrace) {
                                                  return const Center(
                                                    child: Icon(Icons.image_not_supported, size: 40, color: Colors.grey),
                                                  );
                                                },
                                              )
                                            : const Center(
                                                child: Icon(Icons.devices, size: 40, color: TSHTheme.primaryTeal),
                                              ),
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      product['product_name'] ?? 'Unknown Product',
                                      style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      '${product['selling_price'] ?? 0} IQD',
                                      style: TSHTheme.bodySmall.copyWith(
                                        color: TSHTheme.primaryTeal,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    const Spacer(),
                                    SizedBox(
                                      width: double.infinity,
                                      child: ElevatedButton(
                                        onPressed: () {},
                                        style: ElevatedButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(vertical: 6),
                                        ),
                                        child: const Text('Add', style: TextStyle(fontSize: 11)),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
        ],
      ),
    );
  }

  Widget _buildCategoryCard(String title, IconData icon, Color color) {
    return Card(
      child: InkWell(
        onTap: () {},
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  size: 32,
                  color: color,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ===============================================
// PRODUCT CATALOG SCREEN - Full Product Listing
// ===============================================
class ProductCatalogScreen extends StatefulWidget {
  const ProductCatalogScreen({super.key});

  @override
  State<ProductCatalogScreen> createState() => _ProductCatalogScreenState();
}

class _ProductCatalogScreenState extends State<ProductCatalogScreen> {
  List<Map<String, dynamic>> _products = [];
  bool _isLoading = true;
  String _selectedCategory = 'All';

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    setState(() => _isLoading = true);
    final products = await ApiService.fetchProducts();
    setState(() {
      _products = products;
      _isLoading = false;
    });
  }

  List<Map<String, dynamic>> get _filteredProducts {
    if (_selectedCategory == 'All') {
      return _products;
    }
    return _products.where((p) => p['category_name'] == _selectedCategory).toList();
  }

  Set<String> get _categories {
    final cats = _products.map((p) => p['category_name']?.toString() ?? 'Unknown').toSet();
    return {'All', ...cats};
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Category Filter
        Container(
          height: 60,
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: _categories.length,
                  itemBuilder: (context, index) {
                    final category = _categories.elementAt(index);
                    final isSelected = category == _selectedCategory;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: FilterChip(
                        label: Text(category),
                        selected: isSelected,
                        onSelected: (selected) {
                          setState(() => _selectedCategory = category);
                        },
                        backgroundColor: TSHTheme.surfaceLight,
                        selectedColor: TSHTheme.primaryTeal,
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : TSHTheme.textPrimary,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    );
                  },
                ),
        ),

        // Product Grid
        Expanded(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _filteredProducts.isEmpty
                  ? const Center(child: Text('No products available'))
                  : GridView.builder(
                      padding: const EdgeInsets.all(16),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                        childAspectRatio: 0.75,
                      ),
                      itemCount: _filteredProducts.length,
                      itemBuilder: (context, index) {
                        final product = _filteredProducts[index];
                        final imageUrl = ApiService.getImageUrl(product['image_path']);

                        return Card(
                          clipBehavior: Clip.antiAlias,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Product Image
                              Container(
                                height: 140,
                                width: double.infinity,
                                color: TSHTheme.surfaceLight,
                                child: imageUrl.isNotEmpty
                                    ? Image.network(
                                        imageUrl,
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) {
                                          return const Center(
                                            child: Icon(Icons.image_not_supported, size: 50, color: Colors.grey),
                                          );
                                        },
                                      )
                                    : const Center(
                                        child: Icon(Icons.inventory_2, size: 50, color: TSHTheme.primaryTeal),
                                      ),
                              ),

                              // Product Info
                              Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    // Category Badge
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: TSHTheme.primaryTeal.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Text(
                                        product['category_name'] ?? 'Unknown',
                                        style: TSHTheme.bodySmall.copyWith(
                                          color: TSHTheme.primaryTeal,
                                          fontSize: 10,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 8),

                                    // Product Name
                                    Text(
                                      product['product_name'] ?? 'Unknown Product',
                                      style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    const SizedBox(height: 4),

                                    // Stock Info
                                    Text(
                                      'Stock: ${product['quantity'] ?? 0}',
                                      style: TSHTheme.bodySmall.copyWith(
                                        color: (product['quantity'] ?? 0) > 0
                                            ? TSHTheme.successGreen
                                            : TSHTheme.errorRed,
                                      ),
                                    ),
                                    const SizedBox(height: 8),

                                    // Price
                                    Text(
                                      '${product['selling_price'] ?? 0} IQD',
                                      style: TSHTheme.bodyLarge.copyWith(
                                        color: TSHTheme.primaryTeal,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    const SizedBox(height: 8),

                                    // Add to Cart Button
                                    SizedBox(
                                      width: double.infinity,
                                      child: ElevatedButton(
                                        onPressed: (product['quantity'] ?? 0) > 0 ? () {} : null,
                                        style: ElevatedButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(vertical: 8),
                                        ),
                                        child: const Text('Add to Cart', style: TextStyle(fontSize: 12)),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
        ),
      ],
    );
  }
}

class MyOrdersScreen extends StatelessWidget {
  const MyOrdersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('My Orders - Order History'));
  }
}

class MyAccountScreen extends StatelessWidget {
  const MyAccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('My Account - Consumer Profile'));
  }
}

class SupportScreen extends StatelessWidget {
  const SupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Customer Support - 24/7 AI Assistant'));
  }
}
