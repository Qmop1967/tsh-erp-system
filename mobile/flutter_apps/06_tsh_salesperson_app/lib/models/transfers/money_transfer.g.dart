// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'money_transfer.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MoneyTransfer _$MoneyTransferFromJson(Map<String, dynamic> json) =>
    MoneyTransfer(
      id: (json['id'] as num?)?.toInt(),
      salespersonId: (json['salespersonId'] as num).toInt(),
      transferMethod: json['transferMethod'] as String,
      amount: (json['amount'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'IQD',
      date: json['date'] as String,
      timestamp: json['timestamp'] as String,
      customerId: (json['customerId'] as num?)?.toInt(),
      customerName: json['customerName'] as String?,
      referenceNumber: json['referenceNumber'] as String?,
      senderName: json['senderName'] as String?,
      senderPhone: json['senderPhone'] as String?,
      receiverName: json['receiverName'] as String?,
      receiverPhone: json['receiverPhone'] as String?,
      receiptPhotoPath: json['receiptPhotoPath'] as String?,
      receiptPhotoUrl: json['receiptPhotoUrl'] as String?,
      status: json['status'] as String? ?? 'pending',
      verificationNotes: json['verificationNotes'] as String?,
      verifiedBy: json['verifiedBy'] as String?,
      verifiedAt: json['verifiedAt'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      isSynced: json['isSynced'] as bool? ?? false,
    );

Map<String, dynamic> _$MoneyTransferToJson(MoneyTransfer instance) =>
    <String, dynamic>{
      'id': instance.id,
      'salespersonId': instance.salespersonId,
      'transferMethod': instance.transferMethod,
      'amount': instance.amount,
      'currency': instance.currency,
      'date': instance.date,
      'timestamp': instance.timestamp,
      'customerId': instance.customerId,
      'customerName': instance.customerName,
      'referenceNumber': instance.referenceNumber,
      'senderName': instance.senderName,
      'senderPhone': instance.senderPhone,
      'receiverName': instance.receiverName,
      'receiverPhone': instance.receiverPhone,
      'receiptPhotoPath': instance.receiptPhotoPath,
      'receiptPhotoUrl': instance.receiptPhotoUrl,
      'status': instance.status,
      'verificationNotes': instance.verificationNotes,
      'verifiedBy': instance.verifiedBy,
      'verifiedAt': instance.verifiedAt,
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'notes': instance.notes,
      'isSynced': instance.isSynced,
    };

DailyTransferSummary _$DailyTransferSummaryFromJson(
        Map<String, dynamic> json) =>
    DailyTransferSummary(
      date: json['date'] as String,
      totalTransfers: (json['totalTransfers'] as num).toInt(),
      totalAmount: (json['totalAmount'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'IQD',
      transfersByMethod:
          Map<String, int>.from(json['transfersByMethod'] as Map),
      amountsByMethod: (json['amountsByMethod'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
      pendingCount: (json['pendingCount'] as num).toInt(),
      verifiedCount: (json['verifiedCount'] as num).toInt(),
      completedCount: (json['completedCount'] as num).toInt(),
      transfers: (json['transfers'] as List<dynamic>)
          .map((e) => MoneyTransfer.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$DailyTransferSummaryToJson(
        DailyTransferSummary instance) =>
    <String, dynamic>{
      'date': instance.date,
      'totalTransfers': instance.totalTransfers,
      'totalAmount': instance.totalAmount,
      'currency': instance.currency,
      'transfersByMethod': instance.transfersByMethod,
      'amountsByMethod': instance.amountsByMethod,
      'pendingCount': instance.pendingCount,
      'verifiedCount': instance.verifiedCount,
      'completedCount': instance.completedCount,
      'transfers': instance.transfers,
    };

CashBoxBalance _$CashBoxBalanceFromJson(Map<String, dynamic> json) =>
    CashBoxBalance(
      salespersonId: (json['salespersonId'] as num).toInt(),
      cashIQD: (json['cashIQD'] as num?)?.toDouble() ?? 0.0,
      cashUSD: (json['cashUSD'] as num?)?.toDouble() ?? 0.0,
      altaifIQD: (json['altaifIQD'] as num?)?.toDouble() ?? 0.0,
      zainCashIQD: (json['zainCashIQD'] as num?)?.toDouble() ?? 0.0,
      superQiIQD: (json['superQiIQD'] as num?)?.toDouble() ?? 0.0,
      lastUpdated: json['lastUpdated'] as String,
    );

Map<String, dynamic> _$CashBoxBalanceToJson(CashBoxBalance instance) =>
    <String, dynamic>{
      'salespersonId': instance.salespersonId,
      'cashIQD': instance.cashIQD,
      'cashUSD': instance.cashUSD,
      'altaifIQD': instance.altaifIQD,
      'zainCashIQD': instance.zainCashIQD,
      'superQiIQD': instance.superQiIQD,
      'lastUpdated': instance.lastUpdated,
    };
