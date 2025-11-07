import { Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { useAuthStore } from './stores/authStore'

// Import pages
import { DemoPage } from './pages/DemoPage'
import { AdminDashboard } from './pages/dashboard/AdminDashboard'
import { UsersPage } from './pages/users/UsersPage'
import { PermissionsPage } from './pages/permissions/PermissionsPage'
import { EmployeesPage } from './pages/hr/EmployeesPage'
import { CustomersPage } from './pages/customers/CustomersPage'
import { SalesOrdersPage } from './pages/sales/SalesOrdersPage'
import InvoicesPage from './pages/sales/InvoicesPage'
import QuotationsPage from './pages/sales/QuotationsPage'
import PaymentReceivedPage from './pages/sales/PaymentReceivedPage'
import CreditNotePage from './pages/sales/CreditNotePage'
import RefundPage from './pages/sales/RefundPage'
import ItemsPage from './pages/inventory/ItemsPage'
import InventoryAdjustmentPage from './pages/inventory/InventoryAdjustmentPage'
import ChartOfAccountsPage from './pages/accounting/ChartOfAccountsPage'
import JournalEntriesPage from './pages/accounting/JournalEntriesPage'
import FinancialReportsPage from './pages/accounting/FinancialReportsPage'
import { VendorsPage } from './pages/vendors/VendorsPage'
import { PurchaseOrdersPage } from './pages/purchase/PurchaseOrdersPage'
import { BranchesPage } from './pages/branches/BranchesPage'
import { WarehousesPage } from './pages/warehouses/WarehousesPage'
import { SecurityManagementPage } from './pages/security/SecurityManagementPage'
import DynamicTranslationManagementPage from './pages/settings/DynamicTranslationManagementPage'
import SettingsPageMinimal from './pages/settings/SettingsPageMinimal'
import FinancialDashboard from './pages/financial/FinancialDashboard'
import CashBoxesPage from './pages/financial/CashBoxesPage'
import BankAccountsPage from './pages/financial/BankAccountsPage'
import DigitalAccountsPage from './pages/financial/DigitalAccountsPage'
import TransferTrackingPage from './pages/financial/TransferTrackingPage'
import SalespersonBoxesPage from './pages/financial/SalespersonBoxesPage'
import POSInterface from './pages/pos/POSInterface'

// Helper routing components
function TestHR() {
  return (
    <Routes>
      <Route path="users" element={<UsersPage />} />
      <Route path="employees" element={<EmployeesPage />} />
      <Route path="*" element={<UsersPage />} />
    </Routes>
  )
}

function TestSales() {
  return (
    <Routes>
      <Route path="/customers" element={<CustomersPage />} />
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

function TestInventory() {
  return (
    <Routes>
      <Route path="/" element={<ItemsPage />} />
      <Route path="/items" element={<ItemsPage />} />
      <Route path="/adjustments" element={<InventoryAdjustmentPage />} />
      <Route path="/*" element={<ItemsPage />} />
    </Routes>
  )
}

function TestAccounting() {
  return (
    <Routes>
      <Route path="/" element={<ChartOfAccountsPage />} />
      <Route path="/chart-of-accounts" element={<ChartOfAccountsPage />} />
      <Route path="/journal-entries" element={<JournalEntriesPage />} />
      <Route path="/financial-reports" element={<FinancialReportsPage />} />
      <Route path="/*" element={<ChartOfAccountsPage />} />
    </Routes>
  )
}

function TestPurchase() {
  return (
    <Routes>
      <Route path="/" element={<VendorsPage />} />
      <Route path="/vendors" element={<VendorsPage />} />
      <Route path="/orders" element={<PurchaseOrdersPage />} />
      <Route path="/*" element={<VendorsPage />} />
    </Routes>
  )
}

function TestSecurity() {
  return (
    <Routes>
      <Route path="/" element={<SecurityManagementPage />} />
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
  // Initialize auth store to set demo user
  const { checkAuthentication } = useAuthStore()
  checkAuthentication() // This will create the demo user

  // Always show demo page for main routes
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path="/" element={<DemoPage />} />
        <Route path="/dashboard" element={<DemoPage />} />
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
        
        {/* Inventory Module */}
        <Route path="/inventory/*" element={<TestInventory />} />
        <Route path="/items" element={<ItemsPage />} />
        <Route path="/inventory/adjustments" element={<InventoryAdjustmentPage />} />
        
        {/* Accounting Module */}
        <Route path="/accounting/*" element={<TestAccounting />} />
        
        {/* Purchase Module */}
        <Route path="/purchase/*" element={<TestPurchase />} />
        <Route path="/vendors" element={<VendorsPage />} />
        <Route path="/purchase/orders" element={<PurchaseOrdersPage />} />
        
        {/* Organization */}
        <Route path="/branches" element={<BranchesPage />} />
        <Route path="/warehouses" element={<WarehousesPage />} />
        
        {/* Security */}
        <Route path="/security/*" element={<TestSecurity />} />
        
        {/* Settings */}
        <Route path="/settings/*" element={<TestSettings />} />
        
        {/* Financial Management */}
        <Route path="/financial/dashboard" element={<FinancialDashboard />} />
        <Route path="/financial/cash-boxes" element={<CashBoxesPage />} />
        <Route path="/financial/bank-accounts" element={<BankAccountsPage />} />
        <Route path="/financial/digital-accounts" element={<DigitalAccountsPage />} />
        <Route path="/financial/transfer-tracking" element={<TransferTrackingPage />} />
        <Route path="/financial/salesperson-boxes" element={<SalespersonBoxesPage />} />
        
        {/* POS */}
        <Route path="/pos" element={<POSInterface />} />
        
        {/* Default route */}
        <Route path="*" element={<DemoPage />} />
      </Routes>
    </QueryClientProvider>
  )
}

export default App
