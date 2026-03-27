import { useQuery } from '@tanstack/react-query'
import type { HeatmapData } from '../types/statistics'
import { fetchHeatmapData } from '../lib/api'

export function useHeatmapData() {
  return useQuery<HeatmapData>({
    queryKey: ['heatmap'],
    queryFn: fetchHeatmapData,
    staleTime: Infinity,
  })
}
