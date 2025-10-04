import { Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from './components/layout/MainLayout'
import { SimpleDashboardPage } from './pages/dashboard/SimpleDashboardPage'
import { LoginPage } from './pages/auth/LoginPage'
import { UsersPage } from './pages/users/UsersPage'
import { PermissionsPage } from './pages/permissions/PermissionsPage'
import { RolesPage } from './pages/roles/RolesPage'
import ItemsPage from './pages/inventory/ItemsPage'
import { ComingSoonPage } from './pages/ComingSoonPage'
import { useAuthStore } from './stores/authStore'

// Modern Settings Pages
import ModernSettingsPage from './pages/settings/ModernSettingsPage'
import WhatsAppBusinessSettings from './pages/settings/integrations/WhatsAppBusinessSettings'
import ZohoIntegrationSettings from './pages/settings/integrations/ZohoIntegrationSettings'
import ZohoIntegrationSimple from './pages/settings/integrations/ZohoIntegrationSimple'
import DevicesManagement from './pages/settings/auth/DevicesManagement'
import MFASettings from './pages/settings/auth/MFASettings'
import OrganizationProfile from './pages/settings/general/OrganizationProfile'
import DynamicTranslationManagementPage from './pages/settings/DynamicTranslationManagementPage'

console.log('🚀 TSH ERP System - Enhanced Authentication Mode')

// Protected Route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, token } = useAuthStore()
  
  if (!user || !token) {
    console.log('🚫 Not authenticated, redirecting to login')
    return <Navigate to="/login" replace />
  }
  
  return <MainLayout>{children}</MainLayout>
}

function App() {
  console.log('🎯 App component rendering with authentication...')
  
  return (
    <div style={{ margin: 0, padding: 0, height: '100vh', overflow: 'hidden' }}>
      <Routes>
        {/* Public Route */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <SimpleDashboardPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <SimpleDashboardPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/users" 
          element={
            <ProtectedRoute>
              <UsersPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/permissions" 
          element={
            <ProtectedRoute>
              <PermissionsPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/roles" 
          element={
            <ProtectedRoute>
              <RolesPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/inventory/items" 
          element={
            <ProtectedRoute>
              <ItemsPage />
            </ProtectedRoute>
          } 
        />
        
        {/* Other module routes - Coming Soon */}
        <Route 
          path="/hr" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Human Resources" description="Complete HR management system coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/sales" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Sales Management" description="Comprehensive sales management features coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/inventory/*" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Inventory Management" description="Advanced inventory features coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/purchase" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Purchase Management" description="Purchase order management coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/accounting" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Accounting" description="Full accounting system coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/financial" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Financial Management" description="Financial management features coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/pos" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Point of Sale" description="Modern POS system coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/branches" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Branch Management" description="Multi-branch management coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/security" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Security Dashboard" description="Advanced security features coming soon." />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/reports" 
          element={
            <ProtectedRoute>
              <ComingSoonPage title="Reports" description="Comprehensive reporting system coming soon." />
            </ProtectedRoute>
          } 
        />
        {/* Settings Routes */}
        <Route 
          path="/settings" 
          element={
            <ProtectedRoute>
              <ModernSettingsPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings/integrations/whatsapp" 
          element={
            <ProtectedRoute>
              <WhatsAppBusinessSettings />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings/integrations/zoho" 
          element={
            <ProtectedRoute>
              <ZohoIntegrationSettings />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings/auth/devices" 
          element={
            <ProtectedRoute>
              <DevicesManagement />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings/auth/mfa" 
          element={
            <ProtectedRoute>
              <MFASettings />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings/general/organization" 
          element={
            <ProtectedRoute>
              <OrganizationProfile />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings/translations" 
          element={
            <ProtectedRoute>
              <DynamicTranslationManagementPage />
            </ProtectedRoute>
          } 
        />
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  )
}

export default App
