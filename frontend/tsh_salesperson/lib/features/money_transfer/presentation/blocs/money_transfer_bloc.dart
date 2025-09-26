import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

import '../../../../core/api/api_client.dart';
import '../../../../core/models/money_transfer.dart';
import '../../../gps_tracking/services/gps_service.dart';
import '../../../gps_tracking/models/location_data.dart';

// ==============================================
// 🚨 CRITICAL: MONEY TRANSFER EVENTS
// ==============================================

abstract class MoneyTransferEvent extends Equatable {
  const MoneyTransferEvent();

  @override
  List<Object?> get props => [];
}

class LoadDashboard extends MoneyTransferEvent {}

class LoadTransferHistory extends MoneyTransferEvent {
  final int? limit;
  
  const LoadTransferHistory({this.limit});
  
  @override
  List<Object?> get props => [limit];
}

class SubmitMoneyTransfer extends MoneyTransferEvent {
  final MoneyTransferCreateRequest request;
  
  const SubmitMoneyTransfer(this.request);
  
  @override
  List<Object?> get props => [request];
}

class VerifyCurrentLocation extends MoneyTransferEvent {}

class LoadFraudAlerts extends MoneyTransferEvent {}

class LoadWeeklyCommissionReport extends MoneyTransferEvent {
  final String weekStart;
  
  const LoadWeeklyCommissionReport(this.weekStart);
  
  @override
  List<Object?> get props => [weekStart];
}

class RefreshData extends MoneyTransferEvent {}

class ClearErrors extends MoneyTransferEvent {}

// ==============================================
// 🚨 CRITICAL: MONEY TRANSFER STATES
// ==============================================

abstract class MoneyTransferState extends Equatable {
  const MoneyTransferState();

  @override
  List<Object?> get props => [];
}

class MoneyTransferInitial extends MoneyTransferState {}

class MoneyTransferLoading extends MoneyTransferState {}

class MoneyTransferDashboardLoaded extends MoneyTransferState {
  final MoneyTransferDashboard dashboard;
  final LocationData? currentLocation;
  final bool isLocationVerified;
  
  const MoneyTransferDashboardLoaded({
    required this.dashboard,
    this.currentLocation,
    this.isLocationVerified = false,
  });
  
  @override
  List<Object?> get props => [dashboard, currentLocation, isLocationVerified];
}

class MoneyTransferHistoryLoaded extends MoneyTransferState {
  final List<MoneyTransfer> transfers;
  final bool hasMoreData;
  
  const MoneyTransferHistoryLoaded({
    required this.transfers,
    this.hasMoreData = false,
  });
  
  @override
  List<Object?> get props => [transfers, hasMoreData];
}

class MoneyTransferSubmissionLoading extends MoneyTransferState {}

class MoneyTransferSubmissionSuccess extends MoneyTransferState {
  final MoneyTransfer transfer;
  final String message;
  final String messageArabic;
  
  const MoneyTransferSubmissionSuccess({
    required this.transfer,
    required this.message,
    required this.messageArabic,
  });
  
  @override
  List<Object?> get props => [transfer, message, messageArabic];
}

class LocationVerificationInProgress extends MoneyTransferState {}

class LocationVerificationSuccess extends MoneyTransferState {
  final LocationData location;
  final String verificationMessage;
  final String verificationMessageArabic;
  
  const LocationVerificationSuccess({
    required this.location,
    required this.verificationMessage,
    required this.verificationMessageArabic,
  });
  
  @override
  List<Object?> get props => [location, verificationMessage, verificationMessageArabic];
}

class FraudAlertsLoaded extends MoneyTransferState {
  final List<FraudAlert> alerts;
  final int criticalAlertsCount;
  
  const FraudAlertsLoaded({
    required this.alerts,
    required this.criticalAlertsCount,
  });
  
  @override
  List<Object?> get props => [alerts, criticalAlertsCount];
}

class WeeklyCommissionReportLoaded extends MoneyTransferState {
  final Map<String, dynamic> report; // Will be replaced with proper model
  
  const WeeklyCommissionReportLoaded(this.report);
  
  @override
  List<Object?> get props => [report];
}

class MoneyTransferError extends MoneyTransferState {
  final String message;
  final String messageArabic;
  final String errorCode;
  final bool isCritical;
  
  const MoneyTransferError({
    required this.message,
    required this.messageArabic,
    required this.errorCode,
    this.isCritical = false,
  });
  
