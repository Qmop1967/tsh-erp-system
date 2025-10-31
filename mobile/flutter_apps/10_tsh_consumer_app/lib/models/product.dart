class Product {
  final String id;
  final String zohoItemId;
  final String sku;
  final String name;
  final String? description;
  final String? imageUrl;
  final String? cdnImageUrl;
  final String? category;
  final int stockQuantity;
  final String warehouseId;
  final bool isActive;
  final DateTime lastSynced;
  final DateTime createdAt;
  final DateTime updatedAt;
  final double price;
  final String currency;
  final String? pricelistName;

  const Product({
    required this.id,
    required this.zohoItemId,
    required this.sku,
    required this.name,
    this.description,
    this.imageUrl,
    this.cdnImageUrl,
    this.category,
    required this.stockQuantity,
    required this.warehouseId,
    required this.isActive,
    required this.lastSynced,
    required this.createdAt,
    required this.updatedAt,
    required this.price,
    this.currency = 'IQD',
    this.pricelistName,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String,
      zohoItemId: json['zoho_item_id'] as String,
      sku: json['sku'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      cdnImageUrl: json['cdn_image_url'] as String?,
      category: json['category'] as String?,
      stockQuantity: json['stock_quantity'] as int? ?? 0,
      warehouseId: json['warehouse_id'] as String? ?? '',
      isActive: json['is_active'] as bool? ?? true,
      lastSynced: json['last_synced'] != null
          ? DateTime.parse(json['last_synced'] as String)
          : DateTime.now(),
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now(),
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'IQD',
      pricelistName: json['pricelist_name'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'zoho_item_id': zohoItemId,
      'sku': sku,
      'name': name,
      'description': description,
      'image_url': imageUrl,
      'cdn_image_url': cdnImageUrl,
      'category': category,
      'stock_quantity': stockQuantity,
      'warehouse_id': warehouseId,
      'is_active': isActive,
      'last_synced': lastSynced.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'price': price,
      'currency': currency,
      'pricelist_name': pricelistName,
    };
  }

  Product copyWith({
    String? id,
    String? zohoItemId,
    String? sku,
    String? name,
    String? description,
    String? imageUrl,
    String? cdnImageUrl,
    String? category,
    int? stockQuantity,
    String? warehouseId,
    bool? isActive,
    DateTime? lastSynced,
    DateTime? createdAt,
    DateTime? updatedAt,
    double? price,
    String? currency,
    String? pricelistName,
  }) {
    return Product(
      id: id ?? this.id,
      zohoItemId: zohoItemId ?? this.zohoItemId,
      sku: sku ?? this.sku,
      name: name ?? this.name,
      description: description ?? this.description,
      imageUrl: imageUrl ?? this.imageUrl,
      cdnImageUrl: cdnImageUrl ?? this.cdnImageUrl,
      category: category ?? this.category,
      stockQuantity: stockQuantity ?? this.stockQuantity,
      warehouseId: warehouseId ?? this.warehouseId,
      isActive: isActive ?? this.isActive,
      lastSynced: lastSynced ?? this.lastSynced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      price: price ?? this.price,
      currency: currency ?? this.currency,
      pricelistName: pricelistName ?? this.pricelistName,
    );
  }

  bool get inStock => stockQuantity > 0;
  bool get lowStock => stockQuantity > 0 && stockQuantity <= 10;
  bool get hasPrice => price > 0;
}
