import { Language } from '../stores/languageStore'

// Translation keys for English and Arabic
export const translations: Record<Language, Record<string, string>> = {
  en: {
    // Dashboard
    'dashboard.title': 'TSH ERP Dashboard',
    'dashboard.lastUpdated': 'Last updated',
    'dashboard.refresh': 'Refresh',
    'dashboard.loading': 'Loading dashboard data...',
    'dashboard.someDataOutdated': 'Some data may be outdated',
    
    // Financial Overview
    'financial.title': 'Financial Overview',
    'financial.totalReceivables': 'Total Receivables',
    'financial.totalPayables': 'Total Payables',
    'financial.stockValue': 'Stock Value (Cost)',
    'financial.amountOwedToUs': 'Amount owed to us',
    'financial.amountWeOwe': 'Amount we owe',
    'financial.currentInventoryCost': 'Current inventory cost',
    
    // Inventory
    'inventory.title': 'Inventory Summary',
    'inventory.positiveItems': 'Positive Items in Warehouse',
    'inventory.totalPieces': 'Total Pieces Available',
    
    // Staff
    'staff.title': 'Staff Summary',
    'staff.partnerSalesmen': 'Partner Salesmen',
    'staff.travelSalespersons': 'Travel Salespersons',
    
    // Money Boxes
    'moneyBoxes.title': 'Money Boxes',
    'moneyBoxes.mainBox': 'Main Money Box',
    'moneyBoxes.fratAwsatVector': 'Frat Awsat Vector',
    'moneyBoxes.firstSouthVector': 'First South Vector',
    'moneyBoxes.northVector': 'North Vector',
    'moneyBoxes.westVector': 'West Vector',
    'moneyBoxes.daylaBox': 'Dayla Money Box',
    'moneyBoxes.baghdadBox': 'Baghdad Money Box',
    'moneyBoxes.totalCash': 'Total Cash',
    'moneyBoxes.primaryCashFlow': 'Primary cash flow',
    'moneyBoxes.centralRegion': 'Central region',
    'moneyBoxes.southernRegion': 'Southern region',
    'moneyBoxes.northernRegion': 'Northern region',
    'moneyBoxes.westernRegion': 'Western region',
    'moneyBoxes.daylaOperations': 'Dayla operations',
    'moneyBoxes.baghdadOperations': 'Baghdad operations',
    'moneyBoxes.allMoneyBoxes': 'All money boxes',
    
    // Quick Actions
    'quickActions.title': 'Quick Actions',
    'quickActions.viewReports': 'View Reports',
    'quickActions.addTransaction': 'Add Transaction',
    'quickActions.checkInventory': 'Check Inventory',
    'quickActions.manageStaff': 'Manage Staff',
    
    // Navigation
    'nav.dashboard': 'Dashboard',
    'nav.hr': 'HR Management',
    'nav.sales': 'Sales Management',
    
    // HR Module
    'hr.title': 'HR Management',
    'hr.description': 'HR module is working! This will contain employee management, payroll, and more.',
    
    // Sales Module
    'sales.title': 'Sales Management',
    'sales.description': 'Sales module is working! This will contain customers, orders, invoices, and more.',
    
    // Language Switcher
    'language.english': 'English',
    'language.arabic': 'العربية',
    'language.switch': 'Switch Language',
    
    // Common
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.cancel': 'Cancel',
    'common.save': 'Save',
    'common.edit': 'Edit',
    'common.delete': 'Delete',
    'common.add': 'Add',
    'common.search': 'Search',
    'common.filter': 'Filter',
    'common.export': 'Export',
    'common.import': 'Import',
    'common.print': 'Print',
  },
  ar: {
    // Dashboard
    'dashboard.title': 'لوحة تحكم نظام TSH ERP',
    'dashboard.lastUpdated': 'آخر تحديث',
    'dashboard.refresh': 'تحديث',
    'dashboard.loading': 'جاري تحميل بيانات اللوحة...',
    'dashboard.someDataOutdated': 'قد تكون بعض البيانات غير محدثة',
    
    // Financial Overview
    'financial.title': 'نظرة عامة مالية',
    'financial.totalReceivables': 'إجمالي المستحقات',
    'financial.totalPayables': 'إجمالي المدفوعات',
    'financial.stockValue': 'قيمة المخزون (التكلفة)',
    'financial.amountOwedToUs': 'المبلغ المستحق لنا',
    'financial.amountWeOwe': 'المبلغ الذي ندين به',
    'financial.currentInventoryCost': 'تكلفة المخزون الحالي',
    
    // Inventory
    'inventory.title': 'ملخص المخزون',
    'inventory.positiveItems': 'الأصناف الموجبة في المستودع',
    'inventory.totalPieces': 'إجمالي القطع المتاحة',
    
    // Staff
    'staff.title': 'ملخص الموظفين',
    'staff.partnerSalesmen': 'مندوبي الشركاء',
    'staff.travelSalespersons': 'مندوبي السفر',
    
    // Money Boxes
    'moneyBoxes.title': 'صناديق النقد',
    'moneyBoxes.mainBox': 'الصندوق الرئيسي',
    'moneyBoxes.fratAwsatVector': 'فرات أوسط فيكتور',
    'moneyBoxes.firstSouthVector': 'فيكتور الجنوب الأول',
    'moneyBoxes.northVector': 'فيكتور الشمال',
    'moneyBoxes.westVector': 'فيكتور الغرب',
    'moneyBoxes.daylaBox': 'صندوق ديالى',
    'moneyBoxes.baghdadBox': 'صندوق بغداد',
    'moneyBoxes.totalCash': 'إجمالي النقد',
    'moneyBoxes.primaryCashFlow': 'التدفق النقدي الأساسي',
    'moneyBoxes.centralRegion': 'المنطقة الوسطى',
    'moneyBoxes.southernRegion': 'المنطقة الجنوبية',
    'moneyBoxes.northernRegion': 'المنطقة الشمالية',
    'moneyBoxes.westernRegion': 'المنطقة الغربية',
    'moneyBoxes.daylaOperations': 'عمليات ديالى',
    'moneyBoxes.baghdadOperations': 'عمليات بغداد',
    'moneyBoxes.allMoneyBoxes': 'جميع صناديق النقد',
    
    // Quick Actions
    'quickActions.title': 'إجراءات سريعة',
    'quickActions.viewReports': 'عرض التقارير',
    'quickActions.addTransaction': 'إضافة معاملة',
    'quickActions.checkInventory': 'فحص المخزون',
    'quickActions.manageStaff': 'إدارة الموظفين',
    
    // Navigation
    'nav.dashboard': 'لوحة التحكم',
    'nav.hr': 'إدارة الموارد البشرية',
    'nav.sales': 'إدارة المبيعات',
    
    // HR Module
    'hr.title': 'إدارة الموارد البشرية',
    'hr.description': 'وحدة الموارد البشرية تعمل! ستحتوي على إدارة الموظفين والرواتب والمزيد.',
    
    // Sales Module
    'sales.title': 'إدارة المبيعات',
    'sales.description': 'وحدة المبيعات تعمل! ستحتوي على العملاء والطلبات والفواتير والمزيد.',
    
    // Language Switcher
    'language.english': 'English',
    'language.arabic': 'العربية',
    'language.switch': 'تغيير اللغة',
    
    // Common
    'common.loading': 'جاري التحميل...',
    'common.error': 'خطأ',
    'common.success': 'نجح',
    'common.cancel': 'إلغاء',
    'common.save': 'حفظ',
    'common.edit': 'تعديل',
    'common.delete': 'حذف',
    'common.add': 'إضافة',
    'common.search': 'بحث',
    'common.filter': 'تصفية',
    'common.export': 'تصدير',
    'common.import': 'استيراد',
    'common.print': 'طباعة',
  }
}

// Translation function
export const t = (key: string, language: Language): string => {
  return translations[language]?.[key] || key
}
