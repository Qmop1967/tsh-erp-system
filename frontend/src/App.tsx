import { Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import NewLayout from './components/layout/NewLayout'
import { useDashboardData } from './hooks/useDashboardData'
import { useLanguageStore } from './stores/languageStore'
import { useDynamicTranslations } from './lib/dynamicTranslations'
import { useAuthStore } from './stores/authStore'

// Import auth pages
import { LoginPage } from './pages/auth/LoginPage'
// import { SimpleTest } from './components/SimpleTest'
// import { InventorySidebar } from './components/inventory/InventorySidebar'
// import InventoryButton from './components/inventory/InventoryButton'
// import { NavigationTest } from './components/NavigationTest'

// Import branches page
import { BranchesPage } from './pages/branches/BranchesPage'

// Import warehouse, vendor, purchase and security pages
import { WarehousesPage } from './pages/warehouses/WarehousesPage'
import { VendorsPage } from './pages/vendors/VendorsPage'
import { PurchaseOrdersPage } from './pages/purchase/PurchaseOrdersPage'
import { SecurityManagementPage } from './pages/security/SecurityManagementPage'

// Import accounting pages
import ChartOfAccountsPage from './pages/accounting/ChartOfAccountsPage'
import JournalEntriesPage from './pages/accounting/JournalEntriesPage'
import FinancialReportsPage from './pages/accounting/FinancialReportsPage'

// Import sales pages
import { CustomersPage } from './pages/customers/CustomersPage'
import { SalesOrdersPage } from './pages/sales/SalesOrdersPage'
import InvoicesPage from './pages/sales/InvoicesPage'
import QuotationsPage from './pages/sales/QuotationsPage'
import PaymentReceivedPage from './pages/sales/PaymentReceivedPage'
import CreditNotePage from './pages/sales/CreditNotePage'
import RefundPage from './pages/sales/RefundPage'

// Import HR pages
import { EmployeesPage } from './pages/hr/EmployeesPage'
import { UsersPage } from './pages/users/UsersPage'
import { PermissionsPage } from './pages/permissions/PermissionsPage'

// Import Inventory pages
import ItemsPage from './pages/inventory/ItemsPage'
import InventoryAdjustmentPage from './pages/inventory/InventoryAdjustmentPage'

// Import Settings pages
import DynamicTranslationManagementPage from './pages/settings/DynamicTranslationManagementPage'
import SettingsPageMinimal from './pages/settings/SettingsPageMinimal'

// Import Money Transfer pages
import MoneyTransferDashboard from './pages/money-transfer/MoneyTransferDashboard'

// Import Financial Management pages
import FinancialDashboard from './pages/financial/FinancialDashboard'
import CashBoxesPage from './pages/financial/CashBoxesPage'
import BankAccountsPage from './pages/financial/BankAccountsPage'
import DigitalAccountsPage from './pages/financial/DigitalAccountsPage'
import TransferTrackingPage from './pages/financial/TransferTrackingPage'
import SalespersonBoxesPage from './pages/financial/SalespersonBoxesPage'

// Import POS pages
import POSInterface from './pages/pos/POSInterface'

// Import Admin Dashboard
import { AdminDashboard } from './pages/dashboard/AdminDashboard'

// Simple test components
function TestDashboard() {
  const { data, loading, error, refetch } = useDashboardData()
  const { language } = useLanguageStore()
  const { t } = useDynamicTranslations(language)

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num)
  }

  const totalCash = Object.values(data.moneyBoxes).reduce((sum, amount) => sum + amount, 0)

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">{t.loadingDashboardData}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">🏠 {t.tshErpDashboard}</h1>
        <div className="flex items-center gap-4">
          {error && (
            <div className="text-sm text-orange-600 bg-orange-50 px-3 py-1 rounded">
              ⚠️ {t.someDataOutdated}
            </div>
          )}
          <button 
            onClick={refetch}
            className="text-sm text-blue-600 hover:text-blue-800 bg-blue-50 px-3 py-1 rounded transition-colors"
          >
            🔄 {t.refresh}
          </button>
          <div className="text-sm text-gray-500">
            {t.lastUpdated}: {new Date().toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-2">💰 {t.totalRevenue}</h3>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(data.totalRevenue)}</p>
          <p className="text-sm text-gray-500 mt-1">
            {data.totalTransactions} {t.transactions}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-2">👥 {t.activeCustomers}</h3>
          <p className="text-2xl font-bold text-blue-600">{formatNumber(data.activeCustomers)}</p>
          <p className="text-sm text-gray-500 mt-1">{t.thisMonth}</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-2">📦 {t.inventoryValue}</h3>
          <p className="text-2xl font-bold text-purple-600">{formatCurrency(data.inventoryValue)}</p>
          <p className="text-sm text-gray-500 mt-1">{data.totalProducts} {t.products}</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 mb-2">📊 {t.pendingOrders}</h3>
          <p className="text-2xl font-bold text-orange-600">{formatNumber(data.pendingOrders)}</p>
          <p className="text-sm text-gray-500 mt-1">{t.awaitingProcessing}</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">⚡ Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-lg transition-colors">
            📊 View Reports
          </button>
          <button className="bg-green-500 hover:bg-green-600 text-white p-3 rounded-lg transition-colors">
            💰 Add Transaction
          </button>
          <button className="bg-purple-500 hover:bg-purple-600 text-white p-3 rounded-lg transition-colors">
            📦 Check Inventory
          </button>
          <button className="bg-orange-500 hover:bg-orange-600 text-white p-3 rounded-lg transition-colors">
            👥 Manage Staff
          </button>
        </div>
      </div>
    </div>
  )
}

