import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(const TSHAdminDashboardDemoApp());
}

class TSHAdminDashboardDemoApp extends StatelessWidget {
  const TSHAdminDashboardDemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => DemoLanguageService(),
      child: Consumer<DemoLanguageService>(
        builder: (context, languageService, child) {
          return MaterialApp(
            title: 'TSH Admin Dashboard - Demo Mode',
            theme: ThemeData(
              colorScheme: ColorScheme.fromSeed(
                seedColor: const Color(0xFF1565C0), // TSH Blue
                brightness: Brightness.light,
              ),
              useMaterial3: true,
              appBarTheme: const AppBarTheme(
                backgroundColor: Color(0xFF1565C0),
                foregroundColor: Colors.white,
                elevation: 0,
                centerTitle: true,
              ),
            ),
            darkTheme: ThemeData(
              colorScheme: ColorScheme.fromSeed(
                seedColor: const Color(0xFF1565C0),
                brightness: Brightness.dark,
              ),
              useMaterial3: true,
            ),
            themeMode: languageService.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            locale: languageService.currentLocale,
            localizationsDelegates: const [
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            supportedLocales: const [
              Locale('en', 'US'),
              Locale('ar', 'SA'),
            ],
            home: const DemoAdminMainScreen(),
            debugShowCheckedModeBanner: false,
            builder: (context, child) {
              return Directionality(
                textDirection: languageService.isRTL 
                    ? TextDirection.rtl 
                    : TextDirection.ltr,
                child: child!,
              );
            },
          );
        },
      ),
    );
  }
}

class DemoLanguageService extends ChangeNotifier {
  Locale _currentLocale = const Locale('en', 'US');
  bool _isDarkMode = false;

  Locale get currentLocale => _currentLocale;
  bool get isDarkMode => _isDarkMode;
  bool get isRTL => _currentLocale.languageCode == 'ar';

  void toggleLanguage() {
    _currentLocale = _currentLocale.languageCode == 'en' 
        ? const Locale('ar', 'SA')
        : const Locale('en', 'US');
    notifyListeners();
  }

  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
  }
}

class DemoAdminMainScreen extends StatefulWidget {
  const DemoAdminMainScreen({super.key});

  @override
  State<DemoAdminMainScreen> createState() => _DemoAdminMainScreenState();
}

class _DemoAdminMainScreenState extends State<DemoAdminMainScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const DemoExecutiveDashboardScreen(),
    const DemoFinancialControlScreen(),
    const DemoOperationsOverviewScreen(),
    const DemoHRManagementScreen(),
    const DemoSystemAnalyticsScreen(),
    const DemoAdminSettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<DemoLanguageService>(context);
    final isArabic = languageService.currentLocale.languageCode == 'ar';

    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(4),
              ),
              child: const Text(
                'TSH',
                style: TextStyle(
                  color: Color(0xFF1565C0),
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Text(isArabic ? 'لوحة إدارة TSH' : 'TSH Admin Dashboard'),
          ],
        ),
        actions: [
          // Language Toggle
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.white.withOpacity(0.3)),
              borderRadius: BorderRadius.circular(6),
            ),
            child: TextButton(
              onPressed: () => languageService.toggleLanguage(),
              child: Text(
                languageService.currentLocale.languageCode == 'en' ? 'العربية' : 'EN',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          // Dark Mode Toggle
          IconButton(
            icon: Icon(
              languageService.isDarkMode ? Icons.light_mode : Icons.dark_mode,
              color: Colors.white,
            ),
            onPressed: () => languageService.toggleDarkMode(),
          ),
          // Notifications
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(isArabic ? 'لا توجد إشعارات جديدة' : 'No new notifications'),
                ),
              );
            },
          ),
        ],
      ),
      
      body: _screens[_selectedIndex],
      
      // Bottom Navigation Bar
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.dashboard),
            label: isArabic ? 'الرئيسية' : 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.account_balance),
            label: isArabic ? 'المالية' : 'Financial',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.business),
            label: isArabic ? 'العمليات' : 'Operations',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.people),
            label: isArabic ? 'الموارد البشرية' : 'HR',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.analytics),
            label: isArabic ? 'التحليلات' : 'Analytics',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.settings),
            label: isArabic ? 'الإعدادات' : 'Settings',
          ),
        ],
      ),
    );
  }
}

