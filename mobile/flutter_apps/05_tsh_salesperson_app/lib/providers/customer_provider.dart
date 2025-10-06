import 'package:flutter/foundation.dart';
import '../services/odoo_service.dart';

class CustomerProvider extends ChangeNotifier {
  final OdooService _odooService;
  
  bool _isLoading = false;
  String? _error;
  List<Map<String, dynamic>> _customers = [];
  List<Map<String, dynamic>> _filteredCustomers = [];
  String _searchQuery = '';
  String _sortBy = 'name';
  bool _sortAscending = true;

  CustomerProvider(this._odooService);

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasError => _error != null;
  List<Map<String, dynamic>> get customers => _filteredCustomers;
  String get searchQuery => _searchQuery;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  int get totalCustomers => _customers.length;

  // Load customers
  Future<void> loadCustomers() async {
    _setLoading(true);
    _clearError();

    try {
      final data = await _odooService.getCustomersAsMaps();
      _customers = List<Map<String, dynamic>>.from(data ?? []);
      _applyFilters();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  // Search customers
  void searchCustomers(String query) {
    _searchQuery = query;
    _applyFilters();
    notifyListeners();
  }

  // Sort customers
  void sortCustomers(String sortBy, {bool? ascending}) {
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
    _filteredCustomers = List<Map<String, dynamic>>.from(_customers);

    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      _filteredCustomers = _filteredCustomers.where((customer) {
        final name = (customer['name'] ?? '').toString().toLowerCase();
        final code = (customer['customer_code'] ?? '').toString().toLowerCase();
        final phone = (customer['phone'] ?? '').toString().toLowerCase();
        final query = _searchQuery.toLowerCase();
        
        return name.contains(query) || 
               code.contains(query) || 
               phone.contains(query);
      }).toList();
    }

    // Apply sorting
    _filteredCustomers.sort((a, b) {
      dynamic aValue = a[_sortBy] ?? '';
      dynamic bValue = b[_sortBy] ?? '';
      
      if (aValue is String && bValue is String) {
        final comparison = aValue.toLowerCase().compareTo(bValue.toLowerCase());
        return _sortAscending ? comparison : -comparison;
      } else {
        final comparison = aValue.toString().compareTo(bValue.toString());
        return _sortAscending ? comparison : -comparison;
      }
    });
  }

  // Add new customer
  Future<bool> addCustomer(Map<String, dynamic> customerData) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _odooService.createCustomer(customerData);
      if (result?['success'] == true) {
        await loadCustomers(); // Reload to get updated list
        _setLoading(false);
        return true;
      } else {
        _setError(result?['message'] ?? 'Failed to create customer');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Update customer
  Future<bool> updateCustomer(int customerId, Map<String, dynamic> customerData) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _odooService.updateCustomer(customerId, customerData);
      if (result?['success'] == true) {
        await loadCustomers(); // Reload to get updated list
        _setLoading(false);
        return true;
      } else {
        _setError(result?['message'] ?? 'Failed to update customer');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Delete customer
  Future<bool> deleteCustomer(int customerId) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _odooService.deleteCustomer(customerId);
      if (result?['success'] == true) {
        await loadCustomers(); // Reload to get updated list
        _setLoading(false);
        return true;
      } else {
        _setError(result?['message'] ?? 'Failed to delete customer');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Get customer by ID
  Map<String, dynamic>? getCustomerById(int customerId) {
    try {
      return _customers.firstWhere((customer) => customer['id'] == customerId);
    } catch (e) {
      return null;
    }
  }

  // Get customer statistics
  Map<String, dynamic> getCustomerStats() {
    final activeCustomers = _customers.where((c) => c['active'] == true).length;
    final inactiveCustomers = _customers.length - activeCustomers;
    
    return {
      'total': _customers.length,
      'active': activeCustomers,
      'inactive': inactiveCustomers,
    };
  }

  // Clear search and filters
  void clearFilters() {
    _searchQuery = '';
    _sortBy = 'name';
    _sortAscending = true;
    _applyFilters();
    notifyListeners();
  }

  // Refresh customers list
  Future<void> refreshCustomers() async {
    await loadCustomers();
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
    _customers = [
      {
        'id': 1,
        'name': 'أحمد علي محمد',
        'customer_code': 'CUST-001',
        'phone': '+964 770 123 4567',
        'email': 'ahmed.ali@example.com',
        'address': 'بغداد - الكرادة',
        'active': true,
        'created_date': '2024-01-15',
        'total_orders': 15,
        'total_amount': 450000.0,
      },
      {
        'id': 2,
        'name': 'فاطمة حسن أحمد',
        'customer_code': 'CUST-002',
        'phone': '+964 750 987 6543',
        'email': 'fatima.hassan@example.com',
        'address': 'البصرة - المعقل',
        'active': true,
        'created_date': '2024-01-12',
        'total_orders': 8,
        'total_amount': 280000.0,
      },
      {
        'id': 3,
        'name': 'محمد سعد عبدالله',
        'customer_code': 'CUST-003',
        'phone': '+964 790 456 7890',
        'email': 'mohammad.saad@example.com',
        'address': 'أربيل - الشورجة',
        'active': false,
        'created_date': '2024-01-10',
        'total_orders': 3,
        'total_amount': 95000.0,
      },
    ];

    _applyFilters();
    notifyListeners();
  }
}
