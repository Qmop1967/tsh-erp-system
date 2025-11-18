import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Moon,
  Sun,
  Plus
} from 'lucide-react';

export function ModernERPDashboard() {
  const navigate = useNavigate();
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [activeModule, setActiveModule] = useState('dashboard');
  const [showAddItemModal, setShowAddItemModal] = useState(false);
  const [currentModalType, setCurrentModalType] = useState('');
  const [isDark, setIsDark] = useState(false);
  const [newItem, setNewItem] = useState({
    name: '',
    sku: '',
    category: '',
    price: '',
    quantity: '',
    description: ''
  });
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    password: '',
    role_id: 1,
    branch_id: 1,
    employee_code: '',
    phone: ''
  });
  const [newCustomer, setNewCustomer] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    contact_person: ''
  });

  // Theme configuration
  const lightTheme = {
    primary: '#2563eb',
    secondary: '#6b7280',
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    background: '#ffffff',
    surface: '#ffffff',
    text: '#111827',
    textSecondary: '#4b5563',
    border: '#e5e7eb',
    sidebar: '#ffffff',
    sidebarText: '#111827',
    card: '#ffffff',
    hover: '#f9fafb'
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

  // ERP Modules with icons and submenus
  const erpModules = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: LayoutDashboard,
      path: '/',
      color: 'text-blue-600'
    },
    {
      id: 'users',
      name: 'User Management',
      icon: Users,
      path: '/users',
      color: 'text-purple-600',
      subItems: [
        { name: 'All Users', path: '/users' },
        { name: 'Permissions', path: '/permissions' },
        { name: 'Roles', path: '/roles' }
      ]
    },
    {
      id: 'hr',
      name: 'Human Resources',
      icon: UserCheck,
      path: '/hr',
      color: 'text-green-600',
      subItems: [
        { name: 'Employees', path: '/hr/employees' },
        { name: 'Payroll', path: '/hr/payroll' },
        { name: 'Attendance', path: '/hr/attendance' },
        { name: 'Performance', path: '/hr/performance' }
      ]
    },
    {
      id: 'sales',
      name: 'Sales Management',
      icon: ShoppingCart,
      path: '/sales',
      color: 'text-orange-600',
      subItems: [
        { name: 'Customers', path: '/sales/customers' },
        { name: 'Sales Orders', path: '/sales/orders' },
        { name: 'Quotations', path: '/sales/quotations' },
        { name: 'Invoices', path: '/sales/invoices' },
        { name: 'Payments', path: '/sales/payments' }
      ]
    },
    {
      id: 'inventory',
      name: 'Inventory',
      icon: Package,
      path: '/inventory',
      color: 'text-indigo-600',
      subItems: [
        { name: 'Items', path: '/inventory/items' },
        { name: 'Stock Adjustments', path: '/inventory/adjustments' },
        { name: 'Warehouses', path: '/inventory/warehouses' },
        { name: 'Stock Movements', path: '/inventory/movements' }
      ]
    },
    {
      id: 'purchase',
      name: 'Purchase',
      icon: Truck,
      path: '/purchase',
      color: 'text-cyan-600',
      subItems: [
        { name: 'Vendors', path: '/purchase/vendors' },
        { name: 'Purchase Orders', path: '/purchase/orders' },
        { name: 'Receipts', path: '/purchase/receipts' }
      ]
    },
    {
      id: 'accounting',
      name: 'Accounting',
      icon: Calculator,
      path: '/accounting',
      color: 'text-emerald-600',
      subItems: [
        { name: 'Chart of Accounts', path: '/accounting/chart' },
        { name: 'Journal Entries', path: '/accounting/journal' },
        { name: 'Financial Reports', path: '/accounting/reports' },
        { name: 'Tax Management', path: '/accounting/tax' }
      ]
    },
    {
      id: 'financial',
      name: 'Financial Management',
      icon: DollarSign,
      path: '/financial',
      color: 'text-yellow-600',
      subItems: [
        { name: 'Cash Boxes', path: '/financial/cash-boxes' },
        { name: 'Bank Accounts', path: '/financial/banks' },
        { name: 'Money Transfers', path: '/financial/transfers' },
        { name: 'Digital Accounts', path: '/financial/digital' }
      ]
    },
    {
      id: 'pos',
      name: 'Point of Sale',
      icon: Monitor,
      path: '/pos',
      color: 'text-pink-600'
    },
    {
      id: 'branches',
      name: 'Branches',
      icon: Building2,
      path: '/branches',
      color: 'text-teal-600'
    },
    {
      id: 'security',
      name: 'Security',
      icon: Shield,
      path: '/security',
      color: 'text-red-600'
    },
    {
      id: 'reports',
      name: 'Reports',
      icon: BarChart3,
      path: '/reports',
      color: 'text-violet-600'
    },
    {
      id: 'settings',
      name: 'Settings',
      icon: Settings,
      path: '/settings',
      color: 'text-gray-600'
    }
  ];

  // Enhanced demo data with better integration
  const dashboardData = {
    financials: {
      totalReceivables: 125430.50,
      totalPayables: 89720.25,
      stockValue: 234890.75,
      revenue: 1500000.00,
      cashFlow: 45230.50
    },
    inventory: {
      positiveItems: 1247,
      totalPieces: 15892,
      lowStock: 23,
      stockTurnover: 4.2,
      avgItemValue: 188.35,
      fastMovingItems: 156,
      slowMovingItems: 89,
      outOfStock: 12,
      overStocked: 45
    },
    staff: {
      partnerSalesmen: 12,
      travelSalespersons: 8,
      totalEmployees: 156
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
      { type: 'sale', description: 'New sale order #SO-2025-001', time: '2 minutes ago' },
      { type: 'inventory', description: 'Stock adjustment completed', time: '15 minutes ago' },
      { type: 'payment', description: 'Payment received from Customer ABC', time: '1 hour ago' },
      { type: 'user', description: 'New user registered', time: '2 hours ago' }
    ]
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const handleAddItem = () => {
    setShowAddItemModal(true);
  };

  const handleAddNew = (itemType: string, moduleId: string) => {
    console.log(`Adding new ${itemType} for module ${moduleId}`);
    setCurrentModalType(`${moduleId}-${itemType.toLowerCase().replace(/\s+/g, '-')}`);
    setShowAddItemModal(true);
  };

  const handleSaveItem = async () => {
    console.log('Saving new item:', newItem, 'Modal type:', currentModalType);
    
    try {
      let response;
      let successMessage = '';
      
      // Determine the correct API endpoint based on modal type
      if (currentModalType.includes('inventory-items')) {
        response = await fetch('http://localhost:8889/api/inventory/items/add', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(newItem)
        });
        successMessage = `New item "${newItem.name}" added successfully!`;
      } else if (currentModalType.includes('users-all-users')) {
        response = await fetch('http://localhost:8889/api/users/', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(newUser)
        });
        successMessage = `New user "${newUser.name}" created successfully!`;
      } else if (currentModalType.includes('sales-customers')) {
        response = await fetch('http://localhost:8889/api/customers/', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(newCustomer)
        });
        successMessage = `New customer "${newCustomer.name}" created successfully!`;
      } else {
        // Fallback to inventory item creation
        response = await fetch('http://localhost:8889/api/inventory/items/add', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(newItem)
        });
        successMessage = `New item "${newItem.name}" added successfully!`;
      }
      
      if (response && response.ok) {
        const savedItem = await response.json();
        console.log('Item saved successfully:', savedItem);
        alert(successMessage);
      } else if (response) {
        const error = await response.json();
        console.error('Error response:', error);
        const errorMessage = error.detail || error.message || 'Unknown error';
        alert(`Error saving: ${errorMessage}`);
        return; // Don't close modal on error
      }
      
      // Reset form and close modal only on success
      resetForms();
      setShowAddItemModal(false);
      setCurrentModalType('');
      
    } catch (error) {
      console.error('Network error:', error);
      alert('Network error: Could not connect to server. Please check if the backend is running on port 8889.');
    }
  };

  const resetForms = () => {
    setNewItem({
      name: '',
      sku: '',
      category: '',
      price: '',
      quantity: '',
      description: ''
    });
    setNewUser({
      name: '',
      email: '',
      password: '',
      role_id: 1,
      branch_id: 1,
      employee_code: '',
      phone: ''
    });
    setNewCustomer({
      name: '',
      email: '',
      phone: '',
      address: '',
      contact_person: ''
    });
  };

  const handleCancelAdd = () => {
    setShowAddItemModal(false);
    setCurrentModalType('');
    resetForms();
  };

  const totalCash = Object.values(dashboardData.moneyBoxes).reduce((sum, amount) => sum + amount, 0);

  const getModalTitle = () => {
    if (currentModalType.includes('inventory-items')) return 'Add New Inventory Item';
    if (currentModalType.includes('users-all-users')) return 'Add New User';
    if (currentModalType.includes('sales-customers')) return 'Add New Customer';
    if (currentModalType.includes('purchase-vendors')) return 'Add New Vendor';
    if (currentModalType.includes('hr-employees')) return 'Add New Employee';
    return 'Add New Item';
  };

  const renderModalContent = () => {
    if (currentModalType.includes('users-all-users')) {
      return (
        <div style={{ display: 'grid', gap: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Full Name *
              </label>
              <input
                type="text"
                required
                value={newUser.name}
                onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                data-testid="user-name-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter full name"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Email *
              </label>
              <input
                type="email"
                required
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                data-testid="user-email-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter email"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Employee Code
              </label>
              <input
                type="text"
                value={newUser.employee_code}
                onChange={(e) => setNewUser({ ...newUser, employee_code: e.target.value })}
                data-testid="user-employee-code-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter employee code"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Phone
              </label>
              <input
                type="tel"
                value={newUser.phone}
                onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                data-testid="user-phone-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter phone number"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
              Password *
            </label>
            <input
              type="password"
              required
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              data-testid="user-password-input"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s ease'
              }}
              placeholder="Enter password"
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>
        </div>
      );
    }

    if (currentModalType.includes('sales-customers')) {
      return (
        <div style={{ display: 'grid', gap: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Customer Name *
              </label>
              <input
                type="text"
                required
                value={newCustomer.name}
                onChange={(e) => setNewCustomer({ ...newCustomer, name: e.target.value })}
                data-testid="customer-name-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter customer name"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Email
              </label>
              <input
                type="email"
                value={newCustomer.email}
                onChange={(e) => setNewCustomer({ ...newCustomer, email: e.target.value })}
                data-testid="customer-email-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter email"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Phone
              </label>
              <input
                type="tel"
                value={newCustomer.phone}
                onChange={(e) => setNewCustomer({ ...newCustomer, phone: e.target.value })}
                data-testid="customer-phone-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter phone number"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                Contact Person
              </label>
              <input
                type="text"
                value={newCustomer.contact_person}
                onChange={(e) => setNewCustomer({ ...newCustomer, contact_person: e.target.value })}
                data-testid="customer-contact-input"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Enter contact person"
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
              Address
            </label>
            <textarea
              value={newCustomer.address}
              onChange={(e) => setNewCustomer({ ...newCustomer, address: e.target.value })}
              data-testid="customer-address-input"
              rows={3}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s ease',
                resize: 'vertical'
              }}
              placeholder="Enter customer address"
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>
        </div>
      );
    }

    // Default to inventory item form
    return (
      <div style={{ display: 'grid', gap: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
              Item Name *
            </label>
            <input
              type="text"
              required
              value={newItem.name}
              onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
              data-testid="item-name-input"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s ease'
              }}
              placeholder="Enter item name"
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
              SKU *
            </label>
            <input
              type="text"
              required
              value={newItem.sku}
              onChange={(e) => setNewItem({ ...newItem, sku: e.target.value })}
              data-testid="item-sku-input"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s ease'
              }}
              placeholder="Enter SKU"
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
              Category
            </label>
            <select
              value={newItem.category}
              onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
              data-testid="item-category-select"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s ease'
              }}
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            >
              <option value="">Select Category</option>
              <option value="electronics">Electronics</option>
              <option value="clothing">Clothing</option>
              <option value="furniture">Furniture</option>
              <option value="books">Books</option>
              <option value="toys">Toys</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
              Price ($)
            </label>
            <input
              type="number"
              step="0.01"
              value={newItem.price}
              onChange={(e) => setNewItem({ ...newItem, price: e.target.value })}
              data-testid="item-price-input"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s ease'
              }}
              placeholder="0.00"
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
              Quantity
            </label>
            <input
              type="number"
              value={newItem.quantity}
              onChange={(e) => setNewItem({ ...newItem, quantity: e.target.value })}
              data-testid="item-quantity-input"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s ease'
              }}
              placeholder="0"
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
            Description
          </label>
          <textarea
            value={newItem.description}
            onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
            data-testid="item-description-input"
            rows={3}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none',
              transition: 'border-color 0.2s ease',
              resize: 'vertical'
            }}
            placeholder="Enter item description"
            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
            onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
          />
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: theme.background, fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Sidebar */}
      <div 
        style={{
          width: isSidebarOpen ? '280px' : '80px',
          backgroundColor: theme.sidebar,
          color: theme.sidebarText,
          transition: 'width 0.3s ease',
          boxShadow: '4px 0 6px -1px rgba(0, 0, 0, 0.1)',
          zIndex: 10,
          overflow: 'hidden'
        }}
      >
        {/* Sidebar Header */}
        <div style={{ padding: '20px', borderBottom: `1px solid ${theme.border}` }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                backgroundColor: '#3b82f6', 
                borderRadius: '8px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                marginRight: isSidebarOpen ? '12px' : '0'
              }}>
                <LayoutDashboard size={24} />
              </div>
              {isSidebarOpen && (
                <div>
                  <h1 style={{ fontSize: '18px', fontWeight: '700', margin: '0' }}>TSH ERP</h1>
                  <p style={{ fontSize: '12px', color: '#94a3b8', margin: '0' }}>Enterprise System</p>
                </div>
              )}
            </div>
            <button
              onClick={() => setSidebarOpen(!isSidebarOpen)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSidebarOpen(!isSidebarOpen);
                }
              }}
              data-testid="sidebar-toggle"
              aria-label="Toggle sidebar"
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                padding: '8px',
                borderRadius: '4px',
                outline: 'none'
              }}
              onFocus={(e) => {
                (e.target as HTMLElement).style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                (e.target as HTMLElement).style.boxShadow = '0 0 0 2px rgba(255, 255, 255, 0.3)';
              }}
              onBlur={(e) => {
                (e.target as HTMLElement).style.backgroundColor = 'transparent';
                (e.target as HTMLElement).style.boxShadow = 'none';
              }}
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
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setActiveModule(module.id);
                    }
                  }}
                  data-testid={`nav-${module.id}`}
                  role="button"
                  tabIndex={0}
                  aria-label={`${module.name} module`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '12px 20px',
                    cursor: 'pointer',
                    backgroundColor: isActive ? theme.primary : 'transparent',
                    borderRight: isActive ? `4px solid ${theme.primary}` : 'none',
                    transition: 'all 0.2s ease',
                    outline: 'none'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) (e.target as HTMLElement).style.backgroundColor = theme.hover;
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) (e.target as HTMLElement).style.backgroundColor = 'transparent';
                  }}
                  onFocus={(e) => {
                    if (!isActive) (e.target as HTMLElement).style.backgroundColor = theme.hover;
                    (e.target as HTMLElement).style.boxShadow = `0 0 0 2px ${theme.primary}`;
                  }}
                  onBlur={(e) => {
                    if (!isActive) (e.target as HTMLElement).style.backgroundColor = 'transparent';
                    (e.target as HTMLElement).style.boxShadow = 'none';
                  }}
                >
                  <IconComponent 
                    size={20} 
                    className={module.color}
                    style={{ color: isActive ? 'white' : theme.sidebarText, minWidth: '20px' }}
                  />
                  {isSidebarOpen && (
                    <>
                      <span style={{ 
                        marginLeft: '12px', 
                        fontSize: '14px', 
                        fontWeight: isActive ? '600' : '500',
                        color: isActive ? 'white' : theme.sidebarText
                      }}>
                        {module.name}
                      </span>
                      {module.subItems && (
                        <ChevronRight 
                          size={16} 
                          style={{ 
                            marginLeft: 'auto', 
                            color: isActive ? 'white' : theme.sidebarText 
                          }} 
                        />
                      )}
                    </>
                  )}
                </div>
                
                {/* Submenu */}
                {isSidebarOpen && module.subItems && isActive && (
                  <div style={{ 
                    backgroundColor: isDark ? '#1e293b' : '#f8fafc',
                    borderLeft: `3px solid ${theme.primary}`,
                    marginLeft: '20px',
                    marginRight: '20px',
                    borderRadius: '6px',
                    marginBottom: '8px',
                    boxShadow: isDark ? 'none' : '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                  }}>
                    {module.subItems.map((subItem, index) => (
                      <div
                        key={index}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '10px 16px',
                          fontSize: '13px',
                          color: isDark ? '#94a3b8' : '#374151',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          borderRadius: '4px',
                          margin: '2px 4px',
                          outline: 'none'
                        }}
                        onMouseEnter={(e) => {
                          (e.target as HTMLElement).style.backgroundColor = isDark ? '#334155' : '#e2e8f0';
                          (e.target as HTMLElement).style.color = isDark ? '#f1f5f9' : '#1e293b';
                        }}
                        onMouseLeave={(e) => {
                          (e.target as HTMLElement).style.backgroundColor = 'transparent';
                          (e.target as HTMLElement).style.color = isDark ? '#94a3b8' : '#374151';
                        }}
                      >
                        <span
                          onClick={() => {
                            console.log(`Navigating to: ${subItem.name} (${subItem.path})`);
                            navigate(subItem.path);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              console.log(`Navigating to: ${subItem.name} (${subItem.path})`);
                              navigate(subItem.path);
                            }
                          }}
                          role="button"
                          tabIndex={0}
                          aria-label={`Navigate to ${subItem.name}`}
                          data-testid={`submenu-${subItem.name.toLowerCase().replace(/\s+/g, '-')}`}
                          style={{ flex: 1 }}
                        >
                          {subItem.name}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAddNew(subItem.name, module.id);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              e.stopPropagation();
                              handleAddNew(subItem.name, module.id);
                            }
                          }}
                          aria-label={`Add new ${subItem.name}`}
                          data-testid={`add-${subItem.name.toLowerCase().replace(/\s+/g, '-')}`}
                          style={{
                            background: 'none',
                            border: 'none',
                            padding: '4px',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            color: theme.primary,
                            transition: 'all 0.2s ease',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                          onMouseEnter={(e) => {
                            (e.target as HTMLElement).style.backgroundColor = theme.primary;
                            (e.target as HTMLElement).style.color = 'white';
                          }}
                          onMouseLeave={(e) => {
                            (e.target as HTMLElement).style.backgroundColor = 'transparent';
                            (e.target as HTMLElement).style.color = theme.primary;
                          }}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* User Profile */}
        {isSidebarOpen && (
          <div style={{ padding: '20px', borderTop: '1px solid #334155' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: '36px', 
                height: '36px', 
                backgroundColor: '#3b82f6', 
                borderRadius: '50%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                marginRight: '12px'
              }}>
                <User size={18} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '14px', fontWeight: '600', margin: '0', color: theme.sidebarText }}>Demo User</p>
                <p style={{ fontSize: '12px', color: theme.textSecondary, margin: '0' }}>Administrator</p>
              </div>
              <LogOut size={18} style={{ color: theme.textSecondary, cursor: 'pointer' }} />
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top Header */}
        <header style={{ 
          backgroundColor: theme.card, 
          padding: '16px 32px', 
          borderBottom: `1px solid ${theme.border}`,
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between' }}>
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: '700', color: theme.text, margin: '0' }} data-testid="page-title">
                {erpModules.find(m => m.id === activeModule)?.name || 'Dashboard'}
              </h1>
              <p style={{ fontSize: '14px', color: theme.textSecondary, margin: '4px 0 0 0' }}>
                Welcome back! Here's what's happening with your business today.
              </p>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
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
                  data-testid="global-search"
                  aria-label="Global search"
                  style={{
                    padding: '8px 12px 8px 40px',
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    fontSize: '14px',
                    width: '300px',
                    outline: 'none',
                    backgroundColor: theme.card,
                    color: theme.text,
                    transition: 'border-color 0.2s ease'
                  }}
                  onFocus={(e) => e.target.style.borderColor = theme.primary}
                  onBlur={(e) => e.target.style.borderColor = theme.border}
                />
              </div>
              
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleTheme();
                  }
                }}
                data-testid="theme-toggle"
                aria-label="Toggle theme"
                style={{
                  background: 'none',
                  border: `1px solid ${theme.border}`,
                  borderRadius: '8px',
                  padding: '8px',
                  cursor: 'pointer',
                  color: theme.textSecondary,
                  transition: 'all 0.2s ease',
                  outline: 'none'
                }}
                onFocus={(e) => {
                  (e.target as HTMLElement).style.borderColor = theme.primary;
                  (e.target as HTMLElement).style.boxShadow = `0 0 0 2px ${theme.primary}`;
                }}
                onBlur={(e) => {
                  (e.target as HTMLElement).style.borderColor = theme.border;
                  (e.target as HTMLElement).style.boxShadow = 'none';
                }}
              >
                {isDark ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              
              <div style={{ position: 'relative' }}>
                <Bell size={20} style={{ color: theme.textSecondary, cursor: 'pointer' }} />
                <div style={{ 
                  position: 'absolute', 
                  top: '-2px', 
                  right: '-2px', 
                  width: '8px', 
                  height: '8px', 
                  backgroundColor: theme.error, 
                  borderRadius: '50%' 
                }}></div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main style={{ 
          flex: 1, 
          padding: '32px', 
          backgroundColor: theme.surface, 
          overflowY: 'auto' 
        }}>
          {activeModule === 'dashboard' ? (
            <div style={{ display: 'grid', gap: '24px' }}>
              {/* Key Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Total Revenue</h3>
                    <TrendingUp size={20} style={{ color: theme.success }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {formatCurrency(dashboardData.financials.revenue)}
                  </p>
                  <p style={{ fontSize: '14px', color: '#10b981', margin: '8px 0 0 0' }}>+12.5% from last month</p>
                </div>

                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Total Employees</h3>
                    <Users size={20} style={{ color: '#3b82f6' }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {dashboardData.staff.totalEmployees}
                  </p>
                  <p style={{ fontSize: '14px', color: '#3b82f6', margin: '8px 0 0 0' }}>+3 new this month</p>
                </div>

                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }} data-testid="dashboard-inventory-items">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Inventory Items</h3>
                    <Package size={20} style={{ color: '#8b5cf6' }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {formatNumber(dashboardData.inventory.positiveItems)}
                  </p>
                  <p style={{ fontSize: '14px', color: '#f59e0b', margin: '8px 0 0 0' }}>
                    {dashboardData.inventory.lowStock} low stock • {dashboardData.inventory.outOfStock} out of stock
                  </p>
                </div>

                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Total Cash</h3>
                    <DollarSign size={20} style={{ color: '#10b981' }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {formatCurrency(totalCash)}
                  </p>
                  <p style={{ fontSize: '14px', color: '#10b981', margin: '8px 0 0 0' }}>Across all money boxes</p>
                </div>
              </div>

              {/* Financial Overview */}
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>💰 Financial Overview</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                  <div style={{ backgroundColor: '#ecfdf5', padding: '20px', borderRadius: '8px', border: '1px solid #d1fae5' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#065f46', margin: '0 0 8px 0' }}>Total Receivables</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#047857', margin: '0' }}>
                      {formatCurrency(dashboardData.financials.totalReceivables)}
                    </p>
                    <p style={{ fontSize: '12px', color: '#059669', margin: '4px 0 0 0' }}>Amount owed to us</p>
                  </div>
                  
                  <div style={{ backgroundColor: '#fef2f2', padding: '20px', borderRadius: '8px', border: '1px solid #fecaca' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#7f1d1d', margin: '0 0 8px 0' }}>Total Payables</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#dc2626', margin: '0' }}>
                      {formatCurrency(dashboardData.financials.totalPayables)}
                    </p>
                    <p style={{ fontSize: '12px', color: '#ef4444', margin: '4px 0 0 0' }}>Amount we owe</p>
                  </div>
                  
                  <div style={{ backgroundColor: '#eff6ff', padding: '20px', borderRadius: '8px', border: '1px solid #bfdbfe' }} data-testid="dashboard-stock-value">
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af', margin: '0 0 8px 0' }}>Stock Value</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#2563eb', margin: '0' }}>
                      {formatCurrency(dashboardData.financials.stockValue)}
                    </p>
                    <p style={{ fontSize: '12px', color: '#3b82f6', margin: '4px 0 0 0' }}>
                      {formatNumber(dashboardData.inventory.positiveItems)} items • {formatNumber(dashboardData.inventory.totalPieces)} pieces
                    </p>
                  </div>
                </div>
              </div>

              {/* Money Boxes */}
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>💵 Money Boxes</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                  {Object.entries(dashboardData.moneyBoxes).map(([key, value]) => (
                    <div key={key} style={{ backgroundColor: '#f0fdf4', padding: '16px', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
                      <h4 style={{ fontSize: '12px', fontWeight: '600', color: '#166534', margin: '0 0 8px 0', textTransform: 'capitalize' }}>
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </h4>
                      <p style={{ fontSize: '20px', fontWeight: '700', color: '#15803d', margin: '0' }}>
                        {formatCurrency(value)}
                      </p>
                    </div>
                  ))}
                </div>
                <div style={{ backgroundColor: '#dcfce7', padding: '20px', borderRadius: '8px', border: '2px solid #16a34a' }}>
                  <h4 style={{ fontSize: '16px', fontWeight: '700', color: '#166534', margin: '0 0 8px 0' }}>Total Cash Flow</h4>
                  <p style={{ fontSize: '32px', fontWeight: '800', color: '#15803d', margin: '0' }}>
                    {formatCurrency(totalCash)}
                  </p>
                </div>
              </div>

              {/* Recent Activity */}
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>📈 Recent Activity</h3>
                <div style={{ marginTop: '16px' }}>
                  {dashboardData.recentActivity.map((activity, index) => (
                    <div key={index} style={{ display: 'flex', alignItems: 'center', padding: '16px 0', borderBottom: index < dashboardData.recentActivity.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                      <div style={{ 
                        width: '40px', 
                        height: '40px', 
                        backgroundColor: '#eff6ff', 
                        borderRadius: '50%', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        marginRight: '16px'
                      }}>
                        <BarChart3 size={18} style={{ color: '#3b82f6' }} />
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
                  ))}
                </div>
              </div>
            </div>
          ) : activeModule === 'inventory' ? (
            // Enhanced Inventory Module
            <div style={{ display: 'grid', gap: '24px' }}>
              {/* Inventory Overview Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }} data-testid="inventory-total-items">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Total Items</h3>
                    <Package size={20} style={{ color: '#8b5cf6' }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {formatNumber(dashboardData.inventory.positiveItems)}
                  </p>
                  <p style={{ fontSize: '14px', color: '#8b5cf6', margin: '8px 0 0 0' }}>
                    Total pieces: {formatNumber(dashboardData.inventory.totalPieces)}
                  </p>
                </div>

                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }} data-testid="inventory-stock-value">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Stock Value</h3>
                    <DollarSign size={20} style={{ color: '#10b981' }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {formatCurrency(dashboardData.financials.stockValue)}
                  </p>
                  <p style={{ fontSize: '14px', color: '#10b981', margin: '8px 0 0 0' }}>
                    Avg. value per item: {formatCurrency(dashboardData.inventory.avgItemValue)}
                  </p>
                </div>

                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }} data-testid="inventory-stock-alerts">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Stock Alerts</h3>
                    <TrendingUp size={20} style={{ color: '#f59e0b' }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {dashboardData.inventory.lowStock}
                  </p>
                  <p style={{ fontSize: '14px', color: '#f59e0b', margin: '8px 0 0 0' }}>
                    Items need reorder | {dashboardData.inventory.outOfStock} out of stock
                  </p>
                </div>

                <div style={{ backgroundColor: theme.card, padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }} data-testid="inventory-turnover">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: theme.textSecondary, margin: '0' }}>Stock Turnover</h3>
                    <BarChart3 size={20} style={{ color: '#3b82f6' }} />
                  </div>
                  <p style={{ fontSize: '32px', fontWeight: '700', color: theme.text, margin: '0' }}>
                    {dashboardData.inventory.stockTurnover}x
                  </p>
                  <p style={{ fontSize: '14px', color: '#3b82f6', margin: '8px 0 0 0' }}>
                    Annual turnover ratio
                  </p>
                </div>
              </div>

              {/* Inventory Categories */}
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>📦 Inventory Categories</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                  <div style={{ backgroundColor: '#f0f9ff', padding: '20px', borderRadius: '8px', border: '1px solid #bfdbfe' }} data-testid="fast-moving-items">
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af', margin: '0 0 8px 0' }}>Fast Moving Items</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#2563eb', margin: '0' }}>
                      {dashboardData.inventory.fastMovingItems}
                    </p>
                    <p style={{ fontSize: '12px', color: '#3b82f6', margin: '4px 0 0 0' }}>High demand products</p>
                  </div>
                  
                  <div style={{ backgroundColor: '#fef3c7', padding: '20px', borderRadius: '8px', border: '1px solid #fcd34d' }} data-testid="slow-moving-items">
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#92400e', margin: '0 0 8px 0' }}>Slow Moving Items</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#d97706', margin: '0' }}>
                      {dashboardData.inventory.slowMovingItems}
                    </p>
                    <p style={{ fontSize: '12px', color: '#f59e0b', margin: '4px 0 0 0' }}>Need attention</p>
                  </div>
                  
                  <div style={{ backgroundColor: '#fef2f2', padding: '20px', borderRadius: '8px', border: '1px solid #fecaca' }} data-testid="overstocked-items">
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#7f1d1d', margin: '0 0 8px 0' }}>Overstocked Items</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#dc2626', margin: '0' }}>
                      {dashboardData.inventory.overStocked}
                    </p>
                    <p style={{ fontSize: '12px', color: '#ef4444', margin: '4px 0 0 0' }}>Excess inventory</p>
                  </div>
                </div>
              </div>

              {/* Inventory Management Actions */}
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>🔧 Inventory Management</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }} data-testid="inventory-features">
                  {[
                    { name: 'Add New Item', icon: Package, color: '#3b82f6', action: handleAddItem },
                    { name: 'Stock Adjustment', icon: Calculator, color: '#8b5cf6', action: () => alert('Stock Adjustment feature coming soon!') },
                    { name: 'Generate Report', icon: BarChart3, color: '#10b981', action: () => alert('Generate Report feature coming soon!') },
                    { name: 'Warehouse View', icon: Building2, color: '#f59e0b', action: () => alert('Warehouse View feature coming soon!') },
                    { name: 'Stock Movement', icon: TrendingUp, color: '#ef4444', action: () => alert('Stock Movement feature coming soon!') }
                  ].map((feature, index) => (
                    <button 
                      key={index}
                      onClick={feature.action}
                      data-testid={`inventory-${feature.name.toLowerCase().replace(/\s+/g, '-')}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '16px',
                        backgroundColor: theme.card,
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        fontSize: '14px',
                        fontWeight: '500'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#f8fafc';
                        e.currentTarget.style.borderColor = feature.color;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'white';
                        e.currentTarget.style.borderColor = '#e2e8f0';
                      }}
                    >
                      <feature.icon size={20} style={{ color: feature.color, marginRight: '12px' }} />
                      {feature.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Inventory Integration Notice */}
              <div style={{ backgroundColor: '#eff6ff', padding: '24px', borderRadius: '12px', border: '1px solid #bfdbfe' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                  <Package size={24} style={{ color: '#2563eb', marginRight: '12px' }} />
                  <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1e40af', margin: '0' }}>
                    Dashboard Integration Active
                  </h4>
                </div>
                <p style={{ fontSize: '14px', color: '#1e40af', margin: '0', lineHeight: '1.5' }}>
                  This inventory module is fully integrated with the main dashboard. Stock values, item counts, 
                  and alerts are automatically synchronized and reflected in the Financial Overview and key metrics.
                </p>
              </div>
            </div>
          ) : activeModule === 'users' ? (
            // Users Management Module
            <div style={{ display: 'grid', gap: '24px' }}>
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>👥 User Management</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                  <div style={{ backgroundColor: '#f0f9ff', padding: '20px', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af', margin: '0 0 8px 0' }}>Total Users</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#2563eb', margin: '0' }}>156</p>
                    <p style={{ fontSize: '12px', color: '#3b82f6', margin: '4px 0 0 0' }}>Active system users</p>
                  </div>
                  <div style={{ backgroundColor: '#ecfdf5', padding: '20px', borderRadius: '8px', border: '1px solid #d1fae5' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#065f46', margin: '0 0 8px 0' }}>Active Roles</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#047857', margin: '0' }}>8</p>
                    <p style={{ fontSize: '12px', color: '#059669', margin: '4px 0 0 0' }}>Admin, Manager, Sales, etc.</p>
                  </div>
                  <div style={{ backgroundColor: '#fef3c7', padding: '20px', borderRadius: '8px', border: '1px solid #fcd34d' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#92400e', margin: '0 0 8px 0' }}>Pending Approvals</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#d97706', margin: '0' }}>3</p>
                    <p style={{ fontSize: '12px', color: '#f59e0b', margin: '4px 0 0 0' }}>New user requests</p>
                  </div>
                </div>
              </div>
            </div>
          ) : activeModule === 'sales' ? (
            // Sales Management Module
            <div style={{ display: 'grid', gap: '24px' }}>
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>🛒 Sales Management</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                  <div style={{ backgroundColor: '#ecfdf5', padding: '20px', borderRadius: '8px', border: '1px solid #d1fae5' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#065f46', margin: '0 0 8px 0' }}>Total Orders</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#047857', margin: '0' }}>1,247</p>
                    <p style={{ fontSize: '12px', color: '#059669', margin: '4px 0 0 0' }}>This month</p>
                  </div>
                  <div style={{ backgroundColor: '#f0f9ff', padding: '20px', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af', margin: '0 0 8px 0' }}>Active Customers</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#2563eb', margin: '0' }}>892</p>
                    <p style={{ fontSize: '12px', color: '#3b82f6', margin: '4px 0 0 0' }}>Registered customers</p>
                  </div>
                  <div style={{ backgroundColor: '#fef3c7', padding: '20px', borderRadius: '8px', border: '1px solid #fcd34d' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#92400e', margin: '0 0 8px 0' }}>Pending Orders</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#d97706', margin: '0' }}>23</p>
                    <p style={{ fontSize: '12px', color: '#f59e0b', margin: '4px 0 0 0' }}>Need processing</p>
                  </div>
                </div>
              </div>
            </div>
          ) : activeModule === 'financial' ? (
            // Financial Management Module
            <div style={{ display: 'grid', gap: '24px' }}>
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>💰 Financial Management</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                  <div style={{ backgroundColor: '#ecfdf5', padding: '20px', borderRadius: '8px', border: '1px solid #d1fae5' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#065f46', margin: '0 0 8px 0' }}>Total Revenue</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#047857', margin: '0' }}>${formatNumber(dashboardData.financials.revenue)}</p>
                    <p style={{ fontSize: '12px', color: '#059669', margin: '4px 0 0 0' }}>This year</p>
                  </div>
                  <div style={{ backgroundColor: '#f0f9ff', padding: '20px', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af', margin: '0 0 8px 0' }}>Cash Flow</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#2563eb', margin: '0' }}>{formatCurrency(totalCash)}</p>
                    <p style={{ fontSize: '12px', color: '#3b82f6', margin: '4px 0 0 0' }}>Available cash</p>
                  </div>
                  <div style={{ backgroundColor: '#fef2f2', padding: '20px', borderRadius: '8px', border: '1px solid #fecaca' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#7f1d1d', margin: '0 0 8px 0' }}>Outstanding</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#dc2626', margin: '0' }}>{formatCurrency(dashboardData.financials.totalPayables)}</p>
                    <p style={{ fontSize: '12px', color: '#ef4444', margin: '4px 0 0 0' }}>Amount owed</p>
                  </div>
                </div>
              </div>
            </div>
          ) : activeModule === 'hr' ? (
            // HR Module
            <div style={{ display: 'grid', gap: '24px' }}>
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '700', color: theme.text, marginBottom: '24px' }}>👔 Human Resources</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                  <div style={{ backgroundColor: '#f0f9ff', padding: '20px', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af', margin: '0 0 8px 0' }}>Total Employees</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#2563eb', margin: '0' }}>{dashboardData.staff.totalEmployees}</p>
                    <p style={{ fontSize: '12px', color: '#3b82f6', margin: '4px 0 0 0' }}>Active staff</p>
                  </div>
                  <div style={{ backgroundColor: '#ecfdf5', padding: '20px', borderRadius: '8px', border: '1px solid #d1fae5' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#065f46', margin: '0 0 8px 0' }}>Salespeople</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#047857', margin: '0' }}>{dashboardData.staff.partnerSalesmen + dashboardData.staff.travelSalespersons}</p>
                    <p style={{ fontSize: '12px', color: '#059669', margin: '4px 0 0 0' }}>Partners & Travel</p>
                  </div>
                  <div style={{ backgroundColor: '#fef3c7', padding: '20px', borderRadius: '8px', border: '1px solid #fcd34d' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#92400e', margin: '0 0 8px 0' }}>Departments</h4>
                    <p style={{ fontSize: '24px', fontWeight: '700', color: '#d97706', margin: '0' }}>12</p>
                    <p style={{ fontSize: '12px', color: '#f59e0b', margin: '4px 0 0 0' }}>Active departments</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Generic module content for remaining modules
            <div style={{ display: 'grid', gap: '24px' }}>
              <div style={{ backgroundColor: theme.card, padding: '32px', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                  <div style={{ 
                    width: '64px', 
                    height: '64px', 
                    backgroundColor: '#eff6ff', 
                    borderRadius: '50%', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    margin: '0 auto 16px'
                  }}>
                    {React.createElement(erpModules.find(m => m.id === activeModule)?.icon || Package, { 
                      size: 32, 
                      color: '#3b82f6' 
                    })}
                  </div>
                  <h2 style={{ fontSize: '24px', fontWeight: '700', color: theme.text, margin: '0 0 8px 0' }}>
                    {erpModules.find(m => m.id === activeModule)?.name}
                  </h2>
                  <p style={{ fontSize: '16px', color: theme.textSecondary, margin: '0 0 24px 0' }}>
                    Module interface is ready for customization and development.
                  </p>
                </div>
                
                {/* Generic module features */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '32px' }}>
                  <div style={{ backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: theme.text, margin: '0 0 8px 0' }}>Status</h4>
                    <p style={{ fontSize: '20px', fontWeight: '700', color: '#059669', margin: '0' }}>Ready</p>
                    <p style={{ fontSize: '12px', color: theme.textSecondary, margin: '4px 0 0 0' }}>Module structure available</p>
                  </div>
                  <div style={{ backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: theme.text, margin: '0 0 8px 0' }}>Navigation</h4>
                    <p style={{ fontSize: '20px', fontWeight: '700', color: '#3b82f6', margin: '0' }}>Active</p>
                    <p style={{ fontSize: '12px', color: theme.textSecondary, margin: '4px 0 0 0' }}>Keyboard & mouse support</p>
                  </div>
                  <div style={{ backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: '600', color: theme.text, margin: '0 0 8px 0' }}>Integration</h4>
                    <p style={{ fontSize: '20px', fontWeight: '700', color: '#8b5cf6', margin: '0' }}>Available</p>
                    <p style={{ fontSize: '12px', color: theme.textSecondary, margin: '4px 0 0 0' }}>API endpoints ready</p>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                  <button 
                    style={{
                      backgroundColor: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      padding: '12px 24px',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                    onClick={() => setActiveModule('dashboard')}
                  >
                    Go to Dashboard
                  </button>
                  <button 
                    style={{
                      backgroundColor: theme.card,
                      color: '#3b82f6',
                      border: '1px solid #3b82f6',
                      padding: '12px 24px',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                    onClick={() => setActiveModule('inventory')}
                  >
                    View Inventory
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Dynamic Add Item Modal */}
      {showAddItemModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          data-testid="add-item-modal"
        >
          <div 
            style={{
              backgroundColor: theme.card,
              borderRadius: '12px',
              padding: '32px',
              width: '90%',
              maxWidth: '600px',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '24px', fontWeight: '700', color: theme.text, margin: '0' }}>
                {getModalTitle()}
              </h2>
              <button
                onClick={handleCancelAdd}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: theme.textSecondary
                }}
                data-testid="close-modal"
              >
                ✕
              </button>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); handleSaveItem(); }}>
              {renderModalContent()}

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
                <button
                  type="button"
                  onClick={handleCancelAdd}
                  data-testid="cancel-add-item"
                  style={{
                    padding: '12px 24px',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    backgroundColor: theme.card,
                    color: '#374151',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f9fafb';
                    e.currentTarget.style.borderColor = '#9ca3af';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = '#d1d5db';
                  }}
                >
                  Cancel
                </button>
                
                <button
                  type="submit"
                  data-testid="save-add-item"
                  style={{
                    padding: '12px 24px',
                    border: 'none',
                    borderRadius: '8px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#2563eb';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#3b82f6';
                  }}
                >
                  {currentModalType.includes('users') ? 'Create User' : 
                   currentModalType.includes('customers') ? 'Add Customer' : 
                   'Add Item'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
