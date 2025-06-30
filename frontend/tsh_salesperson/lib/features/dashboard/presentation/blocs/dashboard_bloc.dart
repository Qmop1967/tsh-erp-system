import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:tsh_core_package/tsh_core_package.dart';
import 'dashboard_event.dart';
import 'dashboard_state.dart';

class DashboardBloc extends Bloc<DashboardEvent, DashboardState> {
  final AuthService _authService;

  DashboardBloc(this._authService) : super(DashboardInitial()) {
    on<DashboardLoadRequested>(_onDashboardLoadRequested);
    on<DashboardRefreshRequested>(_onDashboardRefreshRequested);
  }

  Future<void> _onDashboardLoadRequested(
    DashboardLoadRequested event,
    Emitter<DashboardState> emit,
  ) async {
    emit(DashboardLoading());
    
    try {
      // Simulate loading dashboard data
      await Future.delayed(const Duration(seconds: 1));
      
      // Mock dashboard data
      final dashboardData = DashboardData(
        totalSales: 125000.0,
        totalOrders: 342,
        totalCustomers: 89,
        pendingOrders: 23,
        salesGrowth: '+12.5%',
        ordersGrowth: '+8.2%',
        customersGrowth: '+15.3%',
        pendingGrowth: '-5.1%',
        recentOrders: [
          Order(
            id: 1,
            orderNumber: 'ORD-001',
            salesPersonId: 1,
            salesPerson: _authService.currentUser!,
            status: OrderStatus.pending,
            paymentStatus: PaymentStatus.pending,
            subtotal: 1200.0,
            taxAmount: 120.0,
            discountAmount: 0.0,
            totalAmount: 1320.0,
            items: [],
            createdAt: DateTime.now().subtract(const Duration(hours: 2)),
            updatedAt: DateTime.now(),
          ),
          Order(
            id: 2,
            orderNumber: 'ORD-002',
            salesPersonId: 1,
            salesPerson: _authService.currentUser!,
            status: OrderStatus.confirmed,
            paymentStatus: PaymentStatus.paid,
            subtotal: 800.0,
            taxAmount: 80.0,
            discountAmount: 50.0,
            totalAmount: 830.0,
            items: [],
            createdAt: DateTime.now().subtract(const Duration(hours: 5)),
            updatedAt: DateTime.now(),
          ),
        ],
      );
      
      emit(DashboardLoaded(
        stats: DashboardStats(
          totalSales: dashboardData.totalSales,
          totalOrders: dashboardData.totalOrders,
          totalCustomers: dashboardData.totalCustomers,
          avgOrderValue: dashboardData.totalSales / dashboardData.totalOrders,
          todayOrders: 15, // Mock data
          pendingOrders: dashboardData.pendingOrders,
          salesTrend: dashboardData.salesGrowth,
          ordersTrend: dashboardData.ordersGrowth,
          customersTrend: dashboardData.customersGrowth,
          pendingTrend: dashboardData.pendingGrowth,
        ),
        recentOrders: dashboardData.recentOrders.map((order) => RecentOrder(
          id: order.orderNumber,
          customerName: '${order.salesPerson.firstName} ${order.salesPerson.lastName}',
          amount: order.totalAmount,
          status: order.status.toString().split('.').last,
          date: order.createdAt,
        )).toList(),
        topProducts: [
          // Mock top products for now
          TopProduct(
            id: '1',
            name: 'Product A',
            quantity: 25,
            revenue: 15000.0,
          ),
          TopProduct(
            id: '2', 
            name: 'Product B',
            quantity: 18,
            revenue: 12000.0,
          ),
        ],
      ));
    } catch (e) {
      emit(DashboardError(e.toString()));
    }
  }

  Future<void> _onDashboardRefreshRequested(
    DashboardRefreshRequested event,
    Emitter<DashboardState> emit,
  ) async {
    // Reload dashboard data
    add(DashboardLoadRequested());
  }
}

class DashboardData extends Equatable {
  final double totalSales;
  final int totalOrders;
  final int totalCustomers;
  final int pendingOrders;
  final String salesGrowth;
  final String ordersGrowth;
  final String customersGrowth;
  final String pendingGrowth;
  final List<Order> recentOrders;

  const DashboardData({
    required this.totalSales,
    required this.totalOrders,
    required this.totalCustomers,
    required this.pendingOrders,
    required this.salesGrowth,
    required this.ordersGrowth,
    required this.customersGrowth,
    required this.pendingGrowth,
    required this.recentOrders,
  });

  @override
  List<Object> get props => [
        totalSales,
        totalOrders,
        totalCustomers,
        pendingOrders,
        salesGrowth,
        ordersGrowth,
        customersGrowth,
        pendingGrowth,
        recentOrders,
      ];
}