function TestHR() {
  return (
    <Routes>
      <Route path="users" element={<UsersPage />} />
      <Route path="employees" element={<EmployeesPage />} />
      <Route path="payroll" element={<EmployeesPage />} />
      <Route path="attendance" element={<EmployeesPage />} />
      <Route path="performance" element={<EmployeesPage />} />
      <Route path="achievements" element={<EmployeesPage />} />
      <Route path="challenges" element={<EmployeesPage />} />
      <Route path="*" element={<UsersPage />} />
    </Routes>
  )
}

function TestSales() {
  return (
    <Routes>
      <Route path="/customers" element={<CustomersPage />} />
      <Route path="/clients" element={<CustomersPage />} />
      <Route path="/consumers" element={<CustomersPage />} />
      <Route path="/quotations" element={<QuotationsPage />} />
      <Route path="/orders" element={<SalesOrdersPage />} />
      <Route path="/invoices" element={<InvoicesPage />} />
      <Route path="/payment-received" element={<PaymentReceivedPage />} />
      <Route path="/credit-notes" element={<CreditNotePage />} />
      <Route path="/refund" element={<RefundPage />} />
      <Route path="/*" element={<CustomersPage />} />
    </Routes>
  )
}

function TestAccounting() {
  return (
    <Routes>
      <Route path="/chart-of-accounts" element={<ChartOfAccountsPage />} />
      <Route path="/journal-entries" element={<JournalEntriesPage />} />
      <Route path="/trial-balance" element={<FinancialReportsPage />} />
      <Route path="/balance-sheet" element={<FinancialReportsPage />} />
      <Route path="/profit-loss" element={<FinancialReportsPage />} />
      <Route path="/cash-flow" element={<FinancialReportsPage />} />
      <Route path="/*" element={<ChartOfAccountsPage />} />
    </Routes>
  )
}

function TestInventory() {
  return (
    <Routes>
      <Route path="/items" element={<ItemsPage />} />
      <Route path="/price-lists" element={<ItemsPage />} />
      <Route path="/adjustments" element={<InventoryAdjustmentPage />} />
      <Route path="/movements" element={<ItemsPage />} />
      <Route path="/*" element={<ItemsPage />} />
    </Routes>
  )
}

function TestPurchase() {
  return (
    <Routes>
      <Route path="/orders" element={<PurchaseOrdersPage />} />
      <Route path="/invoices" element={<PurchaseOrdersPage />} />
      <Route path="/payments" element={<PurchaseOrdersPage />} />
      <Route path="/debit-notes" element={<PurchaseOrdersPage />} />
      <Route path="/*" element={<PurchaseOrdersPage />} />
    </Routes>
  )
}

function TestSecurity() {
  return (
    <Routes>
      <Route path="/" element={<SecurityManagementPage />} />
      <Route path="/permissions" element={<SecurityManagementPage />} />
      <Route path="/roles" element={<SecurityManagementPage />} />
      <Route path="/audit" element={<SecurityManagementPage />} />
      <Route path="/*" element={<SecurityManagementPage />} />
    </Routes>
  )
}

