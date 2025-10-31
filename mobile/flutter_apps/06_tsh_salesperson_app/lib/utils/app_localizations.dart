import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

class AppLocalizations {
  AppLocalizations(this.locale);

  final Locale locale;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = [
    _AppLocalizationsDelegate(),
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ];

  static const List<Locale> supportedLocales = [
    Locale('ar', 'IQ'), // Arabic (Iraq)
    Locale('en', 'US'), // English (United States)
  ];

  // App strings
  String get appTitle => _localizedStrings[locale.languageCode]?['app_title'] ?? 'TSH Salesperson';
  String get dashboard => _localizedStrings[locale.languageCode]?['dashboard'] ?? 'Dashboard';
  String get customers => _localizedStrings[locale.languageCode]?['customers'] ?? 'Customers';
  String get orders => _localizedStrings[locale.languageCode]?['orders'] ?? 'Orders';
  String get products => _localizedStrings[locale.languageCode]?['products'] ?? 'Products';
  String get sales => _localizedStrings[locale.languageCode]?['sales'] ?? 'Sales';
  String get profile => _localizedStrings[locale.languageCode]?['profile'] ?? 'Profile';
  String get login => _localizedStrings[locale.languageCode]?['login'] ?? 'Login';
  String get logout => _localizedStrings[locale.languageCode]?['logout'] ?? 'Logout';
  String get email => _localizedStrings[locale.languageCode]?['email'] ?? 'Email';
  String get password => _localizedStrings[locale.languageCode]?['password'] ?? 'Password';
  String get loading => _localizedStrings[locale.languageCode]?['loading'] ?? 'Loading...';
  String get error => _localizedStrings[locale.languageCode]?['error'] ?? 'Error';
  String get success => _localizedStrings[locale.languageCode]?['success'] ?? 'Success';
  String get cancel => _localizedStrings[locale.languageCode]?['cancel'] ?? 'Cancel';
  String get confirm => _localizedStrings[locale.languageCode]?['confirm'] ?? 'Confirm';
  String get save => _localizedStrings[locale.languageCode]?['save'] ?? 'Save';
  String get delete => _localizedStrings[locale.languageCode]?['delete'] ?? 'Delete';
  String get edit => _localizedStrings[locale.languageCode]?['edit'] ?? 'Edit';
  String get add => _localizedStrings[locale.languageCode]?['add'] ?? 'Add';
  String get search => _localizedStrings[locale.languageCode]?['search'] ?? 'Search';
  String get filter => _localizedStrings[locale.languageCode]?['filter'] ?? 'Filter';
  String get sort => _localizedStrings[locale.languageCode]?['sort'] ?? 'Sort';
  String get refresh => _localizedStrings[locale.languageCode]?['refresh'] ?? 'Refresh';
  String get settings => _localizedStrings[locale.languageCode]?['settings'] ?? 'Settings';
  String get help => _localizedStrings[locale.languageCode]?['help'] ?? 'Help';
  String get about => _localizedStrings[locale.languageCode]?['about'] ?? 'About';

  // Business specific strings
  String get receivables => _localizedStrings[locale.languageCode]?['receivables'] ?? 'Receivables';
  String get commission => _localizedStrings[locale.languageCode]?['commission'] ?? 'Commission';
  String get cashBox => _localizedStrings[locale.languageCode]?['cash_box'] ?? 'Cash Box';
  String get settlement => _localizedStrings[locale.languageCode]?['settlement'] ?? 'Settlement';
  String get totalAmount => _localizedStrings[locale.languageCode]?['total_amount'] ?? 'Total Amount';
  String get orderNumber => _localizedStrings[locale.languageCode]?['order_number'] ?? 'Order Number';
  String get customerName => _localizedStrings[locale.languageCode]?['customer_name'] ?? 'Customer Name';
  String get paymentMethod => _localizedStrings[locale.languageCode]?['payment_method'] ?? 'Payment Method';
  String get status => _localizedStrings[locale.languageCode]?['status'] ?? 'Status';
  String get date => _localizedStrings[locale.languageCode]?['date'] ?? 'Date';
  String get amount => _localizedStrings[locale.languageCode]?['amount'] ?? 'Amount';
  String get currency => _localizedStrings[locale.languageCode]?['currency'] ?? 'Currency';

