class Payment {
  final String id;
  final double amount;
  final String currency;
  final DateTime paymentDate;
  final String paymentMethod; // bank_transfer, check, cash, credit_card
  final String status; // pending, completed, failed, cancelled
  final String? referenceNumber;
  final String? notes;
  final List<String> invoiceIds;

  Payment({
    required this.id,
    required this.amount,
    required this.currency,
    required this.paymentDate,
    required this.paymentMethod,
    required this.status,
    this.referenceNumber,
    this.notes,
    this.invoiceIds = const [],
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'].toString(),
      amount: (json['amount'] ?? 0.0).toDouble(),
      currency: json['currency'] ?? 'IQD',
      paymentDate: DateTime.parse(json['payment_date']),
      paymentMethod: json['payment_method'] ?? 'bank_transfer',
      status: json['status'] ?? 'pending',
      referenceNumber: json['reference_number'],
      notes: json['notes'],
      invoiceIds: (json['invoice_ids'] as List<dynamic>?)
              ?.map((id) => id.toString())
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'amount': amount,
      'currency': currency,
      'payment_date': paymentDate.toIso8601String(),
      'payment_method': paymentMethod,
      'status': status,
      'reference_number': referenceNumber,
      'notes': notes,
      'invoice_ids': invoiceIds,
    };
  }
}
