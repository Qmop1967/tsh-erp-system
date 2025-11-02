class Product {
  final String id;
  final String name;
  final String? description;
  final String? sku;
  final String? barcode;
  final double wholesalePrice;
  final double retailPrice;
  final String currency;
  final int stockQuantity;
  final int minOrderQuantity;
  final String? category;
  final String? brand;
  final String? imageUrl;
  final bool isActive;
  final List<String> tags;

  Product({
    required this.id,
    required this.name,
    this.description,
    this.sku,
    this.barcode,
    required this.wholesalePrice,
    required this.retailPrice,
    required this.currency,
    required this.stockQuantity,
    this.minOrderQuantity = 1,
    this.category,
    this.brand,
    this.imageUrl,
    this.isActive = true,
    this.tags = const [],
  });

  bool get inStock => stockQuantity > 0;
  bool get lowStock => stockQuantity > 0 && stockQuantity <= minOrderQuantity * 5;

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'].toString(),
      name: json['name'] ?? '',
      description: json['description'],
      sku: json['sku'],
      barcode: json['barcode'],
      wholesalePrice: (json['wholesale_price'] ?? 0.0).toDouble(),
      retailPrice: (json['retail_price'] ?? 0.0).toDouble(),
      currency: json['currency'] ?? 'IQD',
      stockQuantity: json['stock_quantity'] ?? 0,
      minOrderQuantity: json['min_order_quantity'] ?? 1,
      category: json['category'],
      brand: json['brand'],
      imageUrl: json['image_url'],
      isActive: json['is_active'] ?? true,
      tags: (json['tags'] as List<dynamic>?)?.map((t) => t.toString()).toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'sku': sku,
      'barcode': barcode,
      'wholesale_price': wholesalePrice,
      'retail_price': retailPrice,
      'currency': currency,
      'stock_quantity': stockQuantity,
      'min_order_quantity': minOrderQuantity,
      'category': category,
      'brand': brand,
      'image_url': imageUrl,
      'is_active': isActive,
      'tags': tags,
    };
  }
}
