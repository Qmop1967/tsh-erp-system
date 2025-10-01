// Core Inventory Models based on TSH ERP Master Development Plan

class InventoryItem {
  final String id;
  final String sku;
  final String barcode;
  final String nameEn;
  final String nameAr;
  final String categoryId;
  final String brand;
  final String unitOfMeasure;
  final List<ItemVariant> variants;
  final ABCClassification abcClass;
  final Map<String, double> purchaseCosts; // USD, IQD, CNY
  final List<double> salesPriceLists;
  final bool trackStock;
  final String? defaultSupplierId;
  final String? imageUrl;
  final DateTime createdAt;
  final DateTime updatedAt;

  InventoryItem({
    required this.id,
    required this.sku,
    required this.barcode,
    required this.nameEn,
    required this.nameAr,
    required this.categoryId,
    required this.brand,
    required this.unitOfMeasure,
    this.variants = const [],
    this.abcClass = ABCClassification.C,
    this.purchaseCosts = const {},
    this.salesPriceLists = const [],
    this.trackStock = true,
    this.defaultSupplierId,
    this.imageUrl,
    required this.createdAt,
    required this.updatedAt,
  });

  factory InventoryItem.fromJson(Map<String, dynamic> json) {
    return InventoryItem(
      id: json['id'],
      sku: json['sku'],
      barcode: json['barcode'],
      nameEn: json['name_en'],
      nameAr: json['name_ar'],
      categoryId: json['category_id'],
      brand: json['brand'],
      unitOfMeasure: json['unit_of_measure'],
      variants: (json['variants'] as List?)?.map((v) => ItemVariant.fromJson(v)).toList() ?? [],
      abcClass: ABCClassification.values.firstWhere(
        (e) => e.name == json['abc_class'],
        orElse: () => ABCClassification.C,
      ),
      purchaseCosts: Map<String, double>.from(json['purchase_costs'] ?? {}),
      salesPriceLists: List<double>.from(json['sales_price_lists'] ?? []),
      trackStock: json['track_stock'] ?? true,
      defaultSupplierId: json['default_supplier_id'],
      imageUrl: json['image_url'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sku': sku,
      'barcode': barcode,
      'name_en': nameEn,
      'name_ar': nameAr,
      'category_id': categoryId,
      'brand': brand,
      'unit_of_measure': unitOfMeasure,
      'variants': variants.map((v) => v.toJson()).toList(),
      'abc_class': abcClass.name,
      'purchase_costs': purchaseCosts,
      'sales_price_lists': salesPriceLists,
      'track_stock': trackStock,
      'default_supplier_id': defaultSupplierId,
      'image_url': imageUrl,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class ItemVariant {
  final String attribute; // color, size, capacity
  final String value;
  final String? additionalInfo;

  ItemVariant({
    required this.attribute,
    required this.value,
    this.additionalInfo,
  });

  factory ItemVariant.fromJson(Map<String, dynamic> json) {
    return ItemVariant(
      attribute: json['attribute'],
      value: json['value'],
      additionalInfo: json['additional_info'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'attribute': attribute,
      'value': value,
      'additional_info': additionalInfo,
    };
  }
}

enum ABCClassification { A, B, C }

class Warehouse {
  final String id;
  final String name;
  final String nameAr;
  final String address;
  final int capacity;
  final int currentUsage;
  final bool isActive;
  final WarehouseType type;
  final String? managerId;

  Warehouse({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.address,
    required this.capacity,
    required this.currentUsage,
    this.isActive = true,
    this.type = WarehouseType.main,
    this.managerId,
  });

  double get utilizationPercentage => (currentUsage / capacity) * 100;

  factory Warehouse.fromJson(Map<String, dynamic> json) {
    return Warehouse(
      id: json['id'],
      name: json['name'],
      nameAr: json['name_ar'],
      address: json['address'],
      capacity: json['capacity'],
      currentUsage: json['current_usage'],
      isActive: json['is_active'] ?? true,
      type: WarehouseType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => WarehouseType.main,
      ),
      managerId: json['manager_id'],
    );
  }
}

enum WarehouseType { main, retail, secondary, temporary }

class StockMovement {
  final String id;
  final String itemId;
  final String warehouseFromId;
  final String warehouseToId;
  final MovementType type;
  final double quantity;
  final double unitCost;
  final String? referenceNumber;
  final String? notes;
  final MovementStatus status;
  final String createdBy;
  final String? approvedBy;
  final DateTime createdAt;
  final DateTime? approvedAt;

  StockMovement({
    required this.id,
    required this.itemId,
    required this.warehouseFromId,
    required this.warehouseToId,
    required this.type,
    required this.quantity,
    required this.unitCost,
    this.referenceNumber,
    this.notes,
    this.status = MovementStatus.pending,
    required this.createdBy,
    this.approvedBy,
    required this.createdAt,
    this.approvedAt,
  });

  double get totalValue => quantity * unitCost;

  factory StockMovement.fromJson(Map<String, dynamic> json) {
    return StockMovement(
      id: json['id'],
      itemId: json['item_id'],
      warehouseFromId: json['warehouse_from_id'],
      warehouseToId: json['warehouse_to_id'],
      type: MovementType.values.firstWhere((e) => e.name == json['type']),
      quantity: json['quantity'].toDouble(),
      unitCost: json['unit_cost'].toDouble(),
      referenceNumber: json['reference_number'],
      notes: json['notes'],
      status: MovementStatus.values.firstWhere((e) => e.name == json['status']),
      createdBy: json['created_by'],
      approvedBy: json['approved_by'],
      createdAt: DateTime.parse(json['created_at']),
      approvedAt: json['approved_at'] != null ? DateTime.parse(json['approved_at']) : null,
    );
  }
}

enum MovementType { receipt, issue, transfer, adjustment }
enum MovementStatus { pending, approved, completed, cancelled }

class StockLevel {
  final String itemId;
  final String warehouseId;
  final double currentStock;
  final double reservedStock;
  final double availableStock;
  final double reorderPoint;
  final double maxStock;
  final DateTime lastUpdated;

  StockLevel({
    required this.itemId,
    required this.warehouseId,
    required this.currentStock,
    this.reservedStock = 0,
    required this.reorderPoint,
    required this.maxStock,
    required this.lastUpdated,
  }) : availableStock = currentStock - reservedStock;

  bool get isLowStock => currentStock <= reorderPoint;
  bool get isOutOfStock => currentStock <= 0;
  bool get isOverstocked => currentStock >= maxStock;

  factory StockLevel.fromJson(Map<String, dynamic> json) {
    return StockLevel(
      itemId: json['item_id'],
      warehouseId: json['warehouse_id'],
      currentStock: json['current_stock'].toDouble(),
      reservedStock: json['reserved_stock']?.toDouble() ?? 0,
      reorderPoint: json['reorder_point'].toDouble(),
      maxStock: json['max_stock'].toDouble(),
      lastUpdated: DateTime.parse(json['last_updated']),
    );
  }
}

class Category {
  final String id;
  final String nameEn;
  final String nameAr;
  final String? parentId;
  final String? description;
  final String? iconName;
  final int itemCount;
  final bool isActive;

  Category({
    required this.id,
    required this.nameEn,
    required this.nameAr,
    this.parentId,
    this.description,
    this.iconName,
    this.itemCount = 0,
    this.isActive = true,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      nameEn: json['name_en'],
      nameAr: json['name_ar'],
      parentId: json['parent_id'],
      description: json['description'],
      iconName: json['icon_name'],
      itemCount: json['item_count'] ?? 0,
      isActive: json['is_active'] ?? true,
    );
  }
}
