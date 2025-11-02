import 'package:flutter/material.dart';
import '../../models/account_statement.dart';
import '../../utils/tsh_theme.dart';
import '../../utils/tsh_localizations.dart';

class AccountStatementScreen extends StatefulWidget {
  const AccountStatementScreen({super.key});

  @override
  State<AccountStatementScreen> createState() => _AccountStatementScreenState();
}

class _AccountStatementScreenState extends State<AccountStatementScreen> {
  AccountStatement? _statement;
  bool _isLoading = false;
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _endDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _loadStatement();
  }

  Future<void> _loadStatement() async {
    setState(() => _isLoading = true);

    // Mock data - Replace with actual API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _statement = AccountStatement(
        startDate: _startDate,
        endDate: _endDate,
        openingBalance: 15000000,
        closingBalance: 12500000,
        transactions: [
          StatementTransaction(
            id: '1',
            date: DateTime.now().subtract(const Duration(days: 25)),
            type: 'debit',
            description: 'Invoice INV-2024-001',
            amount: 8500000,
            balance: 23500000,
            referenceNumber: 'INV-2024-001',
          ),
          StatementTransaction(
            id: '2',
            date: DateTime.now().subtract(const Duration(days: 20)),
            type: 'credit',
            description: 'Payment received - Bank Transfer',
            amount: 5000000,
            balance: 18500000,
            referenceNumber: 'PMT-2024-001',
          ),
          StatementTransaction(
            id: '3',
            date: DateTime.now().subtract(const Duration(days: 10)),
            type: 'debit',
            description: 'Invoice INV-2024-002',
            amount: 6000000,
            balance: 24500000,
            referenceNumber: 'INV-2024-002',
          ),
          StatementTransaction(
            id: '4',
            date: DateTime.now().subtract(const Duration(days: 5)),
            type: 'credit',
            description: 'Credit Note CN-2024-001',
            amount: 500000,
            balance: 24000000,
            referenceNumber: 'CN-2024-001',
          ),
          StatementTransaction(
            id: '5',
            date: DateTime.now().subtract(const Duration(days: 2)),
            type: 'credit',
            description: 'Payment received - Check',
            amount: 3500000,
            balance: 20500000,
            referenceNumber: 'PMT-2024-002',
          ),
        ],
      );
      _isLoading = false;
    });
  }

  Future<void> _selectDateRange() async {
    final DateTimeRange? picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now(),
      initialDateRange: DateTimeRange(start: _startDate, end: _endDate),
    );

    if (picked != null) {
      setState(() {
        _startDate = picked.start;
        _endDate = picked.end;
      });
      _loadStatement();
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = TSHLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.translate('account_statement')),
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Download coming soon')),
              );
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _statement == null
              ? const Center(child: Text('No data available'))
              : Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(16),
                      color: TSHTheme.backgroundLight,
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Period', style: TSHTheme.bodySmall),
                                  Text(
                                    '${_startDate.day}/${_startDate.month}/${_startDate.year} - ${_endDate.day}/${_endDate.month}/${_endDate.year}',
                                    style: TSHTheme.bodyMedium.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                              OutlinedButton.icon(
                                onPressed: _selectDateRange,
                                icon: const Icon(Icons.calendar_today, size: 16),
                                label: const Text('Change'),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              Expanded(
                                child: Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: TSHTheme.card,
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: TSHTheme.border),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text('Opening', style: TSHTheme.bodySmall),
                                      Text(
                                        loc.formatCurrency(_statement!.openingBalance),
                                        style: TSHTheme.bodyLarge.copyWith(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: TSHTheme.card,
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: TSHTheme.border),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text('Closing', style: TSHTheme.bodySmall),
                                      Text(
                                        loc.formatCurrency(_statement!.closingBalance),
                                        style: TSHTheme.bodyLarge.copyWith(
                                          fontWeight: FontWeight.bold,
                                          color: TSHTheme.errorRed,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _statement!.transactions.length,
                        itemBuilder: (context, index) {
                          final transaction = _statement!.transactions[index];
                          final isDebit = transaction.type == 'debit';

                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              contentPadding: const EdgeInsets.all(12),
                              leading: Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: (isDebit
                                          ? TSHTheme.errorRed
                                          : TSHTheme.successGreen)
                                      .withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(
                                  isDebit ? Icons.arrow_upward : Icons.arrow_downward,
                                  color: isDebit
                                      ? TSHTheme.errorRed
                                      : TSHTheme.successGreen,
                                  size: 20,
                                ),
                              ),
                              title: Text(
                                transaction.description,
                                style: TSHTheme.bodyMedium.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text(
                                    '${transaction.date.day}/${transaction.date.month}/${transaction.date.year}',
                                    style: TSHTheme.bodySmall,
                                  ),
                                  if (transaction.referenceNumber != null) ...[
                                    const SizedBox(height: 2),
                                    Text(
                                      transaction.referenceNumber!,
                                      style: TSHTheme.bodySmall,
                                    ),
                                  ],
                                ],
                              ),
                              trailing: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    '${isDebit ? '+' : '-'}${loc.formatCurrency(transaction.amount)}',
                                    style: TSHTheme.bodyLarge.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: isDebit
                                          ? TSHTheme.errorRed
                                          : TSHTheme.successGreen,
                                    ),
                                  ),
                                  Text(
                                    loc.formatCurrency(transaction.balance),
                                    style: TSHTheme.bodySmall,
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
    );
  }
}
