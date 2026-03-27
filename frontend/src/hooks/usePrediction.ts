import { useMutation } from '@tanstack/react-query'
import type { PredictResponse } from '../types/lottery'
import { STRATEGIES } from '../types/lottery'
import { fetchPrediction } from '../lib/api'

export function usePrediction() {
  return useMutation<PredictResponse[], Error, string>({
    mutationFn: async (machine: string) => {
      const results = await Promise.all(
        STRATEGIES.map((strategy) => fetchPrediction(machine, strategy)),
      )
      return results
    },
  })
}
