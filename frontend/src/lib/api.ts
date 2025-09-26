import axios, { AxiosResponse } from 'axios'
import type { 
  LoginCredentials, 
  User, 
  Branch, 
  Warehouse, 
  Item, 
  Customer, 
  Vendor, 
  MigrationBatch,
  PaginatedResponse,
  ChartOfAccounts,
  Account,
  Currency,
  ExchangeRate,
  Journal,
  JournalEntry,
  SalesInvoice,
  PurchaseInvoice,
  InvoicePayment,
  InvoiceSummary,
  InvoiceFilter,
  InvoiceStatusEnum
} from '@/types'

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authData = localStorage.getItem('tsh-erp-auth')
    if (authData) {
      try {
        const { state } = JSON.parse(authData)
        if (state?.token) {
          config.headers.Authorization = `Bearer ${state.token}`
        }
      } catch (error) {
        console.error('Error parsing auth data:', error)
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('tsh-erp-auth')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (credentials: LoginCredentials): Promise<AxiosResponse<{ user: any; access_token: string; token_type: string }>> =>
    api.post('/auth/login', credentials),
  
  refreshToken: (token: string): Promise<AxiosResponse<{ user: User; access_token: string }>> =>
    api.post('/auth/refresh', { refresh_token: token }),
  
  me: (): Promise<AxiosResponse<User>> =>
    api.get('/auth/me'),
}

// Users API
export const usersApi = {
  getUsers: (params?: { page?: number; limit?: number; search?: string }): Promise<AxiosResponse<User[]>> =>
    api.get('/users/', { params: { skip: ((params?.page || 1) - 1) * (params?.limit || 10), limit: params?.limit || 10 } }),
  
  getUser: (id: number): Promise<AxiosResponse<User>> =>
    api.get(`/users/${id}`),
  
  createUser: (data: Partial<User>): Promise<AxiosResponse<User>> =>
    api.post('/users/', data),
  
  updateUser: (id: number, data: Partial<User>): Promise<AxiosResponse<User>> =>
    api.put(`/users/${id}`, data),
  
  deleteUser: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/users/${id}`),
  
  getRoles: (): Promise<AxiosResponse<{ id: number; name: string }[]>> =>
    api.get('/users/roles'),
  
  getBranches: (): Promise<AxiosResponse<{ id: number; name: string; code: string }[]>> =>
    api.get('/users/branches'),
}

// Permissions API
export const permissionsApi = {
  getPermissions: (): Promise<AxiosResponse<any[]>> =>
    api.get('/permissions'),
  
  getRolesWithPermissions: (): Promise<AxiosResponse<any[]>> =>
    api.get('/permissions/roles'),
  
  createRole: (data: any): Promise<AxiosResponse<any>> =>
    api.post('/permissions/roles', data),
  
  updateRole: (id: number, data: any): Promise<AxiosResponse<any>> =>
    api.put(`/permissions/roles/${id}`, data),
  
  deleteRole: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/permissions/roles/${id}`),
  
  getPermissionCategories: (): Promise<AxiosResponse<string[]>> =>
    api.get('/permissions/categories'),
}

// Branches API
export const branchesApi = {
  getBranches: (params?: { page?: number; limit?: number; search?: string }): Promise<AxiosResponse<PaginatedResponse<Branch>>> =>
    api.get('/branches', { params }),
  
  getBranch: (id: number): Promise<AxiosResponse<Branch>> =>
    api.get(`/branches/${id}`),
  
  createBranch: (data: Partial<Branch>): Promise<AxiosResponse<Branch>> =>
    api.post('/branches', data),
  
  updateBranch: (id: number, data: Partial<Branch>): Promise<AxiosResponse<Branch>> =>
    api.put(`/branches/${id}`, data),
  
  deleteBranch: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/branches/${id}`),
}

// Warehouses API
export const warehousesApi = {
  getWarehouses: (params?: { page?: number; limit?: number; search?: string; branch_id?: number }): Promise<AxiosResponse<PaginatedResponse<Warehouse>>> =>
    api.get('/warehouses', { params }),
  
  getWarehouse: (id: number): Promise<AxiosResponse<Warehouse>> =>
    api.get(`/warehouses/${id}`),
  
  createWarehouse: (data: Partial<Warehouse>): Promise<AxiosResponse<Warehouse>> =>
    api.post('/warehouses', data),
  
  updateWarehouse: (id: number, data: Partial<Warehouse>): Promise<AxiosResponse<Warehouse>> =>
    api.put(`/warehouses/${id}`, data),
  
  deleteWarehouse: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/warehouses/${id}`),
}

