import React from 'react'
import { Routes, Route } from 'react-router-dom'
import NewLayout from './components/layout/NewLayout'

// Simple test components
function TestDashboard() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">🏠 Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-lg font-semibold text-blue-600 mb-2">💰 Total Receivables</h3>
          <p className="text-3xl font-bold text-gray-900">$125,430</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-lg font-semibold text-red-600 mb-2">💸 Total Payables</h3>
          <p className="text-3xl font-bold text-gray-900">$89,720</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-lg font-semibold text-green-600 mb-2">📦 Stock Value</h3>
          <p className="text-3xl font-bold text-gray-900">$234,890</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-lg font-semibold text-purple-600 mb-2">👥 Staff Count</h3>
          <p className="text-3xl font-bold text-gray-900">45</p>
        </div>
      </div>
    </div>
  )
}

function TestHR() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">👥 HR Management</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600">HR module is working! This will contain employee management, payroll, and more.</p>
      </div>
    </div>
  )
}

function TestSales() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">💰 Sales Management</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600">Sales module is working! This will contain customers, orders, invoices, and more.</p>
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
