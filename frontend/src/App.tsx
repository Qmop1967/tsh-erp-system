import { Routes, Route } from 'react-router-dom'
import { ModernERPDashboard } from './components/ModernERPDashboard'
import { UsersPage } from './pages/users/UsersPage'
import { PermissionsPage } from './pages/permissions/PermissionsPage'
import { RolesPage } from './pages/roles/RolesPage'
import ItemsPage from './pages/inventory/ItemsPage'

console.log('🚀 Modern TSH ERP System loading...')

function App() {
  console.log('🎯 App component rendering modern dashboard...')
  
  return (
    <div style={{ margin: 0, padding: 0, height: '100vh', overflow: 'hidden' }}>
      <Routes>
        <Route path="/" element={<ModernERPDashboard />} />
        <Route path="/dashboard" element={<ModernERPDashboard />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/permissions" element={<PermissionsPage />} />
        <Route path="/roles" element={<RolesPage />} />
        <Route path="/inventory/items" element={<ItemsPage />} />
        <Route path="*" element={<ModernERPDashboard />} />
      </Routes>
    </div>
  )
}

export default App
