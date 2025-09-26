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
  Future<List<CustomerModel>> getCustomers({
    List<dynamic>? domain,
    int? limit,
    int? offset,
    String? searchTerm,
  }) async {
    try {
      List<dynamic> searchDomain = domain ?? [];
      
      // Add salesperson filter - customers assigned to current user
      if (_userId != null) {
        searchDomain.add(['user_id', '=', _userId]);
      }
      
      // Add customer filter
      searchDomain.add(['is_company', '=', true]);
      searchDomain.add(['customer_rank', '>', 0]);
      
      // Add search term if provided
      if (searchTerm != null && searchTerm.isNotEmpty) {
        searchDomain.add(['name', 'ilike', searchTerm]);
      }
      
      final result = await callMethod(
        model: 'res.partner',
        method: 'search_read',
        args: [searchDomain],
        kwargs: {
          'fields': [
            'name', 'email', 'phone', 'mobile', 'street', 'city', 
            'state_id', 'country_id', 'customer_rank', 'supplier_rank',
            'user_id', 'category_id', 'credit_limit', 'total_receivable',
            'currency_id', 'payment_term_id', 'property_account_receivable_id'
          ],
          'limit': limit ?? AppConfig.defaultPageSize,
          'offset': offset ?? 0,
          'order': 'name asc'
        },
      );
      
      if (result is List) {
        return result.map((data) => CustomerModel.fromJson(data)).toList();
      }
      
      return [];
      
    } catch (e) {
      _logger.e('❌ Failed to get customers: $e');
      throw OdooException('Failed to load customers: $e');
    }
  }
  
  // Product Methods
  Future<List<ProductModel>> getProducts({
    List<dynamic>? domain,
    int? limit,
    int? offset,
    String? searchTerm,
    String? category,
  }) async {
    try {
      List<dynamic> searchDomain = domain ?? [];
      
      // Add basic product filters
      searchDomain.add(['sale_ok', '=', true]);
      searchDomain.add(['active', '=', true]);
      
      // Add search term if provided
      if (searchTerm != null && searchTerm.isNotEmpty) {
        searchDomain.add([
          '|', '|',
          ['name', 'ilike', searchTerm],
          ['default_code', 'ilike', searchTerm],
          ['barcode', 'ilike', searchTerm]
        ]);
      }
      
      // Add category filter if provided
      if (category != null && category.isNotEmpty) {
        searchDomain.add(['categ_id.name', 'ilike', category]);
      }
      
      final result = await callMethod(
        model: 'product.product',
        method: 'search_read',
        args: [searchDomain],
        kwargs: {
          'fields': [
            'name', 'default_code', 'barcode', 'list_price', 'standard_price',
            'categ_id', 'uom_id', 'qty_available', 'virtual_available',
            'sale_ok', 'purchase_ok', 'type', 'weight', 'volume',
            'image_1920', 'description_sale', 'taxes_id'
          ],
          'limit': limit ?? AppConfig.defaultPageSize,
          'offset': offset ?? 0,
          'order': 'name asc'
        },
      );
      
      if (result is List) {
        return result.map((data) => ProductModel.fromJson(data)).toList();
      }
      
      return [];
      
    } catch (e) {
      _logger.e('❌ Failed to get products: $e');
      throw OdooException('Failed to load products: $e');
    }
  }
  
  // Sales Order Methods
  Future<List<SaleOrderModel>> getSaleOrders({
    List<dynamic>? domain,
    int? limit,
    int? offset,
    String? state,
  }) async {
    try {
      List<dynamic> searchDomain = domain ?? [];
      
      // Add salesperson filter
      if (_userId != null) {
        searchDomain.add(['user_id', '=', _userId]);
      }
      
      // Add state filter if provided
      if (state != null && state.isNotEmpty) {
        searchDomain.add(['state', '=', state]);
      }
      
      final result = await callMethod(
        model: 'sale.order',
        method: 'search_read',
        args: [searchDomain],
        kwargs: {
          'fields': [
            'name', 'partner_id', 'user_id', 'date_order', 'validity_date',
            'state', 'amount_untaxed', 'amount_tax', 'amount_total',
            'currency_id', 'pricelist_id', 'payment_term_id',
            'order_line', 'invoice_status', 'delivery_status'
          ],
          'limit': limit ?? AppConfig.defaultPageSize,
          'offset': offset ?? 0,
          'order': 'date_order desc'
        },
      );
      
      if (result is List) {
        return result.map((data) => SaleOrderModel.fromJson(data)).toList();
      }
      
      return [];
      
    } catch (e) {
      _logger.e('❌ Failed to get sale orders: $e');
      throw OdooException('Failed to load sale orders: $e');
    }
  }
  
  // Payment and Commission Methods
  Future<Map<String, dynamic>> getDashboardData() async {
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
} 