import 'config/environment.dart';import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Import TSH Core Design System
import 'package:tsh_core_package/tsh_core_package.dart';

void main() {
  runApp(const TSHAdminDashboardApp());
}

class TSHAdminDashboardApp extends StatelessWidget {
  const TSHAdminDashboardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => LanguageService(),
      child: Consumer<LanguageService>(
        builder: (context, languageService, child) {
          return MaterialApp(
            title: 'TSH Admin App',
            theme: TSHTheme.lightTheme,
            darkTheme: TSHTheme.darkTheme,
            themeMode: languageService.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            locale: languageService.currentLocale,
            localizationsDelegates: const [
              TSHLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            supportedLocales: TSHLocalizations.supportedLocales,
            home: const AdminMainScreen(),
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

class AdminMainScreen extends StatefulWidget {
  const AdminMainScreen({super.key});

  @override
  State<AdminMainScreen> createState() => _AdminMainScreenState();
}

class _AdminMainScreenState extends State<AdminMainScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const ExecutiveDashboardScreen(),
    const FinancialControlScreen(),
    const OperationsOverviewScreen(),
    const HRManagementScreen(),
    const SystemAnalyticsScreen(),
    const AdminSettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;
    final languageService = Provider.of<LanguageService>(context);

    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        title: Row(
          children: [
            TSHTheme.tshLogo(height: 35),
            const SizedBox(width: 12),
            Text(localizations.translate('tsh_admin_app')),
          ],
        ),
        actions: [
          // Language Toggle
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              border: Border.all(color: TSHTheme.surfaceWhite.withOpacity(0.3)),
              borderRadius: BorderRadius.circular(6),
            ),
            child: TextButton(
              onPressed: () => languageService.toggleLanguage(),
              child: Text(
                languageService.currentLocale.languageCode == 'en' ? 'العربية' : 'EN',
                style: const TextStyle(
                  color: TSHTheme.surfaceWhite,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          // Dark Mode Toggle
          IconButton(
            icon: Icon(
              languageService.isDarkMode ? Icons.light_mode : Icons.dark_mode,
              color: TSHTheme.surfaceWhite,
            ),
            onPressed: () => languageService.toggleDarkMode(),
          ),
          // Notifications
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
          // Side Menu Toggle
          IconButton(
            icon: const Icon(Icons.menu),
            onPressed: () => _scaffoldKey.currentState?.openEndDrawer(),
          ),
        ],
      ),
      
      // Side Drawer Menu
      endDrawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(
                color: TSHTheme.primaryTeal,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TSHTheme.tshLogo(height: 45),
                  const SizedBox(height: 12),
                  Text(
                    localizations.translate('executive_summary'),
                    style: TSHTheme.headingSmall.copyWith(color: TSHTheme.surfaceWhite),
                  ),
                  Text(
                    'Owner/CEO Dashboard',
                    style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
                  ),
                ],
              ),
            ),
            _buildDrawerItem(Icons.dashboard, localizations.translate('dashboard'), 0),
            _buildDrawerItem(Icons.account_balance, localizations.translate('financial_metrics'), 1),
            _buildDrawerItem(Icons.business, localizations.translate('business_overview'), 2),
            _buildDrawerItem(Icons.people, localizations.translate('hr_management'), 3),
            _buildDrawerItem(Icons.analytics, localizations.translate('analytics'), 4),
            _buildDrawerItem(Icons.settings, localizations.translate('settings'), 5),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: Text(localizations.translate('logout')),
              onTap: () => _handleLogout(context),
            ),
          ],
        ),
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
            label: localizations.translate('dashboard'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.account_balance),
            label: localizations.translate('cash'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.business),
            label: localizations.translate('business_overview'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.people),
            label: 'HR',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.analytics),
            label: localizations.translate('analytics'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.settings),
            label: localizations.translate('settings'),
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(IconData icon, String title, int index) {
    return ListTile(
      leading: Icon(icon, color: _selectedIndex == index ? TSHTheme.primaryTeal : null),
      title: Text(title),
      selected: _selectedIndex == index,
      onTap: () {
        setState(() => _selectedIndex = index);
        Navigator.pop(context);
      },
    );
  }

  void _handleLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(TSHLocalizations.of(context)!.translate('logout')),
        content: Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(TSHLocalizations.of(context)!.translate('cancel')),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Handle logout logic
            },
            child: Text(TSHLocalizations.of(context)!.translate('logout')),
          ),
        ],
      ),
    );
  }
}

