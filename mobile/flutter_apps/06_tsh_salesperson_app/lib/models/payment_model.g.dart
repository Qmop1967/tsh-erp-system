// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'payment_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Payment _$PaymentFromJson(Map<String, dynamic> json) => Payment(
      id: (json['id'] as num?)?.toInt(),
      paymentNumber: json['payment_number'] as String?,
      customerId: (json['customer_id'] as num?)?.toInt(),
      customerName: json['customer_name'] as String?,
      orderId: (json['order_id'] as num?)?.toInt(),
      invoiceId: (json['invoice_id'] as num?)?.toInt(),
      paymentDate: json['payment_date'] == null
          ? null
          : DateTime.parse(json['payment_date'] as String),
      amount: (json['amount'] as num).toDouble(),
      paymentMethod: json['payment_method'] as String,
      status: json['status'] as String? ?? 'pending',
      referenceNumber: json['reference_number'] as String?,
      currency: json['currency'] as String? ?? 'IQD',
      notes: json['notes'] as String?,
      processedBy: (json['processed_by'] as num?)?.toInt(),
      processedByName: json['processed_by_name'] as String?,
      bankAccountId: (json['bank_account_id'] as num?)?.toInt(),
      bankAccountName: json['bank_account_name'] as String?,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$PaymentToJson(Payment instance) => <String, dynamic>{
      'id': instance.id,
      'payment_number': instance.paymentNumber,
      'customer_id': instance.customerId,
      'customer_name': instance.customerName,
      'order_id': instance.orderId,
      'invoice_id': instance.invoiceId,
      'payment_date': instance.paymentDate?.toIso8601String(),
      'amount': instance.amount,
      'payment_method': instance.paymentMethod,
      'status': instance.status,
      'reference_number': instance.referenceNumber,
      'currency': instance.currency,
      'notes': instance.notes,
      'processed_by': instance.processedBy,
      'processed_by_name': instance.processedByName,
      'bank_account_id': instance.bankAccountId,
      'bank_account_name': instance.bankAccountName,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
