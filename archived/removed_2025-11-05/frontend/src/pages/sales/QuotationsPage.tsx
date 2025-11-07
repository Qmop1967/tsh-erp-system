import React from 'react'
import { FileText, Plus } from 'lucide-react'

const QuotationsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quotations</h1>
          <p className="text-gray-600">Manage sales quotations</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Create Quotation
        </button>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center mb-4">
          <FileText className="w-6 h-6 text-blue-600 mr-3" />
          <h2 className="text-lg font-semibold">Quotation Management</h2>
        </div>
        <p className="text-gray-600">Quotation management features will be implemented here.</p>
      </div>
    </div>
  )
}

export default QuotationsPage
