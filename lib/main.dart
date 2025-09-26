import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import 'config/app_config.dart';
import 'config/app_theme.dart';
import 'config/app_routes.dart';
import 'services/odoo_service.dart';
import 'services/auth_service.dart';
import 'services/connectivity_service.dart';
import 'providers/auth_provider.dart';
import 'providers/dashboard_provider.dart';
import 'providers/customer_provider.dart';
import 'providers/product_provider.dart';
import 'providers/order_provider.dart';
import 'providers/payment_provider.dart';
import 'utils/app_localizations.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive for local storage
  await Hive.initFlutter();
  
  // Initialize services
  await AppConfig.initialize();
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  runApp(const TSHSalespersonApp());
}

class TSHSalespersonApp extends StatelessWidget {
  const TSHSalespersonApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Services
        Provider<OdooService>(
          create: (_) => OdooService(),
        ),
        Provider<AuthService>(
          create: (context) => AuthService(
            context.read<OdooService>(),
          ),
        ),
        Provider<ConnectivityService>(
          create: (_) => ConnectivityService(),
        ),
        
        // State Providers
        ChangeNotifierProvider<AuthProvider>(
          create: (context) => AuthProvider(
            context.read<AuthService>(),
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, DashboardProvider>(
          create: (context) => DashboardProvider(
            context.read<OdooService>(),
          ),
          update: (context, auth, previous) => previous ?? DashboardProvider(
            context.read<OdooService>(),
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, CustomerProvider>(
          create: (context) => CustomerProvider(
            context.read<OdooService>(),
          ),
          update: (context, auth, previous) => previous ?? CustomerProvider(
            context.read<OdooService>(),
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, ProductProvider>(
          create: (context) => ProductProvider(
            context.read<OdooService>(),
          ),
          update: (context, auth, previous) => previous ?? ProductProvider(
            context.read<OdooService>(),
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, OrderProvider>(
          create: (context) => OrderProvider(
            context.read<OdooService>(),
          ),
          update: (context, auth, previous) => previous ?? OrderProvider(
            context.read<OdooService>(),
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, PaymentProvider>(
          create: (context) => PaymentProvider(
            context.read<OdooService>(),
          ),
          update: (context, auth, previous) => previous ?? PaymentProvider(
            context.read<OdooService>(),
          ),
        ),
      ],
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return MaterialApp.router(
            title: 'TSH Salesperson',
            debugShowCheckedModeBanner: false,
            
            // Theme Configuration
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: ThemeMode.system,
            
            // Localization
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('ar', 'IQ'), // Arabic (Iraq) as default
            
            // Routing
            routerConfig: AppRoutes.router,
            
            // Global Builder for Connectivity and Error Handling
            builder: (context, child) {
              return ConnectivityWrapper(
                child: child ?? const SizedBox(),
              );
            },
          );
        },
      ),
    );
  }
}

class ConnectivityWrapper extends StatefulWidget {
  final Widget child;
  
  const ConnectivityWrapper({
    super.key,
    required this.child,
  });

  @override
  State<ConnectivityWrapper> createState() => _ConnectivityWrapperState();
}

class _ConnectivityWrapperState extends State<ConnectivityWrapper> {
  bool _isOnline = true;
  
  @override
  void initState() {
    super.initState();
    _checkConnectivity();
  }
  
  void _checkConnectivity() {
    Connectivity().onConnectivityChanged.listen((ConnectivityResult result) {
      setState(() {
        _isOnline = result != ConnectivityResult.none;
      });
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          widget.child,
          if (!_isOnline)
            Positioned(
              top: MediaQuery.of(context).padding.top,
              left: 0,
              right: 0,
              child: Container(
                height: 40,
                color: Colors.red.shade600,
                child: const Center(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.wifi_off,
                        color: Colors.white,
                        size: 16,
                      ),
                      SizedBox(width: 8),
                      Text(
                        'لا يوجد اتصال بالإنترنت',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
} 