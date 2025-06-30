import { useState } from 'react'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2,
  UserPlus,
  Mail,
  Phone,
  Building,
  Calendar,
  DollarSign,
  Clock
} from 'lucide-react'

interface Employee {
  id: string | number
  employee_id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  department: string
  position: string
  hire_date: string
  salary?: number
  status: 'active' | 'inactive' | 'on_leave'
  manager?: string
  address?: string
  emergency_contact?: string
  emergency_phone?: string
  birth_date?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

// Mock data for employees
const mockEmployees: Employee[] = [
  {
    id: 1,
    employee_id: 'EMP-001',
    first_name: 'Ahmed',
    last_name: 'Al-Rashid',
    email: 'ahmed.alrashid@tsh.com',
    phone: '+971-50-123-4567',
    department: 'Sales',
    position: 'Senior Sales Manager',
    hire_date: '2020-03-15',
    salary: 8500,
    status: 'active',
    manager: 'Regional Sales Director',
    address: 'Dubai, UAE',
    emergency_contact: 'Noor Al-Rashid',
    emergency_phone: '+971-50-987-6543',
    birth_date: '1985-07-22',
    is_active: true,
    created_at: '2020-03-15T09:00:00Z'
  },
  {
    id: 2,
    employee_id: 'EMP-002',
    first_name: 'Sarah',
    last_name: 'Johnson',
    email: 'sarah.johnson@tsh.com',
    phone: '+971-50-234-5678',
    department: 'IT',
    position: 'Software Engineer',
    hire_date: '2019-08-10',
    salary: 7200,
    status: 'active',
    manager: 'IT Director',
    address: 'Abu Dhabi, UAE',
    emergency_contact: 'Mark Johnson',
    emergency_phone: '+971-50-876-5432',
    birth_date: '1990-12-03',
    is_active: true,
    created_at: '2019-08-10T10:30:00Z'
  },
  {
    id: 3,
    employee_id: 'EMP-003',
    first_name: 'Michael',
    last_name: 'Smith',
    email: 'michael.smith@tsh.com',
    phone: '+971-50-345-6789',
    department: 'Marketing',
    position: 'Marketing Coordinator',
    hire_date: '2021-01-20',
    salary: 5800,
    status: 'inactive',
    manager: 'Marketing Manager',
    address: 'Sharjah, UAE',
    emergency_contact: 'Linda Smith',
    emergency_phone: '+971-50-765-4321',
    birth_date: '1990-11-08',
    is_active: true,
    created_at: '2023-05-20T14:30:00Z'
  },
  {
    id: 4,
    employee_id: 'EMP-004',
    first_name: 'Fatima',
    last_name: 'Al-Zahra',
    email: 'fatima.alzahra@tsh.com',
    phone: '+971-50-456-7890',
    department: 'HR',
    position: 'HR Specialist',
    hire_date: '2021-09-12',
    salary: 6800,
    status: 'on_leave',
    manager: 'Sarah Johnson',
    address: 'Dubai, UAE',
    emergency_contact: 'Ali Al-Zahra',
    emergency_phone: '+971-50-654-3210',
    birth_date: '1988-04-25',
    is_active: true,
    created_at: '2021-09-12T11:45:00Z'
  },
  {
    id: 5,
    employee_id: 'EMP-005',
    first_name: 'Omar',
    last_name: 'Ibrahim',
    email: 'omar.ibrahim@tsh.com',
    phone: '+971-50-567-8901',
    department: 'Finance',
    position: 'Accountant',
    hire_date: '2022-11-03',
    salary: 5500,
    status: 'active',
    manager: 'Finance Manager',
    address: 'Ajman, UAE',
    emergency_contact: 'Layla Ibrahim',
    emergency_phone: '+971-50-543-2109',
    birth_date: '1992-12-18',
    is_active: true,
    created_at: '2022-11-03T16:20:00Z'
  }
]

export function EmployeesPage() {
  const [employees] = useState<Employee[]>(mockEmployees)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterDepartment, setFilterDepartment] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  const departments = Array.from(new Set(employees.map(emp => emp.department)))
  const statuses = ['active', 'inactive', 'on_leave']

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = 
      employee.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      employee.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      employee.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      employee.employee_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      employee.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      employee.position.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesDepartment = filterDepartment === 'all' || employee.department === filterDepartment
    const matchesStatus = filterStatus === 'all' || employee.status === filterStatus

