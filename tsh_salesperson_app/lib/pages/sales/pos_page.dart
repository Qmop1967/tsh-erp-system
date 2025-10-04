import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';

import '../../config/app_theme.dart';
import '../../providers/pos_provider.dart';
import '../../models/pos_product.dart';
import '../../models/pos_customer.dart';
import '../../models/cart_item.dart';

class POSPage extends StatefulWidget {
  const POSPage({super.key});

  @override
  State<POSPage> createState() => _POSPageState();
}

class _POSPageState extends State<POSPage> {
  final _searchController = TextEditingController();
  final _numberFormat = NumberFormat('#,##0', 'en_US');

  @override
  void initState() {
    super.initState();
    // Initialize demo data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<POSProvider>().initializeDemoData();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      appBar: AppBar(
        title: const Text('نقطة البيع'),
        backgroundColor: AppTheme.primaryGreen,
        elevation: 0,
        actions: [
          // Cart Badge
          Consumer<POSProvider>(
            builder: (context, provider, child) {
              return Stack(
                children: [
                  IconButton(
                    icon: Icon(MdiIcons.cartOutline),
                    onPressed: () => _showCartBottomSheet(context),
                  ),
                  if (provider.cartItemCount > 0)
                    Positioned(
                      right: 8,
                      top: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: AppTheme.goldAccent,
                          shape: BoxShape.circle,
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 20,
                          minHeight: 20,
                        ),
                        child: Text(
                          '${provider.cartItemCount}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                ],
              );
            },
          ),
          IconButton(
            icon: Icon(MdiIcons.history),
            onPressed: () => _showOrderHistory(context),
          ),
        ],
      ),
      body: Column(
        children: [
          // Client Selection Bar
          _buildClientSelectionBar(),
          // Catalog Header with Search
          _buildCatalogHeader(),
          // Category Tabs
          _buildCategoryTabs(),
          // Products Grid
          Expanded(child: _buildProductGrid()),
        ],
      ),
    );
  }

