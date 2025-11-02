import 'package:flutter/material.dart';
import '../../models/credit_note.dart';
import '../../utils/tsh_theme.dart';
import '../../utils/tsh_localizations.dart';

class CreditNotesScreen extends StatefulWidget {
  const CreditNotesScreen({super.key});

  @override
  State<CreditNotesScreen> createState() => _CreditNotesScreenState();
}

class _CreditNotesScreenState extends State<CreditNotesScreen> {
  List<CreditNote> _creditNotes = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadCreditNotes();
  }

  Future<void> _loadCreditNotes() async {
    setState(() => _isLoading = true);

    // Mock data - Replace with actual API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _creditNotes = [
        CreditNote(
          id: '1',
          creditNoteNumber: 'CN-2024-001',
          issueDate: DateTime.now().subtract(const Duration(days: 15)),
          amount: 500000,
          currency: 'IQD',
          status: 'issued',
          reason: 'Damaged goods returned',
          invoiceNumber: 'INV-2024-001',
          isApplied: false,
        ),
        CreditNote(
          id: '2',
          creditNoteNumber: 'CN-2024-002',
          issueDate: DateTime.now().subtract(const Duration(days: 30)),
          amount: 750000,
          currency: 'IQD',
          status: 'applied',
          reason: 'Pricing adjustment',
          invoiceNumber: 'INV-2024-003',
          isApplied: true,
        ),
      ];
      _isLoading = false;
    });
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'issued':
        return TSHTheme.primary;
      case 'applied':
        return TSHTheme.successGreen;
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
        title: Text(loc.translate('credit_notes')),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _creditNotes.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.note, size: 64, color: TSHTheme.textSecondary),
                      const SizedBox(height: 16),
                      Text(
                        'No credit notes',
                        style: TSHTheme.bodyLarge
                            .copyWith(color: TSHTheme.textSecondary),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadCreditNotes,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _creditNotes.length,
                    itemBuilder: (context, index) {
                      final creditNote = _creditNotes[index];
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
                                    creditNote.creditNoteNumber,
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
                                      color: _getStatusColor(creditNote.status)
                                          .withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(4),
                                      border: Border.all(
                                        color: _getStatusColor(creditNote.status),
                                      ),
                                    ),
                                    child: Text(
                                      creditNote.status.toUpperCase(),
                                      style: TSHTheme.bodySmall.copyWith(
                                        color: _getStatusColor(creditNote.status),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Text(
                                loc.formatCurrency(creditNote.amount),
                                style: TSHTheme.headingMedium.copyWith(
                                  color: TSHTheme.successGreen,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                creditNote.reason,
                                style: TSHTheme.bodyMedium,
                              ),
                              if (creditNote.invoiceNumber != null) ...[
                                const SizedBox(height: 8),
                                Row(
                                  children: [
                                    Icon(
                                      Icons.receipt,
                                      size: 16,
                                      color: TSHTheme.textSecondary,
                                    ),
                                    const SizedBox(width: 4),
                                    Text(
                                      creditNote.invoiceNumber!,
                                      style: TSHTheme.bodySmall,
                                    ),
                                  ],
                                ),
                              ],
                              const SizedBox(height: 8),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    '${creditNote.issueDate.day}/${creditNote.issueDate.month}/${creditNote.issueDate.year}',
                                    style: TSHTheme.bodySmall,
                                  ),
                                  if (creditNote.isApplied)
                                    Row(
                                      children: [
                                        Icon(
                                          Icons.check_circle,
                                          size: 16,
                                          color: TSHTheme.successGreen,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          'Applied',
                                          style: TSHTheme.bodySmall.copyWith(
                                            color: TSHTheme.successGreen,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ],
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
