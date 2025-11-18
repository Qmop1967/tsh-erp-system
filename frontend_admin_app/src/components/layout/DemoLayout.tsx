import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Users,
  ShoppingCart,
  Package,
  Calculator,
  Receipt,
  ChevronDown,
  ChevronRight,
  Menu,
  X,
  Settings,
  LogOut,
  Home
} from 'lucide-react'
import { useLanguageStore } from '../../stores/languageStore'
import { useTranslations } from '../../lib/translations'

interface LayoutProps {
  children: React.ReactNode
}

interface MenuItem {
  id: string
  labelKey: string
  icon: React.ReactNode
  path?: string
  children?: MenuItem[]
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [expandedItems, setExpandedItems] = useState<string[]>(['dashboard'])
  const location = useLocation()
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  
  // Demo user for testing
  const user = { name: 'Demo User', role: 'Admin' }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    )
  }

  const isActiveRoute = (path: string) => {
    return location.pathname === path
  }

  const isParentActive = (children: MenuItem[]) => {
    return children.some(child => child.path && isActiveRoute(child.path))
  }

  const menuItems: MenuItem[] = [
    {
      id: 'dashboard',
      labelKey: 'dashboard',
      icon: <Home className="w-5 h-5" />,
      path: '/dashboard'
    },
    {
      id: 'hr',
      labelKey: 'humanResources',
      icon: <Users className="w-5 h-5" />,
      children: [
        { id: 'users', labelKey: 'users', icon: <Users className="w-4 h-4" />, path: '/hr/users' },
        { id: 'employees', labelKey: 'employees', icon: <Users className="w-4 h-4" />, path: '/hr/employees' }
      ]
    },
    {
      id: 'sales',
      labelKey: 'salesModel',
      icon: <ShoppingCart className="w-5 h-5" />,
      children: [
        { id: 'customers', labelKey: 'customers', icon: <Users className="w-4 h-4" />, path: '/sales/customers' },
        { id: 'sale-orders', labelKey: 'saleOrders', icon: <ShoppingCart className="w-4 h-4" />, path: '/sales/orders' },
        { id: 'invoices', labelKey: 'invoices', icon: <Receipt className="w-4 h-4" />, path: '/sales/invoices' },
        { id: 'payment-received', labelKey: 'paymentReceived', icon: <Receipt className="w-4 h-4" />, path: '/sales/payments' },
        { id: 'credit-note', labelKey: 'creditNotes', icon: <Receipt className="w-4 h-4" />, path: '/sales/credit-notes' },
        { id: 'refund', labelKey: 'refund', icon: <Receipt className="w-4 h-4" />, path: '/sales/refunds' }
      ]
    },
    {
      id: 'purchases',
      labelKey: 'purchasesModel',
      icon: <Package className="w-5 h-5" />,
      children: [
        { id: 'vendors', labelKey: 'vendors', icon: <Users className="w-4 h-4" />, path: '/purchases/vendors' },
        { id: 'purchase-orders', labelKey: 'purchaseOrders', icon: <ShoppingCart className="w-4 h-4" />, path: '/purchases/orders' },
        { id: 'bills', labelKey: 'bills', icon: <Receipt className="w-4 h-4" />, path: '/purchases/bills' },
        { id: 'payment-made', labelKey: 'paymentMade', icon: <Receipt className="w-4 h-4" />, path: '/purchases/payment-made' },
        { id: 'debit-note', labelKey: 'debitNotes', icon: <Receipt className="w-4 h-4" />, path: '/purchases/debit-notes' }
      ]
    },
    {
      id: 'accounting',
      labelKey: 'accountingModel',
      icon: <Calculator className="w-5 h-5" />,
      children: [
        { id: 'chart-of-accounts', labelKey: 'chartOfAccounts', icon: <Calculator className="w-4 h-4" />, path: '/accounting/chart-of-accounts' },
        { id: 'journal-entries', labelKey: 'journalEntries', icon: <Receipt className="w-4 h-4" />, path: '/accounting/journal-entries' },
        { id: 'trial-balance', labelKey: 'trialBalance', icon: <Calculator className="w-4 h-4" />, path: '/accounting/trial-balance' },
        { id: 'profit-loss', labelKey: 'profitAndLoss', icon: <Calculator className="w-4 h-4" />, path: '/accounting/profit-loss' },
        { id: 'balance-sheet', labelKey: 'balanceSheet', icon: <Calculator className="w-4 h-4" />, path: '/accounting/balance-sheet' },
        { id: 'cash-flow', labelKey: 'cashFlow', icon: <Calculator className="w-4 h-4" />, path: '/accounting/cash-flow' }
      ]
    },
    {
      id: 'expenses',
      labelKey: 'expensesModel',
      icon: <Receipt className="w-5 h-5" />,
      children: [
        { id: 'expenses-list', labelKey: 'expensesList', icon: <Receipt className="w-4 h-4" />, path: '/expenses/list' },
        { id: 'expense-categories', labelKey: 'expenseCategories', icon: <Receipt className="w-4 h-4" />, path: '/expenses/categories' },
        { id: 'expense-reports', labelKey: 'expenseReports', icon: <Receipt className="w-4 h-4" />, path: '/expenses/reports' }
      ]
    }
  ]

  const renderMenuItem = (item: MenuItem, level = 0) => {
    const hasChildren = item.children && item.children.length > 0
    const isExpanded = expandedItems.includes(item.id)
    const isActive = item.path ? isActiveRoute(item.path) : isParentActive(item.children || [])

    if (hasChildren) {
      return (
        <div key={item.id} className="mb-1">
          <button
            onClick={() => toggleExpanded(item.id)}
            className={`w-full flex items-center justify-between px-4 py-3 text-left rounded-lg transition-colors ${
              isActive
                ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center">
              {item.icon}
              {sidebarOpen && <span className="ml-3 font-medium">{t[item.labelKey as keyof typeof t]}</span>}
            </div>
            {sidebarOpen && (
              isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />
            )}
          </button>
          {isExpanded && sidebarOpen && (
            <div className="ml-4 mt-1 space-y-1">
              {item.children?.map(child => renderMenuItem(child, level + 1))}
            </div>
          )}
        </div>
      )
    }

    return (
      <Link
        key={item.id}
        to={item.path || '#'}
        className={`flex items-center px-4 py-3 mb-1 rounded-lg transition-colors ${
          isActive
            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
            : 'text-gray-700 hover:bg-gray-100'
        } ${level > 0 ? 'text-sm' : ''}`}
      >
        {item.icon}
        {sidebarOpen && <span className="ml-3">{t[item.labelKey as keyof typeof t]}</span>}
      </Link>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-16'
        } bg-white shadow-lg transition-all duration-300 flex flex-col`}
      >
        {/* Logo and Toggle */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          {sidebarOpen && (
            <div className="flex items-center">
              <Home className="w-8 h-8 text-blue-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-800">TSH ERP</h1>
            </div>
          )}
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          {menuItems.map(item => renderMenuItem(item))}
        </nav>

        {/* User Profile & Settings */}
        <div className="border-t border-gray-200 p-4">
          {sidebarOpen && (
            <div className="mb-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-700">{user?.name || 'User'}</p>
                  <p className="text-xs text-gray-500">{user?.role || 'Admin'}</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="space-y-1">
            <Link 
              to="/settings/translations"
              className={`w-full flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors ${!sidebarOpen && 'justify-center'}`}
            >
              <Settings className="w-5 h-5" />
              {sidebarOpen && <span className="ml-3">{t.settings}</span>}
            </Link>
            <button className={`w-full flex items-center px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors ${!sidebarOpen && 'justify-center'}`}>
              <LogOut className="w-5 h-5" />
              {sidebarOpen && <span className="ml-3">{t.logout}</span>}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-gray-800">
                {location.pathname === '/dashboard' ? 'Dashboard' : 
                 location.pathname.split('/').pop()?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Page'}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Welcome back to TSH ERP System
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-700">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500">{new Date().toLocaleDateString()}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout
