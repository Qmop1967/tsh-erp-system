// ============================================================================
// TSH ERP - BFF API Client for Flutter
// Complete API client for all 11 mobile apps
// ============================================================================

import 'dart:convert';
import 'package:http/http.dart' as http;

/// BFF API Client for TSH ERP System
/// Provides optimized endpoints for all 11 Flutter mobile apps
class BffApiClient {
  final String baseUrl;
  final String? authToken;

  BffApiClient({
    required this.baseUrl,
    this.authToken,
  });

  /// Base URL for BFF endpoints
  String get bffBaseUrl => '$baseUrl/api/bff/mobile';

  /// Get auth headers
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (authToken != null) 'Authorization': 'Bearer $authToken',
  };

  /// Generic GET request
  Future<Map<String, dynamic>> _get(String endpoint, {Map<String, dynamic>? params}) async {
    final uri = Uri.parse('$bffBaseUrl$endpoint').replace(
      queryParameters: params?.map((key, value) => MapEntry(key, value.toString())),
    );

    final response = await http.get(uri, headers: _headers);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw BffApiException(
        statusCode: response.statusCode,
        message: 'API request failed',
        body: response.body,
      );
    }
  }

  /// Generic POST request
  Future<Map<String, dynamic>> _post(String endpoint, {Map<String, dynamic>? body}) async {
    final uri = Uri.parse('$bffBaseUrl$endpoint');

    final response = await http.post(
      uri,
      headers: _headers,
      body: body != null ? json.encode(body) : null,
    );

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw BffApiException(
        statusCode: response.statusCode,
        message: 'API request failed',
        body: response.body,
      );
    }
  }

  // ============================================================================
  // CONSUMER APP (10) - 37 Endpoints
  // ============================================================================

  /// Get home screen data (featured products, banners, etc.)
  Future<ConsumerHomeResponse> getHome({int? customerId, int? branchId}) async {
    final response = await _get('/home', params: {
      if (customerId != null) 'customer_id': customerId,
      if (branchId != null) 'branch_id': branchId,
    });
    return ConsumerHomeResponse.fromJson(response);
  }

  /// Search products
  Future<ProductSearchResponse> searchProducts({
    required String query,
    int page = 1,
    int pageSize = 20,
    int? categoryId,
    double? minPrice,
    double? maxPrice,
  }) async {
    final response = await _get('/products/search', params: {
      'q': query,
      'page': page,
      'page_size': pageSize,
      if (categoryId != null) 'category_id': categoryId,
      if (minPrice != null) 'min_price': minPrice,
      if (maxPrice != null) 'max_price': maxPrice,
    });
    return ProductSearchResponse.fromJson(response);
  }

  /// Get product details
  Future<ProductDetail> getProduct(int productId, {int? customerId}) async {
    final response = await _get('/products/$productId', params: {
      if (customerId != null) 'customer_id': customerId,
    });
    return ProductDetail.fromJson(response);
  }

  /// Get shopping cart
  Future<Cart> getCart(int customerId) async {
    final response = await _get('/cart', params: {'customer_id': customerId});
    return Cart.fromJson(response['data']);
  }

  /// Add item to cart
  Future<Map<String, dynamic>> addToCart({
    required int customerId,
    required int productId,
    required int quantity,
  }) async {
    return await _post('/cart/add', body: {
      'customer_id': customerId,
      'product_id': productId,
      'quantity': quantity,
    });
  }

  /// Update cart item quantity
  Future<Map<String, dynamic>> updateCartItem({
    required int itemId,
    required int customerId,
    required int quantity,
  }) async {
    return await _post('/cart/item/$itemId', body: {
      'customer_id': customerId,
      'quantity': quantity,
    });
  }

  /// Get wishlist
  Future<WishlistResponse> getWishlist(int customerId, {int page = 1}) async {
    final response = await _get('/wishlist', params: {
      'customer_id': customerId,
      'page': page,
    });
    return WishlistResponse.fromJson(response);
  }

  /// Get customer profile
  Future<CustomerProfile> getProfile(int customerId) async {
    final response = await _get('/profile', params: {'customer_id': customerId});
    return CustomerProfile.fromJson(response['data']);
  }

  /// Get order history
  Future<OrderHistoryResponse> getOrderHistory({
    required int customerId,
    String? status,
    int page = 1,
  }) async {
    final response = await _get('/orders/history', params: {
      'customer_id': customerId,
      if (status != null) 'status': status,
      'page': page,
    });
    return OrderHistoryResponse.fromJson(response);
  }

  /// Get product reviews
  Future<ReviewsResponse> getProductReviews({
    required int productId,
    int? rating,
    int page = 1,
  }) async {
    final response = await _get('/products/$productId/reviews', params: {
      if (rating != null) 'rating': rating,
      'page': page,
    });
    return ReviewsResponse.fromJson(response);
  }

  // ============================================================================
  // SALESPERSON APP (06) - 13 Endpoints
  // ============================================================================

  /// Get salesperson dashboard
  Future<SalespersonDashboard> getSalespersonDashboard({
    required int salespersonId,
    String dateRange = 'today',
  }) async {
    final response = await _get('/salesperson/dashboard', params: {
      'salesperson_id': salespersonId,
      'date_range': dateRange,
    });
    return SalespersonDashboard.fromJson(response['data']);
  }

  /// Get salesperson customers
  Future<CustomersResponse> getSalespersonCustomers({
    required int salespersonId,
    String? search,
    int page = 1,
  }) async {
    final response = await _get('/salesperson/customers', params: {
      'salesperson_id': salespersonId,
      if (search != null) 'search': search,
      'page': page,
    });
    return CustomersResponse.fromJson(response);
  }

  /// Get salesperson visits
  Future<VisitsResponse> getSalespersonVisits({
    required int salespersonId,
    String? date,
  }) async {
    final response = await _get('/salesperson/visits', params: {
      'salesperson_id': salespersonId,
      if (date != null) 'date': date,
    });
    return VisitsResponse.fromJson(response);
  }

  /// Start visit with GPS
  Future<Map<String, dynamic>> startVisit({
    required int salespersonId,
    required int customerId,
    required double latitude,
    required double longitude,
  }) async {
    return await _post('/salesperson/visits/start', body: {
      'salesperson_id': salespersonId,
      'customer_id': customerId,
      'gps_location': '$latitude,$longitude',
    });
  }

  // ============================================================================
  // POS APP (07) - 16 Endpoints
  // ============================================================================

  /// Get POS dashboard
  Future<POSDashboard> getPOSDashboard({
    required int cashierId,
    int? branchId,
  }) async {
    final response = await _get('/pos/dashboard', params: {
      'cashier_id': cashierId,
      if (branchId != null) 'branch_id': branchId,
    });
    return POSDashboard.fromJson(response['data']);
  }

  /// Start POS transaction
  Future<POSTransaction> startTransaction({
    required int cashierId,
    required int branchId,
  }) async {
    final response = await _post('/pos/transaction/start', body: {
      'cashier_id': cashierId,
      'branch_id': branchId,
    });
    return POSTransaction.fromJson(response['data']);
  }

  // ============================================================================
  // ADMIN APP (01) - 25 Endpoints
  // ============================================================================

  /// Get admin dashboard
  Future<AdminDashboard> getAdminDashboard(int adminId) async {
    final response = await _get('/admin/dashboard', params: {
      'admin_id': adminId,
    });
    return AdminDashboard.fromJson(response['data']);
  }

  /// Get users list
  Future<UsersResponse> getUsers({
    String? search,
    String? role,
    int page = 1,
  }) async {
    final response = await _get('/admin/users', params: {
      if (search != null) 'search': search,
      if (role != null) 'role': role,
      'page': page,
    });
    return UsersResponse.fromJson(response);
  }

  // ============================================================================
  // INVENTORY APP (05) - 20 Endpoints
  // ============================================================================

  /// Get inventory dashboard
  Future<InventoryDashboard> getInventoryDashboard(int userId) async {
    final response = await _get('/inventory/dashboard', params: {
      'user_id': userId,
    });
    return InventoryDashboard.fromJson(response['data']);
  }

  /// Get stock levels
  Future<StockLevelsResponse> getStockLevels({
    required int branchId,
    bool lowStockOnly = false,
  }) async {
    final response = await _get('/inventory/stock-levels', params: {
      'branch_id': branchId,
      'low_stock_only': lowStockOnly,
    });
    return StockLevelsResponse.fromJson(response);
  }

  // ============================================================================
  // ACCOUNTING APP (03) - 30 Endpoints
  // ============================================================================

  /// Get accounting dashboard
  Future<AccountingDashboard> getAccountingDashboard(int userId) async {
    final response = await _get('/accounting/dashboard', params: {
      'user_id': userId,
    });
    return AccountingDashboard.fromJson(response['data']);
  }

  /// Get balance sheet
  Future<BalanceSheet> getBalanceSheet(String asOfDate) async {
    final response = await _get('/accounting/balance-sheet', params: {
      'as_of_date': asOfDate,
    });
    return BalanceSheet.fromJson(response['data']);
  }

  // ============================================================================
  // HR APP (04) - 25 Endpoints
  // ============================================================================

  /// Get HR dashboard
  Future<HRDashboard> getHRDashboard(int userId) async {
    final response = await _get('/hr/dashboard', params: {
      'user_id': userId,
    });
    return HRDashboard.fromJson(response['data']);
  }

  /// Mark attendance with GPS
  Future<Map<String, dynamic>> markAttendance({
    required int employeeId,
    required double latitude,
    required double longitude,
  }) async {
    return await _post('/hr/attendance/mark', body: {
      'employee_id': employeeId,
      'gps_location': '$latitude,$longitude',
    });
  }

  // ============================================================================
  // SECURITY APP (02) - 20 Endpoints
  // ============================================================================

  /// Get security dashboard
  Future<SecurityDashboard> getSecurityDashboard() async {
    final response = await _get('/security/dashboard');
    return SecurityDashboard.fromJson(response['data']);
  }

  /// Get security threats
  Future<ThreatsResponse> getSecurityThreats({
    String? severity,
    int page = 1,
  }) async {
    final response = await _get('/security/threats', params: {
      if (severity != null) 'severity': severity,
      'page': page,
    });
    return ThreatsResponse.fromJson(response);
  }

  // ============================================================================
  // PARTNER NETWORK APP (08) - 15 Endpoints
  // ============================================================================

  /// Get partner dashboard
  Future<PartnerDashboard> getPartnerDashboard(int partnerId) async {
    final response = await _get('/partner/dashboard', params: {
      'partner_id': partnerId,
    });
    return PartnerDashboard.fromJson(response['data']);
  }

  // ============================================================================
  // WHOLESALE CLIENT APP (09) - 18 Endpoints
  // ============================================================================

  /// Get wholesale dashboard
  Future<WholesaleDashboard> getWholesaleDashboard(int clientId) async {
    final response = await _get('/wholesale/dashboard', params: {
      'client_id': clientId,
    });
    return WholesaleDashboard.fromJson(response['data']);
  }

  // ============================================================================
  // ASO APP (11) - 20 Endpoints
  // ============================================================================

  /// Get ASO dashboard
  Future<ASODashboard> getASODashboard({
    required int userId,
    required String role,
  }) async {
    final response = await _get('/aso/dashboard', params: {
      'user_id': userId,
      'role': role,
    });
    return ASODashboard.fromJson(response['data']);
  }

  /// Get service requests
  Future<ServiceRequestsResponse> getServiceRequests({
    required int userId,
    String? status,
    int page = 1,
  }) async {
    final response = await _get('/aso/service-requests', params: {
      'user_id': userId,
      if (status != null) 'status': status,
      'page': page,
    });
    return ServiceRequestsResponse.fromJson(response);
  }
}

