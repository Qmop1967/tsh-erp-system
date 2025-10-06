import 'package:flutter/foundation.dart';
import '../services/odoo_service.dart';

class DashboardProvider extends ChangeNotifier {
  final OdooService _odooService;
  
  bool _isLoading = false;
  String? _error;
  
  // Dashboard data
  Map<String, dynamic> _receivablesData = {};
  Map<String, dynamic> _commissionData = {};
  Map<String, dynamic> _cashBoxData = {};
  List<Map<String, dynamic>> _regionalData = [];
  
  // Summary statistics
  double _totalReceivables = 0.0;
  double _totalCommission = 0.0;
  double _cashBalance = 0.0;
  int _totalCustomers = 0;
  int _activeOrders = 0;
  
  // Trend data
  double _receivablesTrend = 0.0;
  double _commissionTrend = 0.0;
  
  // Leaderboard data
  Map<String, dynamic> _leaderboardData = {};
  Map<String, dynamic> _dashboardData = {};

  DashboardProvider(this._odooService);

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasError => _error != null;
  
  Map<String, dynamic> get receivablesData => _receivablesData;
  Map<String, dynamic> get commissionData => _commissionData;
  Map<String, dynamic> get cashBoxData => _cashBoxData;
  List<Map<String, dynamic>> get regionalData => _regionalData;
  
  double get totalReceivables => _totalReceivables;
  double get totalCommission => _totalCommission;
  double get cashBalance => _cashBalance;
  int get totalCustomers => _totalCustomers;
  int get activeOrders => _activeOrders;
  
  double get receivablesTrend => _receivablesTrend;
  double get commissionTrend => _commissionTrend;
  
  // New getters for leaderboard
  Map<String, dynamic> get leaderboardData => _leaderboardData;
  Map<String, dynamic> get dashboardData => _dashboardData;

