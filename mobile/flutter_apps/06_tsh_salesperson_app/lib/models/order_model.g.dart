// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'order_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Order _$OrderFromJson(Map<String, dynamic> json) => Order(
      id: (json['id'] as num?)?.toInt(),
      orderNumber: json['order_number'] as String?,
      customerId: (json['customer_id'] as num?)?.toInt(),
      customerName: json['customer_name'] as String?,
      salespersonId: (json['salesperson_id'] as num?)?.toInt(),
      orderDate: json['order_date'] == null
          ? null
          : DateTime.parse(json['order_date'] as String),
      deliveryDate: json['delivery_date'] == null
          ? null
          : DateTime.parse(json['delivery_date'] as String),
      status: json['status'] as String? ?? 'draft',
      totalAmount: (json['total_amount'] as num).toDouble(),
      discountAmount: (json['discount_amount'] as num?)?.toDouble(),
      taxAmount: (json['tax_amount'] as num?)?.toDouble(),
      netAmount: (json['net_amount'] as num?)?.toDouble(),
      currency: json['currency'] as String? ?? 'IQD',
      notes: json['notes'] as String?,
      deliveryAddress: json['delivery_address'] as String?,
      paymentTerms: (json['payment_terms'] as num?)?.toInt(),
      paymentStatus: json['payment_status'] as String?,
      orderItems: (json['order_items'] as List<dynamic>?)
          ?.map((e) => OrderItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$OrderToJson(Order instance) => <String, dynamic>{
      'id': instance.id,
      'order_number': instance.orderNumber,
      'customer_id': instance.customerId,
      'customer_name': instance.customerName,
      'salesperson_id': instance.salespersonId,
      'order_date': instance.orderDate?.toIso8601String(),
      'delivery_date': instance.deliveryDate?.toIso8601String(),
      'status': instance.status,
      'total_amount': instance.totalAmount,
      'discount_amount': instance.discountAmount,
      'tax_amount': instance.taxAmount,
      'net_amount': instance.netAmount,
      'currency': instance.currency,
      'notes': instance.notes,
      'delivery_address': instance.deliveryAddress,
      'payment_terms': instance.paymentTerms,
      'payment_status': instance.paymentStatus,
      'order_items': instance.orderItems,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };

OrderItem _$OrderItemFromJson(Map<String, dynamic> json) => OrderItem(
      id: (json['id'] as num?)?.toInt(),
      orderId: (json['order_id'] as num?)?.toInt(),
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

Map<String, dynamic> _$OrderItemToJson(OrderItem instance) => <String, dynamic>{
      'id': instance.id,
      'order_id': instance.orderId,
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
