class POSProduct {
  final String id;
  final String name;
  final String nameAr;
  final String category;
  final double price;
  final int stock;
  final String sku;
  final String? description;
  final String? image;

  POSProduct({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.category,
    required this.price,
    required this.stock,
    required this.sku,
    this.description,
    this.image,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'name_ar': nameAr,
      'category': category,
      'price': price,
      'stock': stock,
      'sku': sku,
      'description': description,
      'image': image,
    };
  }
}
