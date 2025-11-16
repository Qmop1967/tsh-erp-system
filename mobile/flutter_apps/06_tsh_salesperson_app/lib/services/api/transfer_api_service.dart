import '../../models/transfers/money_transfer.dart';
import 'api_client.dart';

/// Money Transfer API Service
/// Handles all money transfer-related backend communication
class TransferApiService {
  final ApiClient _apiClient = ApiClient();

  /// BFF endpoint prefix for salesperson transfer operations
  static const String _bffPrefix = '/bff/salesperson/transfers';

  /// Create new money transfer
  /// Endpoint: POST /api/bff/salesperson/transfers/create
  Future<Map<String, dynamic>> createTransfer(MoneyTransfer transfer) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/create',
        body: transfer.toJson(),
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'transfer_id': response.data['transfer_id'],
          'reference_number': response.data['reference_number'],
          'status': response.data['status'],
          'message': response.data['message'],
        };
      }

      return {
        'success': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error creating transfer: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Upload receipt photo
  /// Endpoint: POST /api/bff/salesperson/transfers/{transferId}/receipt
  Future<Map<String, dynamic>> uploadReceipt({
    required int transferId,
    required String photoPath,
  }) async {
    try {
      final response = await _apiClient.uploadFile(
        '$_bffPrefix/$transferId/receipt',
        filePath: photoPath,
        fieldName: 'receipt_photo',
        additionalFields: {
          'transfer_id': transferId,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'photo_url': response.data['photo_url'],
          'uploaded_at': response.data['uploaded_at'],
        };
      }

      return {
        'success': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error uploading receipt: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Get transfer list
  /// Endpoint: GET /api/bff/salesperson/transfers/list
  Future<List<MoneyTransfer>> getTransferList({
    required int salespersonId,
    String? status,
    String? method,
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
      if (method != null) queryParams['method'] = method;
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String().split('T')[0];
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String().split('T')[0];
      }
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;

      final response = await _apiClient.get(
        '$_bffPrefix/list',
        queryParameters: queryParams,
      );

      if (response.isSuccess && response.data != null) {
        final List<dynamic> transfersJson = response.data['transfers'] ?? [];
        return transfersJson
            .map((json) => MoneyTransfer.fromJson(json))
            .toList();
      }

      return [];
    } catch (e) {
      print('Error getting transfer list: $e');
      return [];
    }
  }

  /// Get transfer details
  /// Endpoint: GET /api/bff/salesperson/transfers/{transferId}
  Future<MoneyTransfer?> getTransferDetails(int transferId) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/$transferId',
      );

      if (response.isSuccess && response.data != null) {
        return MoneyTransfer.fromJson(response.data);
      }

      return null;
    } catch (e) {
      print('Error getting transfer details: $e');
      return null;
    }
  }

  /// Update transfer status (verification)
  /// Endpoint: PUT /api/bff/salesperson/transfers/{transferId}/verify
  Future<Map<String, dynamic>> updateTransferStatus({
    required int transferId,
    required String status,
    String? notes,
    int? verifiedBy,
  }) async {
    try {
      final response = await _apiClient.put(
        '$_bffPrefix/$transferId/verify',
        body: {
          'status': status,
          if (notes != null) 'notes': notes,
          if (verifiedBy != null) 'verified_by': verifiedBy,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'new_status': response.data['status'],
          'verified_at': response.data['verified_at'],
          'verified_by': response.data['verified_by'],
        };
      }

      return {
        'success': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error updating transfer status: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Get cash box balance
  /// Endpoint: GET /api/bff/salesperson/transfers/balance
  Future<CashBoxBalance?> getCashBoxBalance({
    required int salespersonId,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/balance',
        queryParameters: {
          'salesperson_id': salespersonId,
        },
      );

      if (response.isSuccess && response.data != null) {
        return CashBoxBalance.fromJson(response.data);
      }

      return null;
    } catch (e) {
      print('Error getting cash box balance: $e');
      return null;
    }
  }

  /// Get daily transfer summary
  /// Endpoint: GET /api/bff/salesperson/transfers/summary/daily
  Future<DailyTransferSummary?> getDailySummary({
    required int salespersonId,
    required DateTime date,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/summary/daily',
        queryParameters: {
          'salesperson_id': salespersonId,
          'date': date.toIso8601String().split('T')[0],
        },
      );

      if (response.isSuccess && response.data != null) {
        return DailyTransferSummary.fromJson(response.data);
      }

      return null;
    } catch (e) {
      print('Error getting daily summary: $e');
      return null;
    }
  }

  /// Get weekly transfer summary
  /// Endpoint: GET /api/bff/salesperson/transfers/summary/weekly
  Future<Map<String, dynamic>?> getWeeklySummary({
    required int salespersonId,
    required DateTime weekStart,
  }) async {
    try {
      final response = await _apiClient.get(
        '$_bffPrefix/summary/weekly',
        queryParameters: {
          'salesperson_id': salespersonId,
          'week_start': weekStart.toIso8601String().split('T')[0],
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'totalAmount': response.data['total_amount'] ?? 0.0,
          'totalTransfers': response.data['total_transfers'] ?? 0,
          'dailyBreakdown': response.data['daily_breakdown'] ?? [],
          'methodBreakdown': response.data['method_breakdown'] ?? {},
          'statusBreakdown': response.data['status_breakdown'] ?? {},
        };
      }

      return null;
    } catch (e) {
      print('Error getting weekly summary: $e');
      return null;
    }
  }

  /// Batch sync offline transfers
  /// Endpoint: POST /api/bff/salesperson/transfers/sync
  Future<Map<String, dynamic>> batchSyncTransfers(
    List<MoneyTransfer> transfers,
  ) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/sync',
        body: {
          'transfers': transfers.map((t) => t.toJson()).toList(),
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'synced': response.data['synced'] ?? 0,
          'failed': response.data['failed'] ?? 0,
          'errors': response.data['errors'] ?? [],
          'transfer_ids': response.data['transfer_ids'] ?? [],
        };
      }

      return {
        'success': false,
        'synced': 0,
        'failed': transfers.length,
        'error': response.error,
      };
    } catch (e) {
      print('Error batch syncing transfers: $e');
      return {
        'success': false,
        'synced': 0,
        'failed': transfers.length,
        'error': e.toString(),
      };
    }
  }

  /// Send WhatsApp verification (future enhancement)
  /// Endpoint: POST /api/bff/salesperson/transfers/{transferId}/whatsapp
  Future<Map<String, dynamic>> sendWhatsAppVerification({
    required int transferId,
    required String recipientPhone,
  }) async {
    try {
      final response = await _apiClient.post(
        '$_bffPrefix/$transferId/whatsapp',
        body: {
          'recipient_phone': recipientPhone,
        },
      );

      if (response.isSuccess && response.data != null) {
        return {
          'success': true,
          'message_id': response.data['message_id'],
          'sent_at': response.data['sent_at'],
          'status': response.data['status'],
        };
      }

      return {
        'success': false,
        'error': response.error,
      };
    } catch (e) {
      print('Error sending WhatsApp verification: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  /// Cancel transfer
  /// Endpoint: PUT /api/bff/salesperson/transfers/{transferId}/cancel
  Future<bool> cancelTransfer({
    required int transferId,
    String? reason,
  }) async {
    try {
      final response = await _apiClient.put(
        '$_bffPrefix/$transferId/cancel',
        body: {
          if (reason != null) 'reason': reason,
        },
      );

      return response.isSuccess;
    } catch (e) {
      print('Error cancelling transfer: $e');
      return false;
    }
  }

  /// Get sync status
  /// Endpoint: GET /api/bff/salesperson/transfers/sync-status
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
          'failedCount': response.data['failed_count'] ?? 0,
        };
      }

      return null;
    } catch (e) {
      print('Error getting sync status: $e');
      return null;
    }
  }
}
