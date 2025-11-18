import React, { useState } from 'react'
import {
  TrendingUp,
  TrendingDown,
  Package,
  Users,
  Wallet,
  ShoppingCart,
  Receipt,
  CheckCircle
} from 'lucide-react'

interface DashboardStats {
  receivableAccounts: number
  payableAccounts: number
  currentStockValue: number
  positiveStockItems: number
  totalPieces: number
  partnerSalesman: number
  travelSalesperson: number
  moneyBoxes: {
    main: number
    fratAwsatVector: number
    firstSouthVector: number
    northVector: number
    westVector: number
    dayla: number
    baghdad: number
  }
}

interface StatCard {
  title: string
  value: string | number
  icon: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  color: string
}

const DashboardPage: React.FC = () => {
  // Initialize with mock data for demonstration
  const [stats] = useState<DashboardStats>({
    receivableAccounts: 125430.50,
    payableAccounts: 89250.75,
    currentStockValue: 450000.00,
    positiveStockItems: 1245,
    totalPieces: 15670,
    partnerSalesman: 12,
    travelSalesperson: 8,
    moneyBoxes: {
      main: 75000.00,
      fratAwsatVector: 25000.00,
      firstSouthVector: 18500.00,
      northVector: 32000.00,
      westVector: 15000.00,
      dayla: 22000.00,
      baghdad: 28000.00
    }
  })

  // Future: Replace with actual API call
  // const { data, isLoading, error } = useQuery(
  //   'dashboard-stats',
  //   () => dashboardApi.getStats(),
  //   { refetchInterval: 30000 }
  // )

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num)
  }

  const mainStats: StatCard[] = [
    {
      title: 'Total Receivable Accounts',
      value: formatCurrency(stats.receivableAccounts),
      icon: <TrendingUp className="w-6 h-6" />,
      trend: { value: 12.5, isPositive: true },
      color: 'bg-green-500'
    },
    {
      title: 'Total Payable Accounts',
      value: formatCurrency(stats.payableAccounts),
      icon: <TrendingDown className="w-6 h-6" />,
      trend: { value: 8.2, isPositive: false },
      color: 'bg-red-500'
    },
    {
      title: 'Current Stock Value',
      value: formatCurrency(stats.currentStockValue),
      icon: <Package className="w-6 h-6" />,
      trend: { value: 5.7, isPositive: true },
      color: 'bg-blue-500'
    },
    {
      title: 'Positive Stock Items',
      value: formatNumber(stats.positiveStockItems),
      icon: <CheckCircle className="w-6 h-6" />,
      trend: { value: 3.1, isPositive: true },
      color: 'bg-purple-500'
    },
    {
      title: 'Total Pieces in Stock',
      value: formatNumber(stats.totalPieces),
      icon: <Package className="w-6 h-6" />,
      trend: { value: 7.8, isPositive: true },
      color: 'bg-indigo-500'
    },
    {
      title: 'Partner Salesman',
      value: stats.partnerSalesman,
      icon: <Users className="w-6 h-6" />,
      color: 'bg-orange-500'
    },
    {
      title: 'Travel Salesperson',
      value: stats.travelSalesperson,
      icon: <Users className="w-6 h-6" />,
      color: 'bg-teal-500'
    }
  ]

  const moneyBoxData = [
    { name: 'Main Money Box', amount: stats.moneyBoxes.main, color: 'bg-gradient-to-r from-blue-500 to-blue-600' },
    { name: 'Frat Awsat Vector Money Box', amount: stats.moneyBoxes.fratAwsatVector, color: 'bg-gradient-to-r from-green-500 to-green-600' },
    { name: 'First South Vector Money Box', amount: stats.moneyBoxes.firstSouthVector, color: 'bg-gradient-to-r from-purple-500 to-purple-600' },
    { name: 'North Vector Money Box', amount: stats.moneyBoxes.northVector, color: 'bg-gradient-to-r from-red-500 to-red-600' },
    { name: 'West Vector Money Box', amount: stats.moneyBoxes.westVector, color: 'bg-gradient-to-r from-yellow-500 to-yellow-600' },
    { name: 'Dayla Money Box', amount: stats.moneyBoxes.dayla, color: 'bg-gradient-to-r from-indigo-500 to-indigo-600' },
    { name: 'Baghdad Money Box', amount: stats.moneyBoxes.baghdad, color: 'bg-gradient-to-r from-pink-500 to-pink-600' }
  ]

  // Note: isLoading would come from useQuery when API is connected
  const isLoading = false; // Temporary fix for demo
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading dashboard...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">TSH ERP Dashboard</h1>
            <p className="text-gray-600 mt-2">Overview of your business performance</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Last updated</p>
            <p className="text-lg font-semibold text-gray-900">{new Date().toLocaleTimeString()}</p>
          </div>
        </div>
      </div>

      {/* Main Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {mainStats.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                {stat.trend && (
                  <div className="flex items-center mt-2">
                    <span className={`text-sm font-medium ${stat.trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                      {stat.trend.isPositive ? '+' : '-'}{stat.trend.value}%
                    </span>
                    <span className="text-xs text-gray-500 ml-1">vs last month</span>
                  </div>
                )}
              </div>
              <div className={`${stat.color} p-3 rounded-lg text-white`}>
                {stat.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Money Boxes Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center mb-6">
          <Wallet className="w-6 h-6 text-blue-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">Money Boxes Overview</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {moneyBoxData.map((box, index) => (
            <div key={index} className={`${box.color} rounded-lg p-6 text-white relative overflow-hidden`}>
              <div className="relative z-10">
                <h3 className="text-lg font-semibold mb-2">{box.name}</h3>
                <p className="text-3xl font-bold">{formatCurrency(box.amount)}</p>
              </div>
              <div className="absolute top-0 right-0 p-4 opacity-20">
                <Wallet className="w-12 h-12" />
              </div>
            </div>
          ))}
        </div>

        {/* Total Money Box Value */}
        <div className="mt-6 bg-gray-50 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Total Money Box Value</h3>
              <p className="text-sm text-gray-600">Sum of all money boxes</p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-gray-900">
                {formatCurrency(Object.values(stats.moneyBoxes).reduce((sum, value) => sum + value, 0))}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex items-center p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
            <ShoppingCart className="w-6 h-6 text-blue-600 mr-3" />
            <span className="font-medium text-blue-700">New Sale Order</span>
          </button>
          <button className="flex items-center p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors">
            <Receipt className="w-6 h-6 text-green-600 mr-3" />
            <span className="font-medium text-green-700">Create Invoice</span>
          </button>
          <button className="flex items-center p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors">
            <Package className="w-6 h-6 text-purple-600 mr-3" />
            <span className="font-medium text-purple-700">Add Product</span>
          </button>
          <button className="flex items-center p-4 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors">
            <Users className="w-6 h-6 text-orange-600 mr-3" />
            <span className="font-medium text-orange-700">Add Customer</span>
          </button>
        </div>
      </div>

      {/* System Status - Future implementation */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center">
          <CheckCircle className="w-5 h-5 text-blue-600 mr-2" />
          <span className="text-blue-700">All systems operational. Data is up to date.</span>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
