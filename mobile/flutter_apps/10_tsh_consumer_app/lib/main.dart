import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'utils/tsh_theme.dart';
import 'screens/products_screen_enhanced.dart';
import 'screens/cart_screen.dart';
import 'screens/orders_screen_complete.dart';
import 'screens/account_screen.dart';
import 'screens/robot_splash_screen.dart';
import 'providers/cart_provider.dart';

void main() {
  runApp(
    const ProviderScope(
      child: TSHConsumerApp(),
    ),
  );
}

class TSHConsumerApp extends StatelessWidget {
  const TSHConsumerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TSH Consumer App',
      theme: TSHTheme.lightTheme,
      darkTheme: TSHTheme.darkTheme,
      themeMode: ThemeMode.system,

      // RTL and Arabic support
      locale: const Locale('ar', 'IQ'),
      supportedLocales: const [
        Locale('ar', 'IQ'),
        Locale('en', 'US'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      home: const AppWrapper(),
      debugShowCheckedModeBanner: false,

      // Named routes
      routes: {
        '/products': (context) => const ProductsScreenEnhanced(),
        '/cart': (context) => const CartScreen(),
        '/orders': (context) => const OrdersScreenComplete(),
        '/account': (context) => const AccountScreen(),
      },
    );
  }
}

/// Wrapper to show splash screen on first launch
class AppWrapper extends StatefulWidget {
  const AppWrapper({super.key});

  @override
  State<AppWrapper> createState() => _AppWrapperState();
}

class _AppWrapperState extends State<AppWrapper> {
  bool _showSplash = true;

  @override
  Widget build(BuildContext context) {
    if (_showSplash) {
      return RobotSplashScreen(
        onComplete: () {
          setState(() => _showSplash = false);
        },
      );
    }

    return const MainScreen();
  }
}

class MainScreen extends ConsumerStatefulWidget {
  const MainScreen({super.key});

  @override
  ConsumerState<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends ConsumerState<MainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    ProductsScreenEnhanced(),
    CartScreen(),
    OrdersScreenComplete(),
    AccountScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final cart = ref.watch(cartProvider);
    final cartCount = cart.length;

    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: Theme(
        data: Theme.of(context).copyWith(
          navigationBarTheme: NavigationBarThemeData(
            iconTheme: MaterialStateProperty.resolveWith((states) {
              if (states.contains(MaterialState.selected)) {
                return IconThemeData(color: TSHTheme.primary, size: 28);
              }
              return IconThemeData(color: TSHTheme.textSecondary, size: 24);
            }),
            labelTextStyle: MaterialStateProperty.resolveWith((states) {
              if (states.contains(MaterialState.selected)) {
                return TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: TSHTheme.primary,
                );
              }
              return TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: TSHTheme.textSecondary,
              );
            }),
          ),
        ),
        child: NavigationBar(
          selectedIndex: _selectedIndex,
          onDestinationSelected: (index) {
            setState(() => _selectedIndex = index);
          },
          backgroundColor: Colors.white,
          elevation: 8,
          shadowColor: Colors.black.withOpacity(0.1),
          indicatorColor: TSHTheme.primary.withOpacity(0.1),
          height: 70,
          destinations: [
            const NavigationDestination(
              icon: Icon(Icons.storefront_outlined),
              selectedIcon: Icon(Icons.storefront),
              label: 'المتجر',
            ),
          NavigationDestination(
            icon: cartCount > 0
                ? Badge(
                    label: Text('$cartCount'),
                    backgroundColor: TSHTheme.errorRed,
                    textColor: Colors.white,
                    child: const Icon(Icons.shopping_cart_outlined),
                  )
                : const Icon(Icons.shopping_cart_outlined),
            selectedIcon: cartCount > 0
                ? Badge(
                    label: Text('$cartCount'),
                    backgroundColor: TSHTheme.errorRed,
                    textColor: Colors.white,
                    child: const Icon(Icons.shopping_cart),
                  )
                : const Icon(Icons.shopping_cart),
            label: 'السلة',
          ),
          const NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined),
            selectedIcon: Icon(Icons.receipt_long),
            label: 'طلباتي',
          ),
          const NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'حسابي',
          ),
        ],
      ),
      ),
    );
  }
}

class PlaceholderScreen extends StatelessWidget {
  final String title;

  const PlaceholderScreen({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.construction_outlined,
              size: 80,
              color: TSHTheme.mutedForeground,
            ),
            const SizedBox(height: 24),
            Text(
              '$title - قيد التطوير',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: TSHTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'هذه الميزة قيد التطوير حالياً',
              style: TextStyle(
                fontSize: 16,
                color: TSHTheme.mutedForeground,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
