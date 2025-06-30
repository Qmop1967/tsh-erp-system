// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'order.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Order _$OrderFromJson(Map<String, dynamic> json) => Order(
  id: (json['id'] as num).toInt(),
  orderNumber: json['orderNumber'] as String,
  customerId: (json['customerId'] as num?)?.toInt(),
  customer: json['customer'] == null
      ? null
      : User.fromJson(json['customer'] as Map<String, dynamic>),
  salesPersonId: (json['salesPersonId'] as num).toInt(),
  salesPerson: User.fromJson(json['salesPerson'] as Map<String, dynamic>),
  status: $enumDecode(_$OrderStatusEnumMap, json['status']),
  paymentStatus: $enumDecode(_$PaymentStatusEnumMap, json['paymentStatus']),
  paymentMethod: $enumDecodeNullable(
    _$PaymentMethodEnumMap,
    json['paymentMethod'],
  ),
  subtotal: (json['subtotal'] as num).toDouble(),
  taxAmount: (json['taxAmount'] as num).toDouble(),
  discountAmount: (json['discountAmount'] as num).toDouble(),
  totalAmount: (json['totalAmount'] as num).toDouble(),
  notes: json['notes'] as String?,
  items: (json['items'] as List<dynamic>)
      .map((e) => OrderItem.fromJson(e as Map<String, dynamic>))
      .toList(),
  createdAt: DateTime.parse(json['createdAt'] as String),
  updatedAt: DateTime.parse(json['updatedAt'] as String),
  deliveryDate: json['deliveryDate'] == null
      ? null
      : DateTime.parse(json['deliveryDate'] as String),
);

Map<String, dynamic> _$OrderToJson(Order instance) => <String, dynamic>{
  'id': instance.id,
  'orderNumber': instance.orderNumber,
  'customerId': instance.customerId,
  'customer': instance.customer,
  'salesPersonId': instance.salesPersonId,
  'salesPerson': instance.salesPerson,
  'status': _$OrderStatusEnumMap[instance.status]!,
  'paymentStatus': _$PaymentStatusEnumMap[instance.paymentStatus]!,
  'paymentMethod': _$PaymentMethodEnumMap[instance.paymentMethod],
  'subtotal': instance.subtotal,
  'taxAmount': instance.taxAmount,
  'discountAmount': instance.discountAmount,
  'totalAmount': instance.totalAmount,
  'notes': instance.notes,
  'items': instance.items,
  'createdAt': instance.createdAt.toIso8601String(),
  'updatedAt': instance.updatedAt.toIso8601String(),
  'deliveryDate': instance.deliveryDate?.toIso8601String(),
};

const _$OrderStatusEnumMap = {
  OrderStatus.pending: 'pending',
  OrderStatus.confirmed: 'confirmed',
  OrderStatus.processing: 'processing',
  OrderStatus.shipped: 'shipped',
  OrderStatus.delivered: 'delivered',
  OrderStatus.cancelled: 'cancelled',
  OrderStatus.refunded: 'refunded',
};

const _$PaymentStatusEnumMap = {
  PaymentStatus.pending: 'pending',
  PaymentStatus.paid: 'paid',
  PaymentStatus.failed: 'failed',
  PaymentStatus.refunded: 'refunded',
};

const _$PaymentMethodEnumMap = {
  PaymentMethod.cash: 'cash',
  PaymentMethod.card: 'card',
  PaymentMethod.bankTransfer: 'bank_transfer',
  PaymentMethod.mobilePayment: 'mobile_payment',
};

OrderItem _$OrderItemFromJson(Map<String, dynamic> json) => OrderItem(
  id: (json['id'] as num).toInt(),
  orderId: (json['orderId'] as num).toInt(),
  productId: (json['productId'] as num).toInt(),
  product: json['product'] == null
      ? null
      : Product.fromJson(json['product'] as Map<String, dynamic>),
  productVariantId: (json['productVariantId'] as num?)?.toInt(),
  productVariant: json['productVariant'] == null
      ? null
      : ProductVariant.fromJson(json['productVariant'] as Map<String, dynamic>),
  quantity: (json['quantity'] as num).toInt(),
  unitPrice: (json['unitPrice'] as num).toDouble(),
  totalPrice: (json['totalPrice'] as num).toDouble(),
  discountAmount: (json['discountAmount'] as num?)?.toDouble(),
);

Map<String, dynamic> _$OrderItemToJson(OrderItem instance) => <String, dynamic>{
  'id': instance.id,
  'orderId': instance.orderId,
  'productId': instance.productId,
  'product': instance.product,
  'productVariantId': instance.productVariantId,
  'productVariant': instance.productVariant,
  'quantity': instance.quantity,
  'unitPrice': instance.unitPrice,
  'totalPrice': instance.totalPrice,
  'discountAmount': instance.discountAmount,
};

Cart _$CartFromJson(Map<String, dynamic> json) => Cart(
  items: (json['items'] as List<dynamic>)
      .map((e) => CartItem.fromJson(e as Map<String, dynamic>))
      .toList(),
  subtotal: (json['subtotal'] as num).toDouble(),
  taxAmount: (json['taxAmount'] as num).toDouble(),
  discountAmount: (json['discountAmount'] as num).toDouble(),
  totalAmount: (json['totalAmount'] as num).toDouble(),
);

Map<String, dynamic> _$CartToJson(Cart instance) => <String, dynamic>{
  'items': instance.items,
  'subtotal': instance.subtotal,
  'taxAmount': instance.taxAmount,
  'discountAmount': instance.discountAmount,
  'totalAmount': instance.totalAmount,
};

CartItem _$CartItemFromJson(Map<String, dynamic> json) => CartItem(
  productId: (json['productId'] as num).toInt(),
  product: Product.fromJson(json['product'] as Map<String, dynamic>),
  productVariantId: (json['productVariantId'] as num?)?.toInt(),
  productVariant: json['productVariant'] == null
      ? null
      : ProductVariant.fromJson(json['productVariant'] as Map<String, dynamic>),
  quantity: (json['quantity'] as num).toInt(),
  unitPrice: (json['unitPrice'] as num).toDouble(),
  totalPrice: (json['totalPrice'] as num).toDouble(),
);

Map<String, dynamic> _$CartItemToJson(CartItem instance) => <String, dynamic>{
  'productId': instance.productId,
  'product': instance.product,
  'productVariantId': instance.productVariantId,
  'productVariant': instance.productVariant,
  'quantity': instance.quantity,
  'unitPrice': instance.unitPrice,
  'totalPrice': instance.totalPrice,
};
