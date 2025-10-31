import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'utils/tsh_theme.dart';
import 'screens/products_screen_enhanced.dart';
import 'screens/cart_screen.dart';

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

      home: const MainScreen(),
      debugShowCheckedModeBanner: false,

      // Named routes
      routes: {
        '/products': (context) => const ProductsScreenEnhanced(),
        '/cart': (context) => const CartScreen(),
      },
    );
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
    PlaceholderScreen(title: 'الطلبات'),
    PlaceholderScreen(title: 'الحساب'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() => _selectedIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.shopping_bag_outlined),
            selectedIcon: Icon(Icons.shopping_bag),
            label: 'المنتجات',
          ),
          NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined),
            selectedIcon: Icon(Icons.receipt_long),
            label: 'طلباتي',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'حسابي',
          ),
        ],
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
