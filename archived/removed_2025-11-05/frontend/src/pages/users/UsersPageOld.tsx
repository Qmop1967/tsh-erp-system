import { useState } from 'react'
import { useQuery } from 'react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { usersApi } from '@/lib/api'
import { User } from '@/types'
import { Plus, Search, Filter, MoreHorizontal, Edit, Trash2, Users, UserCheck, Shield } from 'lucide-react'
import { formatDate } from '@/lib/utils'

export function UsersPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const limit = 10

  const { data: usersData, isLoading, error } = useQuery(
    ['users', page, searchTerm],
    () => usersApi.getUsers({ page, limit, search: searchTerm }),
    {
      keepPreviousData: true,
      staleTime: 5 * 60 * 1000,
    }
  )

  const users = usersData?.data || []
  const totalPages = Math.ceil(users.length / limit) || 1

  // Simple test to see if component renders
  if (users.length === 0 && !isLoading && !error) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <h1 className="text-2xl font-bold mb-4">� Users Management</h1>
          <p className="text-gray-600">
            This is the Users page in the HR module. 
            {!usersData ? ' Loading users...' : ' No users found or not authenticated.'}
          </p>
          <div className="mt-4 p-4 bg-gray-100 rounded-lg">
            <p className="text-sm">Debug info:</p>
            <p>- Is Loading: {isLoading ? 'Yes' : 'No'}</p>
            <p>- Has Error: {error ? 'Yes' : 'No'}</p>
            <p>- Users Data: {usersData ? 'Available' : 'None'}</p>
            <p>- Users Count: {users.length}</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    console.error('🔍 [UsersPage] Error state:', error)
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading users</h3>
          <p className="text-gray-600">Please try again later.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">🔐 TSH ERP System Users</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage TSH ERP system users, roles, and permissions
          </p>
        </div>
        <Button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4" />
          <span>Add New User</span>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Total Users</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{users.length}</div>
            <p className="text-xs text-gray-500 mt-1">All system users</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Active Users</CardTitle>
            <UserCheck className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {users.filter(user => user.isActive ?? user.is_active).length}
            </div>
            <p className="text-xs text-gray-500 mt-1">Currently active</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Admins</CardTitle>
            <Shield className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {users.filter(user => user.role === 'admin').length}
            </div>
            <p className="text-xs text-gray-500 mt-1">Admin users</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search users by name, email, or role..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="flex items-center space-x-2">
              <Filter className="h-4 w-4" />
              <span>Filter</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>TSH ERP Users</CardTitle>
          <CardDescription>
            {users.length} users found • Manage user accounts, roles, and system access
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 rounded-lg"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">User</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Email</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Role</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Branch</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Last Login</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user: User) => (
                    <tr key={user.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-3">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            user.role === 'admin' ? 'bg-purple-600' : 
                            user.role === 'manager' ? 'bg-blue-600' : 'bg-green-600'
                          }`}>
                            <span className="text-white font-medium text-sm">
                              {user.name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {user.name}
                            </p>
                            <p className="text-sm text-gray-500">
                              {user.employee_code || 'No employee code'}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-gray-600 dark:text-gray-300">
                        {user.email}
                      </td>
                      <td className="py-4 px-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                          user.role === 'manager' ? 'bg-blue-100 text-blue-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-600 dark:text-gray-300">
                        {user.branch || 'No branch'}
                      </td>
                      <td className="py-4 px-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          (user.isActive ?? user.is_active) 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {(user.isActive ?? user.is_active) ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-600 dark:text-gray-300">
                        {user.last_login 
                          ? formatDate(user.last_login) 
                          : 'Never logged in'
                        }
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          <Button variant="ghost" size="icon" title="Edit User">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" title="Delete User">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" title="More Options">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {users.length === 0 && !isLoading && (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
                  <p className="text-gray-600">Try adjusting your search criteria.</p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setPage(page - 1)}
            disabled={page <= 1}
          >
            Previous
          </Button>
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(page + 1)}
            disabled={page >= totalPages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
