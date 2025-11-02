import 'package:flutter/material.dart';
import '../../models/payment.dart';
import '../../utils/tsh_theme.dart';
import '../../utils/tsh_localizations.dart';

class PaymentsScreen extends StatefulWidget {
  const PaymentsScreen({super.key});

  @override
  State<PaymentsScreen> createState() => _PaymentsScreenState();
}

class _PaymentsScreenState extends State<PaymentsScreen> {
  List<Payment> _payments = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadPayments();
  }

  Future<void> _loadPayments() async {
    setState(() => _isLoading = true);

    // Mock data - Replace with actual API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _payments = [
        Payment(
          id: '1',
          amount: 5000000,
          currency: 'IQD',
          paymentDate: DateTime.now().subtract(const Duration(days: 5)),
          paymentMethod: 'bank_transfer',
          status: 'completed',
          referenceNumber: 'REF-2024-001',
          invoiceIds: ['INV-001', 'INV-002'],
        ),
        Payment(
          id: '2',
          amount: 3500000,
          currency: 'IQD',
          paymentDate: DateTime.now().subtract(const Duration(days: 15)),
          paymentMethod: 'check',
          status: 'completed',
          referenceNumber: 'CHK-2024-045',
          invoiceIds: ['INV-003'],
        ),
        Payment(
          id: '3',
          amount: 2000000,
          currency: 'IQD',
          paymentDate: DateTime.now().subtract(const Duration(days: 25)),
          paymentMethod: 'cash',
          status: 'completed',
          invoiceIds: ['INV-004'],
        ),
      ];
      _isLoading = false;
    });
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'completed':
        return TSHTheme.successGreen;
      case 'pending':
        return TSHTheme.warningOrange;
      case 'failed':
        return TSHTheme.errorRed;
      case 'cancelled':
        return TSHTheme.textSecondary;
      default:
        return TSHTheme.textSecondary;
    }
  }

  String _getPaymentMethodLabel(String method) {
    switch (method) {
      case 'bank_transfer':
        return 'Bank Transfer';
      case 'check':
        return 'Check';
      case 'cash':
        return 'Cash';
      case 'credit_card':
        return 'Credit Card';
      default:
        return method;
    }
  }

  IconData _getPaymentMethodIcon(String method) {
    switch (method) {
      case 'bank_transfer':
        return Icons.account_balance;
      case 'check':
        return Icons.receipt_long;
      case 'cash':
        return Icons.payments;
      case 'credit_card':
        return Icons.credit_card;
      default:
        return Icons.payment;
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = TSHLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.translate('payments')),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Make payment coming soon')),
          );
        },
        icon: const Icon(Icons.add),
        label: Text(loc.translate('make_payment')),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _payments.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.payment, size: 64, color: TSHTheme.textSecondary),
                      const SizedBox(height: 16),
                      Text(
                        'No payment history',
                        style: TSHTheme.bodyLarge
                            .copyWith(color: TSHTheme.textSecondary),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadPayments,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _payments.length,
                    itemBuilder: (context, index) {
                      final payment = _payments[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16),
                          leading: Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              color: _getStatusColor(payment.status).withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Icon(
                              _getPaymentMethodIcon(payment.paymentMethod),
                              color: _getStatusColor(payment.status),
                            ),
                          ),
                          title: Text(
                            loc.formatCurrency(payment.amount),
                            style: TSHTheme.bodyLarge.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 4),
                              Text(_getPaymentMethodLabel(payment.paymentMethod)),
                              if (payment.referenceNumber != null) ...[
                                const SizedBox(height: 4),
                                Text(
                                  payment.referenceNumber!,
                                  style: TSHTheme.bodySmall,
                                ),
                              ],
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: _getStatusColor(payment.status)
                                          .withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(4),
                                      border: Border.all(
                                        color: _getStatusColor(payment.status),
                                      ),
                                    ),
                                    child: Text(
                                      payment.status.toUpperCase(),
                                      style: TSHTheme.bodySmall.copyWith(
                                        color: _getStatusColor(payment.status),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          trailing: Text(
                            '${payment.paymentDate.day}/${payment.paymentDate.month}/${payment.paymentDate.year}',
                            style: TSHTheme.bodySmall,
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