  @override
  List<Object?> get props => [message, messageArabic, errorCode, isCritical];
}

// ==============================================
// 🚨 CRITICAL: MONEY TRANSFER BLOC
// ==============================================

class MoneyTransferBloc extends Bloc<MoneyTransferEvent, MoneyTransferState> {
  final ApiClient _apiClient;
  final GPSService _gpsService;
  
  // Cache for performance
  MoneyTransferDashboard? _cachedDashboard;
  List<MoneyTransfer>? _cachedTransfers;
  LocationData? _currentLocation;
  
  MoneyTransferBloc({
    ApiClient? apiClient,
    GPSService? gpsService,
  })  : _apiClient = apiClient ?? ApiClient.instance,
        _gpsService = gpsService ?? GPSService.instance,
        super(MoneyTransferInitial()) {
    
    // Register event handlers
    on<LoadDashboard>(_onLoadDashboard);
    on<LoadTransferHistory>(_onLoadTransferHistory);
    on<SubmitMoneyTransfer>(_onSubmitMoneyTransfer);
    on<VerifyCurrentLocation>(_onVerifyCurrentLocation);
    on<LoadFraudAlerts>(_onLoadFraudAlerts);
    on<LoadWeeklyCommissionReport>(_onLoadWeeklyCommissionReport);
    on<RefreshData>(_onRefreshData);
    on<ClearErrors>(_onClearErrors);
  }

  // ==============================================
  // 📊 LOAD DASHBOARD DATA
  // ==============================================
  
  Future<void> _onLoadDashboard(
    LoadDashboard event,
    Emitter<MoneyTransferState> emit,
  ) async {
    try {
      emit(MoneyTransferLoading());
      
      // Check internet connection
      if (!await _apiClient.hasInternetConnection()) {
        // Load cached data if available
        if (_cachedDashboard != null) {
          emit(MoneyTransferDashboardLoaded(
            dashboard: _cachedDashboard!,
            currentLocation: _currentLocation,
            isLocationVerified: _currentLocation != null,
          ));
          return;
        }
        
        throw ApiException('No internet connection and no cached data available', 'NO_CONNECTION');
      }
      
      // Load dashboard data from API
      final response = await _apiClient.getMoneyTransferDashboard();
      
      if (response.statusCode == 200) {
        final dashboard = MoneyTransferDashboard.fromJson(response.data);
        _cachedDashboard = dashboard;
        
        emit(MoneyTransferDashboardLoaded(
          dashboard: dashboard,
          currentLocation: _currentLocation,
          isLocationVerified: _currentLocation != null,
        ));
      } else {
        throw ApiException(
          'Failed to load dashboard: ${response.statusMessage}',
          'DASHBOARD_LOAD_FAILED'
        );
      }
    } catch (e) {
      print('❌ Dashboard load error: $e');
      
      if (e is ApiException) {
        emit(MoneyTransferError(
          message: e.message,
          messageArabic: _getArabicErrorMessage(e.code),
          errorCode: e.code,
          isCritical: e.code == 'NO_CONNECTION',
        ));
      } else {
        emit(MoneyTransferError(
          message: 'Failed to load dashboard: $e',
          messageArabic: 'فشل في تحميل لوحة القيادة: $e',
          errorCode: 'UNKNOWN_ERROR',
        ));
      }
    }
  }

  // ==============================================
  // 📜 LOAD TRANSFER HISTORY
  // ==============================================
  
  Future<void> _onLoadTransferHistory(
    LoadTransferHistory event,
    Emitter<MoneyTransferState> emit,
  ) async {
    try {
      emit(MoneyTransferLoading());
      
      final response = await _apiClient.getMyTransfers(limit: event.limit ?? 100);
      
      if (response.statusCode == 200) {
        final List<dynamic> transfersJson = response.data;
        final transfers = transfersJson
            .map((json) => MoneyTransfer.fromJson(json))
            .toList();
        
        _cachedTransfers = transfers;
        
        emit(MoneyTransferHistoryLoaded(
          transfers: transfers,
          hasMoreData: transfers.length == (event.limit ?? 100),
        ));
      } else {
        throw ApiException(
          'Failed to load transfer history: ${response.statusMessage}',
          'HISTORY_LOAD_FAILED'
        );
      }
    } catch (e) {
      print('❌ Transfer history load error: $e');
      
      emit(MoneyTransferError(
        message: 'Failed to load transfer history: $e',
        messageArabic: 'فشل في تحميل تاريخ التحويلات: $e',
        errorCode: 'HISTORY_LOAD_ERROR',
      ));
    }
  }

