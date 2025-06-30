import React from 'react'
import { Users, Plus, Search, Filter } from 'lucide-react'

const ConsumersPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Consumers</h1>
          <p className="text-gray-600">Manage individual consumers</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Consumer
        </button>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Consumer Management</h2>
        <p className="text-gray-600">Consumer management features will be implemented here.</p>
      </div>
    </div>
  )
}

export default ConsumersPage
