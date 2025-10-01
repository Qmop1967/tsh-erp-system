import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';

class CashBoxCard extends StatelessWidget {
  final double totalCash;
  final double dailyCollection;
  final List<Map<String, dynamic>> recentTransactions;
  final bool isLoading;

  const CashBoxCard({
    super.key,
    required this.totalCash,
    required this.dailyCollection,
    required this.recentTransactions,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final currencyFormatter = NumberFormat.currency(symbol: 'IQD ', decimalDigits: 0);

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    MdiIcons.cashMultiple,
                    color: Colors.blue,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Cash Box',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      if (isLoading)
                        Container(
                          height: 20,
                          width: 120,
                          decoration: BoxDecoration(
                            color: Colors.grey[300],
                            borderRadius: BorderRadius.circular(4),
                          ),
                        )
                      else
                        Text(
                          currencyFormatter.format(totalCash),
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.blue[700],
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Icon(
                    MdiIcons.trendingUp,
                    color: Colors.green,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Today\'s Collection',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.green[700],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        if (isLoading)
                          Container(
                            height: 16,
                            width: 80,
                            margin: const EdgeInsets.only(top: 2),
                            decoration: BoxDecoration(
                              color: Colors.grey[300],
                              borderRadius: BorderRadius.circular(4),
                            ),
                          )
                        else
                          Text(
                            currencyFormatter.format(dailyCollection),
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.green[800],
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            if (!isLoading && recentTransactions.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                'Recent Transactions',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              ...recentTransactions.take(3).map((transaction) => _buildTransactionItem(
                context,
                transaction['type'] ?? 'payment',
                transaction['amount'] ?? 0.0,
                transaction['description'] ?? 'Transaction',
                transaction['time'] ?? DateTime.now(),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTransactionItem(BuildContext context, String type, double amount, String description, DateTime time) {
    final isPayment = type == 'payment';
    final timeFormatter = DateFormat('HH:mm');
    final currencyFormatter = NumberFormat.currency(symbol: 'IQD ', decimalDigits: 0);
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            isPayment ? MdiIcons.plus : MdiIcons.minus,
            size: 16,
            color: isPayment ? Colors.green : Colors.red,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              description,
              style: Theme.of(context).textTheme.bodySmall,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            currencyFormatter.format(amount),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontWeight: FontWeight.w600,
              color: isPayment ? Colors.green : Colors.red,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            timeFormatter.format(time),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}
