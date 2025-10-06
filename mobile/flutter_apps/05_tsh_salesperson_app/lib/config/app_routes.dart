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
import '../providers/auth_provider.dart';

class AppRoutes {
  static final GoRouter router = GoRouter(
    initialLocation: '/',
    redirect: (BuildContext context, GoRouterState state) async {
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
}
