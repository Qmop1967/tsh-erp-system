import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/security_event.dart';
import '../../services/security_event_service.dart';

class SecurityEventsScreen extends StatefulWidget {
  const SecurityEventsScreen({super.key});

  @override
  State<SecurityEventsScreen> createState() => _SecurityEventsScreenState();
}

class _SecurityEventsScreenState extends State<SecurityEventsScreen> {
  final SecurityEventService _eventService = SecurityEventService();
  List<SecurityEvent> _events = [];
  bool _isLoading = true;
  String? _severityFilter;
  bool? _resolvedFilter;

  @override
  void initState() {
    super.initState();
    _loadEvents();
  }

  Future<void> _loadEvents() async {
    setState(() => _isLoading = true);
    try {
      final events = await _eventService.getSecurityEvents(
        severity: _severityFilter,
        isResolved: _resolvedFilter,
      );
      setState(() {
        _events = events;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading security events: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _resolveEvent(SecurityEvent event) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Resolve Security Event'),
        content: Text('Mark "${event.title ?? event.eventType}" as resolved?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Resolve'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await _eventService.resolveSecurityEvent(event.id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Event resolved successfully'),
              backgroundColor: Colors.green,
            ),
          );
          _loadEvents();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error resolving event: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter Events'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Severity', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  FilterChip(
                    label: const Text('All'),
                    selected: _severityFilter == null,
                    onSelected: (selected) {
                      setState(() => _severityFilter = null);
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                  FilterChip(
                    label: const Text('Low'),
                    selected: _severityFilter == 'low',
                    onSelected: (selected) {
                      setState(() => _severityFilter = 'low');
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                  FilterChip(
                    label: const Text('Medium'),
                    selected: _severityFilter == 'medium',
                    onSelected: (selected) {
                      setState(() => _severityFilter = 'medium');
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                  FilterChip(
                    label: const Text('High'),
                    selected: _severityFilter == 'high',
                    onSelected: (selected) {
                      setState(() => _severityFilter = 'high');
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                  FilterChip(
                    label: const Text('Critical'),
                    selected: _severityFilter == 'critical',
                    onSelected: (selected) {
                      setState(() => _severityFilter = 'critical');
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text('Status', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  FilterChip(
                    label: const Text('All'),
                    selected: _resolvedFilter == null,
                    onSelected: (selected) {
                      setState(() => _resolvedFilter = null);
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                  FilterChip(
                    label: const Text('Unresolved'),
                    selected: _resolvedFilter == false,
                    onSelected: (selected) {
                      setState(() => _resolvedFilter = false);
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                  FilterChip(
                    label: const Text('Resolved'),
                    selected: _resolvedFilter == true,
                    onSelected: (selected) {
                      setState(() => _resolvedFilter = true);
                      Navigator.pop(context);
                      _loadEvents();
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'low':
        return const Color(0xff10b981);
      case 'medium':
        return const Color(0xfff59e0b);
      case 'high':
        return const Color(0xffef4444);
      case 'critical':
        return const Color(0xff991b1b);
      default:
        return Colors.grey;
    }
  }

  IconData _getEventIcon(String eventType) {
    final typeLower = eventType.toLowerCase();
    if (typeLower.contains('login') || typeLower.contains('authentication')) {
      return Icons.login;
    } else if (typeLower.contains('access') || typeLower.contains('unauthorized')) {
      return Icons.block;
    } else if (typeLower.contains('suspicious')) {
      return Icons.warning_amber_rounded;
    } else if (typeLower.contains('malware') || typeLower.contains('virus')) {
      return Icons.bug_report;
    } else {
      return Icons.shield_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xffef4444),
        foregroundColor: Colors.white,
        title: const Text(
          'Security Events',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
            tooltip: 'Filter',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadEvents,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _events.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.shield_outlined, size: 64, color: Colors.grey[400]),
                      const SizedBox(height: 16),
                      Text(
                        'No security events found',
                        style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadEvents,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _events.length,
                    itemBuilder: (context, index) {
                      final event = _events[index];
                      final severityColor = _getSeverityColor(event.severity);
                      final eventIcon = _getEventIcon(event.eventType);

                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.grey.withOpacity(0.1),
                              blurRadius: 10,
                              offset: const Offset(0, 2),
                            ),
                          ],
                          border: Border(
                            left: BorderSide(
                              color: severityColor,
                              width: 4,
                            ),
                          ),
                        ),
                        child: ExpansionTile(
                          leading: Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              color: severityColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              eventIcon,
                              color: severityColor,
                              size: 28,
                            ),
                          ),
                          title: Text(
                            event.title ?? event.eventType,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Color(0xff1f2937),
                            ),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: severityColor.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Icon(
                                          Icons.warning_amber_rounded,
                                          size: 14,
                                          color: severityColor,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          event.severity.toUpperCase(),
                                          style: TextStyle(
                                            fontSize: 11,
                                            fontWeight: FontWeight.bold,
                                            color: severityColor,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: event.isResolved
                                          ? const Color(0xff10b981).withOpacity(0.1)
                                          : const Color(0xfff59e0b).withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      event.isResolved ? 'RESOLVED' : 'ACTIVE',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: event.isResolved
                                            ? const Color(0xff10b981)
                                            : const Color(0xfff59e0b),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              if (event.createdAt != null) ...[
                                const SizedBox(height: 8),
                                Row(
                                  children: [
                                    Icon(Icons.access_time, size: 14, color: Colors.grey[500]),
                                    const SizedBox(width: 4),
                                    Text(
                                      DateFormat('MMM dd, yyyy HH:mm').format(event.createdAt!),
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ],
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  if (event.description != null) ...[
                                    Text(
                                      event.description!,
                                      style: TextStyle(
                                        fontSize: 14,
                                        color: Colors.grey[700],
                                        height: 1.5,
                                      ),
                                    ),
                                    const SizedBox(height: 16),
                                  ],
                                  _InfoRow(
                                    icon: Icons.category_outlined,
                                    label: 'Event Type',
                                    value: event.eventType,
                                  ),
                                  if (event.ipAddress != null) ...[
                                    const SizedBox(height: 8),
                                    _InfoRow(
                                      icon: Icons.location_on_outlined,
                                      label: 'IP Address',
                                      value: event.ipAddress!,
                                    ),
                                  ],
                                  if (event.resolvedAt != null) ...[
                                    const SizedBox(height: 8),
                                    _InfoRow(
                                      icon: Icons.check_circle_outline,
                                      label: 'Resolved At',
                                      value: DateFormat('MMM dd, yyyy HH:mm').format(event.resolvedAt!),
                                    ),
                                  ],
                                  if (!event.isResolved) ...[
                                    const SizedBox(height: 16),
                                    SizedBox(
                                      width: double.infinity,
                                      child: ElevatedButton.icon(
                                        onPressed: () => _resolveEvent(event),
                                        icon: const Icon(Icons.check_circle, size: 18),
                                        label: const Text('Mark as Resolved'),
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: const Color(0xff10b981),
                                          foregroundColor: Colors.white,
                                          padding: const EdgeInsets.symmetric(vertical: 12),
                                        ),
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: Colors.grey[600]),
        const SizedBox(width: 8),
        Text(
          '$label: ',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              color: Color(0xff1f2937),
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}