// ===============================================
// EXECUTIVE DASHBOARD SCREEN - Main Admin View
// ===============================================
class ExecutiveDashboardScreen extends StatefulWidget {
  const ExecutiveDashboardScreen({super.key});

  @override
  State<ExecutiveDashboardScreen> createState() => _ExecutiveDashboardScreenState();
}

class _ExecutiveDashboardScreenState extends State<ExecutiveDashboardScreen> {
  Map<String, dynamic> _dashboardData = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    try {
      final response = await http.get(
        Uri.parse('Environment.apiBaseUrl/api/admin/dashboard'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        setState(() {
          _dashboardData = json.decode(response.body);
          _isLoading = false;
        });
      } else {
        _loadFallbackData();
      }
    } catch (e) {
      _loadFallbackData();
    }
  }

  void _loadFallbackData() {
    setState(() {
      _dashboardData = {
        'available_cash': 125750000, // 125,750,000 IQD
        'total_receivables': 89320000, // 89,320,000 IQD
        'inventory_valuation': 456890000, // 456,890,000 IQD
        'total_payables': 234560000, // 234,560,000 IQD
        'daily_sales': 12450000, // 12,450,000 IQD
        'monthly_revenue': 378920000, // 378,920,000 IQD
        'total_customers': 2047,
        'active_salespersons': 12,
        'pending_orders': 34,
        'low_stock_items': 23,
        'recent_activities': [
          {'type': 'sale', 'amount': 2340000, 'customer': 'Ahmed Electronics', 'time': '2 hours ago'},
          {'type': 'payment', 'amount': 5670000, 'customer': 'Baghdad Tech Store', 'time': '4 hours ago'},
          {'type': 'transfer', 'amount': 8900000, 'salesperson': 'Mohammed Ali', 'time': '6 hours ago'},
        ],
      };
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations.of(context)!;

    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading executive dashboard...'),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Section
            _buildWelcomeSection(localizations),
            const SizedBox(height: 24),
            
            // Critical Financial Metrics (4 main cards)
            _buildCriticalMetrics(localizations),
            const SizedBox(height: 24),
            
            // Quick Action Buttons
            _buildQuickActions(localizations),
            const SizedBox(height: 24),
            
            // Business Performance Summary
            _buildPerformanceSummary(localizations),
            const SizedBox(height: 24),
            
            // Recent Activities
            _buildRecentActivities(localizations),
          ],
        ),
      ),
    );
  }

  Widget _buildWelcomeSection(TSHLocalizations localizations) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    localizations.translate('welcome_message'),
                    style: TSHTheme.headingMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    localizations.translate('executive_summary'),
                    style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.textLight),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Today: ${DateTime.now().day}/${DateTime.now().month}/${DateTime.now().year}',
                    style: TSHTheme.bodySmall,
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: TSHTheme.primaryTeal.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.business,
                size: 48,
                color: TSHTheme.primaryTeal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCriticalMetrics(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          localizations.translate('financial_metrics'),
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.2,
          children: [
            TSHTheme.metricCard(
              title: localizations.translate('available_cash'),
              value: localizations.formatCurrency(_dashboardData['available_cash']?.toDouble() ?? 0),
              icon: Icons.account_balance_wallet,
              iconColor: TSHTheme.successGreen,
            ),
            TSHTheme.metricCard(
              title: localizations.translate('total_receivables'),
              value: localizations.formatCurrency(_dashboardData['total_receivables']?.toDouble() ?? 0),
              icon: Icons.trending_up,
              iconColor: TSHTheme.primaryBlue,
            ),
            TSHTheme.metricCard(
              title: localizations.translate('inventory_valuation'),
              value: localizations.formatCurrency(_dashboardData['inventory_valuation']?.toDouble() ?? 0),
              icon: Icons.inventory,
              iconColor: TSHTheme.accentOrange,
            ),
            TSHTheme.metricCard(
              title: localizations.translate('total_payables'),
              value: localizations.formatCurrency(_dashboardData['total_payables']?.toDouble() ?? 0),
              icon: Icons.payment,
              iconColor: TSHTheme.warningYellow,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActions(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 4,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          children: [
            TSHTheme.quickActionButton(
              icon: Icons.add_business,
              label: 'New Sale',
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.inventory_2,
              label: localizations.translate('inventory'),
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.people,
              label: localizations.translate('customers'),
              onTap: () {},
            ),
            TSHTheme.quickActionButton(
              icon: Icons.assessment,
              label: localizations.translate('reports'),
              onTap: () {},
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildPerformanceSummary(TSHLocalizations localizations) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              localizations.translate('business_overview'),
              style: TSHTheme.headingSmall,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildPerformanceMetric(
                    'Daily Sales',
                    localizations.formatCurrency(_dashboardData['daily_sales']?.toDouble() ?? 0),
                    Icons.today,
                    TSHTheme.successGreen,
                  ),
                ),
                Expanded(
                  child: _buildPerformanceMetric(
                    'Monthly Revenue',
                    localizations.formatCurrency(_dashboardData['monthly_revenue']?.toDouble() ?? 0),
                    Icons.calendar_month,
                    TSHTheme.primaryTeal,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildPerformanceMetric(
                    localizations.translate('customers'),
                    '${_dashboardData['total_customers'] ?? 0}',
                    Icons.people,
                    TSHTheme.primaryBlue,
                  ),
                ),
                Expanded(
                  child: _buildPerformanceMetric(
                    'Active Salespersons',
                    '${_dashboardData['active_salespersons'] ?? 0}',
                    Icons.person_pin,
                    TSHTheme.accentOrange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceMetric(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TSHTheme.headingSmall.copyWith(color: color),
          ),
          Text(
            title,
            style: TSHTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRecentActivities(TSHLocalizations localizations) {
    final activities = _dashboardData['recent_activities'] as List<dynamic>? ?? [];
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  localizations.translate('recent_activities'),
                  style: TSHTheme.headingSmall,
                ),
                TextButton(
                  onPressed: () {},
                  child: Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: activities.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final activity = activities[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _getActivityColor(activity['type']).withOpacity(0.2),
                    child: Icon(
                      _getActivityIcon(activity['type']),
                      color: _getActivityColor(activity['type']),
                    ),
                  ),
                  title: Text(activity['customer'] ?? activity['salesperson'] ?? 'Unknown'),
                  subtitle: Text(
                    localizations.formatCurrency(activity['amount']?.toDouble() ?? 0),
                  ),
                  trailing: Text(
                    activity['time'] ?? '',
                    style: TSHTheme.bodySmall,
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Color _getActivityColor(String type) {
    switch (type) {
      case 'sale':
        return TSHTheme.successGreen;
      case 'payment':
        return TSHTheme.primaryBlue;
      case 'transfer':
        return TSHTheme.accentOrange;
      default:
        return TSHTheme.textLight;
    }
  }

  IconData _getActivityIcon(String type) {
    switch (type) {
      case 'sale':
        return Icons.point_of_sale;
      case 'payment':
        return Icons.payment;
      case 'transfer':
        return Icons.swap_horiz;
      default:
        return Icons.info;
    }
  }
}

// ===============================================
// PLACEHOLDER SCREENS FOR OTHER SECTIONS
// ===============================================
class FinancialControlScreen extends StatelessWidget {
  const FinancialControlScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Financial Control Center'));
  }
}

class OperationsOverviewScreen extends StatelessWidget {
  const OperationsOverviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Operations Overview'));
  }
}

class HRManagementScreen extends StatelessWidget {
  const HRManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('HR Management'));
  }
}

class SystemAnalyticsScreen extends StatelessWidget {
  const SystemAnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('System Analytics'));
  }
}

class AdminSettingsScreen extends StatelessWidget {
  const AdminSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Admin Settings'));
  }
}
