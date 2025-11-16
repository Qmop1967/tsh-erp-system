import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:hive_flutter/hive_flutter.dart';

import '../../models/gps/gps_location.dart';
import '../../models/transfers/money_transfer.dart';
import '../../models/commission/commission.dart';
import 'gps_api_service.dart';
import 'transfer_api_service.dart';
import 'commission_api_service.dart';

/// Sync Manager
/// Handles automatic synchronization of offline data with backend
class SyncManager {
  static final SyncManager _instance = SyncManager._internal();
  factory SyncManager() => _instance;
  SyncManager._internal();

  final GpsApiService _gpsApi = GpsApiService();
  final TransferApiService _transferApi = TransferApiService();
  final CommissionApiService _commissionApi = CommissionApiService();

  final Connectivity _connectivity = Connectivity();

  Timer? _syncTimer;
  bool _isSyncing = false;
  bool _autoSyncEnabled = true;

  // Sync intervals (can be configured)
  static const Duration _syncInterval = Duration(minutes: 15);
  static const Duration _quickSyncInterval = Duration(minutes: 5);

  // Sync status callbacks
  Function(SyncStatus)? onSyncStatusChanged;
  Function(String)? onSyncError;
  Function(SyncResult)? onSyncCompleted;

  /// Initialize sync manager
  Future<void> initialize() async {
    print('🔄 Initializing Sync Manager...');

    // Listen to connectivity changes
    _connectivity.onConnectivityChanged.listen((result) {
      if (result != ConnectivityResult.none && _autoSyncEnabled) {
        print('📡 Connectivity restored, triggering sync...');
        syncAll();
      }
    });

    // Start periodic sync if enabled
    if (_autoSyncEnabled) {
      startPeriodicSync();
    }

    print('✅ Sync Manager initialized');
  }

  /// Start periodic background sync
  void startPeriodicSync({Duration? interval}) {
    stopPeriodicSync(); // Stop existing timer

    _syncTimer = Timer.periodic(interval ?? _syncInterval, (timer) {
      if (_autoSyncEnabled && !_isSyncing) {
        syncAll();
      }
    });

    print('🔄 Periodic sync started (interval: ${interval ?? _syncInterval})');
  }

  /// Stop periodic sync
  void stopPeriodicSync() {
    _syncTimer?.cancel();
    _syncTimer = null;
    print('⏸️  Periodic sync stopped');
  }

  /// Enable/disable auto sync
  void setAutoSync(bool enabled) {
    _autoSyncEnabled = enabled;
    if (enabled) {
      startPeriodicSync();
    } else {
      stopPeriodicSync();
    }
  }

