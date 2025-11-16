// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'commission.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Commission _$CommissionFromJson(Map<String, dynamic> json) => Commission(
      id: (json['id'] as num?)?.toInt(),
      salespersonId: (json['salespersonId'] as num).toInt(),
      period: json['period'] as String,
      startDate: json['startDate'] as String,
      endDate: json['endDate'] as String,
      totalSalesAmount: (json['totalSalesAmount'] as num).toDouble(),
      commissionRate: (json['commissionRate'] as num?)?.toDouble() ?? 2.25,
      commissionAmount: (json['commissionAmount'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'IQD',
      status: json['status'] as String? ?? 'pending',
      notes: json['notes'] as String?,
      ordersCount: (json['ordersCount'] as num?)?.toInt(),
      createdAt: json['createdAt'] as String,
      paidAt: json['paidAt'] as String?,
      isSynced: json['isSynced'] as bool? ?? false,
    );

Map<String, dynamic> _$CommissionToJson(Commission instance) =>
    <String, dynamic>{
      'id': instance.id,
      'salespersonId': instance.salespersonId,
      'period': instance.period,
      'startDate': instance.startDate,
      'endDate': instance.endDate,
      'totalSalesAmount': instance.totalSalesAmount,
      'commissionRate': instance.commissionRate,
      'commissionAmount': instance.commissionAmount,
      'currency': instance.currency,
      'status': instance.status,
      'notes': instance.notes,
      'ordersCount': instance.ordersCount,
      'createdAt': instance.createdAt,
      'paidAt': instance.paidAt,
      'isSynced': instance.isSynced,
    };

DailyCommissionSummary _$DailyCommissionSummaryFromJson(
        Map<String, dynamic> json) =>
    DailyCommissionSummary(
      date: json['date'] as String,
      totalSales: (json['totalSales'] as num).toDouble(),
      totalCommission: (json['totalCommission'] as num).toDouble(),
      ordersCount: (json['ordersCount'] as num).toInt(),
      commissionRate: (json['commissionRate'] as num?)?.toDouble() ?? 2.25,
    );

Map<String, dynamic> _$DailyCommissionSummaryToJson(
        DailyCommissionSummary instance) =>
    <String, dynamic>{
      'date': instance.date,
      'totalSales': instance.totalSales,
      'totalCommission': instance.totalCommission,
      'ordersCount': instance.ordersCount,
      'commissionRate': instance.commissionRate,
    };

SalesTarget _$SalesTargetFromJson(Map<String, dynamic> json) => SalesTarget(
      id: (json['id'] as num?)?.toInt(),
      salespersonId: (json['salespersonId'] as num).toInt(),
      period: json['period'] as String,
      startDate: json['startDate'] as String,
      endDate: json['endDate'] as String,
      targetAmount: (json['targetAmount'] as num).toDouble(),
      currentAmount: (json['currentAmount'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'IQD',
      notes: json['notes'] as String?,
      isActive: json['isActive'] as bool? ?? true,
    );

Map<String, dynamic> _$SalesTargetToJson(SalesTarget instance) =>
    <String, dynamic>{
      'id': instance.id,
      'salespersonId': instance.salespersonId,
      'period': instance.period,
      'startDate': instance.startDate,
      'endDate': instance.endDate,
      'targetAmount': instance.targetAmount,
      'currentAmount': instance.currentAmount,
      'currency': instance.currency,
      'notes': instance.notes,
      'isActive': instance.isActive,
    };

LeaderboardEntry _$LeaderboardEntryFromJson(Map<String, dynamic> json) =>
    LeaderboardEntry(
      salespersonId: (json['salespersonId'] as num).toInt(),
      salespersonName: json['salespersonName'] as String,
      rank: (json['rank'] as num).toInt(),
      totalSales: (json['totalSales'] as num).toDouble(),
      totalCommission: (json['totalCommission'] as num).toDouble(),
      ordersCount: (json['ordersCount'] as num).toInt(),
      period: json['period'] as String,
      profilePhotoUrl: json['profilePhotoUrl'] as String?,
    );

Map<String, dynamic> _$LeaderboardEntryToJson(LeaderboardEntry instance) =>
    <String, dynamic>{
      'salespersonId': instance.salespersonId,
      'salespersonName': instance.salespersonName,
      'rank': instance.rank,
      'totalSales': instance.totalSales,
      'totalCommission': instance.totalCommission,
      'ordersCount': instance.ordersCount,
      'period': instance.period,
      'profilePhotoUrl': instance.profilePhotoUrl,
    };

CommissionSummary _$CommissionSummaryFromJson(Map<String, dynamic> json) =>
    CommissionSummary(
      salespersonId: (json['salespersonId'] as num).toInt(),
      period: json['period'] as String,
      totalSales: (json['totalSales'] as num).toDouble(),
      totalCommission: (json['totalCommission'] as num).toDouble(),
      pendingCommission: (json['pendingCommission'] as num).toDouble(),
      paidCommission: (json['paidCommission'] as num).toDouble(),
      ordersCount: (json['ordersCount'] as num).toInt(),
      commissionRate: (json['commissionRate'] as num?)?.toDouble() ?? 2.25,
      lastUpdated: json['lastUpdated'] as String,
    );

Map<String, dynamic> _$CommissionSummaryToJson(CommissionSummary instance) =>
    <String, dynamic>{
      'salespersonId': instance.salespersonId,
      'period': instance.period,
      'totalSales': instance.totalSales,
      'totalCommission': instance.totalCommission,
      'pendingCommission': instance.pendingCommission,
      'paidCommission': instance.paidCommission,
      'ordersCount': instance.ordersCount,
      'commissionRate': instance.commissionRate,
      'lastUpdated': instance.lastUpdated,
    };
