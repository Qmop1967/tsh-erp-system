import 'package:json_annotation/json_annotation.dart';
import 'package:intl/intl.dart';

part 'commission.g.dart';

/// Commission Record Model
/// Tracks individual commission earnings for salespersons
@JsonSerializable()
class Commission {
  final int? id;
  final int salespersonId;
  final String period; // 'daily', 'weekly', 'monthly'
  final String startDate; // ISO 8601
  final String endDate; // ISO 8601
  final double totalSalesAmount;
  final double commissionRate; // Default: 2.25 (as percentage)
  final double commissionAmount; // Calculated: totalSalesAmount * (commissionRate / 100)
  final String currency; // IQD, USD
  final String status; // 'pending', 'approved', 'paid', 'disputed'
  final String? notes;
  final int? ordersCount; // Number of orders in this period
  final String createdAt;
  final String? paidAt; // When commission was paid
  final bool isSynced;

  Commission({
    this.id,
    required this.salespersonId,
    required this.period,
    required this.startDate,
    required this.endDate,
    required this.totalSalesAmount,
    this.commissionRate = 2.25,
    required this.commissionAmount,
    this.currency = 'IQD',
    this.status = 'pending',
    this.notes,
    this.ordersCount,
    required this.createdAt,
    this.paidAt,
    this.isSynced = false,
  });

  factory Commission.fromJson(Map<String, dynamic> json) =>
      _$CommissionFromJson(json);

  Map<String, dynamic> toJson() => _$CommissionToJson(this);

  /// Calculate commission from sales amount
  static double calculateCommission(double salesAmount, double rate) {
    return salesAmount * (rate / 100);
  }

  /// Get status name in Arabic
  String get statusName {
    switch (status) {
      case 'pending':
        return 'قيد الانتظار';
      case 'approved':
        return 'معتمد';
      case 'paid':
        return 'مدفوع';
      case 'disputed':
        return 'متنازع عليه';
      default:
        return status;
    }
  }

  /// Get period name in Arabic
  String get periodName {
    switch (period) {
      case 'daily':
        return 'يومي';
      case 'weekly':
        return 'أسبوعي';
      case 'monthly':
        return 'شهري';
      default:
        return period;
    }
  }

  /// Format commission amount with currency
  String get formattedCommissionAmount {
    if (currency == 'USD') {
      return '\$${commissionAmount.toStringAsFixed(2)}';
    } else {
      final formatter = NumberFormat('#,###', 'en_US');
      return '${formatter.format(commissionAmount)} د.ع';
    }
  }

  /// Format sales amount with currency
  String get formattedSalesAmount {
    if (currency == 'USD') {
      return '\$${totalSalesAmount.toStringAsFixed(2)}';
    } else {
      final formatter = NumberFormat('#,###', 'en_US');
      return '${formatter.format(totalSalesAmount)} د.ع';
    }
  }

  /// Format date range
  String get formattedDateRange {
    final start = DateTime.parse(startDate);
    final end = DateTime.parse(endDate);
    final formatter = DateFormat('MMM d', 'ar');
    return '${formatter.format(start)} - ${formatter.format(end)}';
  }
}

/// Daily Commission Summary
/// Aggregated commission data for a specific day
@JsonSerializable()
class DailyCommissionSummary {
  final String date; // ISO 8601
  final double totalSales;
  final double totalCommission;
  final int ordersCount;
  final double commissionRate;

  DailyCommissionSummary({
    required this.date,
    required this.totalSales,
    required this.totalCommission,
    required this.ordersCount,
    this.commissionRate = 2.25,
  });

  factory DailyCommissionSummary.fromJson(Map<String, dynamic> json) =>
      _$DailyCommissionSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$DailyCommissionSummaryToJson(this);

  String get formattedDate {
    final dateTime = DateTime.parse(date);
    return DateFormat('EEE، MMM d', 'ar').format(dateTime);
  }

  String get formattedTotalCommission {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(totalCommission)} د.ع';
  }

  String get formattedTotalSales {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(totalSales)} د.ع';
  }
}

/// Sales Target Model
/// Monthly or weekly sales goals for salesperson
@JsonSerializable()
class SalesTarget {
  final int? id;
  final int salespersonId;
  final String period; // 'weekly', 'monthly', 'quarterly'
  final String startDate;
  final String endDate;
  final double targetAmount;
  final double currentAmount;
  final String currency;
  final String? notes;
  final bool isActive;

  SalesTarget({
    this.id,
    required this.salespersonId,
    required this.period,
    required this.startDate,
    required this.endDate,
    required this.targetAmount,
    this.currentAmount = 0.0,
    this.currency = 'IQD',
    this.notes,
    this.isActive = true,
  });