  // ==============================================
  // 🚨 SUBMIT MONEY TRANSFER (CRITICAL FRAUD PREVENTION)
  // ==============================================
  
  Future<void> _onSubmitMoneyTransfer(
    SubmitMoneyTransfer event,
    Emitter<MoneyTransferState> emit,
  ) async {
    try {
      emit(MoneyTransferSubmissionLoading());
      
      // CRITICAL: Verify location before submission
      if (event.request.gpsLatitude == null || event.request.gpsLongitude == null) {
        throw ApiException(
          'GPS location is required for fraud prevention',
          'GPS_REQUIRED'
        );
      }
      
      // Submit transfer to backend
      final response = await _apiClient.submitMoneyTransfer(event.request.toJson());
      
      if (response.statusCode == 201) {
        final transfer = MoneyTransfer.fromJson(response.data);
        
        // Clear cache to force refresh
        _cachedDashboard = null;
        _cachedTransfers = null;
        
        emit(MoneyTransferSubmissionSuccess(
          transfer: transfer,
          message: 'Transfer submitted successfully! Transfer ID: ${transfer.transferUuid}',
          messageArabic: 'تم إرسال التحويل بنجاح! رقم التحويل: ${transfer.transferUuid}',
        ));
        
        // Auto-refresh dashboard after successful submission
        add(LoadDashboard());
      } else {
        throw ApiException(
          'Failed to submit transfer: ${response.statusMessage}',
          'SUBMISSION_FAILED'
        );
      }
    } catch (e) {
      print('❌ Money transfer submission error: $e');
      
      if (e is ApiException) {
        emit(MoneyTransferError(
          message: e.message,
          messageArabic: _getArabicErrorMessage(e.code),
          errorCode: e.code,
          isCritical: true, // Transfer submission errors are always critical
        ));
      } else {
        emit(MoneyTransferError(
          message: 'Failed to submit transfer: $e',
          messageArabic: 'فشل في إرسال التحويل: $e',
          errorCode: 'SUBMISSION_ERROR',
          isCritical: true,
        ));
      }
    }
  }

  // ==============================================
  // 📍 VERIFY CURRENT LOCATION (FRAUD PREVENTION)
  // ==============================================
  
  Future<void> _onVerifyCurrentLocation(
    VerifyCurrentLocation event,
    Emitter<MoneyTransferState> emit,
  ) async {
    try {
      emit(LocationVerificationInProgress());
      
      // Initialize GPS service if not done
      final gpsInitialized = await _gpsService.initialize();
      if (!gpsInitialized) {
        throw GPSException(
          'GPS service initialization failed',
          'GPS_INIT_FAILED'
        );
      }
      
      // Get current location
      final location = await _gpsService.getCurrentLocation();
      _currentLocation = location;
      
      // Verify location for transfer
      final verification = await _gpsService.verifyLocationForTransfer(location);
      
      if (verification.isValid) {
        emit(LocationVerificationSuccess(
          location: location,
          verificationMessage: 'Location verified successfully',
          verificationMessageArabic: 'تم التحقق من الموقع بنجاح',
        ));
      } else {
        emit(MoneyTransferError(
          message: 'Location verification failed: ${verification.reason}',
          messageArabic: 'فشل التحقق من الموقع: ${verification.reasonArabic}',
          errorCode: 'LOCATION_VERIFICATION_FAILED',
          isCritical: verification.riskLevel > 0.7,
        ));
      }
    } catch (e) {
      print('❌ Location verification error: $e');
      
      if (e is GPSException) {
        emit(MoneyTransferError(
          message: e.message,
          messageArabic: _getArabicGPSErrorMessage(e.code),
          errorCode: e.code,
          isCritical: true,
        ));
      } else {
        emit(MoneyTransferError(
          message: 'Location verification failed: $e',
          messageArabic: 'فشل التحقق من الموقع: $e',
          errorCode: 'LOCATION_ERROR',
          isCritical: true,
        ));
      }
    }
  }

  // ==============================================
  // 🚨 LOAD FRAUD ALERTS
  // ==============================================
  
