import React from 'react'
import { NavLink } from 'react-router-dom'
import { Package, Tags, ClipboardList, ArrowRightLeft } from 'lucide-react'
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'

export const InventorySidebar: React.FC = () => {
  const { language, isRTL } = useLanguageStore()
  const t = useTranslations(language)
  
  return (
    <div className="fixed left-0 top-20 z-50 bg-white shadow-lg rounded-r-lg overflow-hidden">
      <div className="p-2 bg-blue-500 text-white font-bold">
        <div className="flex items-center">
          <Package className="mr-2" size={16} />
          <span>{t.inventory}</span>
        </div>
      </div>
      <nav className="p-2">
        <ul className="space-y-1">
          <li>
            <NavLink 
              to="/items"
              className={({ isActive }) => 
                `flex items-center px-3 py-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <Package className="mr-2" size={16} />
              <span>{t.items}</span>
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/inventory/price-lists"
              className={({ isActive }) => 
                `flex items-center px-3 py-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <Tags className="mr-2" size={16} />
              <span>{t.priceLists}</span>
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/inventory/adjustments"
              className={({ isActive }) => 
                `flex items-center px-3 py-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <ClipboardList className="mr-2" size={16} />
              <span>{t.adjustments}</span>
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/inventory/movements"
              className={({ isActive }) => 
                `flex items-center px-3 py-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <ArrowRightLeft className="mr-2" size={16} />
              <span>{t.movements}</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </div>
  )
}
