import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class TSHLocalizations {
  final Locale locale;

  TSHLocalizations(this.locale);

  static TSHLocalizations? of(BuildContext context) {
    return Localizations.of<TSHLocalizations>(context, TSHLocalizations);
  }

  static const LocalizationsDelegate<TSHLocalizations> delegate =
      _TSHLocalizationsDelegate();

  static const List<Locale> supportedLocales = [
    Locale('ar', 'IQ'),
    Locale('en', 'US'),
  ];

  // Add translation methods as needed
  String get appTitle => locale.languageCode == 'ar' ? 'عميل TSH' : 'TSH Client';
  String get home => locale.languageCode == 'ar' ? 'الرئيسية' : 'Home';
  String get products => locale.languageCode == 'ar' ? 'المنتجات' : 'Products';
  String get orders => locale.languageCode == 'ar' ? 'الطلبات' : 'Orders';
  String get account => locale.languageCode == 'ar' ? 'الحساب' : 'Account';

  // Translation method
  String translate(String key) {
    final translations = {
      // Main Navigation
      'wholesale_client': locale.languageCode == 'ar' ? 'عميل الجملة' : 'Wholesale Client',
      'dashboard': locale.languageCode == 'ar' ? 'لوحة التحكم' : 'Dashboard',
      'products': locale.languageCode == 'ar' ? 'المنتجات' : 'Products',
      'orders': locale.languageCode == 'ar' ? 'الطلبات' : 'Orders',
      'account': locale.languageCode == 'ar' ? 'الحساب' : 'Account',
      'settings': locale.languageCode == 'ar' ? 'الإعدادات' : 'Settings',

      // Profile Menu
      'my_profile': locale.languageCode == 'ar' ? 'حسابي' : 'My Profile',
      'business_info': locale.languageCode == 'ar' ? 'معلومات العمل' : 'Business Info',
      'invoices': locale.languageCode == 'ar' ? 'الفواتير' : 'Invoices',
      'payments': locale.languageCode == 'ar' ? 'المدفوعات' : 'Payments',
      'credit_notes': locale.languageCode == 'ar' ? 'إشعارات الإئتمان' : 'Credit Notes',
      'account_statement': locale.languageCode == 'ar' ? 'كشف الحساب' : 'Account Statement',
      'support_tickets': locale.languageCode == 'ar' ? 'تذاكر الدعم' : 'Support Tickets',
      'logout': locale.languageCode == 'ar' ? 'تسجيل الخروج' : 'Logout',

      // Quick Actions
      'new_order': locale.languageCode == 'ar' ? 'طلب جديد' : 'New Order',
      'reorder': locale.languageCode == 'ar' ? 'إعادة الطلب' : 'Reorder',
      'pay_balance': locale.languageCode == 'ar' ? 'سداد الرصيد' : 'Pay Balance',

      // Dashboard Labels
      'available_credit': locale.languageCode == 'ar' ? 'الإئتمان المتاح' : 'Available Credit',
      'outstanding_balance': locale.languageCode == 'ar' ? 'الرصيد المستحق' : 'Outstanding Balance',
      'monthly_purchases': locale.languageCode == 'ar' ? 'مشتريات الشهر' : 'Monthly Purchases',
      'pending_orders': locale.languageCode == 'ar' ? 'الطلبات المعلقة' : 'Pending Orders',
      'this_month': locale.languageCode == 'ar' ? 'هذا الشهر' : 'This Month',
      'recent_orders': locale.languageCode == 'ar' ? 'الطلبات الأخيرة' : 'Recent Orders',
      'featured_products': locale.languageCode == 'ar' ? 'منتجات مميزة' : 'Featured Products',

      // Support
      'create_ticket': locale.languageCode == 'ar' ? 'إنشاء تذكرة' : 'Create Ticket',
      'my_tickets': locale.languageCode == 'ar' ? 'تذاكري' : 'My Tickets',
      'ticket_subject': locale.languageCode == 'ar' ? 'موضوع التذكرة' : 'Ticket Subject',
      'ticket_description': locale.languageCode == 'ar' ? 'الوصف' : 'Description',
      'priority': locale.languageCode == 'ar' ? 'الأولوية' : 'Priority',
      'status': locale.languageCode == 'ar' ? 'الحالة' : 'Status',

      // Payments
      'payment_history': locale.languageCode == 'ar' ? 'سجل المدفوعات' : 'Payment History',
      'payment_amount': locale.languageCode == 'ar' ? 'المبلغ' : 'Amount',
      'payment_date': locale.languageCode == 'ar' ? 'التاريخ' : 'Date',
      'payment_method': locale.languageCode == 'ar' ? 'طريقة الدفع' : 'Payment Method',
      'make_payment': locale.languageCode == 'ar' ? 'إجراء دفع' : 'Make Payment',

      // Invoices
      'invoice_number': locale.languageCode == 'ar' ? 'رقم الفاتورة' : 'Invoice Number',
      'invoice_date': locale.languageCode == 'ar' ? 'تاريخ الفاتورة' : 'Invoice Date',
      'due_date': locale.languageCode == 'ar' ? 'تاريخ الاستحقاق' : 'Due Date',
      'download': locale.languageCode == 'ar' ? 'تحميل' : 'Download',
      'view': locale.languageCode == 'ar' ? 'عرض' : 'View',

      // Common
      'search': locale.languageCode == 'ar' ? 'بحث' : 'Search',
      'filter': locale.languageCode == 'ar' ? 'تصفية' : 'Filter',
      'save': locale.languageCode == 'ar' ? 'حفظ' : 'Save',
      'cancel': locale.languageCode == 'ar' ? 'إلغاء' : 'Cancel',
      'submit': locale.languageCode == 'ar' ? 'إرسال' : 'Submit',
      'close': locale.languageCode == 'ar' ? 'إغلاق' : 'Close',
      'loading': locale.languageCode == 'ar' ? 'جاري التحميل...' : 'Loading...',
      'error': locale.languageCode == 'ar' ? 'خطأ' : 'Error',
      'success': locale.languageCode == 'ar' ? 'نجح' : 'Success',
    };
    return translations[key] ?? key;
  }

  // Currency formatting method
  String formatCurrency(double amount) {
    return '${amount.toStringAsFixed(2)} IQD';
  }
}

class _TSHLocalizationsDelegate
    extends LocalizationsDelegate<TSHLocalizations> {
  const _TSHLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['ar', 'en'].contains(locale.languageCode);
  }

  @override
  Future<TSHLocalizations> load(Locale locale) {
    return SynchronousFuture<TSHLocalizations>(TSHLocalizations(locale));
  }

  @override
  bool shouldReload(_TSHLocalizationsDelegate old) => false;
}