  // Connection strings
  String get connected => _localizedStrings[locale.languageCode]?['connected'] ?? 'Connected';
  String get disconnected => _localizedStrings[locale.languageCode]?['disconnected'] ?? 'Disconnected';
  String get noInternetConnection => _localizedStrings[locale.languageCode]?['no_internet_connection'] ?? 'No internet connection';
  String get reconnecting => _localizedStrings[locale.languageCode]?['reconnecting'] ?? 'Reconnecting...';

  static const Map<String, Map<String, String>> _localizedStrings = {
    'ar': {
      'app_title': 'TSH مندوب المبيعات',
      'dashboard': 'لوحة التحكم',
      'customers': 'العملاء',
      'orders': 'الطلبات',
      'products': 'المنتجات',
      'sales': 'المبيعات',
      'profile': 'الملف الشخصي',
      'login': 'تسجيل الدخول',
      'logout': 'تسجيل الخروج',
      'email': 'البريد الإلكتروني',
      'password': 'كلمة المرور',
      'loading': 'جاري التحميل...',
      'error': 'خطأ',
      'success': 'نجح',
      'cancel': 'إلغاء',
      'confirm': 'تأكيد',
      'save': 'حفظ',
      'delete': 'حذف',
      'edit': 'تعديل',
      'add': 'إضافة',
      'search': 'بحث',
      'filter': 'فلتر',
      'sort': 'ترتيب',
      'refresh': 'تحديث',
      'settings': 'الإعدادات',
      'help': 'المساعدة',
      'about': 'حول',
      'receivables': 'المستحقات',
      'commission': 'العمولة',
      'cash_box': 'صندوق النقد',
      'settlement': 'التسوية',
      'total_amount': 'المبلغ الإجمالي',
      'order_number': 'رقم الطلب',
      'customer_name': 'اسم العميل',
      'payment_method': 'طريقة الدفع',
      'status': 'الحالة',
      'date': 'التاريخ',
      'amount': 'المبلغ',
      'currency': 'العملة',
      'connected': 'متصل',
      'disconnected': 'غير متصل',
      'no_internet_connection': 'لا يوجد اتصال بالإنترنت',
      'reconnecting': 'جاري الاتصال...',
    },
    'en': {
      'app_title': 'TSH Salesperson',
      'dashboard': 'Dashboard',
      'customers': 'Customers',
      'orders': 'Orders',
      'products': 'Products',
      'sales': 'Sales',
      'profile': 'Profile',
      'login': 'Login',
      'logout': 'Logout',
      'email': 'Email',
      'password': 'Password',
      'loading': 'Loading...',
      'error': 'Error',
      'success': 'Success',
      'cancel': 'Cancel',
      'confirm': 'Confirm',
      'save': 'Save',
      'delete': 'Delete',
      'edit': 'Edit',
      'add': 'Add',
      'search': 'Search',
      'filter': 'Filter',
      'sort': 'Sort',
      'refresh': 'Refresh',
      'settings': 'Settings',
      'help': 'Help',
      'about': 'About',
      'receivables': 'Receivables',
      'commission': 'Commission',
      'cash_box': 'Cash Box',
      'settlement': 'Settlement',
      'total_amount': 'Total Amount',
      'order_number': 'Order Number',
      'customer_name': 'Customer Name',
      'payment_method': 'Payment Method',
      'status': 'Status',
      'date': 'Date',
      'amount': 'Amount',
      'currency': 'Currency',
      'connected': 'Connected',
      'disconnected': 'Disconnected',
      'no_internet_connection': 'No internet connection',
      'reconnecting': 'Reconnecting...',
    },
  };
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return AppLocalizations.supportedLocales.any((supportedLocale) =>
        supportedLocale.languageCode == locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
