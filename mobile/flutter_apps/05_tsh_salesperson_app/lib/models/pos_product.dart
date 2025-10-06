class POSProduct {
  final String id;
  final String name;
  final String nameAr;
  final String category;
  final double price;
  final int stock;
  final String sku;
  final String? description;
  final String? image;

  POSProduct({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.category,
    required this.price,
    required this.stock,
    required this.sku,
    this.description,
    this.image,
  });

  factory POSProduct.fromJson(Map<String, dynamic> json) {
    final product = json['product'] ?? {};
    return POSProduct(
      id: json['product_id']?.toString() ?? '0',
      name: product['name'] ?? '',
      nameAr: product['name_ar'] ?? product['name'] ?? '',
      category: product['category_name'] ?? 'General',
      price: (product['unit_price'] as num?)?.toDouble() ?? 0.0,
      stock: (json['available_quantity'] as num?)?.toInt() ?? 0,
      sku: product['sku'] ?? '',
      description: null,
      image: product['image_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'name_ar': nameAr,
      'category': category,
      'price': price,
      'stock': stock,
      'sku': sku,
      'description': description,
      'image': image,
    };
  }
}