// ============================================================================
// API Exception
// ============================================================================

class BffApiException implements Exception {
  final int statusCode;
  final String message;
  final String? body;

  BffApiException({
    required this.statusCode,
    required this.message,
    this.body,
  });

  @override
  String toString() => 'BffApiException: $message (Status: $statusCode)';
}

// ============================================================================
// Response Models (Placeholder - implement based on your schema)
// ============================================================================

class ConsumerHomeResponse {
  final bool success;
  final Map<String, dynamic> data;

  ConsumerHomeResponse({required this.success, required this.data});

  factory ConsumerHomeResponse.fromJson(Map<String, dynamic> json) {
    return ConsumerHomeResponse(
      success: json['success'],
      data: json['data'],
    );
  }
}

class ProductSearchResponse {
  final bool success;
  final List<dynamic> products;
  final int total;

  ProductSearchResponse({
    required this.success,
    required this.products,
    required this.total,
  });

  factory ProductSearchResponse.fromJson(Map<String, dynamic> json) {
    return ProductSearchResponse(
      success: json['success'],
      products: json['data']['products'] ?? [],
      total: json['data']['total'] ?? 0,
    );
  }
}

class ProductDetail {
  final int id;
  final String name;
  final double price;

  ProductDetail({
    required this.id,
    required this.name,
    required this.price,
  });

