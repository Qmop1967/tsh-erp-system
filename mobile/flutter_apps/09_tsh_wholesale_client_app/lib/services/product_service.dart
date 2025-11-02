import '../config/api_config.dart';
import '../models/api_response.dart';
import '../models/product.dart';
import 'api_service.dart';

class ProductService {
  final ApiService _apiService;

  ProductService(this._apiService);

  /// Get all active products
  Future<ApiResponse<List<Product>>> getProducts({
    int? page,
    int? pageSize,
    String? search,
    String? category,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (page != null) queryParams['page'] = page;
      if (pageSize != null) queryParams['page_size'] = pageSize;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;
      if (category != null && category.isNotEmpty) {
        queryParams['category'] = category;
      }

      final response = await _apiService.get(
        ApiConfig.productsActive,
        queryParameters: queryParams,
      );

      if (response.success && response.data != null) {
        // Parse response data
        final data = response.data;
        List<Product> products = [];

        if (data is List) {
          products = data.map((item) => Product.fromJson(item)).toList();
        } else if (data is Map<String, dynamic>) {
          // Handle paginated response
          final items = data['items'] ?? data['products'] ?? data['data'];
          if (items is List) {
            products = items.map((item) => Product.fromJson(item)).toList();
          }
        }

        return ApiResponse.success(
          data: products,
          message: response.message,
        );
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Failed to fetch products',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  /// Get product by ID
  Future<ApiResponse<Product>> getProductById(String id) async {
    try {
      final response = await _apiService.get(
        ApiConfig.productById(id),
      );

      if (response.success && response.data != null) {
        final product = Product.fromJson(response.data as Map<String, dynamic>);
        return ApiResponse.success(data: product);
      } else {
        return ApiResponse.error(
          error: response.error ?? 'Failed to fetch product',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error(error: e.toString());
    }
  }

  /// Search products
  Future<ApiResponse<List<Product>>> searchProducts(String query) async {
    return getProducts(search: query);
  }

  /// Get products by category
  Future<ApiResponse<List<Product>>> getProductsByCategory(
      String category) async {
    return getProducts(category: category);
  }
}
