import 'package:flutter/material.dart';

class CartItem {
  final String productId;
  final String productName;
  final double price;
  final String? imagePath;
  int quantity;

  CartItem({
    required this.productId,
    required this.productName,
    required this.price,
    this.imagePath,
    this.quantity = 1,
  });

  double get totalPrice => price * quantity;
}

class CartService extends ChangeNotifier {
  final List<CartItem> _items = [];

  List<CartItem> get items => _items;

  int get itemCount => _items.fold(0, (sum, item) => sum + item.quantity);

  double get totalAmount => _items.fold(0, (sum, item) => sum + item.totalPrice);

  void addToCart(Map<String, dynamic> product) {
    final productId = product['id']?.toString() ?? product['item_id']?.toString() ?? '';
    final existingIndex = _items.indexWhere((item) => item.productId == productId);

    if (existingIndex >= 0) {
      _items[existingIndex].quantity++;
    } else {
      _items.add(CartItem(
        productId: productId,
        productName: product['product_name'] ?? 'Unknown Product',
        price: (product['selling_price'] ?? 0).toDouble(),
        imagePath: product['image_path'],
      ));
    }
    notifyListeners();
  }

  void removeFromCart(String productId) {
    _items.removeWhere((item) => item.productId == productId);
    notifyListeners();
  }

  void updateQuantity(String productId, int quantity) {
    final index = _items.indexWhere((item) => item.productId == productId);
    if (index >= 0) {
      if (quantity <= 0) {
        _items.removeAt(index);
      } else {
        _items[index].quantity = quantity;
      }
      notifyListeners();
    }
  }

  void clearCart() {
    _items.clear();
    notifyListeners();
  }

  List<Map<String, dynamic>> getZohoLineItems() {
    return _items.map((item) => {
      'item_id': item.productId,
      'name': item.productName,
      'quantity': item.quantity,
      'rate': item.price,
      'amount': item.totalPrice,
    }).toList();
  }
}
