import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Import TSH Theme and Utilities
import 'utils/tsh_theme.dart';
import 'utils/tsh_localizations.dart';
import 'utils/language_service.dart';

// Import TSH ERP Services
import 'services/storage_service.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'services/product_service.dart';
import 'services/cart_service.dart';

// Import Screens
import 'screens/support/support_tickets_screen.dart';
import 'screens/payments/payments_screen.dart';
import 'screens/invoices/invoices_screen.dart';
import 'screens/account/credit_notes_screen.dart';
import 'screens/account/account_statement_screen.dart';
import 'screens/products/enhanced_product_catalog_screen.dart';

void main() async {
  // Ensure Flutter bindings are initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize services
  final storageService = StorageService();
  await storageService.init();

  final apiService = ApiService(storageService);
  final authService = AuthService(apiService, storageService);
  final productService = ProductService(apiService);

  runApp(TSHWholesaleClientApp(
    storageService: storageService,
    apiService: apiService,
    authService: authService,
    productService: productService,
  ));
}

class TSHWholesaleClientApp extends StatelessWidget {
  final StorageService storageService;
  final ApiService apiService;
  final AuthService authService;
  final ProductService productService;

  const TSHWholesaleClientApp({
    super.key,
    required this.storageService,
    required this.apiService,
    required this.authService,
    required this.productService,
  });

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Core Services
        Provider<StorageService>.value(value: storageService),
        Provider<ApiService>.value(value: apiService),
        ChangeNotifierProvider<AuthService>.value(value: authService),
        Provider<ProductService>.value(value: productService),

        // UI Services
        ChangeNotifierProvider(create: (context) => LanguageService()),
        ChangeNotifierProvider(create: (context) => CartService()),
      ],
      child: Consumer<LanguageService>(
        builder: (context, languageService, child) {
          return MaterialApp(
            title: 'TSH Wholesale Client',
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
            home: const WholesaleMainScreen(),
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

class WholesaleMainScreen extends StatefulWidget {
  const WholesaleMainScreen({super.key});

  @override
  State<WholesaleMainScreen> createState() => _WholesaleMainScreenState();
}

class _WholesaleMainScreenState extends State<WholesaleMainScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const WholesaleDashboardScreen(),
    const EnhancedProductCatalogScreen(),
    const OrderManagementScreen(),
    const AccountManagementScreen(),
    const WholesaleSettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;
    final languageService = Provider.of<LanguageService>(context);
    final cartService = Provider.of<CartService>(context);

    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        leading: Builder(
          builder: (context) => IconButton(
            icon: CircleAvatar(
              backgroundColor: Colors.white24,
              child: Icon(Icons.person, color: TSHTheme.surfaceWhite),
            ),
            onPressed: () => Scaffold.of(context).openDrawer(),
            tooltip: localizations.translate('my_profile'),
          ),
        ),
        title: Row(
          children: [
            TSHTheme.tshLogo(height: 35),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(localizations.translate('wholesale_client')),
                Text(
                  'B2B Electronics Trading',
                  style: TSHTheme.bodySmall.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
                ),
              ],
            ),
          ],
        ),
        actions: [
          // Shopping Cart
          IconButton(
            icon: Stack(
              children: [
                const Icon(Icons.shopping_cart),
                if (cartService.itemCount > 0)
                  Positioned(
                    right: 0,
                    top: 0,
                    child: Container(
                      padding: const EdgeInsets.all(2),
                      decoration: BoxDecoration(
                        color: TSHTheme.successGreen,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 16,
                        minHeight: 16,
                      ),
                      child: Text(
                        '${cartService.itemCount}',
                        style: const TextStyle(
                          color: TSHTheme.surfaceWhite,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
              ],
            ),
            onPressed: () {
              // TODO: Navigate to cart screen
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(cartService.isEmpty
                    ? 'Cart is empty'
                    : 'Cart: ${cartService.itemCount} items'),
                ),
              );
            },
          ),
          // Order History Quick Access
          IconButton(
            icon: Stack(
              children: [
                const Icon(Icons.receipt_long),
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
                      '7',
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
      drawer: _buildProfileDrawer(context, localizations),
      body: _screens[_selectedIndex],

      // Bottom Navigation Bar
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.dashboard),
            label: localizations.translate('dashboard'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.category),
            label: localizations.translate('products'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.shopping_cart),
            label: localizations.translate('orders'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.account_circle),
            label: 'Account',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.settings),
            label: localizations.translate('settings'),
          ),
        ],
      ),
    );
  }

  // Profile Drawer Menu
  Widget _buildProfileDrawer(BuildContext context, TSHLocalizations loc) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          UserAccountsDrawerHeader(
            decoration: BoxDecoration(gradient: TSHTheme.primaryGradient),
            accountName: const Text('Baghdad Electronics Center'),
            accountEmail: const Text('Price Tier: Wholesale A'),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Icon(Icons.business, size: 40, color: TSHTheme.primary),
            ),
          ),
          _drawerItem(Icons.person, loc.translate('my_profile'), () {
            Navigator.pop(context);
            // Navigate to profile screen
          }),
          _drawerItem(Icons.business, loc.translate('business_info'), () {
            Navigator.pop(context);
            // Navigate to business info screen
          }),
          const Divider(),
          _drawerItem(Icons.receipt, loc.translate('invoices'), () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const InvoicesScreen()),
            );
          }),
          _drawerItem(Icons.payment, loc.translate('payments'), () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const PaymentsScreen()),
            );
          }),
          _drawerItem(Icons.note, loc.translate('credit_notes'), () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const CreditNotesScreen()),
            );
          }),
          _drawerItem(Icons.account_balance_wallet, loc.translate('account_statement'), () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const AccountStatementScreen()),
            );
          }),
          const Divider(),
          _drawerItem(Icons.support_agent, loc.translate('support_tickets'), () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const SupportTicketsScreen()),
            );
          }),
          const Divider(),
          _drawerItem(Icons.logout, loc.translate('logout'), () {
            Navigator.pop(context);
            // Show logout confirmation dialog
          }, color: Colors.red),
        ],
      ),
    );
  }

  // Helper method for drawer items
  ListTile _drawerItem(IconData icon, String title, VoidCallback onTap, {Color? color}) {
    return ListTile(
      leading: Icon(icon, color: color ?? TSHTheme.primary),
      title: Text(title, style: TextStyle(color: color)),
      onTap: onTap,
      trailing: const Icon(Icons.chevron_right, size: 16),
    );
  }
}

