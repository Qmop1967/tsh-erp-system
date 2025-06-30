export interface User {
  id: number
  email: string
  name: string
  role_id?: number
  branch_id?: number
  employee_code?: string
  phone?: string
  is_salesperson?: boolean
  is_active?: boolean
  created_at?: string
  updated_at?: string
  last_login?: string
  // For backward compatibility with existing UI
  role?: string
  branch?: string
  permissions?: string[]
  isActive?: boolean
  createdAt?: string
  updatedAt?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface Branch {
  id: number
  code: string
  nameAr: string
  nameEn: string
  city: string
  address: string
  phone?: string
  email?: string
  managerId?: number
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface Warehouse {
  id: number
  code: string
  nameAr: string
  nameEn: string
  address: string
  phone?: string
  managerId?: number
  branchId: number
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface Item {
  id: number
  code: string
  nameAr: string
  nameEn: string
  descriptionAr?: string
  descriptionEn?: string
  categoryId?: number
  brand?: string
  model?: string
  unitOfMeasure: string
  costPriceUsd: number
  costPriceIqd: number
  sellingPriceUsd: number
  sellingPriceIqd: number
  trackInventory: boolean
  reorderLevel: number
  reorderQuantity: number
  isActive: boolean
  zohoItemId?: string
  zohoLastSync?: string
  createdAt: string
  updatedAt: string
}

export interface Customer {
  id: number
  code: string
  nameAr: string
  nameEn: string
  email?: string
  phone?: string
  addressAr?: string
  addressEn?: string
  city?: string
  currency: string
  outstandingReceivable: number
  salespersonId?: number
  priceListId?: number
  isActive: boolean
  zohoCustomerId?: string
  zohoDepositAccount?: string
  zohoLastSync?: string
  createdAt: string
  updatedAt: string
}

export interface Vendor {
  id: number
  code: string
  nameAr: string
  nameEn: string
  email?: string
  phone?: string
  contactPerson?: string
  addressAr?: string
  addressEn?: string
  currency: string
  outstandingPayable: number
  isActive: boolean
  zohoVendorId?: string
  zohoLastSync?: string
  createdAt: string
  updatedAt: string
}

export interface MigrationBatch {
  id: number
  batchNumber: string
  batchName: string
  description?: string
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'REQUIRES_REVIEW'
  startTime?: string
  endTime?: string
  totalEntities: number
  totalRecords: number
  successfulRecords: number
  failedRecords: number
  sourceSystem?: string
  migrationConfig?: string
  errorLog?: string
  createdAt: string
  updatedAt: string
  createdBy?: number
}

export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface Permission {
  id: number
  name: string
  description: string
  resource: string
  action: string
}

export interface Role {
  id: number
  name: string
  description: string
  permissions: Permission[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

// Accounting Types
export interface Currency {
  id: number
  code: string
  name_ar: string
  name_en: string
  symbol: string
  is_base_currency: boolean
  exchange_rate_to_base: number
  decimal_places: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ChartOfAccounts {
  id: number
  code: string
  name_ar: string
  name_en: string
  account_type: 'ASSET' | 'LIABILITY' | 'EQUITY' | 'REVENUE' | 'EXPENSE'
  parent_id?: number
  level: number
  is_active: boolean
  allow_posting: boolean
  description_ar?: string
  description_en?: string
  created_at: string
  updated_at: string
  parent?: ChartOfAccounts
  children?: ChartOfAccounts[]
  accounts?: Account[]
}

export interface Account {
  id: number
  chart_account_id: number
  currency_id: number
  branch_id?: number
  balance_debit: number
  balance_credit: number
  balance: number
  is_active: boolean
  created_at: string
  updated_at: string
  chart_account: ChartOfAccounts
  currency: Currency
}

export interface ExchangeRate {
  id: number
  from_currency_id: number
  to_currency_id: number
  rate: number
  date: string
  is_active: boolean
  created_at: string
  updated_at: string
  from_currency: Currency
  to_currency: Currency
}

export interface Journal {
  id: number
  code: string
  name_ar: string
  name_en: string
  journal_type: 'GENERAL' | 'SALES' | 'PURCHASE' | 'CASH' | 'BANK'
  currency_id: number
  branch_id?: number
  is_active: boolean
  created_at: string
  updated_at: string
  currency: Currency
}

export interface JournalEntry {
  id: number
  journal_id: number
  reference: string
  date: string
  description_ar?: string
  description_en?: string
  total_debit: number
  total_credit: number
  status: 'DRAFT' | 'POSTED' | 'REVERSED'
  created_by: number
  posted_by?: number
  posted_at?: string
  created_at: string
  updated_at: string
  journal: Journal
  journal_lines: JournalLine[]
}

export interface JournalLine {
  id: number
  journal_entry_id: number
  account_id: number
  debit_amount: number
  credit_amount: number
  description?: string
  created_at: string
  updated_at: string
  account: Account
}

// Invoice types
export enum InvoiceTypeEnum {
  SALES = "SALES",
  PURCHASE = "PURCHASE",
  CREDIT_NOTE = "CREDIT_NOTE",
  DEBIT_NOTE = "DEBIT_NOTE"
}

export enum InvoiceStatusEnum {
  DRAFT = "DRAFT",
  PENDING = "PENDING",
  PAID = "PAID",
  PARTIALLY_PAID = "PARTIALLY_PAID",
  OVERDUE = "OVERDUE",
  CANCELLED = "CANCELLED",
  REFUNDED = "REFUNDED"
}

export enum PaymentTermsEnum {
  IMMEDIATE = "IMMEDIATE",
  NET_7 = "NET_7",
  NET_15 = "NET_15",
  NET_30 = "NET_30",
  NET_60 = "NET_60",
  NET_90 = "NET_90",
  CUSTOM = "CUSTOM"
}

export enum PaymentMethodEnum {
  CASH = "CASH",
  BANK_TRANSFER = "BANK_TRANSFER",
  CHECK = "CHECK",
  CREDIT_CARD = "CREDIT_CARD",
  DEBIT_CARD = "DEBIT_CARD",
  ONLINE_PAYMENT = "ONLINE_PAYMENT",
  OTHER = "OTHER"
}

export interface SalesInvoiceItem {
  id: number
  invoice_id: number
  product_id: number
  sales_item_id?: number
  quantity: number
  unit_price: number
  discount_percentage?: number
  discount_amount?: number
  line_total: number
  description?: string
  notes?: string
}

export interface SalesInvoice {
  id: number
  invoice_number: string
  customer_id: number
  sales_order_id?: number
  branch_id: number
  warehouse_id?: number
  invoice_date: string
  due_date: string
  currency_id: number
  exchange_rate?: number
  invoice_type: InvoiceTypeEnum
  status: InvoiceStatusEnum
  payment_terms: PaymentTermsEnum
  subtotal: number
  discount_percentage?: number
  discount_amount?: number
  tax_percentage?: number
  tax_amount?: number
  shipping_amount?: number
  total_amount: number
  paid_amount?: number
  notes?: string
  internal_notes?: string
  payment_method?: string
  reference_number?: string
  is_recurring?: boolean
  recurring_frequency?: string
  parent_invoice_id?: number
  created_by: number
  created_at: string
  updated_at?: string
  issued_at?: string
  cancelled_at?: string
  remaining_amount: number
  is_fully_paid: boolean
  is_overdue: boolean
  invoice_items: SalesInvoiceItem[]
  customer?: Customer
  currency?: Currency
  branch?: Branch
}

export interface PurchaseInvoiceItem {
  id: number
  invoice_id: number
  product_id: number
  purchase_item_id?: number
  quantity: number
  unit_cost: number
  discount_percentage?: number
  discount_amount?: number
  line_total: number
  description?: string
  notes?: string
}

export interface PurchaseInvoice {
  id: number
  invoice_number: string
  supplier_invoice_number?: string
  supplier_id: number
  purchase_order_id?: number
  branch_id: number
  warehouse_id?: number
  invoice_date: string
  due_date: string
  received_date?: string
  currency_id: number
  exchange_rate?: number
  invoice_type: InvoiceTypeEnum
  status: InvoiceStatusEnum
  payment_terms: PaymentTermsEnum
  subtotal: number
  discount_percentage?: number
  discount_amount?: number
  tax_percentage?: number
  tax_amount?: number
  shipping_amount?: number
  total_amount: number
  paid_amount?: number
  notes?: string
  internal_notes?: string
  payment_method?: string
  reference_number?: string
  created_by: number
  created_at: string
  updated_at?: string
  received_at?: string
  cancelled_at?: string
  remaining_amount: number
  is_fully_paid: boolean
  is_overdue: boolean
  invoice_items: PurchaseInvoiceItem[]
  supplier?: Vendor
  currency?: Currency
  branch?: Branch
}

export interface InvoicePayment {
  id: number
  payment_number: string
  sales_invoice_id?: number
  purchase_invoice_id?: number
  invoice_type: InvoiceTypeEnum
  invoice_id: number
  payment_date: string
  amount: number
  currency_id: number
  exchange_rate?: number
  payment_method: PaymentMethodEnum
  reference_number?: string
  bank_account?: string
  check_number?: string
  check_date?: string
  notes?: string
  created_by: number
  created_at: string
  updated_at?: string
  currency?: Currency
}

export interface InvoiceSummary {
  total_sales_invoices: number
  total_purchase_invoices: number
  total_sales_amount: number
  total_purchase_amount: number
  pending_sales_amount: number
  pending_purchase_amount: number
  overdue_sales_count: number
  overdue_purchase_count: number
}

export interface InvoiceFilter {
  status?: InvoiceStatusEnum
  invoice_type?: InvoiceTypeEnum
  customer_id?: number
  supplier_id?: number
  branch_id?: number
  date_from?: string
  date_to?: string
  search?: string
}

// Type aliases for easier usage
export type SalesInvoiceStatus = keyof typeof InvoiceStatusEnum;
export type PurchaseInvoiceStatus = keyof typeof InvoiceStatusEnum;
export type InvoiceType = keyof typeof InvoiceTypeEnum;
export type PaymentTerms = keyof typeof PaymentTermsEnum;
