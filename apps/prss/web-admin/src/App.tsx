import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ReturnsList from './pages/ReturnsList'
import ReturnDetail from './pages/ReturnDetail'
import InspectionForm from './pages/InspectionForm'
import MaintenanceJobs from './pages/MaintenanceJobs'
import Reports from './pages/Reports'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="returns" element={<ReturnsList />} />
          <Route path="returns/:id" element={<ReturnDetail />} />
          <Route path="returns/:id/inspect" element={<InspectionForm />} />
          <Route path="maintenance" element={<MaintenanceJobs />} />
          <Route path="reports" element={<Reports />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
