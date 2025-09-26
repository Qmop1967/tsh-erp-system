import 'package:flutter/material.dart';

void main() {
  runApp(TSHHRApp());
}

// TSH Theme Class
class TSHTheme {
  // Colors
  static const Color primaryTeal = Color(0xFF2DD4BF);
  static const Color primaryBlue = Color(0xFF3B82F6);
  static const Color successGreen = Color(0xFF10B981);
  static const Color warningYellow = Color(0xFFF59E0B);
  static const Color errorRed = Color(0xFFEF4444);
  static const Color accentOrange = Color(0xFFF97316);
  static const Color surfaceWhite = Color(0xFFFAFAFA);
  static const Color textDark = Color(0xFF111827);
  static const Color textLight = Color(0xFF6B7280);

  // Text Styles
  static const TextStyle headingLarge = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: textDark,
  );
  
  static const TextStyle headingSmall = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: textDark,
  );
  
  static const TextStyle bodyMedium = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: textDark,
  );
  
  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: textLight,
  );

  // Widget Builders with better responsive design
  static Widget metricCard({
    required String title,
    required String value,
    required IconData icon,
    required Color iconColor,
  }) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: iconColor, size: 32),
          SizedBox(height: 8),
          Text(
            value, 
            style: headingSmall,
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 4),
          Text(
            title, 
            style: bodySmall, 
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  static Widget quickActionButton({
    required String title,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: primaryTeal,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: surfaceWhite, size: 24),
            SizedBox(height: 6),
            Text(
              title,
              style: bodySmall.copyWith(
                color: surfaceWhite,
                fontSize: 10,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

// Comprehensive Localizations with all text translations
class TSHLocalizations {
  final Locale locale;
  
  TSHLocalizations(this.locale);
  
  static TSHLocalizations of(BuildContext context) {
    return Localizations.of<TSHLocalizations>(context, TSHLocalizations) ?? 
           TSHLocalizations(Locale('en'));
  }
  
  bool get isArabic => locale.languageCode == 'ar';
  
  // Complete Arabic/English text mapping
  String get hrDashboard => isArabic ? 'لوحة إدارة الموارد البشرية' : 'HR Dashboard';
  String get employees => isArabic ? 'الموظفين' : 'Employees';
  String get attendance => isArabic ? 'الحضور' : 'Attendance';
  String get payroll => isArabic ? 'كشوف المرتبات' : 'Payroll';
  String get performance => isArabic ? 'الأداء' : 'Performance';
  String get reports => isArabic ? 'التقارير' : 'Reports';
  String get approvals => isArabic ? 'الموافقات' : 'Approvals';
  String get keyMetrics => isArabic ? 'المقاييس الرئيسية' : 'Key Metrics';
  String get quickActions => isArabic ? 'إجراءات سريعة' : 'Quick Actions';
  String get recentActivities => isArabic ? 'الأنشطة الحديثة' : 'Recent Activities';
  String get criticalAlerts => isArabic ? 'التنبيهات الحرجة' : 'Critical Alerts';
  
  // Welcome section
  String get welcomeBack => isArabic ? 'مرحباً بعودتك!' : 'Welcome Back!';
  String get hrManagementDashboard => isArabic ? 'لوحة إدارة الموارد البشرية TSH' : 'TSH HR Management Dashboard';
  String get systemStatusActive => isArabic ? 'حالة النظام: نشط' : 'System Status: Active';
  
  // Critical alerts
  String get urgentLeaveApproval => isArabic ? 'موافقة إجازة عاجلة مطلوبة' : 'Urgent Leave Approval Required';
  String get pendingApprovalsAttention => isArabic ? '3 موافقات في الانتظار تحتاج عناية فورية' : '3 pending approvals need immediate attention';
  String get review => isArabic ? 'مراجعة' : 'Review';
  
  // Metrics
  String get totalEmployees => isArabic ? 'إجمالي الموظفين' : 'Total Employees';
  String get pendingApprovals => isArabic ? 'الموافقات المعلقة' : 'Pending Approvals';
  String get presentToday => isArabic ? 'الحاضرون اليوم' : 'Present Today';
  String get onLeave => isArabic ? 'في إجازة' : 'On Leave';
  
  // Quick Actions
  String get addEmployee => isArabic ? 'إضافة موظف' : 'Add Employee';
  String get rankings => isArabic ? 'التصنيفات' : 'Rankings';
  String get documents => isArabic ? 'المستندات' : 'Documents';
  String get whatsapp => isArabic ? 'واتساب' : 'WhatsApp';
  
  // Recent Activities
  String get ahmedMarkedAttendance => isArabic ? 'أحمد سجل الحضور' : 'Ahmed marked attendance';
  String get saraSubmittedLeave => isArabic ? 'سارة قدمت طلب إجازة' : 'Sara submitted leave request';
  String get monthlyReviewCompleted => isArabic ? 'تم إكمال المراجعة الشهرية لعمر' : 'Monthly review completed for Omar';
  String get minAgo => isArabic ? 'دقيقة مضت' : 'min ago';
  String get hourAgo => isArabic ? 'ساعة مضت' : 'hour ago';
  String get viewAll => isArabic ? 'عرض الكل' : 'View All';
  
  // Navigation
  String get dashboard => isArabic ? 'الرئيسية' : 'Dashboard';
  String get employeeStatus => isArabic ? 'حالة الموظفين' : 'Employee Status';
  String get realTimeTracking => isArabic ? 'تتبع الموظفين في الوقت الفعلي' : 'Real-time employee tracking';
  String get payrollManagement => isArabic ? 'إدارة الرواتب' : 'Payroll Management';
  String get monthlyPayrollCommissions => isArabic ? 'الرواتب الشهرية والعمولات' : 'Monthly payroll & commissions';
  String get hrApprovals => isArabic ? 'موافقات الموارد البشرية' : 'HR Approvals';
  String get leaveOvertimeExpense => isArabic ? 'موافقات الإجازات والوقت الإضافي والمصروفات' : 'Leave, overtime & expense approvals';
  String get performanceRankings => isArabic ? 'تصنيفات الأداء' : 'Performance Rankings';
  String get silverGoldDiamond => isArabic ? 'تصنيفات الفضة والذهب والماس' : 'Silver, Gold & Diamond rankings';
  String get hrReports => isArabic ? 'تقارير الموارد البشرية' : 'HR Reports';
  String get analyticsWhatsapp => isArabic ? 'التحليلات وأتمتة الواتساب' : 'Analytics & WhatsApp automation';
  
  // Drawer
  String get hrDirector => isArabic ? 'مدير الموارد البشرية' : 'HR Director';
  String get settings => isArabic ? 'الإعدادات' : 'Settings';
  String get help => isArabic ? 'المساعدة' : 'Help';
  String get logout => isArabic ? 'تسجيل خروج' : 'Logout';
  
  // Notifications
  String get notifications => isArabic ? 'الإشعارات' : 'Notifications';
  String get pendingApprovalsNotif => isArabic ? '3 موافقات في الانتظار' : '3 Pending Approvals';
  String get requiresAttention => isArabic ? 'تحتاج موافقة فورية' : 'Requires immediate attention';
  String get monthlyAttendanceReady => isArabic ? 'تقرير الحضور الشهري جاهز' : 'Monthly attendance report ready';
  String get minutesAgo => isArabic ? '5 دقائق مضت' : '5 minutes ago';
  String get excellentPerformance => isArabic ? 'أداء ممتاز للموظف أحمد' : 'Excellent performance - Ahmed';
  String get promotedToGold => isArabic ? 'ترقية إلى رتبة الذهب' : 'Promoted to Gold rank';
  
  // Success messages
  String get switchedToArabic => isArabic ? 'تم التبديل إلى العربية' : 'Switched to Arabic';
  String get switchedToEnglish => isArabic ? 'تم التبديل إلى الإنجليزية' : 'Switched to English';
  String get dataRefreshed => isArabic ? 'تم تحديث البيانات!' : 'Data refreshed!';
}

class TSHHRApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TSH HR Management',
      theme: ThemeData(
        primarySwatch: Colors.teal,
        fontFamily: 'Roboto',
      ),
      supportedLocales: [
        Locale('en', ''),
        Locale('ar', ''),
      ],
      home: TSHHRMainScreen(),
      debugShowCheckedModeBanner: false,
      // Enable RTL support
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.ltr, // Will be overridden per screen
          child: child!,
        );
      },
    );
  }
}

