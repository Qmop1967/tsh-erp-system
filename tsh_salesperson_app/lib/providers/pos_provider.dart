import 'package:flutter/material.dart';
import '../models/pos_product.dart';
import '../models/pos_customer.dart';
import '../models/cart_item.dart';

class POSProvider with ChangeNotifier {
  // Demo Products - Electronics Catalog
  final List<POSProduct> _products = [
    // Smartphones
    POSProduct(
      id: '1',
      name: 'iPhone 15 Pro Max',
      nameAr: 'ايفون 15 برو ماكس',
      category: 'Smartphones',
      price: 1350000,
      stock: 15,
      sku: 'IP15PM-256',
      description: '256GB, Titanium Blue',
    ),
    POSProduct(
      id: '2',
      name: 'Samsung Galaxy S24 Ultra',
      nameAr: 'سامسونج جالاكسي S24 الترا',
      category: 'Smartphones',
      price: 1200000,
      stock: 20,
      sku: 'SGS24U-512',
      description: '512GB, Titanium Gray',
    ),
    POSProduct(
      id: '3',
      name: 'iPhone 14 Pro',
      nameAr: 'ايفون 14 برو',
      category: 'Smartphones',
      price: 950000,
      stock: 25,
      sku: 'IP14P-128',
      description: '128GB, Space Black',
    ),
    POSProduct(
      id: '4',
      name: 'Samsung Galaxy A54',
      nameAr: 'سامسونج جالاكسي A54',
      category: 'Smartphones',
      price: 450000,
      stock: 40,
      sku: 'SGA54-128',
      description: '128GB, Awesome Lime',
    ),
    POSProduct(
      id: '5',
      name: 'Xiaomi 13 Pro',
      nameAr: 'شاومي 13 برو',
      category: 'Smartphones',
      price: 650000,
      stock: 30,
      sku: 'XM13P-256',
      description: '256GB, Ceramic White',
    ),
    
    // Laptops
    POSProduct(
      id: '6',
      name: 'MacBook Pro 16"',
      nameAr: 'ماك بوك برو 16 انش',
      category: 'Laptops',
      price: 3500000,
      stock: 8,
      sku: 'MBP16-M3',
      description: 'M3 Pro, 32GB RAM, 1TB SSD',
    ),
    POSProduct(
      id: '7',
      name: 'Dell XPS 15',
      nameAr: 'ديل XPS 15',
      category: 'Laptops',
      price: 2200000,
      stock: 12,
      sku: 'DXPS15-I9',
      description: 'Intel i9, 32GB RAM, 1TB SSD',
    ),
    POSProduct(
      id: '8',
      name: 'HP Pavilion 15',
      nameAr: 'اتش بي بافيليون 15',
      category: 'Laptops',
      price: 950000,
      stock: 18,
      sku: 'HPP15-I7',
      description: 'Intel i7, 16GB RAM, 512GB SSD',
    ),
    POSProduct(
      id: '9',
      name: 'Lenovo ThinkPad X1',
      nameAr: 'لينوفو ثينك باد X1',
      category: 'Laptops',
      price: 1800000,
      stock: 10,
      sku: 'LTX1-I7',
      description: 'Intel i7, 16GB RAM, 512GB SSD',
    ),
    
    // Tablets
    POSProduct(
      id: '10',
      name: 'iPad Pro 12.9"',
      nameAr: 'ايباد برو 12.9 انش',
      category: 'Tablets',
      price: 1500000,
      stock: 15,
      sku: 'IPP12-M2',
      description: 'M2, 256GB, Space Gray',
    ),
    POSProduct(
      id: '11',
      name: 'Samsung Galaxy Tab S9',
      nameAr: 'سامسونج جالاكسي تاب S9',
      category: 'Tablets',
      price: 850000,
      stock: 20,
      sku: 'SGTS9-256',
      description: '256GB, Graphite',
    ),
    POSProduct(
      id: '12',
      name: 'iPad Air',
      nameAr: 'ايباد اير',
      category: 'Tablets',
      price: 750000,
      stock: 25,
      sku: 'IPA-64',
      description: '64GB, Blue',
    ),
    
    // Accessories
    POSProduct(
      id: '13',
      name: 'AirPods Pro 2',
      nameAr: 'ايربودز برو 2',
      category: 'Accessories',
      price: 350000,
      stock: 50,
      sku: 'APP2-USB',
      description: 'USB-C, Active Noise Cancellation',
    ),
    POSProduct(
      id: '14',
      name: 'Samsung Buds2 Pro',
      nameAr: 'سامسونج بودز 2 برو',
      category: 'Accessories',
      price: 250000,
      stock: 40,
      sku: 'SGB2P-BLK',
      description: 'Graphite, ANC',
    ),
    POSProduct(
      id: '15',
      name: 'Apple Watch Series 9',
      nameAr: 'ابل ووتش سيريز 9',
      category: 'Accessories',
      price: 550000,
      stock: 30,
      sku: 'AWS9-45',
      description: '45mm, GPS + Cellular',
    ),
    POSProduct(
      id: '16',
      name: 'Samsung Galaxy Watch 6',
      nameAr: 'سامسونج جالاكسي ووتش 6',
      category: 'Accessories',
      price: 400000,
      stock: 35,
      sku: 'SGW6-44',
      description: '44mm, Graphite',
    ),
    POSProduct(
      id: '17',
      name: 'Magic Keyboard',
      nameAr: 'لوحة مفاتيح ماجيك',
      category: 'Accessories',
      price: 180000,
      stock: 45,
      sku: 'MK-BLK',
      description: 'Black, Arabic/English',
    ),
    POSProduct(
      id: '18',
      name: 'Logitech MX Master 3S',
      nameAr: 'لوجيتك MX ماستر 3S',
      category: 'Accessories',
      price: 120000,
      stock: 50,
      sku: 'LMX3S-GRY',
      description: 'Wireless Mouse, Graphite',
    ),
  ];

