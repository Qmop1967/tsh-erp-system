import 'package:flutter/material.dart';

/// Enhanced TSH ERP System Localization
/// Comprehensive translations with support for English, Arabic, Kurdish, and Turkish
class EnhancedTSHLocalizations {
  final Locale locale;

  EnhancedTSHLocalizations(this.locale);

  static EnhancedTSHLocalizations? of(BuildContext context) {
    return Localizations.of<EnhancedTSHLocalizations>(context, EnhancedTSHLocalizations);
  }

  static const LocalizationsDelegate<EnhancedTSHLocalizations> delegate = 
      _EnhancedTSHLocalizationsDelegate();

  static const List<Locale> supportedLocales = [
    Locale('en', 'US'), // English
    Locale('ar', 'IQ'), // Arabic (Iraq)
    Locale('ku', 'IQ'), // Kurdish (Iraq)
    Locale('tr', 'TR'), // Turkish
    Locale('fa', 'IR'), // Persian/Farsi
  ];

  static const Map<String, Map<String, String>> _localizedValues = {
    'en': {
      // App Names & Titles
      'tsh_erp': 'TSH ERP System',
      'tsh_admin_app': 'TSH Admin Dashboard',
      'executive_dashboard': 'Executive Dashboard',
      'financial_control': 'Financial Control',
      'operations_overview': 'Operations Overview',
      'system_analytics': 'System Analytics',
      'admin_settings': 'Admin Settings',
      
      // Enhanced Dashboard
      'welcome_admin': 'Welcome, Administrator',
      'today_date': 'Today',
      'executive_summary': 'Executive Summary',
      'financial_metrics': 'Financial Metrics',
      'key_performance': 'Key Performance Indicators',
      'recent_activities': 'Recent Activities',
      'system_status': 'System Status',
      'quick_actions': 'Quick Actions',
      
      // Financial Enhanced
      'available_cash': 'Available Cash',
      'total_receivables': 'Total Receivables',
      'total_payables': 'Total Payables',
      'inventory_valuation': 'Inventory Valuation',
      'net_profit': 'Net Profit',
      'gross_margin': 'Gross Margin',
      'cash_flow': 'Cash Flow',
      'budget_variance': 'Budget Variance',
      
      // Operations
      'active_orders': 'Active Orders',
      'pending_deliveries': 'Pending Deliveries',
      'inventory_alerts': 'Inventory Alerts',
      'customer_satisfaction': 'Customer Satisfaction',
      'supplier_performance': 'Supplier Performance',
      'production_efficiency': 'Production Efficiency',
      
      // HR Enhanced
      'total_employees': 'Total Employees',
      'active_employees': 'Active Employees',
      'departments': 'Departments',
      'attendance_rate': 'Attendance Rate',
      'payroll_pending': 'Payroll Pending',
      'training_sessions': 'Training Sessions',
      'performance_reviews': 'Performance Reviews',
      
      // System & Tech
      'system_uptime': 'System Uptime',
      'database_status': 'Database Status',
      'backup_status': 'Backup Status',
      'security_alerts': 'Security Alerts',
      'api_performance': 'API Performance',
      'user_sessions': 'Active User Sessions',
      
      // Enhanced Actions
      'generate_report': 'Generate Report',
      'export_data': 'Export Data',
      'import_data': 'Import Data',
      'backup_system': 'Backup System',
      'audit_log': 'Audit Log',
      'user_management': 'User Management',
      'system_maintenance': 'System Maintenance',
      
      // Time & Date
      'yesterday': 'Yesterday',
      'last_week': 'Last Week',
      'last_month': 'Last Month',
      'this_quarter': 'This Quarter',
      'year_to_date': 'Year to Date',
      'real_time': 'Real Time',
      
      // Status & Alerts
      'healthy': 'Healthy',
      'warning_status': 'Warning',
      'critical': 'Critical',
      'offline': 'Offline',
      'online': 'Online',
      'maintenance': 'Maintenance',
      'needs_attention': 'Needs Attention',
    },
    
    'ar': {
      // App Names & Titles
      'tsh_erp': 'نظام TSH ERP',
      'tsh_admin_app': 'لوحة إدارة TSH',
      'executive_dashboard': 'لوحة القيادة التنفيذية',
      'financial_control': 'الرقابة المالية',
      'operations_overview': 'نظرة عامة على العمليات',
      'system_analytics': 'تحليلات النظام',
      'admin_settings': 'إعدادات الإدارة',
      
      // Enhanced Dashboard
      'welcome_admin': 'أهلاً وسهلاً، المدير',
      'today_date': 'اليوم',
      'executive_summary': 'الملخص التنفيذي',
      'financial_metrics': 'المؤشرات المالية',
      'key_performance': 'مؤشرات الأداء الرئيسية',
      'recent_activities': 'الأنشطة الحديثة',
      'system_status': 'حالة النظام',
      'quick_actions': 'الإجراءات السريعة',
      
      // Financial Enhanced
      'available_cash': 'النقد المتاح',
      'total_receivables': 'إجمالي المستحقات',
      'total_payables': 'إجمالي المدفوعات',
      'inventory_valuation': 'تقييم المخزون',
      'net_profit': 'صافي الربح',
      'gross_margin': 'إجمالي الهامش',
      'cash_flow': 'التدفق النقدي',
      'budget_variance': 'انحراف الميزانية',
      
      // Operations
      'active_orders': 'الطلبات النشطة',
      'pending_deliveries': 'التسليمات المعلقة',
      'inventory_alerts': 'تنبيهات المخزون',
      'customer_satisfaction': 'رضا العملاء',
      'supplier_performance': 'أداء الموردين',
      'production_efficiency': 'كفاءة الإنتاج',
      
      // HR Enhanced
      'total_employees': 'إجمالي الموظفين',
      'active_employees': 'الموظفون النشطون',
      'departments': 'الأقسام',
      'attendance_rate': 'معدل الحضور',
      'payroll_pending': 'الراتب المعلق',
      'training_sessions': 'جلسات التدريب',
      'performance_reviews': 'مراجعات الأداء',
      
      // System & Tech
      'system_uptime': 'وقت تشغيل النظام',
      'database_status': 'حالة قاعدة البيانات',
      'backup_status': 'حالة النسخ الاحتياطي',
      'security_alerts': 'تنبيهات الأمان',
      'api_performance': 'أداء API',
      'user_sessions': 'جلسات المستخدمين النشطة',
      
      // Enhanced Actions
      'generate_report': 'إنشاء تقرير',
      'export_data': 'تصدير البيانات',
      'import_data': 'استيراد البيانات',
      'backup_system': 'نسخ احتياطي للنظام',
      'audit_log': 'سجل المراجعة',
      'user_management': 'إدارة المستخدمين',
      'system_maintenance': 'صيانة النظام',
      
      // Time & Date
      'yesterday': 'أمس',
      'last_week': 'الأسبوع الماضي',
      'last_month': 'الشهر الماضي',
      'this_quarter': 'هذا الربع',
      'year_to_date': 'من بداية السنة',
      'real_time': 'الوقت الفعلي',
      
      // Status & Alerts
      'healthy': 'جيد',
      'warning_status': 'تحذير',
      'critical': 'حرج',
      'offline': 'غير متصل',
      'online': 'متصل',
      'maintenance': 'صيانة',
      'needs_attention': 'يحتاج انتباه',
    },

    'ku': {
      // App Names & Titles (Kurdish)
      'tsh_erp': 'سیستەمی TSH ERP',
      'tsh_admin_app': 'داشبۆردی بەڕێوەبەری TSH',
      'executive_dashboard': 'داشبۆردی جێبەجێکەر',
      'financial_control': 'کۆنتڕۆڵی دارایی',
      'operations_overview': 'تێڕوانینی گشتی کارەکان',
      'system_analytics': 'شیکاری سیستەم',
      'admin_settings': 'ڕێکخستنی بەڕێوەبەر',
      
      // Enhanced Dashboard
      'welcome_admin': 'بەخێربێیت، بەڕێوەبەر',
      'today_date': 'ئەمڕۆ',
      'executive_summary': 'پوختەی جێبەجێکەر',
      'financial_metrics': 'پێوەرە داراییەکان',
      'key_performance': 'پێوەرە سەرەکییەکانی کارکرد',
      'recent_activities': 'چالاکییە نوێیەکان',
      'system_status': 'دۆخی سیستەم',
      'quick_actions': 'کردارە خێراکان',
    },

    'tr': {
      // App Names & Titles (Turkish)
      'tsh_erp': 'TSH ERP Sistemi',
      'tsh_admin_app': 'TSH Yönetici Paneli',
      'executive_dashboard': 'Yönetici Paneli',
      'financial_control': 'Mali Kontrol',
      'operations_overview': 'Operasyon Genel Bakış',
      'system_analytics': 'Sistem Analizi',
      'admin_settings': 'Yönetici Ayarları',
      
      // Enhanced Dashboard
      'welcome_admin': 'Hoş Geldiniz, Yönetici',
      'today_date': 'Bugün',
      'executive_summary': 'Yönetici Özeti',
      'financial_metrics': 'Mali Ölçümler',
      'key_performance': 'Anahtar Performans Göstergeleri',
      'recent_activities': 'Son Aktiviteler',
      'system_status': 'Sistem Durumu',
      'quick_actions': 'Hızlı İşlemler',
    },

    'fa': {
      // App Names & Titles (Persian/Farsi)
      'tsh_erp': 'سیستم TSH ERP',
      'tsh_admin_app': 'داشبورد مدیریت TSH',
      'executive_dashboard': 'داشبورد اجرایی',
      'financial_control': 'کنترل مالی',
      'operations_overview': 'بررسی عملیات',
      'system_analytics': 'تجزیه و تحلیل سیستم',
      'admin_settings': 'تنظیمات مدیر',
      
      // Enhanced Dashboard
      'welcome_admin': 'خوش آمدید، مدیر',
      'today_date': 'امروز',
      'executive_summary': 'خلاصه اجرایی',
      'financial_metrics': 'معیارهای مالی',
      'key_performance': 'شاخص‌های عملکرد کلیدی',
      'recent_activities': 'فعالیت‌های اخیر',
      'system_status': 'وضعیت سیستم',
      'quick_actions': 'عملیات سریع',
    },
  };

