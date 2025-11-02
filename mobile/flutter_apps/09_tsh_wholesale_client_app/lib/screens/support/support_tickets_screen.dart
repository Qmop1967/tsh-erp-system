import 'package:flutter/material.dart';
import '../../models/ticket.dart';
import '../../utils/tsh_theme.dart';
import '../../utils/tsh_localizations.dart';

class SupportTicketsScreen extends StatefulWidget {
  const SupportTicketsScreen({super.key});

  @override
  State<SupportTicketsScreen> createState() => _SupportTicketsScreenState();
}

class _SupportTicketsScreenState extends State<SupportTicketsScreen> {
  List<SupportTicket> _tickets = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadTickets();
  }

  Future<void> _loadTickets() async {
    setState(() => _isLoading = true);

    // Mock data - Replace with actual API call
    await Future.delayed(const Duration(seconds: 1));

    setState(() {
      _tickets = [
        SupportTicket(
          id: '1',
          subject: 'Issue with order #12345',
          description: 'Some products were damaged during delivery',
          status: 'open',
          priority: 'high',
          createdAt: DateTime.now().subtract(const Duration(days: 2)),
          messages: [],
        ),
        SupportTicket(
          id: '2',
          subject: 'Question about payment terms',
          description: 'Can I extend the payment period?',
          status: 'in_progress',
          priority: 'medium',
          createdAt: DateTime.now().subtract(const Duration(days: 5)),
          updatedAt: DateTime.now().subtract(const Duration(days: 1)),
          messages: [],
        ),
        SupportTicket(
          id: '3',
          subject: 'Invoice discrepancy',
          description: 'Invoice INV-2024-001 shows incorrect total',
          status: 'resolved',
          priority: 'high',
          createdAt: DateTime.now().subtract(const Duration(days: 10)),
          updatedAt: DateTime.now().subtract(const Duration(days: 3)),
          messages: [],
        ),
      ];
      _isLoading = false;
    });
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'open':
        return TSHTheme.warningOrange;
      case 'in_progress':
        return TSHTheme.primary;
      case 'resolved':
        return TSHTheme.successGreen;
      case 'closed':
        return TSHTheme.textSecondary;
      default:
        return TSHTheme.textSecondary;
    }
  }

  Color _getPriorityColor(String priority) {
    switch (priority) {
      case 'urgent':
        return TSHTheme.errorRed;
      case 'high':
        return TSHTheme.warningOrange;
      case 'medium':
        return TSHTheme.primary;
      case 'low':
        return TSHTheme.textSecondary;
      default:
        return TSHTheme.textSecondary;
    }
  }

  void _showCreateTicketDialog() {
    final subjectController = TextEditingController();
    final descriptionController = TextEditingController();
    String selectedPriority = 'medium';

    showDialog(
      context: context,
      builder: (context) {
        final loc = TSHLocalizations.of(context)!;
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: Text(loc.translate('create_ticket')),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TextField(
                      controller: subjectController,
                      decoration: InputDecoration(
                        labelText: loc.translate('ticket_subject'),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: descriptionController,
                      decoration: InputDecoration(
                        labelText: loc.translate('ticket_description'),
                        border: const OutlineInputBorder(),
                      ),
                      maxLines: 4,
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      value: selectedPriority,
                      decoration: InputDecoration(
                        labelText: loc.translate('priority'),
                        border: const OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'low', child: Text('Low')),
                        DropdownMenuItem(value: 'medium', child: Text('Medium')),
                        DropdownMenuItem(value: 'high', child: Text('High')),
                        DropdownMenuItem(value: 'urgent', child: Text('Urgent')),
                      ],
                      onChanged: (value) {
                        setDialogState(() => selectedPriority = value!);
                      },
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text(loc.translate('cancel')),
                ),
                ElevatedButton(
                  onPressed: () {
                    // TODO: Create ticket via API
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(loc.translate('success'))),
                    );
                  },
                  child: Text(loc.translate('submit')),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final loc = TSHLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(loc.translate('support_tickets')),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showCreateTicketDialog,
        icon: const Icon(Icons.add),
        label: Text(loc.translate('create_ticket')),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _tickets.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.support_agent,
                          size: 64, color: TSHTheme.textSecondary),
                      const SizedBox(height: 16),
                      Text(
                        'No support tickets',
                        style: TSHTheme.bodyLarge
                            .copyWith(color: TSHTheme.textSecondary),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadTickets,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _tickets.length,
                    itemBuilder: (context, index) {
                      final ticket = _tickets[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16),
                          title: Text(
                            ticket.subject,
                            style: TSHTheme.bodyLarge.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 8),
                              Text(
                                ticket.description,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: _getStatusColor(ticket.status)
                                          .withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(4),
                                      border: Border.all(
                                        color: _getStatusColor(ticket.status),
                                      ),
                                    ),
                                    child: Text(
                                      ticket.status.toUpperCase(),
                                      style: TSHTheme.bodySmall.copyWith(
                                        color: _getStatusColor(ticket.status),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: _getPriorityColor(ticket.priority)
                                          .withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      ticket.priority.toUpperCase(),
                                      style: TSHTheme.bodySmall.copyWith(
                                        color:
                                            _getPriorityColor(ticket.priority),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  const Spacer(),
                                  Text(
                                    '${ticket.createdAt.day}/${ticket.createdAt.month}/${ticket.createdAt.year}',
                                    style: TSHTheme.bodySmall,
                                  ),
                                ],
                              ),
                            ],
                          ),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () {
                            // Navigate to ticket details
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Ticket details coming soon'),
                              ),
                            );
                          },
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
