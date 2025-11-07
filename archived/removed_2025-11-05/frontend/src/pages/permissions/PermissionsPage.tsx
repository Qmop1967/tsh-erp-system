import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { permissionsApi } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import {
  Plus,
  Shield,
  Users,
  UserCheck,
  Edit,
  Trash2,
  X,
  ArrowLeft,
  Search,
  Filter,
  Settings,
  Lock,
  Unlock,
  Eye,
  Database,
  FileText,
  ShoppingCart,
  Briefcase,
  DollarSign,
  Package,
  Building,
  UserCog,
  TrendingUp,
  CheckCircle2,
  XCircle
} from 'lucide-react'

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

// Category icons and colors mapping
const categoryConfig: Record<string, { icon: any; color: string; gradient: string; bgColor: string }> = {
  'User': {
    icon: Users,
    color: 'text-blue-600',
    gradient: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20'
  },
  'Branch': {
    icon: Building,
    color: 'text-purple-600',
    gradient: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20'
  },
  'Product': {
    icon: Package,
    color: 'text-green-600',
    gradient: 'from-green-500 to-green-600',
    bgColor: 'bg-green-50 dark:bg-green-900/20'
  },
  'Inventory': {
    icon: Database,
    color: 'text-orange-600',
    gradient: 'from-orange-500 to-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20'
  },
  'Sales': {
    icon: ShoppingCart,
    color: 'text-pink-600',
    gradient: 'from-pink-500 to-pink-600',
    bgColor: 'bg-pink-50 dark:bg-pink-900/20'
  },
  'Customer': {
    icon: UserCog,
    color: 'text-indigo-600',
    gradient: 'from-indigo-500 to-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-900/20'
  },
  'Financial': {
    icon: DollarSign,
    color: 'text-emerald-600',
    gradient: 'from-emerald-500 to-emerald-600',
    bgColor: 'bg-emerald-50 dark:bg-emerald-900/20'
  },
  'Reports': {
    icon: TrendingUp,
    color: 'text-cyan-600',
    gradient: 'from-cyan-500 to-cyan-600',
    bgColor: 'bg-cyan-50 dark:bg-cyan-900/20'
  },
  'Settings': {
    icon: Settings,
    color: 'text-gray-600',
    gradient: 'from-gray-500 to-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-900/20'
  },
  'Other': {
    icon: Shield,
    color: 'text-slate-600',
    gradient: 'from-slate-500 to-slate-600',
    bgColor: 'bg-slate-50 dark:bg-slate-900/20'
  }
}

