import 'dart:io';
import 'package:hive/hive.dart';
import 'package:geolocator/geolocator.dart';
import '../../models/transfers/money_transfer.dart';

/// Money Transfer Service
/// Manages recording, tracking, and syncing of money transfers
/// Critical for $35K USD weekly cash flow management
class TransferService {
  static final TransferService _instance = TransferService._internal();
  factory TransferService() => _instance;
  TransferService._internal();

  Box<Map>? _transferBox;
  Box<Map>? _balanceBox;

  /// Initialize service
  Future<void> initialize() async {
    _transferBox = await Hive.openBox<Map>('money_transfers');
    _balanceBox = await Hive.openBox<Map>('cash_box_balance');
  }

  /// Record new money transfer
  Future<MoneyTransfer> recordTransfer({
    required int salespersonId,
    required String transferMethod,
    required double amount,
    String currency = 'IQD',
    int? customerId,
    String? customerName,
    String? referenceNumber,
    String? senderName,
    String? senderPhone,
    String? receiverName,
    String? receiverPhone,
    String? notes,
    String? receiptPhotoPath,
  }) async {
    if (_transferBox == null) {
      await initialize();
    }

    // Get current location
    Position? position;
    try {
      position = await Geolocator.getCurrentPosition();
    } catch (e) {
      print('Could not get location: $e');
    }

    final now = DateTime.now();
    final transfer = MoneyTransfer(
      salespersonId: salespersonId,
      transferMethod: transferMethod,
      amount: amount,
      currency: currency,
      date: '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}',
      timestamp: now.toIso8601String(),
      customerId: customerId,
      customerName: customerName,
      referenceNumber: referenceNumber,
      senderName: senderName,
      senderPhone: senderPhone,
      receiverName: receiverName,
      receiverPhone: receiverPhone,
      receiptPhotoPath: receiptPhotoPath,
      latitude: position?.latitude,
      longitude: position?.longitude,
      notes: notes,
      status: 'pending',
      isSynced: false,
    );

    // Save to local storage
    final key = '${transfer.salespersonId}_${transfer.timestamp}';
    await _transferBox?.put(key, transfer.toJson());

    // Update cash box balance
    await _updateCashBoxBalance(salespersonId, transferMethod, amount, isAdd: false);

    return transfer;
  }

  /// Get transfer by ID
  Future<MoneyTransfer?> getTransfer(String key) async {
    if (_transferBox == null) {
      await initialize();
    }

    final json = _transferBox?.get(key);
    if (json == null) return null;

    return MoneyTransfer.fromJson(Map<String, dynamic>.from(json));
  }

  /// Get all transfers for a salesperson
  Future<List<MoneyTransfer>> getTransfers(int salespersonId) async {
    if (_transferBox == null) {
      await initialize();
    }

    final transfers = _transferBox?.values
        .map((json) => MoneyTransfer.fromJson(Map<String, dynamic>.from(json)))
        .where((t) => t.salespersonId == salespersonId)
        .toList() ?? [];

    transfers.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return transfers;
  }

  /// Get transfers by date
  Future<List<MoneyTransfer>> getTransfersByDate(
    int salespersonId,
    String date,
  ) async {
    final allTransfers = await getTransfers(salespersonId);
    return allTransfers.where((t) => t.date == date).toList();
  }

  /// Get today's transfer summary
  Future<DailyTransferSummary> getTodaysSummary(int salespersonId) async {
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}';

