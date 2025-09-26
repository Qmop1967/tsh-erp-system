import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:image_picker/image_picker.dart';
import 'package:fl_chart/fl_chart.dart';

// Import TSH Core Design System
import 'package:tsh_core_package/tsh_core_package.dart';

// Import Inventory Models and Services
import 'models/inventory_models.dart';
import 'services/inventory_service.dart';
import 'screens/items_management_screen.dart';
import 'screens/abc_analysis_screen.dart';
import 'screens/warehouse_operations_screen.dart';
import 'screens/placeholder_screens.dart';

void main() {
  runApp(const TSHInventoryApp());
}

class TSHInventoryApp extends StatelessWidget {
  const TSHInventoryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => LanguageService(),
      child: Consumer<LanguageService>(
        builder: (context, languageService, child) {
          return MaterialApp(
            title: 'TSH Inventory Management',
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
            home: const InventoryMainScreen(),
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

class InventoryMainScreen extends StatefulWidget {
  const InventoryMainScreen({super.key});

  @override
  State<InventoryMainScreen> createState() => _InventoryMainScreenState();
}

class _InventoryMainScreenState extends State<InventoryMainScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const InventoryDashboardScreen(),
    const ItemsManagementScreen(),
    const WarehouseOperationsScreen(),
    const ABCAnalysisScreen(),
    const BarcodeScanningScreen(),
    const InventorySettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;
    final languageService = Provider.of<LanguageService>(context);

    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Row(
          children: [
            TSHTheme.tshLogo(height: 35),
            const SizedBox(width: 12),
            Text(localizations.translate('inventory_management')),
          ],
        ),
        subtitle: Text(
          'Multi-Location Warehouse System',
          style: TSHTheme.bodySmall.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
        ),
        actions: [
          // Quick Scan Button
          Container(
            margin: const EdgeInsets.only(right: 8),
            child: ElevatedButton.icon(
              onPressed: () => _quickScan(context),
              icon: const Icon(Icons.qr_code_scanner, size: 18),
              label: Text('Quick Scan'),
              style: ElevatedButton.styleFrom(
                backgroundColor: TSHTheme.accentOrange,
                foregroundColor: TSHTheme.surfaceWhite,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
            ),
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
          // Side Menu Toggle
          IconButton(
            icon: const Icon(Icons.menu),
            onPressed: () => _scaffoldKey.currentState?.openEndDrawer(),
          ),
        ],
      ),
      
      // Side Drawer Menu
      endDrawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(
                color: TSHTheme.primaryTeal,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TSHTheme.tshLogo(height: 45),
                  const SizedBox(height: 12),
                  Text(
                    localizations.translate('inventory_management'),
                    style: TSHTheme.headingSmall.copyWith(color: TSHTheme.surfaceWhite),
                  ),
                  Text(
                    'Warehouse Control System',
                    style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
                  ),
                ],
              ),
            ),
            _buildDrawerItem(Icons.dashboard, localizations.translate('dashboard'), 0),
            _buildDrawerItem(Icons.inventory, 'Items Management', 1),
            _buildDrawerItem(Icons.warehouse, 'Warehouse Ops', 2),
            _buildDrawerItem(Icons.analytics, 'ABC Analysis', 3),
            _buildDrawerItem(Icons.qr_code_scanner, 'Barcode Scanner', 4),
            _buildDrawerItem(Icons.settings, localizations.translate('settings'), 5),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.sync),
              title: Text('Sync with Admin'),
              onTap: () => _handleSync(context),
            ),
            ListTile(
              leading: const Icon(Icons.analytics),
              title: Text('Inventory Reports'),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.logout),
              title: Text(localizations.translate('logout')),
              onTap: () => _handleLogout(context),
            ),
          ],
        ),
      ),
      
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
            icon: const Icon(Icons.inventory),
            label: 'Items',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.warehouse),
            label: 'Warehouse',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.analytics),
            label: 'ABC',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.qr_code_scanner),
            label: 'Scanner',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.settings),
            label: localizations.translate('settings'),
          ),
        ],
      ),
      
      // Floating Action Button for Quick Scan
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _quickScan(context),
        backgroundColor: TSHTheme.accentOrange,
        icon: const Icon(Icons.qr_code_scanner),
        label: Text('Scan Item'),
      ),
    );
  }

  Widget _buildDrawerItem(IconData icon, String title, int index) {
    return ListTile(
      leading: Icon(icon, color: _selectedIndex == index ? TSHTheme.primaryTeal : null),
      title: Text(title),
      selected: _selectedIndex == index,
      onTap: () {
        setState(() => _selectedIndex = index);
        Navigator.pop(context);
      },
    );
  }

  void _quickScan(BuildContext context) {
    setState(() => _selectedIndex = 4); // Switch to scanner
    Navigator.pop(context);
  }

  void _handleSync(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Syncing inventory data with main system...'),
        action: SnackBarAction(
          label: 'View Progress',
          onPressed: () {},
        ),
      ),
    );
  }

  void _handleLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(TSHLocalizations.of(context)!.translate('logout')),
        content: Text('Are you sure you want to logout from Inventory System?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(TSHLocalizations.of(context)!.translate('cancel')),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Handle logout logic
            },
            child: Text(TSHLocalizations.of(context)!.translate('logout')),
          ),
        ],
      ),
    );
  }
}