  factory SalesTarget.fromJson(Map<String, dynamic> json) =>
      _$SalesTargetFromJson(json);

  Map<String, dynamic> toJson() => _$SalesTargetToJson(this);

  /// Calculate progress percentage
  double get progressPercentage {
    if (targetAmount == 0) return 0.0;
    return (currentAmount / targetAmount) * 100;
  }

  /// Check if target is achieved
  bool get isAchieved => currentAmount >= targetAmount;

  /// Remaining amount to reach target
  double get remainingAmount => targetAmount - currentAmount;

  /// Format target amount
  String get formattedTargetAmount {
    if (currency == 'USD') {
      return '\$${targetAmount.toStringAsFixed(2)}';
    } else {
      final formatter = NumberFormat('#,###', 'en_US');
      return '${formatter.format(targetAmount)} د.ع';
    }
  }

  /// Format current amount
  String get formattedCurrentAmount {
    if (currency == 'USD') {
      return '\$${currentAmount.toStringAsFixed(2)}';
    } else {
      final formatter = NumberFormat('#,###', 'en_US');
      return '${formatter.format(currentAmount)} د.ع';
    }
  }

  /// Format remaining amount
  String get formattedRemainingAmount {
    if (currency == 'USD') {
      return '\$${remainingAmount.toStringAsFixed(2)}';
    } else {
      final formatter = NumberFormat('#,###', 'en_US');
      return '${formatter.format(remainingAmount)} د.ع';
    }
  }

  /// Get period name in Arabic
  String get periodName {
    switch (period) {
      case 'weekly':
        return 'أسبوعي';
      case 'monthly':
        return 'شهري';
      case 'quarterly':
        return 'ربع سنوي';
      default:
        return period;
    }
  }
}

/// Leaderboard Entry Model
/// Represents a salesperson's ranking in the team
@JsonSerializable()
class LeaderboardEntry {
  final int salespersonId;
  final String salespersonName;
  final int rank;
  final double totalSales;
  final double totalCommission;
  final int ordersCount;
  final String period; // 'weekly', 'monthly', 'all-time'
  final String? profilePhotoUrl;

  LeaderboardEntry({
    required this.salespersonId,
    required this.salespersonName,
    required this.rank,
    required this.totalSales,
    required this.totalCommission,
    required this.ordersCount,
    required this.period,
    this.profilePhotoUrl,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) =>
      _$LeaderboardEntryFromJson(json);

  Map<String, dynamic> toJson() => _$LeaderboardEntryToJson(this);

  String get formattedTotalSales {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(totalSales)} د.ع';
  }

  String get formattedTotalCommission {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(totalCommission)} د.ع';
  }

  /// Get rank badge color
  String get rankBadgeColor {
    switch (rank) {
      case 1:
        return '#FFD700'; // Gold
      case 2:
        return '#C0C0C0'; // Silver
      case 3:
        return '#CD7F32'; // Bronze
      default:
        return '#607D8B'; // Grey
    }
  }

  /// Get rank icon
  String get rankIcon {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return '${rank}';
    }
  }
}

/// Commission Summary Model
/// Overall commission statistics
@JsonSerializable()
class CommissionSummary {
  final int salespersonId;
  final String period; // 'today', 'week', 'month', 'all-time'
  final double totalSales;
  final double totalCommission;
  final double pendingCommission;
  final double paidCommission;
  final int ordersCount;
  final double commissionRate;
  final String lastUpdated;

  CommissionSummary({
    required this.salespersonId,
    required this.period,
    required this.totalSales,
    required this.totalCommission,
    required this.pendingCommission,
    required this.paidCommission,
    required this.ordersCount,
    this.commissionRate = 2.25,
    required this.lastUpdated,
  });

  factory CommissionSummary.fromJson(Map<String, dynamic> json) =>
      _$CommissionSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$CommissionSummaryToJson(this);

  String get formattedTotalCommission {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(totalCommission)} د.ع';
  }

  String get formattedPendingCommission {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(pendingCommission)} د.ع';
  }

  String get formattedPaidCommission {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(paidCommission)} د.ع';
  }

  String get formattedTotalSales {
    final formatter = NumberFormat('#,###', 'en_US');
    return '${formatter.format(totalSales)} د.ع';
  }

  /// Get period name in Arabic
  String get periodName {
    switch (period) {
      case 'today':
        return 'اليوم';
      case 'week':
        return 'هذا الأسبوع';
      case 'month':
        return 'هذا الشهر';
      case 'all-time':
        return 'الإجمالي';
      default:
        return period;
    }
  }
}
