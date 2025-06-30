import { Routes, Route, Navigate } from 'react-router-dom'

// Import stores first
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'

// Create simple fallback components for testing
function SimpleDashboard() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">📊 Dashboard</h1>
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-sm text-gray-500">Sales</h3>
          <p className="text-xl font-bold">$125,430</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-sm text-gray-500">Products</h3>
          <p className="text-xl font-bold">1,245</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-sm text-gray-500">Customers</h3>
          <p className="text-xl font-bold">856</p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h3 className="text-sm text-gray-500">Orders</h3>
          <p className="text-xl font-bold">342</p>
        </div>
      </div>
    </div>
  )
}

function SimpleLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold">🏢 TSH ERP</h1>
        </div>
        <nav className="p-4">
          <a href="/dashboard" className="block py-2 px-4 hover:bg-gray-100 rounded">📊 Dashboard</a>
          <a href="/users" className="block py-2 px-4 hover:bg-gray-100 rounded">👥 Users</a>
          <a href="/branches" className="block py-2 px-4 hover:bg-gray-100 rounded">🏪 Branches</a>
          <a href="/items" className="block py-2 px-4 hover:bg-gray-100 rounded">📦 Items</a>
          <a href="/customers" className="block py-2 px-4 hover:bg-gray-100 rounded">👥 Customers</a>
          <a href="/vendors" className="block py-2 px-4 hover:bg-gray-100 rounded">🏢 Vendors</a>
          <a href="/models" className="block py-2 px-4 hover:bg-gray-100 rounded">🗃️ Models</a>
          <a href="/migration" className="block py-2 px-4 hover:bg-gray-100 rounded">🔄 Migration</a>
        </nav>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b p-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">TSH ERP System</h2>
            <div className="flex items-center space-x-4">
              <select className="px-3 py-1 border rounded">
                <option>Main Branch</option>
                <option>Warehouse</option>
                <option>Retail Store</option>
              </select>
              <span className="text-sm text-gray-600">Admin User</span>
            </div>
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-auto bg-gray-50 p-6">
          {children}
        </div>
      </div>
    </div>
  )
}

function App() {
  // Test if stores work
  const { user } = useAuthStore()
  const { isRTL } = useLanguageStore()

  console.log('App loading, user:', user, 'isRTL:', isRTL)

  return (
    <div className={`min-h-screen bg-gray-50 ${isRTL ? 'rtl' : 'ltr'}`}>
      <Routes>
        {/* Main routes */}
        <Route path="/" element={
          <SimpleLayout>
            <SimpleDashboard />
          </SimpleLayout>
        } />
        
        <Route path="/dashboard" element={
          <SimpleLayout>
            <SimpleDashboard />
          </SimpleLayout>
        } />
        
        <Route path="/users" element={
          <SimpleLayout>
            <div>
              <h1 className="text-2xl font-bold mb-4">👥 Users Management</h1>
              <div className="bg-white p-6 rounded shadow">
                <p>User management functionality will be implemented here.</p>
              </div>
            </div>
          </SimpleLayout>
        } />
        
        <Route path="/branches" element={
          <SimpleLayout>
            <div>
              <h1 className="text-2xl font-bold mb-4">🏪 Branches</h1>
              <div className="bg-white p-6 rounded shadow">
                <p>Branch management functionality will be implemented here.</p>
              </div>
            </div>
          </SimpleLayout>
        } />
        
        <Route path="/items" element={
          <SimpleLayout>
            <div>
              <h1 className="text-2xl font-bold mb-4">📦 Items Management</h1>
              <div className="bg-white p-6 rounded shadow">
                <p>Inventory items management functionality will be implemented here.</p>
              </div>
            </div>
          </SimpleLayout>
        } />
        
        <Route path="/customers" element={
          <SimpleLayout>
            <div>
              <h1 className="text-2xl font-bold mb-4">👥 Customers</h1>
              <div className="bg-white p-6 rounded shadow">
                <p>Customer management functionality will be implemented here.</p>
              </div>
            </div>
          </SimpleLayout>
        } />
        
        <Route path="/vendors" element={
          <SimpleLayout>
            <div>
              <h1 className="text-2xl font-bold mb-4">🏢 Vendors</h1>
              <div className="bg-white p-6 rounded shadow">
                <p>Vendor management functionality will be implemented here.</p>
              </div>
            </div>
          </SimpleLayout>
        } />
        
        <Route path="/models" element={
          <SimpleLayout>
            <div>
              <h1 className="text-2xl font-bold mb-4">🗃️ Data Models</h1>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded shadow">
                  <h3 className="font-bold">Users</h3>
                  <p className="text-sm text-gray-600">User management system</p>
                </div>
                <div className="bg-white p-4 rounded shadow">
                  <h3 className="font-bold">Items</h3>
                  <p className="text-sm text-gray-600">Product catalog</p>
                </div>
                <div className="bg-white p-4 rounded shadow">
                  <h3 className="font-bold">Branches</h3>
                  <p className="text-sm text-gray-600">Location management</p>
                </div>
              </div>
            </div>
          </SimpleLayout>
        } />
        
        <Route path="/migration" element={
          <SimpleLayout>
            <div>
              <h1 className="text-2xl font-bold mb-4">🔄 Data Migration</h1>
              <div className="bg-white p-6 rounded shadow">
                <p>Data migration tools and functionality will be implemented here.</p>
              </div>
            </div>
          </SimpleLayout>
        } />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
