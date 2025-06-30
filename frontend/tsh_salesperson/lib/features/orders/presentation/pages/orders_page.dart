import 'package:flutter/material.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

class OrdersPage extends StatefulWidget {
  const OrdersPage({super.key});

  @override
  State<OrdersPage> createState() => _OrdersPageState();
}

class _OrdersPageState extends State<OrdersPage> with TickerProviderStateMixin {
  late TabController _tabController;
  String _searchQuery = '';
  OrderStatus? _statusFilter;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Search and Filter Bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                AppTextField(
                  hint: 'Search orders...',
                  prefixIcon: const Icon(Icons.search),
                  onChanged: (value) {
                    setState(() {
                      _searchQuery = value;
                    });
                  },
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<OrderStatus?>(
                        value: _statusFilter,
                        decoration: const InputDecoration(
                          labelText: 'Filter by Status',
                          prefixIcon: Icon(Icons.filter_list),
                        ),
                        items: [
                          const DropdownMenuItem(
                            value: null,
                            child: Text('All Statuses'),
                          ),
                          ...OrderStatus.values.map((status) => DropdownMenuItem(
                                value: status,
                                child: Text(status.name.toUpperCase()),
                              )),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _statusFilter = value;
                          });
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton.icon(
                      onPressed: _exportOrders,
                      icon: const Icon(Icons.download),
                      label: const Text('Export'),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // Tab Bar
          Container(
            color: Colors.white,
            child: TabBar(
              controller: _tabController,
              tabs: const [
                Tab(text: 'All Orders'),
                Tab(text: 'Pending'),
                Tab(text: 'Completed'),
              ],
            ),
          ),
          
          // Tab Bar View
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildOrdersList(_getFilteredOrders()),
                _buildOrdersList(_getOrdersByStatus(OrderStatus.pending)),
                _buildOrdersList(_getOrdersByStatus(OrderStatus.delivered)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOrdersList(List<Order> orders) {
    if (orders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.shopping_cart_outlined,
              size: 64,
              color: AppColors.textSecondary400,
            ),
            const SizedBox(height: 16),
            Text(
              'No orders found',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Orders will appear here once created',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: AppColors.textSecondary500,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async {
        // TODO: Implement refresh
        await Future.delayed(const Duration(seconds: 1));
      },
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: orders.length,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final order = orders[index];
          return _buildOrderCard(order);
        },
      ),
    );
  }

  Widget _buildOrderCard(Order order) {
    return AppCard(
      onTap: () => _showOrderDetails(order),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                order.orderNumber,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              _buildOrderStatusChip(order.status),
            ],
          ),
          const SizedBox(height: 8),
          
