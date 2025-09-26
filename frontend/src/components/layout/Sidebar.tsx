import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'
import {
  LayoutDashboard,
  Users,
  Building,
  Warehouse,
  Package,
  UserCheck,
  Truck,
  ArrowRightLeft,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  LogOut,
  Database,
  ShoppingCart,
  FileText,
  Receipt,
  CreditCard,
  Calculator,
  TrendingUp,
  BarChart3,
  Tags,
  ClipboardList,
  PlusCircle,
  Banknote,
  WalletCards,
  UserPlus,
  Award,
  Target,
  Shield,
} from 'lucide-react'

interface NavItem {
  nameKey: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  permissions: string[]
}

interface NavGroup {
  nameKey: string
  icon: React.ComponentType<{ className?: string }>
  permissions: string[]
  items: NavItem[]
}

const getNavigationItems = (): (NavGroup | NavItem)[] => [
  {
    nameKey: 'dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    permissions: ['dashboard.view'],
  },
  {
    nameKey: 'humanResources',
    icon: UserPlus,
    permissions: ['hr.view'],
    items: [
      {
        nameKey: 'users',
        href: '/users',
        icon: Users,
        permissions: ['users.view', 'hr.view'],
      },
      {
        nameKey: 'permissions',
        href: '/permissions',
        icon: Shield,
        permissions: ['admin', 'permissions.manage'],
      },
      {
        nameKey: 'employees',
        href: '/hr/employees',
        icon: UserPlus,
        permissions: ['hr.view'],
      },
      {
        nameKey: 'payroll',
        href: '/hr/payroll',
        icon: Calculator,
        permissions: ['hr.view'],
      },
      {
        nameKey: 'attendance',
        href: '/hr/attendance',
        icon: Users,
        permissions: ['hr.view'],
      },
      {
        nameKey: 'performance',
        href: '/hr/performance',
        icon: TrendingUp,
        permissions: ['hr.view'],
      },
      {
        nameKey: 'achievements',
        href: '/hr/achievements',
        icon: Award,
        permissions: ['hr.view'],
      },
      {
        nameKey: 'challenges',
        href: '/hr/challenges',
        icon: Target,
        permissions: ['hr.view'],
      },
    ],
  },
  {
    nameKey: 'organization',
    icon: Building,
    permissions: ['branches.view'],
    items: [
      {
        nameKey: 'branches',
        href: '/branches',
        icon: Building,
        permissions: ['branches.view'],
      },
      {
        nameKey: 'warehouses',
        href: '/warehouses',
        icon: Warehouse,
        permissions: ['warehouses.view'],
      },
    ],
  },
  {
    nameKey: 'inventory',
    icon: Package,
    permissions: ['inventory.view', 'items.view', 'admin'],
    items: [
      {
        nameKey: 'items',
        href: '/items',
        icon: Package,
        permissions: ['items.view', 'admin'],
      },
      {
        nameKey: 'priceLists',
        href: '/inventory/price-lists',
        icon: Tags,
        permissions: ['inventory.view', 'admin'],
      },
      {
        nameKey: 'adjustments',
        href: '/inventory/adjustments',
        icon: ClipboardList,
        permissions: ['inventory.view', 'admin'],
      },
      {
        nameKey: 'movements',
        href: '/inventory/movements',
        icon: ArrowRightLeft,
        permissions: ['inventory.view', 'admin'],
      },
    ],
  },
  {
    nameKey: 'sales',
    icon: ShoppingCart,
    permissions: ['sales.view'],
    items: [
      {
        nameKey: 'customers',
        href: '/customers',
        icon: UserCheck,
        permissions: ['customers.view'],
      },
      {
        nameKey: 'orders',
        href: '/sales/orders',
        icon: ShoppingCart,
        permissions: ['sales.view'],
      },
      {
        nameKey: 'quotations',
        href: '/sales/quotations',
        icon: FileText,
        permissions: ['sales.view'],
      },
      {
        nameKey: 'invoices',
        href: '/sales/invoices',
        icon: Receipt,
        permissions: ['sales.view'],
      },
      {
        nameKey: 'creditNotes',
        href: '/sales/credit-notes',
        icon: FileText,
        permissions: ['sales.view'],
      },
      {
        nameKey: 'payments',
        href: '/sales/payments',
        icon: CreditCard,
        permissions: ['sales.view'],
      },
      {
        nameKey: 'pointOfSale',
        href: '/pos',
        icon: CreditCard,
        permissions: ['pos.view'],
      },
      {
        nameKey: 'terminals',
        href: '/pos/terminals',
        icon: CreditCard,
        permissions: ['pos.view'],
      },
      {
        nameKey: 'sessions',
        href: '/pos/sessions',
        icon: FileText,
        permissions: ['pos.view'],
      },
      {
        nameKey: 'transactions',
        href: '/pos/transactions',
        icon: ArrowRightLeft,
        permissions: ['pos.view'],
      },
    ],
  },
  {
    nameKey: 'purchasing',
    icon: Truck,
    permissions: ['purchase.view'],
    items: [
      {
        nameKey: 'vendors',
        href: '/vendors',
        icon: Truck,
        permissions: ['vendors.view'],
      },
      {
        nameKey: 'purchaseOrders',
        href: '/purchase/orders',
        icon: Receipt,
        permissions: ['purchase.view'],
      },
      {
        nameKey: 'purchaseInvoices',
        href: '/purchase/invoices',
        icon: FileText,
        permissions: ['purchase.view'],
      },
      {
        nameKey: 'debitNotes',
        href: '/purchase/debit-notes',
        icon: FileText,
        permissions: ['purchase.view'],
      },
      {
        nameKey: 'paymentMade',
        href: '/purchase/payments',
        icon: CreditCard,
        permissions: ['purchase.view'],
      },
    ],
  },
  {
    nameKey: 'expenses',
    icon: Receipt,
    permissions: ['expenses.view'],
    items: [
      {
        nameKey: 'expensesList',
        href: '/expenses',
        icon: Receipt,
        permissions: ['expenses.view'],
      },
      {
        nameKey: 'expenseCategories',
        href: '/expenses/categories',
        icon: Tags,
        permissions: ['expenses.view'],
      },
      {
        nameKey: 'expenseReports',
        href: '/expenses/reports',
        icon: BarChart3,
        permissions: ['expenses.view'],
      },
    ],
  },
  {
    nameKey: 'accounting',
    icon: Calculator,
    permissions: ['accounting.view'],
    items: [
      {
        nameKey: 'chartOfAccounts',
        href: '/accounting/chart-of-accounts',
        icon: FileText,
        permissions: ['accounting.view'],
      },
      {
        nameKey: 'journalEntries',
        href: '/accounting/journal-entries',
        icon: PlusCircle,
        permissions: ['accounting.view'],
      },
      {
        nameKey: 'generalLedger',
        href: '/accounting/general-ledger',
        icon: Calculator,
        permissions: ['accounting.view'],
      },
      {
        nameKey: 'trialBalance',
        href: '/accounting/trial-balance',
        icon: TrendingUp,
        permissions: ['accounting.view'],
      },
      {
        nameKey: 'reports',
        href: '/accounting/reports',
        icon: BarChart3,
        permissions: ['accounting.view'],
      },
    ],
  },
  {
    nameKey: 'cashFlow',
    icon: WalletCards,
    permissions: ['cashflow.view'],
    items: [
      {
        nameKey: 'cashBoxes',
        href: '/cashflow/cash-boxes',
        icon: Banknote,
        permissions: ['cashflow.view'],
      },
      {
        nameKey: 'cashTransactions',
        href: '/cashflow/transactions',
        icon: ArrowRightLeft,
        permissions: ['cashflow.view'],
      },
      {
        nameKey: 'transfers',
        href: '/cashflow/transfers',
        icon: BarChart3,
        permissions: ['cashflow.view'],
      },
    ],
  },
  {
    nameKey: 'financialManagement',
    icon: Calculator,
    permissions: ['financial.view', 'admin'],
    items: [
      {
        nameKey: 'financialDashboard',
        href: '/financial/dashboard',
        icon: LayoutDashboard,
        permissions: ['financial.view', 'admin'],
      },
      {
        nameKey: 'cashBoxes',
        href: '/financial/cash-boxes',
        icon: Banknote,
        permissions: ['financial.view', 'admin'],
      },
      {
        nameKey: 'bankAccounts',
        href: '/financial/bank-accounts',
        icon: WalletCards,
        permissions: ['financial.view', 'admin'],
      },
      {
        nameKey: 'digitalAccounts',
        href: '/financial/digital-accounts',
        icon: Calculator,
        permissions: ['financial.view', 'admin'],
      },
      {
        nameKey: 'moneyTransfers',
        href: '/financial/money-transfers',
        icon: ArrowRightLeft,
        permissions: ['financial.view', 'admin'],
      },
      {
        nameKey: 'transferTracking',
        href: '/financial/transfer-tracking',
        icon: TrendingUp,
        permissions: ['financial.view', 'admin'],
      },
      {
        nameKey: 'salespersonBoxes',
        href: '/financial/salesperson-boxes',
        icon: Users,
        permissions: ['financial.view', 'admin'],
      },
    ],
  },
  {
    nameKey: 'migration',
    href: '/migration',
    icon: ArrowRightLeft,
    permissions: ['migration.view'],
  },
  {
    nameKey: 'modelsSchema',
    href: '/models',
    icon: Database,
    permissions: ['admin'],
  },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['inventory', 'purchasing', 'sales'])
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { language, isRTL } = useLanguageStore()
  const t = useTranslations(language)
  
  const navigationItems = getNavigationItems()

  const hasPermission = (permissions: string[]) => {
    // Accept both frontend permission keys (e.g. 'users.view') and backend permission names (e.g. 'read_user')
    if (!user || !user.permissions) return false
    const userPerms = user.permissions || []
    // Admin shortcut
    if (userPerms.includes('admin')) return true

    const permissionAliases: Record<string, string[]> = {
      'users.view': ['users.view', 'read_user'],
      'users.manage': ['users.view', 'read_user', 'create_user', 'update_user', 'delete_user'],
      'permissions.manage': ['admin', 'permissions.manage'],
      'hr.view': ['hr.view'],
      'branches.view': ['branches.view', 'read_branch'],
      'dashboard.view': ['dashboard.view', 'admin'],
      'inventory.view': ['inventory.view', 'items.view', 'admin'],
      'items.view': ['items.view', 'admin'],
      'customers.view': ['customers.view'],
      'vendors.view': ['vendors.view'],
      'sales.view': ['sales.view'],
      'purchase.view': ['purchase.view'],
      'accounting.view': ['accounting.view'],
      'pos.view': ['pos.view'],
      'cashflow.view': ['cashflow.view'],
      'financial.view': ['financial.view', 'admin'],
      'warehouses.view': ['warehouses.view'],
      'expenses.view': ['expenses.view'],
      'migration.view': ['migration.view', 'admin'],
      // add more mappings as needed
    }

    return permissions.some((permission) => {
      const aliases = permissionAliases[permission] || [permission]
      return aliases.some(alias => userPerms.includes(alias))
    })
  }

  const toggleGroup = (groupNameKey: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupNameKey) 
        ? prev.filter(name => name !== groupNameKey)
        : [...prev, groupNameKey]
    )
  }

  const isGroupExpanded = (groupNameKey: string) => expandedGroups.includes(groupNameKey)

  const isGroupActive = (group: NavGroup) => {
    return group.items.some(item => 
      location.pathname === item.href || 
      (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
    )
  }

  const handleLogout = () => {
    logout()
  }

  return (
    <div className={cn(
      "bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 shadow-lg",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        {!collapsed && (
          <div className={`flex items-center ${isRTL ? 'space-x-reverse' : ''} space-x-3`}>
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-md">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <div>
              <span className="font-bold text-gray-900 dark:text-white text-lg">TSH ERP</span>
              <p className="text-xs text-gray-500 dark:text-gray-400">Enterprise System</p>
            </div>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-600"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4 text-gray-600 dark:text-gray-400" />
          ) : (
            <ChevronLeft className="h-4 w-4 text-gray-600 dark:text-gray-400" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {!collapsed && (
          <div className="mb-4">
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-3">
              {t.mainMenu}
            </h3>
          </div>
        )}
        <ul className="space-y-1">
          {navigationItems.map((item) => {
            if (!hasPermission(item.permissions)) return null

            // Check if it's a group or individual item
            if ('items' in item) {
              // It's a group
              const group = item
              const groupActive = isGroupActive(group)
              const groupExpanded = isGroupExpanded(group.nameKey)

              return (
                <li key={group.nameKey}>
                  <button
                    onClick={() => !collapsed && toggleGroup(group.nameKey)}
                    className={cn(
                      "group flex items-center w-full px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200 relative",
                      groupActive
                        ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25"
                        : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 hover:scale-105 hover:shadow-md",
                      collapsed && "justify-center"
                    )}
                    title={collapsed ? (t as any)[group.nameKey] || group.nameKey : undefined}
                  >
                    <group.icon className={cn(
                      "h-5 w-5 transition-colors", 
                      collapsed ? "" : isRTL ? "ml-3" : "mr-3",
                      groupActive ? "text-white" : "text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300"
                    )} />
                    {!collapsed && (
                      <>
                        <span className="truncate flex-1">{(t as any)[group.nameKey] || group.nameKey}</span>
                        <ChevronDown className={cn(
                          "h-4 w-4 transition-transform",
                          groupExpanded ? "rotate-180" : "",
                          groupActive ? "text-white" : "text-gray-500"
                        )} />
                      </>
                    )}
                  </button>
                  
                  {/* Dropdown items */}
                  {!collapsed && groupExpanded && (
                    <ul className="ml-6 mt-2 space-y-1">
                      {group.items.map((subItem) => {
                        if (!hasPermission(subItem.permissions)) return null

                        const isActive = location.pathname === subItem.href || 
                                       (subItem.href !== '/dashboard' && location.pathname.startsWith(subItem.href))

                        return (
                          <li key={subItem.nameKey}>
                            <NavLink
                              to={subItem.href}
                              className={cn(
                                "group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 relative",
                                isActive
                                  ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                                  : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-200"
                              )}
                            >
                              <subItem.icon className={`h-4 w-4 ${isRTL ? 'ml-3' : 'mr-3'}`} />
                              <span className="truncate">{(t as any)[subItem.nameKey] || subItem.nameKey}</span>
                            </NavLink>
                          </li>
                        )
                      })}
                    </ul>
                  )}
                </li>
              )
            } else {
              // It's an individual item
              const navItem = item as NavItem
              const isActive = location.pathname === navItem.href || 
                             (navItem.href !== '/dashboard' && location.pathname.startsWith(navItem.href))

              return (
                <li key={navItem.nameKey}>
                  <NavLink
                    to={navItem.href}
                    className={cn(
                      "group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200 relative",
                      isActive
                        ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25"
                        : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 hover:scale-105 hover:shadow-md",
                      collapsed && "justify-center"
                    )}
                    title={collapsed ? (t as any)[navItem.nameKey] || navItem.nameKey : undefined}
                  >
                    <navItem.icon className={cn(
                      "h-5 w-5 transition-colors", 
                      collapsed ? "" : isRTL ? "ml-3" : "mr-3",
                      isActive ? "text-white" : "text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300"
                    )} />
                    {!collapsed && <span className="truncate">{(t as any)[navItem.nameKey] || navItem.nameKey}</span>}
                    {isActive && !collapsed && (
                      <div className="absolute right-2 w-2 h-2 bg-white rounded-full opacity-75"></div>
                    )}
                  </NavLink>
                </li>
              )
            }
          })}
        </ul>
      </nav>

      {/* User Profile */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
        {!collapsed && user && (
          <div className="flex items-center space-x-3 mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
            <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center shadow-md">
              <span className="text-sm font-bold text-white">
                {user.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                {user.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate capitalize">
                {user.role} • Online
              </p>
            </div>
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          </div>
        )}
        
        <button
          onClick={handleLogout}
          className={cn(
            "group flex items-center w-full px-3 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900 rounded-xl transition-all duration-200 hover:scale-105",
            collapsed && "justify-center"
          )}
          title={collapsed ? (t as any).logout || 'Logout' : undefined}
        >
          <LogOut className={cn("h-5 w-5 group-hover:rotate-12 transition-transform", collapsed ? "" : isRTL ? "ml-3" : "mr-3")} />
          {!collapsed && <span>{(t as any).logout || 'Logout'}</span>}
        </button>
      </div>
    </div>
  )
}
