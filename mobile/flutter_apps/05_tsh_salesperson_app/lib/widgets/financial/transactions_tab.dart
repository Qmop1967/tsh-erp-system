import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';
import '../../config/app_theme.dart';

class TransactionsTab extends StatelessWidget {
  const TransactionsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildFilterChips(),
        const SizedBox(height: 20),
        _buildSectionHeader('سجل المعاملات المالية', MdiIcons.formatListBulleted),
        const SizedBox(height: 12),
        _buildTransactionsList(),
      ],
    );
  }

  Widget _buildFilterChips() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _buildFilterChip('الكل', true, AppTheme.primaryGreen),
          const SizedBox(width: 8),
          _buildFilterChip('عمولات', false, Colors.green),
          const SizedBox(width: 8),
          _buildFilterChip('رواتب', false, Colors.blue),
          const SizedBox(width: 8),
          _buildFilterChip('مكافآت', false, Colors.purple),
          const SizedBox(width: 8),
          _buildFilterChip('غرامات', false, Colors.red),
          const SizedBox(width: 8),
          _buildFilterChip('خصومات', false, Colors.orange),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, bool isSelected, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: isSelected ? color : Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isSelected ? color : Colors.grey[300]!,
          width: 1,
        ),
        boxShadow: isSelected
            ? [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ]
            : [],
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 13,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          color: isSelected ? Colors.white : Colors.grey[700],
        ),
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

  Widget _buildTransactionsList() {
    final transactions = [
      {
        'type': 'commission',
        'title': 'عمولة طلب #ORD-2024-1234',
        'amount': 850000.0,
        'date': '2024-01-15 14:30',
        'status': 'completed',
        'icon': MdiIcons.cashMultiple,
        'color': AppTheme.success,
        'isCredit': true,
      },
      {
        'type': 'salary',
        'title': 'راتب شهر يناير 2024',
        'amount': 5000000.0,
        'date': '2024-01-01 09:00',
        'status': 'completed',
        'icon': MdiIcons.cashCheck,
        'color': Colors.blue,
        'isCredit': true,
      },
      {
        'type': 'reward',
        'title': 'مكافأة أفضل مندوب مبيعات',
        'amount': 2000000.0,
        'date': '2023-12-31 10:00',
        'status': 'completed',
        'icon': MdiIcons.trophyAward,
        'color': Colors.purple,
        'isCredit': true,
      },
      {
        'type': 'fine',
        'title': 'غرامة عجز في الصندوق',
        'amount': 150000.0,
        'date': '2023-12-28 16:45',
        'status': 'completed',
        'icon': MdiIcons.alertOctagon,
        'color': AppTheme.error,
        'isCredit': false,
      },
      {
        'type': 'commission',
        'title': 'عمولة طلب #ORD-2024-1198',
        'amount': 1200000.0,
        'date': '2023-12-25 11:20',
        'status': 'pending',
        'icon': MdiIcons.cashMultiple,
        'color': AppTheme.warning,
        'isCredit': true,
      },
      {
        'type': 'advance',
        'title': 'سلفة على الراتب',
        'amount': 1000000.0,
        'date': '2023-12-20 09:15',
        'status': 'completed',
        'icon': MdiIcons.cashFast,
        'color': Colors.orange,
        'isCredit': true,
      },
      {
        'type': 'deduction',
        'title': 'خصم التأمينات الاجتماعية',
        'amount': 150000.0,
        'date': '2023-12-01 09:00',
        'status': 'completed',
        'icon': MdiIcons.shieldAccount,
        'color': Colors.grey[700]!,
        'isCredit': false,
      },
      {
        'type': 'commission',
        'title': 'عمولة طلب #ORD-2024-1167',
        'amount': 650000.0,
        'date': '2023-11-28 13:40',
        'status': 'completed',
        'icon': MdiIcons.cashMultiple,
        'color': AppTheme.success,
        'isCredit': true,
      },
    ];

    return Column(
      children: transactions.map((transaction) {
        final isCredit = transaction['isCredit'] as bool;
        final isPending = transaction['status'] == 'pending';

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: (transaction['color'] as Color).withOpacity(0.2),
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
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: (transaction['color'] as Color).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  transaction['icon'] as IconData,
                  color: transaction['color'] as Color,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      transaction['title'] as String,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          MdiIcons.clockOutline,
                          size: 12,
                          color: Colors.grey[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          transaction['date'] as String,
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey[600],
                          ),
                        ),
                        if (isPending) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: AppTheme.warning.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              'معلقة',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: AppTheme.warning,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${isCredit ? '+' : '-'} ${NumberFormat.compact().format((transaction['amount'] as double) / 1000)}K',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: isCredit ? AppTheme.success : AppTheme.error,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'IQD',
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
