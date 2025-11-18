import React from 'react';
import { Link } from 'react-router-dom';
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
  Home
} from 'lucide-react';

export function DemoPage() {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  // Demo data
  const demoData = {
    financials: {
      totalReceivables: 125430.50,
      totalPayables: 89720.25,
      stockValue: 234890.75
    },
    inventory: {
      positiveItems: 1247,
      totalPieces: 15892
    },
    staff: {
      partnerSalesmen: 12,
      travelSalespersons: 8
    },
    moneyBoxes: {
      mainBox: 45230.50,
      fratAwsatVector: 12840.25,
      firstSouthVector: 8920.75,
      northVector: 15670.00,
      westVector: 9450.50,
      daylaBox: 6780.25,
      baghdadBox: 22140.75
    }
  };

  const totalCash = Object.values(demoData.moneyBoxes).reduce((sum, amount) => sum + amount, 0);

  // Navigation items
  const navigationItems = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Users', href: '/users', icon: Users },
    { name: 'HR Management', href: '/hr/users', icon: Users },
    { name: 'Sales', href: '/sales/customers', icon: ShoppingCart },
    { name: 'Inventory', href: '/inventory/items', icon: Package },
    { name: 'Accounting', href: '/accounting/chart-of-accounts', icon: Calculator },
    { name: 'POS System', href: '/pos', icon: Calculator },
    { name: 'Financial Management', href: '/financial/dashboard', icon: DollarSign },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <LayoutDashboard className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">TSH ERP System</h1>
            </div>
            <div className="text-sm text-gray-500">
              Demo Mode • Welcome Demo User
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard Content */}
        <div className="space-y-8">
          {/* Financial Overview */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="w-6 h-6 mr-2 text-green-600" />
              💰 Financial Overview
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="text-sm font-medium text-green-800 mb-2">Total Receivables</h4>
                <p className="text-2xl font-bold text-green-900">{formatCurrency(demoData.financials.totalReceivables)}</p>
                <p className="text-sm text-green-600">Amount owed to us</p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <h4 className="text-sm font-medium text-red-800 mb-2">Total Payables</h4>
                <p className="text-2xl font-bold text-red-900">{formatCurrency(demoData.financials.totalPayables)}</p>
                <p className="text-sm text-red-600">Amount we owe</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="text-sm font-medium text-blue-800 mb-2">Stock Value</h4>
                <p className="text-2xl font-bold text-blue-900">{formatCurrency(demoData.financials.stockValue)}</p>
                <p className="text-sm text-blue-600">Current inventory cost</p>
              </div>
            </div>
          </div>

          {/* Inventory Summary */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Package className="w-6 h-6 mr-2 text-purple-600" />
              📦 Inventory Summary
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <h4 className="text-sm font-medium text-purple-800 mb-2">Positive Items</h4>
                <p className="text-2xl font-bold text-purple-900">{formatNumber(demoData.inventory.positiveItems)}</p>
                <p className="text-sm text-purple-600">Items in warehouse</p>
              </div>
              <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                <h4 className="text-sm font-medium text-indigo-800 mb-2">Total Pieces</h4>
                <p className="text-2xl font-bold text-indigo-900">{formatNumber(demoData.inventory.totalPieces)}</p>
                <p className="text-sm text-indigo-600">Pieces available</p>
              </div>
            </div>
          </div>

          {/* Staff Summary */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-6 h-6 mr-2 text-orange-600" />
              👥 Staff Summary
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <h4 className="text-sm font-medium text-orange-800 mb-2">Partner Salesmen</h4>
                <p className="text-2xl font-bold text-orange-900">{demoData.staff.partnerSalesmen}</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h4 className="text-sm font-medium text-yellow-800 mb-2">Travel Salespersons</h4>
                <p className="text-2xl font-bold text-yellow-900">{demoData.staff.travelSalespersons}</p>
              </div>
            </div>
          </div>

          {/* Money Boxes */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="w-6 h-6 mr-2 text-green-600" />
              💵 Money Boxes
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-4">
              {Object.entries(demoData.moneyBoxes).map(([key, value]) => (
                <div key={key} className="bg-green-50 p-3 rounded-lg border border-green-200">
                  <h4 className="text-xs font-medium text-green-800 mb-1 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </h4>
                  <p className="text-lg font-bold text-green-900">{formatCurrency(value)}</p>
                </div>
              ))}
            </div>
            <div className="bg-green-100 p-4 rounded-lg border border-green-300">
              <h4 className="text-sm font-medium text-green-800 mb-2">Total Cash</h4>
              <p className="text-3xl font-bold text-green-900">{formatCurrency(totalCash)}</p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="w-6 h-6 mr-2 text-blue-600" />
              ⚡ Quick Actions & Navigation
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {navigationItems.map((item) => {
                const IconComponent = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="bg-blue-50 hover:bg-blue-100 p-4 rounded-lg border border-blue-200 transition-colors text-center"
                  >
                    <IconComponent className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                    <p className="text-sm font-medium text-blue-900">{item.name}</p>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