  factory ProductDetail.fromJson(Map<String, dynamic> json) {
    final data = json['data'];
    return ProductDetail(
      id: data['id'],
      name: data['name'],
      price: data['price'].toDouble(),
    );
  }
}

class Cart {
  final List<dynamic> items;
  final Map<String, dynamic> totals;

  Cart({required this.items, required this.totals});

  factory Cart.fromJson(Map<String, dynamic> json) {
    return Cart(
      items: json['items'] ?? [],
      totals: json['totals'] ?? {},
    );
  }
}

class WishlistResponse {
  final List<dynamic> items;
  final int total;

  WishlistResponse({required this.items, required this.total});

  factory WishlistResponse.fromJson(Map<String, dynamic> json) {
    return WishlistResponse(
      items: json['data']['items'] ?? [],
      total: json['data']['total'] ?? 0,
    );
  }
}

class CustomerProfile {
  final int id;
  final String name;
  final String email;

  CustomerProfile({
    required this.id,
    required this.name,
    required this.email,
  });

  factory CustomerProfile.fromJson(Map<String, dynamic> json) {
    return CustomerProfile(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    );
  }
}

class OrderHistoryResponse {
  final List<dynamic> orders;
  final int total;

  OrderHistoryResponse({required this.orders, required this.total});

  factory OrderHistoryResponse.fromJson(Map<String, dynamic> json) {
    return OrderHistoryResponse(
      orders: json['data']['orders'] ?? [],
      total: json['data']['total'] ?? 0,
    );
  }
}

