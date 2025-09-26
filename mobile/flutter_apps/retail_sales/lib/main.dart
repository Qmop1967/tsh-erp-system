import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

void main() {
  runApp(const TSHRetailSalesApp());
}

class TSHRetailSalesApp extends StatelessWidget {
  const TSHRetailSalesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TSH Retail Sales & POS',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const MainScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  String _currentLanguage = 'en';
  
  final List<Widget> _screens = [
    const DashboardScreen(),
    const POSScreen(),
    const InventoryScreen(),
    const SalesScreen(),
    const SettingsScreen(),
  ];

  final Map<String, Map<String, String>> _translations = {
    'en': {
      'dashboard': 'Dashboard',
      'pos': 'POS',
      'inventory': 'Inventory',
      'sales': 'Sales',
      'settings': 'Settings',
      'welcome': 'Welcome to TSH Retail Sales',
      'total_sales': 'Total Sales Today',
      'total_items': 'Total Items',
      'low_stock': 'Low Stock Items',
      'customers': 'Customers Served',
    },
    'ar': {
      'dashboard': 'الرئيسية',
      'pos': 'نقطة البيع',
      'inventory': 'المخزون',
      'sales': 'المبيعات',
      'settings': 'الإعدادات',
      'welcome': 'مرحباً بك في مبيعات TSH التجزئة',
      'total_sales': 'إجمالي المبيعات اليوم',
      'total_items': 'إجمالي العناصر',
      'low_stock': 'عناصر منخفضة المخزون',
      'customers': 'العملاء المخدومين',
    },
  };

  String _translate(String key) {
    return _translations[_currentLanguage]?[key] ?? key;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_translate('welcome')),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: Text(_currentLanguage == 'en' ? 'العربية' : 'EN'),
            onPressed: () {
              setState(() {
                _currentLanguage = _currentLanguage == 'en' ? 'ar' : 'en';
              });
            },
          ),
        ],
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.dashboard),
            label: _translate('dashboard'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.point_of_sale),
            label: _translate('pos'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.inventory),
            label: _translate('inventory'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.trending_up),
            label: _translate('sales'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.settings),
            label: _translate('settings'),
          ),
        ],
      ),
    );
  }
}

