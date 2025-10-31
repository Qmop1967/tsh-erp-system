import 'account_type.dart';

/// Chart of Accounts Model
/// نموذج دليل الحسابات

class ChartOfAccounts {
  final int? id;
  final String code;
  final String nameAr;
  final String nameEn;
  final AccountType accountType;
  final int? parentId;
  final int level;
  final bool isActive;
  final bool allowPosting;
  final String? descriptionAr;
  final String? descriptionEn;
  final List<ChartOfAccounts>? children;
  final Account? account; // الحساب الفعلي مع الأرصدة

  ChartOfAccounts({
    this.id,
    required this.code,
    required this.nameAr,
    required this.nameEn,
    required this.accountType,
    this.parentId,
    required this.level,
    this.isActive = true,
    this.allowPosting = true,
    this.descriptionAr,
    this.descriptionEn,
    this.children,
    this.account,
  });

  factory ChartOfAccounts.fromJson(Map<String, dynamic> json) {
    return ChartOfAccounts(
      id: json['id'],
      code: json['code'],
      nameAr: json['name_ar'],
      nameEn: json['name_en'],
      accountType: accountTypeFromString(json['account_type']),
      parentId: json['parent_id'],
      level: json['level'],
      isActive: json['is_active'] ?? true,
      allowPosting: json['allow_posting'] ?? true,
      descriptionAr: json['description_ar'],
      descriptionEn: json['description_en'],
      children: json['children'] != null
          ? (json['children'] as List)
              .map((child) => ChartOfAccounts.fromJson(child))
              .toList()
          : null,
      account:
          json['account'] != null ? Account.fromJson(json['account']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'name_ar': nameAr,
      'name_en': nameEn,
      'account_type': accountType.name,
      'parent_id': parentId,
      'level': level,
      'is_active': isActive,
      'allow_posting': allowPosting,
      'description_ar': descriptionAr,
      'description_en': descriptionEn,
    };
  }

  bool get hasChildren => children != null && children!.isNotEmpty;
}

/// Account Model with Balances
/// نموذج الحساب مع الأرصدة

class Account {
  final int? id;
  final int chartAccountId;
  final int currencyId;
  final String? currencyCode;
  final double balanceDebit;
  final double balanceCredit;
  final double balance;
  final bool isActive;

  Account({
    this.id,
    required this.chartAccountId,
    required this.currencyId,
    this.currencyCode,
    this.balanceDebit = 0,
    this.balanceCredit = 0,
    this.balance = 0,
    this.isActive = true,
  });

  // الرصيد الصافي
  double get netBalance => balanceDebit - balanceCredit;

  factory Account.fromJson(Map<String, dynamic> json) {
    return Account(
      id: json['id'],
      chartAccountId: json['chart_account_id'],
      currencyId: json['currency_id'],
      currencyCode: json['currency_code'],
      balanceDebit: double.parse(json['balance_debit'].toString()),
      balanceCredit: double.parse(json['balance_credit'].toString()),
      balance: double.parse(json['balance'].toString()),
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'chart_account_id': chartAccountId,
      'currency_id': currencyId,
      'currency_code': currencyCode,
      'balance_debit': balanceDebit,
      'balance_credit': balanceCredit,
      'balance': balance,
      'is_active': isActive,
    };
  }
}

/// Currency Model
/// نموذج العملة

class Currency {
  final int? id;
  final String code;
  final String nameAr;
  final String nameEn;
  final String symbol;
  final double exchangeRate;
  final bool isBaseCurrency;
  final bool isActive;

  Currency({
    this.id,
    required this.code,
    required this.nameAr,
    required this.nameEn,
    required this.symbol,
    this.exchangeRate = 1.0,
    this.isBaseCurrency = false,
    this.isActive = true,
  });

  factory Currency.fromJson(Map<String, dynamic> json) {
    return Currency(
      id: json['id'],
      code: json['code'],
      nameAr: json['name_ar'],
      nameEn: json['name_en'],
      symbol: json['symbol'],
      exchangeRate: double.parse(json['exchange_rate'].toString()),
      isBaseCurrency: json['is_base_currency'] ?? false,
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'name_ar': nameAr,
      'name_en': nameEn,
      'symbol': symbol,
      'exchange_rate': exchangeRate,
      'is_base_currency': isBaseCurrency,
      'is_active': isActive,
    };
  }
}
