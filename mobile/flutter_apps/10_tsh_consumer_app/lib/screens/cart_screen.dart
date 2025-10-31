import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/cart_item.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import '../utils/currency_formatter.dart';
import '../utils/tsh_theme.dart';
import 'checkout_screen.dart';

class CartScreen extends ConsumerWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cart = ref.watch(cartProvider);
    final cartNotifier = ref.read(cartProvider.notifier);

    if (cart.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('سلة التسوق'),
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.grey[100]!, Colors.grey[200]!],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.shopping_cart_outlined,
                  size: 60,
                  color: TSHTheme.mutedForeground,
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'سلة التسوق فارغة',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: TSHTheme.textPrimary,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'لم تقم بإضافة أي منتجات إلى سلة التسوق بعد',
                style: TextStyle(
                  fontSize: 16,
                  color: TSHTheme.mutedForeground,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.shopping_bag),
                label: const Text('تصفح المنتجات'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final totalItems = cartNotifier.getTotalItems();
    final totalPrice = cartNotifier.getTotalPrice();

    return Scaffold(
      appBar: AppBar(
        title: const Text('سلة التسوق'),
        actions: [
          TextButton.icon(
            onPressed: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('إفراغ السلة'),
                  content: const Text('هل أنت متأكد من إفراغ سلة التسوق؟'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('إلغاء'),
                    ),
                    TextButton(
                      onPressed: () {
                        cartNotifier.clearCart();
                        Navigator.pop(context);
                      },
                      child: Text('إفراغ', style: TextStyle(color: TSHTheme.errorRed)),
                    ),
                  ],
                ),
              );
            },
            icon: Icon(Icons.delete_outline, color: TSHTheme.errorRed),
            label: Text('إفراغ السلة', style: TextStyle(color: TSHTheme.errorRed)),
          ),
        ],
      ),
      body: Column(
        children: [
          // Cart Summary Header
          Container(
            padding: const EdgeInsets.all(16),
            color: TSHTheme.muted,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(Icons.shopping_cart, color: TSHTheme.primary),
                    const SizedBox(width: 8),
                    Text(
                      'لديك ',
                      style: TextStyle(color: TSHTheme.textSecondary),
                    ),
                    Text(
                      '$totalItems',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: TSHTheme.primary,
                      ),
                    ),
                    Text(
                      ' منتج في السلة',
                      style: TextStyle(color: TSHTheme.textSecondary),
                    ),
                  ],
                ),
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('متابعة التسوق'),
                ),
              ],
            ),
          ),

          // Cart Items List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: cart.length,
              itemBuilder: (context, index) {
                return _CartItemCard(
                  item: cart[index],
                  onRemove: () => cartNotifier.removeItem(cart[index].product.id),
                  onUpdateQuantity: (quantity) =>
                      cartNotifier.updateQuantity(cart[index].product.id, quantity),
                  onUpdateComment: (comment) =>
                      cartNotifier.updateComment(cart[index].product.id, comment),
                );
              },
            ),
          ),

          // Cart Summary Footer
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: SafeArea(
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'الإجمالي',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        CurrencyFormatter.formatCurrency(totalPrice),
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: TSHTheme.primary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const CheckoutScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.payment, size: 24),
                      label: const Text(
                        'إتمام الطلب',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CartItemCard extends StatefulWidget {
  final CartItem item;
  final VoidCallback onRemove;
  final Function(int) onUpdateQuantity;
  final Function(String) onUpdateComment;

  const _CartItemCard({
    required this.item,
    required this.onRemove,
    required this.onUpdateQuantity,
    required this.onUpdateComment,
  });

  @override
  State<_CartItemCard> createState() => _CartItemCardState();
}

class _CartItemCardState extends State<_CartItemCard> {
  late TextEditingController _commentController;
  bool _showCommentField = false;

  @override
  void initState() {
    super.initState();
    _commentController = TextEditingController(text: widget.item.comment ?? '');
    _showCommentField = widget.item.comment != null && widget.item.comment!.isNotEmpty;
  }

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final imageUrl = ApiService.getProductImageUrl(widget.item.product);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Product Image
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Colors.grey[100]!, Colors.grey[200]!],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: CachedNetworkImage(
                      imageUrl: imageUrl,
                      fit: BoxFit.contain,
                      placeholder: (context, url) => const Center(
                        child: CircularProgressIndicator(),
                      ),
                      errorWidget: (context, url, error) => const Icon(
                        Icons.image_not_supported,
                        size: 40,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),

                // Product Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Text(
                              widget.item.product.name,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          IconButton(
                            onPressed: widget.onRemove,
                            icon: Icon(Icons.delete_outline, color: TSHTheme.errorRed),
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'سعر الوحدة: ${CurrencyFormatter.formatCurrency(widget.item.product.price)}',
                        style: TextStyle(
                          color: TSHTheme.textSecondary,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          // Quantity Controls
                          Container(
                            decoration: BoxDecoration(
                              border: Border.all(color: TSHTheme.border),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              children: [
                                IconButton(
                                  onPressed: () {
                                    if (widget.item.quantity > 1) {
                                      widget.onUpdateQuantity(widget.item.quantity - 1);
                                    }
                                  },
                                  icon: const Icon(Icons.remove),
                                  iconSize: 20,
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 12),
                                  child: Text(
                                    '${widget.item.quantity}',
                                    style: const TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                IconButton(
                                  onPressed: () {
                                    if (widget.item.quantity < widget.item.product.stockQuantity) {
                                      widget.onUpdateQuantity(widget.item.quantity + 1);
                                    }
                                  },
                                  icon: const Icon(Icons.add),
                                  iconSize: 20,
                                ),
                              ],
                            ),
                          ),

                          // Total Price
                          Text(
                            CurrencyFormatter.formatCurrency(widget.item.totalPrice),
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: TSHTheme.primary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),

            // Comment Section
            const SizedBox(height: 8),
            if (_showCommentField)
              TextField(
                controller: _commentController,
                decoration: InputDecoration(
                  labelText: 'ملاحظات على المنتج (اختياري)',
                  hintText: 'مثال: اللون الأزرق، الحجم الكبير...',
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () {
                      setState(() {
                        _showCommentField = false;
                        _commentController.clear();
                        widget.onUpdateComment('');
                      });
                    },
                  ),
                ),
                maxLines: 2,
                onChanged: (value) => widget.onUpdateComment(value),
              )
            else
              TextButton.icon(
                onPressed: () => setState(() => _showCommentField = true),
                icon: const Icon(Icons.comment_outlined, size: 16),
                label: const Text('إضافة ملاحظة'),
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
