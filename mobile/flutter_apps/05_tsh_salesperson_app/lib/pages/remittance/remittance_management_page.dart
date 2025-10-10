import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';
import '../../config/app_theme.dart';
import '../../widgets/remittance/dashboard_overview_card.dart';
import '../../widgets/remittance/pending_transfers_section.dart';
import '../../widgets/remittance/confirmed_transfers_section.dart';
import '../../widgets/remittance/archived_transfers_section.dart';
import 'create_remittance_page.dart';

class RemittanceManagementPage extends StatefulWidget {
  const RemittanceManagementPage({super.key});

  @override
  State<RemittanceManagementPage> createState() => _RemittanceManagementPageState();
}

class _RemittanceManagementPageState extends State<RemittanceManagementPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int _currentTabIndex = 0;

  // Sample data - replace with actual API data
  final Map<String, dynamic> dashboardStats = {
    'total_this_week': 5,
    'total_amount_confirmed': 45000000.0,
    'pending_count': 2,
    'average_commission': 25000.0,
  };

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _tabController.addListener(() {
      setState(() {
        _currentTabIndex = _tabController.index;
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
      backgroundColor: const Color(0xFFF7F8FA),
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            _buildDashboardOverview(),
            _buildTabBar(),
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: const [
                  PendingTransfersSection(),
                  ConfirmedTransfersSection(),
                  ArchivedTransfersSection(),
                ],
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: _buildFloatingActionButton(),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            const Color(0xFF4FC3F7),
            const Color(0xFF0288D1),
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back, color: Colors.white),
                onPressed: () => Navigator.pop(context),
              ),
              const Spacer(),
              const Text(
                'إدارة الحوالات',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              IconButton(
                icon: Icon(MdiIcons.filterVariant, color: Colors.white),
                onPressed: () {
                  _showFilterDialog();
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardOverview() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: DashboardOverviewCard(stats: dashboardStats),
    );
  }

  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
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
      child: TabBar(
        controller: _tabController,
        indicatorSize: TabBarIndicatorSize.label,
        indicator: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: const LinearGradient(
            colors: [
              Color(0xFF4FC3F7),
              Color(0xFF0288D1),
            ],
          ),
        ),
        labelColor: Colors.white,
        unselectedLabelColor: Colors.grey[600],
        labelStyle: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.bold,
        ),
        unselectedLabelStyle: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.normal,
        ),
        tabs: [
          _buildTab(MdiIcons.clockOutline, 'المعلقة', 2),
          _buildTab(MdiIcons.checkCircle, 'المؤكدة', 0),
          _buildTab(MdiIcons.archive, 'الأرشيف', 0),
        ],
      ),
    );
  }

  Widget _buildTab(IconData icon, String label, int count) {
    return Tab(
      height: 50,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 18),
            const SizedBox(width: 8),
            Text(label),
            if (count > 0) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  count.toString(),
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFloatingActionButton() {
    return FloatingActionButton.extended(
      onPressed: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => const CreateRemittancePage(),
          ),
        );
      },
      backgroundColor: const Color(0xFF4FC3F7),
      elevation: 6,
      icon: const Icon(Icons.add, color: Colors.white),
      label: const Text(
        'حوالة جديدة',
        style: TextStyle(
          color: Colors.white,
          fontSize: 14,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تصفية الحوالات'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(MdiIcons.bankTransfer),
              title: const Text('حسب قناة التحويل'),
              onTap: () {},
            ),
            ListTile(
              leading: Icon(MdiIcons.calendarRange),
              title: const Text('حسب التاريخ'),
              onTap: () {},
            ),
            ListTile(
              leading: Icon(MdiIcons.currencyUsd),
              title: const Text('حسب المبلغ'),
              onTap: () {},
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('تطبيق'),
          ),
        ],
      ),
    );
  }
}
