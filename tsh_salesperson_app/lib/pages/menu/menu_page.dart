import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:provider/provider.dart';

import '../../config/app_theme.dart';
import '../../providers/auth_provider.dart';

class MenuPage extends StatelessWidget {
  const MenuPage({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      body: CustomScrollView(
        slivers: [
          // App Bar
          SliverAppBar(
            expandedHeight: 180,
            floating: false,
            pinned: true,
            backgroundColor: AppTheme.primaryGreen,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 30,
                              backgroundColor: Colors.white,
                              child: Icon(
                                MdiIcons.account,
                                size: 35,
                                color: AppTheme.primaryGreen,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    authProvider.user?.name ?? 'مندوب المبيعات',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    authProvider.user?.email ?? '',
                                    style: const TextStyle(
                                      color: Colors.white70,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              title: const Text('القائمة'),
            ),
          ),

          // Menu Items
          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _buildMenuSection(
                  title: 'إدارة المبيعات',
                  items: [
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.accountGroup,
                      title: 'إدارة العملاء',
                      subtitle: 'عرض وإدارة قائمة العملاء',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.packageVariant,
                      title: 'المنتجات',
                      subtitle: 'تصفح كتالوج المنتجات',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.clipboardText,
                      title: 'الطلبات',
                      subtitle: 'إنشاء وإدارة الطلبات',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.receiptText,
                      title: 'الفواتير',
                      subtitle: 'عرض جميع الفواتير',
                      onTap: () {},
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildMenuSection(
                  title: 'المالية',
                  items: [
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.currencyUsd,
                      title: 'المدفوعات',
                      subtitle: 'تسجيل وعرض المدفوعات',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.cashClock,
                      title: 'المستحقات',
                      subtitle: 'متابعة المستحقات',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.walletOutline,
                      title: 'عمولاتي',
                      subtitle: 'عرض العمولات والأرباح',
                      onTap: () {},
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildMenuSection(
                  title: 'التقارير',
                  items: [
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.chartBar,
                      title: 'تقارير المبيعات',
                      subtitle: 'تحليل أداء المبيعات',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.chartPie,
                      title: 'التقارير المالية',
                      subtitle: 'ملخص المالية',
                      onTap: () {},
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildMenuSection(
                  title: 'الإعدادات',
                  items: [
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.accountCircle,
                      title: 'الملف الشخصي',
                      subtitle: 'إدارة معلومات الحساب',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.cog,
                      title: 'الإعدادات',
                      subtitle: 'تخصيص التطبيق',
                      onTap: () {},
                    ),
                    _buildMenuItem(
                      context,
                      icon: MdiIcons.help,
                      title: 'المساعدة والدعم',
                      subtitle: 'احصل على المساعدة',
                      onTap: () {},
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildLogoutButton(context),
                const SizedBox(height: 100),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuSection({
    required String title,
    required List<Widget> items,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
          child: Text(
            title,
            style: const TextStyle(
              color: AppTheme.textLight,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(15),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(children: items),
        ),
      ],
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      onTap: onTap,
      leading: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: AppTheme.primaryGreen.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          icon,
          color: AppTheme.primaryGreen,
          size: 24,
        ),
      ),
      title: Text(
        title,
        style: const TextStyle(
          color: AppTheme.textDark,
          fontSize: 15,
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: const TextStyle(
          color: AppTheme.textLight,
          fontSize: 13,
        ),
      ),
      trailing: Icon(
        MdiIcons.chevronLeft,
        color: AppTheme.textLight,
      ),
    );
  }

  Widget _buildLogoutButton(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListTile(
        onTap: () {
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              title: const Text('تسجيل الخروج'),
              content: const Text('هل أنت متأكد من تسجيل الخروج؟'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('إلغاء'),
                ),
                TextButton(
                  onPressed: () {
                    context.read<AuthProvider>().logout();
                    Navigator.pop(context);
                  },
                  child: const Text(
                    'تسجيل الخروج',
                    style: TextStyle(color: AppTheme.error),
                  ),
                ),
              ],
            ),
          );
        },
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppTheme.error.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            MdiIcons.logout,
            color: AppTheme.error,
            size: 24,
          ),
        ),
        title: const Text(
          'تسجيل الخروج',
          style: TextStyle(
            color: AppTheme.error,
            fontSize: 15,
            fontWeight: FontWeight.w600,
          ),
        ),
        trailing: Icon(
          MdiIcons.chevronLeft,
          color: AppTheme.error,
        ),
      ),
    );
  }
}
