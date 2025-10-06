import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:shimmer/shimmer.dart';

import '../../../config/app_theme.dart';

class QuickActionsCard extends StatelessWidget {
  final bool isLoading;

  const QuickActionsCard({
    super.key,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return _buildShimmer();
    }

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppTheme.goldAccent.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  MdiIcons.flash,
                  color: AppTheme.goldAccent,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'إجراءات سريعة',
                style: TextStyle(
                  color: AppTheme.textDark,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 3,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1,
            children: [
              _buildQuickActionItem(
                context,
                icon: MdiIcons.accountPlus,
                label: 'عميل جديد',
                color: AppTheme.primaryGreen,
                onTap: () => _navigateTo(context, '/customers/new'),
              ),
              _buildQuickActionItem(
                context,
                icon: MdiIcons.cartPlus,
                label: 'طلب جديد',
                color: AppTheme.info,
                onTap: () => _navigateTo(context, '/orders/new'),
              ),
              _buildQuickActionItem(
                context,
                icon: MdiIcons.cashRegister,
                label: 'فاتورة',
                color: AppTheme.warning,
                onTap: () => _navigateTo(context, '/pos'),
              ),
              _buildQuickActionItem(
                context,
                icon: MdiIcons.currencyUsd,
                label: 'تحصيل',
                color: AppTheme.success,
                onTap: () => _showCollectionDialog(context),
              ),
              _buildQuickActionItem(
                context,
                icon: MdiIcons.clipboardText,
                label: 'التقارير',
                color: AppTheme.error,
                onTap: () => _navigateTo(context, '/reports'),
              ),
              _buildQuickActionItem(
                context,
                icon: MdiIcons.accountSearch,
                label: 'بحث',
                color: AppTheme.textDark,
                onTap: () => _showSearchDialog(context),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(15),
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: color,
              size: 32,
            ),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateTo(BuildContext context, String route) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('قريباً'),
        content: Text('سيتم تفعيل $route قريباً'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
  }

  void _showCollectionDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('تحصيل مدفوعات'),
        content: const Text('سيتم تطوير هذه الميزة قريباً'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
  }

  void _showSearchDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('بحث'),
        content: const Text('سيتم تطوير هذه الميزة قريباً'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
  }

  Widget _buildShimmer() {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: Container(
        height: 220,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }
}
