import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { SumDistribution, AcDistribution } from '../../types/statistics'

function SumTooltip({
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

function AcTooltip({
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
      AC {label}: {payload[0].value}회
    </div>
  )
}

export function SumAcDistribution({
  sumData,
  acData,
}: {
  sumData: SumDistribution[]
  acData: AcDistribution[]
}) {
  return (
    <div className="flex gap-4">
      <div className="w-3/5">
        <p className="text-sm font-bold text-text-primary mb-2">총합 분포</p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={sumData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-chart-grid)" />
            <XAxis
              dataKey="range"
              tick={{ fontSize: 9, fill: 'var(--color-chart-text)' }}
              angle={-30}
              textAnchor="end"
              height={50}
            />
            <YAxis width={30} tick={{ fill: 'var(--color-chart-text)' }} />
            <Tooltip content={<SumTooltip />} />
            <Bar dataKey="count" fill="var(--color-chart-blue)" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="w-2/5">
        <p className="text-sm font-bold text-text-primary mb-2">AC값 분포</p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={acData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-chart-grid)" />
            <XAxis dataKey="acValue" tick={{ fontSize: 11, fill: 'var(--color-chart-text)' }} />
            <YAxis width={30} tick={{ fill: 'var(--color-chart-text)' }} />
            <Tooltip content={<AcTooltip />} />
            <Bar dataKey="count" fill="var(--color-chart-purple)" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
