import 'package:flutter/foundation.dart';
import '../services/odoo_service.dart';

class PaymentProvider extends ChangeNotifier {
  final OdooService _odooService;
  
  bool _isLoading = false;
  String? _error;
  List<Map<String, dynamic>> _payments = [];
  List<Map<String, dynamic>> _filteredPayments = [];
  String _searchQuery = '';
  String _selectedMethod = '';
  String _selectedStatus = '';
  List<String> _paymentMethods = ['cash', 'card', 'bank_transfer', 'mobile_payment'];
  List<String> _paymentStatuses = ['pending', 'completed', 'failed', 'refunded'];
  String _sortBy = 'date';
  bool _sortAscending = false;

  PaymentProvider(this._odooService);

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasError => _error != null;
  List<Map<String, dynamic>> get payments => _filteredPayments;
  String get searchQuery => _searchQuery;
  String get selectedMethod => _selectedMethod;
  String get selectedStatus => _selectedStatus;
  List<String> get paymentMethods => _paymentMethods;
  List<String> get paymentStatuses => _paymentStatuses;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  int get totalPayments => _payments.length;

  // Load payments
  Future<void> loadPayments() async {
    _setLoading(true);
    _clearError();

    try {
      final data = await _odooService.getPayments();
      _payments = List<Map<String, dynamic>>.from(data ?? []);
      _applyFilters();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  // Search payments
  void searchPayments(String query) {
    _searchQuery = query;
    _applyFilters();
    notifyListeners();
  }

  // Filter by payment method
  void filterByMethod(String method) {
    _selectedMethod = method;
    _applyFilters();
    notifyListeners();
  }

  // Filter by payment status
  void filterByStatus(String status) {
    _selectedStatus = status;
    _applyFilters();
    notifyListeners();
  }

  // Sort payments
  void sortPayments(String sortBy, {bool? ascending}) {
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
    _filteredPayments = List<Map<String, dynamic>>.from(_payments);

    // Apply method filter
    if (_selectedMethod.isNotEmpty) {
      _filteredPayments = _filteredPayments.where((payment) {
        return (payment['payment_method'] ?? '') == _selectedMethod;
      }).toList();
    }

    // Apply status filter
    if (_selectedStatus.isNotEmpty) {
      _filteredPayments = _filteredPayments.where((payment) {
        return (payment['status'] ?? '') == _selectedStatus;
      }).toList();
    }

    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      _filteredPayments = _filteredPayments.where((payment) {
        final reference = (payment['reference'] ?? '').toString().toLowerCase();
        final customerName = (payment['customer_name'] ?? '').toString().toLowerCase();
        final query = _searchQuery.toLowerCase();
        
        return reference.contains(query) || customerName.contains(query);
      }).toList();
    }

    // Apply sorting
    _filteredPayments.sort((a, b) {
      dynamic aValue = a[_sortBy] ?? '';
      dynamic bValue = b[_sortBy] ?? '';
      
      if (_sortBy == 'amount') {
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

  // Process payment
  Future<bool> processPayment(Map<String, dynamic> paymentData) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _odooService.processPayment(paymentData);
      if (result?['success'] == true) {
        await loadPayments(); // Reload to get updated list
        _setLoading(false);
        return true;
      } else {
        _setError(result?['message'] ?? 'Payment processing failed');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Refund payment
  Future<bool> refundPayment(int paymentId, double amount, String reason) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _odooService.refundPayment(paymentId, amount, reason);
      if (result?['success'] == true) {
        // Update local data
        final paymentIndex = _payments.indexWhere((p) => p['id'] == paymentId);
        if (paymentIndex != -1) {
          _payments[paymentIndex]['status'] = 'refunded';
          _payments[paymentIndex]['refund_amount'] = amount;
          _payments[paymentIndex]['refund_reason'] = reason;
          _applyFilters();
        }
        _setLoading(false);
        return true;
      } else {
        _setError(result?['message'] ?? 'Refund failed');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Get payment by ID
  Map<String, dynamic>? getPaymentById(int paymentId) {
    try {
      return _payments.firstWhere((payment) => payment['id'] == paymentId);
    } catch (e) {
      return null;
    }
  }

  // Get payments by status
  List<Map<String, dynamic>> getPaymentsByStatus(String status) {
    return _payments.where((payment) => payment['status'] == status).toList();
  }

  // Get payment statistics
  Map<String, dynamic> getPaymentStats() {
    final total = _payments.length;
    final pending = getPaymentsByStatus('pending').length;
    final completed = getPaymentsByStatus('completed').length;
    final failed = getPaymentsByStatus('failed').length;
    final refunded = getPaymentsByStatus('refunded').length;
    
    double totalAmount = 0.0;
    double completedAmount = 0.0;
    double refundedAmount = 0.0;
    
    for (final payment in _payments) {
      final amount = ((payment['amount'] ?? 0.0) as num).toDouble();
      totalAmount += amount;
      
      if (payment['status'] == 'completed') {
        completedAmount += amount;
      } else if (payment['status'] == 'refunded') {
        refundedAmount += amount;
      }
    }
    
    // Calculate stats by payment method
    final Map<String, int> methodStats = {};
    final Map<String, double> methodAmounts = {};
    
    for (final payment in _payments) {
      final method = payment['payment_method'] ?? 'unknown';
      final amount = ((payment['amount'] ?? 0.0) as num).toDouble();
      
      methodStats[method] = (methodStats[method] ?? 0) + 1;
      methodAmounts[method] = (methodAmounts[method] ?? 0.0) + amount;
    }
    
    return {
      'total': total,
      'pending': pending,
      'completed': completed,
      'failed': failed,
      'refunded': refunded,
      'total_amount': totalAmount,
      'completed_amount': completedAmount,
      'refunded_amount': refundedAmount,
      'method_stats': methodStats,
      'method_amounts': methodAmounts,
    };
  }

  // Get recent payments
  List<Map<String, dynamic>> getRecentPayments({int limit = 10}) {
    final recentPayments = List<Map<String, dynamic>>.from(_payments);
    recentPayments.sort((a, b) {
      final aDate = DateTime.parse(a['date'].toString());
      final bDate = DateTime.parse(b['date'].toString());
      return bDate.compareTo(aDate);
    });
    return recentPayments.take(limit).toList();
  }

  // Get payments by date range
  List<Map<String, dynamic>> getPaymentsByDateRange(DateTime startDate, DateTime endDate) {
    return _payments.where((payment) {
      final paymentDate = DateTime.parse(payment['date'].toString());
      return paymentDate.isAfter(startDate.subtract(const Duration(days: 1))) &&
             paymentDate.isBefore(endDate.add(const Duration(days: 1)));
    }).toList();
  }

  // Clear filters
  void clearFilters() {
    _searchQuery = '';
    _selectedMethod = '';
    _selectedStatus = '';
    _sortBy = 'date';
    _sortAscending = false;
    _applyFilters();
    notifyListeners();
  }

  // Refresh payments list
  Future<void> refreshPayments() async {
    await loadPayments();
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
    _payments = [
      {
        'id': 1,
        'reference': 'PAY-2024-001',
        'order_id': 1,
        'customer_id': 1,
        'customer_name': 'أحمد علي محمد',
        'amount': 645.0,
        'payment_method': 'card',
        'status': 'completed',
        'date': '2024-01-15T11:00:00.000Z',
        'currency': 'USD',
        'notes': 'دفع بالبطاقة الائتمانية',
      },
      {
        'id': 2,
        'reference': 'PAY-2024-002',
        'order_id': 2,
        'customer_id': 2,
        'customer_name': 'فاطمة حسن أحمد',
        'amount': 285.0,
        'payment_method': 'cash',
        'status': 'completed',
        'date': '2024-01-14T15:30:00.000Z',
        'currency': 'USD',
        'notes': 'دفعة أولى نقدية - باقي المبلغ عند التسليم',
      },
      {
        'id': 3,
        'reference': 'PAY-2024-003',
        'order_id': 3,
        'customer_id': 3,
        'customer_name': 'محمد سعد عبدالله',
        'amount': 525.0,
        'payment_method': 'bank_transfer',
        'status': 'pending',
        'date': '2024-01-13T10:15:00.000Z',
        'currency': 'USD',
        'notes': 'بانتظار تأكيد التحويل البنكي',
      },
      {
        'id': 4,
        'reference': 'PAY-2024-004',
        'order_id': 4,
        'customer_id': 1,
        'customer_name': 'أحمد علي محمد',
        'amount': 195.0,
        'payment_method': 'mobile_payment',
        'status': 'completed',
        'date': '2024-01-12T16:45:00.000Z',
        'currency': 'USD',
        'notes': 'دفع عبر المحفظة الإلكترونية',
      },
      {
        'id': 5,
        'reference': 'PAY-2024-005',
        'order_id': 5,
        'customer_id': 2,
        'customer_name': 'فاطمة حسن أحمد',
        'amount': 450.0,
        'payment_method': 'card',
        'status': 'refunded',
        'date': '2024-01-11T12:30:00.000Z',
        'currency': 'USD',
        'notes': 'تم استرداد المبلغ بعد إلغاء الطلب',
        'refund_amount': 450.0,
        'refund_reason': 'إلغاء الطلب بناءً على طلب العميل',
      },
      {
        'id': 6,
        'reference': 'PAY-2024-006',
        'order_id': 6,
        'customer_id': 3,
        'customer_name': 'محمد سعد عبدالله',
        'amount': 320.0,
        'payment_method': 'cash',
        'status': 'failed',
        'date': '2024-01-10T14:20:00.000Z',
        'currency': 'USD',
        'notes': 'فشل في المعاملة - مبلغ غير كافي',
      },
    ];

    _applyFilters();
    notifyListeners();
  }
}