    return matchesSearch && matchesDepartment && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'inactive':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'on_leave':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getDepartmentColor = (department: string) => {
    const colors = {
      'Sales': 'bg-blue-100 text-blue-800 border-blue-200',
      'Management': 'bg-purple-100 text-purple-800 border-purple-200',
      'IT': 'bg-green-100 text-green-800 border-green-200',
      'HR': 'bg-pink-100 text-pink-800 border-pink-200',
      'Finance': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'Operations': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'Marketing': 'bg-orange-100 text-orange-800 border-orange-200'
    }
    return colors[department as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const stats = {
    total: employees.length,
    active: employees.filter(emp => emp.status === 'active').length,
    onLeave: employees.filter(emp => emp.status === 'on_leave').length,
    departments: departments.length
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Employee Management</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage employee information, departments, and organizational structure
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add New Employee
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Employees</CardTitle>
            <UserPlus className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{stats.total}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400">Across all departments</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Active Employees</CardTitle>
            <Clock className="h-4 w-4 text-green-600 dark:text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">{stats.active}</div>
            <p className="text-xs text-green-600 dark:text-green-400">Currently working</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border-yellow-200 dark:border-yellow-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-yellow-700 dark:text-yellow-300">On Leave</CardTitle>
            <Calendar className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">{stats.onLeave}</div>
            <p className="text-xs text-yellow-600 dark:text-yellow-400">Temporary absence</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Departments</CardTitle>
            <Building className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">{stats.departments}</div>
            <p className="text-xs text-purple-600 dark:text-purple-400">Total departments</p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search & Filter Employees
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Search employees by name, email, ID, or position..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-4">
              <select
                value={filterDepartment}
                onChange={(e) => setFilterDepartment(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="all">All Departments</option>
                {departments.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="all">All Status</option>
                {statuses.map(status => (
                  <option key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Employee List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEmployees.map((employee) => (
          <Card key={employee.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">
                    {employee.first_name} {employee.last_name}
                  </CardTitle>
                  <CardDescription className="text-sm">
                    {employee.position} • {employee.employee_id}
                  </CardDescription>
                </div>
                <div className="flex flex-col gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(employee.status)}`}>
                    {employee.status.charAt(0).toUpperCase() + employee.status.slice(1).replace('_', ' ')}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getDepartmentColor(employee.department)}`}>
                    {employee.department}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <Mail className="h-4 w-4" />
                  <span>{employee.email}</span>
                </div>
                {employee.phone && (
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                    <Phone className="h-4 w-4" />
                    <span>{employee.phone}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <Calendar className="h-4 w-4" />
                  <span>Hired: {new Date(employee.hire_date).toLocaleDateString()}</span>
                </div>
                {employee.salary && (
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                    <DollarSign className="h-4 w-4" />
                    <span>${employee.salary.toLocaleString()} / month</span>
                  </div>
                )}
                {employee.manager && (
                  <div className="text-sm text-gray-600 dark:text-gray-300">
                    <span className="font-medium">Reports to:</span> {employee.manager}
                  </div>
                )}
                <div className="flex items-center justify-end gap-2 pt-2 border-t">
                  <Button variant="outline" size="sm" className="flex items-center gap-1">
                    <Edit className="h-3 w-3" />
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" className="flex items-center gap-1 text-red-600 hover:text-red-700">
                    <Trash2 className="h-3 w-3" />
                    Delete
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredEmployees.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <UserPlus className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No employees found</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {searchQuery || filterDepartment !== 'all' || filterStatus !== 'all'
                ? 'Try adjusting your search criteria or filters.'
                : 'Start by adding your first employee to the system.'}
            </p>
            <Button className="flex items-center gap-2 mx-auto">
              <Plus className="h-4 w-4" />
              Add First Employee
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}