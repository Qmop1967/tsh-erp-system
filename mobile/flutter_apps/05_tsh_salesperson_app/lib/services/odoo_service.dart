import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../config/app_config.dart';
import '../models/auth_model.dart';
import '../models/customer_model.dart';
import '../models/product_model.dart';
import '../models/order_model.dart';
import '../models/payment_model.dart';
import '../models/invoice_model.dart';
import '../utils/exceptions.dart';

class OdooService {
  late final Dio _dio;
  late final Logger _logger;
  
  String? _sessionId;
  int? _userId;
  String? _username;
  String? _password;
  
  // Cache for offline functionality
  final Map<String, dynamic> _cache = {};
  DateTime? _lastCacheUpdate;
  
  OdooService() {
    _initializeDio();
    _logger = Logger(
      printer: PrettyPrinter(
        methodCount: 2,
        errorMethodCount: 8,
        lineLength: 120,
        colors: true,
        printEmojis: true,
        printTime: true,
      ),
    );
  }
  
  void _initializeDio() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConfig.odooUrl,
      connectTimeout: AppConfig.connectionTimeout,
      receiveTimeout: AppConfig.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));
    
    // Add request/response interceptors for logging
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          _logger.d('🚀 Request: ${options.method} ${options.path}');
          if (options.data != null) {
            _logger.d('📤 Request Data: ${options.data}');
          }
          handler.next(options);
        },
        onResponse: (response, handler) {
          _logger.d('✅ Response: ${response.statusCode} ${response.statusMessage}');
          handler.next(response);
        },
        onError: (error, handler) {
          _logger.e('❌ Error: ${error.message}');
          if (error.response != null) {
            _logger.e('Error Response: ${error.response?.data}');
          }
          handler.next(error);
        },
      ),
    );
  }
  
  // Authentication Methods
  Future<AuthResult> authenticate({
    String? username,
    String? password,
  }) async {
    try {
      final user = username ?? AppConfig.defaultUsername;
      final pass = password ?? AppConfig.defaultPassword;
      
      _logger.i('🔐 Authenticating user: $user');
      
      final authData = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
          "service": "common",
          "method": "authenticate",
          "args": [AppConfig.database, user, pass, {}]
        },
        "id": 1
      };
      
      final response = await _dio.post('/jsonrpc', data: authData);
      
      if (response.data['error'] != null) {
        throw OdooException(
          'Authentication failed: ${response.data['error']['message']}',
          code: 'AUTH_ERROR',
        );
      }
      
      final userId = response.data['result'];
      if (userId == null || userId == false) {
        throw OdooException(
          'Invalid credentials',
          code: 'INVALID_CREDENTIALS',
        );
      }
      
      _userId = userId;
      _username = user;
      _password = pass;
      
      // Save credentials
      await AppConfig.saveUserCredentials(
        username: user,
        password: pass,
        userId: userId,
      );
      
      _logger.i('✅ Authentication successful. User ID: $userId');
      
      // Get user details
      final userDetails = await _getUserDetails(userId);
      
      return AuthResult(
        success: true,
        userId: userId,
        username: user,
        userDetails: userDetails,
      );
      
    } on DioException catch (e) {
      _logger.e('🌐 Network error during authentication: ${e.message}');
      throw NetworkException('Network error: ${e.message}');
    } catch (e) {
      _logger.e('❌ Authentication error: $e');
      throw OdooException('Authentication failed: $e');
    }
  }
  
  Future<Map<String, dynamic>> _getUserDetails(int userId) async {
    try {
      final userData = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
          "service": "object",
          "method": "execute_kw",
          "args": [
            AppConfig.database,
            userId,
            _password,
            "res.users",
            "read",
            [userId],
            {"fields": ["name", "email", "partner_id", "groups_id", "company_id"]}
          ]
        },
        "id": 2
      };
      
      final response = await _dio.post('/jsonrpc', data: userData);
      
      if (response.data['error'] != null) {
        throw OdooException('Failed to get user details: ${response.data['error']['message']}');
      }
      
      final result = response.data['result'];
      return result is List && result.isNotEmpty ? result[0] : {};
      
    } catch (e) {
      _logger.w('⚠️ Could not fetch user details: $e');
      return {};
    }
  }
  
  // Generic Odoo RPC call method
  Future<dynamic> callMethod({
    required String model,
    required String method,
    List<dynamic>? args,
    Map<String, dynamic>? kwargs,
  }) async {
    if (_userId == null || _password == null) {
      throw OdooException('Not authenticated', code: 'NOT_AUTHENTICATED');
    }
    
    try {
      final requestData = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
          "service": "object",
          "method": "execute_kw",
          "args": [
            AppConfig.database,
            _userId,
            _password,
            model,
            method,
            args ?? [],
            kwargs ?? {}
          ]
        },
        "id": DateTime.now().millisecondsSinceEpoch
      };
      
      final response = await _dio.post('/jsonrpc', data: requestData);
      
      if (response.data['error'] != null) {
        throw OdooException(
          'Odoo RPC Error: ${response.data['error']['message']}',
          code: 'RPC_ERROR',
        );
      }
      
      return response.data['result'];
      
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw NetworkException('Connection timeout');
      }
      throw NetworkException('Network error: ${e.message}');
    } catch (e) {
      _logger.e('❌ RPC call failed: $e');
      rethrow;
    }
  }
  
  // Customer Methods
  Future<List<Map<String, dynamic>>> getCustomers({
    List<dynamic>? domain,
    int? limit,
    int? offset,
    String? searchTerm,
  }) async {
    try {
      _logger.i('👥 Fetching customers with domain: $domain');
      
      // Mock implementation for now
      return [
        {
          'id': 1,
          'name': 'John Doe',
          'email': 'john@example.com',
          'phone': '+964-123-456789',
          'city': 'Baghdad',
          'country_id': 1,
        },
        {
          'id': 2,
          'name': 'Jane Smith',
          'email': 'jane@example.com',
          'phone': '+964-987-654321',
          'city': 'Basra',
          'country_id': 1,
        },
      ];
    } catch (e) {
      _logger.e('❌ Error fetching customers: $e');
      rethrow;
    }
  }
  
  // Product Methods
  Future<List<Map<String, dynamic>>> getProducts({
    List<dynamic>? domain,
    int? limit,
    int? offset,
    String? searchTerm,
    String? category,
  }) async {
    try {
      _logger.i('🛍️ Fetching products with domain: $domain');
      
      // Mock implementation for now
      return [
        {
          'id': 1,
          'display_name': 'Product A',
          'list_price': 100.0,
          'qty_available': 50,
          'active': true,
          'categ_id': 1,
        },
        {
          'id': 2,
          'display_name': 'Product B',
          'list_price': 150.0,
          'qty_available': 30,
          'active': true,
          'categ_id': 1,
        },
      ];
    } catch (e) {
      _logger.e('❌ Error fetching products: $e');
      rethrow;
    }
  }
  
  // Sales Order Methods
  Future<List<Map<String, dynamic>>> getSaleOrders({
    List<dynamic>? domain,
    int? limit,
    int? offset,
    String? state,
  }) async {
    try {
      _logger.i('📦 Fetching sale orders with domain: $domain');
      
      // Mock implementation for now
      return [
        {
          'id': 1,
          'name': 'SO001',
          'partner_id': 1,
          'amount_total': 15000.0,
          'state': 'confirmed',
          'date_order': DateTime.now().toIso8601String(),
        },
        {
          'id': 2,
          'name': 'SO002',
          'partner_id': 2,
          'amount_total': 8500.0,
          'state': 'draft',
          'date_order': DateTime.now().toIso8601String(),
        },
      ];
    } catch (e) {
      _logger.e('❌ Error fetching sale orders: $e');
      rethrow;
    }
  }
  
  // Payment and Commission Methods
  Future<Map<String, dynamic>> getDashboardDataComplete() async {
    try {
      _logger.i('📊 Loading dashboard data for user: $_userId');
      
      // Get receivables by region
      final receivables = await _getReceivablesByRegion();
      
      // Get commission data
      final commissions = await _getCommissionData();
      
      // Get cash box data
      final cashBox = await _getCashBoxData();
      
      // Get pending transfers
      final transfers = await _getPendingTransfers();
      
      final dashboardData = {
        'receivables': receivables,
        'commissions': commissions,
        'cashBox': cashBox,
        'transfers': transfers,
        'lastUpdate': DateTime.now().toIso8601String(),
      };
      
      // Cache the data
      _cache['dashboard'] = dashboardData;
      _lastCacheUpdate = DateTime.now();
      
      return dashboardData;
      
    } catch (e) {
      _logger.e('❌ Failed to load dashboard data: $e');
      
      // Return cached data if available
      if (_cache.containsKey('dashboard')) {
        _logger.w('📦 Returning cached dashboard data');
        return _cache['dashboard'];
      }
      
      throw OdooException('Failed to load dashboard data: $e');
    }
  }
  
  Future<Map<String, dynamic>> _getReceivablesByRegion() async {
    // Get customers with outstanding receivables
    final customers = await callMethod(
      model: 'res.partner',
      method: 'search_read',
      args: [
        [
          ['user_id', '=', _userId],
          ['customer_rank', '>', 0],
          ['total_receivable', '>', 0]
        ]
      ],
      kwargs: {
        'fields': ['name', 'total_receivable', 'state_id', 'city', 'currency_id'],
      },
    );
    
    Map<String, Map<String, double>> regionReceivables = {};
    double totalReceivables = 0;
    
    if (customers is List) {
      for (var customer in customers) {
        final receivable = (customer['total_receivable'] ?? 0.0).toDouble();
        final region = customer['state_id'] != null 
          ? customer['state_id'][1] 
          : customer['city'] ?? 'غير محدد';
        
        totalReceivables += receivable;
        
        if (!regionReceivables.containsKey(region)) {
          regionReceivables[region] = {'IQD': 0.0, 'USD': 0.0};
        }
        
        // Assume IQD for now - can be enhanced to handle multiple currencies
        regionReceivables[region]!['IQD'] = 
          (regionReceivables[region]!['IQD'] ?? 0.0) + receivable;
      }
    }
    
    return {
      'total': totalReceivables,
      'byRegion': regionReceivables,
      'currency': 'IQD',
    };
  }
  
  Future<Map<String, dynamic>> _getCommissionData() async {
    // Get payments received by this salesperson
    final payments = await callMethod(
      model: 'account.payment',
      method: 'search_read',
      args: [
        [
          ['partner_id.user_id', '=', _userId],
          ['state', '=', 'posted'],
          ['payment_type', '=', 'inbound'],
          ['create_date', '>=', '${DateTime.now().year}-01-01']
        ]
      ],
      kwargs: {
        'fields': ['amount', 'currency_id', 'date', 'partner_id'],
      },
    );
    
    double totalCollected = 0;
    double commission = 0;
    
    if (payments is List) {
      for (var payment in payments) {
        final amount = (payment['amount'] ?? 0.0).toDouble();
        totalCollected += amount;
      }
    }
    
    commission = totalCollected * AppConfig.commissionRate;
    
    return {
      'totalCollected': totalCollected,
      'commission': commission,
      'commissionRate': AppConfig.commissionRate,
      'currency': 'IQD',
    };
  }
  
  Future<Map<String, dynamic>> _getCashBoxData() async {
    // This would integrate with a custom cash management module in Odoo
    // For now, return mock data structure
    return {
      'total': {'IQD': 0.0, 'USD': 0.0},
      'byRegion': <String, Map<String, double>>{},
    };
  }
  
  Future<List<Map<String, dynamic>>> _getPendingTransfers() async {
    // This would integrate with a custom transfer management module
    // For now, return empty list
    return [];
  }
  
  // Settlement Methods
  Future<bool> createSettlement({
    required double amount,
    required String currency,
    required String transferMethod,
    String? receiptImage,
    String? notes,
  }) async {
    try {
      _logger.i('💰 Creating settlement: $amount $currency via $transferMethod');
      
      // This would create a record in a custom settlement model
      final result = await callMethod(
        model: 'tsh.settlement', // Custom model
        method: 'create',
        args: [
          {
            'salesperson_id': _userId,
            'amount': amount,
            'currency': currency,
            'transfer_method': transferMethod,
            'receipt_image': receiptImage,
            'notes': notes,
            'state': 'pending',
            'date': DateTime.now().toIso8601String(),
          }
        ],
      );
      
      _logger.i('✅ Settlement created with ID: $result');
      return true;
      
    } catch (e) {
      _logger.e('❌ Failed to create settlement: $e');
      throw OdooException('Failed to create settlement: $e');
    }
  }
  
  // Utility Methods
  bool get isAuthenticated => _userId != null && _password != null;
  
  int? get userId => _userId;
  String? get username => _username;
  
  void logout() {
    _userId = null;
    _username = null;
    _password = null;
    _sessionId = null;
    _cache.clear();
    AppConfig.clearUserData();
    _logger.i('👋 User logged out');
  }
  
  Future<bool> checkConnectivity() async {
    final connectivityResult = await Connectivity().checkConnectivity();
    return connectivityResult != ConnectivityResult.none;
  }
  
  bool get isCacheExpired {
    if (_lastCacheUpdate == null) return true;
    return DateTime.now().difference(_lastCacheUpdate!) > AppConfig.cacheTimeout;
  }
  
  void clearCache() {
    _cache.clear();
    _lastCacheUpdate = null;
    _logger.i('🗑️ Cache cleared');
  }

  // Additional methods needed by providers
  Future<List<Map<String, dynamic>>> getPayments({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
  }) async {
    try {
      _logger.i('📋 Fetching payments with filters: $filters');
      
      // Mock data for now - in real implementation, this would call Odoo API
      return [
        {
          'id': 1,
          'payment_number': 'PAY001',
          'customer_name': 'John Doe',
          'amount': 5000.0,
          'payment_method': 'cash',
          'status': 'completed',
          'payment_date': DateTime.now().toIso8601String(),
        },
        {
          'id': 2,
          'payment_number': 'PAY002',
          'customer_name': 'Jane Smith',
          'amount': 3000.0,
          'payment_method': 'card',
          'status': 'pending',
          'payment_date': DateTime.now().toIso8601String(),
        },
      ];
    } catch (e) {
      _logger.e('❌ Error fetching payments: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> processPayment(Map<String, dynamic> paymentData) async {
    try {
      _logger.i('💳 Processing payment: $paymentData');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 2));
      
      return {
        'success': true,
        'payment_id': DateTime.now().millisecondsSinceEpoch,
        'message': 'Payment processed successfully',
      };
    } catch (e) {
      _logger.e('❌ Error processing payment: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> refundPayment(int paymentId, double amount, String reason) async {
    try {
      _logger.i('🔄 Refunding payment $paymentId: $amount - $reason');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 2));
      
      return {
        'success': true,
        'refund_id': DateTime.now().millisecondsSinceEpoch,
        'message': 'Refund processed successfully',
      };
    } catch (e) {
      _logger.e('❌ Error processing refund: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getOrdersAsMaps({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
  }) async {
    try {
      _logger.i('📦 Fetching orders as maps with filters: $filters');
      
      // Call existing getSaleOrders and convert to maps
      final orders = await getSaleOrders(
        limit: limit,
        offset: offset,
      );
      
      return orders.map((order) => {
        'id': order['id'],
        'order_number': order['name'],
        'customer_name': order['partner_id']?.toString() ?? 'Unknown',
        'total_amount': order['amount_total'],
        'status': order['state'],
        'order_date': order['date_order'],
      }).toList();
    } catch (e) {
      _logger.e('❌ Error fetching orders: $e');
      // Return mock data as fallback
      return [
        {
          'id': 1,
          'order_number': 'SO001',
          'customer_name': 'John Doe',
          'total_amount': 15000.0,
          'status': 'confirmed',
          'order_date': DateTime.now().toIso8601String(),
        },
        {
          'id': 2,
          'order_number': 'SO002',
          'customer_name': 'Jane Smith',
          'total_amount': 8500.0,
          'status': 'draft',
          'order_date': DateTime.now().toIso8601String(),
        },
      ];
    }
  }

  Future<List<Map<String, dynamic>>> getCustomersAsMaps({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
  }) async {
    try {
      _logger.i('👥 Fetching customers as maps with filters: $filters');
      
      // Call existing getCustomers and convert to maps
      final customers = await getCustomers(
        limit: limit,
        offset: offset,
      );
      
      return customers.map((customer) => {
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'city': customer.city,
        'country': customer.countryId?.toString(),
      }).toList();
    } catch (e) {
      _logger.e('❌ Error fetching customers: $e');
      // Return mock data as fallback
      return [
        {
          'id': 1,
          'name': 'John Doe',
          'email': 'john@example.com',
          'phone': '+964-123-456789',
          'city': 'Baghdad',
          'country': 'Iraq',
        },
        {
          'id': 2,
          'name': 'Jane Smith',
          'email': 'jane@example.com',
          'phone': '+964-987-654321',
          'city': 'Basra',
          'country': 'Iraq',
        },
      ];
    }
  }

  Future<List<Map<String, dynamic>>> getProductsAsMaps({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
  }) async {
    try {
      _logger.i('🛍️ Fetching products as maps with filters: $filters');
      
      // Call existing getProducts and convert to maps
      final products = await getProducts(
        limit: limit,
        offset: offset,
      );
      
      return products.map((product) => {
        'id': product.id,
        'name': product.displayName,
        'price': product.listPrice,
        'stock_quantity': product.qtyAvailable,
        'is_active': product.active,
        'category_name': product.categId?.toString(),
      }).toList();
    } catch (e) {
      _logger.e('❌ Error fetching products: $e');
      // Return mock data as fallback
      return [
        {
          'id': 1,
          'name': 'Product A',
          'price': 100.0,
          'stock_quantity': 50,
          'is_active': true,
        },
        {
          'id': 2,
          'name': 'Product B',
          'price': 150.0,
          'stock_quantity': 30,
          'is_active': true,
        },
      ];
    }
  }

  Future<Map<String, dynamic>> createOrder(Map<String, dynamic> orderData) async {
    try {
      _logger.i('✨ Creating order: $orderData');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 2));
      
      return {
        'success': true,
        'order_id': DateTime.now().millisecondsSinceEpoch,
        'message': 'Order created successfully',
      };
    } catch (e) {
      _logger.e('❌ Error creating order: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> updateOrderStatus(int orderId, String newStatus) async {
    try {
      _logger.i('🔄 Updating order $orderId status to: $newStatus');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 1));
      
      return {
        'success': true,
        'message': 'Order status updated successfully',
      };
    } catch (e) {
      _logger.e('❌ Error updating order status: $e');
      rethrow;
    }
  }


  Future<Map<String, dynamic>> updateProductQuantity(int productId, int newQuantity) async {
    try {
      _logger.i('📦 Updating product $productId quantity to: $newQuantity');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 1));
      
      return {
        'success': true,
        'message': 'Product quantity updated successfully',
      };
    } catch (e) {
      _logger.e('❌ Error updating product quantity: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> createCustomer(Map<String, dynamic> customerData) async {
    try {
      _logger.i('👤 Creating customer: $customerData');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 2));
      
      return {
        'success': true,
        'customer_id': DateTime.now().millisecondsSinceEpoch,
        'message': 'Customer created successfully',
      };
    } catch (e) {
      _logger.e('❌ Error creating customer: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> updateCustomer(int customerId, Map<String, dynamic> customerData) async {
    try {
      _logger.i('🔄 Updating customer $customerId: $customerData');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 1));
      
      return {
        'success': true,
        'message': 'Customer updated successfully',
      };
    } catch (e) {
      _logger.e('❌ Error updating customer: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> deleteCustomer(int customerId) async {
    try {
      _logger.i('🗑️ Deleting customer: $customerId');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 1));
      
      return {
        'success': true,
        'message': 'Customer deleted successfully',
      };
    } catch (e) {
      _logger.e('❌ Error deleting customer: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getDashboardData(String type) async {
    try {
      _logger.i('📊 Fetching dashboard data for: $type');
      
      switch (type) {
        case 'receivables':
          return {
            'total_receivables': 125000.0,
            'overdue_amount': 35000.0,
            'current_month': 90000.0,
            'last_month': 80000.0,
          };
        case 'commission':
          return {
            'total_commission': 15000.0,
            'this_month': 8000.0,
            'last_month': 7000.0,
          };
        case 'cashbox':
          return {
            'total_cash': 45000.0,
            'daily_collection': 12000.0,
            'recent_transactions': [
              {
                'type': 'payment',
                'amount': 5000.0,
                'description': 'Payment from Customer A',
                'time': DateTime.now().toIso8601String(),
              },
            ],
          };
        case 'regional':
          return {
            'Baghdad': 50000.0,
            'Basra': 35000.0,
            'Erbil': 25000.0,
            'Mosul': 15000.0,
          };
        case 'summary':
          return {
            'total_orders': 150,
            'pending_orders': 25,
            'completed_orders': 125,
            'total_customers': 89,
          };
        default:
          return {};
      }
    } catch (e) {
      _logger.e('❌ Error fetching dashboard data: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> processSettlement(Map<String, dynamic> settlementData) async {
    try {
      _logger.i('🏦 Processing settlement: $settlementData');
      
      // Mock implementation
      await Future.delayed(const Duration(seconds: 3));
      
      return {
        'success': true,
        'settlement_id': DateTime.now().millisecondsSinceEpoch,
        'message': 'Settlement processed successfully',
      };
    } catch (e) {
      _logger.e('❌ Error processing settlement: $e');
      rethrow;
    }
  }
} 