  String translate(String key) {
    final languageCode = locale.languageCode;
    return _localizedValues[languageCode]?[key] ?? 
           _localizedValues['en']?[key] ?? 
           key;
  }

  bool get isRTL => ['ar', 'ku', 'fa'].contains(locale.languageCode);
  bool get isEnglish => locale.languageCode == 'en';
  bool get isArabic => locale.languageCode == 'ar';
  bool get isKurdish => locale.languageCode == 'ku';
  bool get isTurkish => locale.languageCode == 'tr';
  bool get isPersian => locale.languageCode == 'fa';
}

class _EnhancedTSHLocalizationsDelegate
    extends LocalizationsDelegate<EnhancedTSHLocalizations> {
  const _EnhancedTSHLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'ar', 'ku', 'tr', 'fa'].contains(locale.languageCode);
  }

  @override
  Future<EnhancedTSHLocalizations> load(Locale locale) async {
    return EnhancedTSHLocalizations(locale);
  }

  @override
  bool shouldReload(_EnhancedTSHLocalizationsDelegate old) => false;
}

/// Enhanced Language Service with more languages
class EnhancedLanguageService extends ChangeNotifier {
  static const List<Locale> supportedLocales = [
    Locale('en', 'US'), // English
    Locale('ar', 'IQ'), // Arabic (Iraq)
    Locale('ku', 'IQ'), // Kurdish (Iraq)
    Locale('tr', 'TR'), // Turkish
    Locale('fa', 'IR'), // Persian/Farsi
  ];

  Locale _currentLocale = const Locale('en', 'US');
  bool _isDarkMode = false;

  Locale get currentLocale => _currentLocale;
  bool get isDarkMode => _isDarkMode;
  bool get isRTL => ['ar', 'ku', 'fa'].contains(_currentLocale.languageCode);

  void changeLanguage(Locale locale) {
    if (supportedLocales.contains(locale)) {
      _currentLocale = locale;
      notifyListeners();
    }
  }

  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
  }

  void toggleLanguage() {
    // Cycle through languages: EN → AR → KU → TR → FA → EN
    final currentIndex = supportedLocales.indexOf(_currentLocale);
    final nextIndex = (currentIndex + 1) % supportedLocales.length;
    _currentLocale = supportedLocales[nextIndex];
    notifyListeners();
  }

  String getLanguageDisplayName(Locale locale) {
    switch (locale.languageCode) {
      case 'en': return 'English';
      case 'ar': return 'العربية';
      case 'ku': return 'کوردی';
      case 'tr': return 'Türkçe';
      case 'fa': return 'فارسی';
      default: return locale.languageCode.toUpperCase();
    }
  }
}
