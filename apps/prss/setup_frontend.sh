#!/bin/bash

# Setup frontend React files for PRSS

BASE_DIR="/Users/khaleelal-mulla/TSH_ERP_Ecosystem/apps/prss/web-admin/src"

echo "Creating frontend components and pages..."

# Store
cat > "$BASE_DIR/store/authStore.ts" << 'EOF'
import { create } from 'zustand'

interface AuthState {
  token: string | null
  user: any | null
  isAuthenticated: boolean
  login: (token: string, user: any) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  isAuthenticated: !!localStorage.getItem('token'),
  login: (token, user) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({ token, user, isAuthenticated: true })
  },
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ token: null, user: null, isAuthenticated: false })
  },
}))
EOF

# API Service
cat > "$BASE_DIR/services/api.ts" << 'EOF'
import axios from 'axios'

const api = axios.create({
  baseURL: '/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const returnsApi = {
  list: (params?: any) => api.get('/returns', { params }),
  get: (id: number) => api.get(`/returns/${id}`),
  create: (data: any) => api.post('/returns', data),
  receive: (id: number, data: any) => api.post(`/returns/${id}/receive`, data),
  inspect: (id: number, data: any) => api.post(`/returns/${id}/inspect`, data),
  decide: (id: number, data: any) => api.post(`/returns/${id}/decide`, data),
}

export const reportsApi = {
  getKPIs: () => api.get('/reports/kpis'),
  getTopReasons: () => api.get('/reports/top-reasons'),
}

export const authApi = {
  login: (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default api
EOF

# Layout Component
cat > "$BASE_DIR/components/Layout.tsx" << 'EOF'
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
EOF

# Login Page
cat > "$BASE_DIR/pages/Login.tsx" << 'EOF'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authApi } from '../services/api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const { data } = await authApi.login(username, password)
      login(data.access_token, { username })
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f5f5f5' }}>
      <div className="card" style={{ width: '400px' }}>
        <h2 style={{ marginBottom: '20px', textAlign: 'center' }}>PRSS Login</h2>
        {error && <div className="error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Login</button>
        </form>
      </div>
    </div>
  )
}
EOF

# Dashboard Page
cat > "$BASE_DIR/pages/Dashboard.tsx" << 'EOF'
import { useQuery } from '@tanstack/react-query'
import { reportsApi } from '../services/api'

export default function Dashboard() {
  const { data: kpis, isLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => reportsApi.getKPIs().then(res => res.data),
  })

  if (isLoading) return <div className="loading">Loading...</div>

  return (
    <div>
      <h1 style={{ marginBottom: '30px' }}>Dashboard</h1>
      <div className="grid">
        <div className="stat-card">
          <h3>Total Returns</h3>
          <div className="value">{kpis?.total_returns || 0}</div>
        </div>
        <div className="stat-card">
          <h3>Avg Processing Time</h3>
          <div className="value">{kpis?.avg_processing_time_hours?.toFixed(1) || 0}h</div>
        </div>
        <div className="stat-card">
          <h3>Defect Rate</h3>
          <div className="value">{((kpis?.defect_rate || 0) * 100).toFixed(1)}%</div>
        </div>
      </div>
    </div>
  )
}
EOF

# Returns List Page
cat > "$BASE_DIR/pages/ReturnsList.tsx" << 'EOF'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { returnsApi } from '../services/api'

