import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';

import '../../config/app_theme.dart';
import 'main_dashboard_page.dart';
import 'leaderboard_dashboard_page.dart';

class DashboardContainerPage extends StatefulWidget {
  const DashboardContainerPage({super.key});

  @override
  State<DashboardContainerPage> createState() => _DashboardContainerPageState();
}

class _DashboardContainerPageState extends State<DashboardContainerPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() {
      setState(() {
        _currentIndex = _tabController.index;
      });
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundLight,
      body: Column(
        children: [
          // Custom Tab Bar
          _buildCustomTabBar(),
          
          // Tab Views
          Expanded(
            child: TabBarView(
              controller: _tabController,
              physics: const BouncingScrollPhysics(),
              children: const [
                MainDashboardPage(),
                LeaderboardDashboardPage(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCustomTabBar() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.only(top: 50),
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(15),
        ),
        child: TabBar(
          controller: _tabController,
          indicator: BoxDecoration(
            gradient: _currentIndex == 0
                ? AppTheme.primaryGradient
                : AppTheme.goldGradient,
            borderRadius: BorderRadius.circular(12),
          ),
          indicatorSize: TabBarIndicatorSize.tab,
          dividerColor: Colors.transparent,
          labelColor: Colors.white,
          unselectedLabelColor: AppTheme.textLight,
          labelStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
          unselectedLabelStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
          tabs: [
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    MdiIcons.viewDashboard,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  const Text('لوحتي'),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    MdiIcons.trophy,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  const Text('المتصدرين'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
