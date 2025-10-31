import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';

class ArchivedTransfersSection extends StatelessWidget {
  const ArchivedTransfersSection({super.key});

  @override
  Widget build(BuildContext context) {
    final archivedTransfers = [
      {
        'id': 'REM-2023-099',
        'amount': 10000000.0,
        'currency': 'IQD',
        'channel': 'Al-Taif Bank',
        'date': '2023-12-30',
        'confirmedDate': '2023-12-31',
      },
      {
        'id': 'REM-2023-098',
        'amount': 8500000.0,
        'currency': 'IQD',
        'channel': 'Al-Taif Exchange',
        'date': '2023-12-23',
        'confirmedDate': '2023-12-24',
      },
      {
        'id': 'REM-2023-097',
        'amount': 12000000.0,
        'currency': 'IQD',
        'channel': 'Zain Cash',
        'date': '2023-12-16',
        'confirmedDate': '2023-12-17',
      },
    ];

    return Column(
      children: [
        _buildSearchBar(),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: archivedTransfers.length,
            itemBuilder: (context, index) {
              return _buildArchivedTransferCard(archivedTransfers[index]);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextField(
        decoration: InputDecoration(
          hintText: 'بحث برقم الحوالة أو التاريخ...',
          border: InputBorder.none,
          icon: Icon(MdiIcons.magnify, color: const Color(0xFF757575)),
        ),
      ),
    );
  }

  Widget _buildArchivedTransferCard(Map<String, dynamic> transfer) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.grey[300]!,
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
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              MdiIcons.archive,
              color: Colors.grey[600],
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  transfer['channel'],
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  transfer['id'],
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  transfer['date'],
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                NumberFormat.compact().format(transfer['amount'] / 1000) + 'K',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                transfer['currency'],
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