  // Demo Customers
  final List<POSCustomer> _customers = [
    POSCustomer(
      id: '1',
      name: 'أحمد محمد علي',
      phone: '+964 770 123 4567',
      email: 'ahmed@example.com',
      address: 'بغداد - الكرادة',
      balance: 0,
    ),
    POSCustomer(
      id: '2',
      name: 'فاطمة حسن',
      phone: '+964 771 234 5678',
      email: 'fatima@example.com',
      address: 'بغداد - المنصور',
      balance: 0,
    ),
    POSCustomer(
      id: '3',
      name: 'علي حسين',
      phone: '+964 772 345 6789',
      email: 'ali@example.com',
      address: 'بصرة - العشار',
      balance: 0,
    ),
    POSCustomer(
      id: '4',
      name: 'سارة جمال',
      phone: '+964 773 456 7890',
      email: 'sara@example.com',
      address: 'أربيل - سامي عبد الرحمن',
      balance: 0,
    ),
    POSCustomer(
      id: '5',
      name: 'محمد عبدالله',
      phone: '+964 774 567 8901',
      email: 'mohammed@example.com',
      address: 'النجف - المدينة القديمة',
      balance: 0,
    ),
  ];

  // Demo Orders
  final List<POSOrder> _orders = [];

  // Cart
  final List<CartItem> _cart = [];
  POSCustomer? _selectedCustomer;
  String _searchQuery = '';
  String _selectedCategory = 'All';

  // Getters
  List<POSProduct> get products => _searchQuery.isEmpty && _selectedCategory == 'All'
      ? _products
      : _products.where((product) {
          final matchesSearch = _searchQuery.isEmpty ||
              product.nameAr.toLowerCase().contains(_searchQuery.toLowerCase()) ||
              product.name.toLowerCase().contains(_searchQuery.toLowerCase());
          final matchesCategory = _selectedCategory == 'All' || product.category == _selectedCategory;
          return matchesSearch && matchesCategory;
        }).toList();

  List<String> get categories => ['All', ...{..._products.map((p) => p.category)}];
  
