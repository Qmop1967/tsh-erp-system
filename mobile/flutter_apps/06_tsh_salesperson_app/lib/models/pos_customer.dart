class POSCustomer {
  final String id;
  final String name;
  final String phone;
  final String? email;
  final String? address;
  final double balance;

  POSCustomer({
    required this.id,
    required this.name,
    required this.phone,
    this.email,
    this.address,
    this.balance = 0,
  });

  factory POSCustomer.fromJson(Map<String, dynamic> json) {
    return POSCustomer(
      id: json['id']?.toString() ?? '0',
      name: json['name'] ?? json['full_name'] ?? '',
      phone: json['phone'] ?? json['phone_number'] ?? '',
      email: json['email'],
      address: json['address'] ?? json['address_ar'] ?? json['address_en'],
      balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'phone': phone,
      'email': email,
      'address': address,
      'balance': balance,
    };
  }
}
