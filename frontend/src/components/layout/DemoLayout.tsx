import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
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

interface LayoutProps {
  children: React.ReactNode
}

interface MenuItem {
  id: string
  label: string
  icon: React.ReactNode
  path?: string
  children?: MenuItem[]
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <LayoutDashboard className="w-5 h-5" />,
    path: '/dashboard'
  },
  {
    id: 'hr',
    label: 'HR Model',
    icon: <Users className="w-5 h-5" />,
    children: [
      { id: 'employees', label: 'All Employees', icon: <Users className="w-4 h-4" />, path: '/hr/employees' },
      { id: 'travel-salesperson', label: 'Travel Salesperson', icon: <Users className="w-4 h-4" />, path: '/hr/travel-salesperson' },
      { id: 'partner-salesman', label: 'Partner Salesman', icon: <Users className="w-4 h-4" />, path: '/hr/partner-salesman' },
      { id: 'retailerman', label: 'Retailerman', icon: <Users className="w-4 h-4" />, path: '/hr/retailerman' }
    ]
  },
  {
    id: 'sales',
    label: 'Sales Model',
    icon: <ShoppingCart className="w-5 h-5" />,
    children: [
      { id: 'customers', label: 'All Customers', icon: <Users className="w-4 h-4" />, path: '/sales/customers' },
      { id: 'clients', label: 'Clients', icon: <Users className="w-4 h-4" />, path: '/sales/clients' },
      { id: 'consumers', label: 'Consumers', icon: <Users className="w-4 h-4" />, path: '/sales/consumers' },
      { id: 'quotations', label: 'Quotations', icon: <Receipt className="w-4 h-4" />, path: '/sales/quotations' },
      { id: 'sale-orders', label: 'Sale Orders', icon: <ShoppingCart className="w-4 h-4" />, path: '/sales/orders' },
      { id: 'invoices', label: 'Invoices', icon: <Receipt className="w-4 h-4" />, path: '/sales/invoices' },
      { id: 'payment-received', label: 'Payment Received', icon: <Receipt className="w-4 h-4" />, path: '/sales/payment-received' },
      { id: 'credit-note', label: 'Credit Note', icon: <Receipt className="w-4 h-4" />, path: '/sales/credit-note' },
      { id: 'refund', label: 'Refund', icon: <Receipt className="w-4 h-4" />, path: '/sales/refund' }
    ]
  },
  {
    id: 'purchases',
    label: 'Purchases Model',
    icon: <Package className="w-5 h-5" />,
    children: [
      { id: 'vendors', label: 'Vendors', icon: <Users className="w-4 h-4" />, path: '/purchases/vendors' },
      { id: 'purchase-orders', label: 'Purchase Orders', icon: <Package className="w-4 h-4" />, path: '/purchases/orders' },
      { id: 'bills', label: 'Bills', icon: <Receipt className="w-4 h-4" />, path: '/purchases/bills' },
      { id: 'payment-made', label: 'Payment Made', icon: <Receipt className="w-4 h-4" />, path: '/purchases/payment-made' },
      { id: 'debit-note', label: 'Debit Note', icon: <Receipt className="w-4 h-4" />, path: '/purchases/debit-note' }
    ]
  },
  {
    id: 'accounting',
    label: 'Accounting Model',
    icon: <Calculator className="w-5 h-5" />,
    children: [
      { id: 'chart-of-accounts', label: 'Chart of Accounts', icon: <Calculator className="w-4 h-4" />, path: '/accounting/chart-of-accounts' },
      { id: 'journal-entries', label: 'Journal Entries', icon: <Receipt className="w-4 h-4" />, path: '/accounting/journal-entries' },
      { id: 'trial-balance', label: 'Trial Balance', icon: <Calculator className="w-4 h-4" />, path: '/accounting/trial-balance' },
      { id: 'profit-loss', label: 'Profit & Loss', icon: <Calculator className="w-4 h-4" />, path: '/accounting/profit-loss' },
      { id: 'balance-sheet', label: 'Balance Sheet', icon: <Calculator className="w-4 h-4" />, path: '/accounting/balance-sheet' },
      { id: 'cash-flow', label: 'Cash Flow', icon: <Calculator className="w-4 h-4" />, path: '/accounting/cash-flow' }
    ]
  },
  {
    id: 'expenses',
    label: 'Expenses Model',
    icon: <Receipt className="w-5 h-5" />,
    children: [
      { id: 'expenses-list', label: 'Expenses', icon: <Receipt className="w-4 h-4" />, path: '/expenses/list' },
      { id: 'expense-categories', label: 'Categories', icon: <Receipt className="w-4 h-4" />, path: '/expenses/categories' },
      { id: 'expense-reports', label: 'Reports', icon: <Receipt className="w-4 h-4" />, path: '/expenses/reports' }
    ]
  }
]

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [expandedItems, setExpandedItems] = useState<string[]>(['dashboard'])
  const location = useLocation()
  
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
              {sidebarOpen && <span className="ml-3 font-medium">{item.label}</span>}
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
        {sidebarOpen && <span className="ml-3">{item.label}</span>}
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
            <button className={`w-full flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors ${!sidebarOpen && 'justify-center'}`}>
              <Settings className="w-5 h-5" />
              {sidebarOpen && <span className="ml-3">Settings</span>}
            </button>
            <button
              className={`w-full flex items-center px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors ${!sidebarOpen && 'justify-center'}`}
            >
              <LogOut className="w-5 h-5" />
              {sidebarOpen && <span className="ml-3">Logout</span>}
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
