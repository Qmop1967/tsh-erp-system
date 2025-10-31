import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';

class ConfirmedTransfersSection extends StatelessWidget {
  const ConfirmedTransfersSection({super.key});

  @override
  Widget build(BuildContext context) {
    final confirmedTransfers = [
      {
        'id': 'REM-2024-003',
        'amount': 12000000.0,
        'currency': 'IQD',
        'channel': 'Al-Taif Bank',
        'date': '2024-01-13',
        'confirmedDate': '2024-01-14',
        'fees': 30000.0,
        'adminNote': 'تم الاستلام بنجاح',
      },
      {
        'id': 'REM-2024-004',
        'amount': 8000000.0,
        'currency': 'IQD',
        'channel': 'Al-Taif Exchange',
        'date': '2024-01-12',
        'confirmedDate': '2024-01-13',
        'fees': 20000.0,
        'adminNote': '',
      },
      {
        'id': 'REM-2024-005',
        'amount': 15000000.0,
        'currency': 'IQD',
        'channel': 'Zain Cash',
        'date': '2024-01-11',
        'confirmedDate': '2024-01-12',
        'fees': 35000.0,
        'adminNote': '',
      },
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: confirmedTransfers.length,
      itemBuilder: (context, index) {
        return _buildConfirmedTransferCard(confirmedTransfers[index]);
      },
    );
  }

  Widget _buildConfirmedTransferCard(Map<String, dynamic> transfer) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFF66BB6A).withOpacity(0.3),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF66BB6A).withOpacity(0.1),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF66BB6A).withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF66BB6A).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    MdiIcons.checkCircle,
                    color: const Color(0xFF66BB6A),
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        transfer['channel'],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        transfer['id'],
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
                    color: const Color(0xFF66BB6A),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    children: [
                      Icon(
                        Icons.check,
                        size: 14,
                        color: Colors.white,
                      ),
                      SizedBox(width: 4),
                      Text(
                        'مؤكدة',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${NumberFormat.currency(symbol: '', decimalDigits: 0).format(transfer['amount'])} ${transfer['currency']}',
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF66BB6A),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Icon(MdiIcons.calendar, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      'التحويل: ${transfer['date']}',
                      style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(MdiIcons.checkCircle, size: 16, color: const Color(0xFF66BB6A)),
                    const SizedBox(width: 8),
                    Text(
                      'التأكيد: ${transfer['confirmedDate']}',
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF66BB6A),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                if (transfer['adminNote'] != null && transfer['adminNote'].toString().isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF66BB6A).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      children: [
                        Icon(MdiIcons.commentText, size: 16, color: const Color(0xFF66BB6A)),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            transfer['adminNote'],
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey[700],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
