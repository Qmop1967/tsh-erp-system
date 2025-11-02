import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/product.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import '../utils/currency_formatter.dart';
import '../utils/tsh_theme.dart';
import '../screens/product_detail_screen_enhanced.dart';

/// Enhanced professional product card with animations and better design
class EnhancedProductCard extends ConsumerStatefulWidget {
  final Product product;
  final VoidCallback? onAddedToCart;

  const EnhancedProductCard({
    super.key,
    required this.product,
    this.onAddedToCart,
  });

  @override
  ConsumerState<EnhancedProductCard> createState() => _EnhancedProductCardState();
}

class _EnhancedProductCardState extends ConsumerState<EnhancedProductCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    _controller.forward();
  }

  void _handleTapUp(TapUpDetails details) {
    _controller.reverse();
  }

  void _handleTapCancel() {
    _controller.reverse();
  }

  void _navigateToDetail() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ProductDetailScreenEnhanced(product: widget.product),
      ),
    );
  }

  void _addToCart() {
    ref.read(cartProvider.notifier).addItem(widget.product);

    // Show elegant snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.white, size: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'تمت إضافة ${widget.product.name} إلى السلة',
                style: const TextStyle(fontSize: 14),
              ),
            ),
          ],
        ),
        backgroundColor: TSHTheme.successGreen,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        duration: const Duration(seconds: 2),
      ),
    );

    widget.onAddedToCart?.call();
  }

  @override
  Widget build(BuildContext context) {
    final imageUrl = ApiService.getProductImageUrl(widget.product);

    return GestureDetector(
      onTap: _navigateToDetail,
      child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.grey.withOpacity(0.1),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: TSHTheme.primary.withOpacity(0.08),
                blurRadius: 24,
                offset: const Offset(0, 8),
                spreadRadius: -4,
              ),
              BoxShadow(
                color: Colors.black.withOpacity(0.03),
                blurRadius: 12,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Product Image with Hero Animation
                _buildProductImage(imageUrl),

                // Product Info
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Category Badge
                        if (widget.product.category != null)
                          _buildCategoryBadge(),

                        const SizedBox(height: 8),

                        // Product Name - More Prominent
                        Container(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Text(
                            widget.product.name,
                            style: TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 16,
                              height: 1.3,
                              letterSpacing: -0.3,
                              color: TSHTheme.textPrimary,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            textAlign: TextAlign.start,
                          ),
                        ),

                        // Product Description (if available)
                        if (widget.product.description != null && widget.product.description!.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(
                            widget.product.description!,
                            style: TextStyle(
                              fontSize: 12,
                              color: TSHTheme.textSecondary.withOpacity(0.8),
                              height: 1.3,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],

                        const Spacer(),

                        // Price Section
                        _buildPriceSection(),

                        const SizedBox(height: 8),

                        // Add to Cart Button
                        _buildAddToCartButton(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
    );
  }

  Widget _buildProductImage(String imageUrl) {
    return Hero(
      tag: 'product-${widget.product.id}',
      child: Stack(
        children: [
          // Image Container with Gradient Background
          Container(
            height: 180,
            width: double.infinity,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  TSHTheme.primary.withOpacity(0.03),
                  TSHTheme.accent.withOpacity(0.03),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              fit: BoxFit.contain,
              httpHeaders: const {
                'Access-Control-Allow-Origin': '*',
              },
              placeholder: (context, url) => Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.grey[100]!,
                      Colors.grey[200]!,
                    ],
                  ),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.shopping_bag_outlined,
                        size: 48,
                        color: TSHTheme.primary.withOpacity(0.3),
                      ),
                      const SizedBox(height: 8),
                      SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            TSHTheme.primary.withOpacity(0.5),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              errorWidget: (context, url, error) => Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      TSHTheme.primary.withOpacity(0.08),
                      TSHTheme.accent.withOpacity(0.08),
                      Colors.white.withOpacity(0.95),
                    ],
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: TSHTheme.primary.withOpacity(0.15),
                            blurRadius: 20,
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: Icon(
                        Icons.inventory_2_outlined,
                        size: 48,
                        color: TSHTheme.primary,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Text(
                        widget.product.name,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: TSHTheme.textPrimary.withOpacity(0.7),
                          height: 1.3,
                        ),
                        textAlign: TextAlign.center,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Stock Badge - Top Right
          Positioned(
            top: 10,
            right: 10,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: widget.product.lowStock
                    ? TSHTheme.warningOrange
                    : TSHTheme.successGreen,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: (widget.product.lowStock
                            ? TSHTheme.warningOrange
                            : TSHTheme.successGreen)
                        .withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Text(
                widget.product.lowStock ? 'مخزون قليل' : 'متوفر',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),

          // Discount Badge (if applicable) - Top Left
          if (widget.product.hasDiscount)
            Positioned(
              top: 10,
              left: 10,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: TSHTheme.errorRed,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Text(
                  'تخفيض',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildCategoryBadge() {
    // Translate "Uncategorized" to Arabic
    String categoryText = widget.product.category!;
    if (categoryText.toLowerCase() == 'uncategorized') {
      categoryText = 'غير مصنف';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            TSHTheme.primary.withOpacity(0.12),
            TSHTheme.accent.withOpacity(0.12),
          ],
        ),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: TSHTheme.primary.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Text(
        categoryText,
        style: TextStyle(
          color: TSHTheme.primary,
          fontSize: 11,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.2,
        ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
    );
  }

  Widget _buildPriceSection() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            TSHTheme.primary.withOpacity(0.10),
            TSHTheme.accent.withOpacity(0.06),
          ],
        ),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: TSHTheme.primary.withOpacity(0.15),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(
              CurrencyFormatter.formatCurrency(
                widget.product.price,
                widget.product.currency,
              ),
              style: TextStyle(
                color: TSHTheme.primary,
                fontWeight: FontWeight.w800,
                fontSize: 15,
                letterSpacing: -0.3,
              ),
            ),
          ),
          Icon(
            Icons.arrow_forward_rounded,
            color: TSHTheme.primary.withOpacity(0.5),
            size: 16,
          ),
        ],
      ),
    );
  }

  Widget _buildAddToCartButton() {
    return Container(
      width: double.infinity,
      height: 38,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [TSHTheme.primary, TSHTheme.accent],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: TSHTheme.primary.withOpacity(0.25),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: widget.product.hasPrice ? _addToCart : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          foregroundColor: Colors.white,
          elevation: 0,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(vertical: 8),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.add_shopping_cart_rounded, size: 16),
            SizedBox(width: 6),
            Text(
              'إضافة للسلة',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Extension to check for discount
extension ProductExtension on Product {
  bool get hasDiscount {
    // You can add discount logic here based on your backend
    // For now, returning false
    return false;
  }
}
