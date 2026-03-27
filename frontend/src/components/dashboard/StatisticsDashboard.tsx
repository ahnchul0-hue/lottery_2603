import { useQuery } from '@tanstack/react-query'
import { fetchMachineData } from '../../lib/api'
import { useStatistics } from '../../hooks/useStatistics'
import { useHeatmapData } from '../../hooks/useHeatmapData'
import { ChartCard } from './ChartCard'
import { FrequencyBarChart } from './FrequencyBarChart'
import { HotColdNumbers } from './HotColdNumbers'
import { HeatmapGrid } from './HeatmapGrid'

export function StatisticsDashboard({
  machine,
}: {
  machine: string | null
}) {
  // Reuse fetchMachineData with a dashboard-specific queryKey
  // TanStack Query deduplicates: same queryFn, different transform = separate cache entry
  const { data } = useQuery({
    queryKey: ['machineDraws', machine],
    queryFn: () => fetchMachineData(machine!),
    staleTime: Infinity,
    enabled: machine !== null,
  })

  const stats = useStatistics(data?.draws ?? [])
  const heatmap = useHeatmapData()

  if (!machine) {
    return (
      <div className="text-center py-8">
        <p className="text-lg font-bold text-text-primary">
          호기를 선택하세요
        </p>
        <p className="text-sm text-text-secondary mt-2">
          위에서 호기를 선택하면 통계 분석이 표시됩니다
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <ChartCard title="번호별 출현 빈도">
        <FrequencyBarChart data={stats.frequencyData} />
      </ChartCard>

      <ChartCard title="Hot / Cold 번호">
        <HotColdNumbers hot={stats.hotNumbers} cold={stats.coldNumbers} />
      </ChartCard>

      <ChartCard title="호기별 번호 편중 히트맵">
        <HeatmapGrid
          data={heatmap.data?.rows ?? []}
          selectedMachine={machine}
        />
      </ChartCard>

      {/* DASH-04, DASH-05, DASH-06 chart sections added in Plan 03 */}
    </div>
  )
}
