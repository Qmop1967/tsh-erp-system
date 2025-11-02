class Invoice {
  final String id;
  final String invoiceNumber;
  final DateTime invoiceDate;
  final DateTime dueDate;
  final double totalAmount;
  final double paidAmount;
  final double balanceAmount;
  final String status; // draft, sent, paid, overdue, cancelled
  final String currency;
  final List<InvoiceItem> items;
  final String? pdfUrl;

  Invoice({
    required this.id,
    required this.invoiceNumber,
    required this.invoiceDate,
    required this.dueDate,
    required this.totalAmount,
    required this.paidAmount,
    required this.balanceAmount,
    required this.status,
    required this.currency,
    this.items = const [],
    this.pdfUrl,
  });

  bool get isOverdue => DateTime.now().isAfter(dueDate) && balanceAmount > 0;
  bool get isPaid => balanceAmount == 0;

  factory Invoice.fromJson(Map<String, dynamic> json) {
    return Invoice(
      id: json['id'].toString(),
      invoiceNumber: json['invoice_number'] ?? '',
      invoiceDate: DateTime.parse(json['invoice_date']),
      dueDate: DateTime.parse(json['due_date']),
      totalAmount: (json['total_amount'] ?? 0.0).toDouble(),
      paidAmount: (json['paid_amount'] ?? 0.0).toDouble(),
      balanceAmount: (json['balance_amount'] ?? 0.0).toDouble(),
      status: json['status'] ?? 'draft',
      currency: json['currency'] ?? 'IQD',
      items: (json['items'] as List<dynamic>?)
              ?.map((item) => InvoiceItem.fromJson(item))
              .toList() ??
          [],
      pdfUrl: json['pdf_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'invoice_number': invoiceNumber,
      'invoice_date': invoiceDate.toIso8601String(),
      'due_date': dueDate.toIso8601String(),
      'total_amount': totalAmount,
      'paid_amount': paidAmount,
      'balance_amount': balanceAmount,
      'status': status,
      'currency': currency,
      'items': items.map((item) => item.toJson()).toList(),
      'pdf_url': pdfUrl,
    };
  }
}

class InvoiceItem {
  final String id;
  final String productName;
  final int quantity;
  final double unitPrice;
  final double totalPrice;

  InvoiceItem({
    required this.id,
    required this.productName,
    required this.quantity,
    required this.unitPrice,
    required this.totalPrice,
  });

  factory InvoiceItem.fromJson(Map<String, dynamic> json) {
    return InvoiceItem(
      id: json['id'].toString(),
      productName: json['product_name'] ?? '',
      quantity: json['quantity'] ?? 0,
      unitPrice: (json['unit_price'] ?? 0.0).toDouble(),
      totalPrice: (json['total_price'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_name': productName,
      'quantity': quantity,
      'unit_price': unitPrice,
      'total_price': totalPrice,
    };
  }
}
