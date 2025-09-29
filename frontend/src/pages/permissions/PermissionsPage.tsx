import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { permissionsApi } from '@/lib/api'
import { Plus, Shield, Users, UserCheck, Edit, Trash2, X, ArrowLeft } from 'lucide-react'

interface Permission {
  id: number
  name: string
  description: string
  category: string
  is_active: boolean
}

interface Role {
  id: number
  name: string
  description: string
  is_active: boolean
  permissions?: Permission[]
}

interface RoleCreateData {
  name: string
  description: string
  permission_ids: number[]
  is_active: boolean
}

export function PermissionsPage() {
  const [showAddRoleDialog, setShowAddRoleDialog] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [formData, setFormData] = useState<RoleCreateData>({
    name: '',
    description: '',
    permission_ids: [],
    is_active: true
  })

  const queryClient = useQueryClient()

  // Fetch roles
  const { data: roles = [], isLoading: rolesLoading, error: rolesError } = useQuery(
    'roles-with-permissions',
    () => permissionsApi.getRolesWithPermissions().then((res: any) => res.data),
    {
      onError: (error) => {
        console.error('Error fetching roles:', error)
        alert('Failed to load roles')
      }
    }
  )

  // Fetch permissions
  const { data: permissions = [], isLoading: permissionsLoading } = useQuery(
    'permissions',
    () => permissionsApi.getPermissions().then((res: any) => res.data),
    {
      onError: (error) => {
        console.error('Error fetching permissions:', error)
      }
    }
  )

  // Group permissions by category
  const permissionsByCategory = permissions.reduce((acc: Record<string, Permission[]>, permission: Permission) => {
    const category = permission.category || 'Other'
    if (!acc[category]) acc[category] = []
    acc[category].push(permission)
    return acc
  }, {})

  // Create role mutation
  const createRoleMutation = useMutation(
    (roleData: RoleCreateData) => permissionsApi.createRole(roleData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('roles-with-permissions')
        setShowAddRoleDialog(false)
        resetForm()
        alert('Role created successfully!')
      },
      onError: (error: any) => {
        console.error('Error creating role:', error)
        alert(error.response?.data?.detail || 'Failed to create role')
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name) {
      alert('Please enter a role name')
      return
    }

    createRoleMutation.mutate(formData)
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      permission_ids: [],
      is_active: true
    })
  }

  const handlePermissionToggle = (permissionId: number) => {
    setFormData(prev => ({
      ...prev,
      permission_ids: prev.permission_ids.includes(permissionId)
        ? prev.permission_ids.filter(id => id !== permissionId)
        : [...prev.permission_ids, permissionId]
    }))
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">🛡️ Permissions Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage user roles, permissions, and access control for TSH ERP System
          </p>
        </div>
        
        <Button 
          onClick={() => setShowAddRoleDialog(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          <span>Add New Role</span>
        </Button>
      </div>

      {/* Add Role Modal */}
      {showAddRoleDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Add New Role</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAddRoleDialog(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Role Name *</label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Sales Manager"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Status</label>
                  <select
                    value={formData.is_active ? 'active' : 'inactive'}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.value === 'active' }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe the role responsibilities..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">Permissions</label>
                <div className="space-y-4 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-4">
                  {Object.entries(permissionsByCategory).map(([category, categoryPermissions]) => (
                    <div key={category} className="space-y-2">
                      <h4 className="font-medium text-gray-900 capitalize">{category}</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {(categoryPermissions as Permission[]).map((permission: any) => (
                          <label key={permission.id} className="flex items-center space-x-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={formData.permission_ids.includes(permission.id)}
                              onChange={() => handlePermissionToggle(permission.id)}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">{permission.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowAddRoleDialog(false)}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Create Role
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Roles</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{roles.length}</div>
            <p className="text-xs text-muted-foreground">Active system roles</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Permissions</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{permissions.length}</div>
            <p className="text-xs text-muted-foreground">Available permissions</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Categories</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{Object.keys(permissionsByCategory).length}</div>
            <p className="text-xs text-muted-foreground">Permission categories</p>
          </CardContent>
        </Card>
      </div>

      {/* Roles Table */}
      <Card>
        <CardHeader>
          <CardTitle>System Roles</CardTitle>
          <CardDescription>
            {roles.length} roles configured • Manage role permissions and access levels
          </CardDescription>
        </CardHeader>
        <CardContent>
          {rolesLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading roles...</p>
            </div>
          ) : rolesError ? (
            <div className="text-center py-8">
              <p className="text-red-600">Error loading roles. Please try again.</p>
            </div>
          ) : roles.length === 0 ? (
            <div className="text-center py-8">
              <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No roles found</h3>
              <p className="text-gray-600">Get started by creating your first role.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-200 px-4 py-2 text-left">Role</th>
                    <th className="border border-gray-200 px-4 py-2 text-left">Description</th>
                    <th className="border border-gray-200 px-4 py-2 text-left">Status</th>
                    <th className="border border-gray-200 px-4 py-2 text-left">Users</th>
                    <th className="border border-gray-200 px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {roles.map((role: any) => (
                    <tr key={role.id} className="hover:bg-gray-50">
                      <td className="border border-gray-200 px-4 py-2">
                        <div className="flex items-center space-x-2">
                          <Shield className="h-4 w-4 text-blue-600" />
                          <span className="font-medium">{role.name}</span>
                        </div>
                      </td>
                      <td className="border border-gray-200 px-4 py-2">
                        <span className="text-gray-600">{role.description || 'No description'}</span>
                      </td>
                      <td className="border border-gray-200 px-4 py-2">
                        <Badge variant={role.is_active ? 'default' : 'secondary'}>
                          {role.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="border border-gray-200 px-4 py-2">
                        <span className="text-gray-600">-</span>
                      </td>
                      <td className="border border-gray-200 px-4 py-2">
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Permissions Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Permissions Overview</CardTitle>
          <CardDescription>
            Available system permissions organized by category
          </CardDescription>
        </CardHeader>
        <CardContent>
          {permissionsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading permissions...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(permissionsByCategory).map(([category, categoryPermissions]) => (
                <div key={category} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3 capitalize flex items-center">
                    <Shield className="h-4 w-4 mr-2 text-blue-600" />
                    {category}
                  </h4>
                  <div className="space-y-1">
                    {(categoryPermissions as Permission[]).map((permission: any) => (
                      <div key={permission.id} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">{permission.name}</span>
                        <Badge variant={permission.is_active ? 'default' : 'secondary'} className="text-xs">
                          {permission.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
