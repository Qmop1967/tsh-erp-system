import { useState, useEffect } from 'react'
// import axios from 'axios' // Commented out for demo mode

// Dashboard data types
interface DashboardData {
  financials: {
    totalReceivables: number
    totalPayables: number
    stockValue: number
  }
  inventory: {
    positiveItems: number
    totalPieces: number
  }
  staff: {
    partnerSalesmen: number
    travelSalespersons: number
  }
  moneyBoxes: {
    mainBox: number
    fratAwsatVector: number
    firstSouthVector: number
    northVector: number
    westVector: number
    daylaBox: number
    baghdadBox: number
  }
}

const defaultData: DashboardData = {
  financials: {
    totalReceivables: 125430.50,
    totalPayables: 89720.25,
    stockValue: 234890.75
  },
  inventory: {
    positiveItems: 1247,
    totalPieces: 15892
  },
  staff: {
    partnerSalesmen: 12,
    travelSalespersons: 8
  },
  moneyBoxes: {
    mainBox: 45230.50,
    fratAwsatVector: 12840.25,
    firstSouthVector: 8920.75,
    northVector: 15670.00,
    westVector: 9450.50,
    daylaBox: 6780.25,
    baghdadBox: 22140.75
  }
}

export const useDashboardData = () => {
  const [data, setData] = useState<DashboardData>(defaultData)
  const [loading, setLoading] = useState(false) // Start with false for demo
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardData = async () => {
    // For demo mode, just return default data immediately
    console.log('🎯 [Demo Mode] Using default dashboard data')
    setLoading(false)
    setError(null)
    setData(defaultData)
    return
    
    // Original API code (commented out for demo)
    /*
    try {
      setLoading(true)
      setError(null)

      // Try to fetch real data from multiple endpoints
      const promises = [
        // Fetch receivables and payables
        axios.get('http://localhost:8000/api/accounting/summary').catch(() => null),
        // Fetch inventory data
        axios.get('http://localhost:8000/api/inventory/summary').catch(() => null),
        // Fetch staff counts
        axios.get('http://localhost:8000/api/users/summary').catch(() => null),
        // Fetch cash flow data
        axios.get('http://localhost:8000/api/cashflow/summary').catch(() => null),
      ]

      const [accountingRes, inventoryRes, staffRes, cashflowRes] = await Promise.all(promises)

      const newData: DashboardData = { ...defaultData }

      // Update with real data if available
      if (accountingRes?.data) {
        newData.financials = {
          totalReceivables: accountingRes.data.total_receivables || defaultData.financials.totalReceivables,
          totalPayables: accountingRes.data.total_payables || defaultData.financials.totalPayables,
          stockValue: accountingRes.data.stock_value || defaultData.financials.stockValue
        }
      }

      if (inventoryRes?.data) {
        newData.inventory = {
          positiveItems: inventoryRes.data.positive_items || defaultData.inventory.positiveItems,
          totalPieces: inventoryRes.data.total_pieces || defaultData.inventory.totalPieces
        }
      }

      if (staffRes?.data) {
        newData.staff = {
          partnerSalesmen: staffRes.data.partner_salesmen || defaultData.staff.partnerSalesmen,
          travelSalespersons: staffRes.data.travel_salespersons || defaultData.staff.travelSalespersons
        }
      }

      if (cashflowRes?.data) {
        newData.moneyBoxes = {
          mainBox: cashflowRes.data.main_box || defaultData.moneyBoxes.mainBox,
          fratAwsatVector: cashflowRes.data.frat_awsat_vector || defaultData.moneyBoxes.fratAwsatVector,
          firstSouthVector: cashflowRes.data.first_south_vector || defaultData.moneyBoxes.firstSouthVector,
          northVector: cashflowRes.data.north_vector || defaultData.moneyBoxes.northVector,
          westVector: cashflowRes.data.west_vector || defaultData.moneyBoxes.westVector,
          daylaBox: cashflowRes.data.dayla_box || defaultData.moneyBoxes.daylaBox,
          baghdadBox: cashflowRes.data.baghdad_box || defaultData.moneyBoxes.baghdadBox
        }
      }

      setData(newData)
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to fetch some dashboard data. Using default values.')
      setData(defaultData)
    } finally {
      setLoading(false)
    }
    */
  }

  useEffect(() => {
    // For demo mode, set data immediately
    fetchDashboardData()
    
    // Comment out auto-refresh for demo
    // const interval = setInterval(fetchDashboardData, 30000)
    // return () => clearInterval(interval)
  }, [])

  return { data, loading, error, refetch: fetchDashboardData }
}
