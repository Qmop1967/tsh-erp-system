import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../services/commission/commission_service.dart';
import '../../models/commission/commission.dart';
import 'commission_history_page.dart';
import 'leaderboard_page.dart';
import 'sales_target_page.dart';

/// Commission Dashboard - Earnings overview and analytics
/// Critical for tracking 2.25% commission on sales
class CommissionDashboardPage extends StatefulWidget {
  final int salespersonId;

  const CommissionDashboardPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<CommissionDashboardPage> createState() => _CommissionDashboardPageState();
}

class _CommissionDashboardPageState extends State<CommissionDashboardPage> with SingleTickerProviderStateMixin {
  final CommissionService _commissionService = CommissionService();
  CommissionSummary? _currentSummary;
  SalesTarget? _currentTarget;
  Map<String, dynamic>? _weeklyData;
  bool _isLoading = true;
  late TabController _tabController;
  String _selectedPeriod = 'month';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    await _commissionService.initialize();

    _currentSummary = await _commissionService.getCommissionSummary(
      widget.salespersonId,
      period: _selectedPeriod,
    );
    _currentTarget = await _commissionService.getCurrentTarget(widget.salespersonId);
    _weeklyData = await _commissionService.getWeeklyData(widget.salespersonId);

    setState(() => _isLoading = false);
  }

  void _changePeriod(String period) {
    setState(() {
      _selectedPeriod = period;
    });
    _loadData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('عمولاتي'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: 'اليوم'),
            Tab(text: 'الأسبوع'),
            Tab(text: 'الشهر'),
            Tab(text: 'الكل'),
          ],
          onTap: (index) {
            switch (index) {
              case 0:
                _changePeriod('today');
                break;
              case 1:
                _changePeriod('week');
                break;
              case 2:
                _changePeriod('month');
                break;
              case 3:
                _changePeriod('all-time');
                break;
            }
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Commission Summary Card
                    _buildCommissionSummaryCard(),
                    const SizedBox(height: 16),

                    // Quick Stats
                    _buildQuickStats(),
                    const SizedBox(height: 16),

                    // Sales Target Card
                    if (_currentTarget != null) ...[
                      _buildSalesTargetCard(),
                      const SizedBox(height: 16),
                    ],

                    // Weekly Earnings Chart
                    if (_weeklyData != null) ...[
                      const Text(
                        'أرباح الأسبوع',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildWeeklyChart(),
                      const SizedBox(height: 16),
                    ],

                    // Quick Actions
                    _buildQuickActions(),
                    const SizedBox(height: 16),

                    // Commission Calculator
                    _buildCommissionCalculator(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildCommissionSummaryCard() {
    if (_currentSummary == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: Text('لا توجد بيانات')),
        ),
      );
    }

    return Card(
      elevation: 4,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [Colors.green.shade600, Colors.green.shade800],
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.attach_money, color: Colors.white, size: 28),
                const SizedBox(width: 12),
                Text(
                  _currentSummary!.periodName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Text(
              _currentSummary!.formattedTotalCommission,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'العمولة الإجمالية',
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 16),
            const Divider(color: Colors.white30),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildSummaryItem('قيد الانتظار', _currentSummary!.formattedPendingCommission),
                _buildSummaryItem('مدفوع', _currentSummary!.formattedPaidCommission),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'إجمالي المبيعات',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 14,
                    ),
                  ),
                  Text(
                    _currentSummary!.formattedTotalSales,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.8),
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickStats() {
    if (_currentSummary == null) return const SizedBox();

    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            icon: Icons.shopping_cart,
            label: 'الطلبات',
            value: '${_currentSummary!.ordersCount}',
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            icon: Icons.percent,
            label: 'نسبة العمولة',
            value: '${_currentSummary!.commissionRate}%',
            color: Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                color: color,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSalesTargetCard() {
    if (_currentTarget == null) return const SizedBox();

    final progress = _currentTarget!.progressPercentage;
    final isAchieved = _currentTarget!.isAchieved;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      isAchieved ? Icons.check_circle : Icons.flag,
                      color: isAchieved ? Colors.green : Colors.orange,
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'الهدف الشهري',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                TextButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => SalesTargetPage(
                          salespersonId: widget.salespersonId,
                        ),
                      ),
                    );
                  },
                  child: const Text('عرض التفاصيل'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress / 100,
                minHeight: 12,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation<Color>(
                  isAchieved ? Colors.green : Colors.orange,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'المحقق',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    Text(
                      _currentTarget!.formattedCurrentAmount,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text(
                      'الهدف',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    Text(
                      _currentTarget!.formattedTargetAmount,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '${progress.toStringAsFixed(1)}% مكتمل',
              style: TextStyle(
                color: isAchieved ? Colors.green : Colors.orange,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeeklyChart() {
    if (_weeklyData == null) return const SizedBox();

    final dailySummaries = _weeklyData!['dailySummaries'] as List<DailyCommissionSummary>;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'إجمالي: ${(_weeklyData!['weeklyCommission'] as double).toStringAsFixed(0)} د.ع',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: dailySummaries.isEmpty
                      ? 10
                      : dailySummaries
                              .map((s) => s.totalCommission)
                              .reduce((a, b) => a > b ? a : b) *
                          1.2,
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          if (value.toInt() >= dailySummaries.length) {
                            return const Text('');
                          }
                          final date = DateTime.parse(dailySummaries[value.toInt()].date);
                          return Text(
                            DateFormat('EEE', 'ar').format(date),
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true, reservedSize: 40),
                    ),
                    topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  barGroups: dailySummaries
                      .asMap()
                      .entries
                      .map(
                        (entry) => BarChartGroupData(
                          x: entry.key,
                          barRods: [
                            BarChartRodData(
                              toY: entry.value.totalCommission,
                              color: Colors.green,
                              width: 20,
                              borderRadius: const BorderRadius.vertical(
                                top: Radius.circular(6),
                              ),
                            ),
                          ],
                        ),
                      )
                      .toList(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'إجراءات سريعة',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => CommissionHistoryPage(
                        salespersonId: widget.salespersonId,
                      ),
                    ),
                  );
                },
                icon: const Icon(Icons.history),
                label: const Text('السجل'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.all(16),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const LeaderboardPage(),
                    ),
                  );
                },
                icon: const Icon(Icons.leaderboard),
                label: const Text('الترتيب'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.all(16),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCommissionCalculator() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.calculate, color: Colors.green),
                SizedBox(width: 8),
                Text(
                  'حاسبة العمولة السريعة',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('نسبة العمولة:'),
                      Text(
                        '${_commissionService.commissionRate}%',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Divider(),
                  const SizedBox(height: 12),
                  _buildCalculatorExample('1,000,000 د.ع', '22,500 د.ع'),
                  const SizedBox(height: 8),
                  _buildCalculatorExample('5,000,000 د.ع', '112,500 د.ع'),
                  const SizedBox(height: 8),
                  _buildCalculatorExample('10,000,000 د.ع', '225,000 د.ع'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCalculatorExample(String sales, String commission) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'مبيعات: $sales',
          style: const TextStyle(fontSize: 14),
        ),
        const Icon(Icons.arrow_forward, size: 16),
        Text(
          'عمولة: $commission',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
      ],
    );
  }
}
