import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/api/api_client.dart';
import 'features/gps_tracking/services/gps_service.dart';
import 'features/money_transfer/presentation/blocs/money_transfer_bloc.dart';
import 'features/money_transfer/presentation/pages/money_transfer_page.dart';
import 'features/customers/presentation/blocs/customers_bloc.dart';
import 'features/customers/presentation/pages/customers_page.dart';
import 'providers/language_provider.dart';
import 'localization/app_localizations.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize critical services for fraud prevention
  await _initializeCriticalServices();
  
  runApp(const TSHFraudPreventionApp());
}

/// Initialize critical services for fraud prevention and money transfer tracking
Future<void> _initializeCriticalServices() async {
  try {
    // Initialize API client authentication
    await ApiClient.instance.loadAuthToken();
    
    // Initialize GPS service for location verification
    final gpsInitialized = await GPSService.instance.initialize();
    if (gpsInitialized) {
      print('🎯 GPS Service initialized successfully for fraud prevention');
    } else {
      print('⚠️ GPS Service initialization failed - location verification may not work');
    }
    
    print('✅ TSH Fraud Prevention System initialized');
  } catch (e) {
    print('❌ Critical service initialization failed: $e');
  }
}

class TSHFraudPreventionApp extends StatelessWidget {
  const TSHFraudPreventionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (context) => LanguageProvider(),
        ),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider(
            create: (context) => MoneyTransferBloc()..add(LoadDashboard()),
          ),
          BlocProvider(
            create: (context) => CustomersBloc()..add(LoadCustomers()),
          ),
        ],
        child: Consumer<LanguageProvider>(
          builder: (context, languageProvider, child) {
            return MaterialApp(
              title: 'TSH Travel Sales - Fraud Prevention',
              theme: _buildTheme(),
              darkTheme: _buildDarkTheme(),
              debugShowCheckedModeBanner: false,
              locale: languageProvider.currentLocale,
              
              // MANDATORY: Bilingual localization support
              localizationsDelegates: const [
                AppLocalizations.delegate,
                GlobalMaterialLocalizations.delegate,
                GlobalWidgetsLocalizations.delegate,
                GlobalCupertinoLocalizations.delegate,
              ],
              supportedLocales: AppLocalizations.supportedLocales,
              
              home: const MainHomePage(),
              
              // Navigation routes
              routes: {
                '/money-transfer': (context) => const MoneyTransferPage(),
                '/dashboard': (context) => const MainHomePage(),
              },
            );
          },
        ),
      ),
    );
  }

  ThemeData _buildTheme() {
    return ThemeData(
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
      cardTheme: CardThemeData(
        elevation: 4,
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF1565C0),
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
  }

  ThemeData _buildDarkTheme() {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF1565C0),
        brightness: Brightness.dark,
      ),
      useMaterial3: true,
    );
  }
}

class MainHomePage extends StatefulWidget {
  const MainHomePage({super.key});

  @override
  State<MainHomePage> createState() => _MainHomePageState();
}

