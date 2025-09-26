import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'product.g.dart';

@JsonSerializable()
class Product extends Equatable {
  final int id;
  final String name;
  final String? description;
  final String sku;
  final double price;
  final double? costPrice;
  final int stockQuantity;
  final int? minStockLevel;
  final bool isActive;
  final String? imageUrl;
  final Category? category;
  final Brand? brand;
  final List<ProductVariant>? variants;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Product({
    required this.id,
    required this.name,
    this.description,
    required this.sku,
    required this.price,
    this.costPrice,
    required this.stockQuantity,
    this.minStockLevel,
    required this.isActive,
    this.imageUrl,
    this.category,
    this.brand,
    this.variants,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) => _$ProductFromJson(json);
  Map<String, dynamic> toJson() => _$ProductToJson(this);

  bool get isLowStock => minStockLevel != null && stockQuantity <= minStockLevel!;
  bool get isOutOfStock => stockQuantity <= 0;
  double? get profitMargin => costPrice != null ? price - costPrice! : null;

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        sku,
        price,
        costPrice,
        stockQuantity,
        minStockLevel,
        isActive,
        imageUrl,
        category,
        brand,
        variants,
        createdAt,
        updatedAt,
      ];
}

@JsonSerializable()
class Category extends Equatable {
  final int id;
  final String name;
  final String? description;
  final String? imageUrl;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Category({
    required this.id,
    required this.name,
    this.description,
    this.imageUrl,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Category.fromJson(Map<String, dynamic> json) => _$CategoryFromJson(json);
  Map<String, dynamic> toJson() => _$CategoryToJson(this);

  @override
  List<Object?> get props => [id, name, description, imageUrl, isActive, createdAt, updatedAt];
}

@JsonSerializable()
class Brand extends Equatable {
  final int id;
  final String name;
  final String? description;
  final String? logoUrl;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Brand({
    required this.id,
    required this.name,
    this.description,
    this.logoUrl,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Brand.fromJson(Map<String, dynamic> json) => _$BrandFromJson(json);
  Map<String, dynamic> toJson() => _$BrandToJson(this);

  @override
  List<Object?> get props => [id, name, description, logoUrl, isActive, createdAt, updatedAt];
}

@JsonSerializable()
class ProductVariant extends Equatable {
  final int id;
  final int productId;
  final String name;
  final String? sku;
  final double? priceAdjustment;
  final int stockQuantity;
  final Map<String, String> attributes; // e.g., {"size": "Large", "color": "Red"}
  final bool isActive;

  const ProductVariant({
    required this.id,
    required this.productId,
    required this.name,
    this.sku,
    this.priceAdjustment,
    required this.stockQuantity,
    required this.attributes,
    required this.isActive,
  });

  factory ProductVariant.fromJson(Map<String, dynamic> json) => _$ProductVariantFromJson(json);
  Map<String, dynamic> toJson() => _$ProductVariantToJson(this);

  @override
  List<Object?> get props => [id, productId, name, sku, priceAdjustment, stockQuantity, attributes, isActive];
}
