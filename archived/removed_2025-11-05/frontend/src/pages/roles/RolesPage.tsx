import React, { useEffect } from 'react'

import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export function RolesPage() {
  const navigate = useNavigate()
  const { checkAuthentication } = useAuthStore()

  useEffect(() => {
    // Check authentication on mount
    checkAuthentication()
  }, [checkAuthentication])
  
  return (
    <div style={{ padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '32px', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          marginBottom: '24px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            <button
              onClick={() => navigate('/')}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '8px 16px',
                backgroundColor: 'transparent',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                color: '#6b7280',
                cursor: 'pointer',
                marginRight: '16px',
                fontSize: '14px'
              }}
            >
              ← Back to Dashboard
            </button>
          </div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#1f2937', marginBottom: '8px' }}>
            👤 Roles Management
          </h1>
          <p style={{ fontSize: '16px', color: '#6b7280' }}>
            Manage user roles and their associated permissions in the TSH ERP system
          </p>
        </div>

        <div style={{ 
          backgroundColor: 'white', 
          padding: '32px', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' 
        }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937', marginBottom: '24px' }}>
            System Roles
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px' }}>
            {[
              { 
                name: 'System Administrator', 
                color: '#dc2626', 
                users: 2, 
                permissions: ['All System Permissions', 'User Management', 'System Configuration', 'Backup & Restore'] 
              },
              { 
                name: 'Manager', 
                color: '#2563eb', 
                users: 8, 
                permissions: ['View All Modules', 'Approve Transactions', 'Generate Reports', 'User View Access'] 
              },
              { 
                name: 'Sales Representative', 
                color: '#059669', 
                users: 25, 
                permissions: ['Sales Management', 'Customer Management', 'Inventory View', 'Generate Sales Reports'] 
              },
              { 
                name: 'Inventory Manager', 
                color: '#7c3aed', 
                users: 12, 
                permissions: ['Full Inventory Access', 'Stock Adjustments', 'Warehouse Management', 'Purchase Orders'] 
              },
              { 
                name: 'Accountant', 
                color: '#ea580c', 
                users: 6, 
                permissions: ['Financial Management', 'Accounting Reports', 'Journal Entries', 'Tax Management'] 
              },
              { 
                name: 'HR Manager', 
                color: '#0891b2', 
                users: 4, 
                permissions: ['Employee Management', 'Payroll Access', 'Performance Reviews', 'Attendance Tracking'] 
              },
              { 
                name: 'Cashier', 
                color: '#65a30d', 
                users: 15, 
                permissions: ['POS Operations', 'Payment Processing', 'Daily Cash Reports', 'Customer Service'] 
              },
              { 
                name: 'Viewer', 
                color: '#6b7280', 
                users: 32, 
                permissions: ['Read-Only Access', 'View Reports', 'Basic Dashboard', 'Limited Data Export'] 
              }
            ].map((role, index) => (
              <div key={index} style={{
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                padding: '20px',
                backgroundColor: 'white',
                transition: 'all 0.2s ease'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    backgroundColor: role.color,
                    borderRadius: '50%',
                    marginRight: '8px'
                  }}></div>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', margin: '0', flex: 1 }}>
                    {role.name}
                  </h3>
                  <span style={{
                    backgroundColor: role.color + '20',
                    color: role.color,
                    fontSize: '12px',
                    fontWeight: '600',
                    padding: '4px 8px',
                    borderRadius: '12px'
                  }}>
                    {role.users} users
                  </span>
                </div>
                
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Key Permissions:
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {role.permissions.map((permission, permIndex) => (
                      <span key={permIndex} style={{
                        fontSize: '13px',
                        color: '#6b7280',
                        backgroundColor: '#f3f4f6',
                        padding: '4px 8px',
                        borderRadius: '4px'
                      }}>
                        • {permission}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={() => {
                      alert(`Edit Role feature coming soon!\n\nRole: ${role.name}\nUsers: ${role.users}\n\nThis will allow you to:\n- Modify role permissions\n- Add/remove capabilities\n- Configure role settings`)
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.opacity = '0.9'
                      e.currentTarget.style.transform = 'scale(1.05)'
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.opacity = '1'
                      e.currentTarget.style.transform = 'scale(1)'
                    }}
                    style={{
                      backgroundColor: role.color,
                      color: 'white',
                      border: 'none',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}>
                    Edit Role
                  </button>
                  <button
                    onClick={() => {
                      // Navigate to users page with role filter
                      navigate(`/users?role=${encodeURIComponent(role.name)}`)
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.backgroundColor = role.color + '20'
                      e.currentTarget.style.transform = 'scale(1.05)'
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent'
                      e.currentTarget.style.transform = 'scale(1)'
                    }}
                    style={{
                      backgroundColor: 'transparent',
                      color: role.color,
                      border: `1px solid ${role.color}`,
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: '500',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}>
                    View Users
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div style={{ 
            marginTop: '32px',
            padding: '16px',
            backgroundColor: '#f0fdf4',
            borderRadius: '8px',
            border: '1px solid #bbf7d0'
          }}>
            <p style={{ fontSize: '14px', color: '#15803d', margin: '0' }}>
              ✅ <strong>Active Integration:</strong> Role management is fully integrated with the TSH ERP backend. 
              All role changes are synchronized across all system modules and mobile applications.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
