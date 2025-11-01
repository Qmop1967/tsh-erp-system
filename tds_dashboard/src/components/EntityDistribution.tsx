// Entity Distribution Chart Component
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useQueueStats } from '../hooks/useTDSData';
import { formatNumber } from '../lib/utils';
import { EntityType } from '../types/tds';

const COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // yellow
  '#ef4444', // red
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#14b8a6', // teal
  '#f97316', // orange
  '#6366f1', // indigo
  '#84cc16', // lime
];

export function EntityDistribution() {
  const { data: queueData, isLoading, isError } = useQueueStats();

  if (isLoading) {
    return (
      <div className="rounded-lg bg-white p-8 shadow-md">
        <div className="animate-pulse">
          <div className="h-6 w-48 rounded bg-gray-200"></div>
          <div className="mt-4 h-64 rounded bg-gray-200"></div>
        </div>
      </div>
    );
  }

  if (isError || !queueData) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-md">
        <p className="text-gray-600">Unable to load entity distribution</p>
      </div>
    );
  }

  const chartData = Object.entries(queueData.by_entity || {})
    .map(([entity, count]) => ({
      name: entity.replace(/_/g, ' ').toUpperCase(),
      value: count,
      entity: entity as EntityType,
    }))
    .filter(item => item.value > 0)
    .sort((a, b) => b.value - a.value);

  if (chartData.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-md">
        <h3 className="text-lg font-semibold text-gray-900">Entity Distribution</h3>
        <p className="mt-4 text-center text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h3 className="text-lg font-semibold text-gray-900">Events by Entity Type</h3>
      <div className="mt-6" style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="name"
              angle={-45}
              textAnchor="end"
              height={100}
              fontSize={12}
            />
            <YAxis tickFormatter={formatNumber} fontSize={12} />
            <Tooltip
              formatter={(value: number) => [formatNumber(value), 'Events']}
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
            />
            <Bar dataKey="value" radius={[8, 8, 0, 0]}>
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