          // Customer Info (if available)
          if (order.customer != null) ...[
            Row(
              children: [
                Icon(
                  Icons.person_outline,
                  size: 16,
                  color: AppColors.textSecondary,
                ),
                const SizedBox(width: 4),
                Text(
                  order.customer!.fullName,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
          ],
          
          // Order Details Row
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Total Amount',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      '\$${order.totalAmount.toStringAsFixed(2)}',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Items',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      '${order.totalItems} items',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Date',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    Text(
                      _formatDate(order.createdAt),
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          // Payment Status and Actions
          Row(
            children: [
              _buildPaymentStatusChip(order.paymentStatus),
              const Spacer(),
              if (order.canBeCancelled) ...[
                TextButton(
                  onPressed: () => _cancelOrder(order),
                  child: Text(
                    'Cancel',
                    style: TextStyle(color: AppColors.error),
                  ),
                ),
                const SizedBox(width: 8),
              ],
              TextButton(
                onPressed: () => _showOrderDetails(order),
                child: const Text('View Details'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOrderStatusChip(OrderStatus status) {
    Color color;
    switch (status) {
      case OrderStatus.pending:
        color = AppColors.warning;
        break;
      case OrderStatus.confirmed:
        color = AppColors.info;
        break;
      case OrderStatus.processing:
        color = AppColors.primary;
        break;
      case OrderStatus.shipped:
        color = AppColors.secondary;
        break;
      case OrderStatus.delivered:
        color = AppColors.success;
        break;
      case OrderStatus.cancelled:
      case OrderStatus.refunded:
        color = AppColors.error;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        status.name.toUpperCase(),
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildPaymentStatusChip(PaymentStatus status) {
    Color color;
    switch (status) {
      case PaymentStatus.pending:
        color = AppColors.warning;
        break;
      case PaymentStatus.paid:
        color = AppColors.success;
        break;
      case PaymentStatus.failed:
      case PaymentStatus.refunded:
        color = AppColors.error;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            status == PaymentStatus.paid ? Icons.check_circle : Icons.schedule,
            size: 12,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            status.name.toUpperCase(),
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  void _showOrderDetails(Order order) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.8,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle bar
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.textSecondary300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              
              // Order Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Order Details',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  _buildOrderStatusChip(order.status),
                ],
              ),
              const SizedBox(height: 16),
              
              // Order Info Cards
              Row(
                children: [
                  Expanded(
                    child: AppStatsCard(
                      title: 'Order Number',
                      value: order.orderNumber,
                      icon: Icons.receipt,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: AppStatsCard(
                      title: 'Total Amount',
                      value: '\$${order.totalAmount.toStringAsFixed(2)}',
                      icon: Icons.attach_money,
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              // Customer Info
              if (order.customer != null) ...[
                AppCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Customer Information',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        order.customer!.fullName,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      if (order.customer!.email.isNotEmpty)
                        Text(
                          order.customer!.email,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],
              
              // Order Items
              Text(
                'Order Items',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Expanded(
                child: ListView.separated(
                  controller: scrollController,
                  itemCount: order.items.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final item = order.items[index];
                    return _buildOrderItemCard(item);
                  },
                ),
              ),
              
              // Actions
              const SizedBox(height: 16),
              Row(
                children: [
                  if (order.canBeCancelled) ...[
                    Expanded(
                      child: AppButton.outline(
                        text: 'Cancel Order',
                        customColor: AppColors.error,
                        onPressed: () => _cancelOrder(order),
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    child: AppButton.primary(
                      text: 'Update Status',
                      onPressed: () => _updateOrderStatus(order),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOrderItemCard(OrderItem item) {
    return AppCard(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: AppColors.textSecondary100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.inventory_2_outlined,
              color: AppColors.textSecondary400,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.product?.name ?? 'Product ${item.productId}',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Qty: ${item.quantity} × \$${item.unitPrice.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Text(
            '\$${item.totalPrice.toStringAsFixed(2)}',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  List<Order> _getFilteredOrders() {
    return _mockOrders.where((order) {
      // Search filter
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        if (!order.orderNumber.toLowerCase().contains(query) &&
            !(order.customer?.fullName.toLowerCase().contains(query) ?? false)) {
          return false;
        }
      }
      
      // Status filter
      if (_statusFilter != null && order.status != _statusFilter) {
        return false;
      }
      
      return true;
    }).toList();
  }

  List<Order> _getOrdersByStatus(OrderStatus status) {
    return _mockOrders.where((order) => order.status == status).toList();
  }

  void _cancelOrder(Order order) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Order'),
        content: Text('Are you sure you want to cancel order ${order.orderNumber}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('No'),
          ),
          AppButton.primary(
            text: 'Yes, Cancel',
            customColor: AppColors.error,
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // Close details if open
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Order ${order.orderNumber} cancelled'),
                  backgroundColor: AppColors.error,
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _updateOrderStatus(Order order) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Update Order Status'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: OrderStatus.values.map((status) => 
            ListTile(
              title: Text(status.name.toUpperCase()),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).pop(); // Close details
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Order ${order.orderNumber} updated to ${status.name}'),
                    backgroundColor: AppColors.success,
                  ),
                );
              },
            ),
          ).toList(),
        ),
      ),
    );
  }

  void _exportOrders() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Orders exported successfully'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    
    if (diff.inDays == 0) {
      return 'Today';
    } else if (diff.inDays == 1) {
      return 'Yesterday';
    } else if (diff.inDays < 7) {
      return '${diff.inDays} days ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}

// Mock orders data
final List<Order> _mockOrders = List.generate(15, (index) => 
  Order(
    id: index + 1,
    orderNumber: 'ORD-${DateTime.now().millisecondsSinceEpoch + index}',
    customerId: index % 3 == 0 ? index + 1 : null,
    customer: index % 3 == 0 ? User(
      id: index + 1,
      email: 'customer${index + 1}@example.com',
      firstName: 'Customer',
      lastName: '${index + 1}',
      isActive: true,
      createdAt: DateTime.now().subtract(Duration(days: index)),
      updatedAt: DateTime.now().subtract(Duration(days: index)),
    ) : null,
    salesPersonId: 1,
    salesPerson: User(
      id: 1,
      email: 'demo@tsh.com',
      firstName: 'Demo',
      lastName: 'User',
      isActive: true,
      createdAt: DateTime.parse('2024-01-01T00:00:00Z'),
      updatedAt: DateTime.parse('2024-01-01T00:00:00Z'),
    ),
    status: OrderStatus.values[index % OrderStatus.values.length],
    paymentStatus: PaymentStatus.values[index % PaymentStatus.values.length],
    subtotal: 100.0 + (index * 50),
    taxAmount: 10.0 + (index * 5),
    discountAmount: index % 3 == 0 ? 20.0 : 0.0,
    totalAmount: 110.0 + (index * 55) - (index % 3 == 0 ? 20.0 : 0.0),
    items: List.generate(
      (index % 3) + 1,
      (itemIndex) => OrderItem(
        id: (index * 10) + itemIndex,
        orderId: index + 1,
        productId: itemIndex + 1,
        product: Product(
          id: itemIndex + 1,
          name: 'Product ${itemIndex + 1}',
          sku: 'SKU${itemIndex + 1}',
          price: 25.0 + (itemIndex * 10),
          stockQuantity: 10,
          isActive: true,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ),
        quantity: (itemIndex % 3) + 1,
        unitPrice: 25.0 + (itemIndex * 10),
        totalPrice: (25.0 + (itemIndex * 10)) * ((itemIndex % 3) + 1),
      ),
    ),
    createdAt: DateTime.now().subtract(Duration(days: index)),
    updatedAt: DateTime.now().subtract(Duration(days: index)),
  ),
);