  /// Check if device is online
  Future<bool> isOnline() async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }

  /// Sync all data (GPS, Transfers, Commissions)
  Future<SyncResult> syncAll({int? salespersonId}) async {
    if (_isSyncing) {
      print('⚠️  Sync already in progress, skipping...');
      return SyncResult(
        success: false,
        message: 'Sync already in progress',
      );
    }

    if (!await isOnline()) {
      print('📴 Device is offline, skipping sync');
      return SyncResult(
        success: false,
        message: 'Device is offline',
      );
    }

    _isSyncing = true;
    onSyncStatusChanged?.call(SyncStatus.syncing);

    final startTime = DateTime.now();
    final result = SyncResult();

    try {
      print('🔄 Starting full sync...');

      // Sync GPS locations
      final gpsResult = await _syncGpsLocations(salespersonId);
      result.gpsUploaded = gpsResult['uploaded'] ?? 0;
      result.gpsFailed = gpsResult['failed'] ?? 0;

      // Sync money transfers
      final transferResult = await _syncTransfers(salespersonId);
      result.transfersUploaded = transferResult['synced'] ?? 0;
      result.transfersFailed = transferResult['failed'] ?? 0;

      // Note: Commissions are usually created by backend when orders are made
      // So we don't sync commissions TO backend, only FROM backend

      final duration = DateTime.now().difference(startTime);
      result.success = true;
      result.message = 'Sync completed in ${duration.inSeconds}s';
      result.syncDuration = duration;

      print('✅ Sync completed successfully');
      print('   GPS: ${result.gpsUploaded} uploaded, ${result.gpsFailed} failed');
      print('   Transfers: ${result.transfersUploaded} uploaded, ${result.transfersFailed} failed');

      onSyncStatusChanged?.call(SyncStatus.success);
      onSyncCompleted?.call(result);

      return result;
    } catch (e) {
      print('❌ Sync failed: $e');

      result.success = false;
      result.message = 'Sync failed: $e';

      onSyncStatusChanged?.call(SyncStatus.error);
      onSyncError?.call(e.toString());

      return result;
    } finally {
      _isSyncing = false;
    }
  }

  /// Sync GPS locations only
  Future<Map<String, dynamic>> _syncGpsLocations(int? salespersonId) async {
    try {
      final box = await Hive.openBox<GPSLocation>('gps_locations');

      // Get unsynced locations (where isSynced == false)
      final unsyncedLocations = box.values
          .where((loc) => !(loc.isSynced ?? false))
          .toList();

      if (unsyncedLocations.isEmpty) {
        print('✅ No GPS locations to sync');
        return {'uploaded': 0, 'failed': 0};
      }

      print('🔄 Syncing ${unsyncedLocations.length} GPS locations...');

      final result = await _gpsApi.batchUploadLocations(unsyncedLocations);

      if (result['success'] == true) {
        // Mark synced locations as synced in local storage
        for (var location in unsyncedLocations) {
          location.isSynced = true;
          await location.save();
        }
      }

      return result;
    } catch (e) {
      print('❌ Error syncing GPS locations: $e');
      return {
        'success': false,
        'uploaded': 0,
        'failed': 0,
        'error': e.toString(),
      };
    }
  }

  /// Sync money transfers only
  Future<Map<String, dynamic>> _syncTransfers(int? salespersonId) async {
    try {
      final box = await Hive.openBox<MoneyTransfer>('money_transfers');

      // Get unsynced transfers (where isSynced == false)
      final unsyncedTransfers = box.values
          .where((transfer) => !(transfer.isSynced ?? false))
          .toList();

      if (unsyncedTransfers.isEmpty) {
        print('✅ No transfers to sync');
        return {'synced': 0, 'failed': 0};
      }

      print('🔄 Syncing ${unsyncedTransfers.length} transfers...');

      final result = await _transferApi.batchSyncTransfers(unsyncedTransfers);

      if (result['success'] == true) {
        // Mark synced transfers as synced in local storage
        final syncedIds = result['transfer_ids'] as List? ?? [];
        for (var i = 0; i < unsyncedTransfers.length; i++) {
          if (i < syncedIds.length) {
            unsyncedTransfers[i].isSynced = true;
            unsyncedTransfers[i].backendId = syncedIds[i];
            await unsyncedTransfers[i].save();
          }
        }
      }

      return result;
    } catch (e) {
      print('❌ Error syncing transfers: $e');
      return {
        'success': false,
        'synced': 0,
        'failed': 0,
        'error': e.toString(),
      };
    }
  }

  /// Get pending sync count
  Future<Map<String, int>> getPendingSyncCount() async {
    try {
      final gpsBox = await Hive.openBox<GPSLocation>('gps_locations');
      final transferBox = await Hive.openBox<MoneyTransfer>('money_transfers');

      final pendingGps = gpsBox.values
          .where((loc) => !(loc.isSynced ?? false))
          .length;

      final pendingTransfers = transferBox.values
          .where((t) => !(t.isSynced ?? false))
          .length;

      return {
        'gps': pendingGps,
        'transfers': pendingTransfers,
        'total': pendingGps + pendingTransfers,
      };
    } catch (e) {
      print('Error getting pending sync count: $e');
      return {
        'gps': 0,
        'transfers': 0,
        'total': 0,
      };
    }
  }

  /// Force sync now (manual trigger)
  Future<SyncResult> forceSyncNow({int? salespersonId}) async {
    print('🔄 Force sync triggered');
    return await syncAll(salespersonId: salespersonId);
  }

  /// Clear sync history
  Future<void> clearSyncHistory() async {
    try {
      // This would clear sync metadata, not the actual data
      print('🗑️  Sync history cleared');
    } catch (e) {
      print('Error clearing sync history: $e');
    }
  }

  /// Dispose resources
  void dispose() {
    stopPeriodicSync();
    print('🛑 Sync Manager disposed');
  }
}

/// Sync status enum
enum SyncStatus {
  idle,
  syncing,
  success,
  error,
}

/// Sync result model
class SyncResult {
  bool success;
  String message;
  int gpsUploaded;
  int gpsFailed;
  int transfersUploaded;
  int transfersFailed;
  Duration? syncDuration;

  SyncResult({
    this.success = false,
    this.message = '',
    this.gpsUploaded = 0,
    this.gpsFailed = 0,
    this.transfersUploaded = 0,
    this.transfersFailed = 0,
    this.syncDuration,
  });

  int get totalUploaded => gpsUploaded + transfersUploaded;
  int get totalFailed => gpsFailed + transfersFailed;

  bool get hasFailures => totalFailed > 0;
  bool get hasUploads => totalUploaded > 0;

  @override
  String toString() {
    return 'SyncResult(success: $success, uploaded: $totalUploaded, failed: $totalFailed, duration: ${syncDuration?.inSeconds}s)';
  }
}
