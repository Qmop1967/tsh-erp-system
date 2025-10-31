import 'dart:convert';
import 'package:http/http.dart' as http;

class ZohoService {
  static const String baseUrl = 'http://localhost:8000/api/zoho';

  // Fetch inventory items from Zoho
  static Future<List<Map<String, dynamic>>> fetchInventoryFromZoho() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/inventory/items'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['items'] ?? []);
      } else {
        print('Failed to fetch Zoho inventory: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('Error fetching Zoho inventory: $e');
      return [];
    }
  }

  // Create sales order in Zoho
  static Future<Map<String, dynamic>?> createSalesOrder({
    required String customerName,
    required String customerEmail,
    required String customerPhone,
    required List<Map<String, dynamic>> lineItems,
    required double totalAmount,
  }) async {
    try {
      final orderData = {
        'customer_name': customerName,
        'customer_email': customerEmail,
        'customer_phone': customerPhone,
        'line_items': lineItems,
        'total': totalAmount,
        'date': DateTime.now().toIso8601String(),
      };

      final response = await http.post(
        Uri.parse('$baseUrl/sales-orders'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(orderData),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        print('Failed to create Zoho sales order: ${response.statusCode}');
        print('Response: ${response.body}');
        return null;
      }
    } catch (e) {
      print('Error creating Zoho sales order: $e');
      return null;
    }
  }

  // Sync inventory quantities from Zoho
  static Future<bool> syncInventoryQuantities() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/sync/inventory'),
        headers: {'Content-Type': 'application/json'},
      );

      return response.statusCode == 200;
    } catch (e) {
      print('Error syncing inventory: $e');
      return false;
    }
  }

  // Get product details from Zoho
  static Future<Map<String, dynamic>?> getProductDetails(String productId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/inventory/items/$productId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Error fetching product details: $e');
      return null;
    }
  }
}
