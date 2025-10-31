import 'account_type.dart';

/// Journal Entry Model
/// نموذج القيد اليومي

class JournalEntry {
  final int? id;
  final String entryNumber;
  final DateTime entryDate;
  final String? reference;
  final String? descriptionAr;
  final String? descriptionEn;
  final double totalDebit;
  final double totalCredit;
  final String status;
  final List<JournalLine> lines;
  final DateTime? createdAt;

  JournalEntry({
    this.id,
    required this.entryNumber,
    required this.entryDate,
    this.reference,
    this.descriptionAr,
    this.descriptionEn,
    required this.totalDebit,
    required this.totalCredit,
    required this.status,
    required this.lines,
    this.createdAt,
  });

  bool get isBalanced => (totalDebit - totalCredit).abs() < 0.01;

  factory JournalEntry.fromJson(Map<String, dynamic> json) {
    return JournalEntry(
      id: json['id'],
      entryNumber: json['entry_number'],
      entryDate: DateTime.parse(json['entry_date']),
      reference: json['reference'],
      descriptionAr: json['description_ar'],
      descriptionEn: json['description_en'],
      totalDebit: double.parse(json['total_debit'].toString()),
      totalCredit: double.parse(json['total_credit'].toString()),
      status: json['status'],
      lines: (json['journal_lines'] as List?)
              ?.map((line) => JournalLine.fromJson(line))
              .toList() ??
          [],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'entry_number': entryNumber,
      'entry_date': entryDate.toIso8601String(),
      'reference': reference,
      'description_ar': descriptionAr,
      'description_en': descriptionEn,
      'total_debit': totalDebit,
      'total_credit': totalCredit,
      'status': status,
      'journal_lines': lines.map((line) => line.toJson()).toList(),
    };
  }
}

/// Journal Line Model
/// نموذج سطر القيد

class JournalLine {
  final int? id;
  final int accountId;
  final String? accountName;
  final String? accountNameAr;
  final AccountType? accountType;
  final String? descriptionAr;
  final String? descriptionEn;
  final double debitAmount;
  final double creditAmount;
  final int lineNumber;

  JournalLine({
    this.id,
    required this.accountId,
    this.accountName,
    this.accountNameAr,
    this.accountType,
    this.descriptionAr,
    this.descriptionEn,
    required this.debitAmount,
    required this.creditAmount,
    required this.lineNumber,
  });

  bool get isDebit => debitAmount > 0;
  bool get isCredit => creditAmount > 0;
  double get amount => isDebit ? debitAmount : creditAmount;

  factory JournalLine.fromJson(Map<String, dynamic> json) {
    return JournalLine(
      id: json['id'],
      accountId: json['account_id'],
      accountName: json['account_name'],
      accountNameAr: json['account_name_ar'],
      accountType: json['account_type'] != null
          ? accountTypeFromString(json['account_type'])
          : null,
      descriptionAr: json['description_ar'],
      descriptionEn: json['description_en'],
      debitAmount: double.parse(json['debit_amount'].toString()),
      creditAmount: double.parse(json['credit_amount'].toString()),
      lineNumber: json['line_number'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'account_id': accountId,
      'account_name': accountName,
      'account_name_ar': accountNameAr,
      'account_type': accountType?.name,
      'description_ar': descriptionAr,
      'description_en': descriptionEn,
      'debit_amount': debitAmount,
      'credit_amount': creditAmount,
      'line_number': lineNumber,
    };
  }
}

/// Journal Entry Status
enum JournalEntryStatus {
  DRAFT,
  POSTED,
  CANCELLED
}

extension JournalEntryStatusExtension on JournalEntryStatus {
  String get nameAr {
    switch (this) {
      case JournalEntryStatus.DRAFT:
        return 'مسودة';
      case JournalEntryStatus.POSTED:
        return 'مرحل';
      case JournalEntryStatus.CANCELLED:
        return 'ملغي';
    }
  }

  String get nameEn {
    switch (this) {
      case JournalEntryStatus.DRAFT:
        return 'Draft';
      case JournalEntryStatus.POSTED:
        return 'Posted';
      case JournalEntryStatus.CANCELLED:
        return 'Cancelled';
    }
  }

  int get colorValue {
    switch (this) {
      case JournalEntryStatus.DRAFT:
        return 0xFFFFA726; // Orange
      case JournalEntryStatus.POSTED:
        return 0xFF66BB6A; // Green
      case JournalEntryStatus.CANCELLED:
        return 0xFFEF5350; // Red
    }
  }
}
