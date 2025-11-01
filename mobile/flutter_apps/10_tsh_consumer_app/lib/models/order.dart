class Order {
  final String id;
  final String orderNumber;
  final String status;
  final double totalAmount;
  final String currency;
  final DateTime createdAt;
  final String customerName;
  final String customerEmail;
  final String customerPhone;
  final String deliveryAddress;
  final String? notes;
  final List<OrderItem> items;
  final DateTime? updatedAt;

  Order({
    required this.id,
    required this.orderNumber,
    required this.status,
    required this.totalAmount,
    required this.currency,
    required this.createdAt,
    required this.customerName,
    required this.customerEmail,
    required this.customerPhone,
    required this.deliveryAddress,
    this.notes,
    required this.items,
    this.updatedAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id']?.toString() ?? '',
      orderNumber: json['order_number']?.toString() ?? '',
      status: json['status']?.toString() ?? 'pending',
      totalAmount: (json['total_amount'] ?? 0).toDouble(),
      currency: json['currency']?.toString() ?? 'IQD',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      customerName: json['customer_name']?.toString() ?? '',
      customerEmail: json['customer_email']?.toString() ?? '',
      customerPhone: json['customer_phone']?.toString() ?? '',
      deliveryAddress: json['delivery_address']?.toString() ?? '',
      notes: json['notes']?.toString(),
      items: (json['items'] as List<dynamic>?)
              ?.map((item) => OrderItem.fromJson(item))
              .toList() ??
          [],
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'order_number': orderNumber,
      'status': status,
      'total_amount': totalAmount,
      'currency': currency,
      'created_at': createdAt.toIso8601String(),
      'customer_name': customerName,
      'customer_email': customerEmail,
      'customer_phone': customerPhone,
      'delivery_address': deliveryAddress,
      'notes': notes,
      'items': items.map((item) => item.toJson()).toList(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  String getStatusText() {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'قيد الانتظار';
      case 'confirmed':
        return 'مؤكد';
      case 'processing':
        return 'قيد المعالجة';
      case 'shipped':
        return 'تم الشحن';
      case 'delivered':
        return 'تم التوصيل';
      case 'cancelled':
        return 'ملغي';
      default:
        return status;
    }
  }

  String getFormattedDate() {
    final now = DateTime.now();
    final difference = now.difference(createdAt);

    if (difference.inDays == 0) {
      if (difference.inHours == 0) {
        return 'منذ ${difference.inMinutes} دقيقة';
      }
      return 'منذ ${difference.inHours} ساعة';
    } else if (difference.inDays == 1) {
      return 'أمس';
    } else if (difference.inDays < 7) {
      return 'منذ ${difference.inDays} أيام';
    } else {
      return '${createdAt.day}/${createdAt.month}/${createdAt.year}';
    }
  }
}

class OrderItem {
  final String productId;
  final String productName;
  final String? productSku;
  final int quantity;
  final double price;
  final String? imageUrl;

  OrderItem({
    required this.productId,
    required this.productName,
    this.productSku,
    required this.quantity,
    required this.price,
    this.imageUrl,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      productId: json['product_id']?.toString() ?? '',
      productName: json['product_name']?.toString() ?? '',
      productSku: json['product_sku']?.toString(),
      quantity: json['quantity'] ?? 1,
      price: (json['price'] ?? 0).toDouble(),
      imageUrl: json['image_url']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'product_name': productName,
      'product_sku': productSku,
      'quantity': quantity,
      'price': price,
      'image_url': imageUrl,
    };
  }

  double get subtotal => price * quantity;
}
