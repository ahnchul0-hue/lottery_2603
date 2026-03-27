import { useMemo } from 'react'
import type { LotteryDraw } from '../types/lottery'
import type {
  NumberFrequency,
  RatioDistribution,
  ZoneDistribution,
  SumDistribution,
  AcDistribution,
  StatisticsResult,
} from '../types/statistics'

function getZone(num: number): string {
  if (num <= 9) return '1-9'
  if (num <= 19) return '10-19'
  if (num <= 29) return '20-29'
  if (num <= 39) return '30-39'
  return '40-45'
}

function getSumBin(total: number): string {
  // Bins: 21-40, 41-60, 61-80, ... 221-240
  const lower = Math.floor((total - 1) / 20) * 20 + 1
  const upper = lower + 19
  return `${lower}-${upper}`
}

function countRatios(
  draws: LotteryDraw[],
  field: 'odd_even_ratio' | 'high_low_ratio',
): RatioDistribution[] {
  const categories = ['0:6', '1:5', '2:4', '3:3', '4:2', '5:1', '6:0']
  const counts: Record<string, number> = {}
  for (const cat of categories) {
    counts[cat] = 0
  }
  for (const draw of draws) {
    const ratio = draw[field]
    if (ratio in counts) {
      counts[ratio]++
    }
  }
  return categories.map((ratio) => ({ ratio, count: counts[ratio] }))
}

export function useStatistics(draws: LotteryDraw[]): StatisticsResult {
  // Frequency data: count per number 1-45
  const frequencyData = useMemo<NumberFrequency[]>(() => {
    const freq: Record<number, number> = {}
    for (let n = 1; n <= 45; n++) {
      freq[n] = 0
    }
    for (const draw of draws) {
      for (const num of draw.numbers) {
        freq[num]++
      }
    }
    return Array.from({ length: 45 }, (_, i) => ({
      number: i + 1,
      count: freq[i + 1],
    }))
  }, [draws])

  // Hot and cold numbers derived from frequency
  const hotNumbers = useMemo<number[]>(() => {
    return [...frequencyData]
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
      .map((d) => d.number)
  }, [frequencyData])

  const coldNumbers = useMemo<number[]>(() => {
    return [...frequencyData]
      .sort((a, b) => a.count - b.count)
      .slice(0, 10)
      .map((d) => d.number)
  }, [frequencyData])

  // Odd/even ratio distribution
  const oddEvenDist = useMemo<RatioDistribution[]>(() => {
    return countRatios(draws, 'odd_even_ratio')
  }, [draws])

  // High/low ratio distribution
  const highLowDist = useMemo<RatioDistribution[]>(() => {
    return countRatios(draws, 'high_low_ratio')
  }, [draws])

  // Zone distribution
  const zoneDist = useMemo<ZoneDistribution[]>(() => {
    const zones = ['1-9', '10-19', '20-29', '30-39', '40-45']
    const counts: Record<string, number> = {}
    for (const z of zones) {
      counts[z] = 0
    }
    for (const draw of draws) {
      for (const num of draw.numbers) {
        counts[getZone(num)]++
      }
    }
    const totalNumbers = draws.length * 6
    return zones.map((zone) => ({
      zone,
      count: counts[zone],
      percentage: totalNumbers > 0
        ? Math.round((counts[zone] / totalNumbers) * 10000) / 100
        : 0,
    }))
  }, [draws])

  // Sum distribution
  const sumDist = useMemo<SumDistribution[]>(() => {
    const bins: Record<string, number> = {}
    for (const draw of draws) {
      const bin = getSumBin(draw.total_sum)
      bins[bin] = (bins[bin] || 0) + 1
    }
    // Sort bins by their lower bound
    return Object.entries(bins)
      .sort(([a], [b]) => {
        const aLow = parseInt(a.split('-')[0], 10)
        const bLow = parseInt(b.split('-')[0], 10)
        return aLow - bLow
      })
      .map(([range, count]) => ({ range, count }))
  }, [draws])

  // AC value distribution
  const acDist = useMemo<AcDistribution[]>(() => {
    const counts: Record<number, number> = {}
    for (const draw of draws) {
      counts[draw.ac_value] = (counts[draw.ac_value] || 0) + 1
    }
    return Object.entries(counts)
      .map(([acValue, count]) => ({
        acValue: parseInt(acValue, 10),
        count,
      }))
      .sort((a, b) => a.acValue - b.acValue)
  }, [draws])

  return {
    frequencyData,
    hotNumbers,
    coldNumbers,
    oddEvenDist,
    highLowDist,
    zoneDist,
    sumDist,
    acDist,
  }
}
