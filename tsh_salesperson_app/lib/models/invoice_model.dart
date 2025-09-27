import 'package:json_annotation/json_annotation.dart';

part 'invoice_model.g.dart';

@JsonSerializable()
class Invoice {
  final int? id;
  @JsonKey(name: 'invoice_number')
  final String? invoiceNumber;
  @JsonKey(name: 'customer_id')
  final int? customerId;
  @JsonKey(name: 'customer_name')
  final String? customerName;
  @JsonKey(name: 'order_id')
  final int? orderId;
  @JsonKey(name: 'salesperson_id')
  final int? salespersonId;
  @JsonKey(name: 'invoice_date')
  final DateTime? invoiceDate;
  @JsonKey(name: 'due_date')
  final DateTime? dueDate;
  final String status;
  @JsonKey(name: 'subtotal_amount')
  final double subtotalAmount;
  @JsonKey(name: 'discount_amount')
  final double? discountAmount;
  @JsonKey(name: 'tax_amount')
  final double? taxAmount;
  @JsonKey(name: 'total_amount')
  final double totalAmount;
  @JsonKey(name: 'paid_amount')
  final double? paidAmount;
  @JsonKey(name: 'remaining_amount')
  final double? remainingAmount;
  final String? currency;
  final String? notes;
  @JsonKey(name: 'payment_terms')
  final int? paymentTerms;
  @JsonKey(name: 'payment_status')
  final String? paymentStatus;
  @JsonKey(name: 'invoice_items')
  final List<InvoiceItem>? invoiceItems;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  const Invoice({
    this.id,
    this.invoiceNumber,
    this.customerId,
    this.customerName,
    this.orderId,
    this.salespersonId,
    this.invoiceDate,
    this.dueDate,
    this.status = 'draft',
    required this.subtotalAmount,
    this.discountAmount,
    this.taxAmount,
    required this.totalAmount,
    this.paidAmount,
    this.remainingAmount,
    this.currency = 'IQD',
    this.notes,
    this.paymentTerms,
    this.paymentStatus,
    this.invoiceItems,
    this.createdAt,
    this.updatedAt,
  });

  factory Invoice.fromJson(Map<String, dynamic> json) => _$InvoiceFromJson(json);

  Map<String, dynamic> toJson() => _$InvoiceToJson(this);

  bool get isPaid => paymentStatus == 'paid';
  bool get isPartiallyPaid => paymentStatus == 'partially_paid';
  bool get isUnpaid => paymentStatus == 'unpaid' || paymentStatus == null;
  bool get isOverdue => dueDate != null && DateTime.now().isAfter(dueDate!) && !isPaid;

  bool get isDraft => status == 'draft';
  bool get isSent => status == 'sent';
  bool get isVoided => status == 'voided';

  double get calculatedRemainingAmount => totalAmount - (paidAmount ?? 0);

  Invoice copyWith({
    int? id,
    String? invoiceNumber,
    int? customerId,
    String? customerName,
    int? orderId,
    int? salespersonId,
    DateTime? invoiceDate,
    DateTime? dueDate,
    String? status,
    double? subtotalAmount,
    double? discountAmount,
    double? taxAmount,
    double? totalAmount,
    double? paidAmount,
    double? remainingAmount,
    String? currency,
    String? notes,
    int? paymentTerms,
    String? paymentStatus,
    List<InvoiceItem>? invoiceItems,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Invoice(
      id: id ?? this.id,
      invoiceNumber: invoiceNumber ?? this.invoiceNumber,
      customerId: customerId ?? this.customerId,
      customerName: customerName ?? this.customerName,
      orderId: orderId ?? this.orderId,
      salespersonId: salespersonId ?? this.salespersonId,
      invoiceDate: invoiceDate ?? this.invoiceDate,
      dueDate: dueDate ?? this.dueDate,
      status: status ?? this.status,
      subtotalAmount: subtotalAmount ?? this.subtotalAmount,
      discountAmount: discountAmount ?? this.discountAmount,
      taxAmount: taxAmount ?? this.taxAmount,
      totalAmount: totalAmount ?? this.totalAmount,
      paidAmount: paidAmount ?? this.paidAmount,
      remainingAmount: remainingAmount ?? this.remainingAmount,
      currency: currency ?? this.currency,
      notes: notes ?? this.notes,
      paymentTerms: paymentTerms ?? this.paymentTerms,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      invoiceItems: invoiceItems ?? this.invoiceItems,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Invoice(id: $id, invoiceNumber: $invoiceNumber, totalAmount: $totalAmount, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Invoice && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

@JsonSerializable()
class InvoiceItem {
  final int? id;
  @JsonKey(name: 'invoice_id')
  final int? invoiceId;
  @JsonKey(name: 'product_id')
  final int productId;
  @JsonKey(name: 'product_name')
  final String? productName;
  @JsonKey(name: 'product_sku')
  final String? productSku;
  final int quantity;
  @JsonKey(name: 'unit_price')
  final double unitPrice;
  @JsonKey(name: 'discount_percentage')
  final double? discountPercentage;
  @JsonKey(name: 'discount_amount')
  final double? discountAmount;
  @JsonKey(name: 'tax_rate')
  final double? taxRate;
  @JsonKey(name: 'tax_amount')
  final double? taxAmount;
  @JsonKey(name: 'line_total')
  final double? lineTotal;
  final String? notes;

  const InvoiceItem({
    this.id,
    this.invoiceId,
    required this.productId,
    this.productName,
    this.productSku,
    required this.quantity,
    required this.unitPrice,
    this.discountPercentage,
    this.discountAmount,
    this.taxRate,
    this.taxAmount,
    this.lineTotal,
    this.notes,
  });

  factory InvoiceItem.fromJson(Map<String, dynamic> json) => _$InvoiceItemFromJson(json);

  Map<String, dynamic> toJson() => _$InvoiceItemToJson(this);

  double get calculatedTotal => (quantity * unitPrice) - (discountAmount ?? 0) + (taxAmount ?? 0);

  InvoiceItem copyWith({
    int? id,
    int? invoiceId,
    int? productId,
    String? productName,
    String? productSku,
    int? quantity,
    double? unitPrice,
    double? discountPercentage,
    double? discountAmount,
    double? taxRate,
    double? taxAmount,
    double? lineTotal,
    String? notes,
  }) {
    return InvoiceItem(
      id: id ?? this.id,
      invoiceId: invoiceId ?? this.invoiceId,
      productId: productId ?? this.productId,
      productName: productName ?? this.productName,
      productSku: productSku ?? this.productSku,
      quantity: quantity ?? this.quantity,
      unitPrice: unitPrice ?? this.unitPrice,
      discountPercentage: discountPercentage ?? this.discountPercentage,
      discountAmount: discountAmount ?? this.discountAmount,
      taxRate: taxRate ?? this.taxRate,
      taxAmount: taxAmount ?? this.taxAmount,
      lineTotal: lineTotal ?? this.lineTotal,
      notes: notes ?? this.notes,
    );
  }

  @override
  String toString() {
    return 'InvoiceItem(id: $id, productName: $productName, quantity: $quantity, unitPrice: $unitPrice)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is InvoiceItem && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
