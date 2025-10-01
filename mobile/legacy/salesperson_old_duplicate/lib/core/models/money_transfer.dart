import 'package:equatable/equatable.dart';

// Money Transfer Model - Core business entity
class MoneyTransfer extends Equatable {
  final int? id;
  final String transferUuid;
  final int salespersonId;
  final String salespersonName;
  final double amountUsd;
  final double amountIqd;
  final double exchangeRate;
  final double grossSales;
  final double commissionRate;
  final double calculatedCommission;
  final double claimedCommission;
  final bool commissionVerified;
  final String transferPlatform;
  final String? platformReference;
  final double transferFee;
  final DateTime transferDateTime;
  final double? gpsLatitude;
  final double? gpsLongitude;
  final String? locationName;
  final String? receiptPhotoUrl;
  final bool receiptVerified;
  final TransferStatus status;
  final bool moneyReceived;
  final DateTime? receivedDateTime;
  final bool isSuspicious;
  final String? fraudAlertReason;
  final bool managerApprovalRequired;
  final DateTime createdAt;
  final DateTime updatedAt;

  const MoneyTransfer({
    this.id,
    required this.transferUuid,
    required this.salespersonId,
    required this.salespersonName,
    required this.amountUsd,
    required this.amountIqd,
    required this.exchangeRate,
    required this.grossSales,
    this.commissionRate = 2.25,
    required this.calculatedCommission,
    required this.claimedCommission,
    this.commissionVerified = false,
    required this.transferPlatform,
    this.platformReference,
    this.transferFee = 0.0,
    required this.transferDateTime,
    this.gpsLatitude,
    this.gpsLongitude,
    this.locationName,
    this.receiptPhotoUrl,
    this.receiptVerified = false,
    this.status = TransferStatus.pending,
    this.moneyReceived = false,
    this.receivedDateTime,
    this.isSuspicious = false,
    this.fraudAlertReason,
    this.managerApprovalRequired = false,
    required this.createdAt,
    required this.updatedAt,
  });

