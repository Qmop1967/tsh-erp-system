class AccountStatement {
  final DateTime startDate;
  final DateTime endDate;
  final double openingBalance;
  final double closingBalance;
  final List<StatementTransaction> transactions;

  AccountStatement({
    required this.startDate,
    required this.endDate,
    required this.openingBalance,
    required this.closingBalance,
    required this.transactions,
  });

  double get totalDebits =>
      transactions.where((t) => t.type == 'debit').fold(0.0, (sum, t) => sum + t.amount);

  double get totalCredits =>
      transactions.where((t) => t.type == 'credit').fold(0.0, (sum, t) => sum + t.amount);

  factory AccountStatement.fromJson(Map<String, dynamic> json) {
    return AccountStatement(
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      openingBalance: (json['opening_balance'] ?? 0.0).toDouble(),
      closingBalance: (json['closing_balance'] ?? 0.0).toDouble(),
      transactions: (json['transactions'] as List<dynamic>?)
              ?.map((t) => StatementTransaction.fromJson(t))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
      'opening_balance': openingBalance,
      'closing_balance': closingBalance,
      'transactions': transactions.map((t) => t.toJson()).toList(),
    };
  }
}

class StatementTransaction {
  final String id;
  final DateTime date;
  final String type; // debit or credit
  final String description;
  final double amount;
  final double balance;
  final String? referenceNumber;

  StatementTransaction({
    required this.id,
    required this.date,
    required this.type,
    required this.description,
    required this.amount,
    required this.balance,
    this.referenceNumber,
  });

  factory StatementTransaction.fromJson(Map<String, dynamic> json) {
    return StatementTransaction(
      id: json['id'].toString(),
      date: DateTime.parse(json['date']),
      type: json['type'] ?? 'debit',
      description: json['description'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      balance: (json['balance'] ?? 0.0).toDouble(),
      referenceNumber: json['reference_number'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'type': type,
      'description': description,
      'amount': amount,
      'balance': balance,
      'reference_number': referenceNumber,
    };
  }
}
