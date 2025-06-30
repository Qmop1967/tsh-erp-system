import React from 'react'
import { Routes, Route } from 'react-router-dom'
import NewLayout from './components/layout/NewLayout'
import { useDashboardData } from './hooks/useDashboardData'
import { useLanguageStore } from './stores/languageStore'
import { useTranslations } from './lib/translations'

// Simple test components
function TestDashboard() {
  const { data, loading, error, refetch } = useDashboardData()
  const { language } = useLanguageStore()
  const t = useTranslations(language)

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

      {/* Financial Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-lg shadow-lg text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">💰 {t.totalReceivables}</h3>
              <p className="text-3xl font-bold">{formatCurrency(data.financials.totalReceivables)}</p>
              <p className="text-blue-100 text-sm mt-1">{t.amountOwedToUs}</p>
            </div>
            <div className="text-4xl opacity-80">📈</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-red-500 to-red-600 p-6 rounded-lg shadow-lg text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">💸 {t.totalPayables}</h3>
              <p className="text-3xl font-bold">{formatCurrency(data.financials.totalPayables)}</p>
              <p className="text-red-100 text-sm mt-1">{t.amountWeOwe}</p>
            </div>
            <div className="text-4xl opacity-80">📉</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-lg shadow-lg text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">📦 {t.stockValueCost}</h3>
              <p className="text-3xl font-bold">{formatCurrency(data.financials.stockValue)}</p>
              <p className="text-green-100 text-sm mt-1">{t.currentInventoryCost}</p>
            </div>
            <div className="text-4xl opacity-80">📊</div>
          </div>
        </div>
      </div>

      {/* Inventory Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-xl font-semibold text-purple-600 mb-4">📋 {t.inventorySummary}</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">{t.positiveItemsInWarehouse}:</span>
              <span className="text-2xl font-bold text-purple-600">{formatNumber(data.inventory.positiveItems)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">{t.totalPiecesAvailable}:</span>
              <span className="text-2xl font-bold text-purple-600">{formatNumber(data.inventory.totalPieces)}</span>
            </div>
          </div>
        </div>

        {/* Staff Summary */}
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-xl font-semibold text-indigo-600 mb-4">👥 {t.staffSummary}</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">{t.partnerSalesmen}:</span>
              <span className="text-2xl font-bold text-indigo-600">{formatNumber(data.staff.partnerSalesmen)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">{t.travelSalespersons}:</span>
              <span className="text-2xl font-bold text-indigo-600">{formatNumber(data.staff.travelSalespersons)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Money Boxes */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">💼 {t.moneyBoxes}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-r from-yellow-400 to-yellow-500 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">🏦 {t.mainMoneyBox}</h4>
            <p className="text-2xl font-bold">{formatCurrency(data.moneyBoxes.mainBox)}</p>
            <p className="text-yellow-100 text-sm">{t.primaryCashFlow}</p>
          </div>
          
          <div className="bg-gradient-to-r from-orange-400 to-orange-500 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">🌅 {t.fratAwsatVector}</h4>
            <p className="text-2xl font-bold">{formatCurrency(data.moneyBoxes.fratAwsatVector)}</p>
            <p className="text-orange-100 text-sm">{t.centralRegion}</p>
          </div>
          
          <div className="bg-gradient-to-r from-teal-400 to-teal-500 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">🌄 {t.firstSouthVector}</h4>
            <p className="text-2xl font-bold">{formatCurrency(data.moneyBoxes.firstSouthVector)}</p>
            <p className="text-teal-100 text-sm">{t.southernRegion}</p>
          </div>
          
          <div className="bg-gradient-to-r from-blue-400 to-blue-500 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">❄️ {t.northVector}</h4>
            <p className="text-2xl font-bold">{formatCurrency(data.moneyBoxes.northVector)}</p>
            <p className="text-blue-100 text-sm">{t.northernRegion}</p>
          </div>
          
          <div className="bg-gradient-to-r from-purple-400 to-purple-500 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">🌅 {t.westVector}</h4>
            <p className="text-2xl font-bold">{formatCurrency(data.moneyBoxes.westVector)}</p>
            <p className="text-purple-100 text-sm">{t.westernRegion}</p>
          </div>
          
          <div className="bg-gradient-to-r from-pink-400 to-pink-500 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">🌸 {t.daylaMoneyBox}</h4>
            <p className="text-2xl font-bold">{formatCurrency(data.moneyBoxes.daylaBox)}</p>
            <p className="text-pink-100 text-sm">{t.daylaOperations}</p>
          </div>
          
          <div className="bg-gradient-to-r from-green-400 to-green-500 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">🏛️ {t.baghdadMoneyBox}</h4>
            <p className="text-2xl font-bold">{formatCurrency(data.moneyBoxes.baghdadBox)}</p>
            <p className="text-green-100 text-sm">{t.baghdadOperations}</p>
          </div>
          
          {/* Total Money Boxes */}
          <div className="bg-gradient-to-r from-gray-700 to-gray-800 p-4 rounded-lg shadow-md text-white">
            <h4 className="font-semibold mb-2">💵 {t.totalCash}</h4>
            <p className="text-2xl font-bold">{formatCurrency(totalCash)}</p>
            <p className="text-gray-300 text-sm">{t.allMoneyBoxes}</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">⚡ {t.quickActions}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-lg transition-colors">
            📊 {t.viewReports}
          </button>
          <button className="bg-green-500 hover:bg-green-600 text-white p-3 rounded-lg transition-colors">
            💰 {t.addTransaction}
          </button>
          <button className="bg-purple-500 hover:bg-purple-600 text-white p-3 rounded-lg transition-colors">
            📦 {t.checkInventory}
          </button>
          <button className="bg-orange-500 hover:bg-orange-600 text-white p-3 rounded-lg transition-colors">
            👥 {t.manageStaff}
          </button>
        </div>
      </div>
    </div>
  )
}

function TestHR() {
  const { language } = useLanguageStore()
  const t = useTranslations(language)

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">👥 {t.humanResources}</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600">{t.hrModuleWorking}</p>
      </div>
    </div>
  )
}

function TestSales() {
  const { language } = useLanguageStore()
  const t = useTranslations(language)

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">💰 {t.sales}</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600">{t.salesModuleWorking}</p>
      </div>
    </div>
  )
}

function App() {
  console.log('🚀 App component is rendering!')
  
  return (
    <NewLayout>
      <Routes>
        <Route path="/" element={<TestDashboard />} />
        <Route path="/dashboard" element={<TestDashboard />} />
        <Route path="/hr/*" element={<TestHR />} />
        <Route path="/sales/*" element={<TestSales />} />
        <Route path="*" element={<TestDashboard />} />
      </Routes>
    </NewLayout>
  )
}

export default App
