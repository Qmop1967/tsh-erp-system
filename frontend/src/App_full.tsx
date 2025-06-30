import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'
import { Layout } from '@/components/layout/Layout'
import { LoginPage } from '@/pages/auth/LoginPage'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { UsersPage } from '@/pages/users/UsersPage'
import { EmployeesPage } from '@/pages/hr/EmployeesPage'
import { AchievementsPage } from '@/pages/hr/AchievementsPage'
import { ChallengesPage } from '@/pages/hr/ChallengesPage'
import { BranchesPage } from '@/pages/branches/BranchesPage'
import { WarehousesPage } from '@/pages/warehouses/WarehousesPage'
import { ItemsPage, ItemsManagement } from '@/pages/inventory/ItemsPage'
import { PriceListsPage } from '@/pages/inventory/PriceListsPage'
import { InventoryAdjustmentsPage } from '@/pages/inventory/InventoryAdjustmentsPage'
import { CustomersPage } from '@/pages/customers/CustomersPage'
import { SalesOrdersPage } from '@/pages/sales/SalesOrdersPage'
import { VendorsPage } from '@/pages/vendors/VendorsPage'
import { ExpensesPage } from '@/pages/expenses/ExpensesPage'
import { MigrationPage } from '@/pages/migration/MigrationPage'
import { ModelsPage } from '@/pages/models/ModelsPage'
import ChartOfAccountsPage from '@/pages/accounting/ChartOfAccountsPage'
import JournalEntriesPage from '@/pages/accounting/JournalEntriesPage'
import FinancialReportsPage from '@/pages/accounting/FinancialReportsPage'
import SalesInvoicesPage from '@/pages/invoices/SalesInvoicesPage'
import PurchaseInvoicesPage from '@/pages/invoices/PurchaseInvoicesPage'
import InvoicePaymentsPage from '@/pages/invoices/InvoicePaymentsPage'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { NotificationProvider } from '@/components/ui/NotificationProvider'

function App() {
  const { user } = useAuthStore()
  const { isRTL } = useLanguageStore()

  return (
    <NotificationProvider>
      <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${isRTL ? 'rtl' : 'ltr'}`}>
        <Routes>
          {/* Public routes */}
          <Route 
            path="/login" 
            element={
              user ? <Navigate to="/dashboard" replace /> : <LoginPage />
            } 
          />
          
          {/* Protected routes */}
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            
            {/* User Management */}
            <Route path="users" element={<UsersPage />} />
            
            {/* HR Module */}
            <Route path="hr/employees" element={<EmployeesPage />} />
            <Route path="hr/achievements" element={<AchievementsPage />} />
            <Route path="hr/challenges" element={<ChallengesPage />} />
            
            {/* Infrastructure */}
            <Route path="branches" element={<BranchesPage />} />
            <Route path="warehouses" element={<WarehousesPage />} />
            
            {/* Inventory */}
            <Route path="items" element={<ItemsPage />} />
            <Route path="inventory/items" element={<ItemsManagement />} />
            <Route path="inventory/price-lists" element={<PriceListsPage />} />
            <Route path="inventory/adjustments" element={<InventoryAdjustmentsPage />} />
            <Route path="inventory/reports" element={<div className="p-8"><h1>Inventory Reports - Coming Soon</h1></div>} />
            
            {/* Sales */}
            <Route path="customers" element={<CustomersPage />} />
            <Route path="sales/orders" element={<SalesOrdersPage />} />
            <Route path="sales/quotations" element={<div className="p-8"><h1>Sales Quotations - Coming Soon</h1></div>} />
            <Route path="sales/reports" element={<div className="p-8"><h1>Sales Reports - Coming Soon</h1></div>} />
            <Route path="pos/sales" element={<div className="p-8"><h1>POS Sales - Coming Soon</h1></div>} />
            <Route path="pos/returns" element={<div className="p-8"><h1>POS Returns - Coming Soon</h1></div>} />
            
            {/* Purchase */}
            <Route path="vendors" element={<VendorsPage />} />
            <Route path="purchase/orders" element={<div className="p-8"><h1>Purchase Orders - Coming Soon</h1></div>} />
            <Route path="purchase/receipts" element={<div className="p-8"><h1>Purchase Receipts - Coming Soon</h1></div>} />
            <Route path="purchase/returns" element={<div className="p-8"><h1>Purchase Returns - Coming Soon</h1></div>} />
            <Route path="purchase/reports" element={<div className="p-8"><h1>Purchase Reports - Coming Soon</h1></div>} />
            
            {/* Expenses */}
            <Route path="expenses" element={<ExpensesPage />} />
            <Route path="expenses/categories" element={<div className="p-8"><h1>Expense Categories - Coming Soon</h1></div>} />
            <Route path="expenses/reports" element={<div className="p-8"><h1>Expense Reports - Coming Soon</h1></div>} />
            
            {/* Accounting */}
            <Route path="accounting/chart-of-accounts" element={<ChartOfAccountsPage />} />
            <Route path="accounting/journal-entries" element={<JournalEntriesPage />} />
            <Route path="accounting/reports" element={<FinancialReportsPage />} />
            
            {/* Invoices */}
            <Route path="invoices/sales" element={<SalesInvoicesPage />} />
            <Route path="invoices/purchase" element={<PurchaseInvoicesPage />} />
            <Route path="invoices/payments" element={<InvoicePaymentsPage />} />
            
            {/* POS */}
            <Route path="pos/terminals" element={<div className="p-8"><h1>POS Terminals - Coming Soon</h1></div>} />
            <Route path="pos/sessions" element={<div className="p-8"><h1>POS Sessions - Coming Soon</h1></div>} />
            <Route path="pos/reports" element={<div className="p-8"><h1>POS Reports - Coming Soon</h1></div>} />
            
            {/* Cash Flow */}
            <Route path="cashflow/cash-boxes" element={<div className="p-8"><h1>Cash Boxes - Coming Soon</h1></div>} />
            <Route path="cashflow/transactions" element={<div className="p-8"><h1>Cash Transactions - Coming Soon</h1></div>} />
            <Route path="cashflow/reports" element={<div className="p-8"><h1>Cash Flow Reports - Coming Soon</h1></div>} />
            
            {/* Data Management */}
            <Route path="migration" element={<MigrationPage />} />
            <Route path="models" element={<ModelsPage />} />
          </Route>
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </NotificationProvider>
  )
}

export default App
