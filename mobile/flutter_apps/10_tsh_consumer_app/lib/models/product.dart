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
  final int actualAvailableStock;
  final String? warehouseId;
  final bool isActive;
  final DateTime? lastSynced;
  final DateTime? createdAt;
  final DateTime? updatedAt;
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
    required this.actualAvailableStock,
    this.warehouseId,
    required this.isActive,
    this.lastSynced,
    this.createdAt,
    this.updatedAt,
    required this.price,
    this.currency = 'IQD',
    this.pricelistName,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String? ?? json['product_id'] as String,
      zohoItemId: json['zoho_item_id'] as String? ?? json['item_id'] as String,
      sku: json['sku'] as String? ?? json['barcode'] as String? ?? '',
      name: json['name'] as String? ?? json['product_name'] as String,
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String? ?? json['image_path'] as String?,
      cdnImageUrl: json['cdn_image_url'] as String?,
      category: json['category'] as String? ?? json['category_name'] as String?,
      stockQuantity: json['stock_quantity'] as int? ?? (json['quantity'] as num?)?.toInt() ?? 0,
      actualAvailableStock: json['actual_available_stock'] as int? ?? (json['quantity'] as num?)?.toInt() ?? 0,
      warehouseId: json['warehouse_id'] as String?,
      isActive: json['is_active'] as bool? ?? json['in_stock'] as bool? ?? true,
      lastSynced: json['last_synced'] != null
          ? DateTime.parse(json['last_synced'] as String)
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      price: (json['price'] as num?)?.toDouble() ?? (json['selling_price'] as num?)?.toDouble() ?? 0.0,
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
      'actual_available_stock': actualAvailableStock,
      'warehouse_id': warehouseId,
      'is_active': isActive,
      'last_synced': lastSynced?.toIso8601String(),
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
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
    int? actualAvailableStock,
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
      actualAvailableStock: actualAvailableStock ?? this.actualAvailableStock,
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

  bool get inStock => actualAvailableStock > 0;
  bool get lowStock => actualAvailableStock > 0 && actualAvailableStock <= 10;
  bool get hasPrice => price > 0;

  String get stockStatusText {
    if (actualAvailableStock == 0) return 'Out of Stock';
    if (actualAvailableStock <= 10) return 'Low Stock';
    return 'In Stock';
  }
}