// Items API
export const itemsApi = {
  getItems: (params?: { page?: number; limit?: number; search?: string; category_id?: number; branch_id?: number }): Promise<AxiosResponse<PaginatedResponse<Item>>> =>
    api.get('/items', { params }),
  
  getItem: (id: number): Promise<AxiosResponse<Item>> =>
    api.get(`/items/${id}`),
  
  createItem: (data: Partial<Item>): Promise<AxiosResponse<Item>> =>
    api.post('/items', data),
  
  updateItem: (id: number, data: Partial<Item>): Promise<AxiosResponse<Item>> =>
    api.put(`/items/${id}`, data),
  
  deleteItem: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/items/${id}`),
}

// Customers API
export const customersApi = {
  getCustomers: (params?: { page?: number; limit?: number; search?: string; branch_id?: number }): Promise<AxiosResponse<PaginatedResponse<Customer>>> =>
    api.get('/customers', { params }),
  
  getCustomer: (id: number): Promise<AxiosResponse<Customer>> =>
    api.get(`/customers/${id}`),
  
  generateCustomerCode: (prefix?: string): Promise<AxiosResponse<{ customer_code: string; format: string; example: string }>> =>
    api.get('/customers/generate-code', { params: { prefix: prefix || 'CUST' } }),
  
  createCustomer: (data: Partial<Customer>): Promise<AxiosResponse<Customer>> =>
    api.post('/customers', data),
  
  updateCustomer: (id: number, data: Partial<Customer>): Promise<AxiosResponse<Customer>> =>
    api.put(`/customers/${id}`, data),
  
  deleteCustomer: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/customers/${id}`),
}

// Vendors API
export const vendorsApi = {
  getVendors: (params?: { page?: number; limit?: number; search?: string }): Promise<AxiosResponse<PaginatedResponse<Vendor>>> =>
    api.get('/vendors', { params }),
  
  getVendor: (id: number): Promise<AxiosResponse<Vendor>> =>
    api.get(`/vendors/${id}`),
  
  createVendor: (data: Partial<Vendor>): Promise<AxiosResponse<Vendor>> =>
    api.post('/vendors', data),
  
  updateVendor: (id: number, data: Partial<Vendor>): Promise<AxiosResponse<Vendor>> =>
    api.put(`/vendors/${id}`, data),
  
  deleteVendor: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/vendors/${id}`),
}

// Migration API
export const migrationApi = {
  getBatches: (params?: { page?: number; limit?: number; status?: string }): Promise<AxiosResponse<PaginatedResponse<MigrationBatch>>> =>
    api.get('/migration/batches', { params }),
  
  getBatch: (id: number): Promise<AxiosResponse<MigrationBatch>> =>
    api.get(`/migration/batches/${id}`),
  
  createBatch: (data: { batch_name: string; description?: string; source_system: string }): Promise<AxiosResponse<MigrationBatch>> =>
    api.post('/migration/batches', data),
  
  startBatch: (id: number): Promise<AxiosResponse<MigrationBatch>> =>
    api.post(`/migration/batches/${id}/start`),
  
  testZohoConnection: (): Promise<AxiosResponse<{ status: string; message: string }>> =>
    api.get('/migration/zoho/test-connection'),
  
  extractZohoData: (data: { data_types: string[]; batch_size?: number }): Promise<AxiosResponse<any>> =>
    api.post('/migration/zoho/extract-async', data),
}

// Migration Items API (public access)
export const migrationItemsApi = {
  getItems: (params?: { skip?: number; limit?: number; search?: string; category_id?: number; active_only?: boolean }): Promise<AxiosResponse<Item[]>> =>
    api.get('/migration/items/', { params }),
  
  getItem: (id: number): Promise<AxiosResponse<Item>> =>
    api.get(`/migration/items/${id}`),
  
  createItem: (data: Partial<Item>): Promise<AxiosResponse<Item>> =>
    api.post('/migration/items/', data),
  
  updateItem: (id: number, data: Partial<Item>): Promise<AxiosResponse<Item>> =>
    api.put(`/migration/items/${id}`, data),
  
  deleteItem: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/migration/items/${id}`),
  
  getCategories: (params?: { skip?: number; limit?: number; active_only?: boolean }): Promise<AxiosResponse<any[]>> =>
    api.get('/migration/categories/', { params }),
}