function TestSettings() {
  return (
    <Routes>
      <Route path="/" element={<SettingsPageMinimal />} />
      <Route path="/translations" element={<DynamicTranslationManagementPage />} />
      <Route path="/*" element={<SettingsPageMinimal />} />
    </Routes>
  )
}

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  const { checkAuthentication } = useAuthStore()
  const isAuthenticated = checkAuthentication()
  
  // If not authenticated, show login page
  if (!isAuthenticated) {
    return (
      <QueryClientProvider client={queryClient}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<LoginPage />} />
        </Routes>
      </QueryClientProvider>
    )
  }
  
  return (
    <QueryClientProvider client={queryClient}>
    <>
      <div className="font-optimized">
        <NewLayout>
        <Routes>
          <Route path="/" element={<TestDashboard />} />
          <Route path="/dashboard" element={<TestDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          
          {/* Users Management */}
          <Route path="/users" element={<UsersPage />} />
          <Route path="/permissions" element={<PermissionsPage />} />
          
          {/* HR Module */}
          <Route path="/hr/*" element={<TestHR />} />
          
          {/* Sales Module */}
          <Route path="/sales/*" element={<TestSales />} />
          <Route path="/customers" element={<CustomersPage />} />
          
          {/* Inventory Module - This is the key addition */}
          <Route path="/inventory/*" element={<TestInventory />} />
          <Route path="/items" element={<ItemsPage />} />
          <Route path="/inventory/adjustments" element={<InventoryAdjustmentPage />} />
          <Route path="/inventory/price-lists" element={<TestDashboard />} />
          <Route path="/inventory/movements" element={<TestDashboard />} />
          
          {/* Accounting Module */}
          <Route path="/accounting/*" element={<TestAccounting />} />
          
          {/* Purchase Module */}
          <Route path="/purchase/*" element={<TestPurchase />} />
          <Route path="/vendors" element={<VendorsPage />} />
          <Route path="/purchase/orders" element={<PurchaseOrdersPage />} />
          
          {/* Organization */}
          <Route path="/branches" element={<BranchesPage />} />
          <Route path="/warehouses" element={<WarehousesPage />} />
          
          {/* Vendors */}
          <Route path="/vendors" element={<VendorsPage />} />
          
          {/* Security */}
          <Route path="/security/*" element={<TestSecurity />} />
          
          {/* Settings */}
          <Route path="/settings/*" element={<TestSettings />} />
          
          {/* Money Transfer */}
          <Route path="/money-transfer/dashboard" element={<MoneyTransferDashboard />} />
          <Route path="/money-transfer/alerts" element={<MoneyTransferDashboard />} />
          
          {/* Financial Management */}
          <Route path="/financial/dashboard" element={<FinancialDashboard />} />
          <Route path="/financial/cash-boxes" element={<CashBoxesPage />} />
          <Route path="/financial/bank-accounts" element={<BankAccountsPage />} />
          <Route path="/financial/digital-accounts" element={<DigitalAccountsPage />} />
          <Route path="/financial/money-transfers" element={<MoneyTransferDashboard />} />
          <Route path="/financial/transfer-tracking" element={<TransferTrackingPage />} />
          <Route path="/financial/salesperson-boxes" element={<SalespersonBoxesPage />} />
          
          {/* POS */}
          <Route path="/pos" element={<POSInterface />} />
          <Route path="/pos/terminals" element={<POSInterface />} />
          <Route path="/pos/sessions" element={<POSInterface />} />
          <Route path="/pos/transactions" element={<POSInterface />} />
          
          {/* Migration and Models */}
          <Route path="/migration" element={<TestDashboard />} />
          <Route path="/models" element={<TestDashboard />} />
          
          {/* Expenses */}
          <Route path="/expenses" element={<TestDashboard />} />
          <Route path="/expenses/categories" element={<TestDashboard />} />
          <Route path="/expenses/reports" element={<TestDashboard />} />
          
          {/* Cashflow */}
          <Route path="/cashflow/cash-boxes" element={<TestDashboard />} />
          <Route path="/cashflow/transactions" element={<TestDashboard />} />
          <Route path="/cashflow/transfers" element={<TestDashboard />} />
          
          <Route path="*" element={<TestDashboard />} />
        </Routes>
      </NewLayout>
    </div>
    </>
    </QueryClientProvider>
  )
}

export default App
