import React, { useState, useEffect } from 'react'
import { Plus, Search, Edit, Eye, AlertCircle, Calendar, FileText, DollarSign } from 'lucide-react'
import { accountingApi } from '@/lib/api'
import type { JournalEntry, Journal } from '@/types'

const JournalEntriesPage: React.FC = () => {
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([])
  const [journals, setJournals] = useState<Journal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedJournal, setSelectedJournal] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')

  const statusOptions = [
    { value: 'DRAFT', label: 'Draft - مسودة', color: 'bg-gray-100 text-gray-800' },
    { value: 'POSTED', label: 'Posted - مرحل', color: 'bg-green-100 text-green-800' },
    { value: 'REVERSED', label: 'Reversed - معكوس', color: 'bg-red-100 text-red-800' }
  ]

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [entriesResponse, journalsResponse] = await Promise.all([
        accountingApi.getJournalEntries(),
        accountingApi.getJournals()
      ])
      setJournalEntries(entriesResponse.data)
      setJournals(journalsResponse.data)
      setError(null)
    } catch (err) {
      console.error('Error fetching data:', err)
      setError('Failed to fetch journal entries data')
    } finally {
      setLoading(false)
    }
  }

  const filteredEntries = journalEntries.filter(entry => {
    const matchesSearch = 
      entry.reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (entry.description_en && entry.description_en.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (entry.description_ar && entry.description_ar.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesJournal = selectedJournal === 'all' || entry.journal_id.toString() === selectedJournal
    const matchesStatus = selectedStatus === 'all' || entry.status === selectedStatus
    
    return matchesSearch && matchesJournal && matchesStatus
  })

  const getStatusInfo = (status: string) => {
    return statusOptions.find(s => s.value === status) || statusOptions[0]
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading journal entries...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Journal Entries</h1>
          <p className="text-gray-600">القيود المحاسبية - Manage accounting journal entries</p>
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
                  placeholder="Search entries..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64"
                />
              </div>
              <select
                value={selectedJournal}
                onChange={(e) => setSelectedJournal(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Journals</option>
                {journals.map(journal => (
                  <option key={journal.id} value={journal.id.toString()}>
                    {journal.code} - {journal.name_en}
                  </option>
                ))}
              </select>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                {statusOptions.map(status => (
                  <option key={status.value} value={status.value}>{status.label}</option>
                ))}
              </select>
            </div>
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center gap-2 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Add Entry
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Entries</p>
                <p className="text-2xl font-bold text-gray-900">{journalEntries.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Debits</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(journalEntries.reduce((sum, entry) => sum + entry.total_debit, 0))}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Credits</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(journalEntries.reduce((sum, entry) => sum + entry.total_credit, 0))}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Entries Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reference & Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Journal
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Debit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Credit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredEntries.map((entry) => {
                  const statusInfo = getStatusInfo(entry.status)
                  const journal = journals.find(j => j.id === entry.journal_id)
                  return (
                    <tr key={entry.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{entry.reference}</div>
                          <div className="text-sm text-gray-500 flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {new Date(entry.date).toLocaleDateString()}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{journal?.code}</div>
                        <div className="text-sm text-gray-500">{journal?.name_en}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{entry.description_en || 'N/A'}</div>
                        <div className="text-sm text-gray-500 font-arabic">{entry.description_ar || 'غير محدد'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(entry.total_debit)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(entry.total_credit)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            className="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            className="text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-50"
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            {filteredEntries.length === 0 && (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No journal entries found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {searchTerm || selectedJournal !== 'all' || selectedStatus !== 'all'
                    ? 'Try adjusting your search criteria.' 
                    : 'Get started by creating your first journal entry.'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default JournalEntriesPage
