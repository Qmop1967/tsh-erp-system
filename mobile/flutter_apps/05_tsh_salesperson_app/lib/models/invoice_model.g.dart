// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invoice_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Invoice _$InvoiceFromJson(Map<String, dynamic> json) => Invoice(
      id: (json['id'] as num?)?.toInt(),
      invoiceNumber: json['invoice_number'] as String?,
      customerId: (json['customer_id'] as num?)?.toInt(),
      customerName: json['customer_name'] as String?,
      orderId: (json['order_id'] as num?)?.toInt(),
      salespersonId: (json['salesperson_id'] as num?)?.toInt(),
      invoiceDate: json['invoice_date'] == null
          ? null
          : DateTime.parse(json['invoice_date'] as String),
      dueDate: json['due_date'] == null
          ? null
          : DateTime.parse(json['due_date'] as String),
      status: json['status'] as String? ?? 'draft',
      subtotalAmount: (json['subtotal_amount'] as num).toDouble(),
      discountAmount: (json['discount_amount'] as num?)?.toDouble(),
      taxAmount: (json['tax_amount'] as num?)?.toDouble(),
      totalAmount: (json['total_amount'] as num).toDouble(),
      paidAmount: (json['paid_amount'] as num?)?.toDouble(),
      remainingAmount: (json['remaining_amount'] as num?)?.toDouble(),
      currency: json['currency'] as String? ?? 'IQD',
      notes: json['notes'] as String?,
      paymentTerms: (json['payment_terms'] as num?)?.toInt(),
      paymentStatus: json['payment_status'] as String?,
      invoiceItems: (json['invoice_items'] as List<dynamic>?)
          ?.map((e) => InvoiceItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$InvoiceToJson(Invoice instance) => <String, dynamic>{
      'id': instance.id,
      'invoice_number': instance.invoiceNumber,
      'customer_id': instance.customerId,
      'customer_name': instance.customerName,
      'order_id': instance.orderId,
      'salesperson_id': instance.salespersonId,
      'invoice_date': instance.invoiceDate?.toIso8601String(),
      'due_date': instance.dueDate?.toIso8601String(),
      'status': instance.status,
      'subtotal_amount': instance.subtotalAmount,
      'discount_amount': instance.discountAmount,
      'tax_amount': instance.taxAmount,
      'total_amount': instance.totalAmount,
      'paid_amount': instance.paidAmount,
      'remaining_amount': instance.remainingAmount,
      'currency': instance.currency,
      'notes': instance.notes,
      'payment_terms': instance.paymentTerms,
      'payment_status': instance.paymentStatus,
      'invoice_items': instance.invoiceItems,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };

InvoiceItem _$InvoiceItemFromJson(Map<String, dynamic> json) => InvoiceItem(
      id: (json['id'] as num?)?.toInt(),
      invoiceId: (json['invoice_id'] as num?)?.toInt(),
      productId: (json['product_id'] as num).toInt(),
      productName: json['product_name'] as String?,
      productSku: json['product_sku'] as String?,
      quantity: (json['quantity'] as num).toInt(),
      unitPrice: (json['unit_price'] as num).toDouble(),
      discountPercentage: (json['discount_percentage'] as num?)?.toDouble(),
      discountAmount: (json['discount_amount'] as num?)?.toDouble(),
      taxRate: (json['tax_rate'] as num?)?.toDouble(),
      taxAmount: (json['tax_amount'] as num?)?.toDouble(),
      lineTotal: (json['line_total'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
    );

Map<String, dynamic> _$InvoiceItemToJson(InvoiceItem instance) =>
    <String, dynamic>{
      'id': instance.id,
      'invoice_id': instance.invoiceId,
      'product_id': instance.productId,
      'product_name': instance.productName,
      'product_sku': instance.productSku,
      'quantity': instance.quantity,
      'unit_price': instance.unitPrice,
      'discount_percentage': instance.discountPercentage,
      'discount_amount': instance.discountAmount,
      'tax_rate': instance.taxRate,
      'tax_amount': instance.taxAmount,
      'line_total': instance.lineTotal,
      'notes': instance.notes,
    };
