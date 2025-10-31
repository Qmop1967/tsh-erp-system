import 'dart:math';

class MockDataService {
  static final Random _random = Random();

  // Generate realistic mock inventory data
  static Map<String, dynamic> getInventoryData() {
    return {
      'totalInventoryValue': 285000.00 + (_random.nextDouble() * 50000),
      'stockTurnoverRatio': 3.8 + (_random.nextDouble() * 1.2),
      'lowStockItemsCount': 20 + _random.nextInt(15),
      'zeroStockItemsCount': 5 + _random.nextInt(8),
      'warehouseUtilization': 75.0 + (_random.nextDouble() * 15),
      'pendingShipments': 8 + _random.nextInt(12),
      'completedPackaging': 85 + _random.nextInt(20),
      'packageVariants': {
        'boxes': 140 + _random.nextInt(30),
        'bundles': 70 + _random.nextInt(25),
        'bags': 25 + _random.nextInt(20),
      },
    };
  }

  // Generate stock levels data
  static List<Map<String, dynamic>> getStockLevelsData() {
    final items = [
      'Phone Charger USB-C',
      'Bluetooth Headphones',
      'Phone Cases iPhone 14',
      'Screen Protectors',
      'Power Banks 10000mAh',
      'Wireless Earbuds',
      'Phone Stands',
      'Car Chargers',
      'Memory Cards 64GB',
      'Cable Organizers',
      'Phone Grips',
      'Tablet Cases',
      'Portable Speakers',
      'Phone Lens Attachments',
      'Charging Cables 3ft',
    ];

    return items.map((item) {
      final currentStock = 10 + _random.nextInt(200);
      final minStock = 20 + _random.nextInt(50);
      final status = currentStock < minStock ? 'Low Stock' : 
                    currentStock == 0 ? 'Out of Stock' : 'Normal';
      
      return {
        'itemName': item,
        'currentStock': currentStock,
        'minStock': minStock,
        'status': status,
        'value': currentStock * (15.0 + _random.nextDouble() * 85.0),
      };
    }).toList();
  }

  // Generate low stock alerts
  static List<Map<String, dynamic>> getLowStockAlerts() {
    final stockData = getStockLevelsData();
    return stockData.where((item) => 
      item['status'] == 'Low Stock' || item['status'] == 'Out of Stock'
    ).toList();
  }

  // Generate packaging summary data
  static Map<String, dynamic> getPackagingSummary() {
    return {
      'totalPackagesProcessed': 450 + _random.nextInt(200),
      'packagesInProgress': 25 + _random.nextInt(20),
      'packagesByType': {
        'Box (Small)': 120 + _random.nextInt(50),
        'Box (Medium)': 85 + _random.nextInt(40),
        'Box (Large)': 45 + _random.nextInt(30),
        'Bundle Pack': 70 + _random.nextInt(35),
        'Poly Bag': 130 + _random.nextInt(60),
      },
      'avgPackagingTime': '12.5 minutes',
      'packagingEfficiency': 85.5 + _random.nextDouble() * 10,
    };
  }

  // Generate shipment tracking data
  static List<Map<String, dynamic>> getShipmentTrackingData() {
    final statuses = ['Preparing', 'In Transit', 'Out for Delivery', 'Delivered', 'Delayed'];
    final destinations = ['Baghdad Central', 'Basra', 'Erbil', 'Najaf', 'Karbala', 'Mosul'];
    
    return List.generate(15, (index) {
      final shipmentId = 'SH${(1000 + index).toString()}';
      final destination = destinations[_random.nextInt(destinations.length)];
      final status = statuses[_random.nextInt(statuses.length)];
      final packages = 1 + _random.nextInt(8);
      
      return {
        'shipmentId': shipmentId,
        'destination': destination,
        'status': status,
        'packages': packages,
        'estimatedDelivery': DateTime.now().add(Duration(days: 1 + _random.nextInt(5))),
        'trackingNumber': 'TSH${1000000 + _random.nextInt(999999)}',
      };
    });
  }

  // Generate warehouse utilization data
  static Map<String, dynamic> getWarehouseUtilizationData() {
    return {
      'mainWarehouse': {
        'name': 'Main Warehouse',
        'capacity': 10000,
        'used': 7500 + _random.nextInt(1500),
        'utilizationPercentage': 75.0 + _random.nextDouble() * 15,
        'categories': {
          'Electronics': 4500 + _random.nextInt(500),
          'Accessories': 2000 + _random.nextInt(300),
          'Cables & Chargers': 800 + _random.nextInt(200),
          'Packaging Materials': 200 + _random.nextInt(100),
        },
      },
      'retailShop': {
        'name': 'Retail Shop Storage',
        'capacity': 2000,
        'used': 900 + _random.nextInt(600),
        'utilizationPercentage': 45.0 + _random.nextDouble() * 30,
        'categories': {
          'Display Items': 400 + _random.nextInt(200),
          'Stock Items': 300 + _random.nextInt(250),
          'New Arrivals': 200 + _random.nextInt(150),
        },
      },
      'totalUtilization': 68.5 + _random.nextDouble() * 15,
      'availableSpace': 3600 + _random.nextInt(1000),
      'recommendations': [
        'Optimize storage layout in electronics section',
        'Consider expansion if utilization exceeds 85%',
        'Relocate slow-moving items to reduce congestion',
      ],
    };
  }

  // Generate movement history data
  static List<Map<String, dynamic>> getMovementHistoryData() {
    final movementTypes = ['IN', 'OUT', 'TRANSFER', 'ADJUSTMENT'];
    final sources = ['Supplier A', 'Supplier B', 'Retail Shop', 'Customer Return', 'Adjustment'];
    
    return List.generate(20, (index) {
      final type = movementTypes[_random.nextInt(movementTypes.length)];
      final source = sources[_random.nextInt(sources.length)];
      final quantity = 1 + _random.nextInt(50);
      final item = getStockLevelsData()[_random.nextInt(10)]['itemName'];
      
      return {
        'id': 'MV${(10000 + index).toString()}',
        'type': type,
        'item': item,
        'quantity': quantity,
        'source': source,
        'timestamp': DateTime.now().subtract(Duration(hours: _random.nextInt(720))),
        'reference': 'REF${1000 + _random.nextInt(9999)}',
        'user': 'TSH_User_${1 + _random.nextInt(5)}',
      };
    });
  }

  // Generate KPI summary
  static Map<String, dynamic> getKPISummary() {
    return {
      'dailyOrders': 28 + _random.nextInt(15),
      'pendingOrders': 8 + _random.nextInt(10),
      'completedShipments': 22 + _random.nextInt(12),
      'lowStockAlerts': 15 + _random.nextInt(10),
      'totalRevenue': 145000.0 + (_random.nextDouble() * 50000),
      'topSellingCategory': 'Phone Accessories',
      'warehouseEfficiency': 87.5 + _random.nextDouble() * 10,
    };
  }
}
