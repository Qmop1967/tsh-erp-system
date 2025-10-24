import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/dashboard_stats.dart';
import '../services/dashboard_service.dart';

/// Dashboard Provider - Manages dashboard statistics with auto-refresh
class DashboardProvider extends ChangeNotifier {
  final DashboardService _dashboardService = DashboardService();

  DashboardStats _stats = DashboardStats.empty();
  bool _isLoading = false;
  String? _error;
  Timer? _refreshTimer;

  DashboardStats get stats => _stats;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Initialize dashboard with auto-refresh
  void initialize({Duration refreshInterval = const Duration(seconds: 30)}) {
    print('📊 DashboardProvider: Initializing...');

    // Load initial data
    loadStats();

    // Set up auto-refresh timer
    _refreshTimer = Timer.periodic(refreshInterval, (timer) {
      print('🔄 DashboardProvider: Auto-refreshing stats...');
      loadStats(silent: true);
    });
  }

  /// Load dashboard statistics
  Future<void> loadStats({bool silent = false}) async {
    if (!silent) {
      _isLoading = true;
      _error = null;
      notifyListeners();
    }

    try {
      print('📊 DashboardProvider: Loading stats...');

      // Fetch stats from API
      final stats = await _dashboardService.getDashboardStats();

      _stats = stats;
      _error = null;

      print('✅ DashboardProvider: Stats loaded - Users: ${stats.totalUsers}, Sessions: ${stats.activeSessions}');
    } catch (e) {
      print('❌ DashboardProvider: Error loading stats: $e');
      _error = e.toString();

      // Keep previous stats if available, otherwise use empty
      if (_stats == DashboardStats.empty()) {
        _stats = DashboardStats.empty();
      }
    } finally {
      if (!silent) {
        _isLoading = false;
      }
      notifyListeners();
    }
  }

  /// Manually refresh stats
  Future<void> refresh() async {
    print('🔄 DashboardProvider: Manual refresh triggered');
    await loadStats();
  }

  @override
  void dispose() {
    print('🗑️ DashboardProvider: Disposing and canceling timer');
    _refreshTimer?.cancel();
    super.dispose();
  }
}
