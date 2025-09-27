import 'package:json_annotation/json_annotation.dart';

part 'customer_model.g.dart';

@JsonSerializable()
class Customer {
  final int? id;
  @JsonKey(name: 'customer_code')
  final String? customerCode;
  final String name;
  @JsonKey(name: 'company_name')
  final String? companyName;
  final String? phone;
  final String? email;
  final String? address;
  final String? city;
  final String? country;
  @JsonKey(name: 'tax_number')
  final String? taxNumber;
  @JsonKey(name: 'credit_limit')
  final double? creditLimit;
  @JsonKey(name: 'payment_terms')
  final int? paymentTerms;
  @JsonKey(name: 'discount_percentage')
  final double? discountPercentage;
  final String? currency;
  @JsonKey(name: 'portal_language')
  final String? portalLanguage;
  @JsonKey(name: 'salesperson_id')
  final int? salespersonId;
  @JsonKey(name: 'is_active')
  final bool isActive;
  final String? notes;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  const Customer({
    this.id,
    this.customerCode,
    required this.name,
    this.companyName,
    this.phone,
    this.email,
    this.address,
    this.city,
    this.country,
    this.taxNumber,
    this.creditLimit,
    this.paymentTerms,
    this.discountPercentage,
    this.currency = 'IQD',
    this.portalLanguage = 'en',
    this.salespersonId,
    this.isActive = true,
    this.notes,
    this.createdAt,
    this.updatedAt,
  });

  factory Customer.fromJson(Map<String, dynamic> json) => _$CustomerFromJson(json);

  Map<String, dynamic> toJson() => _$CustomerToJson(this);

  Customer copyWith({
    int? id,
    String? customerCode,
    String? name,
    String? companyName,
    String? phone,
    String? email,
    String? address,
    String? city,
    String? country,
    String? taxNumber,
    double? creditLimit,
    int? paymentTerms,
    double? discountPercentage,
    String? currency,
    String? portalLanguage,
    int? salespersonId,
    bool? isActive,
    String? notes,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Customer(
      id: id ?? this.id,
      customerCode: customerCode ?? this.customerCode,
      name: name ?? this.name,
      companyName: companyName ?? this.companyName,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      address: address ?? this.address,
      city: city ?? this.city,
      country: country ?? this.country,
      taxNumber: taxNumber ?? this.taxNumber,
      creditLimit: creditLimit ?? this.creditLimit,
      paymentTerms: paymentTerms ?? this.paymentTerms,
      discountPercentage: discountPercentage ?? this.discountPercentage,
      currency: currency ?? this.currency,
      portalLanguage: portalLanguage ?? this.portalLanguage,
      salespersonId: salespersonId ?? this.salespersonId,
      isActive: isActive ?? this.isActive,
      notes: notes ?? this.notes,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Customer(id: $id, name: $name, phone: $phone, email: $email)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Customer && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
