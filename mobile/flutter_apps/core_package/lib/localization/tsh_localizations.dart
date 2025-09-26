import 'package:flutter/material.dart';

/// TSH ERP System Localization
/// Comprehensive Arabic/English translations with RTL support
class TSHLocalizations {
  final Locale locale;

  TSHLocalizations(this.locale);

  static TSHLocalizations? of(BuildContext context) {
    return Localizations.of<TSHLocalizations>(context, TSHLocalizations);
  }

  static const LocalizationsDelegate<TSHLocalizations> delegate = 
      _TSHLocalizationsDelegate();

  static const List<Locale> supportedLocales = [
    Locale('en', 'US'), // English
    Locale('ar', 'IQ'), // Arabic (Iraq)
  ];

  // ===============================================
  // COMMON TRANSLATIONS - Used across all apps
  // ===============================================
  static const Map<String, Map<String, String>> _localizedValues = {
    'en': {
      // App Names
      'tsh_erp': 'TSH ERP System',
      'tsh_admin_app': 'TSH Admin App',
      'hr_management': 'HR Management',
      'retailer_shop': 'Retailer Shop',
      'inventory_management': 'Inventory Management',
      'travel_salesperson': 'Travel Salesperson',
      'wholesale_client': 'Wholesale Client',
      'tsh_consumer_app': 'TSH Consumer App',
      'partner_salesperson': 'Partner Salesperson',
      
      // Navigation
      'dashboard': 'Dashboard',
      'home': 'Home',
      'menu': 'Menu',
      'settings': 'Settings',
      'profile': 'Profile',
      'notifications': 'Notifications',
      'search': 'Search',
      'back': 'Back',
      'next': 'Next',
      'save': 'Save',
      'cancel': 'Cancel',
      'delete': 'Delete',
      'edit': 'Edit',
      'add': 'Add',
      'view': 'View',
      'submit': 'Submit',
      
      // Common Actions
      'login': 'Login',
      'logout': 'Logout',
      'refresh': 'Refresh',
      'loading': 'Loading...',
      'error': 'Error',
      'success': 'Success',
      'warning': 'Warning',
      'info': 'Information',
      'confirm': 'Confirm',
      'close': 'Close',
      
      // Business Terms
      'sales': 'Sales',
      'purchases': 'Purchases',
      'inventory': 'Inventory',
      'customers': 'Customers',
      'vendors': 'Vendors',
      'employees': 'Employees',
      'products': 'Products',
      'orders': 'Orders',
      'invoices': 'Invoices',
      'payments': 'Payments',
      'reports': 'Reports',
      'analytics': 'Analytics',
      
      // Financial Terms
      'cash': 'Cash',
      'receivables': 'Receivables',
      'payables': 'Payables',
      'revenue': 'Revenue',
      'expenses': 'Expenses',
      'profit': 'Profit',
      'commission': 'Commission',
      'salary': 'Salary',
      'balance': 'Balance',
      'total': 'Total',
      'amount': 'Amount',
      'price': 'Price',
      'cost': 'Cost',
      'discount': 'Discount',
      'tax': 'Tax',
      
      // Status Terms
      'active': 'Active',
      'inactive': 'Inactive',
      'pending': 'Pending',
      'approved': 'Approved',
      'rejected': 'Rejected',
      'completed': 'Completed',
      'cancelled': 'Cancelled',
      'in_progress': 'In Progress',
      'draft': 'Draft',
      'published': 'Published',
      
      // Time & Date
      'today': 'Today',
      'yesterday': 'Yesterday',
      'this_week': 'This Week',
      'this_month': 'This Month',
      'this_year': 'This Year',
      'date': 'Date',
      'time': 'Time',
      'duration': 'Duration',
      
      // Admin Dashboard Specific
      'executive_summary': 'Executive Summary',
      'available_cash': 'Available Cash',
      'total_receivables': 'Total Receivables',
      'inventory_valuation': 'Inventory Valuation',
      'total_payables': 'Total Payables',
      'business_overview': 'Business Overview',
      'financial_metrics': 'Financial Metrics',
      'recent_activities': 'Recent Activities',
      
      // HR Specific
      'payroll': 'Payroll',
      'attendance': 'Attendance',
      'performance': 'Performance',
      'leave_management': 'Leave Management',
      'employee_records': 'Employee Records',
      'recruitment': 'Recruitment',
      'training': 'Training',
      'hr_policies': 'HR Policies',
      
      // POS & Retail Specific
      'point_of_sale': 'Point of Sale',
      'pos': 'POS',
      'barcode_scanner': 'Barcode Scanner',
      'checkout': 'Checkout',
      'cart': 'Cart',
      'receipt': 'Receipt',
      'returns': 'Returns',
      'exchanges': 'Exchanges',
      'gift_cards': 'Gift Cards',
      
      // Inventory Specific
      'stock_levels': 'Stock Levels',
      'low_stock': 'Low Stock',
      'out_of_stock': 'Out of Stock',
      'reorder_point': 'Reorder Point',
      'stock_movements': 'Stock Movements',
      'warehouse': 'Warehouse',
      'locations': 'Locations',
      'categories': 'Categories',
      
      // Travel Salesperson Specific
      'money_transfer': 'Money Transfer',
      'gps_tracking': 'GPS Tracking',
      'location': 'Location',
      'route': 'Route',
      'visits': 'Visits',
      'commission_tracking': 'Commission Tracking',
      'transfer_verification': 'Transfer Verification',
      'photo_upload': 'Photo Upload',
      
      // Messages
      'welcome_message': 'Welcome to TSH ERP System',
      'login_success': 'Login successful',
      'login_failed': 'Login failed',
      'data_saved': 'Data saved successfully',
      'data_deleted': 'Data deleted successfully',
      'operation_failed': 'Operation failed',
      'network_error': 'Network connection error',
      'try_again': 'Please try again',
      'no_data': 'No data available',
      'loading_data': 'Loading data...',
    },
    
    'ar': {
             // App Names
       'tsh_erp': 'نظام TSH الإداري',
       'tsh_admin_app': 'تطبيق TSH الإداري',
       'hr_management': 'إدارة الموارد البشرية',
       'retailer_shop': 'متجر التجزئة',
       'inventory_management': 'إدارة المخزون',
       'travel_salesperson': 'مندوب مبيعات متنقل',
       'wholesale_client': 'عميل جملة',
       'tsh_consumer_app': 'تطبيق TSH للمستهلكين',
       'partner_salesperson': 'مندوب شريك',
      
      // Navigation
      'dashboard': 'الرئيسية',
      'home': 'الصفحة الرئيسية',
      'menu': 'القائمة',
      'settings': 'الإعدادات',
      'profile': 'الملف الشخصي',
      'notifications': 'الإشعارات',
      'search': 'البحث',
      'back': 'رجوع',
      'next': 'التالي',
      'save': 'حفظ',
      'cancel': 'إلغاء',
      'delete': 'حذف',
      'edit': 'تحرير',
      'add': 'إضافة',
      'view': 'عرض',
      'submit': 'إرسال',
      
      // Common Actions
      'login': 'تسجيل دخول',
      'logout': 'تسجيل خروج',
      'refresh': 'تحديث',
      'loading': 'جاري التحميل...',
      'error': 'خطأ',
      'success': 'نجح',
      'warning': 'تحذير',
      'info': 'معلومات',
      'confirm': 'تأكيد',
      'close': 'إغلاق',
      
      // Business Terms
      'sales': 'المبيعات',
      'purchases': 'المشتريات',
      'inventory': 'المخزون',
      'customers': 'العملاء',
      'vendors': 'الموردين',
      'employees': 'الموظفين',
      'products': 'المنتجات',
      'orders': 'الطلبات',
      'invoices': 'الفواتير',
      'payments': 'المدفوعات',
      'reports': 'التقارير',
      'analytics': 'التحليلات',
      
      // Financial Terms
      'cash': 'النقد المتاح',
      'receivables': 'المستحقات',
      'payables': 'الالتزامات',
      'revenue': 'الإيرادات',
      'expenses': 'المصروفات',
      'profit': 'الربح',
      'commission': 'العمولة',
      'salary': 'الراتب',
      'balance': 'الرصيد',
      'total': 'الإجمالي',
      'amount': 'المبلغ',
      'price': 'السعر',
      'cost': 'التكلفة',
      'discount': 'الخصم',
      'tax': 'الضريبة',
      
      // Status Terms
      'active': 'نشط',
      'inactive': 'غير نشط',
      'pending': 'قيد الانتظار',
      'approved': 'موافق عليه',
      'rejected': 'مرفوض',
      'completed': 'مكتمل',
      'cancelled': 'ملغي',
      'in_progress': 'قيد التنفيذ',
      'draft': 'مسودة',
      'published': 'منشور',
      
      // Time & Date
      'today': 'اليوم',
      'yesterday': 'أمس',
      'this_week': 'هذا الأسبوع',
      'this_month': 'هذا الشهر',
      'this_year': 'هذا العام',
      'date': 'التاريخ',
      'time': 'الوقت',
      'duration': 'المدة',
      
      // Admin Dashboard Specific
      'executive_summary': 'الملخص التنفيذي',
      'available_cash': 'النقد المتاح',
      'total_receivables': 'إجمالي المستحقات',
      'inventory_valuation': 'تقييم المخزون',
      'total_payables': 'إجمالي الالتزامات',
      'business_overview': 'نظرة عامة على الأعمال',
      'financial_metrics': 'المؤشرات المالية',
      'recent_activities': 'الأنشطة الأخيرة',
      
      // HR Specific
      'payroll': 'الرواتب',
      'attendance': 'الحضور',
      'performance': 'الأداء',
      'leave_management': 'إدارة الإجازات',
      'employee_records': 'سجلات الموظفين',
      'recruitment': 'التوظيف',
      'training': 'التدريب',
      'hr_policies': 'سياسات الموارد البشرية',
      
      // POS & Retail Specific
      'point_of_sale': 'نقطة البيع',
      'pos': 'نقطة البيع',
      'barcode_scanner': 'ماسح الباركود',
      'checkout': 'الدفع',
      'cart': 'السلة',
      'receipt': 'الإيصال',
      'returns': 'المرتجعات',
      'exchanges': 'التبديل',
      'gift_cards': 'بطاقات الهدايا',
      
      // Inventory Specific
      'stock_levels': 'مستويات المخزون',
      'low_stock': 'مخزون منخفض',
      'out_of_stock': 'نفد من المخزون',
      'reorder_point': 'نقطة إعادة الطلب',
      'stock_movements': 'حركات المخزون',
      'warehouse': 'المستودع',
      'locations': 'المواقع',
      'categories': 'الفئات',
      
      // Travel Salesperson Specific
      'money_transfer': 'تحويل الأموال',
      'gps_tracking': 'تتبع GPS',
      'location': 'الموقع',
      'route': 'المسار',
      'visits': 'الزيارات',
      'commission_tracking': 'تتبع العمولة',
      'transfer_verification': 'التحقق من التحويل',
      'photo_upload': 'رفع الصورة',
      
      // Messages
      'welcome_message': 'مرحباً بك في نظام TSH الإداري',
      'login_success': 'تم تسجيل الدخول بنجاح',
      'login_failed': 'فشل تسجيل الدخول',
      'data_saved': 'تم حفظ البيانات بنجاح',
      'data_deleted': 'تم حذف البيانات بنجاح',
      'operation_failed': 'فشلت العملية',
      'network_error': 'خطأ في الاتصال بالشبكة',
      'try_again': 'يرجى المحاولة مرة أخرى',
      'no_data': 'لا توجد بيانات',
      'loading_data': 'جاري تحميل البيانات...',
    },
  };