class DemoExecutiveDashboardScreen extends StatelessWidget {
  const DemoExecutiveDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<DemoLanguageService>(context);
    final isArabic = languageService.currentLocale.languageCode == 'ar';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome Section
          Card(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isArabic ? 'أهلاً وسهلاً بك في نظام TSH ERP' : 'Welcome to TSH ERP System',
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isArabic 
                        ? 'لوحة تحكم شاملة لإدارة جميع العمليات التجارية'
                        : 'Comprehensive dashboard for managing all business operations',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    isArabic ? 'وضع التشغيل: تجريبي' : 'Mode: Demo',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Critical Metrics
          Text(
            isArabic ? 'المقاييس الأساسية' : 'Key Metrics',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 12),
          
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            childAspectRatio: 1.5,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            children: [
              _buildMetricCard(
                context,
                icon: Icons.trending_up,
                title: isArabic ? 'الإيرادات اليومية' : 'Daily Revenue',
                value: '\$12,430',
                change: '+15.3%',
                color: Colors.green,
                isArabic: isArabic,
              ),
              _buildMetricCard(
                context,
                icon: Icons.shopping_bag,
                title: isArabic ? 'الطلبات' : 'Orders',
                value: '342',
                change: '+8.1%',
                color: Colors.blue,
                isArabic: isArabic,
              ),
              _buildMetricCard(
                context,
                icon: Icons.people,
                title: isArabic ? 'العملاء' : 'Customers',
                value: '1,248',
                change: '+12.5%',
                color: Colors.orange,
                isArabic: isArabic,
              ),
              _buildMetricCard(
                context,
                icon: Icons.warning,
                title: isArabic ? 'التنبيهات' : 'Alerts',
                value: '3',
                change: '-25%',
                color: Colors.red,
                isArabic: isArabic,
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Quick Actions
          Text(
            isArabic ? 'الإجراءات السريعة' : 'Quick Actions',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 12),
          
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(isArabic ? 'تم إنشاء تقرير جديد' : 'New report created'),
                      ),
                    );
                  },
                  icon: const Icon(Icons.assessment),
                  label: Text(isArabic ? 'إنشاء تقرير' : 'Generate Report'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(isArabic ? 'تم تصدير البيانات' : 'Data exported'),
                      ),
                    );
                  },
                  icon: const Icon(Icons.download),
                  label: Text(isArabic ? 'تصدير البيانات' : 'Export Data'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCard(BuildContext context, {
    required IconData icon,
    required String title,
    required String value,
    required String change,
    required Color color,
    required bool isArabic,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 24),
                const Spacer(),
                Text(
                  change,
                  style: TextStyle(
                    color: change.startsWith('+') ? Colors.green : Colors.red,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            const Spacer(),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Placeholder screens
class DemoFinancialControlScreen extends StatelessWidget {
  const DemoFinancialControlScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<DemoLanguageService>(context);
    final isArabic = languageService.currentLocale.languageCode == 'ar';
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.account_balance, size: 64, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 16),
          Text(
            isArabic ? 'التحكم المالي' : 'Financial Control',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            isArabic ? 'قريباً...' : 'Coming Soon...',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

class DemoOperationsOverviewScreen extends StatelessWidget {
  const DemoOperationsOverviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<DemoLanguageService>(context);
    final isArabic = languageService.currentLocale.languageCode == 'ar';
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.business, size: 64, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 16),
          Text(
            isArabic ? 'نظرة عامة على العمليات' : 'Operations Overview',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            isArabic ? 'قريباً...' : 'Coming Soon...',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

class DemoHRManagementScreen extends StatelessWidget {
  const DemoHRManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<DemoLanguageService>(context);
    final isArabic = languageService.currentLocale.languageCode == 'ar';
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.people, size: 64, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 16),
          Text(
            isArabic ? 'إدارة الموارد البشرية' : 'HR Management',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            isArabic ? 'قريباً...' : 'Coming Soon...',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

class DemoSystemAnalyticsScreen extends StatelessWidget {
  const DemoSystemAnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<DemoLanguageService>(context);
    final isArabic = languageService.currentLocale.languageCode == 'ar';
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.analytics, size: 64, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 16),
          Text(
            isArabic ? 'تحليلات النظام' : 'System Analytics',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            isArabic ? 'قريباً...' : 'Coming Soon...',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

class DemoAdminSettingsScreen extends StatelessWidget {
  const DemoAdminSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final languageService = Provider.of<DemoLanguageService>(context);
    final isArabic = languageService.currentLocale.languageCode == 'ar';
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.settings, size: 64, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 16),
          Text(
            isArabic ? 'إعدادات الإدارة' : 'Admin Settings',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            isArabic ? 'قريباً...' : 'Coming Soon...',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}
