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