  List<POSCustomer> get customers => _customers;
  List<POSOrder> get orders => _orders;
  List<CartItem> get cart => _cart;
  POSCustomer? get selectedCustomer => _selectedCustomer;
  String get searchQuery => _searchQuery;
  String get selectedCategory => _selectedCategory;

  double get cartSubtotal => _cart.fold(0, (sum, item) => sum + item.total);
  double get cartTax => cartSubtotal * 0.0; // No tax for now
  double get cartTotal => cartSubtotal + cartTax;
  int get cartItemCount => _cart.fold(0, (sum, item) => sum + item.quantity);

  // Methods
  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  void setSelectedCategory(String category) {
    _selectedCategory = category;
    notifyListeners();
  }

  void selectCustomer(POSCustomer? customer) {
    _selectedCustomer = customer;
    notifyListeners();
  }

  void addToCart(POSProduct product) {
    final existingIndex = _cart.indexWhere((item) => item.productId == product.id);
    
    if (existingIndex >= 0) {
      _cart[existingIndex] = _cart[existingIndex].copyWith(
        quantity: _cart[existingIndex].quantity + 1,
      );
    } else {
      _cart.add(CartItem(
        productId: product.id,
        productName: product.name,
        productNameAr: product.nameAr,
        price: product.price,
        quantity: 1,
        image: product.image,
      ));
    }
    notifyListeners();
  }

  void updateCartItemQuantity(String productId, int quantity) {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    final index = _cart.indexWhere((item) => item.productId == productId);
    if (index >= 0) {
      _cart[index] = _cart[index].copyWith(quantity: quantity);
      notifyListeners();
    }
  }

  void updateCartItemPrice(String productId, double newPrice) {
    final index = _cart.indexWhere((item) => item.productId == productId);
    if (index >= 0) {
      _cart[index] = _cart[index].copyWith(price: newPrice);
      notifyListeners();
    }
  }

  void removeFromCart(String productId) {
    _cart.removeWhere((item) => item.productId == productId);
    notifyListeners();
  }

  void clearCart() {
    _cart.clear();
    _selectedCustomer = null;
    notifyListeners();
  }

  Future<bool> checkout({String paymentMethod = 'cash'}) async {
    if (_cart.isEmpty) return false;

    final order = POSOrder(
      id: 'ORD-${DateTime.now().millisecondsSinceEpoch}',
      customerId: _selectedCustomer?.id,
      customerName: _selectedCustomer?.name,
      items: List.from(_cart),
      subtotal: cartSubtotal,
      tax: cartTax,
      total: cartTotal,
      createdAt: DateTime.now(),
      paymentMethod: paymentMethod,
    );

    _orders.insert(0, order);
    clearCart();
    notifyListeners();
    
    return true;
  }

  // Initialize with demo data
  void initializeDemoData() {
    // Demo orders can be added here if needed
    final demoOrder1 = POSOrder(
      id: 'ORD-001',
      customerId: '1',
      customerName: 'أحمد محمد علي',
      items: [
        CartItem(
          productId: '1',
          productName: 'iPhone 15 Pro Max',
          productNameAr: 'ايفون 15 برو ماكس',
          price: 1350000,
          quantity: 1,
        ),
        CartItem(
          productId: '13',
          productName: 'AirPods Pro 2',
          productNameAr: 'ايربودز برو 2',
          price: 350000,
          quantity: 1,
        ),
      ],
      subtotal: 1700000,
      tax: 0,
      total: 1700000,
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      paymentMethod: 'cash',
    );

    final demoOrder2 = POSOrder(
      id: 'ORD-002',
      customerId: '2',
      customerName: 'فاطمة حسن',
      items: [
        CartItem(
          productId: '6',
          productName: 'MacBook Pro 16"',
          productNameAr: 'ماك بوك برو 16 انش',
          price: 3500000,
          quantity: 1,
        ),
      ],
      subtotal: 3500000,
      tax: 0,
      total: 3500000,
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
      paymentMethod: 'card',
    );

    _orders.addAll([demoOrder1, demoOrder2]);
  }
}
