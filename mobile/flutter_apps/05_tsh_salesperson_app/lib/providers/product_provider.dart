import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class ProductProvider extends ChangeNotifier {
  final ApiService _apiService;
  
  bool _isLoading = false;
  String? _error;
  List<Map<String, dynamic>> _products = [];
  List<Map<String, dynamic>> _filteredProducts = [];
  String _searchQuery = '';
  String _selectedCategory = '';
  List<String> _categories = [];
  String _sortBy = 'name';
  bool _sortAscending = true;

  ProductProvider(this._apiService);

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasError => _error != null;
  List<Map<String, dynamic>> get products => _filteredProducts;
  String get searchQuery => _searchQuery;
  String get selectedCategory => _selectedCategory;
  List<String> get categories => _categories;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  int get totalProducts => _products.length;

  // Load products
  Future<void> loadProducts() async {
    _setLoading(true);
    _clearError();

    try {
      final data = await _apiService.getProductsAsMaps();
      _products = List<Map<String, dynamic>>.from(data ?? []);
      _updateCategories();
      _applyFilters();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  // Update categories list
  void _updateCategories() {
    final categorySet = <String>{};
    for (final product in _products) {
      final category = product['category'] ?? '';
      if (category.isNotEmpty) {
        categorySet.add(category);
      }
    }
    _categories = categorySet.toList()..sort();
  }

  // Search products
  void searchProducts(String query) {
    _searchQuery = query;
    _applyFilters();
    notifyListeners();
  }

  // Filter by category
  void filterByCategory(String category) {
    _selectedCategory = category;
    _applyFilters();
    notifyListeners();
  }

  // Sort products
  void sortProducts(String sortBy, {bool? ascending}) {
    _sortBy = sortBy;
    if (ascending != null) {
      _sortAscending = ascending;
    } else {
      _sortAscending = !_sortAscending;
    }
    _applyFilters();
    notifyListeners();
  }

  // Apply filters and sorting
  void _applyFilters() {
    _filteredProducts = List<Map<String, dynamic>>.from(_products);

    // Apply category filter
    if (_selectedCategory.isNotEmpty) {
      _filteredProducts = _filteredProducts.where((product) {
        return (product['category'] ?? '') == _selectedCategory;
      }).toList();
    }

    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      _filteredProducts = _filteredProducts.where((product) {
        final name = (product['name'] ?? '').toString().toLowerCase();
        final code = (product['product_code'] ?? '').toString().toLowerCase();
        final description = (product['description'] ?? '').toString().toLowerCase();
        final query = _searchQuery.toLowerCase();
        
        return name.contains(query) || 
               code.contains(query) || 
               description.contains(query);
      }).toList();
    }

    // Apply sorting
    _filteredProducts.sort((a, b) {
      dynamic aValue = a[_sortBy] ?? '';
      dynamic bValue = b[_sortBy] ?? '';
      
      if (_sortBy == 'price' || _sortBy == 'quantity') {
        aValue = (aValue as num).toDouble();
        bValue = (bValue as num).toDouble();
        final comparison = aValue.compareTo(bValue);
        return _sortAscending ? comparison : -comparison;
      } else {
        final comparison = aValue.toString().toLowerCase().compareTo(bValue.toString().toLowerCase());
        return _sortAscending ? comparison : -comparison;
      }
    });
  }

  // Get product by ID
  Map<String, dynamic>? getProductById(int productId) {
    try {
      return _products.firstWhere((product) => product['id'] == productId);
    } catch (e) {
      return null;
    }
  }

  // Update product quantity
  Future<bool> updateProductQuantity(int productId, int newQuantity) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _apiService.updateProductQuantity(productId, newQuantity);
      if (result['success'] == true) {
        // Update local data
        final productIndex = _products.indexWhere((p) => p['id'] == productId);
        if (productIndex != -1) {
          _products[productIndex]['quantity'] = newQuantity;
          _applyFilters();
        }
        _setLoading(false);
        return true;
      } else {
        _setError(result['message'] ?? 'Failed to update quantity');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Get low stock products
  List<Map<String, dynamic>> getLowStockProducts({int threshold = 10}) {
    return _products.where((product) {
      final quantity = (product['quantity'] ?? 0) as int;
      return quantity <= threshold && quantity > 0;
    }).toList();
  }

  // Get out of stock products
  List<Map<String, dynamic>> getOutOfStockProducts() {
    return _products.where((product) {
      final quantity = (product['quantity'] ?? 0) as int;
      return quantity <= 0;
    }).toList();
  }

  // Get product statistics
  Map<String, dynamic> getProductStats() {
    final totalProducts = _products.length;
    final lowStock = getLowStockProducts().length;
    final outOfStock = getOutOfStockProducts().length;
    final inStock = totalProducts - outOfStock;
    
    double totalValue = 0.0;
    for (final product in _products) {
      final price = ((product['price'] ?? 0.0) as num).toDouble();
      final quantity = ((product['quantity'] ?? 0) as int);
      totalValue += price * quantity;
    }
    
    return {
      'total': totalProducts,
      'in_stock': inStock,
      'low_stock': lowStock,
      'out_of_stock': outOfStock,
      'total_value': totalValue,
      'categories': _categories.length,
    };
  }

  // Clear filters
  void clearFilters() {
    _searchQuery = '';
    _selectedCategory = '';
    _sortBy = 'name';
    _sortAscending = true;
    _applyFilters();
    notifyListeners();
  }

  // Refresh products list
  Future<void> refreshProducts() async {
    await loadProducts();
  }

  // Private helper methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }

  // Mock data for demo purposes
  void loadMockData() {
    _products = [
      {
        'id': 1,
        'name': 'تذكرة سفر - بغداد/دبي',
        'product_code': 'TKT-BGD-DXB-001',
        'category': 'تذاكر طيران',
        'description': 'تذكرة سفر من بغداد إلى دبي - درجة اقتصادية',
        'price': 450.0,
        'quantity': 50,
        'available': true,
        'currency': 'USD',
      },
      {
        'id': 2,
        'name': 'حجز فندق - دبي',
        'product_code': 'HTL-DXB-001',
        'category': 'حجوزات فندقية',
        'description': 'حجز فندق في دبي - غرفة مفردة لمدة ليلة واحدة',
        'price': 120.0,
        'quantity': 25,
        'available': true,
        'currency': 'USD',
      },
      {
        'id': 3,
        'name': 'تأشيرة دخول - الإمارات',
        'product_code': 'VISA-UAE-001',
        'category': 'تأشيرات',
        'description': 'تأشيرة دخول للإمارات العربية المتحدة - سياحية',
        'price': 75.0,
        'quantity': 100,
        'available': true,
        'currency': 'USD',
      },
      {
        'id': 4,
        'name': 'تأمين سفر',
        'product_code': 'INS-TRV-001',
        'category': 'تأمين',
        'description': 'تأمين صحي للسفر - تغطية شاملة',
        'price': 30.0,
        'quantity': 5,
        'available': true,
        'currency': 'USD',
      },
      {
        'id': 5,
        'name': 'خدمة نقل من المطار',
        'product_code': 'TRANS-APT-001',
        'category': 'نقل ومواصلات',
        'description': 'خدمة نقل من المطار إلى الفندق',
        'price': 25.0,
        'quantity': 0,
        'available': false,
        'currency': 'USD',
      },
    ];

    _updateCategories();
    _applyFilters();
    notifyListeners();
  }
}
