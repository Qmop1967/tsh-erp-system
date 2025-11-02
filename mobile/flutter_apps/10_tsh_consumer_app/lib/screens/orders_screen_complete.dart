import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../models/order.dart';
import '../services/api_service.dart';
import '../utils/tsh_theme.dart';
import '../utils/currency_formatter.dart';

final ordersProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  return await ApiService.getMyOrders();
});

class OrdersScreenComplete extends ConsumerStatefulWidget {
  const OrdersScreenComplete({super.key});

  @override
  ConsumerState<OrdersScreenComplete> createState() =>
      _OrdersScreenCompleteState();
}

class _OrdersScreenCompleteState extends ConsumerState<OrdersScreenComplete> {
  String _selectedFilter = 'الكل';
  final List<String> _filters = [
    'الكل',
    'قيد المعالجة',
    'تم الشحن',
    'تم التسليم',
    'ملغي'
  ];

  @override
  Widget build(BuildContext context) {
    final ordersAsync = ref.watch(ordersProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          'طلباتي',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () => _showFilterDialog(),
          ),
        ],
      ),
      body: ordersAsync.when(
        data: (orders) => _buildOrdersList(orders),
        loading: () => _buildLoadingState(),
        error: (error, stack) => _buildErrorState(error),
      ),
    );
  }

  Widget _buildOrdersList(List<Map<String, dynamic>> orders) {
    if (orders.isEmpty) {
      return _buildEmptyState();
    }

    final filteredOrders = _filterOrders(orders);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(ordersProvider);
      },
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredOrders.length,
        itemBuilder: (context, index) {
          return _buildOrderCard(filteredOrders[index]);
        },
      ),
    );
  }

  List<Map<String, dynamic>> _filterOrders(List<Map<String, dynamic>> orders) {
    if (_selectedFilter == 'الكل') return orders;

    return orders.where((order) {
      final status = order['status'] as String? ?? '';
      return _getStatusArabic(status) == _selectedFilter;
    }).toList();
  }

  Widget _buildOrderCard(Map<String, dynamic> order) {
    final orderId = order['id'] ?? 'N/A';
    final status = order['status'] as String? ?? 'pending';
    final total = (order['total'] as num?)?.toDouble() ?? 0.0;
    final createdAt = order['created_at'] as String?;
    final items = (order['items'] as List?)?.length ?? 0;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () => _showOrderDetails(order),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Order Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'طلب رقم #$orderId',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  _buildStatusChip(status),
                ],
              ),
              const SizedBox(height: 12),

              // Order Info
              Row(
                children: [
                  Icon(Icons.calendar_today,
                      size: 16, color: TSHTheme.mutedForeground),
                  const SizedBox(width: 8),
                  Text(
                    _formatDate(createdAt),
                    style: TextStyle(
                      color: TSHTheme.mutedForeground,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(width: 24),
                  Icon(Icons.shopping_bag,
                      size: 16, color: TSHTheme.mutedForeground),
                  const SizedBox(width: 8),
                  Text(
                    '$items منتج',
                    style: TextStyle(
                      color: TSHTheme.mutedForeground,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Total Amount
              Container(
                padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                decoration: BoxDecoration(
                  color: TSHTheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'المجموع:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Text(
                      CurrencyFormatter.formatIQD(total),
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: TSHTheme.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    final statusInfo = _getStatusInfo(status);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: statusInfo['color'].withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: statusInfo['color'], width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(statusInfo['icon'], size: 16, color: statusInfo['color']),
          const SizedBox(width: 4),
          Text(
            statusInfo['label'],
            style: TextStyle(
              color: statusInfo['color'],
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Map<String, dynamic> _getStatusInfo(String status) {
    switch (status.toLowerCase()) {
      case 'delivered':
        return {
          'label': 'تم التسليم',
          'color': Colors.green,
          'icon': Icons.check_circle
        };
      case 'shipped':
        return {
          'label': 'تم الشحن',
          'color': Colors.blue,
          'icon': Icons.local_shipping
        };
      case 'cancelled':
        return {
          'label': 'ملغي',
          'color': Colors.red,
          'icon': Icons.cancel
        };
      default:
        return {
          'label': 'قيد المعالجة',
          'color': Colors.orange,
          'icon': Icons.schedule
        };
    }
  }

  String _getStatusArabic(String status) {
    return _getStatusInfo(status)['label'];
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return 'تاريخ غير متوفر';

    try {
      final date = DateTime.parse(dateStr);
      return DateFormat('yyyy/MM/dd', 'ar').format(date);
    } catch (e) {
      return dateStr;
    }
  }

  void _showOrderDetails(Map<String, dynamic> order) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            children: [
              // Handle
              Container(
                margin: const EdgeInsets.only(top: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),

              // Header
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'تفاصيل الطلب #${order['id']}',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
              ),

              const Divider(height: 1),

              // Content
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.all(16),
                  children: [
                    _buildDetailSection('معلومات الطلب', [
                      _buildDetailRow('رقم الطلب', '#${order['id']}'),
                      _buildDetailRow('الحالة', _getStatusArabic(order['status'] ?? '')),
                      _buildDetailRow('التاريخ', _formatDate(order['created_at'])),
                    ]),

                    const SizedBox(height: 24),

                    if (order['items'] != null)
                      _buildDetailSection(
                        'المنتجات',
                        (order['items'] as List).map((item) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    '${item['name']} x${item['quantity']}',
                                    style: const TextStyle(fontSize: 14),
                                  ),
                                ),
                                Text(
                                  CurrencyFormatter.formatIQD(
                                      (item['price'] as num).toDouble()),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                    const SizedBox(height: 24),

                    _buildDetailSection('معلومات التوصيل', [
                      if (order['customer_name'] != null)
                        _buildDetailRow('الاسم', order['customer_name']),
                      if (order['customer_phone'] != null)
                        _buildDetailRow('الهاتف', order['customer_phone']),
                      if (order['delivery_address'] != null)
                        _buildDetailRow('العنوان', order['delivery_address']),
                    ]),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...children,
      ],
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(color: TSHTheme.mutedForeground),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
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
          Icon(
            Icons.shopping_bag_outlined,
            size: 100,
            color: TSHTheme.mutedForeground.withOpacity(0.5),
          ),
          const SizedBox(height: 24),
          const Text(
            'لا توجد طلبات بعد',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ابدأ بالتسوق لإنشاء طلبك الأول',
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
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(color: TSHTheme.primary),
          const SizedBox(height: 16),
          const Text('جاري تحميل الطلبات...'),
        ],
      ),
    );
  }

  Widget _buildErrorState(Object error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 80,
            color: TSHTheme.destructive,
          ),
          const SizedBox(height: 24),
          const Text(
            'حدث خطأ في تحميل الطلبات',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error.toString(),
            style: TextStyle(
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
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تصفية الطلبات'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: _filters.map((filter) {
            return RadioListTile<String>(
              title: Text(filter),
              value: filter,
              groupValue: _selectedFilter,
              activeColor: TSHTheme.primary,
              onChanged: (value) {
                setState(() {
                  _selectedFilter = value!;
                });
                Navigator.pop(context);
              },
            );
          }).toList(),
        ),
      ),
    );
  }
}
