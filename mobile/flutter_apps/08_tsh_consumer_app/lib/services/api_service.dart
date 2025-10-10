import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Use localhost for web, your Mac's IP for mobile devices
  static const String baseUrl = 'http://localhost:8000/api/consumer';

  // Fetch all inventory items
  static Future<List<Map<String, dynamic>>> fetchProducts({
    String? category,
    String? search,
  }) async {
    try {
      var uri = Uri.parse('$baseUrl/products');

      // Add query parameters
      final queryParams = <String, String>{};
      if (category != null && category.isNotEmpty && category != 'All') {
        queryParams['category'] = category;
      }
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }

      if (queryParams.isNotEmpty) {
        uri = uri.replace(queryParameters: queryParams);
      }

      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['items'] ?? []);
      } else {
        print('Failed to load products: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('Error fetching products: $e');
      return [];
    }
  }

  // Fetch product categories
  static Future<List<String>> fetchCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/categories'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final categories = List<String>.from(data['categories'] ?? []);
        // Add 'All' at the beginning
        return ['All', ...categories];
      }
      return ['All'];
    } catch (e) {
      print('Error fetching categories: $e');
      return ['All'];
    }
  }

  // Get image URL for a product
  static String getImageUrl(String? imagePath) {
    if (imagePath == null || imagePath.isEmpty) {
      return '';
    }
    // Remove /api prefix if present and construct full URL
    final cleanPath = imagePath.startsWith('/api')
        ? imagePath.substring(4)
        : imagePath;
    return 'http://localhost:8000$cleanPath';
  }
}
