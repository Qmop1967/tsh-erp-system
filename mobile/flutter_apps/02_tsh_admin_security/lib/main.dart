import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/dashboard_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/dashboard/dashboard_screen.dart';
import 'screens/users/users_screen.dart';
import 'screens/roles/roles_permissions_screen.dart';
import 'screens/devices/devices_screen.dart';
import 'screens/sessions/sessions_screen.dart';
import 'screens/audit/audit_logs_screen.dart';
import 'screens/security/security_events_screen.dart';

void main() {
  // Enable detailed logging in debug mode
  if (kDebugMode) {
    debugPrint('🚀 TSH Admin Security App Starting...');
  }

  // Capture Flutter errors
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint('🔴 Flutter Error: ${details.exception}');
    debugPrint('Stack trace: ${details.stack}');
  };

  // Capture async errors
  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('🔴 Async Error: $error');
    debugPrint('Stack trace: $stack');
    return true;
  };

  runApp(const TSHAccessManagementApp());
}

class TSHAccessManagementApp extends StatelessWidget {
  const TSHAccessManagementApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()..initialize()),
        ChangeNotifierProvider(create: (_) => DashboardProvider()..initialize()),
      ],
      child: MaterialApp(
        title: 'TSH Access Management',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff2563eb)),
          useMaterial3: true,
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const AuthWrapper(),
          '/login': (context) => const LoginScreen(),
          '/dashboard': (context) => const DashboardScreen(),
          '/users': (context) => const UsersScreen(),
          '/roles': (context) => const RolesPermissionsScreen(),
          '/devices': (context) => const DevicesScreen(),
          '/sessions': (context) => const SessionsScreen(),
          '/audit': (context) => const AuditLogsScreen(),
          '/security': (context) => const SecurityEventsScreen(),
        },
      ),
    );
  }
}

/// Auth Wrapper - Decides whether to show login or dashboard
class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        // Show loading while initializing
        if (authProvider.isLoading) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        // Show dashboard if authenticated, otherwise show login
        if (authProvider.isAuthenticated) {
          return const DashboardScreen();
        } else {
          return const LoginScreen();
        }
      },
    );
  }
}
