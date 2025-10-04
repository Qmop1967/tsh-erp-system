import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';

import '../../config/app_theme.dart';
import '../../providers/dashboard_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/dashboard/leaderboard/salesperson_level_card.dart';
import '../../widgets/dashboard/leaderboard/sales_comparison_chart.dart';
import '../../widgets/dashboard/leaderboard/collection_comparison_chart.dart';
import '../../widgets/dashboard/leaderboard/activity_comparison_card.dart';
import '../../widgets/dashboard/leaderboard/challenges_card.dart';
import '../../widgets/dashboard/leaderboard/top_performers_list.dart';

class LeaderboardDashboardPage extends StatefulWidget {
  const LeaderboardDashboardPage({super.key});

  @override
  State<LeaderboardDashboardPage> createState() => _LeaderboardDashboardPageState();
}

class _LeaderboardDashboardPageState extends State<LeaderboardDashboardPage> {
  bool _isLoading = false;
  String _selectedPeriod = 'month'; // week, month, quarter, year

  @override
  void initState() {
    super.initState();
    _loadLeaderboardData();
  }

  Future<void> _loadLeaderboardData() async {
    setState(() => _isLoading = true);
    try {
      await context.read<DashboardProvider>().fetchLeaderboardData(_selectedPeriod);
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
      onRefresh: _loadLeaderboardData,
      color: AppTheme.goldAccent,
      child: CustomScrollView(
        physics: const BouncingScrollPhysics(
          parent: AlwaysScrollableScrollPhysics(),
        ),
        slivers: [
          // Leaderboard Header
          SliverToBoxAdapter(
            child: _buildLeaderboardHeader(authProvider),
          ),

          // Period Filter
          SliverToBoxAdapter(
            child: _buildPeriodFilter(),
          ),

          // Main Content
          SliverPadding(
            padding: const EdgeInsets.all(16.0),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Salesperson Level Card
                AnimationConfiguration.staggeredList(
                  position: 0,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: SalespersonLevelCard(
                        leaderboardData: dashboardProvider.leaderboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Challenges Card
                AnimationConfiguration.staggeredList(
                  position: 1,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: ChallengesCard(
                        leaderboardData: dashboardProvider.leaderboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Sales Comparison Chart
                AnimationConfiguration.staggeredList(
                  position: 2,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: SalesComparisonChart(
                        leaderboardData: dashboardProvider.leaderboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Collection Comparison Chart
                AnimationConfiguration.staggeredList(
                  position: 3,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: CollectionComparisonChart(
                        leaderboardData: dashboardProvider.leaderboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Activity Comparison
                AnimationConfiguration.staggeredList(
                  position: 4,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: ActivityComparisonCard(
                        leaderboardData: dashboardProvider.leaderboardData,
                        isLoading: _isLoading,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Top Performers List
                AnimationConfiguration.staggeredList(
                  position: 5,
                  duration: const Duration(milliseconds: 375),
                  child: SlideAnimation(
                    verticalOffset: 50.0,
                    child: FadeInAnimation(
                      child: TopPerformersList(
                        leaderboardData: dashboardProvider.leaderboardData,
                        isLoading: _isLoading,
                      ),
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

  Widget _buildLeaderboardHeader(AuthProvider authProvider) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.goldAccent,
            AppTheme.lightGold,
          ],
        ),
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
                  const Text(
                    'لوحة المتصدرين',
                    style: TextStyle(
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
                  MdiIcons.trophy,
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
              children: [
                Icon(
                  MdiIcons.chartLine,
                  color: Colors.white,
                  size: 18,
                ),
                const SizedBox(width: 8),
                const Text(
                  'قارن أدائك مع زملائك وحقق التحديات',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodFilter() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          _buildPeriodButton('أسبوع', 'week'),
          _buildPeriodButton('شهر', 'month'),
          _buildPeriodButton('ربع', 'quarter'),
          _buildPeriodButton('سنة', 'year'),
        ],
      ),
    );
  }

  Widget _buildPeriodButton(String label, String value) {
    final isSelected = _selectedPeriod == value;
    
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() => _selectedPeriod = value);
          _loadLeaderboardData();
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.goldAccent : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected ? Colors.white : AppTheme.textLight,
              fontSize: 14,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            ),
          ),
        ),
      ),
    );
  }
}