  String translate(String key) {
    return _localizedValues[locale.languageCode]?[key] ?? key;
  }

  // Convenience getters for common translations
  String get appTitle => translate('tsh_erp');
  String get dashboard => translate('dashboard');
  String get settings => translate('settings');
  String get loading => translate('loading');
  String get save => translate('save');
  String get cancel => translate('cancel');
  String get welcomeMessage => translate('welcome_message');
  
  // Business specific getters
  String get availableCash => translate('available_cash');
  String get totalReceivables => translate('total_receivables');
  String get inventoryValuation => translate('inventory_valuation');
  String get totalPayables => translate('total_payables');
  
  // Currency formatting with localization
  String formatCurrency(double amount) {
    if (locale.languageCode == 'ar') {
      return '${amount.toStringAsFixed(0).replaceAllMapped(
        RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
        (Match m) => '${m[1]},',
      )} دينار عراقي';
    } else {
      return '${amount.toStringAsFixed(0).replaceAllMapped(
        RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
        (Match m) => '${m[1]},',
      )} IQD';
    }
  }
  
  // RTL support helper
  bool get isRTL => locale.languageCode == 'ar';
  
  TextDirection get textDirection => isRTL ? TextDirection.rtl : TextDirection.ltr;
}

class _TSHLocalizationsDelegate extends LocalizationsDelegate<TSHLocalizations> {
  const _TSHLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['en', 'ar'].contains(locale.languageCode);
  }

  @override
  Future<TSHLocalizations> load(Locale locale) async {
    return TSHLocalizations(locale);
  }

  @override
  bool shouldReload(_TSHLocalizationsDelegate old) => false;
}

/// Language Service for managing app language state
class LanguageService extends ChangeNotifier {
  Locale _currentLocale = const Locale('en', 'US');
  bool _isDarkMode = false;

  Locale get currentLocale => _currentLocale;
  bool get isDarkMode => _isDarkMode;
  bool get isRTL => _currentLocale.languageCode == 'ar';

  void changeLanguage(String languageCode) {
    if (languageCode == 'ar') {
      _currentLocale = const Locale('ar', 'IQ');
    } else {
      _currentLocale = const Locale('en', 'US');
    }
    notifyListeners();
  }

  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
  }

  void toggleLanguage() {
    if (_currentLocale.languageCode == 'en') {
      changeLanguage('ar');
    } else {
      changeLanguage('en');
    }
  }
} 