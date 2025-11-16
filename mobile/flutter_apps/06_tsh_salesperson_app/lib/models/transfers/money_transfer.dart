import 'package:json_annotation/json_annotation.dart';

part 'money_transfer.g.dart';

/// Money Transfer Payment Method
enum TransferMethod {
  altaif,    // ALTaif transfer
  zainCash,  // ZAIN Cash
  superQi,   // SuperQi
  cash,      // Physical cash
  bank       // Bank transfer
}

/// Transfer Status
enum TransferStatus {
  pending,        // Recorded but not verified
  verified,       // Verified with receipt
  rejected,       // Receipt rejected
  completed,      // Money received by office
  cancelled       // Cancelled transfer
}

/// Money Transfer Model
/// Critical for tracking $35K USD weekly from 12 travel salespersons
@JsonSerializable()
class MoneyTransfer {
  final int? id;
  final int salespersonId;
  final String transferMethod; // altaif, zainCash, superQi, cash, bank
  final double amount;
  final String currency; // IQD, USD
  final String date;
  final String timestamp;
  final int? customerId;
  final String? customerName;
  final String? referenceNumber; // Transfer reference/transaction ID
  final String? senderName;
  final String? senderPhone;
  final String? receiverName;
  final String? receiverPhone;
  final String? receiptPhotoPath;
  final String? receiptPhotoUrl;
  final String status; // pending, verified, rejected, completed, cancelled
  final String? verificationNotes;
  final String? verifiedBy;
  final String? verifiedAt;
  final double? latitude;
  final double? longitude;
  final String? notes;
  final bool isSynced;

  MoneyTransfer({
    this.id,
    required this.salespersonId,
    required this.transferMethod,
    required this.amount,
    this.currency = 'IQD',
    required this.date,
    required this.timestamp,
    this.customerId,
    this.customerName,
    this.referenceNumber,
    this.senderName,
    this.senderPhone,
    this.receiverName,
    this.receiverPhone,
    this.receiptPhotoPath,
    this.receiptPhotoUrl,
    this.status = 'pending',
    this.verificationNotes,
    this.verifiedBy,
    this.verifiedAt,
    this.latitude,
    this.longitude,
    this.notes,
    this.isSynced = false,
  });

  factory MoneyTransfer.fromJson(Map<String, dynamic> json) =>
      _$MoneyTransferFromJson(json);

  Map<String, dynamic> toJson() => _$MoneyTransferToJson(this);

  MoneyTransfer copyWith({
    int? id,
    int? salespersonId,
    String? transferMethod,
    double? amount,
    String? currency,
    String? date,
    String? timestamp,
    int? customerId,
    String? customerName,
    String? referenceNumber,
    String? senderName,
    String? senderPhone,
    String? receiverName,
    String? receiverPhone,
    String? receiptPhotoPath,
    String? receiptPhotoUrl,
    String? status,
    String? verificationNotes,
    String? verifiedBy,
    String? verifiedAt,
    double? latitude,
    double? longitude,
    String? notes,
    bool? isSynced,
  }) {
    return MoneyTransfer(
      id: id ?? this.id,
      salespersonId: salespersonId ?? this.salespersonId,
      transferMethod: transferMethod ?? this.transferMethod,
      amount: amount ?? this.amount,
      currency: currency ?? this.currency,
      date: date ?? this.date,
      timestamp: timestamp ?? this.timestamp,
      customerId: customerId ?? this.customerId,
      customerName: customerName ?? this.customerName,
      referenceNumber: referenceNumber ?? this.referenceNumber,
      senderName: senderName ?? this.senderName,
      senderPhone: senderPhone ?? this.senderPhone,
      receiverName: receiverName ?? this.receiverName,
      receiverPhone: receiverPhone ?? this.receiverPhone,
      receiptPhotoPath: receiptPhotoPath ?? this.receiptPhotoPath,
      receiptPhotoUrl: receiptPhotoUrl ?? this.receiptPhotoUrl,
      status: status ?? this.status,
      verificationNotes: verificationNotes ?? this.verificationNotes,
      verifiedBy: verifiedBy ?? this.verifiedBy,
      verifiedAt: verifiedAt ?? this.verifiedAt,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      notes: notes ?? this.notes,
      isSynced: isSynced ?? this.isSynced,
    );
  }