// ===============================================
// WHOLESALE DASHBOARD - Professional B2B Interface
// ===============================================
class WholesaleDashboardScreen extends StatefulWidget {
  const WholesaleDashboardScreen({super.key});

  @override
  State<WholesaleDashboardScreen> createState() => _WholesaleDashboardScreenState();
}

class _WholesaleDashboardScreenState extends State<WholesaleDashboardScreen> {
  Map<String, dynamic> _businessData = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadBusinessData();
  }

  Future<void> _loadBusinessData() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/wholesale/dashboard'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        setState(() {
          _businessData = json.decode(response.body);
          _isLoading = false;
        });
      } else {
        _loadFallbackData();
      }
    } catch (e) {
      _loadFallbackData();
    }
  }

  void _loadFallbackData() {
    setState(() {
      _businessData = {
        'account_balance': -15750000, // Outstanding balance: -15,750,000 IQD (negative = owes money)
        'monthly_purchases': 89320000, // 89,320,000 IQD this month
        'pending_orders': 4,
        'completed_orders': 27,
        'available_credit': 50000000, // 50,000,000 IQD credit limit
        'payment_terms': '30 days',
        'business_name': 'Baghdad Electronics Center',
        'account_manager': 'Ahmed Al-Iraqi',
        'recent_orders': [
          {'id': 'WO-2024-1156', 'amount': 12340000, 'status': 'Processing', 'date': '2 days ago'},
          {'id': 'WO-2024-1155', 'amount': 8570000, 'status': 'Shipped', 'date': '5 days ago'},
          {'id': 'WO-2024-1154', 'amount': 15890000, 'status': 'Delivered', 'date': '1 week ago'},
        ],
        'price_tier': 'Wholesale A', // Wholesale A, Wholesale B, Technical pricing
        'featured_products': [
          {'name': 'iPhone 15 Cases (Pack of 50)', 'price': 2500000, 'sku': 'IP15C-50'},
          {'name': 'Samsung Chargers (Pack of 25)', 'price': 1875000, 'sku': 'SGC-25'},
          {'name': 'Laptop Cooling Pads (Pack of 10)', 'price': 1200000, 'sku': 'LCP-10'},
        ],
      };
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;

    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading business dashboard...'),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadBusinessData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Business Account Overview
            _buildAccountOverview(localizations),
            const SizedBox(height: 24),
            
            // Quick Actions for B2B
            _buildB2BQuickActions(localizations),
            const SizedBox(height: 24),
            
            // Order Summary
            _buildOrderSummary(localizations),
            const SizedBox(height: 24),
            
            // Featured Wholesale Products
            _buildFeaturedProducts(localizations),
            const SizedBox(height: 24),
            
            // Recent Order History
            _buildRecentOrders(localizations),
          ],
        ),
      ),
    );
  }

  Widget _buildAccountOverview(TSHLocalizations localizations) {
    bool hasOutstandingBalance = (_businessData['account_balance'] ?? 0) < 0;
    double balance = (_businessData['account_balance'] ?? 0).toDouble().abs();
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.business,
                  size: 32,
                  color: TSHTheme.primaryTeal,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _businessData['business_name'] ?? 'Business Account',
                        style: TSHTheme.headingMedium,
                      ),
                      Text(
                        'Price Tier: ${_businessData['price_tier'] ?? 'Standard'}',
                        style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.primaryTeal),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: hasOutstandingBalance 
                          ? TSHTheme.errorRed.withOpacity(0.1)
                          : TSHTheme.successGreen.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: hasOutstandingBalance 
                            ? TSHTheme.errorRed.withOpacity(0.3)
                            : TSHTheme.successGreen.withOpacity(0.3),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          hasOutstandingBalance ? 'Outstanding Balance' : 'Account Balance',
                          style: TSHTheme.bodySmall,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          localizations.formatCurrency(balance),
                          style: TSHTheme.headingSmall.copyWith(
                            color: hasOutstandingBalance ? TSHTheme.errorRed : TSHTheme.successGreen,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: TSHTheme.primaryBlue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: TSHTheme.primaryBlue.withOpacity(0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Available Credit',
                          style: TSHTheme.bodySmall,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          localizations.formatCurrency(_businessData['available_credit']?.toDouble() ?? 0),
                          style: TSHTheme.headingSmall.copyWith(color: TSHTheme.primaryBlue),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Account Manager: ${_businessData['account_manager'] ?? 'N/A'}',
                  style: TSHTheme.bodySmall,
                ),
                Text(
                  'Payment Terms: ${_businessData['payment_terms'] ?? 'N/A'}',
                  style: TSHTheme.bodySmall,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildB2BQuickActions(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick B2B Actions',
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 4,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          children: [
            TSHTheme.quickActionButton(
              icon: Icons.shopping_cart,
              label: 'New Order',
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.refresh,
              label: 'Reorder',
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.receipt,
              label: 'Invoices',
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.account_balance,
              label: 'Pay Balance',
              onTap: () {},
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildOrderSummary(TSHLocalizations localizations) {
    return Row(
      children: [
        Expanded(
          child: TSHTheme.metricCard(
            title: 'This Month',
            value: localizations.formatCurrency(_businessData['monthly_purchases']?.toDouble() ?? 0),
            icon: Icons.shopping_bag,
            iconColor: TSHTheme.primaryTeal,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: TSHTheme.metricCard(
            title: 'Pending Orders',
            value: '${_businessData['pending_orders'] ?? 0}',
            icon: Icons.pending,
            iconColor: TSHTheme.warningYellow,
          ),
        ),
      ],
    );
  }

  Widget _buildFeaturedProducts(TSHLocalizations localizations) {
    final products = _businessData['featured_products'] as List<dynamic>? ?? [];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Featured Wholesale Products',
              style: TSHTheme.headingSmall,
            ),
            TextButton(
              onPressed: () {},
              child: Text('View Catalog'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 180,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: products.length,
            itemBuilder: (context, index) {
              final product = products[index];
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
                          height: 60,
                          decoration: BoxDecoration(
                            color: TSHTheme.primaryTeal.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Center(
                            child: Icon(Icons.inventory_2, size: 30, color: TSHTheme.primaryTeal),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          product['name'],
                          style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'SKU: ${product['sku']}',
                          style: TSHTheme.bodySmall,
                        ),
                        const Spacer(),
                        Text(
                          localizations.formatCurrency(product['price']?.toDouble() ?? 0),
                          style: TSHTheme.bodyMedium.copyWith(
                            color: TSHTheme.primaryTeal,
                            fontWeight: FontWeight.w600,
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
    );
  }

  Widget _buildRecentOrders(TSHLocalizations localizations) {
    final orders = _businessData['recent_orders'] as List<dynamic>? ?? [];
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Recent Orders',
                  style: TSHTheme.headingSmall,
                ),
                TextButton(
                  onPressed: () {},
                  child: Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: orders.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final order = orders[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _getOrderStatusColor(order['status']).withOpacity(0.2),
                    child: Icon(
                      _getOrderStatusIcon(order['status']),
                      color: _getOrderStatusColor(order['status']),
                    ),
                  ),
                  title: Text(order['id']),
                  subtitle: Text(order['date']),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        localizations.formatCurrency(order['amount']?.toDouble() ?? 0),
                        style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: _getOrderStatusColor(order['status']).withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          order['status'],
                          style: TSHTheme.bodySmall.copyWith(
                            color: _getOrderStatusColor(order['status']),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Color _getOrderStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'processing':
        return TSHTheme.warningYellow;
      case 'shipped':
        return TSHTheme.primaryBlue;
      case 'delivered':
        return TSHTheme.successGreen;
      case 'cancelled':
        return TSHTheme.errorRed;
      default:
        return TSHTheme.textLight;
    }
  }

  IconData _getOrderStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'processing':
        return Icons.hourglass_empty;
      case 'shipped':
        return Icons.local_shipping;
      case 'delivered':
        return Icons.check_circle;
      case 'cancelled':
        return Icons.cancel;
      default:
        return Icons.info;
    }
  }
}

// ===============================================
// PLACEHOLDER SCREENS FOR OTHER WHOLESALE SECTIONS
// ===============================================
class ProductCatalogScreen extends StatelessWidget {
  const ProductCatalogScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('B2B Product Catalog - Professional Grid View'));
  }
}

class OrderManagementScreen extends StatelessWidget {
  const OrderManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Order Management - Shopping Cart Style with Reorder'));
  }
}

class AccountManagementScreen extends StatelessWidget {
  const AccountManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Account Management - Business Dashboard'));
  }
}

class WholesaleSettingsScreen extends StatelessWidget {
  const WholesaleSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Wholesale Settings'));
  }
}
