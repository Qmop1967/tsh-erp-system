import 'product.dart';

class CartItem {
  final Product product;
  final int quantity;
  final String? comment;

  const CartItem({
    required this.product,
    required this.quantity,
    this.comment,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      product: Product.fromJson(json['product'] as Map<String, dynamic>),
      quantity: json['quantity'] as int,
      comment: json['comment'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product': product.toJson(),
      'quantity': quantity,
      'comment': comment,
    };
  }

  CartItem copyWith({
    Product? product,
    int? quantity,
    String? comment,
  }) {
    return CartItem(
      product: product ?? this.product,
      quantity: quantity ?? this.quantity,
      comment: comment ?? this.comment,
    );
  }

  double get totalPrice => product.price * quantity;
}