// Accounting API
export const accountingApi = {
  // Currencies
  getCurrencies: (): Promise<AxiosResponse<Currency[]>> =>
    api.get('/accounting/currencies'),
  
  createCurrency: (data: Partial<Currency>): Promise<AxiosResponse<Currency>> =>
    api.post('/accounting/currencies', data),
  
  updateCurrency: (id: number, data: Partial<Currency>): Promise<AxiosResponse<Currency>> =>
    api.put(`/accounting/currencies/${id}`, data),

  // Chart of Accounts
  getChartOfAccounts: (): Promise<AxiosResponse<ChartOfAccounts[]>> =>
    api.get('/accounting/chart-of-accounts'),
  
  createChartOfAccounts: (data: Partial<ChartOfAccounts>): Promise<AxiosResponse<ChartOfAccounts>> =>
    api.post('/accounting/chart-of-accounts', data),
  
  updateChartOfAccounts: (id: number, data: Partial<ChartOfAccounts>): Promise<AxiosResponse<ChartOfAccounts>> =>
    api.put(`/accounting/chart-of-accounts/${id}`, data),
  
  getChartOfAccount: (id: number): Promise<AxiosResponse<ChartOfAccounts>> =>
    api.get(`/accounting/chart-of-accounts/${id}`),

  // Accounts
  getAccounts: (params?: { chart_id?: number; account_type?: string; parent_id?: number }): Promise<AxiosResponse<Account[]>> =>
    api.get('/accounting/accounts', { params }),
  
  createAccount: (data: Partial<Account>): Promise<AxiosResponse<Account>> =>
    api.post('/accounting/accounts', data),
  
  updateAccount: (id: number, data: Partial<Account>): Promise<AxiosResponse<Account>> =>
    api.put(`/accounting/accounts/${id}`, data),
  
  getAccount: (id: number): Promise<AxiosResponse<Account>> =>
    api.get(`/accounting/accounts/${id}`),

  // Exchange Rates
  getExchangeRates: (params?: { from_currency?: string; to_currency?: string; date?: string }): Promise<AxiosResponse<ExchangeRate[]>> =>
    api.get('/accounting/exchange-rates', { params }),
  
  createExchangeRate: (data: Partial<ExchangeRate>): Promise<AxiosResponse<ExchangeRate>> =>
    api.post('/accounting/exchange-rates', data),

  // Journals
  getJournals: (): Promise<AxiosResponse<Journal[]>> =>
    api.get('/accounting/journals'),
  
  createJournal: (data: Partial<Journal>): Promise<AxiosResponse<Journal>> =>
    api.post('/accounting/journals', data),

  // Journal Entries
  getJournalEntries: (params?: { journal_id?: number; period_id?: number; start_date?: string; end_date?: string }): Promise<AxiosResponse<JournalEntry[]>> =>
    api.get('/accounting/journal-entries', { params }),
  
  createJournalEntry: (data: Partial<JournalEntry>): Promise<AxiosResponse<JournalEntry>> =>
    api.post('/accounting/journal-entries', data),
  
  getJournalEntry: (id: number): Promise<AxiosResponse<JournalEntry>> =>
    api.get(`/accounting/journal-entries/${id}`),
}

