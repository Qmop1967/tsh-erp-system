import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';
import '../../config/app_theme.dart';

class FinesTab extends StatelessWidget {
  const FinesTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildTotalFinesCard(),
        const SizedBox(height: 20),
        _buildSectionHeader('الغرامات والخصومات', MdiIcons.alertCircleOutline),
        const SizedBox(height: 12),
        _buildFinesList(),
      ],
    );
  }

  Widget _buildTotalFinesCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.red[400]!,
            Colors.red[300]!,
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.red.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  MdiIcons.alertOctagon,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'إجمالي الغرامات',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Text(
            'IQD 350,000',
            style: TextStyle(
              color: Colors.white,
              fontSize: 36,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'هذا العام',
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: _buildQuickStat('مخصومة', 'IQD 350K', MdiIcons.checkCircle),
              ),
              Container(
                width: 1,
                height: 40,
                color: Colors.white.withOpacity(0.3),
                margin: const EdgeInsets.symmetric(horizontal: 16),
              ),
              Expanded(
                child: _buildQuickStat('معلقة', 'IQD 0', MdiIcons.clockOutline),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStat(String label, String amount, IconData icon) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: Colors.white70),
            const SizedBox(width: 6),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          amount,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
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

  Widget _buildFinesList() {
    final fines = [
      {
        'title': 'تأخر في تقديم التقرير اليومي',
        'amount': 50000.0,
        'date': '2024-01-10',
        'description': 'تأخر 3 أيام في تقديم تقرير المبيعات',
        'status': 'deducted',
        'icon': MdiIcons.fileDocumentRemove,
        'severity': 'low',
      },
      {
        'title': 'عجز في الصندوق',
        'amount': 150000.0,
        'date': '2023-12-28',
        'description': 'عجز في الصندوق بمبلغ 150 ألف دينار',
        'status': 'deducted',
        'icon': MdiIcons.cashMinus,
        'severity': 'high',
      },
      {
        'title': 'عدم الالتزام بالزي الرسمي',
        'amount': 25000.0,
        'date': '2023-12-15',
        'description': 'مخالفة سياسة الزي الرسمي للشركة',
        'status': 'deducted',
        'icon': MdiIcons.tshirtCrew,
        'severity': 'low',
      },
      {
        'title': 'فقدان إيصال رسمي',
        'amount': 75000.0,
        'date': '2023-12-05',
        'description': 'فقدان إيصال رسمي رقم #12345',
        'status': 'deducted',
        'icon': MdiIcons.receiptTextRemove,
        'severity': 'medium',
      },
      {
        'title': 'تجاوز الوقت المحدد للزيارات',
        'amount': 50000.0,
        'date': '2023-11-20',
        'description': 'تجاوز المدة المحددة لزيارة العملاء',
        'status': 'deducted',
        'icon': MdiIcons.clockAlert,
        'severity': 'low',
      },
    ];

    return Column(
      children: fines.map((fine) {
        Color severityColor;
        switch (fine['severity']) {
          case 'high':
            severityColor = Colors.red[700]!;
            break;
          case 'medium':
            severityColor = Colors.orange[700]!;
            break;
          default:
            severityColor = Colors.yellow[700]!;
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: severityColor.withOpacity(0.2),
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
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: severityColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      fine['icon'] as IconData,
                      color: severityColor,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          fine['title'] as String,
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          fine['date'] as String,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppTheme.error.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '- ${NumberFormat.compact().format((fine['amount'] as double) / 1000)}K',
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.error,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Icon(
                      MdiIcons.informationOutline,
                      size: 16,
                      color: Colors.red[700],
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        fine['description'] as String,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.red[700],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      MdiIcons.checkCircle,
                      size: 14,
                      color: AppTheme.success,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'تم الخصم من الراتب',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.success,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}
