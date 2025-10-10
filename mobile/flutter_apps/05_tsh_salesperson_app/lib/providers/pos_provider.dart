import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/pos_product.dart';
import '../models/pos_customer.dart';
import '../models/cart_item.dart';

class POSProvider with ChangeNotifier {
  // Products from API
  List<POSProduct> _products = [];
  bool _isLoadingProducts = false;
  String? _productsError;

  bool get isLoadingProducts => _isLoadingProducts;
  String? get productsError => _productsError;

  // Fetch products from inventory API
  Future<void> fetchProducts() async {
    _isLoadingProducts = true;
    _productsError = null;
    notifyListeners();

    try {
      final response = await http.get(
        Uri.parse('http://192.168.68.82:8000/api/inventory/items?limit=1000'),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        _products = data.map((json) => POSProduct.fromJson(json)).toList();
        _productsError = null;
      } else {
        _productsError = 'Failed to load products: ${response.statusCode}';
      }
    } catch (e) {
      _productsError = 'Error loading products: $e';
      print('Error fetching products: $e');
    } finally {
      _isLoadingProducts = false;
      notifyListeners();
    }
  }

  // Demo products removed - using real data from API only

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
  Future<void> initializeDemoData() async {
    // Fetch products from API
    await fetchProducts();

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
