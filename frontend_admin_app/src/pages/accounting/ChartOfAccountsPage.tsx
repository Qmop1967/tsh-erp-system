import React, { useState, useEffect } from 'react'
import { Plus, Search, Edit, Eye, FolderOpen, FileText, AlertCircle, RefreshCw } from 'lucide-react'
import { accountingApi } from '@/lib/api'
import { useBranchAwareApi } from '@/hooks/useBranchAwareApi'
import { useLanguageStore } from '@/stores/languageStore'
import { useTranslations } from '@/lib/translations'
import type { ChartOfAccounts } from '@/types'

const ChartOfAccountsPage: React.FC = () => {
  const [chartOfAccounts, setChartOfAccounts] = useState<ChartOfAccounts[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [showModal, setShowModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState<ChartOfAccounts | null>(null)
  const { useBranchChangeEffect } = useBranchAwareApi()
  const { language } = useLanguageStore()
  const t = useTranslations(language)
  const [newAccount, setNewAccount] = useState<Partial<ChartOfAccounts>>({
    code: '',
    name_ar: '',
    name_en: '',
    account_type: 'ASSET',
    parent_id: undefined,
    is_active: true,
    allow_posting: true,
    description_ar: '',
    description_en: ''
  })

  const accountTypes = [
    { value: 'ASSET', label: 'Assets - الأصول', color: 'bg-green-100 text-green-800' },
    { value: 'LIABILITY', label: 'Liabilities - الخصوم', color: 'bg-red-100 text-red-800' },
    { value: 'EQUITY', label: 'Equity - حقوق الملكية', color: 'bg-blue-100 text-blue-800' },
    { value: 'REVENUE', label: 'Revenue - الإيرادات', color: 'bg-purple-100 text-purple-800' },
    { value: 'EXPENSE', label: 'Expenses - المصروفات', color: 'bg-orange-100 text-orange-800' }
  ]

  // Account type base codes for smart generation
  const accountTypeBaseCodes = {
    'ASSET': 1000,
    'LIABILITY': 2000, 
    'EQUITY': 3000,
    'REVENUE': 4000,
    'EXPENSE': 5000
  }

  // Generate smart account code based on type and parent
  const generateAccountCode = (accountType: string, parentId?: number): string => {
    const baseCode = accountTypeBaseCodes[accountType as keyof typeof accountTypeBaseCodes] || 1000

    if (parentId) {
      // If parent is selected, find parent account and generate sub-code
      const parentAccount = chartOfAccounts.find(acc => acc.id === parentId)
      if (parentAccount) {
        const parentCode = parentAccount.code
        // Get all child accounts of this parent
        const childAccounts = chartOfAccounts.filter(acc => acc.parent_id === parentId)
        const childCodes = childAccounts.map(acc => parseInt(acc.code)).filter(code => !isNaN(code))
        
        // If parent code is like "1100", generate "1101", "1102", etc.
        if (childCodes.length === 0) {
          return `${parentCode}1`
        } else {
          // Find the next available number
          const maxChild = Math.max(...childCodes)
          const nextCode = maxChild + 1
          return nextCode.toString()
        }
      }
    }

    // For top-level accounts, find next available code in the range
    const accountsOfType = chartOfAccounts.filter(acc => 
      acc.account_type === accountType && !acc.parent_id
    )
    const codes = accountsOfType.map(acc => parseInt(acc.code)).filter(code => !isNaN(code))
    
    if (codes.length === 0) {
      return baseCode.toString()
    }
    
    // Find the next available code in increments of 100 for main accounts
    const maxCode = Math.max(...codes)
    const nextCode = maxCode >= baseCode ? maxCode + 100 : baseCode
    return nextCode.toString()
  }

  // Handle account type change with auto-generation
  const handleAccountTypeChange = (accountType: string) => {
    const newCode = generateAccountCode(accountType, newAccount.parent_id)
    setNewAccount({
      ...newAccount, 
      account_type: accountType as any,
      code: newCode
    })
  }

  // Handle parent account change with auto-generation
  const handleParentAccountChange = (parentId: string) => {
    const parentIdNum = parentId ? parseInt(parentId) : undefined
    const newCode = generateAccountCode(newAccount.account_type || 'ASSET', parentIdNum)
    setNewAccount({
      ...newAccount,
      parent_id: parentIdNum,
      code: newCode
    })
  }

  // Auto-generate code when modal opens for new account
  useEffect(() => {
    if (showModal && !editingAccount) {
      const newCode = generateAccountCode(newAccount.account_type || 'ASSET', newAccount.parent_id)
      setNewAccount(prev => ({ ...prev, code: newCode }))
    }
  }, [showModal, editingAccount])

  // Fetch data when component mounts or branch changes
  useBranchChangeEffect(() => {
    fetchData()
  })

  const fetchData = async () => {
    try {
      setLoading(true)
      // Note: Chart of accounts might not be branch-specific, 
      // but we include branch context for future use if needed
      // const params = getBranchParams()
      const chartResponse = await accountingApi.getChartOfAccounts()
      setChartOfAccounts(chartResponse.data)
      setError(null)
    } catch (err) {
      console.error('Error fetching data:', err)
              setError(t.failedToFetchChartOfAccounts)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingAccount) {
        await accountingApi.updateChartOfAccounts(editingAccount.id, newAccount)
      } else {
        await accountingApi.createChartOfAccounts(newAccount)
      }
      setShowModal(false)
      setEditingAccount(null)
      setNewAccount({
        code: '',
        name_ar: '',
        name_en: '',
        account_type: 'ASSET',
        parent_id: undefined,
        is_active: true,
        allow_posting: true,
        description_ar: '',
        description_en: ''
      })
      await fetchData()
    } catch (err) {
      console.error('Error saving account:', err)
      setError('Failed to save account')
    }
  }

  const handleEdit = (account: ChartOfAccounts) => {
    setEditingAccount(account)
    setNewAccount({
      code: account.code,
      name_ar: account.name_ar,
      name_en: account.name_en,
      account_type: account.account_type,
      parent_id: account.parent_id,
      is_active: account.is_active,
      allow_posting: account.allow_posting,
      description_ar: account.description_ar || '',
      description_en: account.description_en || ''
    })
    setShowModal(true)
  }

  const filteredAccounts = chartOfAccounts.filter(account => {
    const matchesSearch = 
      account.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.name_ar.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.name_en.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesType = selectedType === 'all' || account.account_type === selectedType
    
    return matchesSearch && matchesType
  })

  const getTypeInfo = (type: string) => {
    return accountTypes.find(t => t.value === type) || accountTypes[0]
  }

  const buildAccountHierarchy = (accounts: ChartOfAccounts[], parentId: number | null = null, level: number = 0): ChartOfAccounts[] => {
    return accounts
      .filter(account => account.parent_id === parentId)
      .sort((a, b) => a.code.localeCompare(b.code))
      .reduce((acc, account) => {
        const accountWithLevel = { ...account, level }
        acc.push(accountWithLevel)
        const children = buildAccountHierarchy(accounts, account.id, level + 1)
        acc.push(...children)
        return acc
      }, [] as (ChartOfAccounts & { level: number })[])
  }

  const hierarchicalAccounts = buildAccountHierarchy(filteredAccounts)

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t.loadingChartOfAccounts}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t.chartOfAccounts}</h1>
          <p className="text-gray-600">دليل الحسابات - Manage your account structure</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <span className="text-red-800">{error}</span>
          </div>
        )}

        {/* Controls */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search accounts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64"
                />
              </div>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Types</option>
                {accountTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center gap-2 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Add Account
            </button>
          </div>
        </div>

        {/* Accounts Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Posting
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Code & Name
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {hierarchicalAccounts.map((account) => {
                  const typeInfo = getTypeInfo(account.account_type)
                  const hasChildren = chartOfAccounts.some(acc => acc.parent_id === account.id)
                  
                  return (
                    <tr key={account.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEdit(account)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            className="text-green-600 hover:text-green-900"
                            title="View"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          account.allow_posting ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {account.allow_posting ? 'Posting' : 'Non-Posting'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`flex items-center ${account.level > 0 ? `ml-${account.level * 6}` : ''}`}>
                          {hasChildren && (
                            <FolderOpen className="h-4 w-4 text-gray-400 mr-2" />
                          )}
                          {!hasChildren && (
                            <FileText className="h-4 w-4 text-gray-400 mr-2" />
                          )}
                          <div>
                            <div className="text-sm font-medium text-gray-900">{account.code}</div>
                            <div className="text-sm text-gray-600">
                              {language === 'ar' ? account.name_ar : account.name_en}
                            </div>
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${typeInfo.color} mt-1`}>
                              {typeInfo.label}
                            </span>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            {hierarchicalAccounts.length === 0 && (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No accounts found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {searchTerm || selectedType !== 'all' 
                    ? 'Try adjusting your search criteria.' 
                    : 'Get started by creating your first account.'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  {editingAccount ? 'Edit Account' : 'Add New Account'}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Account Type *
                      </label>
                      <select
                        required
                        value={newAccount.account_type}
                        onChange={(e) => handleAccountTypeChange(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        {accountTypes.map(type => (
                          <option key={type.value} value={type.value}>{type.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Account Code *
                        <button
                          type="button"
                          onClick={() => {
                            const newCode = generateAccountCode(newAccount.account_type || 'ASSET', newAccount.parent_id)
                            setNewAccount({...newAccount, code: newCode})
                          }}
                          className="ml-2 text-blue-600 hover:text-blue-800"
                          title="Auto-generate code"
                        >
                          <RefreshCw className="h-3 w-3 inline" />
                        </button>
                      </label>
                      <input
                        type="text"
                        required
                        value={newAccount.code}
                        onChange={(e) => setNewAccount({...newAccount, code: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., 1001"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Auto-generated based on type and parent. You can edit if needed.
                      </p>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Parent Account
                    </label>
                    <select
                      value={newAccount.parent_id || ''}
                      onChange={(e) => handleParentAccountChange(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">No Parent (Top Level)</option>
                      {chartOfAccounts
                        .filter(acc => acc.id !== editingAccount?.id)
                        .map(account => (
                          <option key={account.id} value={account.id}>
                            {account.code} - {account.name_en}
                          </option>
                        ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      English Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={newAccount.name_en}
                      onChange={(e) => setNewAccount({...newAccount, name_en: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Account name in English"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Arabic Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={newAccount.name_ar}
                      onChange={(e) => setNewAccount({...newAccount, name_ar: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-arabic"
                      placeholder="اسم الحساب بالعربية"
                      dir="rtl"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        English Description
                      </label>
                      <textarea
                        value={newAccount.description_en}
                        onChange={(e) => setNewAccount({...newAccount, description_en: e.target.value})}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Account description in English"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Arabic Description
                      </label>
                      <textarea
                        value={newAccount.description_ar}
                        onChange={(e) => setNewAccount({...newAccount, description_ar: e.target.value})}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-arabic"
                        placeholder="وصف الحساب بالعربية"
                        dir="rtl"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={newAccount.is_active}
                        onChange={(e) => setNewAccount({...newAccount, is_active: e.target.checked})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">Active</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={newAccount.allow_posting}
                        onChange={(e) => setNewAccount({...newAccount, allow_posting: e.target.checked})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">Allow Posting</span>
                    </label>
                  </div>

                  <div className="flex justify-end gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowModal(false)
                        setEditingAccount(null)
                        setNewAccount({
                          code: '',
                          name_ar: '',
                          name_en: '',
                          account_type: 'ASSET',
                          parent_id: undefined,
                          is_active: true,
                          allow_posting: true,
                          description_ar: '',
                          description_en: ''
                        })
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      {editingAccount ? 'Update' : 'Create'} Account
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChartOfAccountsPage
