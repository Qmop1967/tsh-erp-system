// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'product_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Product _$ProductFromJson(Map<String, dynamic> json) => Product(
      id: (json['id'] as num?)?.toInt(),
      productCode: json['product_code'] as String?,
      name: json['name'] as String,
      description: json['description'] as String?,
      sku: json['sku'] as String?,
      price: (json['price'] as num).toDouble(),
      costPrice: (json['cost_price'] as num?)?.toDouble(),
      stockQuantity: (json['stock_quantity'] as num?)?.toInt(),
      minStockLevel: (json['min_stock_level'] as num?)?.toInt(),
      isActive: json['is_active'] as bool? ?? true,
      imageUrl: json['image_url'] as String?,
      categoryId: (json['category_id'] as num?)?.toInt(),
      categoryName: json['category_name'] as String?,
      unit: json['unit'] as String?,
      barcode: json['barcode'] as String?,
      taxRate: (json['tax_rate'] as num?)?.toDouble(),
      discountPercentage: (json['discount_percentage'] as num?)?.toDouble(),
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$ProductToJson(Product instance) => <String, dynamic>{
      'id': instance.id,
      'product_code': instance.productCode,
      'name': instance.name,
      'description': instance.description,
      'sku': instance.sku,
      'price': instance.price,
      'cost_price': instance.costPrice,
      'stock_quantity': instance.stockQuantity,
      'min_stock_level': instance.minStockLevel,
      'is_active': instance.isActive,
      'image_url': instance.imageUrl,
      'category_id': instance.categoryId,
      'category_name': instance.categoryName,
      'unit': instance.unit,
      'barcode': instance.barcode,
      'tax_rate': instance.taxRate,
      'discount_percentage': instance.discountPercentage,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
