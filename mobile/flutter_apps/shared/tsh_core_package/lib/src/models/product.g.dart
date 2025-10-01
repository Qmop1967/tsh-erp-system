// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'product.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Product _$ProductFromJson(Map<String, dynamic> json) => Product(
  id: (json['id'] as num).toInt(),
  name: json['name'] as String,
  description: json['description'] as String?,
  sku: json['sku'] as String,
  price: (json['price'] as num).toDouble(),
  costPrice: (json['costPrice'] as num?)?.toDouble(),
  stockQuantity: (json['stockQuantity'] as num).toInt(),
  minStockLevel: (json['minStockLevel'] as num?)?.toInt(),
  isActive: json['isActive'] as bool,
  imageUrl: json['imageUrl'] as String?,
  category: json['category'] == null
      ? null
      : Category.fromJson(json['category'] as Map<String, dynamic>),
  brand: json['brand'] == null
      ? null
      : Brand.fromJson(json['brand'] as Map<String, dynamic>),
  variants: (json['variants'] as List<dynamic>?)
      ?.map((e) => ProductVariant.fromJson(e as Map<String, dynamic>))
      .toList(),
  createdAt: DateTime.parse(json['createdAt'] as String),
  updatedAt: DateTime.parse(json['updatedAt'] as String),
);

Map<String, dynamic> _$ProductToJson(Product instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'description': instance.description,
  'sku': instance.sku,
  'price': instance.price,
  'costPrice': instance.costPrice,
  'stockQuantity': instance.stockQuantity,
  'minStockLevel': instance.minStockLevel,
  'isActive': instance.isActive,
  'imageUrl': instance.imageUrl,
  'category': instance.category,
  'brand': instance.brand,
  'variants': instance.variants,
  'createdAt': instance.createdAt.toIso8601String(),
  'updatedAt': instance.updatedAt.toIso8601String(),
};

Category _$CategoryFromJson(Map<String, dynamic> json) => Category(
  id: (json['id'] as num).toInt(),
  name: json['name'] as String,
  description: json['description'] as String?,
  imageUrl: json['imageUrl'] as String?,
  isActive: json['isActive'] as bool,
  createdAt: DateTime.parse(json['createdAt'] as String),
  updatedAt: DateTime.parse(json['updatedAt'] as String),
);

Map<String, dynamic> _$CategoryToJson(Category instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'description': instance.description,
  'imageUrl': instance.imageUrl,
  'isActive': instance.isActive,
  'createdAt': instance.createdAt.toIso8601String(),
  'updatedAt': instance.updatedAt.toIso8601String(),
};

Brand _$BrandFromJson(Map<String, dynamic> json) => Brand(
  id: (json['id'] as num).toInt(),
  name: json['name'] as String,
  description: json['description'] as String?,
  logoUrl: json['logoUrl'] as String?,
  isActive: json['isActive'] as bool,
  createdAt: DateTime.parse(json['createdAt'] as String),
  updatedAt: DateTime.parse(json['updatedAt'] as String),
);

Map<String, dynamic> _$BrandToJson(Brand instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'description': instance.description,
  'logoUrl': instance.logoUrl,
  'isActive': instance.isActive,
  'createdAt': instance.createdAt.toIso8601String(),
  'updatedAt': instance.updatedAt.toIso8601String(),
};

ProductVariant _$ProductVariantFromJson(Map<String, dynamic> json) =>
    ProductVariant(
      id: (json['id'] as num).toInt(),
      productId: (json['productId'] as num).toInt(),
      name: json['name'] as String,
      sku: json['sku'] as String?,
      priceAdjustment: (json['priceAdjustment'] as num?)?.toDouble(),
      stockQuantity: (json['stockQuantity'] as num).toInt(),
      attributes: Map<String, String>.from(json['attributes'] as Map),
      isActive: json['isActive'] as bool,
    );

Map<String, dynamic> _$ProductVariantToJson(ProductVariant instance) =>
    <String, dynamic>{
      'id': instance.id,
      'productId': instance.productId,
      'name': instance.name,
      'sku': instance.sku,
      'priceAdjustment': instance.priceAdjustment,
      'stockQuantity': instance.stockQuantity,
      'attributes': instance.attributes,
      'isActive': instance.isActive,
    };
