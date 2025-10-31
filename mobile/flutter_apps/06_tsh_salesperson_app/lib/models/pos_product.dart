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
    // Support both inventory API format and direct Supabase products table
    final isInventoryFormat = json.containsKey('product');

    if (isInventoryFormat) {
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
    } else {
      // Direct Supabase products table format
      return POSProduct(
        id: json['id']?.toString() ?? '0',
        name: json['name'] ?? '',
        nameAr: json['name_ar'] ?? json['name'] ?? '',
        category: json['category'] ?? 'General',
        price: (json['unit_price'] as num?)?.toDouble() ?? 0.0,
        stock: (json['stock_quantity'] as num?)?.toInt() ?? 0,
        sku: json['sku'] ?? json['product_code'] ?? '',
        description: json['description'],
        image: json['image_url'],
      );
    }
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
