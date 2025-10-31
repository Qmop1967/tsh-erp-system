/// Dashboard Statistics Model
/// نموذج إحصائيات لوحة التحكم

class DashboardStats {
  // Account Type Totals (لكل نوع حساب)
  final double totalAssets;       // إجمالي الأصول
  final double totalLiabilities;  // إجمالي الخصوم
  final double totalEquity;       // إجمالي حقوق الملكية
  final double totalRevenue;      // إجمالي الإيرادات
  final double totalExpenses;     // إجمالي المصروفات

  // Financial Indicators (مؤشرات مالية)
  final double netProfit;         // صافي الربح
  final double workingCapital;    // رأس المال العامل
  final double cashBalance;       // رصيد النقدية

  // Receivables & Payables
  final double totalReceivables;  // إجمالي المدينين
  final double totalPayables;     // إجمالي الدائنين

  // Stock & Inventory
  final double stockValue;        // قيمة المخزون

  // Journal Entries Stats
  final int totalJournalEntries;  // عدد القيود
  final int draftEntries;         // القيود بحالة مسودة
  final int postedEntries;        // القيود المرحلة

  DashboardStats({
    this.totalAssets = 0,
    this.totalLiabilities = 0,
    this.totalEquity = 0,
    this.totalRevenue = 0,
    this.totalExpenses = 0,
    this.netProfit = 0,
    this.workingCapital = 0,
    this.cashBalance = 0,
    this.totalReceivables = 0,
    this.totalPayables = 0,
    this.stockValue = 0,
    this.totalJournalEntries = 0,
    this.draftEntries = 0,
    this.postedEntries = 0,
  });

  // التحقق من المعادلة المحاسبية
  // Assets = Liabilities + Equity
  bool get isAccountingEquationBalanced {
    final leftSide = totalAssets;
    final rightSide = totalLiabilities + totalEquity;
    return (leftSide - rightSide).abs() < 0.01;
  }

  // نسبة الأصول إلى الخصوم
  double get assetsToLiabilitiesRatio {
    if (totalLiabilities == 0) return 0;
    return totalAssets / totalLiabilities;
  }

  // نسبة السيولة السريعة
  double get quickRatio {
    if (totalLiabilities == 0) return 0;
    return (totalAssets - stockValue) / totalLiabilities;
  }

  // هامش الربح
  double get profitMargin {
    if (totalRevenue == 0) return 0;
    return (netProfit / totalRevenue) * 100;
  }

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalAssets: _parseDouble(json['total_assets']),
      totalLiabilities: _parseDouble(json['total_liabilities']),
      totalEquity: _parseDouble(json['total_equity']),
      totalRevenue: _parseDouble(json['total_revenue']),
      totalExpenses: _parseDouble(json['total_expenses']),
      netProfit: _parseDouble(json['net_profit']),
      workingCapital: _parseDouble(json['working_capital']),
      cashBalance: _parseDouble(json['cash_balance']),
      totalReceivables: _parseDouble(json['total_receivables']),
      totalPayables: _parseDouble(json['total_payables']),
      stockValue: _parseDouble(json['stock_value']),
      totalJournalEntries: _parseInt(json['total_journal_entries']),
      draftEntries: _parseInt(json['draft_entries']),
      postedEntries: _parseInt(json['posted_entries']),
    );
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0;
    return 0;
  }

  static int _parseInt(dynamic value) {
    if (value == null) return 0;
    if (value is int) return value;
    if (value is double) return value.toInt();
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }
}

/// Account Balance Trend
/// اتجاه رصيد الحساب

class AccountBalanceTrend {
  final String period;
  final double balance;
  final DateTime date;

  AccountBalanceTrend({
    required this.period,
    required this.balance,
    required this.date,
  });

  factory AccountBalanceTrend.fromJson(Map<String, dynamic> json) {
    return AccountBalanceTrend(
      period: json['period'],
      balance: double.parse(json['balance'].toString()),
      date: DateTime.parse(json['date']),
    );
  }
}

/// Account Type Distribution
/// توزيع أنواع الحسابات

class AccountTypeDistribution {
  final String accountType;
  final String nameAr;
  final double amount;
  final double percentage;
  final int colorValue;

  AccountTypeDistribution({
    required this.accountType,
    required this.nameAr,
    required this.amount,
    required this.percentage,
    required this.colorValue,
  });

  factory AccountTypeDistribution.fromJson(Map<String, dynamic> json) {
    return AccountTypeDistribution(
      accountType: json['account_type'],
      nameAr: json['name_ar'],
      amount: double.parse(json['amount'].toString()),
      percentage: double.parse(json['percentage'].toString()),
      colorValue: json['color_value'] ?? 0xFF1976D2,
    );
  }
}
