import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { RatioDistribution as RatioDistributionType } from '../../types/statistics'

function RatioTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: { value: number }[]
  label?: string
}) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-card border border-border rounded px-2 py-1 text-sm text-text-primary shadow">
      {label}: {payload[0].value}회
    </div>
  )
}

export function RatioDistribution({
  oddEven,
  highLow,
}: {
  oddEven: RatioDistributionType[]
  highLow: RatioDistributionType[]
}) {
  return (
    <div className="flex gap-4">
      <div className="flex-1">
        <p className="text-sm font-bold text-text-primary mb-2">홀짝 비율</p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={oddEven}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-chart-grid)" />
            <XAxis dataKey="ratio" tick={{ fontSize: 10, fill: 'var(--color-chart-text)' }} />
            <YAxis width={30} tick={{ fill: 'var(--color-chart-text)' }} />
            <Tooltip content={<RatioTooltip />} />
            <Bar dataKey="count" fill="var(--color-chart-blue)" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex-1">
        <p className="text-sm font-bold text-text-primary mb-2">고저 비율</p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={highLow}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-chart-grid)" />
            <XAxis dataKey="ratio" tick={{ fontSize: 10, fill: 'var(--color-chart-text)' }} />
            <YAxis width={30} tick={{ fill: 'var(--color-chart-text)' }} />
            <Tooltip content={<RatioTooltip />} />
            <Bar dataKey="count" fill="var(--color-chart-purple)" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
