import React from 'react'
import { Link } from 'react-router-dom'
import { Package } from 'lucide-react'

const InventoryButton: React.FC = () => {
  return (
    <Link 
      to="/items" 
      className="fixed right-8 bottom-8 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg z-50 flex items-center justify-center"
      title="Inventory Items"
    >
      <Package size={24} />
    </Link>
  )
}

export default InventoryButton
