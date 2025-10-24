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
