import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/product.dart';
import '../models/order.dart';
import '../models/user.dart';

/// BFF API Service for Consumer App
/// Optimized API layer with caching and aggregation
class BFFApiService {
  static const String baseUrl = 'https://erp.tsh.sale/api/bff/mobile';
  static String? _authToken;

  // Authentication token management
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

  // Consumer Products API (BFF)
  static Future<Map<String, dynamic>> getConsumerProducts({
    String? category,
    String? search,
    int page = 1,
    int limit = 100,
  }) async {
    try {
      final headers = await _getHeaders();
      final queryParams = <String, String>{
        'skip': '${(page - 1) * limit}',
        'limit': limit.toString(),
      };
      
      if (category != null && category.isNotEmpty && category != 'All') {
        queryParams['category'] = category;
      }
      
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      
      final uri = Uri.parse('$baseUrl/consumer/products').replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        List<Product> products = [];
        if (data.containsKey('items')) {
          products = (data['items'] as List)
              .map((json) => Product.fromJson(json))
              .toList();
        }

        return {
          'products': products,
          'total': data['total'] as int? ?? products.length,
          'count': data['count'] as int? ?? products.length,
          'has_more': data['pagination']?['has_more'] as bool? ?? false,
        };
      } else {
        throw Exception('Failed to load products: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching products: $e');
    }
  }

  static Future<Product> getConsumerProductById(String id) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/consumer/products/$id'),
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

  static Future<List<String>> getConsumerCategories() async {
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

  // User Profile (for getting email)
  static Future<User?> getUserProfile() async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('https://erp.tsh.sale/api/user/profile'),
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

  // Order History (BFF)
  static Future<Map<String, dynamic>> getConsumerOrderHistory({
    required String customerEmail,
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final headers = await _getHeaders();
      final queryParams = <String, String>{
        'customer_email': customerEmail,
        'page': page.toString(),
        'page_size': pageSize.toString(),
      };
      
      if (status != null && status.isNotEmpty) {
        queryParams['status'] = status;
      }
      
      final uri = Uri.parse('$baseUrl/consumer/orders/history').replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['data'] ?? {'orders': [], 'total': 0};
      } else {
        return {'orders': [], 'total': 0};
      }
    } catch (e) {
      return {'orders': [], 'total': 0};
    }
  }

  // Image URL helper (same as ApiService)
  static String getProductImageUrl(Product product) {
    // CDN image has priority (if it's a valid URL)
    if (product.cdnImageUrl != null &&
        product.cdnImageUrl!.isNotEmpty &&
        product.cdnImageUrl!.startsWith('http')) {
      return product.cdnImageUrl!;
    }

    // Then image_url (if it's a valid URL)
    if (product.imageUrl != null &&
        product.imageUrl!.isNotEmpty &&
        product.imageUrl!.startsWith('http')) {
      return product.imageUrl!;
    }

    // For relative paths from backend, construct full URL
    // NOTE: Backend returns paths like "/product-images/{zoho_item_id}.jpg"
    // But these images don't exist yet on the server
    // So we fallback to placeholder for now
    if (product.imageUrl != null &&
        product.imageUrl!.isNotEmpty &&
        product.imageUrl!.startsWith('/')) {
      // Check if it's a known placeholder path
      if (product.imageUrl!.contains('placeholder')) {
        return _getPlaceholderImage(product.category);
      }
      // Construct full URL for relative paths
      final String serverUrl = 'https://erp.tsh.sale';
      return '$serverUrl${product.imageUrl}';
    }

    // Fallback to category-based placeholder
    return _getPlaceholderImage(product.category);
  }

  static String _getPlaceholderImage(String? category) {
    final categoryLower = category?.toLowerCase() ?? '';
    if (categoryLower.contains('laptop') || categoryLower.contains('computer')) {
      return 'https://via.placeholder.com/400x400.png?text=Laptop';
    } else if (categoryLower.contains('mobile') || categoryLower.contains('phone')) {
      return 'https://via.placeholder.com/400x400.png?text=Mobile';
    } else if (categoryLower.contains('printer')) {
      return 'https://via.placeholder.com/400x400.png?text=Printer';
    } else if (categoryLower.contains('network') || categoryLower.contains('router')) {
      return 'https://via.placeholder.com/400x400.png?text=Network';
    }
    return 'https://via.placeholder.com/400x400.png?text=Product';
  }
}

