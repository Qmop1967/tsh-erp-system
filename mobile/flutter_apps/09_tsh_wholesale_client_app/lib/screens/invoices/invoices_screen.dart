import 'package:flutter/material.dart';
import '../../models/invoice.dart';
import '../../utils/tsh_theme.dart';
import '../../utils/tsh_localizations.dart';

class InvoicesScreen extends StatefulWidget {
  const InvoicesScreen({super.key});

  @override
  State<InvoicesScreen> createState() => _InvoicesScreenState();
}

class _InvoicesScreenState extends State<InvoicesScreen> {
  List<Invoice> _invoices = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadInvoices();
  }

  Future<void> _loadInvoices() async {
    setState(() => _isLoading = true);

    // Mock data - Replace with actual API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _invoices = [
        Invoice(
          id: '1',
          invoiceNumber: 'INV-2024-001',
          invoiceDate: DateTime.now().subtract(const Duration(days: 10)),
          dueDate: DateTime.now().add(const Duration(days: 20)),
          totalAmount: 8500000,
          paidAmount: 5000000,
          balanceAmount: 3500000,
          status: 'sent',
          currency: 'IQD',
        ),
        Invoice(
          id: '2',
          invoiceNumber: 'INV-2024-002',
          invoiceDate: DateTime.now().subtract(const Duration(days: 25)),
          dueDate: DateTime.now().subtract(const Duration(days: 5)),
          totalAmount: 6000000,
          paidAmount: 0,
          balanceAmount: 6000000,
          status: 'overdue',
          currency: 'IQD',
        ),
        Invoice(
          id: '3',
          invoiceNumber: 'INV-2024-003',
          invoiceDate: DateTime.now().subtract(const Duration(days: 40)),
          dueDate: DateTime.now().subtract(const Duration(days: 10)),
          totalAmount: 3500000,
          paidAmount: 3500000,
          balanceAmount: 0,
          status: 'paid',
          currency: 'IQD',
        ),
      ];
      _isLoading = false;
    });
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'paid':
        return TSHTheme.successGreen;
      case 'sent':
        return TSHTheme.primary;
      case 'overdue':
        return TSHTheme.errorRed;
      case 'draft':
        return TSHTheme.textSecondary;
      case 'cancelled':
        return TSHTheme.textSecondary;
      default:
        return TSHTheme.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final loc = TSHLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.translate('invoices')),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _invoices.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.receipt, size: 64, color: TSHTheme.textSecondary),
                      const SizedBox(height: 16),
                      Text(
                        'No invoices',
                        style: TSHTheme.bodyLarge
                            .copyWith(color: TSHTheme.textSecondary),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadInvoices,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _invoices.length,
                    itemBuilder: (context, index) {
                      final invoice = _invoices[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    invoice.invoiceNumber,
                                    style: TSHTheme.bodyLarge.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: _getStatusColor(invoice.status)
                                          .withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(4),
                                      border: Border.all(
                                        color: _getStatusColor(invoice.status),
                                      ),
                                    ),
                                    child: Text(
                                      invoice.status.toUpperCase(),
                                      style: TSHTheme.bodySmall.copyWith(
                                        color: _getStatusColor(invoice.status),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        loc.translate('invoice_date'),
                                        style: TSHTheme.bodySmall,
                                      ),
                                      Text(
                                        '${invoice.invoiceDate.day}/${invoice.invoiceDate.month}/${invoice.invoiceDate.year}',
                                        style: TSHTheme.bodyMedium.copyWith(
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ],
                                  ),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      Text(
                                        loc.translate('due_date'),
                                        style: TSHTheme.bodySmall,
                                      ),
                                      Text(
                                        '${invoice.dueDate.day}/${invoice.dueDate.month}/${invoice.dueDate.year}',
                                        style: TSHTheme.bodyMedium.copyWith(
                                          fontWeight: FontWeight.w600,
                                          color: invoice.isOverdue
                                              ? TSHTheme.errorRed
                                              : null,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              const Divider(height: 24),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text('Total', style: TSHTheme.bodySmall),
                                      Text(
                                        loc.formatCurrency(invoice.totalAmount),
                                        style: TSHTheme.bodyLarge.copyWith(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      Text('Balance', style: TSHTheme.bodySmall),
                                      Text(
                                        loc.formatCurrency(invoice.balanceAmount),
                                        style: TSHTheme.bodyLarge.copyWith(
                                          fontWeight: FontWeight.bold,
                                          color: invoice.balanceAmount > 0
                                              ? TSHTheme.errorRed
                                              : TSHTheme.successGreen,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  Expanded(
                                    child: OutlinedButton.icon(
                                      onPressed: () {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(
                                            content: Text('View invoice coming soon'),
                                          ),
                                        );
                                      },
                                      icon: const Icon(Icons.visibility, size: 18),
                                      label: Text(loc.translate('view')),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: ElevatedButton.icon(
                                      onPressed: () {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(
                                            content: Text('Download coming soon'),
                                          ),
                                        );
                                      },
                                      icon: const Icon(Icons.download, size: 18),
                                      label: Text(loc.translate('download')),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
