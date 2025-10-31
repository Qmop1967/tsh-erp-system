import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';
import '../../config/app_theme.dart';

class CommissionsTab extends StatelessWidget {
  const CommissionsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildStatisticsCards(),
        const SizedBox(height: 20),
        _buildSectionHeader('العمولات الأخيرة', MdiIcons.history),
        const SizedBox(height: 12),
        _buildCommissionsList(),
      ],
    );
  }

  Widget _buildStatisticsCards() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'هذا الشهر',
            'IQD 8,500,000',
            MdiIcons.calendarMonth,
            AppTheme.primaryGreen,
            '+12.5%',
            true,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'المتوسط',
            'IQD 6,200,000',
            MdiIcons.chartLine,
            Colors.blue,
            '',
            null,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
    String title,
    String amount,
    IconData icon,
    Color color,
    String change,
    bool? isPositive,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const Spacer(),
              if (change.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: isPositive == true
                        ? AppTheme.success.withOpacity(0.1)
                        : AppTheme.error.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        isPositive == true
                            ? MdiIcons.trendingUp
                            : MdiIcons.trendingDown,
                        size: 12,
                        color: isPositive == true ? AppTheme.success : AppTheme.error,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        change,
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: isPositive == true ? AppTheme.success : AppTheme.error,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            amount,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 22, color: AppTheme.primaryGreen),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }

  Widget _buildCommissionsList() {
    final commissions = [
      {
        'customer': 'متجر الأمل - بغداد',
        'order': '#ORD-2024-1234',
        'amount': 850000.0,
        'rate': '2.5%',
        'date': '2024-01-15',
        'status': 'paid',
      },
      {
        'customer': 'مؤسسة النور - البصرة',
        'order': '#ORD-2024-1198',
        'amount': 1200000.0,
        'rate': '3.0%',
        'date': '2024-01-14',
        'status': 'pending',
      },
      {
        'customer': 'شركة الفجر - أربيل',
        'order': '#ORD-2024-1167',
        'amount': 650000.0,
        'rate': '2.0%',
        'date': '2024-01-12',
        'status': 'paid',
      },
      {
        'customer': 'معرض السلام - الموصل',
        'order': '#ORD-2024-1156',
        'amount': 920000.0,
        'rate': '2.8%',
        'date': '2024-01-11',
        'status': 'paid',
      },
      {
        'customer': 'محلات النجاح - كربلاء',
        'order': '#ORD-2024-1145',
        'amount': 450000.0,
        'rate': '1.5%',
        'date': '2024-01-10',
        'status': 'cancelled',
      },
    ];

    return Column(
      children: commissions.map((commission) {
        return _buildCommissionItem(commission);
      }).toList(),
    );
  }

  Widget _buildCommissionItem(Map<String, dynamic> commission) {
    final isPaid = commission['status'] == 'paid';
    final isPending = commission['status'] == 'pending';
    final isCancelled = commission['status'] == 'cancelled';

    Color statusColor = isPaid
        ? AppTheme.success
        : isPending
            ? AppTheme.warning
            : AppTheme.error;

    String statusText = isPaid
        ? 'مدفوعة'
        : isPending
            ? 'معلقة'
            : 'ملغية';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: statusColor.withOpacity(0.2),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      commission['customer'],
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      commission['order'],
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  statusText,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: statusColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Divider(color: Colors.grey[200], height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildInfoItem(
                MdiIcons.cashMultiple,
                NumberFormat.currency(symbol: 'IQD ', decimalDigits: 0)
                    .format(commission['amount']),
                AppTheme.primaryGreen,
              ),
              _buildInfoItem(
                MdiIcons.percent,
                commission['rate'],
                Colors.blue,
              ),
              _buildInfoItem(
                MdiIcons.calendarBlank,
                commission['date'],
                Colors.grey[700]!,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String text, Color color) {
    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 6),
        Text(
          text,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: color,
          ),
        ),
      ],
    );
  }
}
