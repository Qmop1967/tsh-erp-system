import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';

class PendingTransfersSection extends StatelessWidget {
  const PendingTransfersSection({super.key});

  @override
  Widget build(BuildContext context) {
    // Sample data - replace with actual API data
    final pendingTransfers = [
      {
        'id': 'REM-2024-001',
        'amount': 10000000.0,
        'currency': 'IQD',
        'channel': 'Al-Taif Exchange',
        'date': '2024-01-15',
        'fees': 25000.0,
        'hasProof': true,
        'notes': 'تحويل اسبوعي - العملاء من بغداد',
      },
      {
        'id': 'REM-2024-002',
        'amount': 5000000.0,
        'currency': 'IQD',
        'channel': 'Zain Cash',
        'date': '2024-01-14',
        'fees': 15000.0,
        'hasProof': true,
        'notes': '',
      },
    ];

    if (pendingTransfers.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: pendingTransfers.length,
      itemBuilder: (context, index) {
        return _buildPendingTransferCard(context, pendingTransfers[index]);
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            MdiIcons.checkboxMultipleMarkedOutline,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد حوالات معلقة',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'جميع حوالاتك تم تأكيدها',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPendingTransferCard(BuildContext context, Map<String, dynamic> transfer) {
    final channel = transfer['channel'] as String;
    IconData channelIcon;
    Color channelColor;

    switch (channel) {
      case 'Al-Taif Exchange':
        channelIcon = MdiIcons.storeOutline;
        channelColor = const Color(0xFF0288D1);
        break;
      case 'Al-Taif Bank':
        channelIcon = MdiIcons.bank;
        channelColor = const Color(0xFF1976D2);
        break;
      case 'Zain Cash':
        channelIcon = MdiIcons.cellphone;
        channelColor = const Color(0xFF9C27B0);
        break;
      case 'Super Key':
        channelIcon = MdiIcons.wallet;
        channelColor = const Color(0xFFE91E63);
        break;
      default:
        channelIcon = MdiIcons.bankTransfer;
        channelColor = const Color(0xFF757575);
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFFFA726).withOpacity(0.3),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFFFA726).withOpacity(0.1),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFFFA726).withOpacity(0.1),
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
                    color: channelColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    channelIcon,
                    color: channelColor,
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
                    color: const Color(0xFFFFA726),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        MdiIcons.clockOutline,
                        size: 14,
                        color: Colors.white,
                      ),
                      const SizedBox(width: 4),
                      const Text(
                        'معلقة',
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
          // Content
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'المبلغ',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${NumberFormat.currency(symbol: '', decimalDigits: 0).format(transfer['amount'])} ${transfer['currency']}',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0288D1),
                          ),
                        ),
                      ],
                    ),
                    if (transfer['hasProof'] == true)
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: const Color(0xFF66BB6A).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(
                          MdiIcons.fileCheck,
                          color: const Color(0xFF66BB6A),
                          size: 24,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                Divider(color: Colors.grey[200]),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(MdiIcons.calendar, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      transfer['date'],
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[700],
                      ),
                    ),
                    const SizedBox(width: 20),
                    Icon(MdiIcons.cashMinus, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 8),
                    Text(
                      'رسوم: ${NumberFormat.compact().format(transfer['fees'])}',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[700],
                      ),
                    ),
                  ],
                ),
                if (transfer['notes'] != null && transfer['notes'].toString().isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      children: [
                        Icon(MdiIcons.noteText, size: 16, color: Colors.grey[600]),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            transfer['notes'],
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
          // Actions
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(16),
                bottomRight: Radius.circular(16),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {},
                    icon: Icon(MdiIcons.pencil, size: 18),
                    label: const Text('تعديل'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF0288D1),
                      side: const BorderSide(color: Color(0xFF0288D1)),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {},
                    icon: Icon(MdiIcons.delete, size: 18),
                    label: const Text('إلغاء'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFFEF5350),
                      side: const BorderSide(color: Color(0xFFEF5350)),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {},
                    icon: Icon(MdiIcons.eye, size: 18),
                    label: const Text('عرض'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4FC3F7),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
