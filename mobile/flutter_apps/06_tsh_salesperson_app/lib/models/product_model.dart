import 'package:json_annotation/json_annotation.dart';

part 'product_model.g.dart';

@JsonSerializable()
class Product {
  final int? id;
  @JsonKey(name: 'product_code')
  final String? productCode;
  final String name;
  final String? description;
  final String? sku;
  final double price;
  @JsonKey(name: 'cost_price')
  final double? costPrice;
  @JsonKey(name: 'stock_quantity')
  final int? stockQuantity;
  @JsonKey(name: 'min_stock_level')
  final int? minStockLevel;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'image_url')
  final String? imageUrl;
  @JsonKey(name: 'category_id')
  final int? categoryId;
  @JsonKey(name: 'category_name')
  final String? categoryName;
  final String? unit;
  @JsonKey(name: 'barcode')
  final String? barcode;
  @JsonKey(name: 'tax_rate')
  final double? taxRate;
  @JsonKey(name: 'discount_percentage')
  final double? discountPercentage;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  const Product({
    this.id,
    this.productCode,
    required this.name,
    this.description,
    this.sku,
    required this.price,
    this.costPrice,
    this.stockQuantity,
    this.minStockLevel,
    this.isActive = true,
    this.imageUrl,
    this.categoryId,
    this.categoryName,
    this.unit,
    this.barcode,
    this.taxRate,
    this.discountPercentage,
    this.createdAt,
    this.updatedAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) => _$ProductFromJson(json);

  Map<String, dynamic> toJson() => _$ProductToJson(this);

  bool get isLowStock => minStockLevel != null && (stockQuantity ?? 0) <= minStockLevel!;
  bool get isOutOfStock => (stockQuantity ?? 0) <= 0;
  double? get profitMargin => costPrice != null ? price - costPrice! : null;

  Product copyWith({
    int? id,
    String? productCode,
    String? name,
    String? description,
    String? sku,
    double? price,
    double? costPrice,
    int? stockQuantity,
    int? minStockLevel,
    bool? isActive,
    String? imageUrl,
    int? categoryId,
    String? categoryName,
    String? unit,
    String? barcode,
    double? taxRate,
    double? discountPercentage,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Product(
      id: id ?? this.id,
      productCode: productCode ?? this.productCode,
      name: name ?? this.name,
      description: description ?? this.description,
      sku: sku ?? this.sku,
      price: price ?? this.price,
      costPrice: costPrice ?? this.costPrice,
      stockQuantity: stockQuantity ?? this.stockQuantity,
      minStockLevel: minStockLevel ?? this.minStockLevel,
      isActive: isActive ?? this.isActive,
      imageUrl: imageUrl ?? this.imageUrl,
      categoryId: categoryId ?? this.categoryId,
      categoryName: categoryName ?? this.categoryName,
      unit: unit ?? this.unit,
      barcode: barcode ?? this.barcode,
      taxRate: taxRate ?? this.taxRate,
      discountPercentage: discountPercentage ?? this.discountPercentage,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Product(id: $id, name: $name, price: $price, stockQuantity: $stockQuantity)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Product && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