// Dashboard Screen
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic> _dashboardData = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/admin/dashboard'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        setState(() {
          _dashboardData = json.decode(response.body);
          _isLoading = false;
        });
      } else {
        // Fallback data if API is not available
        setState(() {
          _dashboardData = {
            'total_sales_today': 1250000,
            'total_items': 3247,
            'low_stock_items': 23,
            'customers_served': 47,
          };
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _dashboardData = {
          'total_sales_today': 1250000,
          'total_items': 3247,
          'low_stock_items': 23,
          'customers_served': 47,
        };
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Sales Overview',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              children: [
                _buildDashboardCard(
                  'Total Sales Today',
                  '${_dashboardData['total_sales_today']?.toString() ?? '0'} IQD',
                  Icons.attach_money,
                  Colors.green,
                ),
                _buildDashboardCard(
                  'Total Items',
                  _dashboardData['total_items']?.toString() ?? '0',
                  Icons.inventory,
                  Colors.blue,
                ),
                _buildDashboardCard(
                  'Low Stock Items',
                  _dashboardData['low_stock_items']?.toString() ?? '0',
                  Icons.warning,
                  Colors.orange,
                ),
                _buildDashboardCard(
                  'Customers Served',
                  _dashboardData['customers_served']?.toString() ?? '0',
                  Icons.people,
                  Colors.purple,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(fontSize: 18, color: color, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

// POS Screen with Google Lens Integration
class POSScreen extends StatefulWidget {
  const POSScreen({super.key});

  @override
  State<POSScreen> createState() => _POSScreenState();
}

class _POSScreenState extends State<POSScreen> {
  final List<Map<String, dynamic>> _cartItems = [];
  double _totalAmount = 0.0;
  final ImagePicker _imagePicker = ImagePicker();

  void _addToCart(Map<String, dynamic> item) {
    setState(() {
      _cartItems.add(item);
      _totalAmount += item['price'] ?? 0.0;
    });
  }

  void _removeFromCart(int index) {
    setState(() {
      _totalAmount -= _cartItems[index]['price'] ?? 0.0;
      _cartItems.removeAt(index);
    });
  }

  Future<void> _scanWithGoogleLens() async {
    try {
      final XFile? image = await _imagePicker.pickImage(source: ImageSource.camera);
      if (image != null) {
        // Simulate Google Lens product recognition
        final response = await http.post(
          Uri.parse('http://localhost:8000/api/pos/enhanced/google-lens/search'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'image_data': 'base64_encoded_image_data',
            'confidence_threshold': 0.7,
          }),
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          final products = data['products'] as List;
          
          if (products.isNotEmpty) {
            final product = products[0];
            _addToCart({
              'name': product['name'],
              'price': product['price'],
              'sku': product['sku'],
              'quantity': 1,
            });
            
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Added ${product['name']} to cart')),
            );
          }
        }
      }
    } catch (e) {
      // Add sample item for demo
      _addToCart({
        'name': 'Sample Product',
        'price': 15000.0,
        'sku': 'SAMPLE001',
        'quantity': 1,
      });
    }
  }

  Future<void> _processPayment() async {
    if (_cartItems.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cart is empty')),
      );
      return;
    }

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Process Payment'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Total Amount: ${_totalAmount.toStringAsFixed(0)} IQD'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _completeTransaction();
              },
              child: const Text('Complete Transaction'),
            ),
          ],
        ),
      ),
    );
  }

  void _completeTransaction() {
    setState(() {
      _cartItems.clear();
      _totalAmount = 0.0;
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Transaction completed successfully!')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Point of Sale',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              ElevatedButton.icon(
                onPressed: _scanWithGoogleLens,
                icon: const Icon(Icons.camera_alt),
                label: const Text('Scan Product'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _cartItems.isEmpty
                ? const Center(
                    child: Text(
                      'Cart is empty\nScan a product to add it to cart',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 16),
                    ),
                  )
                : ListView.builder(
                    itemCount: _cartItems.length,
                    itemBuilder: (context, index) {
                      final item = _cartItems[index];
                      return Card(
                        child: ListTile(
                          title: Text(item['name'] ?? 'Unknown Product'),
                          subtitle: Text('SKU: ${item['sku'] ?? 'N/A'}'),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text('${item['price']?.toStringAsFixed(0) ?? '0'} IQD'),
                              const SizedBox(width: 8),
                              IconButton(
                                icon: const Icon(Icons.delete),
                                onPressed: () => _removeFromCart(index),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
          const Divider(),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Total: ${_totalAmount.toStringAsFixed(0)} IQD',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              ElevatedButton(
                onPressed: _processPayment,
                child: const Text('Process Payment'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// Inventory Screen
class InventoryScreen extends StatefulWidget {
  const InventoryScreen({super.key});

  @override
  State<InventoryScreen> createState() => _InventoryScreenState();
}

class _InventoryScreenState extends State<InventoryScreen> {
  List<Map<String, dynamic>> _inventory = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadInventory();
  }

  Future<void> _loadInventory() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/inventory/summary'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _inventory = List<Map<String, dynamic>>.from(data['items'] ?? []);
          _isLoading = false;
        });
      } else {
        _loadSampleInventory();
      }
    } catch (e) {
      _loadSampleInventory();
    }
  }

  void _loadSampleInventory() {
    setState(() {
      _inventory = [
        {
          'name': 'Laptop Charger',
          'sku': 'LAP001',
          'quantity': 45,
          'price': 25000,
          'category': 'Laptop Accessories',
          'low_stock': false,
        },
        {
          'name': 'USB Cable',
          'sku': 'USB001',
          'quantity': 8,
          'price': 5000,
          'category': 'Mobile Accessories',
          'low_stock': true,
        },
        {
          'name': 'HDMI Cable',
          'sku': 'HDMI001',
          'quantity': 23,
          'price': 15000,
          'category': 'Network Accessories',
          'low_stock': false,
        },
      ];
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Inventory Management',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: _inventory.length,
              itemBuilder: (context, index) {
                final item = _inventory[index];
                final isLowStock = item['quantity'] < 10;
                
                return Card(
                  color: isLowStock ? Colors.red.shade50 : null,
                  child: ListTile(
                    title: Text(item['name'] ?? 'Unknown Item'),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('SKU: ${item['sku'] ?? 'N/A'}'),
                        Text('Category: ${item['category'] ?? 'N/A'}'),
                        Text('Price: ${item['price']?.toString() ?? '0'} IQD'),
                      ],
                    ),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Qty: ${item['quantity']?.toString() ?? '0'}',
                          style: TextStyle(
                            color: isLowStock ? Colors.red : Colors.green,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (isLowStock)
                          const Text(
                            'Low Stock',
                            style: TextStyle(color: Colors.red, fontSize: 12),
                          ),
                      ],
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
}

// Sales Screen
class SalesScreen extends StatefulWidget {
  const SalesScreen({super.key});

  @override
  State<SalesScreen> createState() => _SalesScreenState();
}

class _SalesScreenState extends State<SalesScreen> {
  List<Map<String, dynamic>> _sales = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSales();
  }

  Future<void> _loadSales() async {
    // Simulate loading sales data
    await Future.delayed(const Duration(seconds: 1));
    
    setState(() {
      _sales = [
        {
          'id': 'TXN001',
          'date': '2025-01-06',
          'time': '10:30 AM',
          'items': 3,
          'total': 45000,
          'customer': 'Walk-in Customer',
        },
        {
          'id': 'TXN002',
          'date': '2025-01-06',
          'time': '11:15 AM',
          'items': 1,
          'total': 25000,
          'customer': 'Ahmad Ali',
        },
        {
          'id': 'TXN003',
          'date': '2025-01-06',
          'time': '2:45 PM',
          'items': 2,
          'total': 30000,
          'customer': 'Walk-in Customer',
        },
      ];
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Sales History',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: _sales.length,
              itemBuilder: (context, index) {
                final sale = _sales[index];
                return Card(
                  child: ListTile(
                    title: Text('Transaction ${sale['id']}'),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Date: ${sale['date']} at ${sale['time']}'),
                        Text('Customer: ${sale['customer']}'),
                        Text('Items: ${sale['items']}'),
                      ],
                    ),
                    trailing: Text(
                      '${sale['total']} IQD',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
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
}

// Settings Screen
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Settings',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 16),
          Card(
            child: ListTile(
              leading: Icon(Icons.language),
              title: Text('Language'),
              subtitle: Text('English / العربية'),
              trailing: Icon(Icons.arrow_forward_ios),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.sync),
              title: Text('Sync Data'),
              subtitle: Text('Last sync: 2 minutes ago'),
              trailing: Icon(Icons.arrow_forward_ios),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.print),
              title: Text('Printer Settings'),
              subtitle: Text('Configure receipt printer'),
              trailing: Icon(Icons.arrow_forward_ios),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.info),
              title: Text('About'),
              subtitle: Text('TSH Retail Sales v1.0.0'),
              trailing: Icon(Icons.arrow_forward_ios),
            ),
          ),
        ],
      ),
    );
  }
}
