// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'customer_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Customer _$CustomerFromJson(Map<String, dynamic> json) => Customer(
      id: (json['id'] as num?)?.toInt(),
      customerCode: json['customer_code'] as String?,
      name: json['name'] as String,
      companyName: json['company_name'] as String?,
      phone: json['phone'] as String?,
      email: json['email'] as String?,
      address: json['address'] as String?,
      city: json['city'] as String?,
      country: json['country'] as String?,
      taxNumber: json['tax_number'] as String?,
      creditLimit: (json['credit_limit'] as num?)?.toDouble(),
      paymentTerms: (json['payment_terms'] as num?)?.toInt(),
      discountPercentage: (json['discount_percentage'] as num?)?.toDouble(),
      currency: json['currency'] as String? ?? 'IQD',
      portalLanguage: json['portal_language'] as String? ?? 'en',
      salespersonId: (json['salesperson_id'] as num?)?.toInt(),
      isActive: json['is_active'] as bool? ?? true,
      notes: json['notes'] as String?,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$CustomerToJson(Customer instance) => <String, dynamic>{
      'id': instance.id,
      'customer_code': instance.customerCode,
      'name': instance.name,
      'company_name': instance.companyName,
      'phone': instance.phone,
      'email': instance.email,
      'address': instance.address,
      'city': instance.city,
      'country': instance.country,
      'tax_number': instance.taxNumber,
      'credit_limit': instance.creditLimit,
      'payment_terms': instance.paymentTerms,
      'discount_percentage': instance.discountPercentage,
      'currency': instance.currency,
      'portal_language': instance.portalLanguage,
      'salesperson_id': instance.salespersonId,
      'is_active': instance.isActive,
      'notes': instance.notes,
      'created_at': instance.createdAt?.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
