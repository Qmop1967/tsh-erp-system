import 'package:hive_flutter/hive_flutter.dart';
import '../../models/commission/commission.dart';

/// Commission Service
/// Handles commission calculation, tracking, and analytics
///
/// Business Logic:
/// - 2.25% commission on all sales
/// - Daily, weekly, and monthly aggregations
/// - Sales targets tracking
/// - Leaderboard rankings
class CommissionService {
  static const String _commissionsBoxName = 'commissions';
  static const String _targetsBoxName = 'sales_targets';
  static const double _defaultCommissionRate = 2.25;

  Box<Commission>? _commissionsBox;
  Box<SalesTarget>? _targetsBox;

  /// Initialize Hive boxes
  Future<void> initialize() async {
    if (!Hive.isBoxOpen(_commissionsBoxName)) {
      // Register adapters if needed
      _commissionsBox = await Hive.openBox<Commission>(_commissionsBoxName);
    } else {
      _commissionsBox = Hive.box<Commission>(_commissionsBoxName);
    }

    if (!Hive.isBoxOpen(_targetsBoxName)) {
      _targetsBox = await Hive.openBox<SalesTarget>(_targetsBoxName);
    } else {
      _targetsBox = Hive.box<SalesTarget>(_targetsBoxName);
    }
  }

  /// Record a commission from a sale
  Future<Commission> recordCommission({
    required int salespersonId,
    required double salesAmount,
    String currency = 'IQD',
    double? customRate,
    int? orderId,
    String? notes,
  }) async {
    await initialize();

    final rate = customRate ?? _defaultCommissionRate;
    final commissionAmount = Commission.calculateCommission(salesAmount, rate);
    final now = DateTime.now();

    final commission = Commission(
      salespersonId: salespersonId,
      period: 'daily',
      startDate: DateTime(now.year, now.month, now.day).toIso8601String(),
      endDate: DateTime(now.year, now.month, now.day, 23, 59, 59).toIso8601String(),
      totalSalesAmount: salesAmount,
      commissionRate: rate,
      commissionAmount: commissionAmount,
      currency: currency,
      status: 'pending',
      notes: notes,
      ordersCount: 1,
      createdAt: now.toIso8601String(),
    );

    await _commissionsBox!.add(commission);
    return commission;
  }

  /// Get commission summary for a period
  Future<CommissionSummary> getCommissionSummary(
    int salespersonId, {
    String period = 'month',
  }) async {
    await initialize();

    final now = DateTime.now();
    DateTime startDate;

    switch (period) {
      case 'today':
        startDate = DateTime(now.year, now.month, now.day);
        break;
      case 'week':
        startDate = now.subtract(Duration(days: now.weekday - 1));
        startDate = DateTime(startDate.year, startDate.month, startDate.day);
        break;
      case 'month':
        startDate = DateTime(now.year, now.month, 1);
        break;
      case 'all-time':
        startDate = DateTime(2020, 1, 1); // Far past date
        break;
      default:
        startDate = DateTime(now.year, now.month, 1);
    }

    final commissions = _commissionsBox!.values
        .where((c) =>
            c.salespersonId == salespersonId &&
            DateTime.parse(c.createdAt).isAfter(startDate))
        .toList();

    double totalSales = 0;
    double totalCommission = 0;
    double pendingCommission = 0;
    double paidCommission = 0;
    int ordersCount = 0;

    for (var commission in commissions) {
      totalSales += commission.totalSalesAmount;
      totalCommission += commission.commissionAmount;
      ordersCount += commission.ordersCount ?? 0;

      if (commission.status == 'paid') {
        paidCommission += commission.commissionAmount;
      } else if (commission.status == 'pending' || commission.status == 'approved') {
        pendingCommission += commission.commissionAmount;
      }
    }

    return CommissionSummary(
      salespersonId: salespersonId,
      period: period,
      totalSales: totalSales,
      totalCommission: totalCommission,
      pendingCommission: pendingCommission,
      paidCommission: paidCommission,
      ordersCount: ordersCount,
      commissionRate: _defaultCommissionRate,
      lastUpdated: now.toIso8601String(),
    );
  }