class TSHHRMainScreen extends StatefulWidget {
  @override
  _TSHHRMainScreenState createState() => _TSHHRMainScreenState();
}

class _TSHHRMainScreenState extends State<TSHHRMainScreen> {
  int _selectedIndex = 0;
  bool _isArabic = false;

  final List<Widget> _screens = [
    HRDashboardScreen(),
    EmployeeStatusScreen(),
    PayrollManagementScreen(),
    ApprovalsScreen(),
    PerformanceRankingScreen(),
    HRReportsScreen(),
  ];

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final localizations = TSHLocalizations(_isArabic ? Locale('ar') : Locale('en'));
    
    return Directionality(
      textDirection: _isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            _isArabic ? 'نظام إدارة الموارد البشرية TSH' : 'TSH HR Management System',
            style: TSHTheme.headingSmall.copyWith(color: Colors.white),
          ),
          backgroundColor: TSHTheme.primaryTeal,
          actions: [
            IconButton(
              icon: Icon(Icons.language),
              onPressed: () {
                setState(() {
                  _isArabic = !_isArabic;
                });
                _showSnackBar(
                  _isArabic ? localizations.switchedToArabic : localizations.switchedToEnglish, 
                  TSHTheme.successGreen
                );
              },
            ),
            IconButton(
              icon: Icon(Icons.notifications),
              onPressed: () => _showNotifications(localizations),
            ),
          ],
        ),
        drawer: _buildDrawer(localizations),
        body: _screens[_selectedIndex],
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _selectedIndex,
          onTap: (index) => setState(() => _selectedIndex = index),
          type: BottomNavigationBarType.fixed,
          selectedItemColor: TSHTheme.primaryTeal,
          unselectedItemColor: TSHTheme.textLight,
          items: [
            BottomNavigationBarItem(
              icon: Icon(Icons.dashboard),
              label: localizations.dashboard,
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.people),
              label: localizations.employees,
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.payment),
              label: localizations.payroll,
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.approval),
              label: localizations.approvals,
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.star),
              label: localizations.performance,
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.analytics),
              label: localizations.reports,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawer(TSHLocalizations localizations) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [TSHTheme.primaryTeal, TSHTheme.primaryBlue],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.white,
                  child: Icon(Icons.person, size: 40, color: TSHTheme.primaryTeal),
                ),
                SizedBox(height: 16),
                Text(
                  localizations.hrDirector,
                  style: TSHTheme.headingSmall.copyWith(color: Colors.white),
                ),
                Text(
                  'TSH ERP System',
                  style: TSHTheme.bodySmall.copyWith(color: Colors.white70),
                ),
              ],
            ),
          ),
          ListTile(
            leading: Icon(Icons.settings),
            title: Text(localizations.settings),
            onTap: () => _showSnackBar('Settings opened', TSHTheme.primaryBlue),
          ),
          ListTile(
            leading: Icon(Icons.help),
            title: Text(localizations.help),
            onTap: () => _showSnackBar('Help opened', TSHTheme.accentOrange),
          ),
          ListTile(
            leading: Icon(Icons.logout),
            title: Text(localizations.logout),
            onTap: () => _showSnackBar('Logout clicked', TSHTheme.errorRed),
          ),
        ],
      ),
    );
  }

  void _showNotifications(TSHLocalizations localizations) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Directionality(
        textDirection: _isArabic ? TextDirection.rtl : TextDirection.ltr,
        child: Container(
          padding: EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                localizations.notifications,
                style: TSHTheme.headingSmall,
              ),
              SizedBox(height: 16),
              ListTile(
                leading: Icon(Icons.warning, color: TSHTheme.warningYellow),
                title: Text(localizations.pendingApprovalsNotif),
                subtitle: Text(localizations.requiresAttention),
              ),
              ListTile(
                leading: Icon(Icons.access_time, color: TSHTheme.primaryBlue),
                title: Text(localizations.monthlyAttendanceReady),
                subtitle: Text(localizations.minutesAgo),
              ),
              ListTile(
                leading: Icon(Icons.celebration, color: TSHTheme.successGreen),
                title: Text(localizations.excellentPerformance),
                subtitle: Text(localizations.promotedToGold),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Dashboard Screen with comprehensive translations
class HRDashboardScreen extends StatefulWidget {
  @override
  _HRDashboardScreenState createState() => _HRDashboardScreenState();
}

class _HRDashboardScreenState extends State<HRDashboardScreen> {
  
  @override
  Widget build(BuildContext context) {
    final mainState = context.findAncestorStateOfType<_TSHHRMainScreenState>();
    final isArabic = mainState?._isArabic ?? false;
    final localizations = TSHLocalizations(isArabic ? Locale('ar') : Locale('en'));
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        body: RefreshIndicator(
          onRefresh: () async {
            await Future.delayed(Duration(seconds: 1));
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(localizations.dataRefreshed)),
            );
          },
          child: ListView(
            padding: EdgeInsets.all(16),
            children: [
              _buildWelcomeHeader(localizations),
              SizedBox(height: 20),
              _buildCriticalAlerts(localizations),
              SizedBox(height: 20),
              _buildKeyMetrics(localizations),
              SizedBox(height: 20),
              _buildQuickActions(localizations),
              SizedBox(height: 20),
              _buildRecentActivities(localizations),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader(TSHLocalizations localizations) {
    return Container(
      padding: EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [TSHTheme.primaryTeal, TSHTheme.primaryBlue],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  localizations.welcomeBack,
                  style: TSHTheme.headingLarge.copyWith(color: Colors.white),
                ),
                SizedBox(height: 8),
                Text(
                  localizations.hrManagementDashboard,
                  style: TSHTheme.bodyMedium.copyWith(color: Colors.white70),
                ),
                SizedBox(height: 16),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: TSHTheme.successGreen.withOpacity(0.2),
                    border: Border.all(color: TSHTheme.successGreen.withOpacity(0.3)),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    localizations.systemStatusActive,
                    style: TSHTheme.bodySmall.copyWith(
                      color: TSHTheme.successGreen,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Icon(Icons.business_center, size: 60, color: Colors.white38),
        ],
      ),
    );
  }

  Widget _buildCriticalAlerts(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          localizations.criticalAlerts,
          style: TSHTheme.headingSmall,
        ),
        SizedBox(height: 12),
        Container(
          padding: EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.red.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.red.shade200),
          ),
          child: Row(
            children: [
              Icon(Icons.warning, color: TSHTheme.errorRed),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      localizations.urgentLeaveApproval,
                      style: TSHTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
                    ),
                    Text(
                      localizations.pendingApprovalsAttention,
                      style: TextStyle(color: TSHTheme.textLight, fontSize: 12),
                    ),
                  ],
                ),
              ),
              ElevatedButton(
                onPressed: () => _handleCriticalAction('urgent', localizations),
                style: ElevatedButton.styleFrom(backgroundColor: TSHTheme.errorRed),
                child: Text(localizations.review, style: TextStyle(color: Colors.white)),
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _handleCriticalAction(String action, TSHLocalizations localizations) {
    String message;
    Color color;
    switch (action) {
      case 'urgent':
        message = 'Navigating to leave approvals...';
        color = TSHTheme.errorRed;
        break;
      case 'performance':
        message = 'Opening performance reviews...';
        color = TSHTheme.warningYellow;
        break;
      case 'payroll':
        message = 'Opening payroll management...';
        color = TSHTheme.primaryBlue;
        break;
      default:
        message = 'Action completed';
        color = TSHTheme.successGreen;
    }
    _showSnackBar(message, color);
  }

  Widget _buildKeyMetrics(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          localizations.keyMetrics,
          style: TSHTheme.headingSmall,
        ),
        SizedBox(height: 12),
        GridView.count(
          shrinkWrap: true,
          physics: NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.2, // Better aspect ratio
          children: [
            TSHTheme.metricCard(
              title: localizations.totalEmployees,
              value: '19',
              icon: Icons.people,
              iconColor: TSHTheme.successGreen,
            ),
            TSHTheme.metricCard(
              title: localizations.pendingApprovals,
              value: '5',
              icon: Icons.pending_actions,
              iconColor: TSHTheme.warningYellow,
            ),
            TSHTheme.metricCard(
              title: localizations.presentToday,
              value: '16',
              icon: Icons.check_circle,
              iconColor: TSHTheme.primaryBlue,
            ),
            TSHTheme.metricCard(
              title: localizations.onLeave,
              value: '3',
              icon: Icons.beach_access,
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
          localizations.quickActions,
          style: TSHTheme.headingSmall,
        ),
        SizedBox(height: 12),
        // Fixed grid with better spacing
        ConstrainedBox(
          constraints: BoxConstraints(maxHeight: 200),
          child: GridView.count(
            shrinkWrap: true,
            physics: NeverScrollableScrollPhysics(),
            crossAxisCount: 4,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
            childAspectRatio: 0.8, // Better aspect ratio to prevent overflow
            children: [
              TSHTheme.quickActionButton(
                title: localizations.addEmployee,
                icon: Icons.person_add,
                onTap: () => _showSnackBar('Add Employee opened', TSHTheme.successGreen),
              ),
              TSHTheme.quickActionButton(
                title: localizations.approvals,
                icon: Icons.approval,
                onTap: () => _showSnackBar('Approvals opened', TSHTheme.warningYellow),
              ),
              TSHTheme.quickActionButton(
                title: localizations.payroll,
                icon: Icons.payment,
                onTap: () => _showSnackBar('Payroll opened', TSHTheme.primaryTeal),
              ),
              TSHTheme.quickActionButton(
                title: localizations.reports,
                icon: Icons.analytics,
                onTap: () => _showSnackBar('Reports opened', TSHTheme.primaryBlue),
              ),
              TSHTheme.quickActionButton(
                title: localizations.rankings,
                icon: Icons.star,
                onTap: () => _showSnackBar('Rankings opened', TSHTheme.accentOrange),
              ),
              TSHTheme.quickActionButton(
                title: localizations.attendance,
                icon: Icons.access_time,
                onTap: () => _showSnackBar('Attendance opened', TSHTheme.primaryTeal),
              ),
              TSHTheme.quickActionButton(
                title: localizations.documents,
                icon: Icons.folder,
                onTap: () => _showSnackBar('Documents opened', TSHTheme.successGreen),
              ),
              TSHTheme.quickActionButton(
                title: localizations.whatsapp,
                icon: Icons.chat,
                onTap: () => _showSnackBar('WhatsApp report sent', TSHTheme.successGreen),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRecentActivities(TSHLocalizations localizations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              localizations.recentActivities,
              style: TSHTheme.headingSmall,
            ),
            TextButton(
              onPressed: () => _showSnackBar('All activities opened', TSHTheme.primaryTeal),
              child: Text(localizations.viewAll),
            ),
          ],
        ),
        SizedBox(height: 12),
        ListView.builder(
          shrinkWrap: true,
          physics: NeverScrollableScrollPhysics(),
          itemCount: 3,
          itemBuilder: (context, index) {
            final activities = [
              {
                'type': 'attendance', 
                'title': localizations.ahmedMarkedAttendance, 
                'time': '2 ${localizations.minAgo}'
              },
              {
                'type': 'leave', 
                'title': localizations.saraSubmittedLeave, 
                'time': '15 ${localizations.minAgo}'
              },
              {
                'type': 'performance', 
                'title': localizations.monthlyReviewCompleted, 
                'time': '1 ${localizations.hourAgo}'
              },
            ];
            
            final activity = activities[index];
            return ListTile(
              leading: CircleAvatar(
                backgroundColor: _getActivityColor(activity['type']!),
                child: Icon(_getActivityIcon(activity['type']!), color: Colors.white),
              ),
              title: Text(activity['title']!),
              subtitle: Text(
                activity['time']!,
                style: TSHTheme.bodySmall.copyWith(color: TSHTheme.textLight),
              ),
            );
          },
        ),
      ],
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
      case 'attendance': return Icons.check_circle;
      case 'leave': return Icons.beach_access;
      case 'performance': return Icons.star;
      case 'overtime': return Icons.access_time;
      default: return Icons.info;
    }
  }

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        duration: Duration(seconds: 2),
      ),
    );
  }
}

