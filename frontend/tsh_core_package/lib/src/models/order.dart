import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';
import 'user.dart';
import 'product.dart';

part 'order.g.dart';

enum OrderStatus {
  @JsonValue('pending')
  pending,
  @JsonValue('confirmed')
  confirmed,
  @JsonValue('processing')
  processing,
  @JsonValue('shipped')
  shipped,
  @JsonValue('delivered')
  delivered,
  @JsonValue('cancelled')
  cancelled,
  @JsonValue('refunded')
  refunded,
}

enum PaymentStatus {
  @JsonValue('pending')
  pending,
  @JsonValue('paid')
  paid,
  @JsonValue('failed')
  failed,
  @JsonValue('refunded')
  refunded,
}

enum PaymentMethod {
  @JsonValue('cash')
  cash,
  @JsonValue('card')
  card,
  @JsonValue('bank_transfer')
  bankTransfer,
  @JsonValue('mobile_payment')
  mobilePayment,
}

@JsonSerializable()
class Order extends Equatable {
  final int id;
  final String orderNumber;
  final int? customerId;
  final User? customer;
  final int salesPersonId;
  final User salesPerson;
  final OrderStatus status;
  final PaymentStatus paymentStatus;
  final PaymentMethod? paymentMethod;
  final double subtotal;
  final double taxAmount;
  final double discountAmount;
  final double totalAmount;
  final String? notes;
  final List<OrderItem> items;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? deliveryDate;

  const Order({
    required this.id,
    required this.orderNumber,
    this.customerId,
    this.customer,
    required this.salesPersonId,
    required this.salesPerson,
    required this.status,
    required this.paymentStatus,
    this.paymentMethod,
    required this.subtotal,
    required this.taxAmount,
    required this.discountAmount,
    required this.totalAmount,
    this.notes,
    required this.items,
    required this.createdAt,
    required this.updatedAt,
    this.deliveryDate,
  });

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);
  Map<String, dynamic> toJson() => _$OrderToJson(this);

  int get totalItems => items.fold(0, (sum, item) => sum + item.quantity);
  bool get isPaid => paymentStatus == PaymentStatus.paid;
  bool get isCompleted => status == OrderStatus.delivered;
  bool get canBeCancelled => status == OrderStatus.pending || status == OrderStatus.confirmed;

  @override
  List<Object?> get props => [
        id,
        orderNumber,
        customerId,
        customer,
        salesPersonId,
        salesPerson,
        status,
        paymentStatus,
        paymentMethod,
        subtotal,
        taxAmount,
        discountAmount,
        totalAmount,
        notes,
        items,
        createdAt,
        updatedAt,
        deliveryDate,
      ];
}

@JsonSerializable()
class OrderItem extends Equatable {
  final int id;
  final int orderId;
  final int productId;
  final Product? product;
  final int? productVariantId;
  final ProductVariant? productVariant;
  final int quantity;
  final double unitPrice;
  final double totalPrice;
  final double? discountAmount;

  const OrderItem({
    required this.id,
    required this.orderId,
    required this.productId,
    this.product,
    this.productVariantId,
    this.productVariant,
    required this.quantity,
    required this.unitPrice,
    required this.totalPrice,
    this.discountAmount,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) => _$OrderItemFromJson(json);
  Map<String, dynamic> toJson() => _$OrderItemToJson(this);

  double get finalPrice => totalPrice - (discountAmount ?? 0);

  @override
  List<Object?> get props => [
        id,
        orderId,
        productId,
        product,
        productVariantId,
        productVariant,
        quantity,
        unitPrice,
        totalPrice,
        discountAmount,
      ];
}

@JsonSerializable()
class Cart extends Equatable {
  final List<CartItem> items;
  final double subtotal;
  final double taxAmount;
  final double discountAmount;
  final double totalAmount;

  const Cart({
    required this.items,
    required this.subtotal,
    required this.taxAmount,
    required this.discountAmount,
    required this.totalAmount,
  });

  factory Cart.empty() => const Cart(
        items: [],
        subtotal: 0,
        taxAmount: 0,
        discountAmount: 0,
        totalAmount: 0,
      );

  factory Cart.fromJson(Map<String, dynamic> json) => _$CartFromJson(json);
  Map<String, dynamic> toJson() => _$CartToJson(this);

  int get totalItems => items.fold(0, (sum, item) => sum + item.quantity);
  bool get isEmpty => items.isEmpty;
  bool get isNotEmpty => items.isNotEmpty;

  @override
  List<Object> get props => [items, subtotal, taxAmount, discountAmount, totalAmount];
}

@JsonSerializable()
class CartItem extends Equatable {
  final int productId;
  final Product product;
  final int? productVariantId;
  final ProductVariant? productVariant;
  final int quantity;
  final double unitPrice;
  final double totalPrice;

  const CartItem({
    required this.productId,
    required this.product,
    this.productVariantId,
    this.productVariant,
    required this.quantity,
    required this.unitPrice,
    required this.totalPrice,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) => _$CartItemFromJson(json);
  Map<String, dynamic> toJson() => _$CartItemToJson(this);

  @override
  List<Object?> get props => [
        productId,
        product,
        productVariantId,
        productVariant,
        quantity,
        unitPrice,
        totalPrice,
      ];
}
