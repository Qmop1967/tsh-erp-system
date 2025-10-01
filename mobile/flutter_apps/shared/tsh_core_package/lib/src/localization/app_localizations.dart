import 'package:flutter/material.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  static const List<Locale> supportedLocales = [
    Locale('en', 'US'),
    Locale('ar', 'SA'),
  ];

  bool get isArabic => locale.languageCode == 'ar';

  // App Title
  String get appTitle => isArabic ? 'نظام تخطيط موارد المؤسسات TSH' : 'TSH ERP System';

  // Navigation
  String get dashboard => isArabic ? 'لوحة القيادة' : 'Dashboard';
  String get sales => isArabic ? 'المبيعات' : 'Sales';
  String get products => isArabic ? 'المنتجات' : 'Products';
  String get orders => isArabic ? 'الطلبات' : 'Orders';
  String get customers => isArabic ? 'العملاء' : 'Customers';
  String get profile => isArabic ? 'الملف الشخصي' : 'Profile';

  // Common
  String get search => isArabic ? 'بحث' : 'Search';
  String get add => isArabic ? 'إضافة' : 'Add';
  String get edit => isArabic ? 'تعديل' : 'Edit';
  String get delete => isArabic ? 'حذف' : 'Delete';
  String get save => isArabic ? 'حفظ' : 'Save';
  String get cancel => isArabic ? 'إلغاء' : 'Cancel';
  String get confirm => isArabic ? 'تأكيد' : 'Confirm';
  String get loading => isArabic ? 'جاري التحميل...' : 'Loading...';
  String get error => isArabic ? 'خطأ' : 'Error';
  String get success => isArabic ? 'نجح' : 'Success';

  // Dashboard
  String get welcomeBack => isArabic ? 'مرحباً بعودتك! 👋' : 'Welcome back! 👋';
  String get readyToBoostSales => isArabic ? 'مستعد لتعزيز مبيعاتك اليوم؟' : 'Ready to boost your sales today?';
  String get performanceOverview => isArabic ? 'نظرة عامة على الأداء' : 'Performance Overview';
  String get salesToday => isArabic ? 'مبيعات اليوم' : 'Sales Today';
  String get totalOrders => isArabic ? 'إجمالي الطلبات' : 'Total Orders';
  String get totalCustomers => isArabic ? 'إجمالي العملاء' : 'Total Customers';
  String get pendingOrders => isArabic ? 'الطلبات المعلقة' : 'Pending Orders';
  String get quickSale => isArabic ? 'بيع سريع' : 'Quick Sale';

  // Sales
  String get salesCenter => isArabic ? 'مركز المبيعات' : 'Sales Center';
  String get createOrdersManagePipeline => isArabic ? 'إنشاء الطلبات وإدارة خط الأنابيب' : 'Create orders and manage your sales pipeline';
  String get newSale => isArabic ? 'بيع جديد' : 'New Sale';
  String get cart => isArabic ? 'العربة' : 'Cart';
  String get checkout => isArabic ? 'الدفع' : 'Checkout';
  String get addToCart => isArabic ? 'إضافة للعربة' : 'Add to Cart';

  // Products
  String get allProducts => isArabic ? 'جميع المنتجات' : 'All Products';
  String get activeProducts => isArabic ? 'المنتجات النشطة' : 'Active Products';
  String get lowStock => isArabic ? 'مخزون منخفض' : 'Low Stock';
  String get outOfStock => isArabic ? 'نفد من المخزن' : 'Out of Stock';
  String get price => isArabic ? 'السعر' : 'Price';
  String get stock => isArabic ? 'المخزون' : 'Stock';
  String get active => isArabic ? 'نشط' : 'Active';
  String get inactive => isArabic ? 'غير نشط' : 'Inactive';

  // Orders
  String get orderHistory => isArabic ? 'سجل الطلبات' : 'Order History';
  String get all => isArabic ? 'الكل' : 'All';
  String get pending => isArabic ? 'معلق' : 'Pending';
  String get confirmed => isArabic ? 'مؤكد' : 'Confirmed';
  String get shipped => isArabic ? 'مُرسل' : 'Shipped';
  String get delivered => isArabic ? 'مُسلم' : 'Delivered';
  String get cancelled => isArabic ? 'ملغي' : 'Cancelled';
  String get orderNumber => isArabic ? 'رقم الطلب' : 'Order Number';
  String get customer => isArabic ? 'العميل' : 'Customer';
  String get total => isArabic ? 'الإجمالي' : 'Total';
  String get status => isArabic ? 'الحالة' : 'Status';
  String get date => isArabic ? 'التاريخ' : 'Date';

  // Customers
  String get customerManagement => isArabic ? 'إدارة العملاء' : 'Customer Management';
  String get addCustomer => isArabic ? 'إضافة عميل' : 'Add Customer';
  String get region => isArabic ? 'المنطقة' : 'Region';
  String get name => isArabic ? 'الاسم' : 'Name';
  String get email => isArabic ? 'البريد الإلكتروني' : 'Email';
  String get phone => isArabic ? 'الهاتف' : 'Phone';
  String get address => isArabic ? 'العنوان' : 'Address';

  // Profile
  String get settings => isArabic ? 'الإعدادات' : 'Settings';
  String get language => isArabic ? 'اللغة' : 'Language';
  String get notifications => isArabic ? 'الإشعارات' : 'Notifications';
  String get darkMode => isArabic ? 'الوضع المظلم' : 'Dark Mode';
  String get changePassword => isArabic ? 'تغيير كلمة المرور' : 'Change Password';
  String get logout => isArabic ? 'تسجيل الخروج' : 'Logout';
  String get english => isArabic ? 'الإنجليزية' : 'English';
  String get arabic => isArabic ? 'العربية' : 'Arabic';

  // Error handling and actions
  String get errorOccurred => isArabic ? 'حدث خطأ' : 'An error occurred';
  String get retry => isArabic ? 'إعادة المحاولة' : 'Retry';

  // Dashboard specific
  String get dashboardSubtitle => isArabic ? 'مستعد لتعزيز مبيعاتك اليوم؟' : 'Ready to boost your sales today?';
  String get totalSales => isArabic ? 'إجمالي المبيعات' : 'Total Sales';
  String get quickActions => isArabic ? 'الإجراءات السريعة' : 'Quick Actions';
  String get newOrder => isArabic ? 'طلب جديد' : 'New Order';
  String get viewReports => isArabic ? 'عرض التقارير' : 'View Reports';
  String get manageInventory => isArabic ? 'إدارة المخزون' : 'Manage Inventory';
  String get recentActivity => isArabic ? 'النشاط الأخير' : 'Recent Activity';
  String get viewAll => isArabic ? 'عرض الكل' : 'View All';
  String get performance => isArabic ? 'الأداء' : 'Performance';
  String get chartPlaceholder => isArabic ? 'الرسم البياني يأتي هنا' : 'Chart comes here';
  String get order => isArabic ? 'الطلب' : 'Order';
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
