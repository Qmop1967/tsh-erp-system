import 'package:json_annotation/json_annotation.dart';

part 'order_model.g.dart';

@JsonSerializable()
class Order {
  final int? id;
  @JsonKey(name: 'order_number')
  final String? orderNumber;
  @JsonKey(name: 'customer_id')
  final int? customerId;
  @JsonKey(name: 'customer_name')
  final String? customerName;
  @JsonKey(name: 'salesperson_id')
  final int? salespersonId;
  @JsonKey(name: 'order_date')
  final DateTime? orderDate;
  @JsonKey(name: 'delivery_date')
  final DateTime? deliveryDate;
  final String status;
  @JsonKey(name: 'total_amount')
  final double totalAmount;
  @JsonKey(name: 'discount_amount')
  final double? discountAmount;
  @JsonKey(name: 'tax_amount')
  final double? taxAmount;
  @JsonKey(name: 'net_amount')
  final double? netAmount;
  final String? currency;
  final String? notes;
  @JsonKey(name: 'delivery_address')
  final String? deliveryAddress;
  @JsonKey(name: 'payment_terms')
  final int? paymentTerms;
  @JsonKey(name: 'payment_status')
  final String? paymentStatus;
  @JsonKey(name: 'order_items')
  final List<OrderItem>? orderItems;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  const Order({
    this.id,
    this.orderNumber,
    this.customerId,
    this.customerName,
    this.salespersonId,
    this.orderDate,
    this.deliveryDate,
    this.status = 'draft',
    required this.totalAmount,
    this.discountAmount,
    this.taxAmount,
    this.netAmount,
    this.currency = 'IQD',
    this.notes,
    this.deliveryAddress,
    this.paymentTerms,
    this.paymentStatus,
    this.orderItems,
    this.createdAt,
    this.updatedAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);

  Map<String, dynamic> toJson() => _$OrderToJson(this);

  bool get isPaid => paymentStatus == 'paid';
  bool get isPending => status == 'draft' || status == 'pending';
  bool get isConfirmed => status == 'confirmed';
  bool get isDelivered => status == 'delivered';
  bool get isCancelled => status == 'cancelled';

  Order copyWith({
    int? id,
    String? orderNumber,
    int? customerId,
    String? customerName,
    int? salespersonId,
    DateTime? orderDate,
    DateTime? deliveryDate,
    String? status,
    double? totalAmount,
    double? discountAmount,
    double? taxAmount,
    double? netAmount,
    String? currency,
    String? notes,
    String? deliveryAddress,
    int? paymentTerms,
    String? paymentStatus,
    List<OrderItem>? orderItems,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Order(
      id: id ?? this.id,
      orderNumber: orderNumber ?? this.orderNumber,
      customerId: customerId ?? this.customerId,
      customerName: customerName ?? this.customerName,
      salespersonId: salespersonId ?? this.salespersonId,
      orderDate: orderDate ?? this.orderDate,
      deliveryDate: deliveryDate ?? this.deliveryDate,
      status: status ?? this.status,
      totalAmount: totalAmount ?? this.totalAmount,
      discountAmount: discountAmount ?? this.discountAmount,
      taxAmount: taxAmount ?? this.taxAmount,
      netAmount: netAmount ?? this.netAmount,
      currency: currency ?? this.currency,
      notes: notes ?? this.notes,
      deliveryAddress: deliveryAddress ?? this.deliveryAddress,
      paymentTerms: paymentTerms ?? this.paymentTerms,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      orderItems: orderItems ?? this.orderItems,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Order(id: $id, orderNumber: $orderNumber, totalAmount: $totalAmount, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Order && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

@JsonSerializable()
class OrderItem {
  final int? id;
  @JsonKey(name: 'order_id')
  final int? orderId;
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

  const OrderItem({
    this.id,
    this.orderId,
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

  factory OrderItem.fromJson(Map<String, dynamic> json) => _$OrderItemFromJson(json);

  Map<String, dynamic> toJson() => _$OrderItemToJson(this);

  double get calculatedTotal => (quantity * unitPrice) - (discountAmount ?? 0) + (taxAmount ?? 0);

  OrderItem copyWith({
    int? id,
    int? orderId,
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
    return OrderItem(
      id: id ?? this.id,
      orderId: orderId ?? this.orderId,
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
    return 'OrderItem(id: $id, productName: $productName, quantity: $quantity, unitPrice: $unitPrice)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is OrderItem && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