    return await getDailySummary(salespersonId, todayStr);
  }

  /// Get daily transfer summary
  Future<DailyTransferSummary> getDailySummary(
    int salespersonId,
    String date,
  ) async {
    final transfers = await getTransfersByDate(salespersonId, date);

    if (transfers.isEmpty) {
      return DailyTransferSummary(
        date: date,
        totalTransfers: 0,
        totalAmount: 0.0,
        transfersByMethod: {},
        amountsByMethod: {},
        pendingCount: 0,
        verifiedCount: 0,
        completedCount: 0,
        transfers: [],
      );
    }

    // Calculate totals
    double totalAmount = 0.0;
    final transfersByMethod = <String, int>{};
    final amountsByMethod = <String, double>{};
    int pendingCount = 0;
    int verifiedCount = 0;
    int completedCount = 0;

    for (final transfer in transfers) {
      totalAmount += transfer.amount;

      // Count by method
      transfersByMethod[transfer.transferMethod] =
          (transfersByMethod[transfer.transferMethod] ?? 0) + 1;

      // Sum by method
      amountsByMethod[transfer.transferMethod] =
          (amountsByMethod[transfer.transferMethod] ?? 0.0) + transfer.amount;

      // Count by status
      if (transfer.status == 'pending') pendingCount++;
      if (transfer.status == 'verified') verifiedCount++;
      if (transfer.status == 'completed') completedCount++;
    }

    return DailyTransferSummary(
      date: date,
      totalTransfers: transfers.length,
      totalAmount: totalAmount,
      currency: transfers.first.currency,
      transfersByMethod: transfersByMethod,
      amountsByMethod: amountsByMethod,
      pendingCount: pendingCount,
      verifiedCount: verifiedCount,
      completedCount: completedCount,
      transfers: transfers,
    );
  }

  /// Update transfer status
  Future<void> updateTransferStatus({
    required String transferKey,
    required String status,
    String? verificationNotes,
    String? verifiedBy,
  }) async {
    if (_transferBox == null) {
      await initialize();
    }

    final json = _transferBox?.get(transferKey);
    if (json == null) return;

    final transfer = MoneyTransfer.fromJson(Map<String, dynamic>.from(json));
    final updated = transfer.copyWith(
      status: status,
      verificationNotes: verificationNotes,
      verifiedBy: verifiedBy,
      verifiedAt: status == 'verified' ? DateTime.now().toIso8601String() : null,
      isSynced: false,
    );

    await _transferBox?.put(transferKey, updated.toJson());
  }

  /// Attach receipt photo to transfer
  Future<void> attachReceipt({
    required String transferKey,
    required String photoPath,
  }) async {
    if (_transferBox == null) {
      await initialize();
    }

    final json = _transferBox?.get(transferKey);
    if (json == null) return;

    final transfer = MoneyTransfer.fromJson(Map<String, dynamic>.from(json));
    final updated = transfer.copyWith(
      receiptPhotoPath: photoPath,
      isSynced: false,
    );

    await _transferBox?.put(transferKey, updated.toJson());
  }

  /// Get unsynced transfers
  Future<List<MoneyTransfer>> getUnsyncedTransfers() async {
    if (_transferBox == null) {
      await initialize();
    }

    return _transferBox?.values
        .map((json) => MoneyTransfer.fromJson(Map<String, dynamic>.from(json)))
        .where((t) => !t.isSynced)
        .toList() ?? [];
  }

  /// Mark transfer as synced
  Future<void> markTransferSynced(String transferKey) async {
    if (_transferBox == null) {
      await initialize();
    }

    final json = _transferBox?.get(transferKey);
    if (json == null) return;

    final transfer = MoneyTransfer.fromJson(Map<String, dynamic>.from(json));
    final updated = transfer.copyWith(isSynced: true);

    await _transferBox?.put(transferKey, updated.toJson());
  }

  /// Get cash box balance
  Future<CashBoxBalance> getCashBoxBalance(int salespersonId) async {
    if (_balanceBox == null) {
      await initialize();
    }

    final key = 'balance_$salespersonId';
    final json = _balanceBox?.get(key);

    if (json == null) {
      // Return empty balance
      return CashBoxBalance(
        salespersonId: salespersonId,
        lastUpdated: DateTime.now().toIso8601String(),
      );
    }

    return CashBoxBalance.fromJson(Map<String, dynamic>.from(json));
  }

  /// Update cash box balance
  Future<void> _updateCashBoxBalance(
    int salespersonId,
    String method,
    double amount, {
    bool isAdd = true,
  }) async {
    if (_balanceBox == null) {
      await initialize();
    }

    final balance = await getCashBoxBalance(salespersonId);
    final multiplier = isAdd ? 1.0 : -1.0;

    CashBoxBalance updated;
    switch (method) {
      case 'altaif':
        updated = CashBoxBalance(
          salespersonId: salespersonId,
          cashIQD: balance.cashIQD,
          cashUSD: balance.cashUSD,
          altaifIQD: balance.altaifIQD + (amount * multiplier),
          zainCashIQD: balance.zainCashIQD,
          superQiIQD: balance.superQiIQD,
          lastUpdated: DateTime.now().toIso8601String(),
        );
        break;
      case 'zainCash':
        updated = CashBoxBalance(
          salespersonId: salespersonId,
          cashIQD: balance.cashIQD,
          cashUSD: balance.cashUSD,
          altaifIQD: balance.altaifIQD,
          zainCashIQD: balance.zainCashIQD + (amount * multiplier),
          superQiIQD: balance.superQiIQD,
          lastUpdated: DateTime.now().toIso8601String(),
        );
        break;
      case 'superQi':
        updated = CashBoxBalance(
          salespersonId: salespersonId,
          cashIQD: balance.cashIQD,
          cashUSD: balance.cashUSD,
          altaifIQD: balance.altaifIQD,
          zainCashIQD: balance.zainCashIQD,
          superQiIQD: balance.superQiIQD + (amount * multiplier),
          lastUpdated: DateTime.now().toIso8601String(),
        );
        break;
      case 'cash':
        updated = CashBoxBalance(
          salespersonId: salespersonId,
          cashIQD: balance.cashIQD + (amount * multiplier),
          cashUSD: balance.cashUSD,
          altaifIQD: balance.altaifIQD,
          zainCashIQD: balance.zainCashIQD,
          superQiIQD: balance.superQiIQD,
          lastUpdated: DateTime.now().toIso8601String(),
        );
        break;
      default:
        updated = balance;
    }

    final key = 'balance_$salespersonId';
    await _balanceBox?.put(key, updated.toJson());
  }

  /// Manually set cash box balance (for corrections)
  Future<void> setCashBoxBalance({
    required int salespersonId,
    double? cashIQD,
    double? cashUSD,
    double? altaifIQD,
    double? zainCashIQD,
    double? superQiIQD,
  }) async {
    if (_balanceBox == null) {
      await initialize();
    }

    final balance = await getCashBoxBalance(salespersonId);

    final updated = CashBoxBalance(
      salespersonId: salespersonId,
      cashIQD: cashIQD ?? balance.cashIQD,
      cashUSD: cashUSD ?? balance.cashUSD,
      altaifIQD: altaifIQD ?? balance.altaifIQD,
      zainCashIQD: zainCashIQD ?? balance.zainCashIQD,
      superQiIQD: superQiIQD ?? balance.superQiIQD,
      lastUpdated: DateTime.now().toIso8601String(),
    );

    final key = 'balance_$salespersonId';
    await _balanceBox?.put(key, updated.toJson());
  }

  /// Get weekly summary
  Future<Map<String, dynamic>> getWeeklySummary(int salespersonId) async {
    final today = DateTime.now();
    final weekStart = today.subtract(Duration(days: today.weekday - 1));

    double totalAmount = 0.0;
    int totalTransfers = 0;
    final dailySummaries = <DailyTransferSummary>[];

    for (int i = 0; i < 7; i++) {
      final date = weekStart.add(Duration(days: i));
      final dateStr = '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

      final summary = await getDailySummary(salespersonId, dateStr);
      dailySummaries.add(summary);

      totalAmount += summary.totalAmount;
      totalTransfers += summary.totalTransfers;
    }

    return {
      'totalAmount': totalAmount,
      'totalTransfers': totalTransfers,
      'dailySummaries': dailySummaries,
    };
  }

  /// Dispose resources
  void dispose() {
    _transferBox?.close();
    _balanceBox?.close();
  }
}
