/// Account Type Enum
/// أنواع الحسابات

enum AccountType {
  ASSET,      // الأصول
  LIABILITY,  // الخصوم (الالتزامات)
  EQUITY,     // حقوق الملكية
  REVENUE,    // الإيرادات
  EXPENSE     // المصروفات
}

extension AccountTypeExtension on AccountType {
  String get nameAr {
    switch (this) {
      case AccountType.ASSET:
        return 'أصول';
      case AccountType.LIABILITY:
        return 'خصوم';
      case AccountType.EQUITY:
        return 'حقوق الملكية';
      case AccountType.REVENUE:
        return 'إيرادات';
      case AccountType.EXPENSE:
        return 'مصروفات';
    }
  }

  String get nameEn {
    switch (this) {
      case AccountType.ASSET:
        return 'Assets';
      case AccountType.LIABILITY:
        return 'Liabilities';
      case AccountType.EQUITY:
        return 'Equity';
      case AccountType.REVENUE:
        return 'Revenue';
      case AccountType.EXPENSE:
        return 'Expenses';
    }
  }

  String get icon {
    switch (this) {
      case AccountType.ASSET:
        return '🏦'; // Bank/Assets
      case AccountType.LIABILITY:
        return '📊'; // Liabilities
      case AccountType.EQUITY:
        return '👤'; // Equity/Owner
      case AccountType.REVENUE:
        return '💰'; // Revenue/Money
      case AccountType.EXPENSE:
        return '💳'; // Expenses/Card
    }
  }

  int get colorValue {
    switch (this) {
      case AccountType.ASSET:
        return 0xFF1976D2; // Blue
      case AccountType.LIABILITY:
        return 0xFFE53935; // Red
      case AccountType.EQUITY:
        return 0xFF7B1FA2; // Purple
      case AccountType.REVENUE:
        return 0xFF388E3C; // Green
      case AccountType.EXPENSE:
        return 0xFFF57C00; // Orange
    }
  }

  // للمعادلة المحاسبية: الأصول = الخصوم + حقوق الملكية
  bool get isLeftSide {
    return this == AccountType.ASSET;
  }

  bool get isRightSide {
    return this == AccountType.LIABILITY || this == AccountType.EQUITY;
  }

  // الحسابات التي تزيد بالمدين
  bool get increasesWithDebit {
    return this == AccountType.ASSET || this == AccountType.EXPENSE;
  }

  // الحسابات التي تزيد بالدائن
  bool get increasesWithCredit {
    return this == AccountType.LIABILITY ||
           this == AccountType.EQUITY ||
           this == AccountType.REVENUE;
  }
}

AccountType accountTypeFromString(String type) {
  switch (type.toUpperCase()) {
    case 'ASSET':
      return AccountType.ASSET;
    case 'LIABILITY':
      return AccountType.LIABILITY;
    case 'EQUITY':
      return AccountType.EQUITY;
    case 'REVENUE':
      return AccountType.REVENUE;
    case 'EXPENSE':
      return AccountType.EXPENSE;
    default:
      throw Exception('Unknown account type: $type');
  }
}
