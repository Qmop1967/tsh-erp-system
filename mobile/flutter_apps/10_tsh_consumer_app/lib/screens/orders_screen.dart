import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/order.dart';
import '../services/api_service.dart';
import '../utils/tsh_theme.dart';
import '../utils/currency_formatter.dart';

final ordersProvider = FutureProvider<List<Order>>((ref) async {
  try {
    final ordersData = await ApiService.getMyOrders();
    return ordersData.map((json) => Order.fromJson(json)).toList();
  } catch (e) {
    return [];
  }
});

class OrdersScreen extends ConsumerStatefulWidget {
  const OrdersScreen({super.key});

  @override
  ConsumerState<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends ConsumerState<OrdersScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut),
    );
    _fadeController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ordersAsync = ref.watch(ordersProvider);

    return Scaffold(
      backgroundColor: TSHTheme.backgroundLight,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: const Text(
          'طلباتي',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: TSHTheme.textPrimary,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: TSHTheme.primary),
            onPressed: () {
              ref.invalidate(ordersProvider);
            },
          ),
        ],
      ),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: ordersAsync.when(
          data: (orders) {
            if (orders.isEmpty) {
              return _buildEmptyState();
            }
            return RefreshIndicator(
              onRefresh: () async {
                ref.invalidate(ordersProvider);
              },
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: orders.length,
                itemBuilder: (context, index) {
                  return _buildOrderCard(context, orders[index], index);
                },
              ),
            );
          },
          loading: () => _buildLoadingState(),
          error: (error, stack) => _buildErrorState(error.toString()),
        ),
      ),
    );
  }

  Widget _buildOrderCard(BuildContext context, Order order, int index) {
    return TweenAnimationBuilder<double>(
      duration: Duration(milliseconds: 300 + (index * 100)),
      tween: Tween(begin: 0.0, end: 1.0),
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, 20 * (1 - value)),
            child: child,
          ),
        );
      },
      child: Card(
        elevation: 2,
        margin: const EdgeInsets.only(bottom: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: InkWell(
          onTap: () => _showOrderDetails(context, order),
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Order header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'طلب #${order.orderNumber}',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: TSHTheme.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            order.getFormattedDate(),
                            style: TextStyle(
                              fontSize: 13,
                              color: TSHTheme.mutedForeground,
                            ),
                          ),
                        ],
                      ),
                    ),
                    _buildStatusBadge(order.status),
                  ],
                ),
                const SizedBox(height: 16),
                const Divider(height: 1),
                const SizedBox(height: 16),

                // Order items preview
                ...order.items.take(2).map((item) => _buildOrderItemPreview(item)),

                if (order.items.length > 2)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      'و ${order.items.length - 2} منتج آخر...',
                      style: TextStyle(
                        fontSize: 13,
                        color: TSHTheme.mutedForeground,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),

                const SizedBox(height: 16),
                const Divider(height: 1),
                const SizedBox(height: 16),

                // Total and action
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'المجموع',
                          style: TextStyle(
                            fontSize: 13,
                            color: TSHTheme.mutedForeground,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          CurrencyFormatter.format(order.totalAmount, order.currency),
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: TSHTheme.primary,
                          ),
                        ),
                      ],
                    ),
                    TextButton.icon(
                      onPressed: () => _showOrderDetails(context, order),
                      icon: const Icon(Icons.arrow_back, size: 18),
                      label: const Text('التفاصيل'),
                      style: TextButton.styleFrom(
                        foregroundColor: TSHTheme.primary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildOrderItemPreview(OrderItem item) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          // Product image
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: Colors.grey[100],
            ),
            child: item.imageUrl != null
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: CachedNetworkImage(
                      imageUrl: item.imageUrl!,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(
                        color: Colors.grey[200],
                      ),
                      errorWidget: (context, url, error) => Icon(
                        Icons.image_outlined,
                        color: Colors.grey[400],
                        size: 24,
                      ),
                    ),
                  )
                : Icon(
                    Icons.image_outlined,
                    color: Colors.grey[400],
                    size: 24,
                  ),
          ),
          const SizedBox(width: 12),

          // Product info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.productName,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: TSHTheme.textPrimary,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  'الكمية: ${item.quantity}',
                  style: TextStyle(
                    fontSize: 12,
                    color: TSHTheme.mutedForeground,
                  ),
                ),
              ],
            ),
          ),

          // Price
          Text(
            CurrencyFormatter.format(item.subtotal, 'IQD'),
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: TSHTheme.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color badgeColor;
    IconData icon;

    switch (status.toLowerCase()) {
      case 'delivered':
        badgeColor = TSHTheme.success;
        icon = Icons.check_circle;
        break;
      case 'shipped':
        badgeColor = Colors.blue;
        icon = Icons.local_shipping;
        break;
      case 'processing':
        badgeColor = Colors.orange;
        icon = Icons.sync;
        break;
      case 'cancelled':
        badgeColor = TSHTheme.destructive;
        icon = Icons.cancel;
        break;
      default:
        badgeColor = Colors.grey;
        icon = Icons.schedule;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            badgeColor.withOpacity(0.8),
            badgeColor,
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: badgeColor.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.white),
          const SizedBox(width: 4),
          Text(
            Order(
              id: '',
              orderNumber: '',
              status: status,
              totalAmount: 0,
              currency: '',
              createdAt: DateTime.now(),
              customerName: '',
              customerEmail: '',
              customerPhone: '',
              deliveryAddress: '',
              items: [],
            ).getStatusText(),
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [
                  TSHTheme.primary.withOpacity(0.1),
                  TSHTheme.accent.withOpacity(0.1),
                ],
              ),
            ),
            child: const Icon(
              Icons.receipt_long_outlined,
              size: 60,
              color: TSHTheme.primary,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'لا توجد طلبات بعد',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: TSHTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ابدأ التسوق لإنشاء طلبك الأول',
            style: TextStyle(
              fontSize: 16,
              color: TSHTheme.mutedForeground,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 3,
      itemBuilder: (context, index) {
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Container(
            height: 200,
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 150,
                  height: 20,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(height: 16),
                ...List.generate(
                  2,
                  (i) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        Container(
                          width: 50,
                          height: 50,
                          decoration: BoxDecoration(
                            color: Colors.grey[300],
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                width: double.infinity,
                                height: 14,
                                decoration: BoxDecoration(
                                  color: Colors.grey[300],
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              const SizedBox(height: 8),
                              Container(
                                width: 80,
                                height: 12,
                                decoration: BoxDecoration(
                                  color: Colors.grey[300],
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            size: 64,
            color: TSHTheme.destructive,
          ),
          const SizedBox(height: 16),
          const Text(
            'حدث خطأ في تحميل الطلبات',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: TSHTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: TextStyle(
              fontSize: 14,
              color: TSHTheme.mutedForeground,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              ref.invalidate(ordersProvider);
            },
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
            style: ElevatedButton.styleFrom(
              backgroundColor: TSHTheme.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showOrderDetails(BuildContext context, Order order) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.85,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) {
          return Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(24),
                topRight: Radius.circular(24),
              ),
            ),
            child: Column(
              children: [
                // Handle
                Container(
                  margin: const EdgeInsets.symmetric(vertical: 12),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),

                // Header
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'طلب #${order.orderNumber}',
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: TSHTheme.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            order.getFormattedDate(),
                            style: TextStyle(
                              fontSize: 14,
                              color: TSHTheme.mutedForeground,
                            ),
                          ),
                        ],
                      ),
                      _buildStatusBadge(order.status),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Content
                Expanded(
                  child: ListView(
                    controller: scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    children: [
                      // Customer info
                      _buildDetailSection(
                        'معلومات العميل',
                        Icons.person_outline,
                        [
                          _buildDetailRow('الاسم', order.customerName),
                          _buildDetailRow('البريد الإلكتروني', order.customerEmail),
                          _buildDetailRow('الهاتف', order.customerPhone),
                          _buildDetailRow('عنوان التوصيل', order.deliveryAddress),
                          if (order.notes != null && order.notes!.isNotEmpty)
                            _buildDetailRow('ملاحظات', order.notes!),
                        ],
                      ),
                      const SizedBox(height: 24),

                      // Order items
                      _buildDetailSection(
                        'المنتجات',
                        Icons.shopping_bag_outlined,
                        order.items.map((item) => _buildDetailOrderItem(item)).toList(),
                      ),
                      const SizedBox(height: 24),

                      // Total
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              TSHTheme.primary.withOpacity(0.1),
                              TSHTheme.accent.withOpacity(0.1),
                            ],
                          ),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'المجموع الكلي',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: TSHTheme.textPrimary,
                              ),
                            ),
                            Text(
                              CurrencyFormatter.format(order.totalAmount, order.currency),
                              style: const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: TSHTheme.primary,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 20),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildDetailSection(String title, IconData icon, List<Widget> children) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      TSHTheme.primary.withOpacity(0.1),
                      TSHTheme.accent.withOpacity(0.1),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 20, color: TSHTheme.primary),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: TSHTheme.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...children,
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: TSHTheme.mutedForeground,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                color: TSHTheme.textPrimary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailOrderItem(OrderItem item) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Image
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: Colors.grey[100],
            ),
            child: item.imageUrl != null
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: CachedNetworkImage(
                      imageUrl: item.imageUrl!,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(
                        color: Colors.grey[200],
                      ),
                      errorWidget: (context, url, error) => Icon(
                        Icons.image_outlined,
                        color: Colors.grey[400],
                        size: 30,
                      ),
                    ),
                  )
                : Icon(
                    Icons.image_outlined,
                    color: Colors.grey[400],
                    size: 30,
                  ),
          ),
          const SizedBox(width: 12),

          // Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.productName,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: TSHTheme.textPrimary,
                  ),
                ),
                if (item.productSku != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    'رمز المنتج: ${item.productSku}',
                    style: TextStyle(
                      fontSize: 12,
                      color: TSHTheme.mutedForeground,
                    ),
                  ),
                ],
                const SizedBox(height: 8),
                Row(
                  children: [
                    Text(
                      'الكمية: ${item.quantity}',
                      style: TextStyle(
                        fontSize: 13,
                        color: TSHTheme.mutedForeground,
                      ),
                    ),
                    Text(
                      ' × ',
                      style: TextStyle(
                        fontSize: 13,
                        color: TSHTheme.mutedForeground,
                      ),
                    ),
                    Text(
                      CurrencyFormatter.format(item.price, 'IQD'),
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: TSHTheme.textPrimary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Subtotal
          Text(
            CurrencyFormatter.format(item.subtotal, 'IQD'),
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: TSHTheme.primary,
            ),
          ),
        ],
      ),
    );
  }
}
