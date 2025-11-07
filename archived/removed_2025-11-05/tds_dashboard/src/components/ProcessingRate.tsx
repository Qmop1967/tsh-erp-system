// Processing Rate Chart Component
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useQueueStats } from '../hooks/useTDSData';
import { formatNumber } from '../lib/utils';
import { useState, useEffect } from 'react';
import type { ChartDataPoint } from '../types/tds';

export function ProcessingRate() {
  const { data: queueData } = useQueueStats();
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

  useEffect(() => {
    if (queueData) {
      const now = new Date();
      const newPoint: ChartDataPoint = {
        time: now.toLocaleTimeString(),
        'Per Minute': queueData.processing_rate?.last_minute || 0,
        'Per Hour': Math.round((queueData.processing_rate?.last_hour || 0) / 60),
      };

      setChartData(prev => {
        const updated = [...prev, newPoint];
        // Keep last 20 data points
        return updated.slice(-20);
      });
    }
  }, [queueData]);

  if (chartData.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-md">
        <h3 className="text-lg font-semibold text-gray-900">Processing Rate</h3>
        <p className="mt-4 text-center text-gray-500">Collecting data...</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-white p-6 shadow-md">
      <h3 className="text-lg font-semibold text-gray-900">Processing Rate Over Time</h3>
      <div className="mt-6" style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="time"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
            />
            <YAxis
              tickFormatter={formatNumber}
              fontSize={12}
              tick={{ fill: '#6b7280' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="Per Minute"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="Per Hour"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
