class User {
  final String id;
  final String email;
  final String? zohoCustomerId;
  final String? zohoContactId;
  final String? fullName;
  final String? phone;
  final String? zohoPricelistId;
  final DateTime createdAt;
  final DateTime updatedAt;

  const User({
    required this.id,
    required this.email,
    this.zohoCustomerId,
    this.zohoContactId,
    this.fullName,
    this.phone,
    this.zohoPricelistId,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      zohoCustomerId: json['zoho_customer_id'] as String?,
      zohoContactId: json['zoho_contact_id'] as String?,
      fullName: json['full_name'] as String?,
      phone: json['phone'] as String?,
      zohoPricelistId: json['zoho_pricelist_id'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'zoho_customer_id': zohoCustomerId,
      'zoho_contact_id': zohoContactId,
      'full_name': fullName,
      'phone': phone,
      'zoho_pricelist_id': zohoPricelistId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