class ReviewsResponse {
  final List<dynamic> reviews;
  final int total;
  final double averageRating;

  ReviewsResponse({
    required this.reviews,
    required this.total,
    required this.averageRating,
  });

  factory ReviewsResponse.fromJson(Map<String, dynamic> json) {
    return ReviewsResponse(
      reviews: json['data']['reviews'] ?? [],
      total: json['data']['total'] ?? 0,
      averageRating: json['data']['average_rating']?.toDouble() ?? 0.0,
    );
  }
}

// Salesperson models
class SalespersonDashboard {
  final Map<String, dynamic> performance;
  final List<dynamic> recentOrders;

  SalespersonDashboard({
    required this.performance,
    required this.recentOrders,
  });

  factory SalespersonDashboard.fromJson(Map<String, dynamic> json) {
    return SalespersonDashboard(
      performance: json['performance'] ?? {},
      recentOrders: json['recent_orders'] ?? [],
    );
  }
}

class CustomersResponse {
  final List<dynamic> customers;
  final int total;

  CustomersResponse({required this.customers, required this.total});

  factory CustomersResponse.fromJson(Map<String, dynamic> json) {
    return CustomersResponse(
      customers: json['data']['customers'] ?? [],
      total: json['data']['total'] ?? 0,
    );
  }
}

class VisitsResponse {
  final List<dynamic> visits;
  final int total;

  VisitsResponse({required this.visits, required this.total});

  factory VisitsResponse.fromJson(Map<String, dynamic> json) {
    return VisitsResponse(
      visits: json['data']['visits'] ?? [],
      total: json['data']['total'] ?? 0,
    );
  }
}

