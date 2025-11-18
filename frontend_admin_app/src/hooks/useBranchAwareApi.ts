import { useEffect, useRef } from 'react'
import { useBranchStore } from '@/stores/branchStore'

/**
 * Hook that provides branch-aware API calls and automatic refetching when branch changes
 */
export function useBranchAwareApi() {
  const { currentBranch } = useBranchStore()
  const previousBranchId = useRef<number | null>(null)

  // Get current branch ID for API calls
  const getCurrentBranchId = () => {
    return currentBranch?.id || null
  }

  // Get branch-aware API parameters
  const getBranchParams = (params: Record<string, any> = {}) => {
    const branchId = getCurrentBranchId()
    if (branchId) {
      return { ...params, branch_id: branchId }
    }
    return params
  }

  // Check if branch has changed
  const hasBranchChanged = () => {
    const currentId = getCurrentBranchId()
    const hasChanged = previousBranchId.current !== currentId
    previousBranchId.current = currentId
    return hasChanged
  }

  // Setup branch change listener
  const useBranchChangeEffect = (callback: () => void, dependencies: any[] = []) => {
    useEffect(() => {
      const handleBranchChanged = () => {
        callback()
      }

      // Listen for branch change events
      window.addEventListener('branchChanged', handleBranchChanged)
      
      // Also call callback if dependencies change
      callback()

      return () => {
        window.removeEventListener('branchChanged', handleBranchChanged)
      }
    }, [currentBranch?.id, ...dependencies])
  }

  return {
    currentBranch,
    getCurrentBranchId,
    getBranchParams,
    hasBranchChanged,
    useBranchChangeEffect
  }
}
