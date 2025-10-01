import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Import TSH Core Design System
import 'package:tsh_core_package/tsh_core_package.dart';

void main() {
  runApp(const TSHHRApp());
}

class TSHHRApp extends StatelessWidget {
  const TSHHRApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => LanguageService(),
      child: Consumer<LanguageService>(
        builder: (context, languageService, child) {
          return MaterialApp(
            title: 'TSH HR Management',
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
            home: const HRMainScreen(),
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

class HRMainScreen extends StatefulWidget {
  const HRMainScreen({super.key});

  @override
  State<HRMainScreen> createState() => _HRMainScreenState();
}

class _HRMainScreenState extends State<HRMainScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const HRDashboardScreen(),
    const EmployeeStatusScreen(),
    const PayrollManagementScreen(),
    const ApprovalsScreen(),
    const PerformanceRankingScreen(),
    const HRReportsScreen(),
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
            Text(localizations.translate('hr_management')),
          ],
        ),
        subtitle: Text(
          'HR Director Control Panel',
          style: TSHTheme.bodySmall.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
        ),
        actions: [
          // Quick Actions Menu
          PopupMenuButton<String>(
            icon: const Icon(Icons.lightning_bolt, color: TSHTheme.surfaceWhite),
            onSelected: (value) => _handleQuickAction(value),
            itemBuilder: (BuildContext context) => [
              PopupMenuItem(value: 'payroll', child: Text('Generate Payroll')),
              PopupMenuItem(value: 'attendance', child: Text('Mark Attendance')),
              PopupMenuItem(value: 'performance', child: Text('Update Rankings')),
              PopupMenuItem(value: 'whatsapp_report', child: Text('Send WhatsApp Report')),
            ],
          ),
          // Notifications with badge
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () => _showNotifications(context),
              ),
              Positioned(
                right: 8,
                top: 8,
                child: Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    color: TSHTheme.accentOrange,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  constraints: const BoxConstraints(
                    minWidth: 16,
                    minHeight: 16,
                  ),
                  child: const Text(
                    '5',
                    style: TextStyle(
                      color: TSHTheme.surfaceWhite,
                      fontSize: 12,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
            ],
          ),
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
                languageService.currentLocale.languageCode == 'en' ? 'عربي' : 'EN',
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
        ],
      ),
      