// POS models
class POSDashboard {
  final Map<String, dynamic> session;
  final Map<String, dynamic> sales;

  POSDashboard({required this.session, required this.sales});

  factory POSDashboard.fromJson(Map<String, dynamic> json) {
    return POSDashboard(
      session: json['current_session'] ?? {},
      sales: json['sales_summary'] ?? {},
    );
  }
}

class POSTransaction {
  final String transactionId;
  final Map<String, dynamic> cart;

  POSTransaction({required this.transactionId, required this.cart});

  factory POSTransaction.fromJson(Map<String, dynamic> json) {
    return POSTransaction(
      transactionId: json['transaction_id'],
      cart: json['cart'] ?? {},
    );
  }
}

// Other app models (placeholders)
class AdminDashboard {
  final Map<String, dynamic> data;
  AdminDashboard({required this.data});
  factory AdminDashboard.fromJson(Map<String, dynamic> json) => AdminDashboard(data: json);
}

class UsersResponse {
  final List<dynamic> users;
  final int total;
  UsersResponse({required this.users, required this.total});
  factory UsersResponse.fromJson(Map<String, dynamic> json) => UsersResponse(
    users: json['data']['users'] ?? [],
    total: json['data']['total'] ?? 0,
  );
}

class InventoryDashboard {
  final Map<String, dynamic> data;
  InventoryDashboard({required this.data});
  factory InventoryDashboard.fromJson(Map<String, dynamic> json) => InventoryDashboard(data: json);
}

class StockLevelsResponse {
  final List<dynamic> items;
  final int total;
  StockLevelsResponse({required this.items, required this.total});
  factory StockLevelsResponse.fromJson(Map<String, dynamic> json) => StockLevelsResponse(
    items: json['data']['items'] ?? [],
    total: json['data']['total'] ?? 0,
  );
}

class AccountingDashboard {
  final Map<String, dynamic> data;
  AccountingDashboard({required this.data});
  factory AccountingDashboard.fromJson(Map<String, dynamic> json) => AccountingDashboard(data: json);
}

class BalanceSheet {
  final Map<String, dynamic> data;
  BalanceSheet({required this.data});
  factory BalanceSheet.fromJson(Map<String, dynamic> json) => BalanceSheet(data: json);
}

class HRDashboard {
  final Map<String, dynamic> data;
  HRDashboard({required this.data});
  factory HRDashboard.fromJson(Map<String, dynamic> json) => HRDashboard(data: json);
}

class SecurityDashboard {
  final Map<String, dynamic> data;
  SecurityDashboard({required this.data});
  factory SecurityDashboard.fromJson(Map<String, dynamic> json) => SecurityDashboard(data: json);
}

class ThreatsResponse {
  final List<dynamic> threats;
  final int total;
  ThreatsResponse({required this.threats, required this.total});
  factory ThreatsResponse.fromJson(Map<String, dynamic> json) => ThreatsResponse(
    threats: json['data']['threats'] ?? [],
    total: json['data']['total'] ?? 0,
  );
}

class PartnerDashboard {
  final Map<String, dynamic> data;
  PartnerDashboard({required this.data});
  factory PartnerDashboard.fromJson(Map<String, dynamic> json) => PartnerDashboard(data: json);
}

class WholesaleDashboard {
  final Map<String, dynamic> data;
  WholesaleDashboard({required this.data});
  factory WholesaleDashboard.fromJson(Map<String, dynamic> json) => WholesaleDashboard(data: json);
}

class ASODashboard {
  final Map<String, dynamic> data;
  ASODashboard({required this.data});
  factory ASODashboard.fromJson(Map<String, dynamic> json) => ASODashboard(data: json);
}

class ServiceRequestsResponse {
  final List<dynamic> requests;
  final int total;
  ServiceRequestsResponse({required this.requests, required this.total});
  factory ServiceRequestsResponse.fromJson(Map<String, dynamic> json) => ServiceRequestsResponse(
    requests: json['data']['requests'] ?? [],
    total: json['data']['total'] ?? 0,
  );
}
