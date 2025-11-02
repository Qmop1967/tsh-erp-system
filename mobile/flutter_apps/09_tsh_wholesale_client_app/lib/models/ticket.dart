class SupportTicket {
  final String id;
  final String subject;
  final String description;
  final String status; // open, in_progress, resolved, closed
  final String priority; // low, medium, high, urgent
  final DateTime createdAt;
  final DateTime? updatedAt;
  final List<TicketMessage> messages;

  SupportTicket({
    required this.id,
    required this.subject,
    required this.description,
    required this.status,
    required this.priority,
    required this.createdAt,
    this.updatedAt,
    this.messages = const [],
  });

  factory SupportTicket.fromJson(Map<String, dynamic> json) {
    return SupportTicket(
      id: json['id'].toString(),
      subject: json['subject'] ?? '',
      description: json['description'] ?? '',
      status: json['status'] ?? 'open',
      priority: json['priority'] ?? 'medium',
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      messages: (json['messages'] as List<dynamic>?)
              ?.map((m) => TicketMessage.fromJson(m))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'subject': subject,
      'description': description,
      'status': status,
      'priority': priority,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'messages': messages.map((m) => m.toJson()).toList(),
    };
  }
}

class TicketMessage {
  final String id;
  final String ticketId;
  final String message;
  final bool isStaff;
  final DateTime createdAt;

  TicketMessage({
    required this.id,
    required this.ticketId,
    required this.message,
    required this.isStaff,
    required this.createdAt,
  });

  factory TicketMessage.fromJson(Map<String, dynamic> json) {
    return TicketMessage(
      id: json['id'].toString(),
      ticketId: json['ticket_id'].toString(),
      message: json['message'] ?? '',
      isStaff: json['is_staff'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'ticket_id': ticketId,
      'message': message,
      'is_staff': isStaff,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
