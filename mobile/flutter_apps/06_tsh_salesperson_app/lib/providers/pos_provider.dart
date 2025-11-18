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

  // Fetch products from TSH ERP API (Self-Hosted)
  Future<void> fetchProducts() async {
    _isLoadingProducts = true;
    _productsError = null;
    notifyListeners();

    try {
      final response = await http.get(
        Uri.parse('https://erp.tsh.sale/api/consumer/products?limit=1000'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final responseData = json.decode(response.body);
        // Consumer API returns {status, items, count, total}
        final List<dynamic> items = responseData['items'] ?? [];
        _products = items.map((json) => POSProduct.fromJson(json)).toList();
        _productsError = null;
        print('Successfully loaded ${_products.length} products');
      } else {
        _productsError = 'Failed to load products: ${response.statusCode}';
        print('Failed to load products: ${response.statusCode}');
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

  // Customers from TSH ERP (Self-Hosted)
  List<POSCustomer> _customers = [];
  bool _isLoadingCustomers = false;
  String? _customersError;

  bool get isLoadingCustomers => _isLoadingCustomers;
  String? get customersError => _customersError;

  // Fetch customers from TSH ERP API
  Future<void> fetchCustomers() async {
    _isLoadingCustomers = true;
    _customersError = null;
    notifyListeners();

    try {
      // TODO: Implement BFF customer endpoint for salesperson
      // For now, use sample customers for testing
      _customers = [
        POSCustomer(
          id: '1',
          name: 'عميل نقدي',
          phone: '07XX XXX XXXX',
          email: 'cash@tsh.sale',
        ),
        POSCustomer(
          id: '2',
          name: 'شركة السلام للتجارة',
          phone: '07701234567',
          email: 'alsalam@example.com',
        ),
        POSCustomer(
          id: '3',
          name: 'متجر النور',
          phone: '07707654321',
          email: 'alnoor@example.com',
        ),
      ];
      _customersError = null;
      print('Loaded ${_customers.length} sample customers (endpoint pending)');
    } catch (e) {
      _customersError = 'Error loading customers: $e';
      print('Error fetching customers: $e');
    } finally {
      _isLoadingCustomers = false;
      notifyListeners();
    }
  }

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

  // Initialize with real data from TSH ERP API
  Future<void> initializeDemoData() async {
    // Fetch products and customers from TSH ERP API
    await Future.wait([
      fetchProducts(),
      fetchCustomers(),
    ]);

    // Orders will be fetched from backend when needed
    // For now, keeping it empty (no demo orders)
  }
}
