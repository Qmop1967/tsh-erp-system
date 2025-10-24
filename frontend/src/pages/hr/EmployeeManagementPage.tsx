import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Users, Search, Plus, Edit, Trash2, Eye, Filter, Download,
  Building2, Briefcase, Mail, Phone, Calendar, DollarSign,
  X, Save, UserCheck, UserX, MapPin, Award
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

interface Employee {
  id: number
  employee_code: string
  full_name_en: string
  full_name_ar: string
  email: string
  phone: string
  department: string
  position: string
  employment_status: string
  hire_date: string
  base_salary: number
  is_active: boolean
}

export function EmployeeManagementPage() {
  const navigate = useNavigate()
  const { checkAuthentication } = useAuthStore()
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null)

  useEffect(() => {
    checkAuthentication()
    fetchEmployees()
  }, [checkAuthentication])

  const fetchEmployees = async () => {
    try {
      // Mock data - replace with actual API call
      const mockEmployees: Employee[] = [
        {
          id: 1,
          employee_code: 'EMP001',
          full_name_en: 'Ahmed Hassan',
          full_name_ar: 'أحمد حسن',
          email: 'ahmed.hassan@tsh.com',
          phone: '+964 770 123 4567',
          department: 'Sales',
          position: 'Sales Manager',
          employment_status: 'active',
          hire_date: '2023-01-15',
          base_salary: 50000000,
          is_active: true
        },
        {
          id: 2,
          employee_code: 'EMP002',
          full_name_en: 'Fatima Ali',
          full_name_ar: 'فاطمة علي',
          email: 'fatima.ali@tsh.com',
          phone: '+964 770 234 5678',
          department: 'HR',
          position: 'HR Specialist',
          employment_status: 'active',
          hire_date: '2023-03-20',
          base_salary: 45000000,
          is_active: true
        },
        {
          id: 3,
          employee_code: 'EMP003',
          full_name_en: 'Mohammed Ibrahim',
          full_name_ar: 'محمد إبراهيم',
          email: 'mohammed.ibrahim@tsh.com',
          phone: '+964 770 345 6789',
          department: 'Warehouse',
          position: 'Warehouse Supervisor',
          employment_status: 'active',
          hire_date: '2022-11-10',
          base_salary: 40000000,
          is_active: true
        }
      ]
      setEmployees(mockEmployees)
    } catch (error) {
      console.error('Error fetching employees:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IQ', {
      style: 'currency',
      currency: 'IQD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const filteredEmployees = employees.filter(emp => {
    const matchesSearch = emp.full_name_en.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         emp.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         emp.employee_code.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = selectedStatus === 'all' || emp.employment_status === selectedStatus
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return { bg: '#dcfce7', text: '#16a34a', border: '#86efac' }
      case 'inactive':
        return { bg: '#fef3c7', text: '#d97706', border: '#fcd34d' }
      case 'terminated':
        return { bg: '#fee2e2', text: '#dc2626', border: '#fca5a5' }
      case 'on_leave':
        return { bg: '#dbeafe', text: '#2563eb', border: '#93c5fd' }
      default:
        return { bg: '#f3f4f6', text: '#6b7280', border: '#d1d5db' }
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f8fafc' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #e5e7eb',
            borderTopColor: '#3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>Loading employees...</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
          borderRadius: '20px',
          padding: '32px',
          marginBottom: '24px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            width: '200px',
            height: '200px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '50%',
            filter: 'blur(40px)'
          }}></div>

          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <Users size={32} color="white" />
                  <h1 style={{ fontSize: '28px', fontWeight: '700', color: 'white', margin: '0' }}>
                    Employee Management
                  </h1>
                </div>
                <p style={{ fontSize: '16px', color: 'rgba(255, 255, 255, 0.9)', margin: '0' }}>
                  إدارة الموظفين - Manage employee records and information
                </p>
              </div>

              <button
                onClick={() => navigate('/hr')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '10px',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'
                }}
              >
                ← Back to HR Dashboard
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px'
        }}>
          {[
            { label: 'Total Employees', value: employees.length, color: '#3b82f6' },
            { label: 'Active', value: employees.filter(e => e.employment_status === 'active').length, color: '#16a34a' },
            { label: 'On Leave', value: employees.filter(e => e.employment_status === 'on_leave').length, color: '#d97706' },
            { label: 'Inactive', value: employees.filter(e => e.employment_status === 'inactive').length, color: '#dc2626' },
          ].map((stat, index) => (
            <div key={index} style={{
              background: 'white',
              padding: '20px',
              borderRadius: '12px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
              borderLeft: `4px solid ${stat.color}`
            }}>
              <div style={{ fontSize: '28px', fontWeight: '700', color: stat.color, marginBottom: '4px' }}>
                {stat.value}
              </div>
              <div style={{ fontSize: '13px', color: '#6b7280', fontWeight: '500' }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Search and Filters */}
        <div style={{
          background: 'white',
          padding: '24px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {/* Search */}
            <div style={{ flex: '1', minWidth: '250px', position: 'relative' }}>
              <Search size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
              <input
                type="text"
                placeholder="Search by name, email, or employee code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 12px 10px 40px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
            </div>

            {/* Status Filter */}
            <div style={{ position: 'relative' }}>
              <Filter size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af', pointerEvents: 'none' }} />
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                style={{
                  padding: '10px 12px 10px 40px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '14px',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  outline: 'none'
                }}
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="on_leave">On Leave</option>
                <option value="terminated">Terminated</option>
              </select>
            </div>

            {/* Add Employee Button */}
            <button
              onClick={() => setShowCreateModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'scale(1.05)'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'scale(1)'
              }}
            >
              <Plus size={20} />
              Add Employee
            </button>

            {/* Export Button */}
            <button
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                background: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                color: '#374151',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = '#f9fafb'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'white'
              }}
            >
              <Download size={20} />
              Export
            </button>
          </div>
        </div>

        {/* Employee Table */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                  <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Code</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Employee</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Contact</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Department</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Position</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Salary</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Status</th>
                  <th style={{ padding: '16px', textAlign: 'center', fontSize: '12px', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((employee) => {
                  const statusColor = getStatusColor(employee.employment_status)
                  return (
                    <tr key={employee.id} style={{ borderBottom: '1px solid #e5e7eb', transition: 'background 0.2s' }}
                      onMouseOver={(e) => e.currentTarget.style.background = '#f9fafb'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'white'}
                    >
                      <td style={{ padding: '16px' }}>
                        <span style={{ fontFamily: 'monospace', fontSize: '13px', fontWeight: '600', color: '#374151' }}>
                          {employee.employee_code}
                        </span>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <div>
                          <div style={{ fontWeight: '600', color: '#1f2937', fontSize: '14px' }}>
                            {employee.full_name_en}
                          </div>
                          <div style={{ fontSize: '12px', color: '#6b7280' }}>
                            {employee.full_name_ar}
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#374151' }}>
                            <Mail size={14} style={{ color: '#6b7280' }} />
                            {employee.email}
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#374151' }}>
                            <Phone size={14} style={{ color: '#6b7280' }} />
                            {employee.phone}
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Building2 size={16} style={{ color: '#6b7280' }} />
                          <span style={{ fontSize: '13px', color: '#374151' }}>{employee.department}</span>
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Briefcase size={16} style={{ color: '#6b7280' }} />
                          <span style={{ fontSize: '13px', color: '#374151' }}>{employee.position}</span>
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{ fontSize: '13px', fontWeight: '600', color: '#374151' }}>
                          {formatCurrency(employee.base_salary)}
                        </span>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span style={{
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '600',
                          background: statusColor.bg,
                          color: statusColor.text,
                          border: `1px solid ${statusColor.border}`,
                          textTransform: 'capitalize'
                        }}>
                          {employee.employment_status.replace('_', ' ')}
                        </span>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                          <button
                            onClick={() => setSelectedEmployee(employee)}
                            style={{
                              padding: '6px',
                              background: '#eff6ff',
                              border: '1px solid #dbeafe',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.background = '#dbeafe'}
                            onMouseOut={(e) => e.currentTarget.style.background = '#eff6ff'}
                            title="View Details"
                          >
                            <Eye size={16} style={{ color: '#2563eb' }} />
                          </button>
                          <button
                            style={{
                              padding: '6px',
                              background: '#f0fdf4',
                              border: '1px solid #dcfce7',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.background = '#dcfce7'}
                            onMouseOut={(e) => e.currentTarget.style.background = '#f0fdf4'}
                            title="Edit Employee"
                          >
                            <Edit size={16} style={{ color: '#16a34a' }} />
                          </button>
                          <button
                            style={{
                              padding: '6px',
                              background: '#fef2f2',
                              border: '1px solid #fee2e2',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.background = '#fee2e2'}
                            onMouseOut={(e) => e.currentTarget.style.background = '#fef2f2'}
                            title="Delete Employee"
                          >
                            <Trash2 size={16} style={{ color: '#dc2626' }} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {filteredEmployees.length === 0 && (
            <div style={{ padding: '60px', textAlign: 'center' }}>
              <Users size={48} style={{ color: '#d1d5db', margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#6b7280', margin: '0 0 8px 0' }}>
                No employees found
              </h3>
              <p style={{ fontSize: '14px', color: '#9ca3af', margin: '0' }}>
                Try adjusting your search or filters
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Animation Keyframes */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
