import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Users, Building2, Briefcase, Calendar, Clock, DollarSign,
  TrendingUp, Award, AlertCircle, CheckCircle, XCircle,
  UserPlus, UserMinus, FileText, Settings, ArrowUpRight,
  MapPin, Star, Target, Activity
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

interface HRMetrics {
  total_employees: number
  active_employees: number
  new_hires_month: number
  terminations_month: number
  attendance_rate: number
  late_arrivals_today: number
  pending_leave_requests: number
  total_payroll_amount: number
  average_salary: number
  departments: {
    [key: string]: {
      employees: number
      attendance_rate: number
    }
  }
  performance_metrics: {
    average_rating: number
    completed_reviews: number
    pending_reviews: number
  }
  payroll_breakdown: {
    total_gross: number
    total_deductions: number
    total_net: number
    overtime_cost: number
  }
  system_status: {
    hr_system: string
    payroll_system: string
    attendance_system: string
    performance_system: string
  }
}

export function HRDashboard() {
  const navigate = useNavigate()
  const { checkAuthentication } = useAuthStore()
  const [metrics, setMetrics] = useState<HRMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthentication()
    fetchHRMetrics()
  }, [checkAuthentication])

  const fetchHRMetrics = async () => {
    try {
      // For now, using mock data - replace with actual API call
      const response = await fetch('http://localhost:8000/api/hr/mock-data/dashboard')
      const result = await response.json()
      if (result.success) {
        setMetrics(result.data)
      }
    } catch (error) {
      console.error('Error fetching HR metrics:', error)
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

  const statCards = [
    {
      title: 'Total Employees',
      titleAr: 'إجمالي الموظفين',
      value: metrics?.total_employees || 0,
      change: `+${metrics?.new_hires_month || 0} this month`,
      icon: Users,
      gradient: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      trend: 'up'
    },
    {
      title: 'Attendance Rate',
      titleAr: 'معدل الحضور',
      value: `${metrics?.attendance_rate || 0}%`,
      change: `${metrics?.late_arrivals_today || 0} late today`,
      icon: Clock,
      gradient: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      trend: 'up'
    },
    {
      title: 'Pending Leaves',
      titleAr: 'الإجازات المعلقة',
      value: metrics?.pending_leave_requests || 0,
      change: 'Requires approval',
      icon: Calendar,
      gradient: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      trend: 'neutral'
    },
    {
      title: 'Total Payroll',
      titleAr: 'إجمالي الرواتب',
      value: formatCurrency(metrics?.total_payroll_amount || 0),
      change: 'This month',
      icon: DollarSign,
      gradient: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      trend: 'up'
    },
  ]

  const quickActions = [
    {
      title: 'Employees',
      titleAr: 'الموظفين',
      icon: Users,
      color: 'blue',
      path: '/hr/employees',
      description: 'Manage employee records'
    },
    {
      title: 'Attendance',
      titleAr: 'الحضور',
      icon: Clock,
      color: 'green',
      path: '/hr/attendance',
      description: 'Track attendance & hours'
    },
    {
      title: 'Leave Requests',
      titleAr: 'طلبات الإجازة',
      icon: Calendar,
      color: 'orange',
      path: '/hr/leave-requests',
      description: 'Review leave applications'
    },
    {
      title: 'Payroll',
      titleAr: 'الرواتب',
      icon: DollarSign,
      color: 'purple',
      path: '/hr/payroll',
      description: 'Manage payroll records'
    },
    {
      title: 'Performance',
      titleAr: 'الأداء',
      icon: Award,
      color: 'pink',
      path: '/hr/performance',
      description: 'Performance reviews'
    },
    {
      title: 'Departments',
      titleAr: 'الأقسام',
      icon: Building2,
      color: 'indigo',
      path: '/hr/departments',
      description: 'Department structure'
    },
  ]

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
          <p style={{ color: '#6b7280', fontSize: '14px' }}>Loading HR Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header Section with Gradient */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '20px',
          padding: '40px',
          marginBottom: '32px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
        }}>
          {/* Decorative Elements */}
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            width: '300px',
            height: '300px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '50%',
            filter: 'blur(60px)'
          }}></div>

          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                  <Users size={40} color="white" />
                  <h1 style={{ fontSize: '32px', fontWeight: '700', color: 'white', margin: '0' }}>
                    Human Resources
                  </h1>
                </div>
                <p style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.9)', margin: '0' }}>
                  إدارة الموارد البشرية - Complete HR Management System
                </p>
              </div>

              <button
                onClick={() => navigate('/')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 24px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '12px',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'
                  e.currentTarget.style.transform = 'scale(1.05)'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'
                  e.currentTarget.style.transform = 'scale(1)'
                }}
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {statCards.map((card, index) => {
            const Icon = card.icon
            return (
              <div
                key={index}
                style={{
                  background: 'white',
                  borderRadius: '16px',
                  padding: '24px',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)'
                  e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                }}
              >
                {/* Gradient Background Element */}
                <div style={{
                  position: 'absolute',
                  top: '0',
                  right: '0',
                  width: '120px',
                  height: '120px',
                  background: `linear-gradient(135deg, ${card.gradient})`,
                  opacity: '0.1',
                  borderRadius: '0 16px 0 100%'
                }}></div>

                <div style={{ position: 'relative', zIndex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <div style={{
                      padding: '12px',
                      borderRadius: '12px',
                      background: card.bgColor
                    }}>
                      <Icon size={24} className={card.iconColor} />
                    </div>
                    {card.trend === 'up' && (
                      <TrendingUp size={20} style={{ color: '#10b981' }} />
                    )}
                  </div>

                  <h3 style={{ fontSize: '28px', fontWeight: '700', color: '#1f2937', margin: '0 0 4px 0' }}>
                    {card.value}
                  </h3>
                  <p style={{ fontSize: '14px', fontWeight: '600', color: '#374151', margin: '0 0 4px 0' }}>
                    {card.title}
                  </p>
                  <p style={{ fontSize: '13px', color: '#6b7280', margin: '0' }}>
                    {card.change}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

        {/* Quick Actions Section */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '32px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          marginBottom: '32px'
        }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={24} style={{ color: '#667eea' }} />
            Quick Actions
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            {quickActions.map((action, index) => {
              const Icon = action.icon
              const colors = {
                blue: { bg: '#eff6ff', text: '#2563eb', hover: '#dbeafe' },
                green: { bg: '#f0fdf4', text: '#16a34a', hover: '#dcfce7' },
                orange: { bg: '#fff7ed', text: '#ea580c', hover: '#ffedd5' },
                purple: { bg: '#faf5ff', text: '#9333ea', hover: '#f3e8ff' },
                pink: { bg: '#fdf2f8', text: '#db2777', hover: '#fce7f3' },
                indigo: { bg: '#eef2ff', text: '#4f46e5', hover: '#e0e7ff' },
              }[action.color]

              return (
                <button
                  key={index}
                  onClick={() => navigate(action.path)}
                  style={{
                    background: colors.bg,
                    border: 'none',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = colors.hover
                    e.currentTarget.style.transform = 'scale(1.05)'
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = colors.bg
                    e.currentTarget.style.transform = 'scale(1)'
                  }}
                >
                  <Icon size={28} style={{ color: colors.text, marginBottom: '12px' }} />
                  <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937', margin: '0 0 4px 0' }}>
                    {action.title}
                  </h3>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '0' }}>
                    {action.description}
                  </p>
                  <ArrowUpRight size={16} style={{
                    position: 'absolute',
                    top: '16px',
                    right: '16px',
                    color: colors.text,
                    opacity: 0.6
                  }} />
                </button>
              )
            })}
          </div>
        </div>

        {/* Department & Performance Overview */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '24px' }}>
          {/* Departments Overview */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Building2 size={20} style={{ color: '#667eea' }} />
              Departments
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {metrics?.departments && Object.entries(metrics.departments).map(([name, data], index) => (
                <div key={index} style={{
                  padding: '16px',
                  borderRadius: '12px',
                  background: '#f9fafb',
                  border: '1px solid #e5e7eb'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: '600', color: '#374151', margin: '0', textTransform: 'capitalize' }}>
                      {name}
                    </h3>
                    <span style={{
                      padding: '4px 12px',
                      borderRadius: '12px',
                      background: '#dbeafe',
                      color: '#2563eb',
                      fontSize: '12px',
                      fontWeight: '600'
                    }}>
                      {data.employees} employees
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{
                      flex: 1,
                      height: '8px',
                      background: '#e5e7eb',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${data.attendance_rate}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                        borderRadius: '4px',
                        transition: 'width 0.3s ease'
                      }}></div>
                    </div>
                    <span style={{ fontSize: '12px', fontWeight: '600', color: '#059669' }}>
                      {data.attendance_rate}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Overview */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Award size={20} style={{ color: '#667eea' }} />
              Performance Metrics
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{
                padding: '20px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                color: 'white'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <Star size={24} />
                  <span style={{ fontSize: '14px', fontWeight: '500', opacity: 0.9 }}>Average Rating</span>
                </div>
                <div style={{ fontSize: '36px', fontWeight: '700' }}>
                  {metrics?.performance_metrics.average_rating.toFixed(1)} / 5.0
                </div>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '12px'
              }}>
                <div style={{
                  padding: '16px',
                  borderRadius: '12px',
                  background: '#dcfce7',
                  border: '1px solid #86efac'
                }}>
                  <CheckCircle size={20} style={{ color: '#16a34a', marginBottom: '8px' }} />
                  <div style={{ fontSize: '24px', fontWeight: '700', color: '#15803d' }}>
                    {metrics?.performance_metrics.completed_reviews}
                  </div>
                  <div style={{ fontSize: '12px', color: '#166534', fontWeight: '500' }}>
                    Completed
                  </div>
                </div>

                <div style={{
                  padding: '16px',
                  borderRadius: '12px',
                  background: '#fef3c7',
                  border: '1px solid #fcd34d'
                }}>
                  <AlertCircle size={20} style={{ color: '#d97706', marginBottom: '8px' }} />
                  <div style={{ fontSize: '24px', fontWeight: '700', color: '#b45309' }}>
                    {metrics?.performance_metrics.pending_reviews}
                  </div>
                  <div style={{ fontSize: '12px', color: '#92400e', fontWeight: '500' }}>
                    Pending
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Status Footer */}
        <div style={{
          marginTop: '32px',
          padding: '20px',
          background: '#f0fdf4',
          borderRadius: '12px',
          border: '1px solid #86efac'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <CheckCircle size={20} style={{ color: '#16a34a' }} />
            <span style={{ fontSize: '14px', fontWeight: '600', color: '#15803d' }}>
              All HR Systems Operational
            </span>
            <span style={{ fontSize: '12px', color: '#166534', marginLeft: 'auto' }}>
              Last updated: {new Date().toLocaleString()}
            </span>
          </div>
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
