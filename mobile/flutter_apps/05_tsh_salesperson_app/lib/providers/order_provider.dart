import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class OrderProvider extends ChangeNotifier {
  final ApiService _apiService;
  
  bool _isLoading = false;
  String? _error;
  List<Map<String, dynamic>> _orders = [];
  List<Map<String, dynamic>> _filteredOrders = [];
  String _searchQuery = '';
  String _selectedStatus = '';
  List<String> _statuses = ['draft', 'confirmed', 'processing', 'delivered', 'cancelled'];
  String _sortBy = 'date';
  bool _sortAscending = false;

  OrderProvider(this._apiService);

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasError => _error != null;
  List<Map<String, dynamic>> get orders => _filteredOrders;
  String get searchQuery => _searchQuery;
  String get selectedStatus => _selectedStatus;
  List<String> get statuses => _statuses;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  int get totalOrders => _orders.length;

  // Load orders
  Future<void> loadOrders() async {
    _setLoading(true);
    _clearError();

    try {
      final data = await _apiService.getOrdersAsMaps();
      _orders = List<Map<String, dynamic>>.from(data ?? []);
      _applyFilters();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  // Search orders
  void searchOrders(String query) {
    _searchQuery = query;
    _applyFilters();
    notifyListeners();
  }

  // Filter by status
  void filterByStatus(String status) {
    _selectedStatus = status;
    _applyFilters();
    notifyListeners();
  }

  // Sort orders
  void sortOrders(String sortBy, {bool? ascending}) {
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
    _filteredOrders = List<Map<String, dynamic>>.from(_orders);

    // Apply status filter
    if (_selectedStatus.isNotEmpty) {
      _filteredOrders = _filteredOrders.where((order) {
        return (order['status'] ?? '') == _selectedStatus;
      }).toList();
    }

    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      _filteredOrders = _filteredOrders.where((order) {
        final orderNumber = (order['order_number'] ?? '').toString().toLowerCase();
        final customerName = (order['customer_name'] ?? '').toString().toLowerCase();
        final query = _searchQuery.toLowerCase();
        
        return orderNumber.contains(query) || customerName.contains(query);
      }).toList();
    }

    // Apply sorting
    _filteredOrders.sort((a, b) {
      dynamic aValue = a[_sortBy] ?? '';
      dynamic bValue = b[_sortBy] ?? '';
      
      if (_sortBy == 'total_amount') {
        aValue = (aValue as num).toDouble();
        bValue = (bValue as num).toDouble();
        final comparison = aValue.compareTo(bValue);
        return _sortAscending ? comparison : -comparison;
      } else if (_sortBy == 'date') {
        // Handle date sorting
        aValue = DateTime.parse(aValue.toString());
        bValue = DateTime.parse(bValue.toString());
        final comparison = aValue.compareTo(bValue);
        return _sortAscending ? comparison : -comparison;
      } else {
        final comparison = aValue.toString().toLowerCase().compareTo(bValue.toString().toLowerCase());
        return _sortAscending ? comparison : -comparison;
      }
    });
  }

  // Create new order
  Future<bool> createOrder(Map<String, dynamic> orderData) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _apiService.createOrder(orderData);
      if (result['success'] == true) {
        await loadOrders(); // Reload to get updated list
        _setLoading(false);
        return true;
      } else {
        _setError(result['message'] ?? 'Failed to create order');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Update order status
  Future<bool> updateOrderStatus(int orderId, String newStatus) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _apiService.updateOrderStatus(orderId, newStatus);
      if (result['success'] == true) {
        // Update local data
        final orderIndex = _orders.indexWhere((o) => o['id'] == orderId);
        if (orderIndex != -1) {
          _orders[orderIndex]['status'] = newStatus;
          _applyFilters();
        }
        _setLoading(false);
        return true;
      } else {
        _setError(result['message'] ?? 'Failed to update order status');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Cancel order
  Future<bool> cancelOrder(int orderId) async {
    return await updateOrderStatus(orderId, 'cancelled');
  }

  // Confirm order
  Future<bool> confirmOrder(int orderId) async {
    return await updateOrderStatus(orderId, 'confirmed');
  }

  // Get order by ID
  Map<String, dynamic>? getOrderById(int orderId) {
    try {
      return _orders.firstWhere((order) => order['id'] == orderId);
    } catch (e) {
      return null;
    }
  }

  // Get orders by status
  List<Map<String, dynamic>> getOrdersByStatus(String status) {
    return _orders.where((order) => order['status'] == status).toList();
  }

  // Get order statistics
  Map<String, dynamic> getOrderStats() {
    final total = _orders.length;
    final draft = getOrdersByStatus('draft').length;
    final confirmed = getOrdersByStatus('confirmed').length;
    final processing = getOrdersByStatus('processing').length;
    final delivered = getOrdersByStatus('delivered').length;
    final cancelled = getOrdersByStatus('cancelled').length;
    
    double totalAmount = 0.0;
    for (final order in _orders) {
      if (order['status'] != 'cancelled') {
        totalAmount += ((order['total_amount'] ?? 0.0) as num).toDouble();
      }
    }
    
    return {
      'total': total,
      'draft': draft,
      'confirmed': confirmed,
      'processing': processing,
      'delivered': delivered,
      'cancelled': cancelled,
      'total_amount': totalAmount,
    };
  }

  // Get recent orders
  List<Map<String, dynamic>> getRecentOrders({int limit = 10}) {
    final recentOrders = List<Map<String, dynamic>>.from(_orders);
    recentOrders.sort((a, b) {
      final aDate = DateTime.parse(a['date'].toString());
      final bDate = DateTime.parse(b['date'].toString());
      return bDate.compareTo(aDate);
    });
    return recentOrders.take(limit).toList();
  }

  // Clear filters
  void clearFilters() {
    _searchQuery = '';
    _selectedStatus = '';
    _sortBy = 'date';
    _sortAscending = false;
    _applyFilters();
    notifyListeners();
  }

  // Refresh orders list
  Future<void> refreshOrders() async {
    await loadOrders();
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
    _orders = [
      {
        'id': 1,
        'order_number': 'ORD-2024-001',
        'customer_id': 1,
        'customer_name': 'أحمد علي محمد',
        'date': '2024-01-15T10:30:00.000Z',
        'status': 'confirmed',
        'total_amount': 645.0,
        'items': [
          {'name': 'تذكرة سفر - بغداد/دبي', 'quantity': 1, 'price': 450.0},
          {'name': 'حجز فندق - دبي', 'quantity': 1, 'price': 120.0},
          {'name': 'تأشيرة دخول - الإمارات', 'quantity': 1, 'price': 75.0},
        ],
        'notes': 'طلب عاجل - يفضل التأكيد اليوم',
      },
      {
        'id': 2,
        'order_number': 'ORD-2024-002',
        'customer_id': 2,
        'customer_name': 'فاطمة حسن أحمد',
        'date': '2024-01-14T14:15:00.000Z',
        'status': 'processing',
        'total_amount': 570.0,
        'items': [
          {'name': 'تذكرة سفر - بغداد/دبي', 'quantity': 1, 'price': 450.0},
          {'name': 'تأمين سفر', 'quantity': 1, 'price': 30.0},
          {'name': 'تأشيرة دخول - الإمارات', 'quantity': 1, 'price': 75.0},
          {'name': 'خدمة نقل من المطار', 'quantity': 1, 'price': 25.0},
        ],
        'notes': '',
      },
      {
        'id': 3,
        'order_number': 'ORD-2024-003',
        'customer_id': 3,
        'customer_name': 'محمد سعد عبدالله',
        'date': '2024-01-13T09:45:00.000Z',
        'status': 'draft',
        'total_amount': 525.0,
        'items': [
          {'name': 'تذكرة سفر - بغداد/دبي', 'quantity': 1, 'price': 450.0},
          {'name': 'تأشيرة دخول - الإمارات', 'quantity': 1, 'price': 75.0},
        ],
        'notes': 'بانتظار تأكيد العميل',
      },
      {
        'id': 4,
        'order_number': 'ORD-2024-004',
        'customer_id': 1,
        'customer_name': 'أحمد علي محمد',
        'date': '2024-01-12T16:20:00.000Z',
        'status': 'delivered',
        'total_amount': 195.0,
        'items': [
          {'name': 'حجز فندق - دبي', 'quantity': 1, 'price': 120.0},
          {'name': 'تأشيرة دخول - الإمارات', 'quantity': 1, 'price': 75.0},
        ],
        'notes': 'تم التسليم بنجاح',
      },
      {
        'id': 5,
        'order_number': 'ORD-2024-005',
        'customer_id': 2,
        'customer_name': 'فاطمة حسن أحمد',
        'date': '2024-01-11T11:10:00.000Z',
        'status': 'cancelled',
        'total_amount': 450.0,
        'items': [
          {'name': 'تذكرة سفر - بغداد/دبي', 'quantity': 1, 'price': 450.0},
        ],
        'notes': 'تم الإلغاء بناءً على طلب العميل',
      },
    ];

    _applyFilters();
    notifyListeners();
  }
}
