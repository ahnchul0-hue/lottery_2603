import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { NumberFrequency } from '../../types/statistics'

function FrequencyTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: { value: number }[]
  label?: number
}) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-card border border-border rounded px-2 py-1 text-sm text-text-primary shadow">
      {label}번: {payload[0].value}회
    </div>
  )
}

export function FrequencyBarChart({ data }: { data: NumberFrequency[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="number" tick={{ fontSize: 10 }} />
        <YAxis width={40} />
        <Tooltip content={<FrequencyTooltip />} />
        <Bar dataKey="count" fill="#3b82f6" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