export function PermissionsPage() {
  const navigate = useNavigate()
  const { checkAuthentication } = useAuthStore()
  const [showAddRoleDialog, setShowAddRoleDialog] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [formData, setFormData] = useState<RoleCreateData>({
    name: '',
    description: '',
    permission_ids: [],
    is_active: true
  })

  const queryClient = useQueryClient()

  useEffect(() => {
    checkAuthentication()
  }, [checkAuthentication])

  // Fetch roles
  const { data: roles = [], isLoading: rolesLoading, error: rolesError } = useQuery(
    'roles-with-permissions',
    () => permissionsApi.getRolesWithPermissions().then((res: any) => res.data),
    {
      onError: (error) => {
        console.error('Error fetching roles:', error)
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

  // Filter permissions based on search and category
  const filteredPermissions = permissions.filter((permission: Permission) => {
    const matchesSearch = permission.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         permission.description?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || permission.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  // Create role mutation
  const createRoleMutation = useMutation(
    (roleData: RoleCreateData) => permissionsApi.createRole(roleData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('roles-with-permissions')
        setShowAddRoleDialog(false)
        resetForm()
      },
      onError: (error: any) => {
        console.error('Error creating role:', error)
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name) return
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

  const getCategoryIcon = (category: string) => {
    const config = categoryConfig[category] || categoryConfig['Other']
    const IconComponent = config.icon
    return <IconComponent className={`h-5 w-5 ${config.color}`} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Page Header with Gradient */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-8 shadow-2xl">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                    <Shield className="h-8 w-8 text-white" />
                  </div>
                  <h1 className="text-4xl font-bold text-white">Permissions Management</h1>
                </div>
                <p className="text-blue-100 text-lg max-w-2xl">
                  Advanced role-based access control system for managing user permissions and security policies
                </p>
              </div>

              <Button
                onClick={() => setShowAddRoleDialog(true)}
                className="bg-white text-blue-600 hover:bg-blue-50 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                size="lg"
              >
                <Plus className="h-5 w-5 mr-2" />
                <span className="font-semibold">Create Role</span>
              </Button>
            </div>
          </div>

          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-32 translate-x-32"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-24 -translate-x-24"></div>
        </div>

        {/* Stats Cards with Modern Design */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-none shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg">
                  <Shield className="h-6 w-6 text-white" />
                </div>
                <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  {roles.length}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">Total Roles</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Active system roles</p>
            </CardContent>
          </Card>

          <Card className="border-none shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg">
                  <UserCheck className="h-6 w-6 text-white" />
                </div>
                <span className="text-3xl font-bold bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent">
                  {permissions.length}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">Permissions</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Total permissions</p>
            </CardContent>
          </Card>

          <Card className="border-none shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg">
                  <Users className="h-6 w-6 text-white" />
                </div>
                <span className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent">
                  {Object.keys(permissionsByCategory).length}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">Categories</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Permission groups</p>
            </CardContent>
          </Card>

          <Card className="border-none shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg">
                  <CheckCircle2 className="h-6 w-6 text-white" />
                </div>
                <span className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-orange-800 bg-clip-text text-transparent">
                  {permissions.filter((p: Permission) => p.is_active).length}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">Active</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Enabled permissions</p>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter Bar */}
        <Card className="border-none shadow-lg">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  placeholder="Search permissions by name or description..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-12 border-2 border-gray-200 focus:border-blue-500 rounded-xl"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Filter className="h-5 w-5 text-gray-400" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 bg-white dark:bg-gray-800"
                >
                  <option value="all">All Categories</option>
                  {Object.keys(permissionsByCategory).map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Permissions Grid - Beautiful Cards */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Permission Categories</h2>
            <Badge variant="outline" className="text-sm">
              {filteredPermissions.length} permissions
            </Badge>
          </div>

          {permissionsLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading permissions...</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(permissionsByCategory)
                .filter(([category]) => selectedCategory === 'all' || category === selectedCategory)
                .map(([category, categoryPermissions]) => {
                  const config = categoryConfig[category] || categoryConfig['Other']
                  const IconComponent = config.icon

                  return (
                    <Card
                      key={category}
                      className={`border-none shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 ${config.bgColor}`}
                    >
                      <CardHeader className="pb-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`p-3 bg-gradient-to-br ${config.gradient} rounded-xl shadow-lg`}>
                              <IconComponent className="h-6 w-6 text-white" />
                            </div>
                            <div>
                              <CardTitle className="text-lg font-bold text-gray-900 dark:text-white">
                                {category}
                              </CardTitle>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                {(categoryPermissions as Permission[]).length} permissions
                              </p>
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                          {(categoryPermissions as Permission[])
                            .filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
                            .map((permission: Permission) => (
                              <div
                                key={permission.id}
                                className="flex items-center justify-between p-3 rounded-lg bg-white/50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-700 transition-all duration-200 group"
                              >
                                <div className="flex items-center space-x-3 flex-1">
                                  {permission.is_active ? (
                                    <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                                  ) : (
                                    <XCircle className="h-4 w-4 text-gray-400 flex-shrink-0" />
                                  )}
                                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white">
                                    {permission.name}
                                  </span>
                                </div>
                                <Badge
                                  variant={permission.is_active ? 'default' : 'secondary'}
                                  className="text-xs"
                                >
                                  {permission.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
            </div>
          )}
        </div>

        {/* Roles Section */}
        <Card className="border-none shadow-xl">
          <CardHeader className="border-b bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-900">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white">System Roles</CardTitle>
                <CardDescription className="text-base mt-1">
                  Manage role permissions and access levels across the system
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            {rolesLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading roles...</p>
              </div>
            ) : rolesError ? (
              <div className="text-center py-12">
                <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 font-medium">Failed to load roles</p>
              </div>
            ) : roles.length === 0 ? (
              <div className="text-center py-12">
                <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No roles found</h3>
                <p className="text-gray-600 dark:text-gray-400">Create your first role to get started</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {roles.map((role: any) => (
                  <div
                    key={role.id}
                    className="p-6 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-800"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
                          <Shield className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h4 className="font-bold text-gray-900 dark:text-white">{role.name}</h4>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {role.permissions?.length || 0} permissions
                          </p>
                        </div>
                      </div>
                      <Badge variant={role.is_active ? 'default' : 'secondary'}>
                        {role.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                      {role.description || 'No description provided'}
                    </p>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                      <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700 hover:bg-red-50">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Add Role Modal - keeping the original functionality */}
      {showAddRoleDialog && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-white/20 rounded-lg">
                    <Plus className="h-6 w-6 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">Create New Role</h2>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAddRoleDialog(false)}
                  className="text-white hover:bg-white/20"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Role Name *</label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Sales Manager"
                    className="h-12"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Status</label>
                  <select
                    value={formData.is_active ? 'active' : 'inactive'}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.value === 'active' }))}
                    className="w-full h-12 px-4 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 bg-white dark:bg-gray-700"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe the role responsibilities..."
                  className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 bg-white dark:bg-gray-700"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Select Permissions</label>
                <div className="space-y-4 max-h-96 overflow-y-auto border-2 border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-900/50">
                  {Object.entries(permissionsByCategory).map(([category, categoryPermissions]) => (
                    <div key={category} className="space-y-2">
                      <h4 className="font-semibold text-gray-900 dark:text-white capitalize flex items-center">
                        {getCategoryIcon(category)}
                        <span className="ml-2">{category}</span>
                      </h4>
                      <div className="grid grid-cols-2 gap-2 pl-7">
                        {(categoryPermissions as Permission[]).map((permission: any) => (
                          <label key={permission.id} className="flex items-center space-x-2 cursor-pointer hover:bg-white dark:hover:bg-gray-800 p-2 rounded-lg transition-colors">
                            <input
                              type="checkbox"
                              checked={formData.permission_ids.includes(permission.id)}
                              onChange={() => handlePermissionToggle(permission.id)}
                              className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700 dark:text-gray-300">{permission.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowAddRoleDialog(false)}
                  className="px-6"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  Create Role
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
    </div>
  )
}