  // Load dashboard data
  Future<void> loadDashboard() async {
    _setLoading(true);
    _clearError();

    try {
      // Load all dashboard data
      await Future.wait([
        _loadReceivables(),
        _loadCommission(),
        _loadCashBox(),
        _loadRegionalData(),
        _loadSummaryStats(),
        _loadLeaderboardData(),
      ]);
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  // Load receivables data
  Future<void> _loadReceivables() async {
    try {
      final data = await _odooService.getDashboardData('receivables');
      _receivablesData = data ?? {};
      _totalReceivables = (_receivablesData['total'] ?? 0.0).toDouble();
      _receivablesTrend = (_receivablesData['trend'] ?? 0.0).toDouble();
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading receivables: $e');
    }
  }

  // Load commission data
  Future<void> _loadCommission() async {
    try {
      final data = await _odooService.getDashboardData('commission');
      _commissionData = data ?? {};
      _totalCommission = (_commissionData['total'] ?? 0.0).toDouble();
      _commissionTrend = (_commissionData['trend'] ?? 0.0).toDouble();
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading commission: $e');
    }
  }

  // Load cash box data
  Future<void> _loadCashBox() async {
    try {
      final data = await _odooService.getDashboardData('cashbox');
      _cashBoxData = data ?? {};
      _cashBalance = (_cashBoxData['balance'] ?? 0.0).toDouble();
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading cash box: $e');
    }
  }

  // Load regional breakdown data
  Future<void> _loadRegionalData() async {
    try {
      final data = await _odooService.getDashboardData('regional');
      if (data != null && data['regions'] is List) {
        _regionalData = List<Map<String, dynamic>>.from(data['regions']);
      } else {
        _regionalData = [];
      }
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading regional data: $e');
      _regionalData = [];
    }
  }

  // Load summary statistics
  Future<void> _loadSummaryStats() async {
    try {
      final data = await _odooService.getDashboardData('summary');
      if (data != null) {
        _totalCustomers = (data['total_customers'] ?? 0).toInt();
        _activeOrders = (data['active_orders'] ?? 0).toInt();
      }
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading summary stats: $e');
    }
  }

  // Load leaderboard data
  Future<void> _loadLeaderboardData() async {
    try {
      final data = await _odooService.getDashboardData('leaderboard');
      _leaderboardData = data ?? {};
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading leaderboard data: $e');
      _leaderboardData = {};
    }
  }

  // Refresh dashboard
  Future<void> refreshDashboard() async {
    await loadDashboard();
  }

  // Process settlement
  Future<bool> processSettlement(Map<String, dynamic> settlementData) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _odooService.processSettlement(settlementData);
      if (result['success'] == true) {
        // Reload cash box data after successful settlement
        await _loadCashBox();
        _setLoading(false);
        return true;
      } else {
        _setError(result['message'] ?? 'Settlement failed');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError(e.toString());
      _setLoading(false);
      return false;
    }
  }

  // Get performance metrics
  Map<String, double> getPerformanceMetrics() {
    return {
      'receivables_total': _totalReceivables,
      'commission_total': _totalCommission,
      'cash_balance': _cashBalance,
      'receivables_trend': _receivablesTrend,
      'commission_trend': _commissionTrend,
    };
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
    _receivablesData = {
      'total': 150000.0,
      'trend': 12.5,
      'details': [
        {'name': 'فاتورة غير مدفوعة', 'amount': 50000.0, 'date': '2024-01-15'},
        {'name': 'مستحقات متأخرة', 'amount': 100000.0, 'date': '2023-12-20'},
      ]
    };

    _commissionData = {
      'total': 25000.0,
      'trend': 8.3,
      'monthly_target': 30000.0,
      'achievement_rate': 83.3,
    };

    _cashBoxData = {
      'balance': 75000.0,
      'last_settlement': '2024-01-10',
      'pending_amount': 15000.0,
    };

    _regionalData = [
      {'name': 'بغداد', 'sales': 80000.0, 'customers': 150},
      {'name': 'البصرة', 'sales': 45000.0, 'customers': 85},
      {'name': 'أربيل', 'sales': 25000.0, 'customers': 45},
    ];

    _totalReceivables = 150000.0;
    _totalCommission = 25000.0;
    _cashBalance = 75000.0;
    _totalCustomers = 280;
    _activeOrders = 45;
    _receivablesTrend = 12.5;
    _commissionTrend = 8.3;

    notifyListeners();
  }
  
  // Fetch dashboard data
  Future<void> fetchDashboardData() async {
    _setLoading(true);
    _clearError();

    try {
      // Mock dashboard data
      _dashboardData = {
        'commission': {
          'total': 45000000.0,
          'paid': 30000000.0,
          'pending': 15000000.0,
          'this_month': 8500000.0,
        },
        'receivables': {
          'total': 125000000.0,
          'overdue': 35000000.0,
          'due_this_week': 12000000.0,
          'customer_count': 45,
        },
        'cash_box': {
          'amount': 5500000.0,
        },
        'digital_payments': {
          'amount': 12500000.0,
          'count': 38,
        },
        'sales': {
          'today': 3200000.0,
          'this_week': 18500000.0,
          'this_month': 65000000.0,
          'growth_percentage': 15.5,
          'top_products': [
            {'name': 'منتج A', 'quantity': 45, 'revenue': 12500000.0},
            {'name': 'منتج B', 'quantity': 32, 'revenue': 8900000.0},
            {'name': 'منتج C', 'quantity': 28, 'revenue': 7200000.0},
          ],
        },
      };
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }
  
  // Fetch leaderboard data
  Future<void> fetchLeaderboardData(String period) async {
    _setLoading(true);
    _clearError();

    try {
      // Mock leaderboard data
      _leaderboardData = {
        'current_level': {
          'name': 'ذهبي',
          'progress': 0.65,
          'current_points': 6500,
          'next_level_points': 10000,
          'rank': 8,
          'total_salespeople': 45,
        },
        'challenges': [
          {
            'title': 'بطل المبيعات',
            'description': 'حقق 50 مليون مبيعات هذا الشهر',
            'progress': 0.82,
            'reward': '500,000 نقطة',
            'is_completed': false,
          },
          {
            'title': 'جامع الديون',
            'description': 'حصّل 30 مليون هذا الأسبوع',
            'progress': 0.45,
            'reward': '300,000 نقطة',
            'is_completed': false,
          },
          {
            'title': 'الزيارات النشطة',
            'description': 'قم بزيارة 20 عميل',
            'progress': 1.0,
            'reward': '200,000 نقطة',
            'is_completed': true,
          },
        ],
        'sales_comparison': {
          'my_sales': 65000000.0,
          'team_average': 52000000.0,
          'top_performer': 95000000.0,
        },
        'collection_comparison': {
          'my_collections': 42000000.0,
          'team_average': 38000000.0,
          'top_collector': 68000000.0,
        },
        'activity': {
          'visits': 18,
          'calls': 45,
          'follow_ups': 32,
        },
        'top_performers': [
          {
            'name': 'أحمد محمد',
            'sales': 95000000.0,
            'collections': 68000000.0,
            'is_current_user': false,
          },
          {
            'name': 'فاطمة علي',
            'sales': 88000000.0,
            'collections': 65000000.0,
            'is_current_user': false,
          },
          {
            'name': 'محمد حسن',
            'sales': 82000000.0,
            'collections': 58000000.0,
            'is_current_user': false,
          },
          {
            'name': 'أنت',
            'sales': 65000000.0,
            'collections': 42000000.0,
            'is_current_user': true,
          },
          {
            'name': 'علي كريم',
            'sales': 58000000.0,
            'collections': 45000000.0,
            'is_current_user': false,
          },
        ],
      };
      notifyListeners();
    } catch (e) {
      _setError(e.toString());
    } finally {
      _setLoading(false);
    }
  }
}