// Invoice API
export const invoiceApi = {
  // Sales Invoices
  getSalesInvoices: (params?: InvoiceFilter & { skip?: number; limit?: number }): Promise<AxiosResponse<SalesInvoice[]>> =>
    api.get('/invoices/sales', { params }),
  
  createSalesInvoice: (data: Partial<SalesInvoice>): Promise<AxiosResponse<SalesInvoice>> =>
    api.post('/invoices/sales', data),
  
  getSalesInvoice: (id: number): Promise<AxiosResponse<SalesInvoice>> =>
    api.get(`/invoices/sales/${id}`),
  
  updateSalesInvoice: (id: number, data: Partial<SalesInvoice>): Promise<AxiosResponse<SalesInvoice>> =>
    api.put(`/invoices/sales/${id}`, data),
  
  deleteSalesInvoice: (id: number): Promise<AxiosResponse<{ message: string }>> =>
    api.delete(`/invoices/sales/${id}`),

  // Purchase Invoices
  getPurchaseInvoices: (params?: InvoiceFilter & { skip?: number; limit?: number }): Promise<AxiosResponse<PurchaseInvoice[]>> =>
    api.get('/invoices/purchase', { params }),
  
  createPurchaseInvoice: (data: Partial<PurchaseInvoice>): Promise<AxiosResponse<PurchaseInvoice>> =>
    api.post('/invoices/purchase', data),
  
  getPurchaseInvoice: (id: number): Promise<AxiosResponse<PurchaseInvoice>> =>
    api.get(`/invoices/purchase/${id}`),
  
  updatePurchaseInvoice: (id: number, data: Partial<PurchaseInvoice>): Promise<AxiosResponse<PurchaseInvoice>> =>
    api.put(`/invoices/purchase/${id}`, data),
  
  deletePurchaseInvoice: (id: number): Promise<AxiosResponse<{ message: string }>> =>
    api.delete(`/invoices/purchase/${id}`),

  // Invoice Payments
  createPayment: (data: Partial<InvoicePayment>): Promise<AxiosResponse<InvoicePayment>> =>
    api.post('/invoices/payments', data),
  
  getAllPayments: (params?: { page?: number; size?: number; invoice_type?: 'SALES' | 'PURCHASE' }): Promise<AxiosResponse<InvoicePayment[]>> =>
    api.get('/invoices/payments', { params }),
  
  getInvoicePayments: (invoiceId: number, invoiceType: 'SALES' | 'PURCHASE'): Promise<AxiosResponse<InvoicePayment[]>> =>
    api.get(`/invoices/payments/${invoiceId}`, { params: { invoice_type: invoiceType } }),

  // Invoice Status Management
  markSalesInvoiceAsSent: (id: number): Promise<AxiosResponse<{ message: string }>> =>
    api.post(`/invoices/sales/${id}/send`),
  
  markPurchaseInvoiceAsSent: (id: number): Promise<AxiosResponse<{ message: string }>> =>
    api.post(`/invoices/purchase/${id}/send`),
  
  cancelSalesInvoice: (id: number): Promise<AxiosResponse<{ message: string }>> =>
    api.post(`/invoices/sales/${id}/cancel`),
  
  cancelPurchaseInvoice: (id: number): Promise<AxiosResponse<{ message: string }>> =>
    api.post(`/invoices/purchase/${id}/cancel`),

  // Dashboard and Reports
  getInvoiceSummary: (branchId?: number): Promise<AxiosResponse<InvoiceSummary>> =>
    api.get('/invoices/summary', { params: branchId ? { branch_id: branchId } : undefined }),
  
  getOverdueInvoices: (branchId?: number): Promise<AxiosResponse<{ sales: SalesInvoice[]; purchase: PurchaseInvoice[] }>> =>
    api.get('/invoices/overdue', { params: branchId ? { branch_id: branchId } : undefined }),

  // Generate Invoice from Order
  generateInvoiceFromOrder: (orderId: number, orderType: 'SALES' | 'PURCHASE'): Promise<AxiosResponse<SalesInvoice | PurchaseInvoice>> =>
    api.post('/invoices/generate-from-order', null, { params: { order_id: orderId, order_type: orderType } }),
}