export default function ReturnsList() {
  const { data: returns, isLoading } = useQuery({
    queryKey: ['returns'],
    queryFn: () => returnsApi.list().then(res => res.data),
  })

  if (isLoading) return <div className="loading">Loading...</div>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>Returns</h1>
        <Link to="/returns/new" className="btn btn-primary">New Return</Link>
      </div>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Customer</th>
              <th>Product</th>
              <th>Serial</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {returns?.map((ret: any) => (
              <tr key={ret.id}>
                <td>#{ret.id}</td>
                <td>{ret.customer_id}</td>
                <td>{ret.product_id}</td>
                <td>{ret.serial_number || 'N/A'}</td>
                <td><span className={`status-badge status-${ret.status}`}>{ret.status}</span></td>
                <td>{new Date(ret.created_at).toLocaleDateString()}</td>
                <td>
                  <Link to={`/returns/${ret.id}`} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>View</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
EOF

# Return Detail Page
cat > "$BASE_DIR/pages/ReturnDetail.tsx" << 'EOF'
import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { returnsApi } from '../services/api'

export default function ReturnDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: returnData, isLoading } = useQuery({
    queryKey: ['return', id],
    queryFn: () => returnsApi.get(Number(id)).then(res => res.data),
  })

  if (isLoading) return <div className="loading">Loading...</div>

  return (
    <div>
      <h1>Return #{id}</h1>
      <div className="card">
        <h3>Details</h3>
        <p><strong>Status:</strong> <span className={`status-badge status-${returnData?.status}`}>{returnData?.status}</span></p>
        <p><strong>Customer ID:</strong> {returnData?.customer_id}</p>
        <p><strong>Product ID:</strong> {returnData?.product_id}</p>
        <p><strong>Serial Number:</strong> {returnData?.serial_number || 'N/A'}</p>
        <p><strong>Reason:</strong> {returnData?.reason_code}</p>
        <p><strong>Created:</strong> {new Date(returnData?.created_at).toLocaleString()}</p>

        <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
          <Link to={`/returns/${id}/inspect`} className="btn btn-primary">Inspect</Link>
          <button className="btn btn-success">Approve</button>
          <button className="btn btn-danger">Reject</button>
        </div>
      </div>
    </div>
  )
}
EOF

# Inspection Form
cat > "$BASE_DIR/pages/InspectionForm.tsx" << 'EOF'
import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { returnsApi } from '../services/api'

export default function InspectionForm() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [finding, setFinding] = useState('ok')
  const [recommendation, setRecommendation] = useState('restock')
  const [notes, setNotes] = useState('')

  const mutation = useMutation({
    mutationFn: (data: any) => returnsApi.inspect(Number(id), data),
    onSuccess: () => {
      alert('Inspection saved!')
      navigate(`/returns/${id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      return_request_id: Number(id),
      inspector_id: 1,
      finding,
      recommendation,
      notes,
      checklists: {},
      inspection_photos: [],
    })
  }

  return (
    <div>
      <h1>Inspection - Return #{id}</h1>
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Finding</label>
            <select value={finding} onChange={(e) => setFinding(e.target.value)}>
              <option value="ok">OK</option>
              <option value="cosmetic_defect">Cosmetic Defect</option>
              <option value="functional_defect">Functional Defect</option>
              <option value="wrong_item">Wrong Item</option>
            </select>
          </div>
          <div className="form-group">
            <label>Recommendation</label>
            <select value={recommendation} onChange={(e) => setRecommendation(e.target.value)}>
              <option value="restock">Restock</option>
              <option value="repair">Repair</option>
              <option value="scrap">Scrap</option>
              <option value="supplier_return">Return to Supplier</option>
              <option value="refund">Refund</option>
            </select>
          </div>
          <div className="form-group">
            <label>Notes</label>
            <textarea rows={4} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary">Submit Inspection</button>
        </form>
      </div>
    </div>
  )
}
EOF

# Maintenance Jobs
cat > "$BASE_DIR/pages/MaintenanceJobs.tsx" << 'EOF'
export default function MaintenanceJobs() {
  return (
    <div>
      <h1>Maintenance Jobs</h1>
      <div className="card">
        <p>Maintenance jobs list will appear here</p>
      </div>
    </div>
  )
}
EOF

# Reports
cat > "$BASE_DIR/pages/Reports.tsx" << 'EOF'
import { useQuery } from '@tanstack/react-query'
import { reportsApi } from '../services/api'

export default function Reports() {
  const { data: topReasons } = useQuery({
    queryKey: ['top-reasons'],
    queryFn: () => reportsApi.getTopReasons().then(res => res.data),
  })

  return (
    <div>
      <h1>Reports</h1>
      <div className="card">
        <h3>Top Return Reasons</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Reason</th>
              <th>Count</th>
            </tr>
          </thead>
          <tbody>
            {topReasons?.map((item: any, idx: number) => (
              <tr key={idx}>
                <td>{item.reason}</td>
                <td>{item.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
EOF

echo "✅ Frontend components created successfully!"