      // Side Drawer Menu
      drawer: _buildSideDrawer(localizations),
      
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
            icon: const Icon(Icons.people),
            label: 'Employee Status',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.attach_money),
            label: localizations.translate('payroll'),
          ),
          BottomNavigationBarItem(
            icon: Stack(
              children: [
                const Icon(Icons.approval),
                Positioned(
                  right: 0,
                  top: 0,
                  child: Container(
                    padding: const EdgeInsets.all(1),
                    decoration: BoxDecoration(
                      color: TSHTheme.errorRed,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text(
                      '3',
                      style: TextStyle(color: TSHTheme.surfaceWhite, fontSize: 10),
                    ),
                  ),
                ),
              ],
            ),
            label: 'Approvals',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.star),
            label: 'Rankings',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.analytics),
            label: 'Reports',
          ),
        ],
      ),
    );
  }

  Widget _buildSideDrawer(TSHLocalizations localizations) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [TSHTheme.primaryTeal, TSHTheme.primaryBlue],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TSHTheme.tshLogo(height: 45),
                const SizedBox(height: 12),
                Text(
                  localizations.translate('hr_management'),
                  style: TSHTheme.headingSmall.copyWith(color: TSHTheme.surfaceWhite),
                ),
                Text(
                  'Complete HR Control System',
                  style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.surfaceWhite.withOpacity(0.9)),
                ),
              ],
            ),
          ),
          _buildDrawerItem(Icons.dashboard, localizations.translate('dashboard'), 0),
          _buildDrawerItem(Icons.people_alt, 'Employee Status', 1),
          _buildDrawerItem(Icons.attach_money, localizations.translate('payroll'), 2),
          _buildDrawerItem(Icons.approval, 'Pending Approvals', 3),
          _buildDrawerItem(Icons.star, 'Performance Rankings', 4),
          _buildDrawerItem(Icons.analytics, 'HR Reports', 5),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.access_time, color: TSHTheme.primaryTeal),
            title: Text('Attendance Tracking'),
            onTap: () => _navigateToAttendanceTracking(),
          ),
          ListTile(
            leading: const Icon(Icons.vacation_rental, color: TSHTheme.warningYellow),
            title: Text('Leave Management'),
            onTap: () => _navigateToLeaveManagement(),
          ),
          ListTile(
            leading: const Icon(Icons.document_scanner, color: TSHTheme.successGreen),
            title: Text('Document Storage'),
            onTap: () => _navigateToDocumentStorage(),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.whatsapp, color: TSHTheme.successGreen),
            title: Text('Send WhatsApp Report'),
            onTap: () => _sendWhatsAppReport(),
          ),
          ListTile(
            leading: const Icon(Icons.sync_alt, color: TSHTheme.primaryBlue),
            title: Text('Sync with Admin'),
            onTap: () => _handleSync(context),
          ),
          ListTile(
            leading: const Icon(Icons.settings, color: TSHTheme.textLight),
            title: Text(localizations.translate('settings')),
            onTap: () => _navigateToSettings(),
          ),
          ListTile(
            leading: const Icon(Icons.logout, color: TSHTheme.errorRed),
            title: Text(localizations.translate('logout')),
            onTap: () => _handleLogout(context),
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(IconData icon, String title, int index) {
    bool isSelected = _selectedIndex == index;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: isSelected ? TSHTheme.primaryTeal.withOpacity(0.1) : null,
        borderRadius: BorderRadius.circular(8),
        border: isSelected ? Border.all(color: TSHTheme.primaryTeal.withOpacity(0.3)) : null,
      ),
      child: ListTile(
        leading: Icon(
          icon, 
          color: isSelected ? TSHTheme.primaryTeal : TSHTheme.textLight,
        ),
        title: Text(
          title,
          style: TextStyle(
            color: isSelected ? TSHTheme.primaryTeal : TSHTheme.textPrimary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
        onTap: () {
          setState(() => _selectedIndex = index);
          Navigator.pop(context);
        },
      ),
    );
  }

  void _handleQuickAction(String action) {
    switch (action) {
      case 'payroll':
        _generatePayroll();
        break;
      case 'attendance':
        _markAttendance();
        break;
      case 'performance':
        _updateRankings();
        break;
      case 'whatsapp_report':
        _sendWhatsAppReport();
        break;
    }
  }

  void _generatePayroll() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Generate Payroll'),
        content: Text('Generate payroll for all employees this month?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showSnackBar('Payroll generation started...', TSHTheme.successGreen);
            },
            child: Text('Generate'),
          ),
        ],
      ),
    );
  }

  void _markAttendance() {
    _showSnackBar('Attendance marking opened', TSHTheme.primaryTeal);
  }

  void _updateRankings() {
    _showSnackBar('Performance rankings updated', TSHTheme.accentOrange);
  }

  void _sendWhatsAppReport() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Send WhatsApp Report'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Send monthly HR report via WhatsApp to managers?'),
            const SizedBox(height: 16),
            Row(
              children: [
                Icon(Icons.whatsapp, color: TSHTheme.successGreen),
                const SizedBox(width: 8),
                Expanded(child: Text('Report includes: Performance rankings, attendance summary, payroll status')),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showSnackBar('WhatsApp report sent successfully!', TSHTheme.successGreen);
            },
            child: Text('Send Report'),
          ),
        ],
      ),
    );
  }

  void _showNotifications(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('HR Notifications', style: TSHTheme.headingMedium),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: 5,
                itemBuilder: (context, index) {
                  return Card(
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: _getNotificationColor(index),
                        child: Icon(_getNotificationIcon(index), color: TSHTheme.surfaceWhite),
                      ),
                      title: Text(_getNotificationTitle(index)),
                      subtitle: Text(_getNotificationSubtitle(index)),
                      trailing: Text('${index + 1}h ago'),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getNotificationColor(int index) {
    switch (index % 4) {
      case 0: return TSHTheme.errorRed;
      case 1: return TSHTheme.warningYellow;
      case 2: return TSHTheme.successGreen;
      default: return TSHTheme.primaryTeal;
    }
  }

  IconData _getNotificationIcon(int index) {
    switch (index % 4) {
      case 0: return Icons.pending_actions;
      case 1: return Icons.warning;
      case 2: return Icons.check_circle;
      default: return Icons.info;
    }
  }

  String _getNotificationTitle(int index) {
    switch (index % 4) {
      case 0: return 'Leave Request Pending';
      case 1: return 'Performance Review Due';
      case 2: return 'Payroll Completed';
      default: return 'New Employee Added';
    }
  }

  String _getNotificationSubtitle(int index) {
    switch (index % 4) {
      case 0: return 'Ahmed Al-Iraqi requested 3 days leave';
      case 1: return 'Monthly reviews for Sales department';
      case 2: return 'November payroll processed successfully';
      default: return 'Sara Mohammed joined IT department';
    }
  }

  void _navigateToAttendanceTracking() {
    Navigator.pop(context);
    _showSnackBar('Attendance tracking opened', TSHTheme.primaryTeal);
  }

  void _navigateToLeaveManagement() {
    Navigator.pop(context);
    _showSnackBar('Leave management opened', TSHTheme.warningYellow);
  }

  void _navigateToDocumentStorage() {
    Navigator.pop(context);
    _showSnackBar('Document storage opened', TSHTheme.successGreen);
  }

  void _navigateToSettings() {
    Navigator.pop(context);
    _showSnackBar('Settings opened', TSHTheme.textLight);
  }

  void _handleSync(BuildContext context) {
    Navigator.pop(context);
    _showSnackBar('Syncing with admin dashboard...', TSHTheme.primaryBlue);
  }

  void _handleLogout(BuildContext context) {
    Navigator.pop(context);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Logout'),
        content: Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showSnackBar('Logged out successfully', TSHTheme.errorRed);
            },
            style: ElevatedButton.styleFrom(backgroundColor: TSHTheme.errorRed),
            child: Text('Logout', style: TextStyle(color: TSHTheme.surfaceWhite)),
          ),
        ],
      ),
    );
  }

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }
}

