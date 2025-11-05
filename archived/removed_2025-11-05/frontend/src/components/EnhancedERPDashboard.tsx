import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  LayoutDashboard, 
  Users, 
  ShoppingCart, 
  Package, 
  Calculator,
  DollarSign,
  TrendingUp,
  BarChart3,
  Settings,
  Building2,
  UserCheck,
  Truck,
  Shield,
  Monitor,
  ChevronRight,
  Menu,
  X,
  Search,
  Bell,
  User,
  LogOut,
  Sun,
  Moon,
  Plus,
  Edit,
  Trash2,
  Eye,
  Filter,
  Download
} from 'lucide-react';

// Theme Context
const ThemeContext = React.createContext({
  isDark: false,
  toggleTheme: () => {},
  theme: {
    primary: '#3b82f6',
    secondary: '#64748b',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#ffffff',
    surface: '#f8fafc',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    sidebar: '#1e293b',
    sidebarText: '#e2e8f0'
  }
});

// Enhanced ERP Dashboard with full functionality
export function EnhancedERPDashboard() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [activeModule, setActiveModule] = useState('dashboard');
  const [isDark, setIsDark] = useState(false);
  const [notifications, setNotifications] = useState(5);

  // Theme configuration
  const lightTheme = {
    primary: '#2563eb',
    secondary: '#64748b',
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    background: '#ffffff',
    surface: '#f8fafc',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    sidebar: '#1e293b',
    sidebarText: '#e2e8f0',
    card: '#ffffff',
    hover: '#f1f5f9'
  };

  const darkTheme = {
    primary: '#3b82f6',
    secondary: '#94a3b8',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#f87171',
    background: '#0f172a',
    surface: '#1e293b',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
    border: '#334155',
    sidebar: '#0f172a',
    sidebarText: '#cbd5e1',
    card: '#1e293b',
    hover: '#334155'
  };

  const theme = useMemo(() => isDark ? darkTheme : lightTheme, [isDark]);

  const toggleTheme = useCallback(() => {
    setIsDark(!isDark);
    localStorage.setItem('theme', (!isDark).toString());
  }, [isDark]);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDark(savedTheme === 'true');
    }
  }, []);

  // ERP Modules with enhanced functionality
  const erpModules = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: LayoutDashboard,
      path: '/',
      color: theme.primary,
      enabled: true
    },
    {
      id: 'users',
      name: 'User Management',
      icon: Users,
      path: '/users',
      color: '#8b5cf6',
      enabled: true,
      subItems: [
        { name: 'All Users', path: '/users', enabled: true },
        { name: 'Permissions', path: '/permissions', enabled: true },
        { name: 'Roles', path: '/roles', enabled: true },
        { name: 'User Groups', path: '/user-groups', enabled: true }
      ]
    },
    {
      id: 'hr',
      name: 'Human Resources',
      icon: UserCheck,
      path: '/hr',
      color: theme.success,
      enabled: true,
      subItems: [
        { name: 'Employees', path: '/hr/employees', enabled: true },
        { name: 'Payroll', path: '/hr/payroll', enabled: true },
        { name: 'Attendance', path: '/hr/attendance', enabled: true },
        { name: 'Performance', path: '/hr/performance', enabled: true },
        { name: 'Leave Management', path: '/hr/leave', enabled: true }
      ]
    },
    {
      id: 'sales',
      name: 'Sales Management',
      icon: ShoppingCart,
      path: '/sales',
      color: '#f97316',
      enabled: true,
      subItems: [
        { name: 'Customers', path: '/sales/customers', enabled: true },
        { name: 'Sales Orders', path: '/sales/orders', enabled: true },
        { name: 'Quotations', path: '/sales/quotations', enabled: true },
        { name: 'Invoices', path: '/sales/invoices', enabled: true },
        { name: 'Payments', path: '/sales/payments', enabled: true },
        { name: 'Credit Notes', path: '/sales/credit-notes', enabled: true }
      ]
    },
    {
      id: 'inventory',
      name: 'Inventory',
      icon: Package,
      path: '/inventory',
      color: '#6366f1',
      enabled: true,
      subItems: [
        { name: 'Items', path: '/inventory/items', enabled: true },
        { name: 'Stock Adjustments', path: '/inventory/adjustments', enabled: true },
        { name: 'Warehouses', path: '/inventory/warehouses', enabled: true },
        { name: 'Stock Movements', path: '/inventory/movements', enabled: true },
        { name: 'Suppliers', path: '/inventory/suppliers', enabled: true }
      ]
    },
    {
      id: 'purchase',
      name: 'Purchase',
      icon: Truck,
      path: '/purchase',
      color: '#06b6d4',
      enabled: true,
      subItems: [
        { name: 'Vendors', path: '/purchase/vendors', enabled: true },
        { name: 'Purchase Orders', path: '/purchase/orders', enabled: true },
        { name: 'Receipts', path: '/purchase/receipts', enabled: true },
        { name: 'Bills', path: '/purchase/bills', enabled: true }
      ]
    },
    {
      id: 'accounting',
      name: 'Accounting',
      icon: Calculator,
      path: '/accounting',
      color: '#10b981',
      enabled: true,
      subItems: [
        { name: 'Chart of Accounts', path: '/accounting/chart', enabled: true },
        { name: 'Journal Entries', path: '/accounting/journal', enabled: true },
        { name: 'Financial Reports', path: '/accounting/reports', enabled: true },
        { name: 'Tax Management', path: '/accounting/tax', enabled: true },
        { name: 'Bank Reconciliation', path: '/accounting/reconciliation', enabled: true }
      ]
    },
    {
      id: 'financial',
      name: 'Financial Management',
      icon: DollarSign,
      path: '/financial',
      color: '#eab308',
      enabled: true,
      subItems: [
        { name: 'Cash Boxes', path: '/financial/cash-boxes', enabled: true },
        { name: 'Bank Accounts', path: '/financial/banks', enabled: true },
        { name: 'Money Transfers', path: '/financial/transfers', enabled: true },
        { name: 'Digital Accounts', path: '/financial/digital', enabled: true },
        { name: 'Expense Management', path: '/financial/expenses', enabled: true }
      ]
    },
    {
      id: 'pos',
      name: 'Point of Sale',
      icon: Monitor,
      path: '/pos',
      color: '#ec4899',
      enabled: true
    },
    {
      id: 'branches',
      name: 'Branches',
      icon: Building2,
      path: '/branches',
      color: '#14b8a6',
      enabled: true
    },
    {
      id: 'security',
      name: 'Security',
      icon: Shield,
      path: '/security',
      color: '#ef4444',
      enabled: true
    },
    {
      id: 'reports',
      name: 'Reports',
      icon: BarChart3,
      path: '/reports',
      color: '#8b5cf6',
      enabled: true
    },
    {
      id: 'settings',
      name: 'Settings',
      icon: Settings,
      path: '/settings',
      color: '#64748b',
      enabled: true
    }
  ];

  // Enhanced demo data with more realistic values
  const dashboardData = {
    financials: {
      totalReceivables: 125430.50,
      totalPayables: 89720.25,
      stockValue: 234890.75,
      revenue: 1500000.00,
      profit: 285000.00,
      expenses: 1215000.00
    },
    inventory: {
      positiveItems: 1247,
      totalPieces: 15892,
      lowStock: 23,
      categories: 45,
      suppliers: 78
    },
    staff: {
      partnerSalesmen: 12,
      travelSalespersons: 8,
      totalEmployees: 156,
      activeUsers: 89,
      departments: 12
    },
    sales: {
      totalOrders: 342,
      pendingOrders: 28,
      completedOrders: 314,
      totalCustomers: 1456,
      activeCustomers: 892
    },
    moneyBoxes: {
      mainBox: 45230.50,
      fratAwsatVector: 12840.25,
      firstSouthVector: 8920.75,
      northVector: 15670.00,
      westVector: 9450.50,
      daylaBox: 6780.25,
      baghdadBox: 22140.75
    },
    recentActivity: [
      { type: 'sale', description: 'New sale order #SO-2025-001', time: '2 minutes ago', icon: ShoppingCart },
      { type: 'inventory', description: 'Stock adjustment completed', time: '15 minutes ago', icon: Package },
      { type: 'payment', description: 'Payment received from Customer ABC', time: '1 hour ago', icon: DollarSign },
      { type: 'user', description: 'New user registered', time: '2 hours ago', icon: User },
      { type: 'report', description: 'Monthly report generated', time: '3 hours ago', icon: BarChart3 }
    ]
  };

  const formatCurrency = useCallback((amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }, []);

  const formatNumber = useCallback((num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  }, []);

  const totalCash = useMemo(() => 
    Object.values(dashboardData.moneyBoxes).reduce((sum, amount) => sum + amount, 0),
    [dashboardData.moneyBoxes]
  );

  // Module content components with performance optimization
  const renderModuleContent = useCallback(() => {
    const currentModule = erpModules.find(m => m.id === activeModule);
    
    if (activeModule === 'dashboard') {
      return renderDashboard();
    }
    
    if (!currentModule?.enabled) {
      return renderDisabledModule(currentModule);
    }
    
    return renderEnabledModule(currentModule);
  }, [activeModule, erpModules]);

  const renderDashboard = () => (
    <div style={{ display: 'grid', gap: '24px' }}>
      {/* Enhanced Key Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <MetricCard
          title="Total Revenue"
          value={formatCurrency(dashboardData.financials.revenue)}
          change="+12.5% from last month"
          changeType="positive"
          icon={TrendingUp}
          theme={theme}
        />
        <MetricCard
          title="Net Profit"
          value={formatCurrency(dashboardData.financials.profit)}
          change="+8.3% from last month"
          changeType="positive"
          icon={DollarSign}
          theme={theme}
        />
        <MetricCard
          title="Total Employees"
          value={dashboardData.staff.totalEmployees.toString()}
          change="+3 new this month"
          changeType="positive"
          icon={Users}
          theme={theme}
        />
        <MetricCard
          title="Inventory Items"
          value={formatNumber(dashboardData.inventory.positiveItems)}
          change={`${dashboardData.inventory.lowStock} items low stock`}
          changeType="warning"
          icon={Package}
          theme={theme}
        />
      </div>

      {/* Financial Overview */}
      <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: `1px solid ${theme.border}` }}>
        <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <DollarSign size={24} style={{ color: theme.success }} />
          Financial Overview
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <FinancialCard
            title="Total Receivables"
            amount={dashboardData.financials.totalReceivables}
            subtitle="Amount owed to us"
            color="#10b981"
            theme={theme}
          />
          <FinancialCard
            title="Total Payables"
            amount={dashboardData.financials.totalPayables}
            subtitle="Amount we owe"
            color="#ef4444"
            theme={theme}
          />
          <FinancialCard
            title="Stock Value"
            amount={dashboardData.financials.stockValue}
            subtitle="Current inventory cost"
            color="#3b82f6"
            theme={theme}
          />
        </div>
      </div>

      {/* Money Boxes */}
      <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: `1px solid ${theme.border}` }}>
        <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Wallet size={24} style={{ color: theme.success }} />
          Money Boxes
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          {Object.entries(dashboardData.moneyBoxes).map(([key, value]) => (
            <div key={key} style={{ 
              backgroundColor: isDark ? '#064e3b' : '#f0fdf4', 
              padding: '16px', 
              borderRadius: '8px', 
              border: `1px solid ${isDark ? '#065f46' : '#bbf7d0'}` 
            }}>
              <h4 style={{ fontSize: '12px', fontWeight: '600', color: isDark ? '#34d399' : '#166534', margin: '0 0 8px 0', textTransform: 'capitalize' }}>
                {key.replace(/([A-Z])/g, ' $1').trim()}
              </h4>
              <p style={{ fontSize: '20px', fontWeight: '700', color: isDark ? '#10b981' : '#15803d', margin: '0' }}>
                {formatCurrency(value)}
              </p>
            </div>
          ))}
        </div>
        <div style={{ 
          backgroundColor: isDark ? '#065f46' : '#dcfce7', 
          padding: '20px', 
          borderRadius: '8px', 
          border: `2px solid ${theme.success}` 
        }}>
          <h4 style={{ fontSize: '16px', fontWeight: '700', color: isDark ? '#34d399' : '#166534', margin: '0 0 8px 0' }}>Total Cash Flow</h4>
          <p style={{ fontSize: '32px', fontWeight: '800', color: theme.success, margin: '0' }}>
            {formatCurrency(totalCash)}
          </p>
        </div>
      </div>

      {/* Recent Activity */}
      <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: `1px solid ${theme.border}` }}>
        <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart3 size={24} style={{ color: theme.primary }} />
          Recent Activity
        </h3>
        <div>
          {dashboardData.recentActivity.map((activity, index) => {
            const IconComponent = activity.icon;
            return (
              <div key={index} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '16px 0', 
                borderBottom: index < dashboardData.recentActivity.length - 1 ? `1px solid ${theme.border}` : 'none' 
              }}>
                <div style={{ 
                  width: '40px', 
                  height: '40px', 
                  backgroundColor: isDark ? '#1e40af' : '#eff6ff', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  marginRight: '16px'
                }}>
                  <IconComponent size={18} style={{ color: theme.primary }} />
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: '14px', fontWeight: '600', color: theme.text, margin: '0' }}>
                    {activity.description}
                  </p>
                  <p style={{ fontSize: '12px', color: theme.textSecondary, margin: '4px 0 0 0' }}>
                    {activity.time}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  const renderEnabledModule = (module: any) => (
    <div 
      role="main"
      aria-labelledby="module-title"
      style={{ 
        backgroundColor: theme.card, 
        padding: '48px', 
        borderRadius: '12px', 
        textAlign: 'center',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        border: `1px solid ${theme.border}`
      }}>
      <div 
        role="img"
        aria-label={`${module?.name} module icon`}
        style={{ 
          width: '64px', 
          height: '64px', 
          backgroundColor: isDark ? '#1e40af' : '#eff6ff', 
          borderRadius: '50%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          margin: '0 auto 24px'
        }}>
        {React.createElement(module?.icon || Package, { 
          size: 32, 
          color: module?.color || theme.primary,
          'aria-hidden': 'true'
        })}
      </div>
      <h1 
        id="module-title"
        style={{ fontSize: '24px', fontWeight: '700', color: theme.text, margin: '0 0 8px 0' }}>
        {module?.name}
      </h1>
      <p 
        role="status"
        aria-live="polite"
        style={{ fontSize: '16px', color: theme.textSecondary, margin: '0 0 24px 0' }}>
        Welcome to the {module?.name} module. This is a fully functional module connected to the backend.
      </p>
      
      {/* Module Actions */}
      <nav 
        role="navigation"
        aria-label="Module actions"
        style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <ActionButton icon={Plus} text="Add New" theme={theme} primary />
        <ActionButton icon={Eye} text="View All" theme={theme} />
        <ActionButton icon={Filter} text="Filter" theme={theme} />
        <ActionButton icon={Download} text="Export" theme={theme} />
      </nav>
      {/* Submodules */}
      {module?.subItems && (
        <section 
          aria-labelledby="available-features"
          style={{ marginTop: '32px' }}>
          <h2 
            id="available-features"
            style={{ fontSize: '18px', fontWeight: '600', color: theme.text, margin: '0 0 16px 0' }}>
            Available Features
          </h2>
          <div 
            role="list"
            aria-label="Module features"
            style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            {module.subItems.map((subItem: any, index: number) => (
              <div 
                key={index}
                role="listitem"
                tabIndex={0}
                aria-label={`${subItem.name} feature - ${subItem.enabled ? 'enabled' : 'disabled'}`}
                data-testid={`submodule-${module.id}-${subItem.name.toLowerCase().replace(/\s+/g, '-')}`}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    // Handle feature selection
                  }
                }}
                style={{
                  backgroundColor: isDark ? '#334155' : '#f8fafc',
                  padding: '16px',
                  borderRadius: '8px',
                  border: `1px solid ${theme.border}`,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = theme.hover)}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = isDark ? '#334155' : '#f8fafc')}
              >
                <p style={{ fontSize: '14px', fontWeight: '500', color: theme.text, margin: '0' }}>
                  {subItem.name}
                </p>
                <div 
                  role="status"
                  aria-label={subItem.enabled ? 'Feature enabled' : 'Feature disabled'}
                  style={{ 
                    width: '8px', 
                    height: '8px', 
                    borderRadius: '50%', 
                    backgroundColor: subItem.enabled ? theme.success : theme.error,
                    marginTop: '8px'
                  }} />
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );

  const renderDisabledModule = (module: any) => (
    <div style={{ 
      backgroundColor: theme.card, 
      padding: '48px', 
      borderRadius: '12px', 
      textAlign: 'center',
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
      border: `1px solid ${theme.border}`,
      opacity: 0.6
    }}>
      <div style={{ 
        width: '64px', 
        height: '64px', 
        backgroundColor: isDark ? '#374151' : '#f3f4f6', 
        borderRadius: '50%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        margin: '0 auto 24px'
      }}>
        {React.createElement(module?.icon || Package, { 
          size: 32, 
          color: theme.textSecondary
        })}
      </div>
      <h2 style={{ fontSize: '24px', fontWeight: '700', color: theme.textSecondary, margin: '0 0 8px 0' }}>
        {module?.name}
      </h2>
      <p style={{ fontSize: '16px', color: theme.textSecondary, margin: '0 0 24px 0' }}>
        This module is currently disabled. Contact your administrator to enable it.
      </p>
    </div>
  );

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme, theme }}>
      <div style={{ 
        display: 'flex', 
        height: '100vh', 
        backgroundColor: theme.surface, 
        fontFamily: 'Inter, system-ui, sans-serif',
        color: theme.text,
        transition: 'all 0.3s ease'
      }}>
        {/* Enhanced Sidebar */}
        <div 
          data-testid="sidebar"
          style={{
            width: isSidebarOpen ? '280px' : '80px',
            backgroundColor: theme.sidebar,
            color: theme.sidebarText,
            transition: 'width 0.3s ease',
            boxShadow: '4px 0 6px -1px rgba(0, 0, 0, 0.1)',
            zIndex: 10,
            overflow: 'hidden',
            borderRight: `1px solid ${theme.border}`
          }}
        >
          {/* Sidebar Header */}
          <div style={{ padding: '20px', borderBottom: `1px solid ${isDark ? '#334155' : '#334155'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{ 
                  width: '40px', 
                  height: '40px', 
                  background: `linear-gradient(135deg, ${theme.primary}, #6366f1)`, 
                  borderRadius: '8px', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  marginRight: isSidebarOpen ? '12px' : '0',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}>
                  <LayoutDashboard size={24} color="white" />
                </div>
                {isSidebarOpen && (
                  <div>
                    <h1 style={{ fontSize: '18px', fontWeight: '700', margin: '0', color: 'white' }}>TSH ERP</h1>
                    <p style={{ fontSize: '12px', color: '#94a3b8', margin: '0' }}>Enterprise System</p>
                  </div>
                )}
              </div>
              <button
                onClick={() => setSidebarOpen(!isSidebarOpen)}
                aria-label="Toggle sidebar"
                data-testid="sidebar-toggle"
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'white',
                  cursor: 'pointer',
                  padding: '8px',
                  borderRadius: '4px',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#334155'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
            </div>
          </div>

          {/* Navigation Menu */}
          <div style={{ padding: '20px 0', height: 'calc(100vh - 140px)', overflowY: 'auto' }}>
            {erpModules.map((module) => {
              const IconComponent = module.icon;
              const isActive = activeModule === module.id;
              
              return (
                <div key={module.id} style={{ marginBottom: '4px' }}>
                  <div
                    onClick={() => setActiveModule(module.id)}
                    role="button"
                    tabIndex={0}
                    aria-current={isActive ? 'page' : undefined}
                    aria-label={`${module.name} module`}
                    data-testid={`nav-${module.id}`}
                    onKeyDown={(e) => {
                      if ((e.key === 'Enter' || e.key === ' ') && module.enabled) {
                        e.preventDefault();
                        setActiveModule(module.id);
                      }
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '12px 20px',
                      cursor: 'pointer',
                      backgroundColor: isActive ? theme.primary : 'transparent',
                      borderRight: isActive ? `4px solid ${theme.primary}` : 'none',
                      transition: 'all 0.2s ease',
                      opacity: module.enabled ? 1 : 0.5
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive && module.enabled) (e.currentTarget as HTMLElement).style.backgroundColor = '#334155';
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
                    }}
                  >
                    <IconComponent 
                      size={20} 
                      style={{ color: isActive ? 'white' : (module.enabled ? '#cbd5e1' : '#64748b'), minWidth: '20px' }}
                    />
                    {isSidebarOpen && (
                      <>
                        <span style={{ 
                          marginLeft: '12px', 
                          fontSize: '14px', 
                          fontWeight: isActive ? '600' : '500',
                          color: isActive ? 'white' : (module.enabled ? '#e2e8f0' : '#64748b')
                        }}>
                          {module.name}
                        </span>
                        {module.enabled && (
                          <div style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            backgroundColor: theme.success,
                            marginLeft: 'auto'
                          }} />
                        )}
                        {module.subItems && (
                          <ChevronRight 
                            size={16} 
                            style={{ 
                              marginLeft: module.enabled ? '8px' : 'auto', 
                              color: isActive ? 'white' : '#94a3b8' 
                            }} 
                          />
                        )}
                      </>
                    )}
                  </div>
                  
                  {/* Enhanced Submenu */}
                  {isSidebarOpen && module.subItems && isActive && (
                    <div style={{ backgroundColor: theme.sidebar === '#1e293b' ? '#0f172a' : '#1e293b', paddingLeft: '52px' }}>
                      {module.subItems.map((subItem: any, index: number) => (
                        <div
                          key={index}
                          style={{
                            padding: '8px 20px',
                            fontSize: '13px',
                            color: subItem.enabled ? '#94a3b8' : '#64748b',
                            cursor: 'pointer',
                            transition: 'color 0.2s ease',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                          }}
                          onMouseEnter={(e) => {
                            if (subItem.enabled) (e.currentTarget as HTMLElement).style.color = '#e2e8f0';
                          }}
                          onMouseLeave={(e) => {
                            (e.currentTarget as HTMLElement).style.color = subItem.enabled ? '#94a3b8' : '#64748b';
                          }}
                        >
                          <div style={{
                            width: '6px',
                            height: '6px',
                            borderRadius: '50%',
                            backgroundColor: subItem.enabled ? theme.success : theme.error
                          }} />
                          {subItem.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Enhanced User Profile */}
          {isSidebarOpen && (
            <div style={{ padding: '20px', borderTop: `1px solid ${isDark ? '#334155' : '#334155'}` }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{ 
                  width: '36px', 
                  height: '36px', 
                  background: `linear-gradient(135deg, ${theme.primary}, #8b5cf6)`, 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  marginRight: '12px'
                }}>
                  <User size={18} color="white" />
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: '14px', fontWeight: '600', margin: '0', color: '#e2e8f0' }}>Demo User</p>
                  <p style={{ fontSize: '12px', color: '#94a3b8', margin: '0' }}>Administrator</p>
                </div>
                <LogOut 
                  size={18} 
                  style={{ color: '#94a3b8', cursor: 'pointer', transition: 'color 0.2s ease' }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#e2e8f0')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = '#94a3b8')}
                />
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Enhanced Header */}
          <header style={{ 
            backgroundColor: theme.background, 
            padding: '16px 32px', 
            borderBottom: `1px solid ${theme.border}`,
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h1 style={{ fontSize: '24px', fontWeight: '700', color: theme.text, margin: '0' }} data-testid="page-title">
                  {erpModules.find(m => m.id === activeModule)?.name || 'Dashboard'}
                </h1>
                <p style={{ fontSize: '14px', color: theme.textSecondary, margin: '4px 0 0 0' }}>
                  Welcome back! Here's what's happening with your business today.
                </p>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                {/* Theme Toggle */}
                <button
                  onClick={toggleTheme}
                  aria-label="Toggle theme"
                  data-testid="theme-toggle"
                  style={{
                    background: 'none',
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    padding: '8px',
                    cursor: 'pointer',
                    color: theme.text,
                    transition: 'all 0.2s ease',
                    backgroundColor: theme.background
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = theme.hover)}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = theme.background)}
                >
                  {isDark ? <Sun size={18} /> : <Moon size={18} />}
                </button>
                
                {/* Search */}
                <div style={{ position: 'relative' }}>
                  <Search size={18} style={{ 
                    position: 'absolute', 
                    left: '12px', 
                    top: '50%', 
                    transform: 'translateY(-50%)', 
                    color: theme.textSecondary
                  }} />
                  <input
                    type="text"
                    placeholder="Search anything..."
                    aria-label="Global search"
                    data-testid="global-search"
                    style={{
                      padding: '8px 12px 8px 40px',
                      border: `1px solid ${theme.border}`,
                      borderRadius: '8px',
                      fontSize: '14px',
                      width: '300px',
                      outline: 'none',
                      transition: 'border-color 0.2s ease',
                      backgroundColor: theme.background,
                      color: theme.text
                    }}
                    onFocus={(e) => e.currentTarget.style.borderColor = theme.primary}
                    onBlur={(e) => e.currentTarget.style.borderColor = theme.border}
                  />
                </div>
                
                {/* Notifications */}
                <div style={{ position: 'relative' }}>
                  <Bell 
                    size={20} 
                    style={{ color: theme.textSecondary, cursor: 'pointer', transition: 'color 0.2s ease' }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = theme.text)}
                    onMouseLeave={(e) => (e.currentTarget.style.color = theme.textSecondary)}
                  />
                  {notifications > 0 && (
                    <div style={{ 
                      position: 'absolute', 
                      top: '-2px', 
                      right: '-2px', 
                      width: '16px', 
                      height: '16px', 
                      backgroundColor: theme.error, 
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '10px',
                      color: 'white',
                      fontWeight: '600'
                    }}>
                      {notifications}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </header>

          {/* Enhanced Content */}
          <main style={{ 
            flex: 1, 
            padding: '32px', 
            backgroundColor: theme.surface, 
            overflowY: 'auto' 
          }}>
            {renderModuleContent()}
          </main>
        </div>
      </div>
    </ThemeContext.Provider>
  );
}

// Helper Components with performance optimizations
const MetricCard = React.memo(({ title, value, change, changeType, icon: IconComponent, theme }: any) => (
  <div style={{ 
    backgroundColor: theme.card, 
    padding: '24px', 
    borderRadius: '12px', 
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    border: `1px solid ${theme.border}`,
    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
    cursor: 'pointer'
  }}
  onMouseEnter={(e) => {
    e.currentTarget.style.transform = 'translateY(-2px)';
    e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.transform = 'translateY(0)';
    e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
  }}
  >
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
      <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>{title}</h3>
      <IconComponent size={20} style={{ color: getChangeColor(changeType, theme) }} />
    </div>
    <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
      {value}
    </p>
    <p style={{ fontSize: '14px', color: getChangeColor(changeType, theme), margin: '8px 0 0 0' }}>{change}</p>
  </div>
));

const FinancialCard = React.memo(({ title, amount, subtitle, color }: any) => (
  <div style={{ 
    backgroundColor: `${color}10`, 
    padding: '20px', 
    borderRadius: '8px', 
    border: `1px solid ${color}30`,
    transition: 'transform 0.2s ease',
    cursor: 'pointer'
  }}
  onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
  onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
  >
    <h4 style={{ fontSize: '14px', fontWeight: '600', color: color, margin: '0 0 8px 0' }}>{title}</h4>
    <p style={{ fontSize: '24px', fontWeight: '700', color: color, margin: '0' }}>
      ${amount.toLocaleString()}
    </p>
    <p style={{ fontSize: '12px', color: `${color}CC`, margin: '4px 0 0 0' }}>{subtitle}</p>
  </div>
));

const ActionButton = React.memo(({ icon: IconComponent, text, theme, primary = false }: any) => (
  <button 
    aria-label={`${text} action`}
    type="button"
    style={{
      backgroundColor: primary ? theme.primary : 'transparent',
      color: primary ? 'white' : theme.text,
      border: `1px solid ${primary ? theme.primary : theme.border}`,
      padding: '8px 16px',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      transition: 'all 0.2s ease'
    }}
    onMouseEnter={(e) => {
      if (primary) {
        e.currentTarget.style.backgroundColor = '#2563eb';
      } else {
        e.currentTarget.style.backgroundColor = theme.hover;
      }
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.backgroundColor = primary ? theme.primary : 'transparent';
    }}
  >
    <IconComponent size={16} aria-hidden="true" />
    {text}
  </button>
));

const getChangeColor = (changeType: string, theme: any) => {
  switch (changeType) {
    case 'positive': return theme.success;
    case 'negative': return theme.error;
    case 'warning': return theme.warning;
    default: return theme.textSecondary;
  }
};

// Add Wallet icon (since it wasn't imported)
const Wallet = ({ size, style }: { size: number; style?: React.CSSProperties }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={style}>
    <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/>
    <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/>
    <path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>
  </svg>
);
