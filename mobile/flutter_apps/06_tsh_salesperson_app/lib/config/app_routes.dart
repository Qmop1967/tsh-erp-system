import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../pages/auth/login_page.dart';
import '../pages/home/home_page.dart';
import '../pages/customers/customers_page.dart';
import '../pages/orders/orders_page.dart';
import '../pages/products/products_page.dart';
import '../pages/profile/profile_page.dart';
import '../pages/sales/sales_page.dart';
import '../pages/gps/gps_tracking_page.dart';
import '../pages/gps/tracking_dashboard_page.dart';
import '../pages/gps/location_history_page.dart';
import '../pages/transfers/transfer_dashboard_page.dart';
import '../pages/transfers/create_transfer_page.dart';
import '../pages/transfers/transfer_history_page.dart';
import '../pages/commission/commission_dashboard_page.dart';
import '../providers/auth_provider.dart';

class AppRoutes {
  static final GoRouter router = GoRouter(
    initialLocation: '/home', // Skip authentication, go directly to home
    redirect: (BuildContext context, GoRouterState state) async {
      // AUTHENTICATION DISABLED - Direct access to all pages
      // This allows the app to run without login for testing/demo purposes

      // If on root path, redirect to home
      if (state.matchedLocation == '/') {
        return '/home';
      }

      // No redirect needed - allow all routes
      return null;

      /* ORIGINAL AUTHENTICATION CODE (Commented out for bypass):
      final authProvider = context.read<AuthProvider>();
      final isLoggedIn = await authProvider.authService.isLoggedIn();
      final isGoingToLogin = state.matchedLocation == '/login';

      // If not logged in and not going to login page, redirect to login
      if (!isLoggedIn && !isGoingToLogin) {
        return '/login';
      }

      // If logged in and going to login page, redirect to home
      if (isLoggedIn && isGoingToLogin) {
        return '/home';
      }

      // If on root path, redirect based on login status
      if (state.matchedLocation == '/') {
        return isLoggedIn ? '/home' : '/login';
      }

      // No redirect needed
      return null;
      */
    },
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/home',
        name: 'home',
        builder: (context, state) => const HomePage(),
      ),
      GoRoute(
        path: '/customers',
        name: 'customers',
        builder: (context, state) => const CustomersPage(),
      ),
      GoRoute(
        path: '/orders',
        name: 'orders',
        builder: (context, state) => const OrdersPage(),
      ),
      GoRoute(
        path: '/products',
        name: 'products',
        builder: (context, state) => const ProductsPage(),
      ),
      GoRoute(
        path: '/sales',
        name: 'sales',
        builder: (context, state) => const SalesPage(),
      ),
      GoRoute(
        path: '/profile',
        name: 'profile',
        builder: (context, state) => const ProfilePage(),
      ),
      GoRoute(
        path: '/gps-tracking',
        name: 'gps-tracking',
        builder: (context, state) => const GPSTrackingPage(),
      ),
      GoRoute(
        path: '/tracking-dashboard',
        name: 'tracking-dashboard',
        builder: (context, state) {
          final salespersonId = state.uri.queryParameters['salespersonId'];
          return TrackingDashboardPage(
            salespersonId: int.tryParse(salespersonId ?? '1') ?? 1,
          );
        },
      ),
      GoRoute(
        path: '/location-history',
        name: 'location-history',
        builder: (context, state) {
          final salespersonId = state.uri.queryParameters['salespersonId'];
          return LocationHistoryPage(
            salespersonId: int.tryParse(salespersonId ?? '1') ?? 1,
          );
        },
      ),
      GoRoute(
        path: '/transfer-dashboard',
        name: 'transfer-dashboard',
        builder: (context, state) {
          final salespersonId = state.uri.queryParameters['salespersonId'];
          return TransferDashboardPage(
            salespersonId: int.tryParse(salespersonId ?? '1') ?? 1,
          );
        },
      ),
      GoRoute(
        path: '/create-transfer',
        name: 'create-transfer',
        builder: (context, state) {
          final salespersonId = state.uri.queryParameters['salespersonId'];
          return CreateTransferPage(
            salespersonId: int.tryParse(salespersonId ?? '1') ?? 1,
          );
        },
      ),
      GoRoute(
        path: '/transfer-history',
        name: 'transfer-history',
        builder: (context, state) {
          final salespersonId = state.uri.queryParameters['salespersonId'];
          return TransferHistoryPage(
            salespersonId: int.tryParse(salespersonId ?? '1') ?? 1,
          );
        },
      ),
      GoRoute(
        path: '/commission-dashboard',
        name: 'commission-dashboard',
        builder: (context, state) {
          final salespersonId = state.uri.queryParameters['salespersonId'];
          return CommissionDashboardPage(
            salespersonId: int.tryParse(salespersonId ?? '1') ?? 1,
          );
        },
      ),
    ],
  );

  // Route names
  static const String login = '/login';
  static const String home = '/home';
  static const String customers = '/customers';
  static const String orders = '/orders';
  static const String products = '/products';
  static const String sales = '/sales';
  static const String profile = '/profile';
  static const String gpsTracking = '/gps-tracking';
  static const String trackingDashboard = '/tracking-dashboard';
  static const String locationHistory = '/location-history';
  static const String transferDashboard = '/transfer-dashboard';
  static const String createTransfer = '/create-transfer';
  static const String transferHistory = '/transfer-history';
  static const String commissionDashboard = '/commission-dashboard';
}
