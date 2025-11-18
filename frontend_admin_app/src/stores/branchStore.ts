import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { branchesApi } from '@/lib/api'
import type { Branch } from '@/types'

interface BranchState {
  currentBranch: Branch | null
  branches: Branch[]
  isLoading: boolean
  error: string | null
  
  // Actions
  setCurrentBranch: (branch: Branch) => void
  fetchBranches: () => Promise<void>
  switchBranch: (branchId: number) => Promise<void>
  getCurrentBranchName: () => string
  getCurrentBranchCode: () => string
}

export const useBranchStore = create<BranchState>()(
  persist(
    (set, get) => ({
      currentBranch: null,
      branches: [],
      isLoading: false,
      error: null,

      setCurrentBranch: (branch: Branch) => {
        set({ currentBranch: branch, error: null })
      },

      fetchBranches: async () => {
        try {
          set({ isLoading: true, error: null })
          const response = await branchesApi.getBranches()
          const branches = response.data.data || []
          set({ 
            branches: Array.isArray(branches) ? branches : [],
            isLoading: false 
          })
          
          // Set default branch if none selected
          const { currentBranch } = get()
          if (!currentBranch && branches.length > 0) {
            set({ currentBranch: branches[0] })
          }
        } catch (error) {
          console.error('Error fetching branches:', error)
          set({ 
            error: 'Failed to fetch branches',
            isLoading: false,
            branches: []
          })
        }
      },

      switchBranch: async (branchId: number) => {
        try {
          const { branches } = get()
          const branch = branches.find(b => b.id === branchId)
          if (branch) {
            set({ currentBranch: branch, error: null })
            
            // You can add logic here to refresh data when branch changes
            // For example, trigger dashboard refresh, clear cached data, etc.
            
            // Dispatch custom event for components to react to branch change
            window.dispatchEvent(new CustomEvent('branchChanged', { 
              detail: { branch } 
            }))
          }
        } catch (error) {
          console.error('Error switching branch:', error)
          set({ error: 'Failed to switch branch' })
        }
      },

      getCurrentBranchName: () => {
        const { currentBranch } = get()
        return currentBranch?.nameEn || 'No Branch Selected'
      },

      getCurrentBranchCode: () => {
        const { currentBranch } = get()
        return currentBranch?.code || ''
      }
    }),
    {
      name: 'branch-storage',
      partialize: (state) => ({ 
        currentBranch: state.currentBranch 
      })
    }
  )
)
