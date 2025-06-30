import { useState, useEffect } from 'react'
import { useBranchStore } from '@/stores/branchStore'
import { useLanguageStore } from '@/stores/languageStore'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Building,
  ChevronDown,
  Check,
  RefreshCw,
  MapPin
} from 'lucide-react'

export function BranchSwitcher() {
  const [isOpen, setIsOpen] = useState(false)
  const { 
    currentBranch, 
    branches, 
    isLoading, 
    error,
    fetchBranches, 
    switchBranch, 
    getCurrentBranchName 
  } = useBranchStore()
  const { language, isRTL } = useLanguageStore()

  useEffect(() => {
    fetchBranches()
  }, [fetchBranches])

  const handleBranchSwitch = async (branchId: number) => {
    await switchBranch(branchId)
    setIsOpen(false)
  }

  const branchDisplayName = language === 'ar' 
    ? (currentBranch?.nameAr || getCurrentBranchName())
    : getCurrentBranchName()

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <RefreshCw className="h-4 w-4 animate-spin" />
        <span className="text-sm text-gray-600 dark:text-gray-400">
          Loading branches...
        </span>
      </div>
    )
  }

  if (error || branches.length === 0) {
    return (
      <div className="flex items-center space-x-2 px-4 py-2 bg-red-100 dark:bg-red-900 rounded-lg">
        <Building className="h-4 w-4 text-red-600 dark:text-red-400" />
        <span className="text-sm text-red-600 dark:text-red-400">
          No branches available
        </span>
      </div>
    )
  }

  return (
    <div className="relative">
      {/* Current Branch Display */}
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center space-x-3 px-4 py-3 bg-white dark:bg-gray-800 
          border-2 border-blue-200 dark:border-blue-600 rounded-xl 
          hover:border-blue-300 dark:hover:border-blue-500 
          hover:bg-blue-50 dark:hover:bg-blue-900 
          transition-all duration-200 shadow-sm hover:shadow-md
          min-w-[200px] max-w-[300px]
          ${isRTL ? 'flex-row-reverse' : ''}
        `}
      >
        <div className="flex items-center space-x-2 flex-1">
          <div className="p-1.5 bg-blue-100 dark:bg-blue-800 rounded-lg">
            <Building className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex flex-col items-start min-w-0">
            <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
              Current Branch
            </span>
            <span className="font-semibold text-gray-900 dark:text-white truncate max-w-[150px]">
              {branchDisplayName}
            </span>
          </div>
        </div>
        <ChevronDown className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {/* Branch Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown Menu */}
          <div className={`
            absolute top-full mt-2 w-80 bg-white dark:bg-gray-800 
            border border-gray-200 dark:border-gray-600 rounded-xl shadow-xl 
            z-20 max-h-96 overflow-y-auto
            ${isRTL ? 'right-0' : 'left-0'}
          `}>
            <div className="p-3 border-b border-gray-200 dark:border-gray-600">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
                <Building className="h-4 w-4 text-blue-600" />
                <span>Switch Branch</span>
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Select a branch to work with
              </p>
            </div>
            
            <div className="py-2">
              {branches.map((branch) => {
                const isSelected = currentBranch?.id === branch.id
                const displayName = language === 'ar' ? branch.nameAr : branch.nameEn
                
                return (
                  <button
                    key={branch.id}
                    onClick={() => handleBranchSwitch(branch.id)}
                    className={`
                      w-full px-4 py-3 flex items-center justify-between 
                      hover:bg-gray-50 dark:hover:bg-gray-700 
                      transition-colors text-left
                      ${isSelected ? 'bg-blue-50 dark:bg-blue-900' : ''}
                    `}
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <div className={`
                        p-2 rounded-lg
                        ${isSelected 
                          ? 'bg-blue-100 dark:bg-blue-800' 
                          : 'bg-gray-100 dark:bg-gray-700'
                        }
                      `}>
                        <Building className={`
                          h-4 w-4 
                          ${isSelected 
                            ? 'text-blue-600 dark:text-blue-400' 
                            : 'text-gray-600 dark:text-gray-400'
                          }
                        `} />
                      </div>
                      <div className="flex flex-col items-start min-w-0 flex-1">
                        <span className={`
                          font-medium truncate max-w-full
                          ${isSelected 
                            ? 'text-blue-900 dark:text-blue-100' 
                            : 'text-gray-900 dark:text-white'
                          }
                        `}>
                          {displayName}
                        </span>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {branch.code}
                          </Badge>
                          {branch.city && (
                            <div className="flex items-center space-x-1 text-xs text-gray-500">
                              <MapPin className="h-3 w-3" />
                              <span>{branch.city}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    {isSelected && (
                      <Check className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                    )}
                  </button>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
