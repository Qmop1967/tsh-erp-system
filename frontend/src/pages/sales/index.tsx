// Template Component Generator
import React from 'react'
import { FileText, Plus } from 'lucide-react'

interface PageTemplateProps {
  title: string
  description: string
  buttonText: string
}

export const PageTemplate: React.FC<PageTemplateProps> = ({ title, description, buttonText }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          <p className="text-gray-600">{description}</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          {buttonText}
        </button>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center mb-4">
          <FileText className="w-6 h-6 text-blue-600 mr-3" />
          <h2 className="text-lg font-semibold">{title} Management</h2>
        </div>
        <p className="text-gray-600">{title} management features will be implemented here.</p>
      </div>
    </div>
  )
}