// Convenience functions for easier import
export const getAllSalesInvoices = async (params?: {
  page?: number;
  size?: number;
  status?: InvoiceStatusEnum;
}): Promise<PaginatedResponse<SalesInvoice>> => {
  const { page = 1, size = 10, status } = params || {};
  const response = await invoiceApi.getSalesInvoices({ 
    skip: (page - 1) * size, 
    limit: size, 
    status
  });
  return {
    data: response.data,
    total: response.data.length, // Backend should return total count
    page,
    pageSize: size,
    totalPages: Math.ceil(response.data.length / size)
  };
};

export const purchaseInvoicesPaginated = async (params?: {
  page?: number;
  size?: number;
  status?: InvoiceStatusEnum;
}): Promise<PaginatedResponse<PurchaseInvoice>> => {
  const { page = 1, size = 10, status } = params || {};
  const response = await invoiceApi.getPurchaseInvoices({ 
    skip: (page - 1) * size, 
    limit: size, 
    status
  });
  return {
    data: response.data,
    total: response.data.length, // Backend should return total count
    page,
    pageSize: size,
    totalPages: Math.ceil(response.data.length / size)
  };
};

// Alias function for backward compatibility
export const getAllPurchaseInvoices = purchaseInvoicesPaginated;

// Dashboard API
export const dashboardApi = {
  getStats: (params?: { branch_id?: number }): Promise<AxiosResponse<{
    totalUsers: number;
    totalItems: number;
    totalOrders: number;
    totalRevenue: number;
    totalBranches: number;
    totalWarehouses: number;
    lowStockItems: number;
    pendingOrders: number;
    monthlyRevenue: number[];
    recentActivities: any[];
  }>> =>
    api.get('/dashboard/stats', { params }),
  
  getRecentActivities: (params?: { branch_id?: number; limit?: number }): Promise<AxiosResponse<any[]>> =>
    api.get('/dashboard/activities', { params }),
}

// Expenses API
export const expensesApi = {
  getExpenses: (params?: { page?: number; limit?: number; search?: string; branch_id?: number; category_id?: number; status?: string }): Promise<AxiosResponse<PaginatedResponse<any>>> =>
    api.get('/expenses', { params }),
  
  getExpense: (id: number): Promise<AxiosResponse<any>> =>
    api.get(`/expenses/${id}`),
  
  createExpense: (data: any): Promise<AxiosResponse<any>> =>
    api.post('/expenses', data),
  
  updateExpense: (id: number, data: any): Promise<AxiosResponse<any>> =>
    api.put(`/expenses/${id}`, data),
  
  deleteExpense: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/expenses/${id}`),
  
  getCategories: (): Promise<AxiosResponse<any[]>> =>
    api.get('/expenses/categories'),
  
  getStatuses: (): Promise<AxiosResponse<any[]>> =>
    api.get('/expenses/statuses'),
}

// Admin Dashboard API
export const adminApi = {
  // Get comprehensive admin dashboard data
  getDashboard: (params?: { date_from?: string; date_to?: string }) =>
    api.get('/admin/dashboard', { params }),
  
  // Get GPS tracking data for travel salespersons
  getGPSTracking: (params?: { user_id?: number; date_from?: string; date_to?: string }) =>
    api.get('/admin/gps-tracking', { params }),
  
  // Get partner salesmen performance metrics
  getPartnerPerformance: (params?: { limit?: number; time_period?: string }) =>
    api.get('/admin/partner-salesmen/performance', { params }),
  
  // Get system alerts
  getAlerts: (params?: { priority?: string; alert_type?: string; limit?: number }) =>
    api.get('/admin/alerts', { params }),
  
  // Mark alert as read
  markAlertAsRead: (alertId: string) =>
    api.post(`/admin/alerts/${alertId}/mark-read`),
  
  // Get system health status
  getSystemHealth: () =>
    api.get('/admin/system-health'),
  
  // Real-time dashboard refresh
  refreshDashboard: () =>
    api.get('/admin/dashboard?_t=' + Date.now()),
}

export default api
