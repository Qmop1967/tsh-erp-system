import React, { useState } from 'react'
import { BarChart3, FileText, TrendingUp, DollarSign, Calendar, Download, AlertCircle } from 'lucide-react'

const FinancialReportsPage: React.FC = () => {
  const [selectedReport, setSelectedReport] = useState<string>('')
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  })

  const reports = [
    {
      id: 'trial-balance',
      name: 'Trial Balance',
      nameAr: 'ميزان المراجعة',
      description: 'Summary of all account balances',
      descriptionAr: 'ملخص أرصدة جميع الحسابات',
      icon: BarChart3,
      color: 'bg-blue-500',
      endpoint: '/api/accounting/reports/trial-balance'
    },
    {
      id: 'balance-sheet',
      name: 'Balance Sheet',
      nameAr: 'الميزانية العمومية',
      description: 'Assets, liabilities, and equity summary',
      descriptionAr: 'ملخص الأصول والخصوم وحقوق الملكية',
      icon: FileText,
      color: 'bg-green-500',
      endpoint: '/api/accounting/reports/balance-sheet'
    },
    {
      id: 'income-statement',
      name: 'Income Statement',
      nameAr: 'قائمة الدخل',
      description: 'Revenue and expenses summary',
      descriptionAr: 'ملخص الإيرادات والمصروفات',
      icon: TrendingUp,
      color: 'bg-purple-500',
      endpoint: '/api/accounting/reports/income-statement'
    },
    {
      id: 'cash-flow',
      name: 'Cash Flow Statement',
      nameAr: 'قائمة التدفقات النقدية',
      description: 'Cash inflows and outflows',
      descriptionAr: 'التدفقات النقدية الداخلة والخارجة',
      icon: DollarSign,
      color: 'bg-orange-500',
      endpoint: '/api/accounting/reports/cash-flow'
    }
  ]

  const handleGenerateReport = () => {
    if (!selectedReport) {
      alert('Please select a report type')
      return
    }
    
    if (!dateRange.startDate || !dateRange.endDate) {
      alert('Please select date range')
      return
    }

    // Here you would typically make an API call to generate the report
    alert(`Generating ${reports.find(r => r.id === selectedReport)?.name} report for ${dateRange.startDate} to ${dateRange.endDate}`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Financial Reports</h1>
          <p className="text-gray-600">التقارير المالية - Generate and view financial reports</p>
        </div>

        {/* Report Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Report Type</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {reports.map((report) => {
              const IconComponent = report.icon
              return (
                <div
                  key={report.id}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedReport === report.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedReport(report.id)}
                >
                  <div className="flex items-center justify-center mb-3">
                    <div className={`p-3 rounded-full ${report.color} text-white`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 text-center mb-1">
                    {report.name}
                  </h3>
                  <p className="text-sm text-gray-600 text-center font-arabic mb-2">
                    {report.nameAr}
                  </p>
                  <p className="text-xs text-gray-500 text-center">
                    {report.description}
                  </p>
                </div>
              )
            })}
          </div>

          {/* Date Range Selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="date"
                  value={dateRange.startDate}
                  onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="date"
                  value={dateRange.endDate}
                  onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
                />
              </div>
            </div>
            <div>
              <button
                onClick={handleGenerateReport}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center justify-center gap-2 transition-colors"
              >
                <FileText className="h-4 w-4" />
                Generate Report
              </button>
            </div>
          </div>
        </div>

        {/* Report Preview/Results */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Report Results</h2>
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
          
          {!selectedReport ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No Report Selected</h3>
              <p className="mt-1 text-sm text-gray-500">
                Please select a report type and date range to generate a report.
              </p>
            </div>
          ) : (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <AlertCircle className="mx-auto h-8 w-8 text-yellow-500 mb-3" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Report Generation</h3>
              <p className="text-gray-600 mb-4">
                Selected: {reports.find(r => r.id === selectedReport)?.name}
              </p>
              <p className="text-sm text-gray-500">
                Click "Generate Report" to create the report with your selected parameters.
              </p>
            </div>
          )}
        </div>

        {/* Quick Links */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/accounting/chart-of-accounts"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <FileText className="h-5 w-5 text-blue-600 mr-3" />
              <div>
                <div className="font-medium text-gray-900">Chart of Accounts</div>
                <div className="text-sm text-gray-500">View account structure</div>
              </div>
            </a>
            <a
              href="/accounting/journal-entries"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <BarChart3 className="h-5 w-5 text-green-600 mr-3" />
              <div>
                <div className="font-medium text-gray-900">Journal Entries</div>
                <div className="text-sm text-gray-500">View transactions</div>
              </div>
            </a>
            <a
              href="/accounting/general-ledger"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <TrendingUp className="h-5 w-5 text-purple-600 mr-3" />
              <div>
                <div className="font-medium text-gray-900">General Ledger</div>
                <div className="text-sm text-gray-500">Account details</div>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FinancialReportsPage