  /// Get daily commission breakdown for last N days
  Future<List<DailyCommissionSummary>> getDailyBreakdown(
    int salespersonId, {
    int days = 30,
  }) async {
    await initialize();

    final now = DateTime.now();
    final startDate = now.subtract(Duration(days: days));

    final commissions = _commissionsBox!.values
        .where((c) =>
            c.salespersonId == salespersonId &&
            DateTime.parse(c.createdAt).isAfter(startDate))
        .toList();

    // Group by date
    final Map<String, List<Commission>> groupedByDate = {};
    for (var commission in commissions) {
      final date = DateTime.parse(commission.createdAt);
      final dateKey = DateTime(date.year, date.month, date.day).toIso8601String();

      if (!groupedByDate.containsKey(dateKey)) {
        groupedByDate[dateKey] = [];
      }
      groupedByDate[dateKey]!.add(commission);
    }

    // Create daily summaries
    final List<DailyCommissionSummary> dailySummaries = [];
    for (var entry in groupedByDate.entries) {
      double totalSales = 0;
      double totalCommission = 0;
      int ordersCount = 0;

      for (var commission in entry.value) {
        totalSales += commission.totalSalesAmount;
        totalCommission += commission.commissionAmount;
        ordersCount += commission.ordersCount ?? 0;
      }

      dailySummaries.add(DailyCommissionSummary(
        date: entry.key,
        totalSales: totalSales,
        totalCommission: totalCommission,
        ordersCount: ordersCount,
        commissionRate: _defaultCommissionRate,
      ));
    }

    // Sort by date
    dailySummaries.sort((a, b) => a.date.compareTo(b.date));

    return dailySummaries;
  }

  /// Get weekly commission data
  Future<Map<String, dynamic>> getWeeklyData(int salespersonId) async {
    await initialize();

    final now = DateTime.now();
    final startOfWeek = now.subtract(Duration(days: now.weekday - 1));
    final startDate = DateTime(startOfWeek.year, startOfWeek.month, startOfWeek.day);

    final dailySummaries = await getDailyBreakdown(salespersonId, days: 7);

    // Calculate weekly totals
    double weeklyTotal = 0;
    double weeklyCommission = 0;
    int weeklyOrders = 0;

    for (var summary in dailySummaries) {
      weeklyTotal += summary.totalSales;
      weeklyCommission += summary.totalCommission;
      weeklyOrders += summary.ordersCount;
    }

    return {
      'dailySummaries': dailySummaries,
      'weeklyTotal': weeklyTotal,
      'weeklyCommission': weeklyCommission,
      'weeklyOrders': weeklyOrders,
    };
  }

  /// Get current sales target
  Future<SalesTarget?> getCurrentTarget(int salespersonId) async {
    await initialize();

    final now = DateTime.now();
    final targets = _targetsBox!.values
        .where((t) =>
            t.salespersonId == salespersonId &&
            t.isActive &&
            DateTime.parse(t.startDate).isBefore(now) &&
            DateTime.parse(t.endDate).isAfter(now))
        .toList();

    if (targets.isEmpty) return null;

    // Return the most recent target
    targets.sort((a, b) => b.startDate.compareTo(a.startDate));
    return targets.first;
  }

  /// Create or update sales target
  Future<SalesTarget> setTarget({
    required int salespersonId,
    required double targetAmount,
    required String period,
    String currency = 'IQD',
    String? notes,
  }) async {
    await initialize();

    final now = DateTime.now();
    DateTime startDate;
    DateTime endDate;

    switch (period) {
      case 'weekly':
        startDate = now.subtract(Duration(days: now.weekday - 1));
        startDate = DateTime(startDate.year, startDate.month, startDate.day);
        endDate = startDate.add(const Duration(days: 7));
        break;
      case 'monthly':
        startDate = DateTime(now.year, now.month, 1);
        endDate = DateTime(now.year, now.month + 1, 1);
        break;
      case 'quarterly':
        final quarter = ((now.month - 1) / 3).floor();
        startDate = DateTime(now.year, quarter * 3 + 1, 1);
        endDate = DateTime(now.year, quarter * 3 + 4, 1);
        break;
      default:
        startDate = DateTime(now.year, now.month, 1);
        endDate = DateTime(now.year, now.month + 1, 1);
    }

    // Get current sales for this period
    final summary = await getCommissionSummary(salespersonId, period: period);

    final target = SalesTarget(
      salespersonId: salespersonId,
      period: period,
      startDate: startDate.toIso8601String(),
      endDate: endDate.toIso8601String(),
      targetAmount: targetAmount,
      currentAmount: summary.totalSales,
      currency: currency,
      notes: notes,
      isActive: true,
    );

    await _targetsBox!.add(target);
    return target;
  }