class _MainHomePageState extends State<MainHomePage> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const SimpleDashboardPage(),
    const MoneyTransferPage(),
    const CustomersPage(),
    const SimpleAlertsPage(),
    const SimpleProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Text(localizations.appTitle),
          actions: [
            // Language switcher
            IconButton(
              icon: Icon(isArabic ? Icons.language : Icons.translate),
              onPressed: () => _showLanguageSelector(context),
            ),
            
            // Notifications
            Consumer<LanguageProvider>(
              builder: (context, provider, child) {
                return IconButton(
                  icon: const Badge(
                    backgroundColor: Colors.red,
                    smallSize: 8,
                    child: Icon(Icons.notifications),
                  ),
                  onPressed: () => _showNotifications(context),
                );
              },
            ),
          ],
        ),
        body: IndexedStack(
          index: _currentIndex,
          children: _pages,
        ),
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          selectedItemColor: const Color(0xFF1565C0),
          unselectedItemColor: Colors.grey,
          items: [
            BottomNavigationBarItem(
              icon: const Icon(Icons.dashboard),
              label: localizations.dashboard,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.security),
              label: localizations.moneyTransfer,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.people),
              label: 'Customers',
            ),
            BottomNavigationBarItem(
              icon: const Badge(
                backgroundColor: Colors.red,
                smallSize: 8,
                child: Icon(Icons.warning),
              ),
              label: localizations.alerts,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.person),
              label: localizations.profile,
            ),
          ],
        ),
      ),
    );
  }

  void _showLanguageSelector(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.language),
              title: const Text('English'),
              trailing: Localizations.localeOf(context).languageCode == 'en'
                  ? const Icon(Icons.check, color: Colors.green)
                  : null,
              onTap: () {
                context.read<LanguageProvider>().setLanguage('en');
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.language),
              title: const Text('العربية'),
              trailing: Localizations.localeOf(context).languageCode == 'ar'
                  ? const Icon(Icons.check, color: Colors.green)
                  : null,
              onTap: () {
                context.read<LanguageProvider>().setLanguage('ar');
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showNotifications(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    
    showModalBottomSheet(
      context: context,
      builder: (context) => Directionality(
        textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
        child: Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                localizations.recentAlerts,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              
              // Critical Alert Example
              Card(
                color: Colors.red.shade50,
                child: ListTile(
                  leading: const Icon(Icons.error, color: Colors.red),
                  title: Text(
                    isArabic 
                        ? 'تنبيه بالغ الأهمية: تحويل مشبوه'
                        : 'Critical Alert: Suspicious Transfer',
                  ),
                  subtitle: Text(
                    isArabic
                        ? 'تم اكتشاف تضارب في العمولة - انتباه فوري مطلوب'
                        : 'Commission discrepancy detected - immediate attention required',
                  ),
                  trailing: Text(
                    '5 min ago',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
              
              // Info Alert
              Card(
                color: Colors.green.shade50,
                child: ListTile(
                  leading: const Icon(Icons.check_circle, color: Colors.green),
                  title: Text(
                    isArabic 
                        ? 'تم التحقق من التحويل بنجاح'
                        : 'Transfer Verified Successfully',
                  ),
                  subtitle: Text(
                    isArabic
                        ? 'تحويل بقيمة 1,250,000 د.ع تم التحقق منه'
                        : 'Transfer of 1,250,000 IQD has been verified',
                  ),
                  trailing: Text(
                    '1 hour ago',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Simplified Dashboard Page
class SimpleDashboardPage extends StatelessWidget {
  const SimpleDashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Section
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      const Color(0xFF1565C0),
                      const Color(0xFF1565C0).withOpacity(0.8),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      localizations.welcomeBack,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      isArabic 
                          ? 'نظام منع الاحتيال ومراقبة التحويلات'
                          : 'Fraud Prevention & Transfer Monitoring',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              
              // Metrics Row
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      isArabic ? 'التحويلات اليوم' : 'Today\'s Transfers',
                      '8',
                      Icons.swap_horiz,
                      Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricCard(
                      isArabic ? 'المبلغ الإجمالي' : 'Total Amount',
                      '12.5K',
                      Icons.attach_money,
                      Colors.green,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      isArabic ? 'العمولة' : 'Commission',
                      '281',
                      Icons.account_balance_wallet,
                      Colors.orange,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricCard(
                      isArabic ? 'تنبيهات الأمان' : 'Security Alerts',
                      '2',
                      Icons.warning,
                      Colors.red,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Quick Actions
              Text(
                isArabic ? 'الإجراءات السريعة' : 'Quick Actions',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              
              const SizedBox(height: 12),
              
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        // Navigate to money transfer
                      },
                      icon: const Icon(Icons.security),
                      label: Text(
                        isArabic ? 'تحويل جديد' : 'New Transfer',
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1565C0),
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        // Show GPS status
                      },
                      icon: const Icon(Icons.gps_fixed),
                      label: Text(
                        isArabic ? 'حالة GPS' : 'GPS Status',
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: Colors.grey,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// Simplified Alerts Page
class SimpleAlertsPage extends StatelessWidget {
  const SimpleAlertsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Text(
                localizations.alerts,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                isArabic 
                    ? 'تنبيهات الأمان ومنع الاحتيال'
                    : 'Security alerts and fraud prevention notifications',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 24),
              
              // Critical Alert Example
              _buildAlertCard(
                context,
                title: isArabic 
                    ? 'تنبيه بالغ الأهمية: تحويل مشبوه'
                    : 'Critical Alert: Suspicious Transfer',
                subtitle: isArabic
                    ? 'تم اكتشاف تضارب في العمولة - انتباه فوري مطلوب'
                    : 'Commission discrepancy detected - immediate attention required',
                icon: Icons.error,
                color: Colors.red,
                time: '5 min ago',
              ),
              
              const SizedBox(height: 12),
              
              // Warning Alert
              _buildAlertCard(
                context,
                title: isArabic 
                    ? 'تحذير: دقة الموقع منخفضة'
                    : 'Warning: Low GPS Accuracy',
                subtitle: isArabic
                    ? 'تحقق من إعدادات الموقع للحصول على تتبع أفضل'
                    : 'Check location settings for better tracking accuracy',
                icon: Icons.location_off,
                color: Colors.orange,
                time: '15 min ago',
              ),
              
              const SizedBox(height: 12),
              
              // Info Alert
              _buildAlertCard(
                context,
                title: isArabic 
                    ? 'تم التحقق من التحويل بنجاح'
                    : 'Transfer Verified Successfully',
                subtitle: isArabic
                    ? 'تحويل بقيمة 1,250,000 د.ع تم التحقق منه'
                    : 'Transfer of 1,250,000 IQD has been verified',
                icon: Icons.check_circle,
                color: Colors.green,
                time: '1 hour ago',
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildAlertCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required String time,
  }) {
    return Card(
      elevation: 2,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.1),
          child: Icon(icon, color: color),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(subtitle),
            const SizedBox(height: 4),
            Text(
              time,
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 12,
              ),
            ),
          ],
        ),
        isThreeLine: true,
      ),
    );
  }
}

// Simplified Profile Page
class SimpleProfilePage extends StatelessWidget {
  const SimpleProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              // Profile Header
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      const Color(0xFF1565C0),
                      const Color(0xFF1565C0).withOpacity(0.8),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    const CircleAvatar(
                      radius: 40,
                      backgroundColor: Colors.white,
                      child: Icon(
                        Icons.person,
                        size: 40,
                        color: Color(0xFF1565C0),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      isArabic ? 'أحمد محمد' : 'Ahmed Mohammed',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isArabic ? 'مندوب مبيعات متنقل' : 'Travel Salesperson',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'ID: TSH-SP-001',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              
              // Settings Section
              Card(
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.language, color: Color(0xFF1565C0)),
                      title: Text(isArabic ? 'اللغة' : 'Language'),
                      subtitle: Text(isArabic ? 'العربية' : 'English'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {
                        // Show language picker
                      },
                    ),
                    const Divider(),
                    ListTile(
                      leading: const Icon(Icons.security, color: Color(0xFF1565C0)),
                      title: Text(isArabic ? 'مصادقة التحويل' : 'Transfer Authentication'),
                      subtitle: Text(isArabic ? 'مفعل' : 'Enabled'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {
                        // Security settings
                      },
                    ),
                    const Divider(),
                    ListTile(
                      leading: const Icon(Icons.gps_fixed, color: Color(0xFF1565C0)),
                      title: Text(isArabic ? 'التتبع المباشر' : 'Live Tracking'),
                      subtitle: Text(isArabic ? 'نشط' : 'Active'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {
                        // GPS tracking settings
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
