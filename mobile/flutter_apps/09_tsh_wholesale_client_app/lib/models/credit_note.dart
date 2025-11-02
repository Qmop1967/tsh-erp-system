class CreditNote {
  final String id;
  final String creditNoteNumber;
  final DateTime issueDate;
  final double amount;
  final String currency;
  final String status; // draft, issued, applied, cancelled
  final String reason;
  final String? invoiceId;
  final String? invoiceNumber;
  final bool isApplied;

  CreditNote({
    required this.id,
    required this.creditNoteNumber,
    required this.issueDate,
    required this.amount,
    required this.currency,
    required this.status,
    required this.reason,
    this.invoiceId,
    this.invoiceNumber,
    this.isApplied = false,
  });

  factory CreditNote.fromJson(Map<String, dynamic> json) {
    return CreditNote(
      id: json['id'].toString(),
      creditNoteNumber: json['credit_note_number'] ?? '',
      issueDate: DateTime.parse(json['issue_date']),
      amount: (json['amount'] ?? 0.0).toDouble(),
      currency: json['currency'] ?? 'IQD',
      status: json['status'] ?? 'draft',
      reason: json['reason'] ?? '',
      invoiceId: json['invoice_id']?.toString(),
      invoiceNumber: json['invoice_number'],
      isApplied: json['is_applied'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'credit_note_number': creditNoteNumber,
      'issue_date': issueDate.toIso8601String(),
      'amount': amount,
      'currency': currency,
      'status': status,
      'reason': reason,
      'invoice_id': invoiceId,
      'invoice_number': invoiceNumber,
      'is_applied': isApplied,
    };
  }
}
