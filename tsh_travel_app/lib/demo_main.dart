import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:tsh_core_package/tsh_core_package.dart';

// Import all the BLoCs
import 'features/dashboard/presentation/blocs/dashboard_bloc.dart';
import 'features/dashboard/presentation/blocs/dashboard_event.dart';
import 'features/auth/presentation/blocs/auth_bloc.dart';
import 'features/customers/presentation/blocs/customers_bloc.dart';
import 'features/profile/presentation/blocs/profile_bloc.dart';

// Import all the pages
import 'features/dashboard/presentation/pages/dashboard_page.dart';
import 'features/sales/presentation/pages/sales_page.dart';
import 'features/products/presentation/pages/products_page.dart';
import 'features/orders/presentation/pages/orders_page.dart';
import 'features/customers/presentation/pages/customers_page.dart';
import 'features/profile/presentation/pages/profile_page.dart';

// Import DI setup
import 'core/di/service_locator.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  setupServiceLocator();
  runApp(const TSHDemoApp());
}

class TSHDemoApp extends StatelessWidget {
  const TSHDemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (context) => AuthBloc(getIt<AuthService>())..add(AuthCheckRequested())),
        BlocProvider(create: (context) => DashboardBloc(getIt<AuthService>())..add(DashboardLoadRequested())),
        BlocProvider(create: (context) => CustomersBloc()..add(LoadCustomers())),
        BlocProvider(create: (context) => ProfileBloc()..add(LoadProfile())),
      ],
      child: ChangeNotifierProvider<LocaleService>(
        create: (context) => getIt<LocaleService>(),
        child: Consumer<LocaleService>(
          builder: (context, localeService, child) {
            return MaterialApp(
              title: 'TSH Travel Sales - Demo',
              theme: AppTheme.lightTheme,
              darkTheme: AppTheme.darkTheme,
              locale: localeService.currentLocale,
              localizationsDelegates: const [
                AppLocalizations.delegate,
                GlobalMaterialLocalizations.delegate,
                GlobalWidgetsLocalizations.delegate,
                GlobalCupertinoLocalizations.delegate,
              ],
              supportedLocales: AppLocalizations.supportedLocales,
              home: const TSHMainDemo(),
              debugShowCheckedModeBanner: false,
            );
          },
        ),
      ),
    );
  }
}

class TSHMainDemo extends StatefulWidget {
  const TSHMainDemo({super.key});

  @override
  State<TSHMainDemo> createState() => _TSHMainDemoState();
}

class _TSHMainDemoState extends State<TSHMainDemo> {
  int _currentIndex = 0;
  late PageController _pageController;

  final List<Widget> _pages = const [
    DashboardPage(),
    SalesPage(),
    ProductsPage(),
    OrdersPage(),
    CustomersPage(),
    ProfilePage(),
  ];

  final List<BottomNavigationBarItem> _navItems = const [
    BottomNavigationBarItem(
      icon: Icon(Icons.dashboard),
      label: 'Dashboard',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.trending_up),
      label: 'Sales',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.inventory_2),
      label: 'Products',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.receipt_long),
      label: 'Orders',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.people),
      label: 'Customers',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.person),
      label: 'Profile',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView(
        controller: _pageController,
        onPageChanged: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        children: _pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
          _pageController.animateToPage(
            index,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeInOut,
          );
        },
        items: _navItems,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textSecondary,
        backgroundColor: AppColors.surface,
        elevation: 8,
      ),
    );
  }
}
