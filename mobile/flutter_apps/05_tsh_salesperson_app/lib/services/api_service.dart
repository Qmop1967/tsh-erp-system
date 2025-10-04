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

/// TSH API Service
/// Handles all API communication with the TSH ERP System backend
class ApiService {
  late final Dio _dio;
  late final Logger _logger;
  
  String? _accessToken;
  int? _userId;
  String? _username;
  
  // Cache for offline functionality
  final Map<String, dynamic> _cache = {};
  DateTime? _lastCacheUpdate;
  
  ApiService() {
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
      baseUrl: AppConfig.apiUrl,
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
          if (_accessToken != null) {
            options.headers['Authorization'] = 'Bearer $_accessToken';
          }
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
    required String username,
    required String password,
  }) async {
    try {
      _logger.i('🔐 Authenticating user: $username');
      
      final response = await _dio.post('/auth/login', data: {
        'username': username,
        'password': password,
      });
      
      if (response.statusCode != 200) {
        throw ApiException(
          'Authentication failed',
          code: 'AUTH_ERROR',
        );
      }
      
      final data = response.data;
      _accessToken = data['access_token'];
      _userId = data['user_id'];
      _username = username;
      
      // Save credentials
      await AppConfig.saveUserCredentials(
        username: username,
        accessToken: _accessToken!,
        userId: _userId!,
      );
      
      _logger.i('✅ Authentication successful. User ID: $_userId');
      
      // Get user details
      final userDetails = await _getUserDetails(_userId!);
      
      return AuthResult(
        success: true,
        userId: _userId!,
        username: username,
        userDetails: userDetails,
      );
      
    } on DioException catch (e) {
      _logger.e('🌐 Network error during authentication: ${e.message}');
      throw NetworkException('Network error: ${e.message}');
    } catch (e) {
      _logger.e('❌ Authentication error: $e');
      throw ApiException('Authentication failed: $e');
    }
  }
  
  Future<Map<String, dynamic>> _getUserDetails(int userId) async {
    try {
      final response = await _dio.get('/users/$userId');
      
      if (response.statusCode != 200) {
        throw ApiException('Failed to get user details');
      }
      
      return response.data;
      
    } catch (e) {
      _logger.w('⚠️ Could not fetch user details: $e');
      return {};
    }
  }
  
  // Generic API call method
  Future<dynamic> callApi({
    required String endpoint,
    required String method,
    Map<String, dynamic>? data,
    Map<String, dynamic>? queryParameters,
  }) async {
    if (_accessToken == null) {
      throw ApiException('Not authenticated', code: 'NOT_AUTHENTICATED');
    }
    
    try {
      Response response;
      
      switch (method.toUpperCase()) {
        case 'GET':
          response = await _dio.get(endpoint, queryParameters: queryParameters);
          break;
        case 'POST':
          response = await _dio.post(endpoint, data: data, queryParameters: queryParameters);
          break;
        case 'PUT':
          response = await _dio.put(endpoint, data: data, queryParameters: queryParameters);
          break;
        case 'DELETE':
          response = await _dio.delete(endpoint, queryParameters: queryParameters);
          break;
        default:
          throw ApiException('Unsupported HTTP method: $method');
      }
      
      if (response.statusCode! >= 200 && response.statusCode! < 300) {
        return response.data;
      } else {
        throw ApiException(
          'API Error: ${response.statusMessage}',
          code: 'API_ERROR',
        );
      }
      
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw NetworkException('Connection timeout');
      }
      throw NetworkException('Network error: ${e.message}');
    } catch (e) {
      _logger.e('❌ API call failed: $e');
      rethrow;
    }
  }
  
  // Customer Methods
  Future<List<Map<String, dynamic>>> getCustomers({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
    String? searchTerm,
  }) async {
    try {
      _logger.i('👥 Fetching customers with filters: $filters');
      
      final response = await callApi(
        endpoint: '/customers',
        method: 'GET',
        queryParameters: {
          if (filters != null) ...filters,
          if (limit != null) 'limit': limit,
          if (offset != null) 'offset': offset,
          if (searchTerm != null) 'search': searchTerm,
        },
      );
      
      return List<Map<String, dynamic>>.from(response['data'] ?? []);
    } catch (e) {
      _logger.e('❌ Error fetching customers: $e');
      rethrow;
    }
  }
  
  // Product Methods
  Future<List<Map<String, dynamic>>> getProducts({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
    String? searchTerm,
    String? category,
  }) async {
    try {
      _logger.i('🛍️ Fetching products with filters: $filters');
      
      final response = await callApi(
        endpoint: '/products',
        method: 'GET',
        queryParameters: {
          if (filters != null) ...filters,
          if (limit != null) 'limit': limit,
          if (offset != null) 'offset': offset,
          if (searchTerm != null) 'search': searchTerm,
          if (category != null) 'category': category,
        },
      );
      
      return List<Map<String, dynamic>>.from(response['data'] ?? []);
    } catch (e) {
      _logger.e('❌ Error fetching products: $e');
      rethrow;
    }
  }
  
  // Sales Order Methods
  Future<List<Map<String, dynamic>>> getSaleOrders({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
    String? state,
  }) async {
    try {
      _logger.i('📦 Fetching sale orders with filters: $filters');
      
      final response = await callApi(
        endpoint: '/orders',
        method: 'GET',
        queryParameters: {
          if (filters != null) ...filters,
          if (limit != null) 'limit': limit,
          if (offset != null) 'offset': offset,
          if (state != null) 'state': state,
        },
      );
      
      return List<Map<String, dynamic>>.from(response['data'] ?? []);
    } catch (e) {
      _logger.e('❌ Error fetching sale orders: $e');
      rethrow;
    }
  }
  
  // Payment and Commission Methods
  Future<Map<String, dynamic>> getDashboardDataComplete() async {
    try {
      _logger.i('📊 Loading dashboard data for user: $_userId');
      
      final response = await callApi(
        endpoint: '/dashboard/complete',
        method: 'GET',
        queryParameters: {'user_id': _userId},
      );
      
      // Cache the data
      _cache['dashboard'] = response;
      _lastCacheUpdate = DateTime.now();
      
      return response;
      
    } catch (e) {
      _logger.e('❌ Failed to load dashboard data: $e');
      
      // Return cached data if available
      if (_cache.containsKey('dashboard')) {
        _logger.w('📦 Returning cached dashboard data');
        return _cache['dashboard'];
      }
      
      throw ApiException('Failed to load dashboard data: $e');
    }
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
      
      final response = await callApi(
        endpoint: '/settlements',
        method: 'POST',
        data: {
          'salesperson_id': _userId,
          'amount': amount,
          'currency': currency,
          'transfer_method': transferMethod,
          'receipt_image': receiptImage,
          'notes': notes,
          'state': 'pending',
          'date': DateTime.now().toIso8601String(),
        },
      );
      
      _logger.i('✅ Settlement created with ID: ${response['id']}');
      return true;
      
    } catch (e) {
      _logger.e('❌ Failed to create settlement: $e');
      throw ApiException('Failed to create settlement: $e');
    }
  }
  
  // Payment Methods
  Future<List<Map<String, dynamic>>> getPayments({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
  }) async {
    try {
      _logger.i('📋 Fetching payments with filters: $filters');
      
      final response = await callApi(
        endpoint: '/payments',
        method: 'GET',
        queryParameters: {
          if (filters != null) ...filters,
          if (limit != null) 'limit': limit,
          if (offset != null) 'offset': offset,
        },
      );
      
      return List<Map<String, dynamic>>.from(response['data'] ?? []);
    } catch (e) {
      _logger.e('❌ Error fetching payments: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> processPayment(Map<String, dynamic> paymentData) async {
    try {
      _logger.i('💳 Processing payment: $paymentData');
      
      final response = await callApi(
        endpoint: '/payments/process',
        method: 'POST',
        data: paymentData,
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error processing payment: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> refundPayment(int paymentId, double amount, String reason) async {
    try {
      _logger.i('🔄 Refunding payment $paymentId: $amount - $reason');
      
      final response = await callApi(
        endpoint: '/payments/$paymentId/refund',
        method: 'POST',
        data: {
          'amount': amount,
          'reason': reason,
        },
      );
      
      return response;
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
      return await getSaleOrders(
        filters: filters,
        limit: limit,
        offset: offset,
      );
    } catch (e) {
      _logger.e('❌ Error fetching orders: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getCustomersAsMaps({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
  }) async {
    try {
      return await getCustomers(
        filters: filters,
        limit: limit,
        offset: offset,
      );
    } catch (e) {
      _logger.e('❌ Error fetching customers: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getProductsAsMaps({
    Map<String, dynamic>? filters,
    int? limit,
    int? offset,
  }) async {
    try {
      return await getProducts(
        filters: filters,
        limit: limit,
        offset: offset,
      );
    } catch (e) {
      _logger.e('❌ Error fetching products: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> createOrder(Map<String, dynamic> orderData) async {
    try {
      _logger.i('✨ Creating order: $orderData');
      
      final response = await callApi(
        endpoint: '/orders',
        method: 'POST',
        data: orderData,
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error creating order: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> updateOrderStatus(int orderId, String newStatus) async {
    try {
      _logger.i('🔄 Updating order $orderId status to: $newStatus');
      
      final response = await callApi(
        endpoint: '/orders/$orderId/status',
        method: 'PUT',
        data: {'status': newStatus},
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error updating order status: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> updateProductQuantity(int productId, int newQuantity) async {
    try {
      _logger.i('📦 Updating product $productId quantity to: $newQuantity');
      
      final response = await callApi(
        endpoint: '/products/$productId/quantity',
        method: 'PUT',
        data: {'quantity': newQuantity},
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error updating product quantity: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> createCustomer(Map<String, dynamic> customerData) async {
    try {
      _logger.i('👤 Creating customer: $customerData');
      
      final response = await callApi(
        endpoint: '/customers',
        method: 'POST',
        data: customerData,
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error creating customer: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> updateCustomer(int customerId, Map<String, dynamic> customerData) async {
    try {
      _logger.i('🔄 Updating customer $customerId: $customerData');
      
      final response = await callApi(
        endpoint: '/customers/$customerId',
        method: 'PUT',
        data: customerData,
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error updating customer: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> deleteCustomer(int customerId) async {
    try {
      _logger.i('🗑️ Deleting customer: $customerId');
      
      final response = await callApi(
        endpoint: '/customers/$customerId',
        method: 'DELETE',
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error deleting customer: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getDashboardData(String type) async {
    try {
      _logger.i('📊 Fetching dashboard data for: $type');
      
      final response = await callApi(
        endpoint: '/dashboard/$type',
        method: 'GET',
        queryParameters: {'user_id': _userId},
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error fetching dashboard data: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> processSettlement(Map<String, dynamic> settlementData) async {
    try {
      _logger.i('🏦 Processing settlement: $settlementData');
      
      final response = await callApi(
        endpoint: '/settlements/process',
        method: 'POST',
        data: settlementData,
      );
      
      return response;
    } catch (e) {
      _logger.e('❌ Error processing settlement: $e');
      rethrow;
    }
  }
  
  // Utility Methods
  bool get isAuthenticated => _accessToken != null;
  
  int? get userId => _userId;
  String? get username => _username;
  String? get accessToken => _accessToken;
  
  void logout() {
    _userId = null;
    _username = null;
    _accessToken = null;
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
