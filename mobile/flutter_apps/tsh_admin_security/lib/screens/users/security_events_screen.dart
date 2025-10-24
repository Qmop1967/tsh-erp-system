import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/security_event.dart';
import '../../services/security_event_service.dart';

/// Security Events Screen
/// Displays security events and alerts with filtering and review capabilities
class SecurityEventsScreen extends StatefulWidget {
  final int? userId;

  const SecurityEventsScreen({Key? key, this.userId}) : super(key: key);

  @override
  State<SecurityEventsScreen> createState() => _SecurityEventsScreenState();
}

class _SecurityEventsScreenState extends State<SecurityEventsScreen> {
  final SecurityEventService _securityEventService = SecurityEventService();
  List<SecurityEvent> _securityEvents = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  int _currentPage = 1;
  bool _hasMore = true;

  // Filters
  String? _selectedEventType;
  String? _selectedSeverity;
  bool? _isResolvedFilter;
  final ScrollController _scrollController = ScrollController();

  final List<String> _eventTypes = [
    'login_attempt',
    'password_change',
    '2fa_event',
    'permission_change',
    'suspicious_activity',
  ];

  final List<String> _severityLevels = ['info', 'warning', 'critical'];

  @override
  void initState() {
    super.initState();
    _loadSecurityEvents();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      if (!_isLoadingMore && _hasMore) {
        _loadMoreEvents();
      }
    }
  }

  Future<void> _loadSecurityEvents() async {
    setState(() {
      _isLoading = true;
      _currentPage = 1;
      _hasMore = true;
    });

    try {
      final events = await _securityEventService.getSecurityEvents(
        userId: widget.userId,
        eventType: _selectedEventType,
        severity: _selectedSeverity,
        isResolved: _isResolvedFilter,
        page: _currentPage,
        pageSize: 20,
      );

      setState(() {
        _securityEvents = events;
        _isLoading = false;
        _hasMore = events.length >= 20;
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

  Future<void> _loadMoreEvents() async {
    if (_isLoadingMore) return;

    setState(() {
      _isLoadingMore = true;
      _currentPage++;
    });

    try {
      final events = await _securityEventService.getSecurityEvents(
        userId: widget.userId,
        eventType: _selectedEventType,
        severity: _selectedSeverity,
        isResolved: _isResolvedFilter,
        page: _currentPage,
        pageSize: 20,
      );

      setState(() {
        _securityEvents.addAll(events);
        _isLoadingMore = false;
        _hasMore = events.length >= 20;
      });
    } catch (e) {
      setState(() {
        _isLoadingMore = false;
        _currentPage--;
      });
    }
  }

  Future<void> _markAsReviewed(SecurityEvent event) async {
    try {
      await _securityEventService.resolveSecurityEvent(event.id);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Event marked as reviewed'),
          backgroundColor: Color(0xFF10B981),
        ),
      );
      _loadSecurityEvents();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error marking event as reviewed: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _clearFilters() {
    setState(() {
      _selectedEventType = null;
      _selectedSeverity = null;
      _isResolvedFilter = null;
    });
    _loadSecurityEvents();
  }

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Filter Security Events',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Event Type Filter
              const Text(
                'Event Type',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildFilterChip(
                    'All',
                    _selectedEventType == null,
                    () {
                      setModalState(() => _selectedEventType = null);
                      setState(() => _selectedEventType = null);
                    },
                    Colors.grey,
                  ),
                  ..._eventTypes.map((type) => _buildFilterChip(
                        _formatEventType(type),
                        _selectedEventType == type,
                        () {
                          setModalState(() => _selectedEventType = type);
                          setState(() => _selectedEventType = type);
                        },
                        const Color(0xFF2563EB),
                      )),
                ],
              ),

              const SizedBox(height: 20),

              // Severity Filter
              const Text(
                'Severity',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _severityLevels.map((severity) {
                  return _buildFilterChip(
                    severity.toUpperCase(),
                    _selectedSeverity == severity,
                    () {
                      setModalState(() => _selectedSeverity = severity);
                      setState(() => _selectedSeverity = severity);
                    },
                    _getSeverityColor(severity),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              // Status Filter
              const Text(
                'Status',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildFilterChip(
                    'All',
                    _isResolvedFilter == null,
                    () {
                      setModalState(() => _isResolvedFilter = null);
                      setState(() => _isResolvedFilter = null);
                    },
                    Colors.grey,
                  ),
                  _buildFilterChip(
                    'Pending',
                    _isResolvedFilter == false,
                    () {
                      setModalState(() => _isResolvedFilter = false);
                      setState(() => _isResolvedFilter = false);
                    },
                    const Color(0xFFF59E0B),
                  ),
                  _buildFilterChip(
                    'Reviewed',
                    _isResolvedFilter == true,
                    () {
                      setModalState(() => _isResolvedFilter = true);
                      setState(() => _isResolvedFilter = true);
                    },
                    const Color(0xFF10B981),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Action Buttons
              Row(
                children: [
                  if (_selectedEventType != null ||
                      _selectedSeverity != null ||
                      _isResolvedFilter != null) ...[
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () {
                          Navigator.pop(context);
                          _clearFilters();
                        },
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          side: const BorderSide(color: Colors.red),
                          foregroundColor: Colors.red,
                        ),
                        child: const Text('Clear'),
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context);
                        _loadSecurityEvents();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text(
                        'Apply Filters',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFilterChip(
    String label,
    bool isSelected,
    VoidCallback onTap,
    Color color,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.1) : Colors.grey[100],
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? color : Colors.grey[300]!,
            width: 1.5,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: isSelected ? color : Colors.grey[700],
          ),
        ),
      ),
    );
  }

  void _showEventDetails(SecurityEvent event) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),

              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _getSeverityColor(event.severity).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      _getEventIcon(event.eventType),
                      color: _getSeverityColor(event.severity),
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          event.title ?? _formatEventType(event.eventType),
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1F2937),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getSeverityColor(event.severity)
                                .withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            event.severity.toUpperCase(),
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: _getSeverityColor(event.severity),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              Expanded(
                child: ListView(
                  controller: scrollController,
                  children: [
                    if (event.description != null) ...[
                      const Text(
                        'Description',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF6B7280),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        event.description!,
                        style: const TextStyle(
                          fontSize: 15,
                          color: Color(0xFF1F2937),
                        ),
                      ),
                      const SizedBox(height: 20),
                    ],

                    _buildDetailRow(
                      Icons.category,
                      'Event Type',
                      _formatEventType(event.eventType),
                    ),
                    const SizedBox(height: 12),

                    if (event.createdAt != null)
                      _buildDetailRow(
                        Icons.access_time,
                        'Occurred At',
                        DateFormat('MMM dd, yyyy • hh:mm a')
                            .format(event.createdAt!),
                      ),
                    const SizedBox(height: 12),

                    if (event.ipAddress != null)
                      _buildDetailRow(
                        Icons.location_on,
                        'IP Address',
                        event.ipAddress!,
                      ),
                    const SizedBox(height: 12),

                    if (event.sessionId != null)
                      _buildDetailRow(
                        Icons.vpn_key,
                        'Session ID',
                        event.sessionId!,
                      ),
                    const SizedBox(height: 12),

                    _buildDetailRow(
                      event.isResolved ? Icons.check_circle : Icons.pending,
                      'Status',
                      event.isResolved ? 'Reviewed' : 'Pending Review',
                    ),

                    if (event.isResolved && event.resolvedAt != null) ...[
                      const SizedBox(height: 12),
                      _buildDetailRow(
                        Icons.done_all,
                        'Reviewed At',
                        DateFormat('MMM dd, yyyy • hh:mm a')
                            .format(event.resolvedAt!),
                      ),
                    ],
                  ],
                ),
              ),

              if (!event.isResolved) ...[
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      _markAsReviewed(event);
                    },
                    icon: const Icon(Icons.check_circle, color: Colors.white),
                    label: const Text(
                      'Mark as Reviewed',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: Colors.grey[600]),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF1F2937),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFF2563EB),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Security Events',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list, color: Colors.white),
            onPressed: _showFilterSheet,
            tooltip: 'Filter',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadSecurityEvents,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _securityEvents.isEmpty
                ? _buildEmptyState()
                : Column(
                    children: [
                      // Active Filters Display
                      if (_selectedEventType != null ||
                          _selectedSeverity != null ||
                          _isResolvedFilter != null)
                        _buildActiveFilters(),

                      // Events List
                      Expanded(
                        child: ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.all(16),
                          itemCount: _securityEvents.length + 1,
                          itemBuilder: (context, index) {
                            if (index == _securityEvents.length) {
                              return _isLoadingMore
                                  ? const Center(
                                      child: Padding(
                                        padding: EdgeInsets.all(16.0),
                                        child: CircularProgressIndicator(),
                                      ),
                                    )
                                  : const SizedBox.shrink();
                            }
                            return _buildEventCard(_securityEvents[index]);
                          },
                        ),
                      ),
                    ],
                  ),
      ),
    );
  }

  Widget _buildActiveFilters() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          const Text(
            'Active Filters:',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: Color(0xFF6B7280),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (_selectedEventType != null)
                  _buildActiveFilterChip(
                    _formatEventType(_selectedEventType!),
                    () => setState(() {
                      _selectedEventType = null;
                      _loadSecurityEvents();
                    }),
                  ),
                if (_selectedSeverity != null)
                  _buildActiveFilterChip(
                    _selectedSeverity!.toUpperCase(),
                    () => setState(() {
                      _selectedSeverity = null;
                      _loadSecurityEvents();
                    }),
                  ),
                if (_isResolvedFilter != null)
                  _buildActiveFilterChip(
                    _isResolvedFilter! ? 'Reviewed' : 'Pending',
                    () => setState(() {
                      _isResolvedFilter = null;
                      _loadSecurityEvents();
                    }),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActiveFilterChip(String label, VoidCallback onRemove) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF2563EB).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2563EB)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Color(0xFF2563EB),
            ),
          ),
          const SizedBox(width: 4),
          InkWell(
            onTap: onRemove,
            child: const Icon(
              Icons.close,
              size: 14,
              color: Color(0xFF2563EB),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.security,
              size: 64,
              color: Colors.grey[400],
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'No Security Events',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[700],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'No security events found for the selected filters',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEventCard(SecurityEvent event) {
    final severityColor = _getSeverityColor(event.severity);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: severityColor.withOpacity(0.3),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: severityColor.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => _showEventDetails(event),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Icon
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: severityColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getEventIcon(event.eventType),
                    color: severityColor,
                    size: 24,
                  ),
                ),

                const SizedBox(width: 16),

                // Event Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              event.title ?? _formatEventType(event.eventType),
                              style: const TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1F2937),
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: severityColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Text(
                              event.severity.toUpperCase(),
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: severityColor,
                              ),
                            ),
                          ),
                        ],
                      ),

                      if (event.description != null) ...[
                        const SizedBox(height: 6),
                        Text(
                          event.description!,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],

                      const SizedBox(height: 8),

                      Row(
                        children: [
                          Icon(
                            Icons.access_time,
                            size: 12,
                            color: Colors.grey[500],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            event.createdAt != null
                                ? DateFormat('MMM dd, yyyy • hh:mm a')
                                    .format(event.createdAt!)
                                : 'Unknown',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey[600],
                            ),
                          ),

                          const SizedBox(width: 12),

                          if (event.ipAddress != null) ...[
                            Icon(
                              Icons.location_on,
                              size: 12,
                              color: Colors.grey[500],
                            ),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(
                                event.ipAddress!,
                                style: TextStyle(
                                  fontSize: 11,
                                  color: Colors.grey[600],
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(width: 8),

                // Status Indicator
                Column(
                  children: [
                    Icon(
                      event.isResolved ? Icons.check_circle : Icons.pending,
                      color: event.isResolved
                          ? const Color(0xFF10B981)
                          : const Color(0xFFF59E0B),
                      size: 24,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      event.isResolved ? 'Reviewed' : 'Pending',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        color: event.isResolved
                            ? const Color(0xFF10B981)
                            : const Color(0xFFF59E0B),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'info':
        return const Color(0xFF2563EB); // Blue
      case 'warning':
        return const Color(0xFFF59E0B); // Orange
      case 'critical':
        return const Color(0xFFEF4444); // Red
      default:
        return Colors.grey;
    }
  }

  IconData _getEventIcon(String eventType) {
    switch (eventType.toLowerCase()) {
      case 'login_attempt':
        return Icons.login;
      case 'password_change':
        return Icons.lock_reset;
      case '2fa_event':
        return Icons.verified_user;
      case 'permission_change':
        return Icons.admin_panel_settings;
      case 'suspicious_activity':
        return Icons.warning;
      default:
        return Icons.info;
    }
  }

  String _formatEventType(String eventType) {
    return eventType
        .split('_')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }
}
