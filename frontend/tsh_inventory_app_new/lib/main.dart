import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

// Import screens
import 'screens/items_management_screen_simple.dart';
import 'screens/enhanced_dashboard_screen.dart';
import 'screens/sales_orders_packing_screen.dart';
import 'screens/enhanced_shipments_screen.dart';
import 'screens/enhanced_purchase_orders_screen.dart';
import 'screens/comprehensive_reports_screen.dart';
import 'screens/placeholder_screens.dart';

// Simple language service for demo
class SimpleLanguageService extends ChangeNotifier {
  bool get isDarkMode => false;
  Locale get currentLocale => const Locale('en');
  bool get isRTL => false;
}

void main() {
  runApp(const TSHInventoryApp());
}

class TSHInventoryApp extends StatelessWidget {
  const TSHInventoryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => SimpleLanguageService(),
      child: MaterialApp(
        title: 'TSH Inventory Management',
        theme: ThemeData(
          primarySwatch: Colors.teal,
          visualDensity: VisualDensity.adaptivePlatformDensity,
          appBarTheme: const AppBarTheme(
            backgroundColor: Colors.teal,
            foregroundColor: Colors.white,
            elevation: 2,
          ),
        ),
        home: const InventoryMainScreen(),
        debugShowCheckedModeBanner: false,
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
    const EnhancedInventoryDashboardScreen(),
    const SalesOrdersPackingScreen(),
    const EnhancedShipmentsScreen(),
    const EnhancedPurchaseOrdersScreen(),
    const ItemsManagementScreen(),
    const ComprehensiveReportsScreen(),
    const InventorySettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.inventory, size: 35),
            SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Inventory Management', overflow: TextOverflow.ellipsis),
                  Text(
                    'Multi-Location Warehouse System',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          // Quick Scan Button
          Container(
            margin: const EdgeInsets.only(right: 8),
            child: ElevatedButton.icon(
              onPressed: () => _quickScan(context),
              icon: const Icon(Icons.qr_code_scanner, size: 18),
              label: const Text('Quick Scan'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                foregroundColor: Colors.white,
                elevation: 2,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              ),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      drawer: _buildDrawer(context),
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        selectedItemColor: Colors.teal,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.inventory_2),
            label: 'Sales Orders',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.local_shipping),
            label: 'Shipments',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: 'Purchase Orders',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.category),
            label: 'Items',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Reports',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      backgroundColor: Colors.teal[900],
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          const DrawerHeader(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Colors.teal, Color(0xFF00695C)],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.white,
                  child: Icon(Icons.inventory, size: 35, color: Colors.teal),
                ),
                SizedBox(height: 10),
                Text(
                  'TSH Inventory',
                  style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Management System',
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                ),
              ],
            ),
          ),
          _buildDrawerItem(Icons.dashboard, 'Dashboard', 0),
          _buildDrawerItem(Icons.inventory_2, 'Sales Orders to Pack', 1),
          _buildDrawerItem(Icons.local_shipping, 'Shipments', 2),
          _buildDrawerItem(Icons.shopping_cart, 'Purchase Orders', 3),
          _buildDrawerItem(Icons.category, 'Items Management', 4),
          _buildDrawerItem(Icons.analytics, 'Reports & Analytics', 5),
          _buildDrawerItem(Icons.settings, 'Settings', 6),
          const Divider(color: Colors.white30),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.white),
            title: const Text('Logout', style: TextStyle(color: Colors.white)),
            onTap: () {
              // TODO: Implement logout
              Navigator.pop(context);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(IconData icon, String title, int index) {
    return ListTile(
      leading: Icon(icon, color: _selectedIndex == index ? Colors.teal : Colors.white),
      title: Text(title, style: TextStyle(color: _selectedIndex == index ? Colors.teal : Colors.white)),
      onTap: () {
        setState(() => _selectedIndex = index);
        Navigator.pop(context);
      },
    );
  }

  void _quickScan(BuildContext context) {
    setState(() => _selectedIndex = 4); // Navigate to items management for scanning
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Quick Scan activated - Navigating to Items Management')),
    );
  }
}
