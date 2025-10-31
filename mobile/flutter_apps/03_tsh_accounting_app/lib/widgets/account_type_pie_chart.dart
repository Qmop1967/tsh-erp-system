import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/dashboard_stats.dart';
import '../models/account_type.dart';
import '../config/app_config.dart';

/// Account Type Distribution Pie Chart
/// رسم بياني دائري لتوزيع أنواع الحسابات

class AccountTypePieChart extends StatefulWidget {
  final DashboardStats stats;

  const AccountTypePieChart({Key? key, required this.stats}) : super(key: key);

  @override
  State<AccountTypePieChart> createState() => _AccountTypePieChartState();
}

class _AccountTypePieChartState extends State<AccountTypePieChart> {
  int touchedIndex = -1;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.pie_chart,
                    color: Color(AppConfig.primaryColorValue)),
                const SizedBox(width: 8),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text(
                      'توزيع الحسابات',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Account Distribution',
                      style: TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 20),
            AspectRatio(
              aspectRatio: 1.3,
              child: PieChart(
                PieChartData(
                  pieTouchData: PieTouchData(
                    touchCallback: (FlTouchEvent event, pieTouchResponse) {
                      setState(() {
                        if (!event.isInterestedForInteractions ||
                            pieTouchResponse == null ||
                            pieTouchResponse.touchedSection == null) {
                          touchedIndex = -1;
                          return;
                        }
                        touchedIndex = pieTouchResponse
                            .touchedSection!.touchedSectionIndex;
                      });
                    },
                  ),
                  borderData: FlBorderData(show: false),
                  sectionsSpace: 2,
                  centerSpaceRadius: 40,
                  sections: _generateSections(),
                ),
              ),
            ),
            const SizedBox(height: 20),
            _buildLegend(),
          ],
        ),
      ),
    );
  }

  List<PieChartSectionData> _generateSections() {
    final total = widget.stats.totalAssets +
        widget.stats.totalLiabilities +
        widget.stats.totalEquity +
        widget.stats.totalRevenue +
        widget.stats.totalExpenses;

    if (total == 0) {
      return [
        PieChartSectionData(
          color: Colors.grey,
          value: 100,
          title: 'لا توجد بيانات',
          radius: 60,
        ),
      ];
    }

    return [
      // Assets
      PieChartSectionData(
        color: Color(AppConfig.assetColorValue),
        value: widget.stats.totalAssets,
        title: touchedIndex == 0
            ? '${((widget.stats.totalAssets / total) * 100).toStringAsFixed(1)}%'
            : '',
        radius: touchedIndex == 0 ? 70 : 60,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      // Liabilities
      PieChartSectionData(
        color: Color(AppConfig.liabilityColorValue),
        value: widget.stats.totalLiabilities,
        title: touchedIndex == 1
            ? '${((widget.stats.totalLiabilities / total) * 100).toStringAsFixed(1)}%'
            : '',
        radius: touchedIndex == 1 ? 70 : 60,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      // Equity
      PieChartSectionData(
        color: Color(AppConfig.equityColorValue),
        value: widget.stats.totalEquity,
        title: touchedIndex == 2
            ? '${((widget.stats.totalEquity / total) * 100).toStringAsFixed(1)}%'
            : '',
        radius: touchedIndex == 2 ? 70 : 60,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      // Revenue
      PieChartSectionData(
        color: Color(AppConfig.revenueColorValue),
        value: widget.stats.totalRevenue,
        title: touchedIndex == 3
            ? '${((widget.stats.totalRevenue / total) * 100).toStringAsFixed(1)}%'
            : '',
        radius: touchedIndex == 3 ? 70 : 60,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      // Expenses
      PieChartSectionData(
        color: Color(AppConfig.expenseColorValue),
        value: widget.stats.totalExpenses,
        title: touchedIndex == 4
            ? '${((widget.stats.totalExpenses / total) * 100).toStringAsFixed(1)}%'
            : '',
        radius: touchedIndex == 4 ? 70 : 60,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    ];
  }

  Widget _buildLegend() {
    return Column(
      children: [
        _buildLegendItem(
          'أصول',
          'Assets',
          widget.stats.totalAssets,
          Color(AppConfig.assetColorValue),
        ),
        _buildLegendItem(
          'خصوم',
          'Liabilities',
          widget.stats.totalLiabilities,
          Color(AppConfig.liabilityColorValue),
        ),
        _buildLegendItem(
          'حقوق ملكية',
          'Equity',
          widget.stats.totalEquity,
          Color(AppConfig.equityColorValue),
        ),
        _buildLegendItem(
          'إيرادات',
          'Revenue',
          widget.stats.totalRevenue,
          Color(AppConfig.revenueColorValue),
        ),
        _buildLegendItem(
          'مصروفات',
          'Expenses',
          widget.stats.totalExpenses,
          Color(AppConfig.expenseColorValue),
        ),
      ],
    );
  }

  Widget _buildLegendItem(
      String titleAr, String titleEn, double value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 16,
            height: 16,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  titleAr,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  titleEn,
                  style: const TextStyle(
                    fontSize: 10,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ),
          Text(
            _formatCurrency(value),
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  String _formatCurrency(double amount) {
    if (amount >= 1000000) {
      return '${(amount / 1000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000) {
      return '${(amount / 1000).toStringAsFixed(1)}K';
    } else {
      return amount.toStringAsFixed(0);
    }
  }
}
