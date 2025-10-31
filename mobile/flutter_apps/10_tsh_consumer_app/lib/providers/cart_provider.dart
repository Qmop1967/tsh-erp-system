import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/cart_item.dart';
import '../models/product.dart';

class CartNotifier extends StateNotifier<List<CartItem>> {
  CartNotifier() : super([]) {
    _loadCart();
  }

  static const String _cartKey = 'tsh_cart_storage';

  Future<void> _loadCart() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cartJson = prefs.getString(_cartKey);
      if (cartJson != null) {
        final List<dynamic> decoded = json.decode(cartJson);
        state = decoded.map((item) => CartItem.fromJson(item)).toList();
      }
    } catch (e) {
      // Failed to load cart, start with empty
      state = [];
    }
  }

  Future<void> _saveCart() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cartJson = json.encode(state.map((item) => item.toJson()).toList());
      await prefs.setString(_cartKey, cartJson);
    } catch (e) {
      // Failed to save cart
    }
  }

  void addItem(Product product, [int quantity = 1]) {
    final existingIndex = state.indexWhere((item) => item.product.id == product.id);

    if (existingIndex >= 0) {
      // Update quantity of existing item
      state = [
        for (int i = 0; i < state.length; i++)
          if (i == existingIndex)
            state[i].copyWith(quantity: state[i].quantity + quantity)
          else
            state[i],
      ];
    } else {
      // Add new item
      state = [...state, CartItem(product: product, quantity: quantity)];
    }

    _saveCart();
  }

  void removeItem(String productId) {
    state = state.where((item) => item.product.id != productId).toList();
    _saveCart();
  }

  void updateQuantity(String productId, int quantity) {
    if (quantity <= 0) {
      removeItem(productId);
      return;
    }

    state = [
      for (final item in state)
        if (item.product.id == productId)
          item.copyWith(quantity: quantity)
        else
          item,
    ];

    _saveCart();
  }

  void updateComment(String productId, String comment) {
    state = [
      for (final item in state)
        if (item.product.id == productId)
          item.copyWith(comment: comment)
        else
          item,
    ];

    _saveCart();
  }

  void clearCart() {
    state = [];
    _saveCart();
  }

  int getTotalItems() {
    return state.fold(0, (total, item) => total + item.quantity);
  }

  double getTotalPrice() {
    return state.fold(0.0, (total, item) => total + item.totalPrice);
  }
}

final cartProvider = StateNotifierProvider<CartNotifier, List<CartItem>>((ref) {
  return CartNotifier();
});