// Enhanced Screen Placeholders with translations
class EmployeeStatusScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final mainState = context.findAncestorStateOfType<_TSHHRMainScreenState>();
    final isArabic = mainState?._isArabic ?? false;
    final localizations = TSHLocalizations(isArabic ? Locale('ar') : Locale('en'));
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people, size: 80, color: TSHTheme.primaryTeal),
            SizedBox(height: 16),
            Text(localizations.employeeStatus, style: TSHTheme.headingLarge),
            Text(localizations.realTimeTracking, style: TSHTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

class PayrollManagementScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final mainState = context.findAncestorStateOfType<_TSHHRMainScreenState>();
    final isArabic = mainState?._isArabic ?? false;
    final localizations = TSHLocalizations(isArabic ? Locale('ar') : Locale('en'));
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.payment, size: 80, color: TSHTheme.primaryBlue),
            SizedBox(height: 16),
            Text(localizations.payrollManagement, style: TSHTheme.headingLarge),
            Text(localizations.monthlyPayrollCommissions, style: TSHTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

class ApprovalsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final mainState = context.findAncestorStateOfType<_TSHHRMainScreenState>();
    final isArabic = mainState?._isArabic ?? false;
    final localizations = TSHLocalizations(isArabic ? Locale('ar') : Locale('en'));
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.approval, size: 80, color: TSHTheme.warningYellow),
            SizedBox(height: 16),
            Text(localizations.hrApprovals, style: TSHTheme.headingLarge),
            Text(localizations.leaveOvertimeExpense, style: TSHTheme.bodyMedium, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

class PerformanceRankingScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final mainState = context.findAncestorStateOfType<_TSHHRMainScreenState>();
    final isArabic = mainState?._isArabic ?? false;
    final localizations = TSHLocalizations(isArabic ? Locale('ar') : Locale('en'));
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.star, size: 80, color: TSHTheme.accentOrange),
            SizedBox(height: 16),
            Text(localizations.performanceRankings, style: TSHTheme.headingLarge),
            Text(localizations.silverGoldDiamond, style: TSHTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

class HRReportsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final mainState = context.findAncestorStateOfType<_TSHHRMainScreenState>();
    final isArabic = mainState?._isArabic ?? false;
    final localizations = TSHLocalizations(isArabic ? Locale('ar') : Locale('en'));
    
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.analytics, size: 80, color: TSHTheme.primaryTeal),
            SizedBox(height: 16),
            Text(localizations.hrReports, style: TSHTheme.headingLarge),
            Text(localizations.analyticsWhatsapp, style: TSHTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

/* 
===========================================
🌟 MANDATORY TRANSLATION PLANNING RULES 🌟
===========================================

⚠️ CRITICAL INSTRUCTION FOR ALL FUTURE UPDATES:

🔴 BEFORE adding ANY new feature, screen, or text to this app:

1. 📝 ADD Arabic translation to TSHLocalizations class
   - Every new string MUST have both English and Arabic versions
   - Follow naming convention: camelCase for variables
   - Use clear, professional Arabic translations

2. 🔄 IMPLEMENT RTL support for new components
   - Wrap new screens with Directionality widget
   - Test layout in both LTR and RTL modes
   - Ensure proper text alignment and icon positioning

3. 📱 UPDATE all new screens to use localizations
   - Access TSHLocalizations from context
   - Replace hardcoded strings with localization calls
   - Test language switching functionality

4. ✅ QUALITY CHECKLIST before committing:
   □ All text is translatable
   □ RTL layout works correctly
   □ Arabic text displays properly
   □ Language switching works
   □ No hardcoded English/Arabic strings
   □ Professional translation quality

5. 📋 TRANSLATION TESTING REQUIREMENTS:
   - Test every new feature in both languages
   - Verify proper text direction (RTL/LTR)
   - Check text overflow and spacing
   - Ensure cultural appropriateness

⚡ NO EXCEPTIONS: Every feature MUST support both languages from day one!

🎯 This ensures consistent bilingual experience for TSH's Iraqi operations.
*/ 