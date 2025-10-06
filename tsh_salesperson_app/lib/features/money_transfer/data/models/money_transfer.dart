import '../../core/constants/app_constants.dart';

class MoneyTransfer {
  final String? id;
  final String salespersonId;
  final double amountUSD;
  final double amountIQD;
  final TransferPlatform platform;
  final double commissionRate;
  final double commissionAmount;
  final double claimedCommission;
  final String? receiptPhotoPath;
  final LocationData? location;
  final TransferStatus status;
  final List<FraudAlert>? fraudAlerts;
  final String? notes;
  final DateTime createdAt;
  final DateTime? verifiedAt;
  final String? verifiedBy;

  MoneyTransfer({
    this.id,
    required this.salespersonId,
    required this.amountUSD,
    required this.amountIQD,
    required this.platform,
    this.commissionRate = AppConstants.commissionRate,
    required this.commissionAmount,
    required this.claimedCommission,
    this.receiptPhotoPath,
    this.location,
    this.status = TransferStatus.pending,
    this.fraudAlerts,
    this.notes,
    required this.createdAt,
    this.verifiedAt,
    this.verifiedBy,
  });

  // Calculate commission
  static double calculateCommission(double amount) {
    return amount * (AppConstants.commissionRate / 100);
  }

  // Check if commission matches
  bool isCommissionValid() {
    final calculatedCommission = calculateCommission(amountUSD);
    final difference = (claimedCommission - calculatedCommission).abs();
    return difference < 0.01; // Allow 1 cent difference
  }

  // Check if has fraud alerts
  bool hasFraudAlerts() {
    return fraudAlerts != null && fraudAlerts!.isNotEmpty;
  }

  // Get critical fraud alerts
  List<FraudAlert> getCriticalAlerts() {
    if (fraudAlerts == null) return [];
    return fraudAlerts!
        .where((alert) => alert.severity == AlertSeverity.critical)
        .toList();
  }

  factory MoneyTransfer.fromJson(Map<String, dynamic> json) {
    return MoneyTransfer(
      id: json['id']?.toString(),
      salespersonId: json['salesperson_id']?.toString() ?? '',
      amountUSD: (json['amount_usd'] as num?)?.toDouble() ?? 0.0,
      amountIQD: (json['amount_iqd'] as num?)?.toDouble() ?? 0.0,
      platform: TransferPlatform.fromString(json['platform'] ?? ''),
      commissionRate: (json['commission_rate'] as num?)?.toDouble() ?? AppConstants.commissionRate,
      commissionAmount: (json['commission_amount'] as num?)?.toDouble() ?? 0.0,
      claimedCommission: (json['claimed_commission'] as num?)?.toDouble() ?? 0.0,
      receiptPhotoPath: json['receipt_photo_path'],
      location: json['location'] != null
          ? LocationData.fromJson(json['location'])
          : null,
      status: TransferStatus.fromString(json['status'] ?? ''),
      fraudAlerts: json['fraud_alerts'] != null
          ? (json['fraud_alerts'] as List)
              .map((alert) => FraudAlert.fromJson(alert))
              .toList()
          : null,
      notes: json['notes'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      verifiedAt: json['verified_at'] != null
          ? DateTime.parse(json['verified_at'])
          : null,
      verifiedBy: json['verified_by'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'salesperson_id': salespersonId,
      'amount_usd': amountUSD,
      'amount_iqd': amountIQD,
      'platform': platform.value,
      'commission_rate': commissionRate,
      'commission_amount': commissionAmount,
      'claimed_commission': claimedCommission,
      'receipt_photo_path': receiptPhotoPath,
      'location': location?.toJson(),
      'status': status.value,
      'fraud_alerts': fraudAlerts?.map((alert) => alert.toJson()).toList(),
      'notes': notes,
      'created_at': createdAt.toIso8601String(),
      'verified_at': verifiedAt?.toIso8601String(),
      'verified_by': verifiedBy,
    };
  }
}

// Transfer Platform Enum
enum TransferPlatform {
  zainCash('ZAIN_CASH', 'ZAIN Cash', '🟡'),
  superQi('SUPER_QI', 'SuperQi', '🟣'),
  altaifBank('ALTAIF_BANK', 'ALTaif Bank', '🏦'),
  cash('CASH', 'نقداً', '💵');

  final String value;
  final String displayName;
  final String icon;

  const TransferPlatform(this.value, this.displayName, this.icon);

  static TransferPlatform fromString(String value) {
    return TransferPlatform.values.firstWhere(
      (platform) => platform.value == value,
      orElse: () => TransferPlatform.cash,
    );
  }
}

// Transfer Status Enum
enum TransferStatus {
  pending('PENDING', 'قيد الانتظار', '⏳'),
  verified('VERIFIED', 'تم التحقق', '✅'),
  rejected('REJECTED', 'مرفوض', '❌'),
  investigating('INVESTIGATING', 'قيد التحقيق', '🔍');

  final String value;
  final String displayName;
  final String icon;

  const TransferStatus(this.value, this.displayName, this.icon);

  static TransferStatus fromString(String value) {
    return TransferStatus.values.firstWhere(
      (status) => status.value == value,
      orElse: () => TransferStatus.pending,
    );
  }
}

// Location Data Model
class LocationData {
  final double latitude;
  final double longitude;
  final double? accuracy;
  final String? address;
  final DateTime timestamp;

  LocationData({
    required this.latitude,
    required this.longitude,
    this.accuracy,
    this.address,
    required this.timestamp,
  });

  factory LocationData.fromJson(Map<String, dynamic> json) {
    return LocationData(
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracy: (json['accuracy'] as num?)?.toDouble(),
      address: json['address'],
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
      'accuracy': accuracy,
      'address': address,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

// Fraud Alert Model
class FraudAlert {
  final String id;
  final String type;
  final AlertSeverity severity;
  final String message;
  final String messageAr;
  final DateTime createdAt;

  FraudAlert({
    required this.id,
    required this.type,
    required this.severity,
    required this.message,
    required this.messageAr,
    required this.createdAt,
  });

  factory FraudAlert.fromJson(Map<String, dynamic> json) {
    return FraudAlert(
      id: json['id']?.toString() ?? '',
      type: json['type'] ?? '',
      severity: AlertSeverity.fromString(json['severity'] ?? ''),
      message: json['message'] ?? '',
      messageAr: json['message_ar'] ?? '',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'severity': severity.value,
      'message': message,
      'message_ar': messageAr,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

// Alert Severity Enum
enum AlertSeverity {
  critical('CRITICAL', '🔴'),
  high('HIGH', '🟠'),
  medium('MEDIUM', '🟡'),
  low('LOW', '🟢');

  final String value;
  final String icon;

  const AlertSeverity(this.value, this.icon);

  static AlertSeverity fromString(String value) {
    return AlertSeverity.values.firstWhere(
      (severity) => severity.value == value,
      orElse: () => AlertSeverity.low,
    );
  }
}
