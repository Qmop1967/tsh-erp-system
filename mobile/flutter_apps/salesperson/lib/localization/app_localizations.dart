import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  static const List<Locale> supportedLocales = [
    Locale('en', 'US'),
    Locale('ar', 'IQ'),
  ];

  late Map<String, String> _localizedStrings;

  Future<bool> load() async {
    String jsonString = await rootBundle.loadString('assets/localization/app_${locale.languageCode}.json');
    Map<String, dynamic> jsonMap = json.decode(jsonString);

    _localizedStrings = jsonMap.map((key, value) {
      return MapEntry(key, value.toString());
    });

    return true;
  }

  String translate(String key) {
    return _localizedStrings[key] ?? key;
  }

  // ==============================================
  // 🚨 CRITICAL: MONEY TRANSFER & FRAUD PREVENTION
  // ==============================================

  String get appTitle => translate('app_title');
  String get moneyTransfer => translate('money_transfer');
  String get submitTransfer => translate('submit_transfer');
  String get transferAmount => translate('transfer_amount');
  String get exchangeRate => translate('exchange_rate');
  String get commission => translate('commission');
  String get fraudAlert => translate('fraud_alert');
  String get fraudPrevention => translate('fraud_prevention');
  String get locationVerification => translate('location_verification');
  String get gpsTracking => translate('gps_tracking');
  String get receiptPhoto => translate('receipt_photo');
  String get transferPlatform => translate('transfer_platform');
  String get zainCash => translate('zain_cash');
  String get superQi => translate('super_qi');
  String get altaifBank => translate('altaif_bank');
  String get cashTransfer => translate('cash_transfer');
  String get platformReference => translate('platform_reference');
  String get transferFee => translate('transfer_fee');
  String get grossSales => translate('gross_sales');
  String get claimedCommission => translate('claimed_commission');
  String get calculatedCommission => translate('calculated_commission');
  String get commissionDiscrepancy => translate('commission_discrepancy');
  String get commissionVerified => translate('commission_verified');
  String get transferStatus => translate('transfer_status');
  String get pending => translate('pending');
  String get verified => translate('verified');
  String get rejected => translate('rejected');
  String get investigating => translate('investigating');
  String get suspicious => translate('suspicious');
  String get managerApprovalRequired => translate('manager_approval_required');

  // ==============================================
  // 📍 GPS & LOCATION TRACKING
  // ==============================================

  String get currentLocation => translate('current_location');
  String get locationAccuracy => translate('location_accuracy');
  String get locationAddress => translate('location_address');
  String get gpsCoordinates => translate('gps_coordinates');
  String get locationServicesDisabled => translate('location_services_disabled');
  String get locationPermissionDenied => translate('location_permission_denied');
  String get enableLocationServices => translate('enable_location_services');
  String get locationVerificationFailed => translate('location_verification_failed');
  String get locationTooInaccurate => translate('location_too_inaccurate');
  String get suspiciousLocationDetected => translate('suspicious_location_detected');
  String get locationVerifiedSuccessfully => translate('location_verified_successfully');

  // ==============================================
  // 🎯 DASHBOARD & ANALYTICS
  // ==============================================

  String get dashboard => translate('dashboard');
  String get welcomeBack => translate('welcome_back');
  String get readyToBoostSales => translate('ready_to_boost_sales');
  String get totalSales => translate('total_sales');
  String get totalTransfers => translate('total_transfers');
  String get pendingTransfers => translate('pending_transfers');
  String get verifiedTransfers => translate('verified_transfers');
  String get suspiciousTransfers => translate('suspicious_transfers');
  String get totalCommissions => translate('total_commissions');
  String get averageExchangeRate => translate('average_exchange_rate');
  String get recentAlerts => translate('recent_alerts');
  String get weeklyReport => translate('weekly_report');
  String get performanceMetrics => translate('performance_metrics');

  // ==============================================
  // 📱 NAVIGATION & UI
  // ==============================================

  String get home => translate('home');
  String get transfers => translate('transfers');
  String get reports => translate('reports');
  String get alerts => translate('alerts');
  String get profile => translate('profile');
  String get customers => translate('customers');
  String get orders => translate('orders');
  String get products => translate('products');
  String get sales => translate('sales');
  String get settings => translate('settings');
  String get help => translate('help');
  String get logout => translate('logout');

  // ==============================================
  // 📝 FORMS & INPUTS
  // ==============================================

  String get amountInUSD => translate('amount_in_usd');
  String get amountInIQD => translate('amount_in_iqd');
  String get enterAmount => translate('enter_amount');
  String get enterExchangeRate => translate('enter_exchange_rate');
  String get enterGrossSales => translate('enter_gross_sales');
  String get enterClaimedCommission => translate('enter_claimed_commission');
  String get enterPlatformReference => translate('enter_platform_reference');
  String get selectPlatform => translate('select_platform');
  String get takeReceiptPhoto => translate('take_receipt_photo');
  String get uploadReceiptPhoto => translate('upload_receipt_photo');
  String get required => translate('required');
  String get optional => translate('optional');
  String get submit => translate('submit');
  String get cancel => translate('cancel');
  String get save => translate('save');
  String get edit => translate('edit');
  String get delete => translate('delete');
  String get confirm => translate('confirm');

  // ==============================================
  // ⚠️ ALERTS & NOTIFICATIONS
  // ==============================================

  String get success => translate('success');
  String get error => translate('error');
  String get warning => translate('warning');
  String get info => translate('info');
  String get criticalAlert => translate('critical_alert');
  String get highRiskTransfer => translate('high_risk_transfer');
  String get mediumRiskTransfer => translate('medium_risk_transfer');
  String get lowRiskTransfer => translate('low_risk_transfer');
  String get immediateAttentionRequired => translate('immediate_attention_required');
  String get transferSubmittedSuccessfully => translate('transfer_submitted_successfully');
  String get transferRejected => translate('transfer_rejected');
  String get commissionMismatch => translate('commission_mismatch');
  String get locationVerificationRequired => translate('location_verification_required');
  String get receiptUploadRequired => translate('receipt_upload_required');
  String get networkError => translate('network_error');
  String get connectionTimeout => translate('connection_timeout');
  String get pleaseCheckInternet => translate('please_check_internet');

  // ==============================================
  // 📊 REPORTS & ANALYTICS
  // ==============================================

  String get dailyReport => translate('daily_report');
  String get weeklyCommissionReport => translate('weekly_commission_report');
  String get monthlyReport => translate('monthly_report');
  String get transferHistory => translate('transfer_history');
  String get commissionHistory => translate('commission_history');
  String get fraudAlertsHistory => translate('fraud_alerts_history');
  String get performanceAnalysis => translate('performance_analysis');
  String get riskAssessment => translate('risk_assessment');
  String get complianceReport => translate('compliance_report');

  // ==============================================
  // 🔐 AUTHENTICATION & SECURITY
  // ==============================================

  String get login => translate('login');
  String get username => translate('username');
  String get password => translate('password');
  String get forgotPassword => translate('forgot_password');
  String get invalidCredentials => translate('invalid_credentials');
  String get sessionExpired => translate('session_expired');
  String get pleaseLoginAgain => translate('please_login_again');
  String get accountLocked => translate('account_locked');
  String get contactManager => translate('contact_manager');

  // ==============================================
  // 📋 GENERAL UI ELEMENTS
  // ==============================================

  String get loading => translate('loading');
  String get pleaseWait => translate('please_wait');
  String get retry => translate('retry');
  String get refresh => translate('refresh');
  String get noData => translate('no_data');
  String get noInternetConnection => translate('no_internet_connection');
  String get dataLoadedSuccessfully => translate('data_loaded_successfully');
  String get operationCompleted => translate('operation_completed');
  String get operationFailed => translate('operation_failed');
  String get yes => translate('yes');
  String get no => translate('no');
  String get ok => translate('ok');
  String get close => translate('close');
  String get back => translate('back');
  String get next => translate('next');
  String get previous => translate('previous');
  String get search => translate('search');
  String get filter => translate('filter');
  String get sort => translate('sort');
  String get viewAll => translate('view_all');
  String get viewDetails => translate('view_details');

  // ==============================================
  // 📅 DATE & TIME
  // ==============================================

  String get today => translate('today');
  String get yesterday => translate('yesterday');
  String get thisWeek => translate('this_week');
  String get lastWeek => translate('last_week');
  String get thisMonth => translate('this_month');
  String get lastMonth => translate('last_month');
  String get date => translate('date');
  String get time => translate('time');
  String get dateTime => translate('date_time');

  // ==============================================
  // 💰 CURRENCY & NUMBERS
  // ==============================================

  String get usd => translate('usd');
  String get iqd => translate('iqd');
  String get currency => translate('currency');
  String get amount => translate('amount');
  String get total => translate('total');
  String get subtotal => translate('subtotal');
  String get fee => translate('fee');
  String get rate => translate('rate');
  String get percentage => translate('percentage');
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'ar'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    AppLocalizations localizations = AppLocalizations(locale);
    await localizations.load();
    return localizations;
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}