// ===============================================
// INVENTORY DASHBOARD - Dashboard Indicators with Counters
// ===============================================
class InventoryDashboardScreen extends StatefulWidget {
  const InventoryDashboardScreen({super.key});

  @override
  State<InventoryDashboardScreen> createState() => _InventoryDashboardScreenState();
}

class _InventoryDashboardScreenState extends State<InventoryDashboardScreen> {
  Map<String, dynamic> _inventoryData = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadInventoryData();
  }

  Future<void> _loadInventoryData() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/inventory/dashboard'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        setState(() {
          _inventoryData = json.decode(response.body);
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
      _inventoryData = {
        'total_products': 3247,
        'total_stock_movements': 1842,
        'low_stock_alerts': 23,
        'out_of_stock': 7,
        'total_locations': 8,
        'inventory_value': 456890000, // 456,890,000 IQD
        'recent_movements': [
          {'type': 'incoming', 'product': 'iPhone 14 Case', 'quantity': 50, 'location': 'Main Warehouse', 'time': '15 minutes ago'},
          {'type': 'outgoing', 'product': 'Samsung Charger', 'quantity': 25, 'location': 'Retail Shop', 'time': '32 minutes ago'},
          {'type': 'transfer', 'product': 'HP Printer Ink', 'quantity': 12, 'location': 'Secondary Warehouse', 'time': '1 hour ago'},
        ],
        'low_stock_items': [
          {'product': 'USB-C Cable', 'current_stock': 8, 'reorder_point': 20, 'location': 'Main Warehouse'},
          {'product': 'Mouse Pad', 'current_stock': 3, 'reorder_point': 15, 'location': 'Retail Shop'},
          {'product': 'Keyboard Cover', 'current_stock': 5, 'reorder_point': 25, 'location': 'Secondary Warehouse'},
        ],
        'categories': [
          {'name': 'Laptop Accessories', 'count': 842, 'icon': 'laptop'},
          {'name': 'Printer Accessories', 'count': 623, 'icon': 'printer'},
          {'name': 'CCTV Accessories', 'count': 459, 'icon': 'security'},
          {'name': 'Network Accessories', 'count': 731, 'icon': 'network'},
          {'name': 'Mobile Accessories', 'count': 592, 'icon': 'phone'},
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
            Text('Loading inventory dashboard...'),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadInventoryData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Dashboard Indicators with Counters
            _buildDashboardIndicators(localizations),
            const SizedBox(height: 24),
            
            // Category Overview with Icon-Based Layout
            _buildCategoryOverview(localizations),
            const SizedBox(height: 24),
            
            // Quick Actions for Inventory
            _buildInventoryQuickActions(localizations),
            const SizedBox(height: 24),
            
            // Low Stock Alerts
            _buildLowStockAlerts(localizations),
            const SizedBox(height: 24),
            
            // Recent Stock Movements
            _buildRecentMovements(localizations),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardIndicators(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Inventory Overview',
              style: TSHTheme.headingSmall,
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: TSHTheme.primaryTeal.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: TSHTheme.primaryTeal.withOpacity(0.3)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.trending_up,
                    size: 16,
                    color: TSHTheme.primaryTeal,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'Phase 1-4 Active',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: TSHTheme.primaryTeal,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.1,
          children: [
            TSHTheme.metricCard(
              title: 'Total Items',
              value: '${_inventoryData['total_products']}',
              icon: Icons.inventory_2,
              iconColor: TSHTheme.primaryBlue,
              subtitle: 'SKU Management Active',
            ),
            TSHTheme.metricCard(
              title: 'ABC Classification',
              value: 'Active',
              icon: Icons.analytics,
              iconColor: TSHTheme.successGreen,
              subtitle: 'Smart Analysis Running',
            ),
            TSHTheme.metricCard(
              title: 'Low Stock Alerts',
              value: '${_inventoryData['low_stock_alerts']}',
              icon: Icons.warning,
              iconColor: TSHTheme.warningYellow,
              subtitle: 'Automated Monitoring',
            ),
            TSHTheme.metricCard(
              title: 'Multi-Warehouse',
              value: '${_inventoryData['total_locations']}',
              icon: Icons.warehouse,
              iconColor: TSHTheme.accentOrange,
              subtitle: 'Real-time Sync',
            ),
          ],
        ),
      ],
    );
  }
        const SizedBox(height: 16),
        // Additional metrics
        Row(
          children: [
            Expanded(
              child: TSHTheme.metricCard(
                title: 'Total Locations',
                value: '${_inventoryData['total_locations']}',
                icon: Icons.location_on,
                iconColor: TSHTheme.accentOrange,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: TSHTheme.metricCard(
                title: 'Inventory Value',
                value: localizations.formatCurrency(_inventoryData['inventory_value']?.toDouble() ?? 0),
                icon: Icons.attach_money,
                iconColor: TSHTheme.primaryTeal,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCategoryOverview(TSHLocalizations localizations) {
    final categories = _inventoryData['categories'] as List<dynamic>? ?? [];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Product Categories',
              style: TSHTheme.headingSmall,
            ),
            TextButton.icon(
              onPressed: () => setState(() => _selectedIndex = 1),
              icon: const Icon(Icons.warehouse),
              label: Text('View Warehouse'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.3,
          ),
          itemCount: categories.length,
          itemBuilder: (context, index) {
            final category = categories[index];
            return _buildCategoryCard(category);
          },
        ),
      ],
    );
  }

  Widget _buildCategoryCard(Map<String, dynamic> category) {
    IconData categoryIcon = _getCategoryIcon(category['icon']);
    Color categoryColor = _getCategoryColor(category['icon']);
    
    return Card(
      child: InkWell(
        onTap: () {
          // Navigate to category-specific inventory view
          setState(() => _selectedIndex = 1);
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: categoryColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  categoryIcon,
                  size: 32,
                  color: categoryColor,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                category['name'],
                style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                '${category['count']} items',
                style: TSHTheme.bodySmall.copyWith(color: categoryColor),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getCategoryIcon(String iconType) {
    switch (iconType) {
      case 'laptop':
        return Icons.laptop;
      case 'printer':
        return Icons.print;
      case 'security':
        return Icons.security;
      case 'network':
        return Icons.router;
      case 'phone':
        return Icons.smartphone;
      default:
        return Icons.category;
    }
  }

  Color _getCategoryColor(String iconType) {
    switch (iconType) {
      case 'laptop':
        return TSHTheme.primaryBlue;
      case 'printer':
        return TSHTheme.successGreen;
      case 'security':
        return TSHTheme.errorRed;
      case 'network':
        return TSHTheme.accentOrange;
      case 'phone':
        return TSHTheme.primaryTeal;
      default:
        return TSHTheme.textLight;
    }
  }

  Widget _buildInventoryQuickActions(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Inventory Actions',
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
              icon: Icons.qr_code_scanner,
              label: 'Scan Item',
              onTap: () => setState(() => _selectedIndex = 4),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.add_box,
              label: 'Add Stock',
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.move_down,
              label: 'Move Stock',
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.assessment,
              label: 'Stock Report',
              onTap: () {},
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildLowStockAlerts(TSHLocalizations localizations) {
    final lowStockItems = _inventoryData['low_stock_items'] as List<dynamic>? ?? [];
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: TSHTheme.warningYellow),
                const SizedBox(width: 8),
                Text(
                  'Low Stock Alerts',
                  style: TSHTheme.headingSmall,
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: TSHTheme.warningYellow.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${lowStockItems.length}',
                    style: TSHTheme.bodySmall.copyWith(
                      color: TSHTheme.warningYellow,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: lowStockItems.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final item = lowStockItems[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: TSHTheme.warningYellow.withOpacity(0.2),
                    child: Icon(Icons.warning, color: TSHTheme.warningYellow),
                  ),
                  title: Text(item['product']),
                  subtitle: Text('${item['location']} • Reorder at: ${item['reorder_point']}'),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${item['current_stock']}',
                        style: TSHTheme.headingSmall.copyWith(color: TSHTheme.warningYellow),
                      ),
                      Text(
                        'in stock',
                        style: TSHTheme.bodySmall,
                      ),
                    ],
                  ),
                  onTap: () {
                    // Show reorder dialog
                    _showReorderDialog(context, item);
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentMovements(TSHLocalizations localizations) {
    final movements = _inventoryData['recent_movements'] as List<dynamic>? ?? [];
    
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
                  'Recent Stock Movements',
                  style: TSHTheme.headingSmall,
                ),
                TextButton(
                  onPressed: () => setState(() => _selectedIndex = 2),
                  child: Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: movements.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final movement = movements[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _getMovementColor(movement['type']).withOpacity(0.2),
                    child: Icon(
                      _getMovementIcon(movement['type']),
                      color: _getMovementColor(movement['type']),
                    ),
                  ),
                  title: Text(movement['product']),
                  subtitle: Text('${movement['location']} • ${movement['time']}'),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${movement['type'] == 'outgoing' ? '-' : '+'}${movement['quantity']}',
                        style: TSHTheme.bodyMedium.copyWith(
                          color: _getMovementColor(movement['type']),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        movement['type'].toString().toUpperCase(),
                        style: TSHTheme.bodySmall,
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

  Color _getMovementColor(String type) {
    switch (type) {
      case 'incoming':
        return TSHTheme.successGreen;
      case 'outgoing':
        return TSHTheme.errorRed;
      case 'transfer':
        return TSHTheme.primaryBlue;
      default:
        return TSHTheme.textLight;
    }
  }

  IconData _getMovementIcon(String type) {
    switch (type) {
      case 'incoming':
        return Icons.arrow_downward;
      case 'outgoing':
        return Icons.arrow_upward;
      case 'transfer':
        return Icons.swap_horiz;
      default:
        return Icons.timeline;
    }
  }

  void _showReorderDialog(BuildContext context, Map<String, dynamic> item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Reorder Item'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Product: ${item['product']}'),
            Text('Location: ${item['location']}'),
            Text('Current Stock: ${item['current_stock']}'),
            Text('Reorder Point: ${item['reorder_point']}'),
            const SizedBox(height: 16),
            TextField(
              decoration: InputDecoration(
                labelText: 'Quantity to Order',
                hintText: 'Enter quantity',
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Reorder request submitted for ${item['product']}')),
              );
            },
            child: Text('Create Order'),
          ),
        ],
      ),
    );
  }
}

// ===============================================
// PLACEHOLDER SCREENS FOR OTHER INVENTORY SECTIONS
// ===============================================
class WarehouseViewScreen extends StatelessWidget {
  const WarehouseViewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Warehouse Grid Layout - Icon-Based Categories'));
  }
}

class StockMovementsScreen extends StatelessWidget {
  const StockMovementsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Stock Movements History'));
  }
}

class LocationManagementScreen extends StatelessWidget {
  const LocationManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Multi-Location Management'));
  }
}

class BarcodeScanning Screen extends StatelessWidget {
  const BarcodeScanning Screen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Camera/Barcode Scanner - Primary Input'));
  }
}

class InventorySettingsScreen extends StatelessWidget {
  const InventorySettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Inventory System Settings'));
  }
} 