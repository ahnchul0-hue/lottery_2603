export type NumberFrequency = { number: number; count: number }

export type RatioDistribution = { ratio: string; count: number }

export type ZoneDistribution = {
  zone: string // "1-9", "10-19", "20-29", "30-39", "40-45"
  count: number
  percentage: number
}

export type SumDistribution = { range: string; count: number }

export type AcDistribution = { acValue: number; count: number }

export type HeatmapRow = {
  machine: string
  deviations: Record<string, number>
  total_draws: number
}

export type HeatmapData = {
  rows: HeatmapRow[]
}

export type StatisticsResult = {
  frequencyData: NumberFrequency[]
  hotNumbers: number[]
  coldNumbers: number[]
  oddEvenDist: RatioDistribution[]
  highLowDist: RatioDistribution[]
  zoneDist: ZoneDistribution[]
  sumDist: SumDistribution[]
  acDist: AcDistribution[]
}
