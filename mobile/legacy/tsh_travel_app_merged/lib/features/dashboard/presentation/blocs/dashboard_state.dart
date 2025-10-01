import 'package:equatable/equatable.dart';

abstract class DashboardState extends Equatable {
  const DashboardState();

  @override
  List<Object?> get props => [];
}

class DashboardInitial extends DashboardState {}

class DashboardLoading extends DashboardState {}

class DashboardLoaded extends DashboardState {
  final DashboardStats stats;
  final List<RecentOrder> recentOrders;
  final List<TopProduct> topProducts;

  const DashboardLoaded({
    required this.stats,
    required this.recentOrders,
    required this.topProducts,
  });

  @override
  List<Object?> get props => [stats, recentOrders, topProducts];
}

class DashboardError extends DashboardState {
  final String message;

  const DashboardError(this.message);

  @override
  List<Object?> get props => [message];
}

// Dashboard Stats Model
class DashboardStats extends Equatable {
  final double totalSales;
  final int totalOrders;
  final int totalCustomers;
  final double avgOrderValue;
  final int todayOrders;
  final int pendingOrders;
  final String salesTrend;
  final String ordersTrend;
  final String customersTrend;
  final String pendingTrend;

  const DashboardStats({
    required this.totalSales,
    required this.totalOrders,
    required this.totalCustomers,
    required this.avgOrderValue,
    required this.todayOrders,
    required this.pendingOrders,
    required this.salesTrend,
    required this.ordersTrend,
    required this.customersTrend,
    required this.pendingTrend,
  });

  @override
  List<Object?> get props => [
    totalSales, totalOrders, totalCustomers, avgOrderValue,
    todayOrders, pendingOrders, salesTrend, ordersTrend, 
    customersTrend, pendingTrend
  ];
}

// Recent Order Model
class RecentOrder extends Equatable {
  final String id;
  final String customerName;
  final double amount;
  final String status;
  final DateTime date;

  const RecentOrder({
    required this.id,
    required this.customerName,
    required this.amount,
    required this.status,
    required this.date,
  });

  @override
  List<Object?> get props => [id, customerName, amount, status, date];
}

// Top Product Model
class TopProduct extends Equatable {
  final String id;
  final String name;
  final int quantity;
  final double revenue;

  const TopProduct({
    required this.id,
    required this.name,
    required this.quantity,
    required this.revenue,
  });

  @override
  List<Object?> get props => [id, name, quantity, revenue];
}