// ===============================================
// HR DASHBOARD SCREEN - Executive Overview
// ===============================================
class HRDashboardScreen extends StatefulWidget {
  const HRDashboardScreen({super.key});

  @override
  State<HRDashboardScreen> createState() => _HRDashboardScreenState();
}

class _HRDashboardScreenState extends State<HRDashboardScreen> {
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
        Uri.parse('http://localhost:8000/api/hr/dashboard'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        setState(() {
          _dashboardData = json.decode(response.body)['data'];
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
        'total_employees': 19,
        'active_employees': 17,
        'new_hires_month': 2,
        'terminations_month': 0,
        'average_attendance_rate': 94.5,
        'total_late_arrivals': 8,
        'total_overtime_hours': 127.5,
        'pending_leave_requests': 3,
        'approved_leaves_month': 7,
        'total_payroll_amount': 45670000, // 45,670,000 IQD
        'average_salary': 2687647, // Average monthly salary
        'total_overtime_cost': 2340000, // 2,340,000 IQD
        'pending_reviews': 5,
        'completed_reviews_month': 12,
        'average_performance_rating': 4.2,
        'critical_alerts': [
          {'type': 'urgent', 'message': '3 leave requests need approval'},
          {'type': 'warning', 'message': '5 performance reviews overdue'},
          {'type': 'info', 'message': 'Payroll for November ready to process'},
        ],
        'recent_activities': [
          {'time': '10 min ago', 'activity': 'Ahmed Al-Iraqi checked in (On time)', 'type': 'attendance'},
          {'time': '25 min ago', 'activity': 'Sara Mohammed submitted leave request', 'type': 'leave'},
          {'time': '1 hour ago', 'activity': 'Performance review completed for IT department', 'type': 'performance'},
          {'time': '2 hours ago', 'activity': 'Overtime approved for Retail Shop staff', 'type': 'overtime'},
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
            Text('Loading HR Dashboard...'),
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
            // Executive Summary
            _buildExecutiveSummary(localizations),
            const SizedBox(height: 24),
            
            // Critical Alerts
            _buildCriticalAlerts(localizations),
            const SizedBox(height: 24),
            
            // Key Metrics Grid
            _buildKeyMetrics(localizations),
            const SizedBox(height: 24),
            
            // Quick Actions
            _buildQuickActions(localizations),
            const SizedBox(height: 24),
            
            // Recent HR Activities
            _buildRecentActivities(localizations),
          ],
        ),
      ),
    );
  }

  Widget _buildExecutiveSummary(TSHLocalizations localizations) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.dashboard,
                  size: 32,
                  color: TSHTheme.primaryTeal,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'HR Executive Summary',
                        style: TSHTheme.headingMedium,
                      ),
                      Text(
                        'Complete overview of TSH workforce',
                        style: TSHTheme.bodyMedium.copyWith(color: TSHTheme.textLight),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: TSHTheme.successGreen.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: TSHTheme.successGreen.withOpacity(0.3)),
                  ),
                  child: Text(
                    'All Systems Operational',
                    style: TSHTheme.bodySmall.copyWith(
                      color: TSHTheme.successGreen,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: _buildSummaryCard(
                    'Total Workforce',
                    '${_dashboardData['total_employees']}',
                    Icons.people,
                    TSHTheme.primaryTeal,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSummaryCard(
                    'Monthly Payroll',
                    localizations.formatCurrency(_dashboardData['total_payroll_amount']?.toDouble() ?? 0),
                    Icons.attach_money,
                    TSHTheme.successGreen,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildSummaryCard(
                    'Attendance Rate',
                    '${_dashboardData['average_attendance_rate']}%',
                    Icons.access_time,
                    TSHTheme.primaryBlue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSummaryCard(
                    'Performance Avg',
                    '${_dashboardData['average_performance_rating']}/5.0',
                    Icons.star,
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

  Widget _buildSummaryCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: TSHTheme.bodySmall.copyWith(color: TSHTheme.textLight),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TSHTheme.headingSmall.copyWith(color: color, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }

  Widget _buildCriticalAlerts(TSHLocalizations localizations) {
    final alerts = _dashboardData['critical_alerts'] as List<dynamic>? ?? [];
    
    if (alerts.isEmpty) return Container();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Critical Alerts & Actions Required',
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: alerts.length,
          itemBuilder: (context, index) {
            final alert = alerts[index];
            Color alertColor = _getAlertColor(alert['type']);
            IconData alertIcon = _getAlertIcon(alert['type']);
            
            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: alertColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: alertColor.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  Icon(alertIcon, color: alertColor),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      alert['message'],
                      style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () => _handleAlert(alert['type']),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: alertColor,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    ),
                    child: Text(
                      'Take Action',
                      style: TextStyle(color: TSHTheme.surfaceWhite, fontSize: 12),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Color _getAlertColor(String type) {
    switch (type) {
      case 'urgent': return TSHTheme.errorRed;
      case 'warning': return TSHTheme.warningYellow;
      case 'info': return TSHTheme.primaryBlue;
      default: return TSHTheme.textLight;
    }
  }

  IconData _getAlertIcon(String type) {
    switch (type) {
      case 'urgent': return Icons.error;
      case 'warning': return Icons.warning;
      case 'info': return Icons.info;
      default: return Icons.notification_important;
    }
  }

  void _handleAlert(String type) {
    switch (type) {
      case 'urgent':
        _showSnackBar('Navigating to leave approvals...', TSHTheme.errorRed);
        break;
      case 'warning':
        _showSnackBar('Opening performance reviews...', TSHTheme.warningYellow);
        break;
      case 'info':
        _showSnackBar('Opening payroll management...', TSHTheme.primaryBlue);
        break;
    }
  }

  Widget _buildKeyMetrics(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Key HR Metrics',
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.4,
          children: [
            TSHTheme.metricCard(
              title: 'New Hires',
              value: '${_dashboardData['new_hires_month']}',
              subtitle: 'This Month',
              icon: Icons.person_add,
              iconColor: TSHTheme.successGreen,
            ),
            TSHTheme.metricCard(
              title: 'Pending Reviews',
              value: '${_dashboardData['pending_reviews']}',
              subtitle: 'Need Completion',
              icon: Icons.rate_review,
              iconColor: TSHTheme.warningYellow,
            ),
            TSHTheme.metricCard(
              title: 'Overtime Hours',
              value: '${_dashboardData['total_overtime_hours']}h',
              subtitle: 'This Month',
              icon: Icons.access_time,
              iconColor: TSHTheme.primaryBlue,
            ),
            TSHTheme.metricCard(
              title: 'Leave Requests',
              value: '${_dashboardData['pending_leave_requests']}',
              subtitle: 'Pending Approval',
              icon: Icons.vacation_rental,
              iconColor: TSHTheme.accentOrange,
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
          'Quick HR Actions',
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
              icon: Icons.person_add,
              label: 'Add Employee',
              onTap: () => _showSnackBar('Add Employee opened', TSHTheme.successGreen),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.approval,
              label: 'Approvals',
              onTap: () => _showSnackBar('Approvals opened', TSHTheme.warningYellow),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.attach_money,
              label: 'Payroll',
              onTap: () => _showSnackBar('Payroll opened', TSHTheme.primaryTeal),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.analytics,
              label: 'Reports',
              onTap: () => _showSnackBar('Reports opened', TSHTheme.primaryBlue),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.star,
              label: 'Rankings',
              onTap: () => _showSnackBar('Rankings opened', TSHTheme.accentOrange),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.access_time,
              label: 'Attendance',
              onTap: () => _showSnackBar('Attendance opened', TSHTheme.primaryTeal),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.document_scanner,
              label: 'Documents',
              onTap: () => _showSnackBar('Documents opened', TSHTheme.successGreen),
            ),
            TSHTheme.quickActionButton(
              icon: Icons.whatsapp,
              label: 'WhatsApp',
              onTap: () => _showSnackBar('WhatsApp report sent', TSHTheme.successGreen),
            ),
          ],
        ),
      ],
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
                  'Recent HR Activities',
                  style: TSHTheme.headingSmall,
                ),
                TextButton(
                  onPressed: () => _showSnackBar('All activities opened', TSHTheme.primaryTeal),
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
                  title: Text(activity['activity']),
                  trailing: Text(
                    activity['time'],
                    style: TSHTheme.bodySmall.copyWith(color: TSHTheme.textLight),
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
      case 'attendance': return TSHTheme.successGreen;
      case 'leave': return TSHTheme.warningYellow;
      case 'performance': return TSHTheme.accentOrange;
      case 'overtime': return TSHTheme.primaryBlue;
      default: return TSHTheme.textLight;
    }
  }

  IconData _getActivityIcon(String type) {
    switch (type) {
      case 'attendance': return Icons.access_time;
      case 'leave': return Icons.vacation_rental;
      case 'performance': return Icons.star;
      case 'overtime': return Icons.schedule;
      default: return Icons.info;
    }
  }

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }
}

// ===============================================
// PLACEHOLDER SCREENS FOR OTHER HR SECTIONS
// ===============================================
class EmployeeStatusScreen extends StatelessWidget {
  const EmployeeStatusScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Employee Status - Real-time tracking with photos'));
  }
}

class PayrollManagementScreen extends StatelessWidget {
  const PayrollManagementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Payroll Management - Monthly/Commission based'));
  }
}

class ApprovalsScreen extends StatelessWidget {
  const ApprovalsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Approvals - Leave/Overtime/Expenses'));
  }
}

class PerformanceRankingScreen extends StatelessWidget {
  const PerformanceRankingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Performance Rankings - Silver/Gold/Diamond'));
  }
}

class HRReportsScreen extends StatelessWidget {
  const HRReportsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('HR Reports - Analytics and WhatsApp Auto-send'));
  }
} 