  Widget _buildClientSelectionBar() {
    return Consumer<POSProvider>(
      builder: (context, provider, child) {
        return Container(
          color: Colors.white,
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              const Text(
                'العميل',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textDark,
                ),
              ),
              const SizedBox(height: 8),
              InkWell(
                onTap: () => _showCustomerDialog(context, provider),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  decoration: BoxDecoration(
                    color: AppTheme.backgroundLight,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.borderColor),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Icon(
                        MdiIcons.chevronDown,
                        color: AppTheme.primaryGreen,
                      ),
                      Expanded(
                        child: Text(
                          provider.selectedCustomer?.name ?? 'اختر عميل',
                          style: TextStyle(
                            fontSize: 15,
                            color: provider.selectedCustomer != null
                                ? AppTheme.textDark
                                : AppTheme.textLight,
                            fontWeight: provider.selectedCustomer != null
                                ? FontWeight.w600
                                : FontWeight.normal,
                          ),
                          textAlign: TextAlign.right,
                        ),
                      ),
                      Icon(
                        MdiIcons.accountCircle,
                        color: AppTheme.primaryGreen,
                        size: 28,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCatalogHeader() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          // Search Button
          Expanded(
            child: TextField(
              controller: _searchController,
              textAlign: TextAlign.right,
              decoration: InputDecoration(
                hintText: 'بحث عن منتج...',
                prefixIcon: Icon(MdiIcons.magnify, color: AppTheme.primaryGreen),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: AppTheme.borderColor),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: AppTheme.borderColor),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: AppTheme.primaryGreen, width: 2),
                ),
                filled: true,
                fillColor: AppTheme.backgroundLight,
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
              onChanged: (value) {
                context.read<POSProvider>().setSearchQuery(value);
              },
            ),
          ),
          const SizedBox(width: 12),
          // Catalog Icon
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.primaryGreen,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              MdiIcons.viewGrid,
              color: Colors.white,
              size: 28,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryTabs() {
    return Consumer<POSProvider>(
      builder: (context, provider, child) {
        return Container(
          color: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            reverse: true,
            child: Row(
              children: provider.categories.map((category) {
                final isSelected = provider.selectedCategory == category;
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: InkWell(
                    onTap: () => provider.setSelectedCategory(category),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      decoration: BoxDecoration(
                        color: isSelected ? AppTheme.primaryGreen : Colors.transparent,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: isSelected ? AppTheme.primaryGreen : AppTheme.borderColor,
                          width: 1.5,
                        ),
                      ),
                      child: Text(
                        _getCategoryNameAr(category),
                        style: TextStyle(
                          color: isSelected ? Colors.white : AppTheme.textDark,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        );
      },
    );
  }

  Widget _buildProductGrid() {
    return Consumer<POSProvider>(
      builder: (context, provider, child) {
        final products = provider.products;
        
        if (products.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  MdiIcons.packageVariantClosed,
                  size: 80,
                  color: AppTheme.textLight.withOpacity(0.5),
                ),
                const SizedBox(height: 16),
                const Text(
                  'لا توجد منتجات',
                  style: TextStyle(
                    fontSize: 18,
                    color: AppTheme.textLight,
                  ),
                ),
              ],
            ),
          );
        }

        return GridView.builder(
          padding: const EdgeInsets.all(16),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 0.7,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: products.length,
          itemBuilder: (context, index) {
            return _buildProductCard(products[index], provider);
          },
        );
      },
    );
  }

  Widget _buildProductCard(POSProduct product, POSProvider provider) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Product Image with Add to Cart Button
          Expanded(
            flex: 5,
            child: Stack(
              children: [
                // Product Image/Icon
                Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        AppTheme.primaryGreen.withOpacity(0.1),
                        AppTheme.lightGreen.withOpacity(0.05),
                      ],
                    ),
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(16),
                    ),
                  ),
                  child: Center(
                    child: Icon(
                      _getCategoryIcon(product.category),
                      size: 64,
                      color: AppTheme.primaryGreen.withOpacity(0.7),
                    ),
                  ),
                ),
                // Stock Badge
                Positioned(
                  top: 8,
                  right: 8,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: product.stock > 10
                          ? Colors.green
                          : Colors.orange,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'متوفر ${product.stock}',
                      style: const TextStyle(
                        fontSize: 10,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                // Add to Cart Button
                Positioned(
                  bottom: 8,
                  left: 8,
                  right: 8,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      provider.addToCart(product);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('تمت إضافة ${product.nameAr} إلى السلة'),
                          duration: const Duration(seconds: 1),
                          behavior: SnackBarBehavior.floating,
                          backgroundColor: AppTheme.primaryGreen,
                        ),
                      );
                    },
                    icon: Icon(MdiIcons.cartPlus, size: 18),
                    label: const Text('أضف'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryGreen,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Product Info
          Expanded(
            flex: 3,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Product Name
                  Text(
                    product.nameAr,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                      color: AppTheme.textDark,
                    ),
                    textAlign: TextAlign.right,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  // Product Description
                  if (product.description != null)
                    Text(
                      product.description!,
                      style: TextStyle(
                        fontSize: 11,
                        color: AppTheme.textLight,
                      ),
                      textAlign: TextAlign.right,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  const Spacer(),
                  // Price
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryGreen.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${_numberFormat.format(product.price)} د.ع',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: AppTheme.primaryGreen,
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

  Widget _buildCart() {
    return Consumer<POSProvider>(
      builder: (context, provider, child) {
        return Column(
          children: [
            // Customer Selection
            _buildCustomerSelection(provider),
            const Divider(height: 1),
            // Cart Items
            Expanded(
              child: provider.cart.isEmpty
                  ? _buildEmptyCart()
                  : _buildCartItems(provider),
            ),
            const Divider(height: 1),
            // Cart Summary
            _buildCartSummary(provider),
          ],
        );
      },
    );
  }

  Widget _buildCustomerSelection(POSProvider provider) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          const Text(
            'العميل',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: AppTheme.textDark,
            ),
          ),
          const SizedBox(height: 8),
          InkWell(
            onTap: () => _showCustomerDialog(context, provider),
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.backgroundLight,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppTheme.borderColor),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Expanded(
                    child: Text(
                      provider.selectedCustomer?.name ?? 'اختر عميل',
                      style: TextStyle(
                        fontSize: 13,
                        color: provider.selectedCustomer != null
                            ? AppTheme.textDark
                            : AppTheme.textLight,
                      ),
                      textAlign: TextAlign.right,
                    ),
                  ),
                  Icon(
                    MdiIcons.accountCircle,
                    color: AppTheme.primaryGreen,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyCart() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            MdiIcons.cartOutline,
            size: 80,
            color: AppTheme.textLight.withOpacity(0.5),
          ),
          const SizedBox(height: 16),
          const Text(
            'السلة فارغة',
            style: TextStyle(
              fontSize: 16,
              color: AppTheme.textLight,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCartItems(POSProvider provider) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: provider.cart.length,
      itemBuilder: (context, index) {
        return _buildCartItem(provider.cart[index], provider);
      },
    );
  }

  Widget _buildCartItem(CartItem item, POSProvider provider) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Card(
        elevation: 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: Icon(MdiIcons.delete, size: 20),
                    color: Colors.red,
                    onPressed: () => provider.removeFromCart(item.productId),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                  Expanded(
                    child: Text(
                      item.productNameAr,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                      textAlign: TextAlign.right,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              // Price with Edit Button
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Text(
                    '${_numberFormat.format(item.price)} د.ع',
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppTheme.primaryGreen,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 4),
                  const Text(
                    'السعر:',
                    style: TextStyle(fontSize: 12, color: AppTheme.textLight),
                  ),
                  const SizedBox(width: 8),
                  InkWell(
                    onTap: () => _editPrice(context, item, provider),
                    child: Icon(
                      MdiIcons.pencil,
                      size: 16,
                      color: AppTheme.primaryGreen,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              // Quantity Controls
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${_numberFormat.format(item.total)} د.ع',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textDark,
                    ),
                  ),
                  Row(
                    children: [
                      IconButton(
                        icon: Icon(MdiIcons.minus, size: 18),
                        onPressed: () => provider.updateCartItemQuantity(
                          item.productId,
                          item.quantity - 1,
                        ),
                        padding: const EdgeInsets.all(4),
                        constraints: const BoxConstraints(),
                        style: IconButton.styleFrom(
                          backgroundColor: AppTheme.backgroundLight,
                        ),
                      ),
                      Container(
                        margin: const EdgeInsets.symmetric(horizontal: 12),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryGreen.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '${item.quantity}',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      IconButton(
                        icon: Icon(MdiIcons.plus, size: 18),
                        onPressed: () => provider.updateCartItemQuantity(
                          item.productId,
                          item.quantity + 1,
                        ),
                        padding: const EdgeInsets.all(4),
                        constraints: const BoxConstraints(),
                        style: IconButton.styleFrom(
                          backgroundColor: AppTheme.primaryGreen.withOpacity(0.1),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCartSummary(POSProvider provider) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        children: [
          // Summary Rows
          _buildSummaryRow('المجموع الفرعي:', provider.cartSubtotal),
          const SizedBox(height: 8),
          _buildSummaryRow('الضريبة:', provider.cartTax),
          const Divider(height: 20),
          _buildSummaryRow(
            'الإجمالي:',
            provider.cartTotal,
            isTotal: true,
          ),
          const SizedBox(height: 16),
          // Action Buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: provider.cart.isEmpty
                      ? null
                      : () => provider.clearCart(),
                  icon: Icon(MdiIcons.deleteOutline, size: 18),
                  label: const Text('مسح'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    side: BorderSide(color: Colors.red.shade300),
                    foregroundColor: Colors.red,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                flex: 2,
                child: ElevatedButton.icon(
                  onPressed: provider.cart.isEmpty
                      ? null
                      : () => _checkout(context, provider),
                  icon: Icon(MdiIcons.cashRegister, size: 18),
                  label: const Text('إتمام البيع'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryGreen,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, double amount, {bool isTotal = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          '${_numberFormat.format(amount)} د.ع',
          style: TextStyle(
            fontSize: isTotal ? 18 : 14,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            color: isTotal ? AppTheme.primaryGreen : AppTheme.textDark,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: isTotal ? 16 : 14,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            color: AppTheme.textDark,
          ),
        ),
      ],
    );
  }

  void _showCustomerDialog(BuildContext context, POSProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(
          'اختر عميل',
          textAlign: TextAlign.right,
        ),
        content: SizedBox(
          width: 400,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                title: const Text('بدون عميل', textAlign: TextAlign.right),
                leading: Radio<POSCustomer?>(
                  value: null,
                  groupValue: provider.selectedCustomer,
                  onChanged: (value) {
                    provider.selectCustomer(value);
                    Navigator.pop(context);
                  },
                ),
              ),
              const Divider(),
              ...provider.customers.map((customer) {
                return ListTile(
                  title: Text(customer.name, textAlign: TextAlign.right),
                  subtitle: Text(customer.phone, textAlign: TextAlign.right),
                  leading: Radio<POSCustomer?>(
                    value: customer,
                    groupValue: provider.selectedCustomer,
                    onChanged: (value) {
                      provider.selectCustomer(value);
                      Navigator.pop(context);
                    },
                  ),
                );
              }).toList(),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
        ],
      ),
    );
  }

  void _editPrice(BuildContext context, CartItem item, POSProvider provider) {
    final controller = TextEditingController(text: item.price.toStringAsFixed(0));
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تعديل السعر', textAlign: TextAlign.right),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          textAlign: TextAlign.right,
          decoration: const InputDecoration(
            labelText: 'السعر الجديد',
            suffixText: 'د.ع',
          ),
          inputFormatters: [
            FilteringTextInputFormatter.digitsOnly,
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              final newPrice = double.tryParse(controller.text);
              if (newPrice != null && newPrice > 0) {
                provider.updateCartItemPrice(item.productId, newPrice);
                Navigator.pop(context);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryGreen,
            ),
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }

  void _checkout(BuildContext context, POSProvider provider) async {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('طريقة الدفع', textAlign: TextAlign.right),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: const Text('نقداً', textAlign: TextAlign.right),
              leading: Icon(MdiIcons.cash, color: AppTheme.primaryGreen),
              onTap: () async {
                Navigator.pop(context);
                final success = await provider.checkout(paymentMethod: 'cash');
                if (success && context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('تمت العملية بنجاح'),
                      backgroundColor: Colors.green,
                    ),
                  );
                }
              },
            ),
            ListTile(
              title: const Text('بطاقة', textAlign: TextAlign.right),
              leading: Icon(MdiIcons.creditCard, color: AppTheme.primaryGreen),
              onTap: () async {
                Navigator.pop(context);
                final success = await provider.checkout(paymentMethod: 'card');
                if (success && context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('تمت العملية بنجاح'),
                      backgroundColor: Colors.green,
                    ),
                  );
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showOrderHistory(BuildContext context) {
    final provider = context.read<POSProvider>();
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) {
          return Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryGreen,
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white),
                        onPressed: () => Navigator.pop(context),
                      ),
                      const Text(
                        'سجل الطلبات',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 48),
                    ],
                  ),
                ),
                Expanded(
                  child: provider.orders.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                MdiIcons.receiptTextOutline,
                                size: 80,
                                color: AppTheme.textLight.withOpacity(0.5),
                              ),
                              const SizedBox(height: 16),
                              const Text(
                                'لا توجد طلبات',
                                style: TextStyle(
                                  fontSize: 16,
                                  color: AppTheme.textLight,
                                ),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          controller: scrollController,
                          padding: const EdgeInsets.all(16),
                          itemCount: provider.orders.length,
                          itemBuilder: (context, index) {
                            final order = provider.orders[index];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ExpansionTile(
                                title: Text(
                                  order.id,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                  textAlign: TextAlign.right,
                                ),
                                subtitle: Text(
                                  '${order.customerName ?? "بدون عميل"} - ${DateFormat('yyyy-MM-dd HH:mm').format(order.createdAt)}',
                                  textAlign: TextAlign.right,
                                ),
                                trailing: Text(
                                  '${_numberFormat.format(order.total)} د.ع',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.primaryGreen,
                                  ),
                                ),
                                children: [
                                  const Divider(height: 1),
                                  ...order.items.map((item) {
                                    return ListTile(
                                      title: Text(
                                        item.productNameAr,
                                        textAlign: TextAlign.right,
                                      ),
                                      subtitle: Text(
                                        'الكمية: ${item.quantity} × ${_numberFormat.format(item.price)} د.ع',
                                        textAlign: TextAlign.right,
                                      ),
                                      trailing: Text(
                                        '${_numberFormat.format(item.total)} د.ع',
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    );
                                  }).toList(),
                                ],
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _showCartBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) {
          return Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Consumer<POSProvider>(
              builder: (context, provider, child) {
                return Column(
                  children: [
                    // Header
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryGreen,
                        borderRadius: const BorderRadius.vertical(
                          top: Radius.circular(20),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.close, color: Colors.white),
                            onPressed: () => Navigator.pop(context),
                          ),
                          Column(
                            children: [
                              const Text(
                                'سلة التسوق',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                              Text(
                                '${provider.cartItemCount} عناصر',
                                style: const TextStyle(
                                  fontSize: 14,
                                  color: Colors.white70,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(width: 48),
                        ],
                      ),
                    ),
                    // Cart Items
                    Expanded(
                      child: provider.cart.isEmpty
                          ? _buildEmptyCart()
                          : ListView.builder(
                              controller: scrollController,
                              padding: const EdgeInsets.all(16),
                              itemCount: provider.cart.length,
                              itemBuilder: (context, index) {
                                return _buildCartItem(provider.cart[index], provider);
                              },
                            ),
                    ),
                    // Cart Summary
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 10,
                            offset: const Offset(0, -2),
                          ),
                        ],
                      ),
                      child: Column(
                        children: [
                          _buildSummaryRow('المجموع الفرعي:', provider.cartSubtotal),
                          const SizedBox(height: 8),
                          _buildSummaryRow('الضريبة:', provider.cartTax),
                          const Divider(height: 20),
                          _buildSummaryRow(
                            'الإجمالي:',
                            provider.cartTotal,
                            isTotal: true,
                          ),
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              Expanded(
                                child: OutlinedButton.icon(
                                  onPressed: provider.cart.isEmpty
                                      ? null
                                      : () => provider.clearCart(),
                                  icon: Icon(MdiIcons.deleteOutline, size: 18),
                                  label: const Text('مسح'),
                                  style: OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(vertical: 14),
                                    side: BorderSide(color: Colors.red.shade300),
                                    foregroundColor: Colors.red,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                flex: 2,
                                child: ElevatedButton.icon(
                                  onPressed: provider.cart.isEmpty
                                      ? null
                                      : () {
                                          Navigator.pop(context);
                                          _checkout(context, provider);
                                        },
                                  icon: Icon(MdiIcons.cashRegister, size: 18),
                                  label: const Text('إتمام البيع'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: AppTheme.primaryGreen,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 14),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              },
            ),
          );
        },
      ),
    );
  }

  String _getCategoryNameAr(String category) {
    final map = {
      'All': 'الكل',
      'Smartphones': 'هواتف',
      'Laptops': 'لابتوبات',
      'Tablets': 'تابلت',
      'Accessories': 'إكسسوارات',
    };
    return map[category] ?? category;
  }

  IconData _getCategoryIcon(String category) {
    final map = {
      'Smartphones': MdiIcons.cellphone,
      'Laptops': MdiIcons.laptop,
      'Tablets': MdiIcons.tablet,
      'Accessories': MdiIcons.headphones,
    };
    return map[category] ?? MdiIcons.packageVariant;
  }
}
