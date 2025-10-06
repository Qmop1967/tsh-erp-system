class CartItem {
  final String productId;
  final String productName;
  final String productNameAr;
  double price;
  int quantity;
  final String? image;

  CartItem({
    required this.productId,
    required this.productName,
    required this.productNameAr,
    required this.price,
    required this.quantity,
    this.image,
  });

  double get total => price * quantity;

  CartItem copyWith({
    String? productId,
    String? productName,
    String? productNameAr,
    double? price,
    int? quantity,
    String? image,
  }) {
    return CartItem(
      productId: productId ?? this.productId,
      productName: productName ?? this.productName,
      productNameAr: productNameAr ?? this.productNameAr,
      price: price ?? this.price,
      quantity: quantity ?? this.quantity,
      image: image ?? this.image,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'product_name': productName,
      'product_name_ar': productNameAr,
      'price': price,
      'quantity': quantity,
      'image': image,
      'total': total,
    };
  }
}

class POSOrder {
  final String id;
  final String? customerId;
  final String? customerName;
  final List<CartItem> items;
  final double subtotal;
  final double discount;
  final double tax;
  final double total;
  final DateTime createdAt;
  final String status;
  final String paymentMethod;

  POSOrder({
    required this.id,
    this.customerId,
    this.customerName,
    required this.items,
    required this.subtotal,
    this.discount = 0,
    this.tax = 0,
    required this.total,
    required this.createdAt,
    this.status = 'completed',
    this.paymentMethod = 'cash',
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'customer_id': customerId,
      'customer_name': customerName,
      'items': items.map((item) => item.toJson()).toList(),
      'subtotal': subtotal,
      'discount': discount,
      'tax': tax,
      'total': total,
      'created_at': createdAt.toIso8601String(),
      'status': status,
      'payment_method': paymentMethod,
    };
  }
}
