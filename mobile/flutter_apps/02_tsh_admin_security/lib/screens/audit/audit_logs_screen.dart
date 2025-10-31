import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/audit_log.dart';
import '../../services/audit_service.dart';

class AuditLogsScreen extends StatefulWidget {
  const AuditLogsScreen({super.key});

  @override
  State<AuditLogsScreen> createState() => _AuditLogsScreenState();
}

class _AuditLogsScreenState extends State<AuditLogsScreen> {
  final AuditService _auditService = AuditService();
  List<AuditLog> _logs = [];
  bool _isLoading = true;
  DateTime? _startDate;
  DateTime? _endDate;

  @override
  void initState() {
    super.initState();
    _loadLogs();
  }

  Future<void> _loadLogs() async {
    setState(() => _isLoading = true);
    try {
      final logs = await _auditService.getAuditLogs(
        startDate: _startDate,
        endDate: _endDate,
      );
      setState(() {
        _logs = logs;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading audit logs: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _selectDateRange() async {
    final DateTimeRange? picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      initialDateRange: _startDate != null && _endDate != null
          ? DateTimeRange(start: _startDate!, end: _endDate!)
          : null,
    );

    if (picked != null) {
      setState(() {
        _startDate = picked.start;
        _endDate = picked.end;
      });
      _loadLogs();
    }
  }

  void _clearDateFilter() {
    setState(() {
      _startDate = null;
      _endDate = null;
    });
    _loadLogs();
  }

  Color _getActionColor(String action) {
    final actionLower = action.toLowerCase();
    if (actionLower.contains('create')) {
      return const Color(0xff10b981);
    } else if (actionLower.contains('update') || actionLower.contains('edit')) {
      return const Color(0xff06b6d4);
    } else if (actionLower.contains('delete') || actionLower.contains('remove')) {
      return const Color(0xffef4444);
    } else if (actionLower.contains('login')) {
      return const Color(0xff7c3aed);
    } else {
      return const Color(0xfff59e0b);
    }
  }

  IconData _getActionIcon(String action) {
    final actionLower = action.toLowerCase();
    if (actionLower.contains('create')) {
      return Icons.add_circle_outline;
    } else if (actionLower.contains('update') || actionLower.contains('edit')) {
      return Icons.edit_outlined;
    } else if (actionLower.contains('delete') || actionLower.contains('remove')) {
      return Icons.delete_outline;
    } else if (actionLower.contains('login')) {
      return Icons.login;
    } else if (actionLower.contains('logout')) {
      return Icons.logout;
    } else {
      return Icons.info_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xfff59e0b),
        foregroundColor: Colors.white,
        title: const Text(
          'Audit Logs',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          if (_startDate != null || _endDate != null)
            IconButton(
              icon: const Icon(Icons.clear),
              onPressed: _clearDateFilter,
              tooltip: 'Clear Filter',
            ),
          IconButton(
            icon: const Icon(Icons.date_range),
            onPressed: _selectDateRange,
            tooltip: 'Filter by Date',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadLogs,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          // Date Range Filter Display
          if (_startDate != null || _endDate != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: const Color(0xfff59e0b).withOpacity(0.1),
              child: Row(
                children: [
                  const Icon(Icons.filter_list, size: 20, color: Color(0xfff59e0b)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Filtered: ${_startDate != null ? DateFormat('MMM dd, yyyy').format(_startDate!) : 'Start'} - ${_endDate != null ? DateFormat('MMM dd, yyyy').format(_endDate!) : 'End'}',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xfff59e0b),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Logs List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _logs.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.history_outlined, size: 64, color: Colors.grey[400]),
                            const SizedBox(height: 16),
                            Text(
                              'No audit logs found',
                              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadLogs,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _logs.length,
                          itemBuilder: (context, index) {
                            final log = _logs[index];
                            final actionColor = _getActionColor(log.action);
                            final actionIcon = _getActionIcon(log.action);

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
                                    color: actionColor,
                                    width: 4,
                                  ),
                                ),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(16),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    // Action Icon
                                    Container(
                                      width: 40,
                                      height: 40,
                                      decoration: BoxDecoration(
                                        color: actionColor.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                      child: Icon(
                                        actionIcon,
                                        color: actionColor,
                                        size: 22,
                                      ),
                                    ),
                                    const SizedBox(width: 16),

                                    // Log Details
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            children: [
                                              Container(
                                                padding: const EdgeInsets.symmetric(
                                                  horizontal: 8,
                                                  vertical: 4,
                                                ),
                                                decoration: BoxDecoration(
                                                  color: actionColor.withOpacity(0.1),
                                                  borderRadius: BorderRadius.circular(6),
                                                ),
                                                child: Text(
                                                  log.action.toUpperCase(),
                                                  style: TextStyle(
                                                    fontSize: 11,
                                                    fontWeight: FontWeight.bold,
                                                    color: actionColor,
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
                                                  color: Colors.grey.withOpacity(0.1),
                                                  borderRadius: BorderRadius.circular(6),
                                                ),
                                                child: Text(
                                                  log.resourceType,
                                                  style: TextStyle(
                                                    fontSize: 11,
                                                    fontWeight: FontWeight.w600,
                                                    color: Colors.grey[700],
                                                  ),
                                                ),
                                              ),
                                            ],
                                          ),
                                          if (log.description != null) ...[
                                            const SizedBox(height: 8),
                                            Text(
                                              log.description!,
                                              style: const TextStyle(
                                                fontSize: 14,
                                                color: Color(0xff1f2937),
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                          ],
                                          const SizedBox(height: 8),
                                          Row(
                                            children: [
                                              Icon(Icons.access_time, size: 14, color: Colors.grey[500]),
                                              const SizedBox(width: 4),
                                              Text(
                                                log.timestamp != null
                                                    ? DateFormat('MMM dd, yyyy HH:mm').format(log.timestamp!)
                                                    : 'Unknown',
                                                style: TextStyle(
                                                  fontSize: 12,
                                                  color: Colors.grey[600],
                                                ),
                                              ),
                                              if (log.ipAddress != null) ...[
                                                const SizedBox(width: 16),
                                                Icon(Icons.location_on_outlined, size: 14, color: Colors.grey[500]),
                                                const SizedBox(width: 4),
                                                Text(
                                                  log.ipAddress!,
                                                  style: TextStyle(
                                                    fontSize: 12,
                                                    color: Colors.grey[600],
                                                  ),
                                                ),
                                              ],
                                            ],
                                          ),
                                          if (log.resourceId != null) ...[
                                            const SizedBox(height: 4),
                                            Text(
                                              'Resource ID: ${log.resourceId}',
                                              style: TextStyle(
                                                fontSize: 11,
                                                color: Colors.grey[500],
                                              ),
                                            ),
                                          ],
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}
