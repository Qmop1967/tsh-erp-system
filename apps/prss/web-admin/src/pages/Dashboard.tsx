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
