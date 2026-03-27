import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { ZoneDistribution } from '../../types/statistics'

function ZoneTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: { payload: ZoneDistribution }[]
  label?: string
}) {
  if (!active || !payload?.length) return null
  const item = payload[0].payload
  return (
    <div className="bg-card border border-border rounded px-2 py-1 text-sm text-text-primary shadow">
      {label}: {item.count}회 ({item.percentage.toFixed(1)}%)
    </div>
  )
}

export function RangeDistribution({ data }: { data: ZoneDistribution[] }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-chart-grid)" />
        <XAxis dataKey="zone" tick={{ fontSize: 11, fill: 'var(--color-chart-text)' }} />
        <YAxis width={40} tick={{ fill: 'var(--color-chart-text)' }} />
        <Tooltip content={<ZoneTooltip />} />
        <Bar dataKey="count" fill="var(--color-chart-blue)" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
