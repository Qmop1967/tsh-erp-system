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
