import React, { useState, useEffect } from 'react'
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
  Clock,
  Users,
  Car,
  UserCheck,
  Store,
  X,
  Save,
  Filter
} from 'lucide-react'
import { useLanguageStore } from '@/stores/languageStore'
import { useDynamicTranslations } from '@/lib/dynamicTranslations'

interface Employee {
  id: string | number
  name: string
  email: string
  employee_code?: string
  phone?: string
  role: string
  branch: string
  is_salesperson: boolean
  is_active: boolean
  created_at: string
  last_login?: string
}

interface NewEmployeeForm {
  name: string
  email: string
  password: string
  employee_code: string
  phone: string
  role_id: number
  branch_id: number
  is_salesperson: boolean
}

interface Role {
  id: number
  name: string
}

interface Branch {
  id: number
  name: string
  code: string
}

type FilterType = 'all' | 'travel_salesperson' | 'partner_salesman' | 'retailerman'

export function EmployeesPage() {
  const { language } = useLanguageStore()
  const { t } = useDynamicTranslations(language)
  
  const [employees, setEmployees] = useState<Employee[]>([])
  const [filteredEmployees, setFilteredEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')
  const [showAddModal, setShowAddModal] = useState(false)
  const [roles, setRoles] = useState<Role[]>([])
  const [branches, setBranches] = useState<Branch[]>([])
  
  const [newEmployee, setNewEmployee] = useState<NewEmployeeForm>({
    name: '',
    email: '',
    password: '123456', // Default password
    employee_code: '',
    phone: '',
    role_id: 0,
    branch_id: 0,
    is_salesperson: false
  })

  // Fetch employees from API
  const fetchEmployees = async (filterType: FilterType = 'all') => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:8000/api/users/by-type/${filterType}`)
      if (response.ok) {
        const data = await response.json()
        setEmployees(data)
        setFilteredEmployees(data)
      } else {
        console.error('Failed to fetch employees')
      }
    } catch (error) {
      console.error('Error fetching employees:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch roles and branches for the form
  const fetchFormData = async () => {
    try {
      const [rolesResponse, branchesResponse] = await Promise.all([
        fetch('http://localhost:8000/api/users/roles'),
        fetch('http://localhost:8000/api/users/branches')
      ])
      
      if (rolesResponse.ok) {
        const rolesData = await rolesResponse.json()
        setRoles(rolesData)
      }
      
      if (branchesResponse.ok) {
        const branchesData = await branchesResponse.json()
        setBranches(branchesData)
      }
    } catch (error) {
      console.error('Error fetching form data:', error)
    }
  }

  // Create new employee
  const createEmployee = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newEmployee)
      })
      
      if (response.ok) {
        setShowAddModal(false)
        setNewEmployee({
          name: '',
          email: '',
          password: '123456',
          employee_code: '',
          phone: '',
          role_id: 0,
          branch_id: 0,
          is_salesperson: false
        })
        fetchEmployees(activeFilter) // Refresh the list
      } else {
        console.error('Failed to create employee')
      }
    } catch (error) {
      console.error('Error creating employee:', error)
    }
  }

  // Filter employees based on search query
  useEffect(() => {
    const filtered = employees.filter(employee => {
      const matchesSearch = 
        employee.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        employee.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (employee.employee_code && employee.employee_code.toLowerCase().includes(searchQuery.toLowerCase())) ||
        employee.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
        employee.branch.toLowerCase().includes(searchQuery.toLowerCase())

      return matchesSearch
    })
    setFilteredEmployees(filtered)
  }, [searchQuery, employees])

  // Load data on component mount
  useEffect(() => {
    fetchEmployees()
    fetchFormData()
  }, [])

  // Handle filter change
  const handleFilterChange = (filterType: FilterType) => {
    setActiveFilter(filterType)
    fetchEmployees(filterType)
  }

  // Generate employee code based on role
  const generateEmployeeCode = (roleId: number) => {
    const role = roles.find(r => r.id === roleId)
    if (!role) return ''
    
    const prefixes = {
      "Travel Salesperson": "TSP",
      "Partner Salesman": "PSM", 
      "Retailerman": "RTM",
      "Admin": "ADM",
      "Manager": "MGR",
      "Employee": "EMP",
      "Accountant": "ACC",
      "HR Specialist": "HRS"
    }
    
    const prefix = prefixes[role.name as keyof typeof prefixes] || "EMP"
    const count = employees.filter(emp => emp.role === role.name).length + 1
    return `${prefix}-${count.toString().padStart(3, '0')}`
  }

  // Handle role change in form
  const handleRoleChange = (roleId: number) => {
    const role = roles.find(r => r.id === roleId)
    const isSalesperson = role ? ['Travel Salesperson', 'Partner Salesman', 'Retailerman'].includes(role.name) : false
    
    setNewEmployee({
      ...newEmployee,
      role_id: roleId,
      is_salesperson: isSalesperson,
      employee_code: generateEmployeeCode(roleId)
    })
  }

  const getStatusBadge = (isActive: boolean) => {
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        isActive 
          ? 'bg-green-100 text-green-800 border border-green-200' 
          : 'bg-red-100 text-red-800 border border-red-200'
      }`}>
                 {isActive ? (language === 'ar' ? 'نشط' : 'Active') : (language === 'ar' ? 'غير نشط' : 'Inactive')}
      </span>
    )
  }

  const getRoleBadge = (role: string) => {
    const colors = {
      'Travel Salesperson': 'bg-blue-100 text-blue-800 border-blue-200',
      'Partner Salesman': 'bg-purple-100 text-purple-800 border-purple-200',
      'Retailerman': 'bg-orange-100 text-orange-800 border-orange-200',
      'Manager': 'bg-green-100 text-green-800 border-green-200',
      'Admin': 'bg-red-100 text-red-800 border-red-200',
      'Employee': 'bg-gray-100 text-gray-800 border-gray-200',
      'Accountant': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'HR Specialist': 'bg-pink-100 text-pink-800 border-pink-200'
    }
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
        colors[role as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200'
      }`}>
        {role}
      </span>
    )
  }

  // Statistics
  const stats = {
    total: employees.length,
    travelSalesperson: employees.filter(emp => emp.role === 'Travel Salesperson').length,
    partnerSalesman: employees.filter(emp => emp.role === 'Partner Salesman').length,
    retailerman: employees.filter(emp => emp.role === 'Retailerman').length,
    active: employees.filter(emp => emp.is_active).length
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading employees...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6" dir={language === 'ar' ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-8 h-8" />
            {t.employeeManagement}
          </h1>
          <p className="text-gray-600 mt-1">
            {t.manageEmployeesDescription}
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          {t.addNewEmployee}
        </Button>
      </div>

      {/* Quick Filter Buttons */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">
            {t.quickFilter}
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant={activeFilter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleFilterChange('all')}
            className="flex items-center gap-2"
          >
            <Users className="w-4 h-4" />
            {t.allEmployees}
            <span className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded-full text-xs">
              {stats.total}
            </span>
          </Button>
          
          <Button
            variant={activeFilter === 'travel_salesperson' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleFilterChange('travel_salesperson')}
            className="flex items-center gap-2"
          >
            <Car className="w-4 h-4" />
            {t.travelSalespersons}
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full text-xs">
              {stats.travelSalesperson}
            </span>
          </Button>
          
          <Button
            variant={activeFilter === 'partner_salesman' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleFilterChange('partner_salesman')}
            className="flex items-center gap-2"
          >
                         <UserCheck className="w-4 h-4" />
            {t.partnerSalesmen}
            <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full text-xs">
              {stats.partnerSalesman}
            </span>
          </Button>
          
          <Button
            variant={activeFilter === 'retailerman' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleFilterChange('retailerman')}
            className="flex items-center gap-2"
          >
            <Store className="w-4 h-4" />
            {t.retailermen}
            <span className="bg-orange-100 text-orange-800 px-2 py-0.5 rounded-full text-xs">
              {stats.retailerman}
            </span>
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {t.totalEmployees}
                </p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {t.travelSalespersons}
                </p>
                <p className="text-2xl font-bold text-blue-600">{stats.travelSalesperson}</p>
              </div>
              <Car className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {t.partnerSalesmen}
                </p>
                <p className="text-2xl font-bold text-purple-600">{stats.partnerSalesman}</p>
              </div>
                             <UserCheck className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {t.retailermen}
                </p>
                <p className="text-2xl font-bold text-orange-600">{stats.retailerman}</p>
              </div>
              <Store className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              {t.employeeList}
            </CardTitle>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder={t.searchEmployees}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t.employee}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t.role}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t.branch}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {language === 'ar' ? 'الحالة' : 'Status'}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {language === 'ar' ? 'تاريخ الإنشاء' : 'Created Date'}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {language === 'ar' ? 'الإجراءات' : 'Actions'}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredEmployees.map((employee) => (
                  <tr key={employee.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-700">
                              {employee.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{employee.name}</div>
                          <div className="text-sm text-gray-500 flex items-center gap-1">
                            <Mail className="w-3 h-3" />
                            {employee.email}
                          </div>
                          {employee.employee_code && (
                            <div className="text-xs text-gray-400">ID: {employee.employee_code}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      {getRoleBadge(employee.role)}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-1 text-sm text-gray-900">
                        <Building className="w-3 h-3 text-gray-400" />
                        {employee.branch}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      {getStatusBadge(employee.is_active)}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-1 text-sm text-gray-500">
                        <Calendar className="w-3 h-3" />
                        {new Date(employee.created_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" className="p-2">
                          <Edit className="w-3 h-3" />
                        </Button>
                        <Button variant="outline" size="sm" className="p-2 text-red-600 hover:text-red-700">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredEmployees.length === 0 && (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">
                {language === 'ar' ? 'لا توجد موظفين مطابقين للبحث' : 'No employees found matching your search'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Employee Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                {language === 'ar' ? 'إضافة موظف جديد' : 'Add New Employee'}
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAddModal(false)}
                className="p-2"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'ar' ? 'الاسم' : 'Name'}
                </label>
                <Input
                  value={newEmployee.name}
                  onChange={(e) => setNewEmployee({...newEmployee, name: e.target.value})}
                  placeholder={language === 'ar' ? 'أدخل اسم الموظف' : 'Enter employee name'}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'ar' ? 'البريد الإلكتروني' : 'Email'}
                </label>
                <Input
                  type="email"
                  value={newEmployee.email}
                  onChange={(e) => setNewEmployee({...newEmployee, email: e.target.value})}
                  placeholder={language === 'ar' ? 'أدخل البريد الإلكتروني' : 'Enter email address'}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'ar' ? 'رقم الهاتف' : 'Phone'}
                </label>
                <Input
                  value={newEmployee.phone}
                  onChange={(e) => setNewEmployee({...newEmployee, phone: e.target.value})}
                  placeholder={language === 'ar' ? 'أدخل رقم الهاتف' : 'Enter phone number'}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'ar' ? 'الدور' : 'Role'}
                </label>
                <select
                  value={newEmployee.role_id}
                  onChange={(e) => handleRoleChange(Number(e.target.value))}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value={0}>{language === 'ar' ? 'اختر الدور' : 'Select Role'}</option>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'ar' ? 'الفرع' : 'Branch'}
                </label>
                <select
                  value={newEmployee.branch_id}
                  onChange={(e) => setNewEmployee({...newEmployee, branch_id: Number(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value={0}>{language === 'ar' ? 'اختر الفرع' : 'Select Branch'}</option>
                  {branches.map((branch) => (
                    <option key={branch.id} value={branch.id}>{branch.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {language === 'ar' ? 'رمز الموظف' : 'Employee Code'}
                </label>
                <Input
                  value={newEmployee.employee_code}
                  onChange={(e) => setNewEmployee({...newEmployee, employee_code: e.target.value})}
                  placeholder={language === 'ar' ? 'رمز الموظف' : 'Employee code'}
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <Button
                onClick={createEmployee}
                disabled={!newEmployee.name || !newEmployee.email || !newEmployee.role_id || !newEmployee.branch_id}
                className="flex-1"
              >
                <Save className="w-4 h-4 mr-2" />
                {language === 'ar' ? 'حفظ' : 'Save'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowAddModal(false)}
                className="flex-1"
              >
                {language === 'ar' ? 'إلغاء' : 'Cancel'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}