import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function Layout() {
  const { logout, user } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <nav style={{ background: '#212529', color: 'white', padding: '1rem 2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0, fontSize: '20px' }}>PRSS - After-Sales Operations</h1>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
            <Link to="/returns" style={{ color: 'white', textDecoration: 'none' }}>Returns</Link>
            <Link to="/maintenance" style={{ color: 'white', textDecoration: 'none' }}>Maintenance</Link>
            <Link to="/reports" style={{ color: 'white', textDecoration: 'none' }}>Reports</Link>
            <span style={{ color: '#adb5bd' }}>{user?.username || 'User'}</span>
            <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '6px 12px' }}>Logout</button>
          </div>
        </div>
      </nav>
      <main style={{ flex: 1, padding: '2rem' }}>
        <Outlet />
      </main>
    </div>
  )
}
