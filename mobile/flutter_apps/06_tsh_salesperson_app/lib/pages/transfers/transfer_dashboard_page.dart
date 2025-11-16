import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../services/transfers/transfer_service.dart';
import '../../models/transfers/money_transfer.dart';
import 'create_transfer_page.dart';
import 'transfer_history_page.dart';

/// Transfer Dashboard - Money management overview
/// Critical for tracking $35K USD weekly cash flow
class TransferDashboardPage extends StatefulWidget {
  final int salespersonId;

  const TransferDashboardPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<TransferDashboardPage> createState() => _TransferDashboardPageState();
}

class _TransferDashboardPageState extends State<TransferDashboardPage> {
  final TransferService _transferService = TransferService();
  DailyTransferSummary? _todaysSummary;
  CashBoxBalance? _cashBoxBalance;
  Map<String, dynamic>? _weeklySummary;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    await _transferService.initialize();

    _todaysSummary = await _transferService.getTodaysSummary(widget.salespersonId);
    _cashBoxBalance = await _transferService.getCashBoxBalance(widget.salespersonId);
    _weeklySummary = await _transferService.getWeeklySummary(widget.salespersonId);

    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('إدارة التحويلات المالية'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => TransferHistoryPage(
                    salespersonId: widget.salespersonId,
                  ),
                ),
              );
            },
          ),
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
                    // Cash Box Balance Card
                    _buildCashBoxCard(),
                    const SizedBox(height: 16),

                    // Today's Summary
                    _buildTodaySummary(),
                    const SizedBox(height: 16),

                    // Quick Actions
                    _buildQuickActions(),
                    const SizedBox(height: 16),

                    // Week Chart
                    if (_weeklySummary != null) ...[
                      const Text(
                        'التحويلات الأسبوعية',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildWeekChart(),
                      const SizedBox(height: 16),
                    ],

                    // Transfer Methods Breakdown
                    if (_todaysSummary != null &&
                        _todaysSummary!.totalTransfers > 0) ...[
                      const Text(
                        'التوزيع حسب طريقة التحويل',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildMethodsBreakdown(),
                    ],
                  ],
                ),
              ),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => CreateTransferPage(
                salespersonId: widget.salespersonId,
              ),
            ),
          );

          if (result == true) {
            _loadData();
          }
        },
        icon: const Icon(Icons.add),
        label: const Text('تحويل جديد'),
        backgroundColor: Colors.green,
      ),
    );
  }

  Widget _buildCashBoxCard() {
    if (_cashBoxBalance == null) {
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
            const Row(
              children: [
                Icon(Icons.account_balance_wallet, color: Colors.white, size: 28),
                SizedBox(width: 12),
                Text(
                  'صندوق المال',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Text(
              _cashBoxBalance!.formattedTotal,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            const Divider(color: Colors.white30),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildBalanceItem('نقدي', _cashBoxBalance!.cashIQD, 'IQD'),
                _buildBalanceItem('الطيف', _cashBoxBalance!.altaifIQD, 'IQD'),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildBalanceItem('زين كاش', _cashBoxBalance!.zainCashIQD, 'IQD'),
                _buildBalanceItem('سوبر كيو', _cashBoxBalance!.superQiIQD, 'IQD'),
              ],
            ),
            if (_cashBoxBalance!.cashUSD > 0) ...[
              const SizedBox(height: 12),
              _buildBalanceItem('نقدي USD', _cashBoxBalance!.cashUSD, 'USD'),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildBalanceItem(String label, double amount, String currency) {
    String formattedAmount;
    if (currency == 'USD') {
      formattedAmount = '\$${amount.toStringAsFixed(2)}';
    } else {
      formattedAmount = '${amount.toStringAsFixed(0)} د.ع';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          formattedAmount,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildTodaySummary() {
    if (_todaysSummary == null || _todaysSummary!.totalTransfers == 0) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(Icons.transfer_within_a_station,
                  size: 48, color: Colors.grey.shade400),
              const SizedBox(height: 8),
              const Text('لا توجد تحويلات اليوم'),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () async {
                  final result = await Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => CreateTransferPage(
                        salespersonId: widget.salespersonId,
                      ),
                    ),
                  );

                  if (result == true) {
                    _loadData();
                  }
                },
                icon: const Icon(Icons.add),
                label: const Text('تسجيل تحويل'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'تحويلات اليوم',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStat(
                  icon: Icons.swap_horiz,
                  label: 'التحويلات',
                  value: '${_todaysSummary!.totalTransfers}',
                  color: Colors.blue,
                ),
                _buildStat(
                  icon: Icons.attach_money,
                  label: 'المبلغ',
                  value: _todaysSummary!.formattedTotalAmount,
                  color: Colors.green,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatusStat(
                  'قيد الانتظار',
                  _todaysSummary!.pendingCount,
                  Colors.orange,
                ),
                _buildStatusStat(
                  'تم التحقق',
                  _todaysSummary!.verifiedCount,
                  Colors.blue,
                ),
                _buildStatusStat(
                  'مكتمل',
                  _todaysSummary!.completedCount,
                  Colors.green,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStat({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
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
        Text(
          label,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildStatusStat(String label, int count, Color color) {
    return Column(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              count.toString(),
              style: TextStyle(
                color: color,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () async {
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => CreateTransferPage(
                    salespersonId: widget.salespersonId,
                  ),
                ),
              );

              if (result == true) {
                _loadData();
              }
            },
            icon: const Icon(Icons.add_circle),
            label: const Text('تحويل جديد'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
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
                  builder: (context) => TransferHistoryPage(
                    salespersonId: widget.salespersonId,
                  ),
                ),
              );
            },
            icon: const Icon(Icons.history),
            label: const Text('السجل'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey.shade700,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.all(16),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWeekChart() {
    if (_weeklySummary == null) return const SizedBox();

    final dailySummaries =
        _weeklySummary!['dailySummaries'] as List<DailyTransferSummary>;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'إجمالي الأسبوع: ${(_weeklySummary!['totalAmount'] as double).toStringAsFixed(0)} د.ع',
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
                              .map((s) => s.totalAmount)
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
                          final date =
                              DateTime.parse(dailySummaries[value.toInt()].date);
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
                              toY: entry.value.totalAmount,
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

  Widget _buildMethodsBreakdown() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: _todaysSummary!.amountsByMethod.entries.map((entry) {
            final method = entry.key;
            final amount = entry.value;
            final count = _todaysSummary!.transfersByMethod[method] ?? 0;

            IconData icon;
            Color color;
            String name;

            switch (method) {
              case 'altaif':
                icon = MdiIcons.bankTransfer;
                color = Colors.blue;
                name = 'الطيف';
                break;
              case 'zainCash':
                icon = MdiIcons.cellphone;
                color = Colors.purple;
                name = 'زين كاش';
                break;
              case 'superQi':
                icon = MdiIcons.qrcode;
                color = Colors.orange;
                name = 'سوبر كيو';
                break;
              case 'cash':
                icon = MdiIcons.cash;
                color = Colors.green;
                name = 'نقدي';
                break;
              default:
                icon = MdiIcons.help;
                color = Colors.grey;
                name = method;
            }

            return ListTile(
              leading: CircleAvatar(
                backgroundColor: color.withOpacity(0.2),
                child: Icon(icon, color: color),
              ),
              title: Text(name),
              subtitle: Text('$count تحويل'),
              trailing: Text(
                '${amount.toStringAsFixed(0)} د.ع',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}
