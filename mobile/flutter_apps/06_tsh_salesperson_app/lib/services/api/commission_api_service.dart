import '../../models/commission/commission.dart';
import 'api_client.dart';

/// Commission API Service
/// Handles all commission-related backend communication
class CommissionApiService {
  final ApiClient _apiClient = ApiClient();

  /// BFF endpoint prefix for salesperson commission operations
  static const String _bffPrefix = '/bff/salesperson/commissions';

  /// Get commission summary
  /// Endpoint: GET /api/bff/salesperson/commissions/summary
  Future<CommissionSummary?> getCommissionSummary({
    required int salespersonId,
    String period = 'month', // today, week, month, all
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/summary',
        queryParameters: {
          'salesperson_id': salespersonId,
          'period': period,
        },
      );

      if (response.isSuccess && response.data != null) {
        return CommissionSummary.fromJson(response.data);
      }

      return null;
    } catch (e) {
      print('Error getting commission summary: $e');
      return null;
    }
  }

  /// Get commission history
  /// Endpoint: GET /api/bff/salesperson/commissions/history
  Future<List<Commission>> getCommissionHistory({
    required int salespersonId,
    String? status,
    String? period,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
    int? offset,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'salesperson_id': salespersonId,
      };

      if (status != null) queryParams['status'] = status;
      if (period != null) queryParams['period'] = period;
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String().split('T')[0];
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String().split('T')[0];
      }
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;

      final response = await _apiClient.get(
        '$_bffPrefix/history',
        queryParameters: queryParams,
      );

      if (response.isSuccess && response.data != null) {
        final List<dynamic> commissionsJson = response.data['commissions'] ?? [];
        return commissionsJson
            .map((json) => Commission.fromJson(json))
            .toList();
      }

      return [];
    } catch (e) {
      print('Error getting commission history: $e');
      return [];
    }
  }

  /// Get commission details
  /// Endpoint: GET /api/bff/salesperson/commissions/{commissionId}
  Future<Commission?> getCommissionDetails(int commissionId) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/$commissionId',
      );

      if (response.isSuccess && response.data != null) {
        return Commission.fromJson(response.data);
      }

      return null;
    } catch (e) {
      print('Error getting commission details: $e');
      return null;
    }
  }

  /// Calculate commission (preview before creating order)
  /// Endpoint: POST /api/bff/salesperson/commissions/calculate
  Future<Map<String, dynamic>?> calculateCommission({
    required double salesAmount,
    double? customRate,
  }) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/calculate',
        body: {
          'sales_amount': salesAmount,
          if (customRate != null) 'commission_rate': customRate,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'salesAmount': response.data['sales_amount'],
          'commissionRate': response.data['commission_rate'],
          'commissionAmount': response.data['commission_amount'],
          'estimatedPayout': response.data['estimated_payout'],
        };
      }

      return null;
    } catch (e) {
      print('Error calculating commission: $e');
      return null;
    }
  }

  /// Get sales target
  /// Endpoint: GET /api/bff/salesperson/targets
  Future<SalesTarget?> getSalesTarget({
    required int salespersonId,
    String period = 'monthly', // weekly, monthly, quarterly
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/targets',
        queryParameters: {
          'salesperson_id': salespersonId,
          'period': period,
        },
      );

      if (response.isSuccess && response.data != null) {
        return SalesTarget.fromJson(response.data);
      }

      return null;
    } catch (e) {
      print('Error getting sales target: $e');
      return null;
    }
  }

  /// Set sales target
  /// Endpoint: POST /api/bff/salesperson/targets/set
  Future<Map<String, dynamic>> setSalesTarget({
    required int salespersonId,
    required double targetAmount,
    required String period,
  }) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/targets/set',
        body: {
          'salesperson_id': salespersonId,
          'target_amount': targetAmount,
          'period': period,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'target_id': response.data['target_id'],
          'target_amount': response.data['target_amount'],
          'period': response.data['period'],
          'starts_at': response.data['starts_at'],
          'ends_at': response.data['ends_at'],
        };
      }

      return {
        'success': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error setting sales target: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Get leaderboard
  /// Endpoint: GET /api/bff/salesperson/commissions/leaderboard
  Future<List<LeaderboardEntry>> getLeaderboard({
    String period = 'month', // week, month, quarter, year, all
    int limit = 10,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/leaderboard',
        queryParameters: {
          'period': period,
          'limit': limit,
        },
      );

      if (response.isSuccess && response.data != null) {
        final List<dynamic> leaderboardJson = response.data['leaderboard'] ?? [];
        return leaderboardJson
            .map((json) => LeaderboardEntry.fromJson(json))
            .toList();
      }

      return [];
    } catch (e) {
      print('Error getting leaderboard: $e');
      return [];
    }
  }

  /// Get weekly earnings breakdown
  /// Endpoint: GET /api/bff/salesperson/commissions/weekly-earnings
  Future<List<Map<String, dynamic>>> getWeeklyEarnings({
    required int salespersonId,
    required DateTime weekStart,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/weekly-earnings',
        queryParameters: {
          'salesperson_id': salespersonId,
          'week_start': weekStart.toIso8601String().split('T')[0],
        },
      );

      if (response.isSuccess && response.data != null) {
        final List<dynamic> earningsJson = response.data['earnings'] ?? [];
        return earningsJson.map((e) => Map<String, dynamic>.from(e)).toList();
      }

      return [];
    } catch (e) {
      print('Error getting weekly earnings: $e');
      return [];
    }
  }

  /// Update commission status (admin only)
  /// Endpoint: PUT /api/bff/salesperson/commissions/{commissionId}/status
  Future<Map<String, dynamic>> updateCommissionStatus({
    required int commissionId,
    required String status,
    String? notes,
  }) async {
    try {
      final response = await _apiClient.put(
        '$_bffPrefix/$commissionId/status',
        body: {
          'status': status,
          if (notes != null) 'notes': notes,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'new_status': response.data['status'],
          'updated_at': response.data['updated_at'],
        };
      }

      return {
        'success': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error updating commission status: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Mark commission as paid
  /// Endpoint: PUT /api/bff/salesperson/commissions/{commissionId}/mark-paid
  Future<bool> markCommissionAsPaid({
    required int commissionId,
    String? paymentMethod,
    String? transactionRef,
  }) async {
    try {
      final response = await _apiClient.put(
        '$_bffPrefix/$commissionId/mark-paid',
        body: {
          if (paymentMethod != null) 'payment_method': paymentMethod,
          if (transactionRef != null) 'transaction_ref': transactionRef,
        },
      );

      return response.isSuccess;
    } catch (e) {
      print('Error marking commission as paid: $e');
      return false;
    }
  }

  /// Get commission statistics
  /// Endpoint: GET /api/bff/salesperson/commissions/statistics
  Future<Map<String, dynamic>?> getCommissionStatistics({
    required int salespersonId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'salesperson_id': salespersonId,
      };

      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String().split('T')[0];
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String().split('T')[0];
      }

      final response = await _apiClient.get(
        '$_bffPrefix/statistics',
        queryParameters: queryParams,
      );

      if (response.isSuccess && response.data != null) {
        return {
          'totalEarned': response.data['total_earned'] ?? 0.0,
          'totalPending': response.data['total_pending'] ?? 0.0,
          'totalPaid': response.data['total_paid'] ?? 0.0,
          'totalOrders': response.data['total_orders'] ?? 0,
          'averageCommission': response.data['average_commission'] ?? 0.0,
          'highestCommission': response.data['highest_commission'] ?? 0.0,
          'lowestCommission': response.data['lowest_commission'] ?? 0.0,
          'commissionTrend': response.data['commission_trend'] ?? [],
        };
      }

      return null;
    } catch (e) {
      print('Error getting commission statistics: $e');
      return null;
    }
  }

  /// Request commission payout
  /// Endpoint: POST /api/bff/salesperson/commissions/request-payout
  Future<Map<String, dynamic>> requestPayout({
    required int salespersonId,
    required double amount,
    String? notes,
  }) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/request-payout',
        body: {
          'salesperson_id': salespersonId,
          'amount': amount,
          if (notes != null) 'notes': notes,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'request_id': response.data['request_id'],
          'amount': response.data['amount'],
          'status': response.data['status'],
          'requested_at': response.data['requested_at'],
        };
      }

      return {
        'success': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error requesting payout: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Get sync status
  /// Endpoint: GET /api/bff/salesperson/commissions/sync-status
  Future<Map<String, dynamic>?> getSyncStatus({
    required int salespersonId,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/sync-status',
        queryParameters: {
          'salesperson_id': salespersonId,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'lastSyncTime': response.data['last_sync_time'],
          'pendingCount': response.data['pending_count'] ?? 0,
          'syncedCount': response.data['synced_count'] ?? 0,
        };
      }

      return null;
    } catch (e) {
      print('Error getting sync status: $e');
      return null;
    }
  }
}
