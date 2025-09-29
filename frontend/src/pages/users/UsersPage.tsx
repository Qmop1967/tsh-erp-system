import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { usersApi } from '@/lib/api'
import { Plus, Users, UserCheck, Shield, Edit, Trash2, Eye, EyeOff, X, ArrowLeft } from 'lucide-react'

interface UserCreateData {
  name: string
  email: string
  password: string
  role_id: number
  branch_id: number
  phone?: string
  employee_code?: string
  is_active: boolean
}

interface UserUpdateData {
  name?: string
  email?: string
  password?: string
  role_id?: number
  branch_id?: number
  phone?: string
  employee_code?: string
  is_active?: boolean
}

export function UsersPage() {
  const navigate = useNavigate()
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [editingUser, setEditingUser] = useState<any>(null)
  const [deletingUser, setDeletingUser] = useState<any>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [usersPerPage] = useState(10)
  const [formData, setFormData] = useState<UserCreateData>({
    name: '',
    email: '',
    password: '',
    role_id: 0,
    branch_id: 0,
    phone: '',
    employee_code: '',
    is_active: true
  })
  const [editFormData, setEditFormData] = useState<UserUpdateData>({})

  const queryClient = useQueryClient()

  // Fetch users with pagination
  const { data: usersResponse, isLoading: usersLoading, error: usersError } = useQuery(
    ['users', currentPage],
    () => usersApi.getUsers({ page: currentPage, limit: usersPerPage }).then(res => res.data),
    {
      onError: (error) => {
        console.error('Error fetching users:', error)
        alert('Failed to load users')
      },
      keepPreviousData: true
    }
  )

  // For backward compatibility, handle both array and paginated response
  const users = Array.isArray(usersResponse) ? usersResponse : ((usersResponse as any)?.data || [])
  const totalUsersCount = Array.isArray(usersResponse) ? usersResponse.length : ((usersResponse as any)?.total || users.length)
  const totalPages = Array.isArray(usersResponse) ? Math.ceil(usersResponse.length / usersPerPage) : ((usersResponse as any)?.pages || Math.ceil(totalUsersCount / usersPerPage))

  // Fetch roles for dropdown
  const { data: roles = [] } = useQuery(
    'roles',
    () => usersApi.getRoles().then(res => res.data),
    {
      onError: (error) => {
        console.error('Error fetching roles:', error)
      }
    }
  )

  // Fetch branches for dropdown
  const { data: branches = [] } = useQuery(
    'branches',
    () => usersApi.getBranches().then(res => res.data),
    {
      onError: (error) => {
        console.error('Error fetching branches:', error)
      }
    }
  )

  // Create user mutation
  const createUserMutation = useMutation(
    (userData: UserCreateData) => usersApi.createUser(userData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['users', currentPage])
        queryClient.invalidateQueries('users') // Invalidate all user queries
        setShowAddDialog(false)
        setFormData({
          name: '',
          email: '',
          password: '',
          role_id: 0,
          branch_id: 0,
          phone: '',
          employee_code: '',
          is_active: true
        })
        alert('User created successfully!')
      },
      onError: (error: any) => {
        console.error('Error creating user:', error)
        alert(error.response?.data?.detail || 'Failed to create user')
      }
    }
  )

  // Update user mutation
  const updateUserMutation = useMutation(
    ({ id, data }: { id: number; data: UserUpdateData }) => usersApi.updateUser(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['users', currentPage])
        queryClient.invalidateQueries('users')
        setShowEditDialog(false)
        setEditingUser(null)
        setEditFormData({})
        alert('User updated successfully!')
      },
      onError: (error: any) => {
        console.error('Error updating user:', error)
        alert(error.response?.data?.detail || 'Failed to update user')
      }
    }
  )

  // Delete user mutation
  const deleteUserMutation = useMutation(
    (userId: number) => usersApi.deleteUser(userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['users', currentPage])
        queryClient.invalidateQueries('users')
        setShowDeleteDialog(false)
        setDeletingUser(null)
        alert('User deleted successfully!')
      },
      onError: (error: any) => {
        console.error('Error deleting user:', error)
        alert(error.response?.data?.detail || 'Failed to delete user')
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.name || !formData.email || !formData.password) {
      alert('Please fill in all required fields')
      return
    }
    
    if (!formData.role_id || !formData.branch_id) {
      alert('Please select a role and branch')
      return
    }

    createUserMutation.mutate(formData)
  }

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!editingUser) return
    
    // Validation
    if (editFormData.email && !editFormData.email.includes('@')) {
      alert('Please enter a valid email address')
      return
    }

    updateUserMutation.mutate({ id: editingUser.id, data: editFormData })
  }

  const handleDeleteConfirm = () => {
    if (!deletingUser) return
    deleteUserMutation.mutate(deletingUser.id)
  }

  const handleEditUser = (user: any) => {
    setEditingUser(user)
    setEditFormData({
      name: user.name,
      email: user.email,
      role_id: user.role_id,
      branch_id: user.branch_id,
      phone: user.phone || '',
      employee_code: user.employee_code || '',
      is_active: user.is_active
    })
    setShowEditDialog(true)
  }

  const handleDeleteUser = (user: any) => {
    setDeletingUser(user)
    setShowDeleteDialog(true)
  }

  const handleInputChange = (field: keyof UserCreateData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleEditInputChange = (field: keyof UserUpdateData, value: any) => {
    setEditFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  // Calculate stats
  const activeUsers = users.filter((user: any) => user.is_active || user.isActive).length
  const adminUsers = users.filter((user: any) => 
    user.role === 'Admin' || (user.role && user.role.toLowerCase().includes('admin'))
  ).length

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Dashboard</span>
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">🔐 TSH ERP System Users</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Manage TSH ERP system users, roles, and permissions
            </p>
          </div>
        </div>
        
        <Button 
          onClick={() => setShowAddDialog(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          <span>Add New User</span>
        </Button>
      </div>

      {/* Add User Modal */}
      {showAddDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Add New User</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAddDialog(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Full Name *</label>
                  <Input
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="John Doe"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Employee Code</label>
                  <Input
                    value={formData.employee_code}
                    onChange={(e) => handleInputChange('employee_code', e.target.value)}
                    placeholder="EMP001"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Email Address *</label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="john.doe@tsh.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Phone Number</label>
                <Input
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  placeholder="+964 xxx xxxx xxx"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Password *</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    placeholder="Enter secure password"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Role *</label>
                  <select
                    value={formData.role_id}
                    onChange={(e) => handleInputChange('role_id', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value={0}>Select role</option>
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Branch *</label>
                  <select
                    value={formData.branch_id}
                    onChange={(e) => handleInputChange('branch_id', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value={0}>Select branch</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>
                        {branch.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowAddDialog(false)}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={createUserMutation.isLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {createUserMutation.isLoading ? 'Creating...' : 'Create User'}
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
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{totalUsersCount}</div>
            <p className="text-xs text-muted-foreground">All system users</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{activeUsers}</div>
            <p className="text-xs text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Admin Users</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{adminUsers}</div>
            <p className="text-xs text-muted-foreground">Administrator access</p>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>TSH ERP Users</CardTitle>
          <CardDescription>
            {totalUsersCount} users found • Manage user accounts, roles, and system access
          </CardDescription>
        </CardHeader>
        <CardContent>
          {usersLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading users...</p>
            </div>
          ) : usersError ? (
            <div className="text-center py-8">
              <p className="text-red-600">Error loading users. Please try again.</p>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
              <p className="text-gray-600">Get started by adding your first user.</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-200">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 px-4 py-2 text-left">User</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Email</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Role</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Branch</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Status</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user: any) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="border border-gray-200 px-4 py-2">
                          <div>
                            <div className="font-medium">{user.name}</div>
                            {user.employee_code && (
                              <div className="text-sm text-gray-500">{user.employee_code}</div>
                            )}
                          </div>
                        </td>
                        <td className="border border-gray-200 px-4 py-2">{user.email}</td>
                        <td className="border border-gray-200 px-4 py-2">
                          <Badge variant={user.role === 'Admin' ? 'destructive' : 'secondary'}>
                            {user.role || 'Unknown'}
                          </Badge>
                        </td>
                        <td className="border border-gray-200 px-4 py-2">{user.branch || 'Unknown'}</td>
                        <td className="border border-gray-200 px-4 py-2">
                          <Badge variant={user.is_active || user.isActive ? 'default' : 'secondary'}>
                            {user.is_active || user.isActive ? 'Active' : 'Inactive'}
                          </Badge>
                        </td>
                        <td className="border border-gray-200 px-4 py-2">
                          <div className="flex items-center space-x-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => handleEditUser(user)}
                              disabled={updateUserMutation.isLoading}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => handleDeleteUser(user)}
                              disabled={deleteUserMutation.isLoading}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-gray-700">
                    Showing page {currentPage} of {totalPages}
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <span className="text-sm text-gray-600">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Edit User Modal */}
      {showEditDialog && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Edit User</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowEditDialog(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Full Name</label>
                  <Input
                    value={editFormData.name || ''}
                    onChange={(e) => handleEditInputChange('name', e.target.value)}
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Employee Code</label>
                  <Input
                    value={editFormData.employee_code || ''}
                    onChange={(e) => handleEditInputChange('employee_code', e.target.value)}
                    placeholder="EMP001"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Email Address</label>
                <Input
                  type="email"
                  value={editFormData.email || ''}
                  onChange={(e) => handleEditInputChange('email', e.target.value)}
                  placeholder="john.doe@tsh.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Phone Number</label>
                <Input
                  value={editFormData.phone || ''}
                  onChange={(e) => handleEditInputChange('phone', e.target.value)}
                  placeholder="+964 xxx xxxx xxx"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">New Password (leave empty to keep current)</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={editFormData.password || ''}
                    onChange={(e) => handleEditInputChange('password', e.target.value)}
                    placeholder="Enter new password or leave empty"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Role</label>
                  <select
                    value={editFormData.role_id || 0}
                    onChange={(e) => handleEditInputChange('role_id', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={0}>Select role</option>
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Branch</label>
                  <select
                    value={editFormData.branch_id || 0}
                    onChange={(e) => handleEditInputChange('branch_id', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={0}>Select branch</option>
                    {branches.map((branch) => (
                      <option key={branch.id} value={branch.id}>
                        {branch.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={editFormData.is_active ?? true}
                  onChange={(e) => handleEditInputChange('is_active', e.target.checked)}
                  className="rounded border-gray-300 focus:ring-blue-500"
                />
                <label htmlFor="is_active" className="text-sm font-medium">Active User</label>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowEditDialog(false)}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={updateUserMutation.isLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {updateUserMutation.isLoading ? 'Updating...' : 'Update User'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete User Modal */}
      {showDeleteDialog && deletingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-red-600">Delete User</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDeleteDialog(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-4">
              <p className="text-gray-700">
                Are you sure you want to delete the user <strong>{deletingUser.name}</strong>?
              </p>
              <p className="text-sm text-red-600">
                This action cannot be undone. All data associated with this user will be permanently removed.
              </p>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowDeleteDialog(false)}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleDeleteConfirm}
                  disabled={deleteUserMutation.isLoading}
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  {deleteUserMutation.isLoading ? 'Deleting...' : 'Delete User'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
