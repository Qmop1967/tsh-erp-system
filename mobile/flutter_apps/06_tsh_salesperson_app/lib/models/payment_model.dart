import 'package:json_annotation/json_annotation.dart';

part 'payment_model.g.dart';

@JsonSerializable()
class Payment {
  final int? id;
  @JsonKey(name: 'payment_number')
  final String? paymentNumber;
  @JsonKey(name: 'customer_id')
  final int? customerId;
  @JsonKey(name: 'customer_name')
  final String? customerName;
  @JsonKey(name: 'order_id')
  final int? orderId;
  @JsonKey(name: 'invoice_id')
  final int? invoiceId;
  @JsonKey(name: 'payment_date')
  final DateTime? paymentDate;
  final double amount;
  @JsonKey(name: 'payment_method')
  final String paymentMethod;
  final String status;
  @JsonKey(name: 'reference_number')
  final String? referenceNumber;
  final String? currency;
  final String? notes;
  @JsonKey(name: 'processed_by')
  final int? processedBy;
  @JsonKey(name: 'processed_by_name')
  final String? processedByName;
  @JsonKey(name: 'bank_account_id')
  final int? bankAccountId;
  @JsonKey(name: 'bank_account_name')
  final String? bankAccountName;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  const Payment({
    this.id,
    this.paymentNumber,
    this.customerId,
    this.customerName,
    this.orderId,
    this.invoiceId,
    this.paymentDate,
    required this.amount,
    required this.paymentMethod,
    this.status = 'pending',
    this.referenceNumber,
    this.currency = 'IQD',
    this.notes,
    this.processedBy,
    this.processedByName,
    this.bankAccountId,
    this.bankAccountName,
    this.createdAt,
    this.updatedAt,
  });

  factory Payment.fromJson(Map<String, dynamic> json) => _$PaymentFromJson(json);

  Map<String, dynamic> toJson() => _$PaymentToJson(this);

  bool get isPending => status == 'pending';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isCancelled => status == 'cancelled';

  bool get isCash => paymentMethod == 'cash';
  bool get isCard => paymentMethod == 'card';
  bool get isTransfer => paymentMethod == 'transfer';
  bool get isCheque => paymentMethod == 'cheque';

  Payment copyWith({
    int? id,
    String? paymentNumber,
    int? customerId,
    String? customerName,
    int? orderId,
    int? invoiceId,
    DateTime? paymentDate,
    double? amount,
    String? paymentMethod,
    String? status,
    String? referenceNumber,
    String? currency,
    String? notes,
    int? processedBy,
    String? processedByName,
    int? bankAccountId,
    String? bankAccountName,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Payment(
      id: id ?? this.id,
      paymentNumber: paymentNumber ?? this.paymentNumber,
      customerId: customerId ?? this.customerId,
      customerName: customerName ?? this.customerName,
      orderId: orderId ?? this.orderId,
      invoiceId: invoiceId ?? this.invoiceId,
      paymentDate: paymentDate ?? this.paymentDate,
      amount: amount ?? this.amount,
      paymentMethod: paymentMethod ?? this.paymentMethod,
      status: status ?? this.status,
      referenceNumber: referenceNumber ?? this.referenceNumber,
      currency: currency ?? this.currency,
      notes: notes ?? this.notes,
      processedBy: processedBy ?? this.processedBy,
      processedByName: processedByName ?? this.processedByName,
      bankAccountId: bankAccountId ?? this.bankAccountId,
      bankAccountName: bankAccountName ?? this.bankAccountName,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Payment(id: $id, amount: $amount, paymentMethod: $paymentMethod, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Payment && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

// Payment Method Options
class PaymentMethods {
  static const String cash = 'cash';
  static const String card = 'card';
  static const String transfer = 'transfer';
  static const String cheque = 'cheque';
  static const String creditCard = 'credit_card';
  static const String debitCard = 'debit_card';

  static const List<String> all = [
    cash,
    card,
    transfer,
    cheque,
    creditCard,
    debitCard,
  ];

  static String getDisplayName(String method) {
    switch (method) {
      case cash:
        return 'Cash';
      case card:
        return 'Card';
      case transfer:
        return 'Bank Transfer';
      case cheque:
        return 'Cheque';
      case creditCard:
        return 'Credit Card';
      case debitCard:
        return 'Debit Card';
      default:
        return method;
    }
  }
}

// Payment Status Options
class PaymentStatus {
  static const String pending = 'pending';
  static const String completed = 'completed';
  static const String failed = 'failed';
  static const String cancelled = 'cancelled';
  static const String refunded = 'refunded';

  static const List<String> all = [
    pending,
    completed,
    failed,
    cancelled,
    refunded,
  ];

  static String getDisplayName(String status) {
    switch (status) {
      case pending:
        return 'Pending';
      case completed:
        return 'Completed';
      case failed:
        return 'Failed';
      case cancelled:
        return 'Cancelled';
      case refunded:
        return 'Refunded';
      default:
        return status;
    }
  }
}
