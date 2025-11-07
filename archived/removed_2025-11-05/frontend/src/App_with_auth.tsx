import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { QueryClient, QueryClientProvider } from 'react-query'

// Layout Components
import Layout from '@/components/layout/NewLayout'
import { LoginPage } from '@/pages/auth/LoginPage'
import DashboardPage from '@/pages/dashboard/NewDashboardPage'

// HR Module Pages
import { EmployeesPage } from '@/pages/hr/EmployeesPage'
import TravelSalespersonPage from '@/pages/hr/TravelSalespersonPage'
import PartnerSalesmanPage from '@/pages/hr/PartnerSalesmanPage'
import RetailermanPage from '@/pages/hr/RetailermanPage'

// Sales Module Pages
import CustomersPage from '@/pages/sales/CustomersPage'
import ClientsPage from '@/pages/sales/ClientsPage'
import ConsumersPage from '@/pages/sales/ConsumersPage'
import QuotationsPage from '@/pages/sales/QuotationsPage'
import SaleOrdersPage from '@/pages/sales/SaleOrdersPage'
import InvoicesPage from '@/pages/sales/InvoicesPage'
import PaymentReceivedPage from '@/pages/sales/PaymentReceivedPage'
import CreditNotePage from '@/pages/sales/CreditNotePage'
import RefundPage from '@/pages/sales/RefundPage'

// Stores
import { useAuthStore } from '@/stores/authStore'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

// Simple template component for missing pages
const TemplatePage: React.FC<{ title: string; description: string }> = ({ title, description }) => (
  <div className="space-y-6">
    <div>
      <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
      <p className="text-gray-600">{description}</p>
    </div>
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold mb-4">{title} Management</h2>
      <p className="text-gray-600">{title} management features will be implemented here.</p>
    </div>
  </div>
)

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Auth Routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected Routes */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      {/* Dashboard */}
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard" element={<DashboardPage />} />
                      
                      {/* HR Module Routes */}
                      <Route path="/hr/employees" element={<EmployeesPage />} />
                      <Route path="/hr/travel-salesperson" element={<TravelSalespersonPage />} />
                      <Route path="/hr/partner-salesman" element={<PartnerSalesmanPage />} />
                      <Route path="/hr/retailerman" element={<RetailermanPage />} />
                      
                      {/* Sales Module Routes */}
                      <Route path="/sales/customers" element={<CustomersPage />} />
                      <Route path="/sales/clients" element={<ClientsPage />} />
                      <Route path="/sales/consumers" element={<ConsumersPage />} />
                      <Route path="/sales/quotations" element={<QuotationsPage />} />
                      <Route path="/sales/orders" element={<SaleOrdersPage />} />
                      <Route path="/sales/invoices" element={<InvoicesPage />} />
                      <Route path="/sales/payment-received" element={<PaymentReceivedPage />} />
                      <Route path="/sales/credit-note" element={<CreditNotePage />} />
                      <Route path="/sales/refund" element={<RefundPage />} />
                      
                      {/* Purchases Module Routes */}
                      <Route path="/purchases/vendors" element={<TemplatePage title="Vendors" description="Manage vendors and suppliers" />} />
                      <Route path="/purchases/orders" element={<TemplatePage title="Purchase Orders" description="Manage purchase orders" />} />
                      <Route path="/purchases/bills" element={<TemplatePage title="Bills" description="Manage vendor bills" />} />
                      <Route path="/purchases/payment-made" element={<TemplatePage title="Payment Made" description="Track payments made to vendors" />} />
                      <Route path="/purchases/debit-note" element={<TemplatePage title="Debit Note" description="Manage debit notes" />} />
                      
                      {/* Accounting Module Routes */}
                      <Route path="/accounting/chart-of-accounts" element={<TemplatePage title="Chart of Accounts" description="Manage chart of accounts" />} />
                      <Route path="/accounting/journal-entries" element={<TemplatePage title="Journal Entries" description="Manage journal entries" />} />
                      <Route path="/accounting/trial-balance" element={<TemplatePage title="Trial Balance" description="View trial balance reports" />} />
                      <Route path="/accounting/profit-loss" element={<TemplatePage title="Profit & Loss" description="View profit and loss statements" />} />
                      <Route path="/accounting/balance-sheet" element={<TemplatePage title="Balance Sheet" description="View balance sheet reports" />} />
                      <Route path="/accounting/cash-flow" element={<TemplatePage title="Cash Flow" description="View cash flow statements" />} />
                      
                      {/* Expenses Module Routes */}
                      <Route path="/expenses/list" element={<TemplatePage title="Expenses" description="Manage company expenses" />} />
                      <Route path="/expenses/categories" element={<TemplatePage title="Expense Categories" description="Manage expense categories" />} />
                      <Route path="/expenses/reports" element={<TemplatePage title="Expense Reports" description="View expense reports" />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
          <Toaster position="top-right" />
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
