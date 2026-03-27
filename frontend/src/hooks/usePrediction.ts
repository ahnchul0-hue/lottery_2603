import { useRef, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import type { PredictResponse } from '../types/lottery'
import { STRATEGIES } from '../types/lottery'
import { fetchPrediction } from '../lib/api'

export function usePrediction() {
  const abortControllerRef = useRef<AbortController | null>(null)

  const mutation = useMutation<PredictResponse[], Error, string>({
    mutationFn: async (machine: string) => {
      // Abort any in-flight prediction request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      const controller = new AbortController()
      abortControllerRef.current = controller

      const results = await Promise.all(
        STRATEGIES.map((strategy) =>
          fetchPrediction(machine, strategy, controller.signal),
        ),
      )
      return results
    },
  })

  const cancelPrediction = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    mutation.reset()
  }, [mutation])

  return { ...mutation, cancelPrediction }
}
