import { useState, useEffect } from 'react'
import { Shield, Users, Key, Activity, Search, Plus, Edit2, Trash2, AlertTriangle } from 'lucide-react'

interface Permission {
  id: number
  name: string
  description: string
  resource_type: string
  permission_type: string
  is_active: boolean
}

interface Role {
  id: number
  name: string
  description: string
  is_active: boolean
  permissions_count: number
}

interface AuditLog {
  id: number
  user_id: number
  user_name?: string
  action: string
  resource_type: string
  resource_id?: string
  ip_address?: string
  timestamp: string
}

interface UserPermission {
  id: number
  user_id: number
  user_name?: string
  permission_id: number
  permission_name?: string
  is_granted: boolean
  granted_by?: number
  granted_at: string
  expires_at?: string
}

export function SecurityManagementPage() {
  const [activeTab, setActiveTab] = useState<'permissions' | 'roles' | 'audit' | 'user-permissions'>('permissions')
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [userPermissions, setUserPermissions] = useState<UserPermission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchSecurityData()
  }, [activeTab])

  const fetchSecurityData = async () => {
    try {
      setLoading(true)
      
      // Mock data for demonstration - in real implementation, fetch from /api/security endpoints
      const mockPermissions: Permission[] = [
        { id: 1, name: 'users.view', description: 'View users', resource_type: 'USER', permission_type: 'READ', is_active: true },
        { id: 2, name: 'users.create', description: 'Create users', resource_type: 'USER', permission_type: 'CREATE', is_active: true },
        { id: 3, name: 'products.view', description: 'View products', resource_type: 'PRODUCT', permission_type: 'READ', is_active: true },
        { id: 4, name: 'sales.create', description: 'Create sales', resource_type: 'SALES', permission_type: 'CREATE', is_active: true },
        { id: 5, name: 'reports.export', description: 'Export reports', resource_type: 'REPORTS', permission_type: 'EXPORT', is_active: true }
      ]

      const mockRoles: Role[] = [
        { id: 1, name: 'Admin', description: 'Full system access', is_active: true, permissions_count: 25 },
        { id: 2, name: 'Manager', description: 'Management level access', is_active: true, permissions_count: 15 },
        { id: 3, name: 'Sales Rep', description: 'Sales operations access', is_active: true, permissions_count: 8 },
        { id: 4, name: 'Inventory Clerk', description: 'Inventory management access', is_active: true, permissions_count: 6 }
      ]

      const mockAuditLogs: AuditLog[] = [
        { id: 1, user_id: 1, user_name: 'Admin User', action: 'LOGIN', resource_type: 'USER', ip_address: '192.168.1.100', timestamp: '2024-08-14T09:30:00Z' },
        { id: 2, user_id: 2, user_name: 'John Smith', action: 'CREATE', resource_type: 'CUSTOMER', resource_id: '123', ip_address: '192.168.1.101', timestamp: '2024-08-14T09:25:00Z' },
        { id: 3, user_id: 3, user_name: 'Sarah Johnson', action: 'UPDATE', resource_type: 'PRODUCT', resource_id: '456', ip_address: '192.168.1.102', timestamp: '2024-08-14T09:20:00Z' },
        { id: 4, user_id: 1, user_name: 'Admin User', action: 'DELETE', resource_type: 'USER', resource_id: '789', ip_address: '192.168.1.100', timestamp: '2024-08-14T09:15:00Z' }
      ]

      const mockUserPermissions: UserPermission[] = [
        { id: 1, user_id: 2, user_name: 'John Smith', permission_id: 1, permission_name: 'users.view', is_granted: true, granted_by: 1, granted_at: '2024-08-01T10:00:00Z' },
        { id: 2, user_id: 2, user_name: 'John Smith', permission_id: 3, permission_name: 'products.view', is_granted: true, granted_by: 1, granted_at: '2024-08-01T10:00:00Z' },
        { id: 3, user_id: 3, user_name: 'Sarah Johnson', permission_id: 4, permission_name: 'sales.create', is_granted: false, granted_by: 1, granted_at: '2024-08-01T10:00:00Z', expires_at: '2024-12-31T23:59:59Z' }
      ]

      setPermissions(mockPermissions)
      setRoles(mockRoles)
      setAuditLogs(mockAuditLogs)
      setUserPermissions(mockUserPermissions)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleGrantPermission = async (userId: number, permissionId: number) => {
    try {
      // In real implementation, call /api/security/permissions/grant
      console.log(`Granting permission ${permissionId} to user ${userId}`)
      await fetchSecurityData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const handleRevokePermission = async (userId: number, permissionId: number) => {
    try {
      // In real implementation, call /api/security/permissions/revoke
      console.log(`Revoking permission ${permissionId} from user ${userId}`)
      await fetchSecurityData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const filteredData = () => {
    switch (activeTab) {
      case 'permissions':
        return permissions.filter(p => 
          p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.description.toLowerCase().includes(searchTerm.toLowerCase())
        )
      case 'roles':
        return roles.filter(r => 
          r.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          r.description.toLowerCase().includes(searchTerm.toLowerCase())
        )
      case 'audit':
        return auditLogs.filter(log => 
          log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.resource_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.user_name?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      case 'user-permissions':
        return userPermissions.filter(up => 
          up.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          up.permission_name?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      default:
        return []
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'LOGIN': return 'bg-blue-100 text-blue-800'
      case 'CREATE': return 'bg-green-100 text-green-800'
      case 'UPDATE': return 'bg-yellow-100 text-yellow-800'
      case 'DELETE': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">🔒 Security Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage permissions, roles, and security auditing
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Security Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Key className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Permissions</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{permissions.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Roles</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {roles.filter(r => r.is_active).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Activity className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Recent Activities</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{auditLogs.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Security Alerts</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">2</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'permissions', label: 'Permissions', icon: Key },
              { id: 'roles', label: 'Roles', icon: Users },
              { id: 'user-permissions', label: 'User Permissions', icon: Shield },
              { id: 'audit', label: 'Audit Logs', icon: Activity }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Search */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'permissions' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">System Permissions</h3>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Add Permission
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredData().map((permission: any) => (
                  <div key={permission.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">{permission.name}</h4>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        permission.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {permission.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{permission.description}</p>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>{permission.resource_type}</span>
                      <span>{permission.permission_type}</span>
                    </div>
                    <div className="flex justify-end gap-2 mt-3">
                      <button className="text-blue-600 hover:text-blue-800">
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-800">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'roles' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">User Roles</h3>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Add Role
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredData().map((role: any) => (
                  <div key={role.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">{role.name}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{role.description}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        role.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {role.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">{role.permissions_count} permissions</span>
                      <div className="flex gap-2">
                        <button className="text-blue-600 hover:text-blue-800">
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-800">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'user-permissions' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">User-Specific Permissions</h3>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-900">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Permission
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Granted Date
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {filteredData().map((userPerm: any) => (
                      <tr key={userPerm.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {userPerm.user_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 dark:text-white">{userPerm.permission_name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            userPerm.is_granted ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {userPerm.is_granted ? 'Granted' : 'Revoked'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {new Date(userPerm.granted_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            {userPerm.is_granted ? (
                              <button
                                onClick={() => handleRevokePermission(userPerm.user_id, userPerm.permission_id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Revoke
                              </button>
                            ) : (
                              <button
                                onClick={() => handleGrantPermission(userPerm.user_id, userPerm.permission_id)}
                                className="text-green-600 hover:text-green-900"
                              >
                                Grant
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'audit' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Security Audit Logs</h3>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-900">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Action
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Resource
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        IP Address
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Timestamp
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {filteredData().map((log: any) => (
                      <tr key={log.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {log.user_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(log.action)}`}>
                            {log.action}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 dark:text-white">
                            {log.resource_type}
                            {log.resource_id && <span className="text-gray-500"> #{log.resource_id}</span>}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {log.ip_address}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
