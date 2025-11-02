import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/product.dart';
import '../models/user.dart';

class ApiService {
  static const String baseUrl = 'https://erp.tsh.sale/api';
  static String? _authToken;

  // Authentication methods
  static Future<void> setAuthToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  static Future<String?> getAuthToken() async {
    if (_authToken != null) return _authToken;
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
    return _authToken;
  }

  static Future<void> clearAuthToken() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  static Future<Map<String, String>> _getHeaders() async {
    final token = await getAuthToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Products API
  static Future<Map<String, dynamic>> getProductsWithTotal({
    int page = 1,
    int limit = 100,
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/consumer/products?limit=$limit&skip=${(page - 1) * limit}'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Handle both response formats
        List<Product> products;
        if (data.containsKey('items')) {
          // New format: {status: "success", count: 5, items: [...]}
          products = (data['items'] as List)
              .map((json) => Product.fromJson(json))
              .toList();
        } else if (data.containsKey('products')) {
          // Old format: {products: [...], total: 100}
          products = (data['products'] as List)
              .map((json) => Product.fromJson(json))
              .toList();
        } else {
          products = [];
        }

        final total = data['total'] as int? ?? data['count'] as int? ?? products.length;
        return {
          'products': products,
          'total': total,
        };
      } else {
        throw Exception('Failed to load products: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching products: $e');
    }
  }

  static Future<List<Product>> getProducts({
    int page = 1,
    int limit = 100,
  }) async {
    final result = await getProductsWithTotal(page: page, limit: limit);
    return result['products'] as List<Product>;
  }

  static Future<Product> getProductById(String id) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/products/$id'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return Product.fromJson(data['product']);
      } else {
        throw Exception('Failed to load product: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching product: $e');
    }
  }

  static Future<List<String>> getCategories() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/consumer/categories'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<String>.from(data['categories'] ?? []);
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  // User/Auth API
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['access_token'] != null) {
          await setAuthToken(data['access_token']);
        }
        return data;
      } else {
        final data = json.decode(response.body);
        throw Exception(data['error'] ?? 'Login failed');
      }
    } catch (e) {
      throw Exception('Error during login: $e');
    }
  }

  static Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    String? fullName,
    String? phone,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'full_name': fullName,
          'phone': phone,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
        if (data['access_token'] != null) {
          await setAuthToken(data['access_token']);
        }
        return data;
      } else {
        final data = json.decode(response.body);
        throw Exception(data['error'] ?? 'Registration failed');
      }
    } catch (e) {
      throw Exception('Error during registration: $e');
    }
  }

  // Alias for register to match auth_screen.dart usage
  static Future<Map<String, dynamic>> signup({
    required String name,
    required String email,
    required String password,
    String? phone,
  }) async {
    return register(
      email: email,
      password: password,
      fullName: name,
      phone: phone,
    );
  }

  static Future<User?> getUserProfile() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/user/profile'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return User.fromJson(data);
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  // Orders API
  static Future<Map<String, dynamic>> createOrder({
    required List<Map<String, dynamic>> items,
    required String customerName,
    required String customerEmail,
    required String customerPhone,
    required String deliveryAddress,
    String? notes,
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/orders'),
        headers: headers,
        body: json.encode({
          'items': items,
          'customer_name': customerName,
          'customer_email': customerEmail,
          'customer_phone': customerPhone,
          'delivery_address': deliveryAddress,
          'notes': notes,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        final data = json.decode(response.body);
        throw Exception(data['error'] ?? 'Failed to create order');
      }
    } catch (e) {
      throw Exception('Error creating order: $e');
    }
  }

  static Future<List<Map<String, dynamic>>> getMyOrders() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/orders/my-orders'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['orders'] ?? []);
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  // Image URL helper
  static String getProductImageUrl(Product product) {
    // CDN image has priority
    if (product.cdnImageUrl != null && product.cdnImageUrl!.isNotEmpty) {
      return product.cdnImageUrl!;
    }

    // Then image_url - prepend baseUrl if it's a relative path
    if (product.imageUrl != null && product.imageUrl!.isNotEmpty) {
      // If imageUrl starts with /, prepend the base URL
      if (product.imageUrl!.startsWith('/')) {
        return '$baseUrl${product.imageUrl}';
      }
      return product.imageUrl!;
    }

    // Fallback to placeholder based on category
    return _getPlaceholderImage(product.category);
  }

  static String _getPlaceholderImage(String? category) {
    final categoryLower = category?.toLowerCase() ?? '';

    if (categoryLower.contains('laptop') || categoryLower.contains('computer')) {
      return 'https://via.placeholder.com/400x400.png?text=Laptop';
    } else if (categoryLower.contains('mobile') ||
        categoryLower.contains('phone')) {
      return 'https://via.placeholder.com/400x400.png?text=Mobile';
    } else if (categoryLower.contains('printer')) {
      return 'https://via.placeholder.com/400x400.png?text=Printer';
    } else if (categoryLower.contains('network') ||
        categoryLower.contains('router')) {
      return 'https://via.placeholder.com/400x400.png?text=Network';
    }

    return 'https://via.placeholder.com/400x400.png?text=Product';
  }
}