  /// Get leaderboard for a period
  Future<List<LeaderboardEntry>> getLeaderboard({
    String period = 'month',
    int limit = 10,
  }) async {
    await initialize();

    final now = DateTime.now();
    DateTime startDate;

    switch (period) {
      case 'week':
        startDate = now.subtract(Duration(days: now.weekday - 1));
        startDate = DateTime(startDate.year, startDate.month, startDate.day);
        break;
      case 'month':
        startDate = DateTime(now.year, now.month, 1);
        break;
      case 'all-time':
        startDate = DateTime(2020, 1, 1);
        break;
      default:
        startDate = DateTime(now.year, now.month, 1);
    }

    // Group commissions by salesperson
    final Map<int, List<Commission>> groupedBySalesperson = {};
    for (var commission in _commissionsBox!.values) {
      if (DateTime.parse(commission.createdAt).isAfter(startDate)) {
        if (!groupedBySalesperson.containsKey(commission.salespersonId)) {
          groupedBySalesperson[commission.salespersonId] = [];
        }
        groupedBySalesperson[commission.salespersonId]!.add(commission);
      }
    }

    // Calculate totals for each salesperson
    final List<Map<String, dynamic>> salespersonData = [];
    for (var entry in groupedBySalesperson.entries) {
      double totalSales = 0;
      double totalCommission = 0;
      int ordersCount = 0;

      for (var commission in entry.value) {
        totalSales += commission.totalSalesAmount;
        totalCommission += commission.commissionAmount;
        ordersCount += commission.ordersCount ?? 0;
      }

      salespersonData.add({
        'salespersonId': entry.key,
        'totalSales': totalSales,
        'totalCommission': totalCommission,
        'ordersCount': ordersCount,
      });
    }

    // Sort by total sales (descending)
    salespersonData.sort((a, b) =>
        (b['totalSales'] as double).compareTo(a['totalSales'] as double));

    // Create leaderboard entries with ranks
    final List<LeaderboardEntry> leaderboard = [];
    for (var i = 0; i < salespersonData.length && i < limit; i++) {
      final data = salespersonData[i];
      leaderboard.add(LeaderboardEntry(
        salespersonId: data['salespersonId'],
        salespersonName: 'مندوب ${data['salespersonId']}', // TODO: Get from user data
        rank: i + 1,
        totalSales: data['totalSales'],
        totalCommission: data['totalCommission'],
        ordersCount: data['ordersCount'],
        period: period,
      ));
    }

    return leaderboard;
  }

  /// Get all commissions for a salesperson
  Future<List<Commission>> getCommissions(
    int salespersonId, {
    String? status,
    int? limit,
  }) async {
    await initialize();

    var commissions = _commissionsBox!.values
        .where((c) => c.salespersonId == salespersonId)
        .toList();

    if (status != null) {
      commissions = commissions.where((c) => c.status == status).toList();
    }

    // Sort by date (newest first)
    commissions.sort((a, b) => b.createdAt.compareTo(a.createdAt));

    if (limit != null && commissions.length > limit) {
      commissions = commissions.take(limit).toList();
    }

    return commissions;
  }

  /// Get unsynced commissions (for backend sync)
  Future<List<Commission>> getUnsyncedCommissions() async {
    await initialize();

    return _commissionsBox!.values
        .where((c) => !c.isSynced)
        .toList();
  }

  /// Calculate commission for quick reference
  double quickCalculateCommission(double salesAmount, {double? customRate}) {
    final rate = customRate ?? _defaultCommissionRate;
    return Commission.calculateCommission(salesAmount, rate);
  }

  /// Get commission rate
  double get commissionRate => _defaultCommissionRate;
}
