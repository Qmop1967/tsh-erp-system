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
