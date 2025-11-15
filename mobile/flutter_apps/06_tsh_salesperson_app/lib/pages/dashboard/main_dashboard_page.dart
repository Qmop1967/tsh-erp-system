import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';

import '../../config/app_theme.dart';
import '../../providers/dashboard_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/dashboard/main_dashboard/commission_summary_card.dart';
import '../../widgets/dashboard/main_dashboard/receivables_summary_card.dart';
import '../../widgets/dashboard/main_dashboard/cash_box_actions_card.dart';
import '../../widgets/dashboard/main_dashboard/digital_payments_card.dart';
import '../../widgets/dashboard/main_dashboard/sales_hotReport_card.dart';
import '../../widgets/dashboard/main_dashboard/quick_actions_card.dart';

class MainDashboardPage extends StatefulWidget {
  const MainDashboardPage({super.key});

  @override
  State<MainDashboardPage> createState() => _MainDashboardPageState();
}

class _MainDashboardPageState extends State<MainDashboardPage> {
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Schedule the data load after the first frame to avoid setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadDashboardData();
    });
  }

  Future<void> _loadDashboardData() async {
    if (!mounted) return;
    setState(() => _isLoading = true);
    try {
      await context.read<DashboardProvider>().fetchDashboardData();
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final dashboardProvider = context.watch<DashboardProvider>();

    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      color: AppTheme.primaryGreen,
      child: CustomScrollView(
        physics: const BouncingScrollPhysics(
          parent: AlwaysScrollableScrollPhysics(),
        ),
        slivers: [
          // Welcome Header
          SliverToBoxAdapter(
            child: _buildWelcomeHeader(authProvider),
          ),

          // Main Content
          SliverPadding(
            padding: const EdgeInsets.all(16.0),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Commission Card
                AnimationConfiguration.staggeredList(
                  position: 0,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: CommissionSummaryCard(
                        dashboardData: dashboardProvider.dashboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Receivables Card
                AnimationConfiguration.staggeredList(
                  position: 1,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: ReceivablesSummaryCard(
                        dashboardData: dashboardProvider.dashboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Cash Box & Digital Payments Row
                AnimationConfiguration.staggeredList(
                  position: 2,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: Row(
                        children: [
                          Expanded(
                            child: CashBoxActionsCard(
                              dashboardData: dashboardProvider.dashboardData,
                              isLoading: _isLoading,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: DigitalPaymentsCard(
                              dashboardData: dashboardProvider.dashboardData,
                              isLoading: _isLoading,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Sales Hot Report
                AnimationConfiguration.staggeredList(
                  position: 3,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: SalesHotReportCard(
                        dashboardData: dashboardProvider.dashboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Quick Actions
                AnimationConfiguration.staggeredList(
                  position: 4,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: QuickActionsCard(isLoading: _isLoading),
                    ),
                  ),
                ),
                const SizedBox(height: 100), // Bottom padding for nav bar
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWelcomeHeader(AuthProvider authProvider) {
    final now = DateTime.now();
    final hour = now.hour;
    String greeting;
    
    if (hour < 12) {
      greeting = 'صباح الخير';
    } else if (hour < 18) {
      greeting = 'مساء الخير';
    } else {
      greeting = 'مساء الخير';
    }

    return Container(
      decoration: BoxDecoration(
        gradient: AppTheme.primaryGradient,
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(30),
          bottomRight: Radius.circular(30),
        ),
      ),
      padding: const EdgeInsets.fromLTRB(20, 60, 20, 30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    greeting,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    authProvider.user?.name ?? 'مندوب المبيعات',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Icon(
                  MdiIcons.accountTie,
                  color: Colors.white,
                  size: 32,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  DateFormat('EEEE, d MMMM yyyy', 'ar').format(now),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Icon(
                  MdiIcons.calendarToday,
                  color: Colors.white.withOpacity(0.8),
                  size: 18,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