  factory MoneyTransfer.fromJson(Map<String, dynamic> json) {
    return MoneyTransfer(
      id: json['id'],
      transferUuid: json['transfer_uuid'],
      salespersonId: json['salesperson_id'],
      salespersonName: json['salesperson_name'],
      amountUsd: (json['amount_usd'] as num).toDouble(),
      amountIqd: (json['amount_iqd'] as num).toDouble(),
      exchangeRate: (json['exchange_rate'] as num).toDouble(),
      grossSales: (json['gross_sales'] as num).toDouble(),
      commissionRate: (json['commission_rate'] as num).toDouble(),
      calculatedCommission: (json['calculated_commission'] as num).toDouble(),
      claimedCommission: (json['claimed_commission'] as num).toDouble(),
      commissionVerified: json['commission_verified'] ?? false,
      transferPlatform: json['transfer_platform'],
      platformReference: json['platform_reference'],
      transferFee: (json['transfer_fee'] as num?)?.toDouble() ?? 0.0,
      transferDateTime: DateTime.parse(json['transfer_datetime']),
      gpsLatitude: json['gps_latitude']?.toDouble(),
      gpsLongitude: json['gps_longitude']?.toDouble(),
      locationName: json['location_name'],
      receiptPhotoUrl: json['receipt_photo_url'],
      receiptVerified: json['receipt_verified'] ?? false,
      status: TransferStatus.fromString(json['status'] ?? 'pending'),
      moneyReceived: json['money_received'] ?? false,
      receivedDateTime: json['received_datetime'] != null 
          ? DateTime.parse(json['received_datetime']) 
          : null,
      isSuspicious: json['is_suspicious'] ?? false,
      fraudAlertReason: json['fraud_alert_reason'],
      managerApprovalRequired: json['manager_approval_required'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'transfer_uuid': transferUuid,
      'salesperson_id': salespersonId,
      'salesperson_name': salespersonName,
      'amount_usd': amountUsd,
      'amount_iqd': amountIqd,
      'exchange_rate': exchangeRate,
      'gross_sales': grossSales,
      'commission_rate': commissionRate,
      'calculated_commission': calculatedCommission,
      'claimed_commission': claimedCommission,
      'commission_verified': commissionVerified,
      'transfer_platform': transferPlatform,
      'platform_reference': platformReference,
      'transfer_fee': transferFee,
      'transfer_datetime': transferDateTime.toIso8601String(),
      'gps_latitude': gpsLatitude,
      'gps_longitude': gpsLongitude,
      'location_name': locationName,
      'receipt_photo_url': receiptPhotoUrl,
      'receipt_verified': receiptVerified,
      'status': status.value,
      'money_received': moneyReceived,
      'received_datetime': receivedDateTime?.toIso8601String(),
      'is_suspicious': isSuspicious,
      'fraud_alert_reason': fraudAlertReason,
      'manager_approval_required': managerApprovalRequired,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  // Calculate commission discrepancy
  double get commissionDiscrepancy => claimedCommission - calculatedCommission;
  
  // Check if commission is accurate
  bool get isCommissionAccurate => commissionDiscrepancy.abs() < 0.01;
  
  // Get status color for UI
  String get statusColor {
    switch (status) {
      case TransferStatus.pending:
        return '#FF9800'; // Orange
      case TransferStatus.verified:
        return '#4CAF50'; // Green
      case TransferStatus.rejected:
        return '#F44336'; // Red
      case TransferStatus.investigating:
        return '#FF5722'; // Deep Orange
    }
  }

  @override
  List<Object?> get props => [
        id,
        transferUuid,
        salespersonId,
        salespersonName,
        amountUsd,
        amountIqd,
        exchangeRate,
        grossSales,
        commissionRate,
        calculatedCommission,
        claimedCommission,
        commissionVerified,
        transferPlatform,
        platformReference,
        transferFee,
        transferDateTime,
        gpsLatitude,
        gpsLongitude,
        locationName,
        receiptPhotoUrl,
        receiptVerified,
        status,
        moneyReceived,
        receivedDateTime,
        isSuspicious,
        fraudAlertReason,
        managerApprovalRequired,
        createdAt,
        updatedAt,
      ];
}

// Transfer Status Enum
enum TransferStatus {
  pending('pending'),
  verified('verified'),
  rejected('rejected'),
  investigating('investigating');

  const TransferStatus(this.value);
  final String value;

  static TransferStatus fromString(String value) {
    switch (value.toLowerCase()) {
      case 'pending':
        return TransferStatus.pending;
      case 'verified':
        return TransferStatus.verified;
      case 'rejected':
        return TransferStatus.rejected;
      case 'investigating':
        return TransferStatus.investigating;
      default:
        return TransferStatus.pending;
    }
  }

  String get displayName {
    switch (this) {
      case TransferStatus.pending:
        return 'Pending';
      case TransferStatus.verified:
        return 'Verified';
      case TransferStatus.rejected:
        return 'Rejected';
      case TransferStatus.investigating:
        return 'Under Investigation';
    }
  }

  String get displayNameArabic {
    switch (this) {
      case TransferStatus.pending:
        return 'قيد الانتظار';
      case TransferStatus.verified:
        return 'تم التحقق';
      case TransferStatus.rejected:
        return 'مرفوض';
      case TransferStatus.investigating:
        return 'قيد التحقيق';
    }
  }
}

// Transfer Platform Enum
enum TransferPlatform {
  zainCash('ZAIN_CASH'),
  superQi('SUPER_QI'),
  altaif('ALTAIF'),
  cash('CASH');

  const TransferPlatform(this.value);
  final String value;

  static TransferPlatform fromString(String value) {
    switch (value.toUpperCase()) {
      case 'ZAIN_CASH':
        return TransferPlatform.zainCash;
      case 'SUPER_QI':
        return TransferPlatform.superQi;
      case 'ALTAIF':
        return TransferPlatform.altaif;
      case 'CASH':
        return TransferPlatform.cash;
      default:
        return TransferPlatform.zainCash;
    }
  }

  String get displayName {
    switch (this) {
      case TransferPlatform.zainCash:
        return 'ZAIN Cash';
      case TransferPlatform.superQi:
        return 'SuperQi';
      case TransferPlatform.altaif:
        return 'ALTaif Bank';
      case TransferPlatform.cash:
        return 'Cash';
    }
  }

  String get displayNameArabic {
    switch (this) {
      case TransferPlatform.zainCash:
        return 'زين كاش';
      case TransferPlatform.superQi:
        return 'سوبر كي';
      case TransferPlatform.altaif:
        return 'بنك الطائف';
      case TransferPlatform.cash:
        return 'نقد';
    }
  }
}

// Money Transfer Creation Request
class MoneyTransferCreateRequest extends Equatable {
  final double amountUsd;
  final double amountIqd;
  final double exchangeRate;
  final double grossSales;
  final double claimedCommission;
  final String transferPlatform;
  final String? platformReference;
  final double transferFee;
  final double? gpsLatitude;
  final double? gpsLongitude;
  final String? locationName;
  final String? receiptPhotoUrl;

  const MoneyTransferCreateRequest({
    required this.amountUsd,
    required this.amountIqd,
    required this.exchangeRate,
    required this.grossSales,
    required this.claimedCommission,
    required this.transferPlatform,
    this.platformReference,
    this.transferFee = 0.0,
    this.gpsLatitude,
    this.gpsLongitude,
    this.locationName,
    this.receiptPhotoUrl,
  });

  Map<String, dynamic> toJson() {
    return {
      'amount_usd': amountUsd,
      'amount_iqd': amountIqd,
      'exchange_rate': exchangeRate,
      'gross_sales': grossSales,
      'claimed_commission': claimedCommission,
      'transfer_platform': transferPlatform,
      'platform_reference': platformReference,
      'transfer_fee': transferFee,
      'gps_latitude': gpsLatitude,
      'gps_longitude': gpsLongitude,
      'location_name': locationName,
      'receipt_photo_url': receiptPhotoUrl,
    };
  }

  @override
  List<Object?> get props => [
        amountUsd,
        amountIqd,
        exchangeRate,
        grossSales,
        claimedCommission,
        transferPlatform,
        platformReference,
        transferFee,
        gpsLatitude,
        gpsLongitude,
        locationName,
        receiptPhotoUrl,
      ];
}

// Fraud Alert Model
class FraudAlert extends Equatable {
  final int id;
  final int transferId;
  final String salespersonName;
  final String alertType;
  final String alertMessage;
  final String alertMessageArabic;
  final double riskLevel;
  final DateTime alertDateTime;
  final bool isResolved;
  final String? resolutionNotes;

  const FraudAlert({
    required this.id,
    required this.transferId,
    required this.salespersonName,
    required this.alertType,
    required this.alertMessage,
    required this.alertMessageArabic,
    required this.riskLevel,
    required this.alertDateTime,
    this.isResolved = false,
    this.resolutionNotes,
  });

  factory FraudAlert.fromJson(Map<String, dynamic> json) {
    return FraudAlert(
      id: json['id'],
      transferId: json['transfer_id'],
      salespersonName: json['salesperson_name'],
      alertType: json['alert_type'],
      alertMessage: json['alert_message'],
      alertMessageArabic: json['alert_message_arabic'],
      riskLevel: (json['risk_level'] as num).toDouble(),
      alertDateTime: DateTime.parse(json['alert_datetime']),
      isResolved: json['is_resolved'] ?? false,
      resolutionNotes: json['resolution_notes'],
    );
  }

  String get riskLevelText {
    if (riskLevel >= 0.8) return 'High Risk';
    if (riskLevel >= 0.5) return 'Medium Risk';
    return 'Low Risk';
  }

  String get riskLevelTextArabic {
    if (riskLevel >= 0.8) return 'خطر عالي';
    if (riskLevel >= 0.5) return 'خطر متوسط';
    return 'خطر منخفض';
  }

  @override
  List<Object?> get props => [
        id,
        transferId,
        salespersonName,
        alertType,
        alertMessage,
        alertMessageArabic,
        riskLevel,
        alertDateTime,
        isResolved,
        resolutionNotes,
      ];
}

// Dashboard Statistics Model
class MoneyTransferDashboard extends Equatable {
  final double totalAmountUsd;
  final double totalAmountIqd;
  final double totalCommissions;
  final int totalTransfers;
  final int pendingTransfers;
  final int verifiedTransfers;
  final int suspiciousTransfers;
  final double averageExchangeRate;
  final List<FraudAlert> recentAlerts;

  const MoneyTransferDashboard({
    required this.totalAmountUsd,
    required this.totalAmountIqd,
    required this.totalCommissions,
    required this.totalTransfers,
    required this.pendingTransfers,
    required this.verifiedTransfers,
    required this.suspiciousTransfers,
    required this.averageExchangeRate,
    required this.recentAlerts,
  });

  factory MoneyTransferDashboard.fromJson(Map<String, dynamic> json) {
    return MoneyTransferDashboard(
      totalAmountUsd: (json['total_amount_usd'] as num).toDouble(),
      totalAmountIqd: (json['total_amount_iqd'] as num).toDouble(),
      totalCommissions: (json['total_commissions'] as num).toDouble(),
      totalTransfers: json['total_transfers'],
      pendingTransfers: json['pending_transfers'],
      verifiedTransfers: json['verified_transfers'],
      suspiciousTransfers: json['suspicious_transfers'],
      averageExchangeRate: (json['average_exchange_rate'] as num).toDouble(),
      recentAlerts: (json['recent_alerts'] as List)
          .map((alert) => FraudAlert.fromJson(alert))
          .toList(),
    );
  }

  @override
  List<Object?> get props => [
        totalAmountUsd,
        totalAmountIqd,
        totalCommissions,
        totalTransfers,
        pendingTransfers,
        verifiedTransfers,
        suspiciousTransfers,
        averageExchangeRate,
        recentAlerts,
      ];
} 