  Future<void> _onLoadFraudAlerts(
    LoadFraudAlerts event,
    Emitter<MoneyTransferState> emit,
  ) async {
    try {
      emit(MoneyTransferLoading());
      
      final response = await _apiClient.getFraudAlerts();
      
      if (response.statusCode == 200) {
        final List<dynamic> alertsJson = response.data;
        final alerts = alertsJson
            .map((json) => FraudAlert.fromJson(json))
            .toList();
        
        final criticalAlertsCount = alerts
            .where((alert) => alert.riskLevel >= 0.8 && !alert.isResolved)
            .length;
        
        emit(FraudAlertsLoaded(
          alerts: alerts,
          criticalAlertsCount: criticalAlertsCount,
        ));
      } else {
        throw ApiException(
          'Failed to load fraud alerts: ${response.statusMessage}',
          'FRAUD_ALERTS_LOAD_FAILED'
        );
      }
    } catch (e) {
      print('❌ Fraud alerts load error: $e');
      
      emit(MoneyTransferError(
        message: 'Failed to load fraud alerts: $e',
        messageArabic: 'فشل في تحميل تنبيهات الاحتيال: $e',
        errorCode: 'FRAUD_ALERTS_ERROR',
        isCritical: true,
      ));
    }
  }

  // ==============================================
  // 📊 LOAD WEEKLY COMMISSION REPORT
  // ==============================================
  
  Future<void> _onLoadWeeklyCommissionReport(
    LoadWeeklyCommissionReport event,
    Emitter<MoneyTransferState> emit,
  ) async {
    try {
      emit(MoneyTransferLoading());
      
      final response = await _apiClient.getWeeklyCommissionReport(event.weekStart);
      
      if (response.statusCode == 200) {
        emit(WeeklyCommissionReportLoaded(response.data));
      } else {
        throw ApiException(
          'Failed to load commission report: ${response.statusMessage}',
          'COMMISSION_REPORT_FAILED'
        );
      }
    } catch (e) {
      print('❌ Commission report load error: $e');
      
      emit(MoneyTransferError(
        message: 'Failed to load commission report: $e',
        messageArabic: 'فشل في تحميل تقرير العمولة: $e',
        errorCode: 'COMMISSION_REPORT_ERROR',
      ));
    }
  }

  // ==============================================
  // 🔄 REFRESH ALL DATA
  // ==============================================
  
  Future<void> _onRefreshData(
    RefreshData event,
    Emitter<MoneyTransferState> emit,
  ) async {
    // Clear cache
    _cachedDashboard = null;
    _cachedTransfers = null;
    
    // Reload dashboard
    add(LoadDashboard());
  }

  // ==============================================
  // 🧹 CLEAR ERRORS
  // ==============================================
  
  Future<void> _onClearErrors(
    ClearErrors event,
    Emitter<MoneyTransferState> emit,
  ) async {
    if (_cachedDashboard != null) {
      emit(MoneyTransferDashboardLoaded(
        dashboard: _cachedDashboard!,
        currentLocation: _currentLocation,
        isLocationVerified: _currentLocation != null,
      ));
    } else {
      emit(MoneyTransferInitial());
    }
  }

  // ==============================================
  // 🌐 ERROR MESSAGE TRANSLATIONS
  // ==============================================
  
  String _getArabicErrorMessage(String errorCode) {
    switch (errorCode) {
      case 'NO_CONNECTION':
        return 'لا يوجد اتصال بالإنترنت';
      case 'TIMEOUT':
        return 'انتهت مهلة الاتصال';
      case 'GPS_REQUIRED':
        return 'موقع GPS مطلوب لمنع الاحتيال';
      case 'SUBMISSION_FAILED':
        return 'فشل في إرسال التحويل';
      case 'LOCATION_VERIFICATION_FAILED':
        return 'فشل التحقق من الموقع';
      case 'FRAUD_ALERTS_ERROR':
        return 'خطأ في تحميل تنبيهات الاحتيال';
      default:
        return 'حدث خطأ غير متوقع';
    }
  }
  
  String _getArabicGPSErrorMessage(String errorCode) {
    switch (errorCode) {
      case 'SERVICE_DISABLED':
        return 'خدمات الموقع معطلة';
      case 'PERMISSION_DENIED':
        return 'تم رفض إذن الموقع';
      case 'PERMISSION_DENIED_FOREVER':
        return 'تم رفض إذن الموقع نهائياً';
      case 'LOCATION_ERROR':
        return 'خطأ في الحصول على الموقع';
      case 'GPS_INIT_FAILED':
        return 'فشل في تهيئة خدمة GPS';
      default:
        return 'خطأ في GPS';
    }
  }

  @override
  Future<void> close() {
    // Cleanup resources if needed
    return super.close();
  }
} 