  /// Get transfer method display name in Arabic
  String get transferMethodName {
    switch (transferMethod) {
      case 'altaif':
        return 'الطيف';
      case 'zainCash':
        return 'زين كاش';
      case 'superQi':
        return 'سوبر كيو';
      case 'cash':
        return 'نقدي';
      case 'bank':
        return 'تحويل بنكي';
      default:
        return transferMethod;
    }
  }

  /// Get status display name in Arabic
  String get statusName {
    switch (status) {
      case 'pending':
        return 'قيد الانتظار';
      case 'verified':
        return 'تم التحقق';
      case 'rejected':
        return 'مرفوض';
      case 'completed':
        return 'مكتمل';
      case 'cancelled':
        return 'ملغى';
      default:
        return status;
    }
  }

  /// Format amount with currency
  String get formattedAmount {
    if (currency == 'USD') {
      return '\$${amount.toStringAsFixed(2)}';
    } else if (currency == 'IQD') {
      return '${amount.toStringAsFixed(0)} د.ع';
    }
    return '${amount.toStringAsFixed(2)} $currency';
  }
}

/// Daily Transfer Summary
@JsonSerializable()
class DailyTransferSummary {
  final String date;
  final int totalTransfers;
  final double totalAmount;
  final String currency;
  final Map<String, int> transfersByMethod;
  final Map<String, double> amountsByMethod;
  final int pendingCount;
  final int verifiedCount;
  final int completedCount;
  final List<MoneyTransfer> transfers;

  DailyTransferSummary({
    required this.date,
    required this.totalTransfers,
    required this.totalAmount,
    this.currency = 'IQD',
    required this.transfersByMethod,
    required this.amountsByMethod,
    required this.pendingCount,
    required this.verifiedCount,
    required this.completedCount,
    required this.transfers,
  });

  factory DailyTransferSummary.fromJson(Map<String, dynamic> json) =>
      _$DailyTransferSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$DailyTransferSummaryToJson(this);

  /// Format total amount with currency
  String get formattedTotalAmount {
    if (currency == 'USD') {
      return '\$${totalAmount.toStringAsFixed(2)}';
    } else if (currency == 'IQD') {
      return '${totalAmount.toStringAsFixed(0)} د.ع';
    }
    return '${totalAmount.toStringAsFixed(2)} $currency';
  }
}

/// Cash Box Balance
@JsonSerializable()
class CashBoxBalance {
  final int salespersonId;
  final double cashIQD;
  final double cashUSD;
  final double altaifIQD;
  final double zainCashIQD;
  final double superQiIQD;
  final String lastUpdated;

  CashBoxBalance({
    required this.salespersonId,
    this.cashIQD = 0.0,
    this.cashUSD = 0.0,
    this.altaifIQD = 0.0,
    this.zainCashIQD = 0.0,
    this.superQiIQD = 0.0,
    required this.lastUpdated,
  });

  factory CashBoxBalance.fromJson(Map<String, dynamic> json) =>
      _$CashBoxBalanceFromJson(json);

  Map<String, dynamic> toJson() => _$CashBoxBalanceToJson(this);

  /// Total balance in IQD (converting USD to IQD)
  double get totalIQD {
    const double usdToIqdRate = 1500.0; // Example rate, should come from backend
    return cashIQD + (cashUSD * usdToIqdRate) + altaifIQD + zainCashIQD + superQiIQD;
  }

  /// Format total balance
  String get formattedTotal {
    return '${totalIQD.toStringAsFixed(0)} د.ع';
  }
}
