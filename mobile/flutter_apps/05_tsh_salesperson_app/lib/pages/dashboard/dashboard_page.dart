import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:shimmer/shimmer.dart';
import 'package:intl/intl.dart';

import '../../config/app_theme.dart';
import '../../config/app_config.dart';
import '../../providers/dashboard_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/tsh_card.dart';
import '../../widgets/common/tsh_loading_indicator.dart';
import '../../widgets/dashboard/receivables_card.dart';
import '../../widgets/dashboard/commission_card.dart';
import '../../widgets/dashboard/cash_box_card.dart';
import '../../widgets/dashboard/quick_stats_card.dart';
import '../../widgets/dashboard/settlement_button.dart';
import '../../widgets/dashboard/regional_breakdown_card.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage>
    with TickerProviderStateMixin {
  late AnimationController _refreshController;
  late Animation<double> _refreshAnimation;
  final RefreshIndicator refreshIndicator = const RefreshIndicator(
    onRefresh: null,
    child: SizedBox(),
  );

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _loadDashboardData();
  }

  void _initializeAnimations() {
    _refreshController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _refreshAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _refreshController,
      curve: Curves.easeInOut,
    ));
  }

  Future<void> _loadDashboardData() async {
    final dashboardProvider = context.read<DashboardProvider>();
    await dashboardProvider.loadDashboardData();
  }

  Future<void> _refreshDashboard() async {
    _refreshController.forward();
    try {
      await _loadDashboardData();
    } finally {
      _refreshController.reverse();
    }
  }

  @override
  void dispose() {
    _refreshController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      body: Consumer2<DashboardProvider, AuthProvider>(
        builder: (context, dashboardProvider, authProvider, child) {
          return RefreshIndicator(
            onRefresh: _refreshDashboard,
            color: AppTheme.primaryGreen,
            backgroundColor: Colors.white,
            child: CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                _buildAppBar(authProvider),
                if (dashboardProvider.isLoading)
                  _buildLoadingSliver()
                else if (dashboardProvider.hasError)
                  _buildErrorSliver(dashboardProvider.error)
                else
                  _buildDashboardContent(dashboardProvider),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildAppBar(AuthProvider authProvider) {
    return SliverAppBar(
      expandedHeight: 140,
      floating: false,
      pinned: true,
      elevation: 0,
      backgroundColor: AppTheme.primaryGreen,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: AppTheme.primaryGradient,
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 50, 20, 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 24,
                        backgroundColor: Colors.white.withOpacity(0.2),
                        child: Text(
                          authProvider.user?.initials ?? '؟',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'أهلاً وسهلاً',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.9),
                                fontSize: 14,
                                fontFamily: 'Cairo',
                              ),
                            ),
                            Text(
                              authProvider.user?.displayName ?? 'مندوب المبيعات',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                fontFamily: 'Cairo',
                              ),
                            ),
                          ],
                        ),
                      ),
                      AnimatedBuilder(
                        animation: _refreshAnimation,
                        builder: (context, child) {
                          return Transform.rotate(
                            angle: _refreshAnimation.value * 2 * 3.14159,
                            child: IconButton(
                              onPressed: _refreshDashboard,
                              icon: const Icon(
                                Icons.refresh,
                                color: Colors.white,
                                size: 24,
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingSliver() {
    return SliverPadding(
      padding: const EdgeInsets.all(16),
      sliver: SliverGrid(
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 1.2,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
        ),
        delegate: SliverChildBuilderDelegate(
          (context, index) => _buildShimmerCard(),
          childCount: 6,
        ),
      ),
    );
  }

  Widget _buildShimmerCard() {
    return Shimmer.fromColors(
      baseColor: Colors.grey.shade300,
      highlightColor: Colors.grey.shade100,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: AppTheme.largeRadius,
          boxShadow: AppTheme.cardShadow,
        ),
      ),
    );
  }

  Widget _buildErrorSliver(String? error) {
    return SliverFillRemaining(
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              MdiIcons.alertCircleOutline,
              size: 64,
              color: AppTheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'خطأ في تحميل البيانات',
              style: AppTheme.heading3.copyWith(
                color: AppTheme.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error ?? 'حدث خطأ غير متوقع',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.textLight,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _refreshDashboard,
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardContent(DashboardProvider provider) {
    return SliverPadding(
      padding: const EdgeInsets.all(16),
      sliver: SliverList(
        delegate: SliverChildListDelegate([
          // Quick Stats Row
          _buildQuickStatsRow(provider),
          const SizedBox(height: 24),
          
          // Main Dashboard Cards
          AnimationLimiter(
            child: Column(
              children: AnimationConfiguration.toStaggeredList(
                duration: const Duration(milliseconds: 375),
                childAnimationBuilder: (widget) => SlideAnimation(
                  horizontalOffset: 50.0,
                  child: FadeInAnimation(child: widget),
                ),
                children: [
                  // Receivables Card
                  ReceivablesCard(
                    data: provider.receivablesData,
                    onTap: () => _showReceivablesDetails(provider),
                  ),
                  const SizedBox(height: 16),
                  
                  // Commission Card
                  CommissionCard(
                    data: provider.commissionData,
                    onTap: () => _showCommissionDetails(provider),
                  ),
                  const SizedBox(height: 16),
                  
                  // Cash Box Card
                  CashBoxCard(
                    data: provider.cashBoxData,
                    onSettlement: () => _showSettlementDialog(provider),
                  ),
                  const SizedBox(height: 16),
                  
                  // Regional Breakdown
                  if (provider.regionalData.isNotEmpty)
                    RegionalBreakdownCard(
                      data: provider.regionalData,
                      onRegionTap: (region) => _showRegionDetails(region),
                    ),
                  
                  const SizedBox(height: 100), // Space for bottom navigation
                ],
              ),
            ),
          ),
        ]),
      ),
    );
  }

  Widget _buildQuickStatsRow(DashboardProvider provider) {
    return Row(
      children: [
        Expanded(
          child: QuickStatsCard(
            title: 'إجمالي المستحقات',
            value: NumberFormat.currency(
              locale: 'ar_IQ',
              symbol: 'د.ع',
              decimalDigits: 0,
            ).format(provider.totalReceivables),
            icon: MdiIcons.cashMultiple,
            color: AppTheme.info,
            trend: provider.receivablesTrend,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: QuickStatsCard(
            title: 'العمولة المكتسبة',
            value: NumberFormat.currency(
              locale: 'ar_IQ',
              symbol: 'د.ع',
              decimalDigits: 0,
            ).format(provider.totalCommission),
            icon: MdiIcons.percentOutline,
            color: AppTheme.success,
            trend: provider.commissionTrend,
          ),
        ),
      ],
    );
  }

  void _showReceivablesDetails(DashboardProvider provider) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(24),
          ),
        ),
        child: Column(
          children: [
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(top: 12),
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Text(
                'تفاصيل المستحقات',
                style: AppTheme.heading2,
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                itemCount: provider.receivablesData.length,
                itemBuilder: (context, index) {
                  final item = provider.receivablesData[index];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: AppTheme.primaryGreen.withOpacity(0.1),
                        child: Icon(
                          MdiIcons.mapMarkerOutline,
                          color: AppTheme.primaryGreen,
                        ),
                      ),
                      title: Text(item['region'] ?? ''),
                      subtitle: Text('${item['customerCount']} عميل'),
                      trailing: Text(
                        NumberFormat.currency(
                          locale: 'ar_IQ',
                          symbol: 'د.ع',
                          decimalDigits: 0,
                        ).format(item['amount']),
                        style: AppTheme.bodyMedium.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primaryGreen,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showCommissionDetails(DashboardProvider provider) {
    // Implementation for commission details
  }

  void _showSettlementDialog(DashboardProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: AppTheme.largeRadius,
        ),
        title: Row(
          children: [
            Icon(
              MdiIcons.bankTransferOut,
              color: AppTheme.primaryGreen,
            ),
            const SizedBox(width: 12),
            const Text('تسوية شاملة'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'هل تريد إجراء تسوية شاملة للمبالغ المستحصلة؟',
              style: AppTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryGreen.withOpacity(0.1),
                borderRadius: AppTheme.mediumRadius,
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('المبلغ النقدي:'),
                      Text(
                        NumberFormat.currency(
                          locale: 'ar_IQ',
                          symbol: 'د.ع',
                          decimalDigits: 0,
                        ).format(provider.cashBoxData['total']['IQD']),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('المبلغ الرقمي:'),
                      Text(
                        NumberFormat.currency(
                          locale: 'ar_IQ',
                          symbol: 'د.ع',
                          decimalDigits: 0,
                        ).format(provider.cashBoxData['digital']['IQD'] ?? 0),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              _initiateSettlement(provider);
            },
            child: const Text('تأكيد التسوية'),
          ),
        ],
      ),
    );
  }

  void _showRegionDetails(Map<String, dynamic> region) {
    // Implementation for region details
  }

  void _initiateSettlement(DashboardProvider provider) {
    // Implementation for settlement process
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم بدء عملية التسوية'),
        backgroundColor: AppTheme.success,
      ),
    );
  }
} 